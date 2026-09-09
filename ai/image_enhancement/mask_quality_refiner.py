"""
CraftMitra - Mask Quality / Refinement Stage

Consumes a mask produced by background_remover_mask.py and returns a cleaner
alpha mask. This module does NOT perform semantic foreground detection.

Pipeline:
    lighting_corrector
        -> background_remover_mask
        -> mask_quality_refiner   <-- this file
        -> final transparent image

Design principles:
    - model-agnostic
    - OpenCV + NumPy only
    - conservative around product edges
    - removes weak halos and tiny mask noise
    - fills small accidental holes
    - optionally uses GrabCut as a secondary refinement
    - reports mask quality so the pipeline can retry a stronger model

Important limitation:
    If a background object is connected to the product and has very similar
    color/texture, classical mask refinement cannot reliably know the
    semantic boundary. In that case the correct solution is a better
    segmentation model/mask, not increasingly aggressive morphology.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import cv2
import numpy as np


ImageInput = Union[str, Path, np.ndarray]


class MaskQualityRefiner:
    """Analyze and conservatively refine a segmentation mask."""

    MAX_WORK_SIZE = 1280

    # Raw model alpha is normally in [0, 255].
    DEFAULT_FOREGROUND_THRESHOLD = 160
    DEFAULT_SOFT_THRESHOLD = 40
    STRONG_FOREGROUND_THRESHOLD = 220

    # Small morphology only. Artisan products can contain thin details.
    OPEN_KERNEL = 3
    CLOSE_KERNEL = 3

    # Small isolated regions below this image fraction are removed.
    MIN_COMPONENT_AREA_RATIO = 0.00005

    # Small holes inside the product can be filled.
    MAX_HOLE_AREA_RATIO = 0.004

    # Final alpha edge feathering.
    FEATHER_RADIUS = 1

    # Quality score thresholds.
    GOOD_SCORE = 0.75
    ACCEPTABLE_SCORE = 0.58

    def __init__(
        self,
        max_work_size: int = MAX_WORK_SIZE,
        foreground_threshold: int = DEFAULT_FOREGROUND_THRESHOLD,
        use_grabcut: bool = False,
    ) -> None:
        self.max_work_size = max_work_size
        self.foreground_threshold = int(
            np.clip(foreground_threshold, 80, 220)
        )
        self.use_grabcut = use_grabcut

    # =========================================================
    # PUBLIC API
    # =========================================================

    def refine(
        self,
        image: ImageInput,
        mask: ImageInput,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Analyze and refine a raw segmentation mask.

        Returns:
            refined_mask: uint8 alpha mask, same dimensions as image.
            report: quality measurements before/after refinement.
        """

        image_bgr = self._load_image(image, color=True)
        raw = self._load_mask(mask)

        original_h, original_w = image_bgr.shape[:2]
        work_image = self._resize_for_work(image_bgr)
        work_mask = cv2.resize(
            raw,
            (work_image.shape[1], work_image.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )
        work_mask = np.clip(work_mask, 0, 255).astype(np.uint8)

        before = self._quality_report(work_image, work_mask)

        # -----------------------------------------------------
        # 1. Convert model alpha into a conservative foreground mask.
        # -----------------------------------------------------
        binary = self._make_binary_mask(work_mask)

        # -----------------------------------------------------
        # 2. Remove tiny isolated noise.
        # -----------------------------------------------------
        binary = self._remove_small_components(binary)

        # -----------------------------------------------------
        # 3. Fill only small holes.
        # -----------------------------------------------------
        binary = self._fill_small_holes(binary)

        # -----------------------------------------------------
        # 4. Very small morphological cleanup.
        # -----------------------------------------------------
        kernel_open = np.ones(
            (self.OPEN_KERNEL, self.OPEN_KERNEL),
            np.uint8,
        )
        kernel_close = np.ones(
            (self.CLOSE_KERNEL, self.CLOSE_KERNEL),
            np.uint8,
        )

        binary = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            kernel_open,
            iterations=1,
        )
        binary = cv2.morphologyEx(
            binary,
            cv2.MORPH_CLOSE,
            kernel_close,
            iterations=1,
        )

        # Reconnect/retain the main product component after morphology.
        binary = self._keep_meaningful_components(binary)

        # -----------------------------------------------------
        # 5. Optional image-guided refinement.
        # -----------------------------------------------------
        grabcut_used = False
        if self.use_grabcut and self._safe_for_grabcut(binary):
            gc = self._grabcut(work_image, binary)
            if gc is not None:
                # Only accept GrabCut if it is not wildly different from
                # the model mask. Semantic segmentation remains the model's
                # responsibility.
                if self._reasonable_area_change(binary, gc):
                    binary = gc
                    grabcut_used = True

        # -----------------------------------------------------
        # 6. Rebuild a clean alpha mask.
        # -----------------------------------------------------
        refined = self._build_alpha(work_mask, binary)
        refined = self._remove_outer_weak_alpha(refined, binary)
        refined = self._feather(refined, binary)
        refined = self._protect_border(refined)

        after = self._quality_report(work_image, refined)

        # If refinement made the quality score worse, keep the raw model
        # mask. This makes the refiner fail-safe rather than destructive.
        if after["score"] + 0.01 < before["score"]:
            refined = work_mask.copy()
            after = before
            grabcut_used = False
            selected = "raw_mask"
        else:
            selected = "refined_mask"

        # Restore original dimensions.
        refined_mask = cv2.resize(
            refined,
            (original_w, original_h),
            interpolation=cv2.INTER_LINEAR,
        )
        refined_mask = np.clip(refined_mask, 0, 255).astype(np.uint8)

        report = self._build_report(
            before,
            after,
            selected=selected,
            grabcut_used=grabcut_used,
            image_size=(original_w, original_h),
            work_size=(work_image.shape[1], work_image.shape[0]),
        )

        return refined_mask, report

    def refine_to_rgba(
        self,
        image: ImageInput,
        mask: ImageInput,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Return a BGRA transparent image using the refined mask."""

        image_bgr = self._load_image(image, color=True)
        refined_mask, report = self.refine(image_bgr, mask)

        result = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = refined_mask
        return result, report

    # =========================================================
    # LOADING
    # =========================================================

    @staticmethod
    def _load_image(
        image: ImageInput,
        color: bool = True,
    ) -> np.ndarray:
        if isinstance(image, (str, Path)):
            path = Path(image)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {path}")

            flag = cv2.IMREAD_COLOR if color else cv2.IMREAD_GRAYSCALE
            loaded = cv2.imread(str(path), flag)
            if loaded is None:
                raise ValueError(f"Unable to read image: {path}")
            return loaded

        if not isinstance(image, np.ndarray) or image.size == 0:
            raise TypeError("Image must be a valid path or NumPy array.")

        arr = image.copy()

        if color:
            if arr.ndim == 2:
                arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
            elif arr.ndim == 3 and arr.shape[2] == 4:
                arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
            elif arr.ndim != 3 or arr.shape[2] != 3:
                raise ValueError("Unsupported color image format.")
        else:
            if arr.ndim == 3 and arr.shape[2] == 4:
                arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)
            elif arr.ndim == 3 and arr.shape[2] == 3:
                arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
            elif arr.ndim != 2:
                raise ValueError("Unsupported mask format.")

        return arr

    def _load_mask(self, mask: ImageInput) -> np.ndarray:
        if isinstance(mask, (str, Path)):
            path = Path(mask)
            if not path.exists():
                raise FileNotFoundError(f"Mask not found: {path}")
            loaded = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            if loaded is None:
                raise ValueError(f"Unable to read mask: {path}")
        else:
            if not isinstance(mask, np.ndarray) or mask.size == 0:
                raise TypeError("Mask must be a valid path or NumPy array.")
            loaded = mask.copy()

        if loaded.ndim == 2:
            result = loaded
        elif loaded.ndim == 3 and loaded.shape[2] == 4:
            result = loaded[:, :, 3]
        elif loaded.ndim == 3 and loaded.shape[2] == 3:
            result = cv2.cvtColor(loaded, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Unsupported mask format.")

        if result.dtype != np.uint8:
            result = cv2.normalize(
                result,
                None,
                0,
                255,
                cv2.NORM_MINMAX,
            ).astype(np.uint8)

        return result

    # =========================================================
    # WORK IMAGE
    # =========================================================

    def _resize_for_work(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        largest = max(h, w)

        if largest <= self.max_work_size:
            return image.copy()

        scale = self.max_work_size / largest
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))

        return cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_AREA,
        )

    # =========================================================
    # MASK CREATION
    # =========================================================

    def _make_binary_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        Convert alpha into a binary product prior.

        160 is intentionally stricter than the common 128 threshold. In
        our tested cluttered blend image this removes much of the faint
        background/halo that remains in the U2Net-family alpha output while
        retaining the solid product body.
        """

        binary = np.where(
            mask >= self.foreground_threshold,
            255,
            0,
        ).astype(np.uint8)

        return binary

    # =========================================================
    # COMPONENTS / HOLES
    # =========================================================

    def _remove_small_components(self, binary: np.ndarray) -> np.ndarray:
        count, labels, stats, _ = cv2.connectedComponentsWithStats(
            (binary > 0).astype(np.uint8),
            connectivity=8,
        )

        if count <= 1:
            return binary

        min_area = max(
            16,
            int(binary.size * self.MIN_COMPONENT_AREA_RATIO),
        )

        cleaned = np.zeros_like(binary)
        areas = stats[1:, cv2.CC_STAT_AREA]

        for label in range(1, count):
            if stats[label, cv2.CC_STAT_AREA] >= min_area:
                cleaned[labels == label] = 255

        if not np.any(cleaned) and areas.size:
            largest = 1 + int(np.argmax(areas))
            cleaned[labels == largest] = 255

        return cleaned

    def _keep_meaningful_components(self, binary: np.ndarray) -> np.ndarray:
        count, labels, stats, _ = cv2.connectedComponentsWithStats(
            (binary > 0).astype(np.uint8),
            connectivity=8,
        )

        if count <= 1:
            return binary

        image_area = binary.size
        areas = stats[1:, cv2.CC_STAT_AREA]
        largest_area = int(np.max(areas)) if areas.size else 0

        result = np.zeros_like(binary)

        for label in range(1, count):
            area = stats[label, cv2.CC_STAT_AREA]
            # Keep the main product and useful small detached pieces.
            # Detached pieces larger than 0.02% of the frame are retained.
            if area >= max(16, int(image_area * 0.0002)):
                result[labels == label] = 255
            elif area >= largest_area * 0.015:
                result[labels == label] = 255

        return result

    def _fill_small_holes(self, binary: np.ndarray) -> np.ndarray:
        binary_bool = binary > 0
        if not np.any(binary_bool):
            return binary

        h, w = binary.shape
        flood = (binary_bool * 255).astype(np.uint8)
        flood_mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(flood, flood_mask, (0, 0), 128)

        holes = (flood == 0).astype(np.uint8)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(
            holes,
            connectivity=8,
        )

        max_area = int(binary.size * self.MAX_HOLE_AREA_RATIO)
        result = binary.copy()

        for label in range(1, count):
            area = stats[label, cv2.CC_STAT_AREA]
            if area <= max_area:
                result[labels == label] = 255

        return result

    # =========================================================
    # ALPHA RECONSTRUCTION
    # =========================================================

    def _build_alpha(
        self,
        raw_alpha: np.ndarray,
        binary: np.ndarray,
    ) -> np.ndarray:
        """
        Keep strong model alpha in the accepted foreground, but suppress
        weak alpha outside the refined silhouette.
        """

        accepted = binary > 0
        result = np.where(accepted, raw_alpha, 0).astype(np.uint8)

        # Product interior should be fully opaque if the model was already
        # strongly confident there.
        strong = accepted & (raw_alpha >= self.STRONG_FOREGROUND_THRESHOLD)
        result[strong] = raw_alpha[strong]

        return result

    def _remove_outer_weak_alpha(
        self,
        alpha: np.ndarray,
        binary: np.ndarray,
    ) -> np.ndarray:
        """Remove faint pixels immediately outside the product silhouette."""

        result = alpha.copy()
        dilated = cv2.dilate(
            binary,
            np.ones((5, 5), np.uint8),
            iterations=1,
        )

        outer_ring = (dilated > 0) & (binary == 0)
        result[outer_ring & (result < self.DEFAULT_SOFT_THRESHOLD)] = 0

        return result

    def _feather(
        self,
        alpha: np.ndarray,
        binary: np.ndarray,
    ) -> np.ndarray:
        if self.FEATHER_RADIUS <= 0:
            return alpha

        k = self.FEATHER_RADIUS * 2 + 1
        blurred = cv2.GaussianBlur(alpha, (k, k), 0)

        # Preserve strong interior alpha.
        interior = binary > 0
        strong = interior & (alpha >= 220)
        blurred[strong] = alpha[strong]

        return blurred.astype(np.uint8)

    @staticmethod
    def _protect_border(alpha: np.ndarray) -> np.ndarray:
        result = alpha.copy()
        h, w = result.shape
        thickness = max(1, int(min(h, w) * 0.004))

        result[:thickness, :] = 0
        result[-thickness:, :] = 0
        result[:, :thickness] = 0
        result[:, -thickness:] = 0

        return result

    # =========================================================
    # OPTIONAL GRABCUT
    # =========================================================

    @staticmethod
    def _safe_for_grabcut(binary: np.ndarray) -> bool:
        ratio = float(np.mean(binary > 0))
        return 0.01 < ratio < 0.80

    def _grabcut(
        self,
        image: np.ndarray,
        binary: np.ndarray,
    ) -> Optional[np.ndarray]:
        h, w = binary.shape
        gc = np.full((h, w), cv2.GC_PR_BGD, np.uint8)

        gc[binary == 0] = cv2.GC_PR_BGD

        sure_fg = cv2.erode(
            binary,
            np.ones((5, 5), np.uint8),
            iterations=1,
        ) > 0

        gc[sure_fg] = cv2.GC_FGD

        # A small image border is definite background.
        b = max(2, int(min(h, w) * 0.01))
        gc[:b, :] = cv2.GC_BGD
        gc[-b:, :] = cv2.GC_BGD
        gc[:, :b] = cv2.GC_BGD
        gc[:, -b:] = cv2.GC_BGD

        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        try:
            cv2.grabCut(
                image,
                gc,
                None,
                bgd_model,
                fgd_model,
                3,
                cv2.GC_INIT_WITH_MASK,
            )
        except cv2.error:
            return None

        result = np.where(
            (gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD),
            255,
            0,
        ).astype(np.uint8)

        return self._remove_small_components(result)

    @staticmethod
    def _reasonable_area_change(
        old: np.ndarray,
        new: np.ndarray,
    ) -> bool:
        old_ratio = float(np.mean(old > 0))
        new_ratio = float(np.mean(new > 0))

        if old_ratio <= 0:
            return False

        relative_change = abs(old_ratio - new_ratio) / old_ratio
        return relative_change <= 0.25

    # =========================================================
    # QUALITY ANALYSIS
    # =========================================================

    def _quality_report(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> Dict[str, Any]:
        binary = mask >= 128

        foreground_ratio = float(np.mean(binary))
        border_ratio = self._border_foreground_ratio(mask)
        component_count, largest_ratio = self._component_stats(binary)
        hole_ratio = self._hole_ratio(binary)
        edge_alignment = self._edge_alignment(image, mask)
        halo_ratio = self._halo_ratio(mask)

        area_score = self._area_score(foreground_ratio)
        border_score = 1.0 - np.clip(border_ratio / 0.08, 0.0, 1.0)
        component_score = 1.0 if component_count <= 2 else max(
            0.0,
            1.0 - (component_count - 2) / 15.0,
        )
        hole_score = 1.0 - np.clip(hole_ratio / 0.08, 0.0, 1.0)
        halo_score = 1.0 - np.clip(halo_ratio / 0.25, 0.0, 1.0)

        score = (
            0.22 * area_score
            + 0.22 * border_score
            + 0.16 * component_score
            + 0.10 * hole_score
            + 0.20 * edge_alignment
            + 0.10 * halo_score
        )

        if score >= self.GOOD_SCORE:
            quality = "good"
        elif score >= self.ACCEPTABLE_SCORE:
            quality = "acceptable"
        else:
            quality = "poor"

        return {
            "score": round(float(score), 4),
            "quality": quality,
            "foreground_area_ratio": round(foreground_ratio, 4),
            "border_foreground_ratio": round(border_ratio, 4),
            "connected_components": int(component_count),
            "largest_component_ratio": round(largest_ratio, 4),
            "hole_ratio": round(hole_ratio, 4),
            "edge_alignment": round(float(edge_alignment), 4),
            "halo_ratio": round(float(halo_ratio), 4),
        }

    @staticmethod
    def _border_foreground_ratio(mask: np.ndarray) -> float:
        h, w = mask.shape
        t = max(2, int(min(h, w) * 0.02))

        border = np.zeros_like(mask, dtype=bool)
        border[:t, :] = True
        border[-t:, :] = True
        border[:, :t] = True
        border[:, -t:] = True

        return float(np.mean(mask[border] >= 128))

    @staticmethod
    def _component_stats(binary: np.ndarray) -> Tuple[int, float]:
        count, _, stats, _ = cv2.connectedComponentsWithStats(
            binary.astype(np.uint8),
            connectivity=8,
        )

        if count <= 1:
            return 0, 0.0

        areas = stats[1:, cv2.CC_STAT_AREA]
        largest = int(np.max(areas)) if areas.size else 0
        return count - 1, largest / max(binary.size, 1)

    @staticmethod
    def _hole_ratio(binary: np.ndarray) -> float:
        if not np.any(binary):
            return 0.0

        h, w = binary.shape
        flood = (binary * 255).astype(np.uint8)
        flood_mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(flood, flood_mask, (0, 0), 128)

        holes = flood == 0
        foreground = max(int(np.sum(binary)), 1)
        return float(np.sum(holes) / foreground)

    @staticmethod
    def _edge_alignment(image: np.ndarray, mask: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.dilate(edges, np.ones((5, 5), np.uint8)) > 0

        boundary = cv2.morphologyEx(
            (mask >= 128).astype(np.uint8) * 255,
            cv2.MORPH_GRADIENT,
            np.ones((3, 3), np.uint8),
        ) > 0

        total = int(np.sum(boundary))
        if total == 0:
            return 0.0

        return float(np.sum(boundary & edges) / total)

    @staticmethod
    def _halo_ratio(mask: np.ndarray) -> float:
        strong = mask >= 128
        expanded = cv2.dilate(
            strong.astype(np.uint8),
            np.ones((7, 7), np.uint8),
        ) > 0

        outside = expanded & ~strong
        if not np.any(outside):
            return 0.0

        # Pixels with meaningful alpha immediately outside the silhouette
        # are a likely halo.
        return float(np.mean(mask[outside] >= 40))

    @staticmethod
    def _area_score(ratio: float) -> float:
        if ratio <= 0.003 or ratio >= 0.95:
            return 0.05
        if 0.03 <= ratio <= 0.75:
            return 1.0
        if ratio < 0.03:
            return ratio / 0.03
        return max(0.0, (0.95 - ratio) / 0.20)

    # =========================================================
    # REPORT
    # =========================================================

    @staticmethod
    def _build_report(
        before: Dict[str, Any],
        after: Dict[str, Any],
        selected: str,
        grabcut_used: bool,
        image_size: Tuple[int, int],
        work_size: Tuple[int, int],
    ) -> Dict[str, Any]:
        improvement = after["score"] - before["score"]

        if selected == "raw_mask":
            if after["quality"] == "good":
                action = "use_raw_mask"
            elif after["quality"] == "acceptable":
                action = "use_raw_mask_with_caution"
            else:
                action = "retry_segmentation_model"
        elif after["quality"] == "good":
            action = "use_refined_mask"
        elif after["quality"] == "acceptable":
            action = "use_refined_mask_with_caution"
        else:
            action = "retry_segmentation_model"

        warnings: list[str] = []

        if after["border_foreground_ratio"] > 0.02:
            warnings.append("foreground_reaches_image_border")

        if after["halo_ratio"] > 0.20:
            warnings.append("possible_mask_halo")

        if after["connected_components"] > 4:
            warnings.append("multiple_foreground_components")

        if after["quality"] == "poor":
            warnings.append("mask_quality_is_not_reliable")

        return {
            "mask_quality": after["quality"],
            "mask_score": after["score"],
            "quality_improvement": round(improvement, 4),
            "selected_mask": selected,
            "grabcut_used": grabcut_used,
            "action": action,
            "before": before,
            "after": after,
            "image": {
                "width": image_size[0],
                "height": image_size[1],
                "work_width": work_size[0],
                "work_height": work_size[1],
            },
            "warnings": warnings,
        }


# =============================================================
# SIMPLE FUNCTION API
# =============================================================


def refine_mask(
    image: ImageInput,
    mask: ImageInput,
    foreground_threshold: int = 160,
    use_grabcut: bool = False,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Convenience function."""

    refiner = MaskQualityRefiner(
        foreground_threshold=foreground_threshold,
        use_grabcut=use_grabcut,
    )
    return refiner.refine(image, mask)


# =============================================================
# COMMAND LINE TEST
# =============================================================

if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) not in {3, 4}:
        print(
            "Usage: python mask_quality_refiner.py "
            "<image_path> <mask_path> [output_mask_path]"
        )
        sys.exit(1)

    image_path = sys.argv[1]
    mask_path = sys.argv[2]
    output_path = (
        sys.argv[3]
        if len(sys.argv) == 4
        else "refined_mask.png"
    )

    refined, report = refine_mask(
        image_path,
        mask_path,
        foreground_threshold=160,
        use_grabcut=False,
    )

    if not cv2.imwrite(output_path, refined):
        raise RuntimeError(
            f"Could not save refined mask: {output_path}"
        )

    print(json.dumps(report, indent=4))