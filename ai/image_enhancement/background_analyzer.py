"""
CraftMitra - Background Analyzer

Purpose:
    Analyze whether an artisan product photograph has a clean
    enough background to keep, or whether it should be sent
    to the background-removal stage.

Important:
    This module DOES NOT remove the background.

    It only analyzes the image and makes a decision.

Design goals:
    - Reliable for real-world artisan photographs
    - Works with arbitrary image dimensions
    - Uses lightweight computer-vision techniques
    - No assumption that the background exists only in the border
    - Uses multiple spatial regions
    - Avoid unnecessary background removal
    - Provides measurements and explanations

Pipeline position:

    Lighting-corrected image
            |
            v
    BackgroundAnalyzer
            |
       +----+----+
       |         |
      KEEP     REMOVE
       |         |
       v         v
    original   background_remover_mask.py
"""


from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union

import cv2
import numpy as np


ImageInput = Union[str, Path, np.ndarray]


class BackgroundAnalyzer:
    """
    Multi-region background-quality analyzer.

    The previous version relied heavily on an outer 8% border.
    That is unreliable for artisan photographs because clutter
    can exist well inside the image.

    This version analyzes:

        1. Corner regions
        2. Top / bottom regions
        3. Left / right regions
        4. Spatial brightness variation
        5. Color variation
        6. Edge density
        7. Texture
        8. Subject/background separation
        9. Estimated foreground occupancy

    Higher final score means:
        more evidence that background removal may be useful.
    """

    # =========================================================
    # ANALYSIS CONFIGURATION
    # =========================================================

    MAX_ANALYSIS_SIZE = 1280

    # Fraction of image used for regional analysis.
    REGION_RATIO = 0.15

    # Fraction of image used to estimate the central subject.
    CENTER_RATIO = 0.60

    # =========================================================
    # DECISION THRESHOLDS
    # =========================================================

    BACKGROUND_GOOD_THRESHOLD = 0.35
    BACKGROUND_POOR_THRESHOLD = 0.55

    # =========================================================
    # SCORE WEIGHTS
    # =========================================================

    WEIGHT_UNIFORMITY = 0.20
    WEIGHT_COLOR_VARIATION = 0.15
    WEIGHT_EDGE_DENSITY = 0.25
    WEIGHT_TEXTURE = 0.15
    WEIGHT_SEPARATION = 0.25

    def __init__(
        self,
        max_analysis_size: int = MAX_ANALYSIS_SIZE
    ):
        self.max_analysis_size = max_analysis_size

    # =========================================================
    # PUBLIC API
    # =========================================================

    def analyze(
        self,
        image: ImageInput
    ) -> Dict[str, Any]:
        """
        Analyze background quality.

        Args:
            image:
                Image file path, pathlib.Path, or NumPy array.

        Returns:
            Dictionary containing image information,
            measurements, decision, confidence and reasons.
        """

        original = self._load_image(image)

        original_height, original_width = original.shape[:2]

        analysis_image = self._resize_for_analysis(
            original
        )

        gray = cv2.cvtColor(
            analysis_image,
            cv2.COLOR_BGR2GRAY
        )

        lab = cv2.cvtColor(
            analysis_image,
            cv2.COLOR_BGR2LAB
        )

        # -----------------------------------------------------
        # Create spatial analysis regions
        # -----------------------------------------------------

        regions = self._create_analysis_regions(
            analysis_image.shape[:2]
        )

        # -----------------------------------------------------
        # Analyze background using multiple regions
        # -----------------------------------------------------

        uniformity = self._analyze_uniformity(
            lab,
            regions
        )

        color_variation = self._analyze_color_variation(
            lab,
            regions
        )

        edge_density = self._analyze_edge_density(
            gray,
            regions
        )

        texture = self._analyze_texture(
            gray,
            regions
        )

        separation = self._analyze_subject_separation(
            lab
        )

        occupancy = self._estimate_subject_occupancy(
            analysis_image
        )

        # -----------------------------------------------------
        # Calculate final score
        # -----------------------------------------------------

        score = self._calculate_background_score(
            uniformity=uniformity["score"],
            color_variation=color_variation["score"],
            edge_density=edge_density["score"],
            texture=texture["score"],
            separation=separation["score"]
        )

        # -----------------------------------------------------
        # Classification
        # -----------------------------------------------------

        quality, recommendation = self._classify_background(
            score
        )

        confidence = self._calculate_confidence(
            score,
            quality
        )

        # -----------------------------------------------------
        # Reasons
        # -----------------------------------------------------

        reasons = self._generate_reasons(
            uniformity=uniformity,
            color_variation=color_variation,
            edge_density=edge_density,
            texture=texture,
            separation=separation,
            occupancy=occupancy,
            score=score
        )

        return {
            "image": {
                "width": original_width,
                "height": original_height,
                "analysis_width": analysis_image.shape[1],
                "analysis_height": analysis_image.shape[0]
            },

            "background": {
                "score": round(
                    score,
                    4
                ),

                "quality": quality,

                "confidence": round(
                    confidence,
                    4
                ),

                "measurements": {
                    "uniformity": uniformity,
                    "color_variation": color_variation,
                    "edge_density": edge_density,
                    "texture": texture,
                    "subject_separation": separation,
                    "subject_occupancy": occupancy
                }
            },

            "recommendation": {
                "remove_background": recommendation,

                "action": (
                    "send_to_background_removal"
                    if recommendation
                    else "keep_original"
                )
            },

            "reasons": reasons
        }

    # =========================================================
    # IMAGE LOADING
    # =========================================================

    @staticmethod
    def _load_image(
        image: ImageInput
    ) -> np.ndarray:
        """
        Load and validate an image.
        """

        if isinstance(
            image,
            (str, Path)
        ):

            path = Path(image)

            if not path.exists():

                raise FileNotFoundError(
                    f"Image not found: {path}"
                )

            img = cv2.imread(
                str(path),
                cv2.IMREAD_COLOR
            )

            if img is None:

                raise ValueError(
                    f"Unable to read image: {path}"
                )

            return img

        if isinstance(
            image,
            np.ndarray
        ):

            if image.size == 0:

                raise ValueError(
                    "Image array is empty."
                )

            if image.ndim == 2:

                return cv2.cvtColor(
                    image,
                    cv2.COLOR_GRAY2BGR
                )

            if (
                image.ndim == 3
                and image.shape[2] == 4
            ):

                return cv2.cvtColor(
                    image,
                    cv2.COLOR_BGRA2BGR
                )

            if (
                image.ndim == 3
                and image.shape[2] == 3
            ):

                return image.copy()

        raise TypeError(
            "Image must be a path or NumPy array."
        )

    # =========================================================
    # RESIZING
    # =========================================================

    def _resize_for_analysis(
        self,
        image: np.ndarray
    ) -> np.ndarray:
        """
        Resize only for analysis.

        Original image is never modified.
        """

        height, width = image.shape[:2]

        largest_dimension = max(
            height,
            width
        )

        if (
            largest_dimension
            <= self.max_analysis_size
        ):

            return image

        scale = (
            self.max_analysis_size
            /
            largest_dimension
        )

        new_width = max(
            1,
            int(width * scale)
        )

        new_height = max(
            1,
            int(height * scale)
        )

        return cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

    # =========================================================
    # SPATIAL REGIONS
    # =========================================================

    def _create_analysis_regions(
        self,
        shape: tuple[int, int]
    ) -> list[tuple[int, int, int, int]]:
        """
        Create multiple regions around the image.

        Instead of assuming the entire background is contained
        in an 8% border, we inspect several meaningful areas.

        Each region is:

            (x1, y1, x2, y2)
        """

        height, width = shape

        rx = max(
            1,
            int(width * self.REGION_RATIO)
        )

        ry = max(
            1,
            int(height * self.REGION_RATIO)
        )

        regions = []

        # -----------------------------------------------------
        # Four corners
        # -----------------------------------------------------

        regions.append(
            (
                0,
                0,
                rx,
                ry
            )
        )

        regions.append(
            (
                width - rx,
                0,
                width,
                ry
            )
        )

        regions.append(
            (
                0,
                height - ry,
                rx,
                height
            )
        )

        regions.append(
            (
                width - rx,
                height - ry,
                width,
                height
            )
        )

        # -----------------------------------------------------
        # Top center
        # -----------------------------------------------------

        x1 = int(width * 0.30)
        x2 = int(width * 0.70)

        regions.append(
            (
                x1,
                0,
                x2,
                ry
            )
        )

        # -----------------------------------------------------
        # Bottom center
        # -----------------------------------------------------

        regions.append(
            (
                x1,
                height - ry,
                x2,
                height
            )
        )

        # -----------------------------------------------------
        # Left center
        # -----------------------------------------------------

        y1 = int(height * 0.30)
        y2 = int(height * 0.70)

        regions.append(
            (
                0,
                y1,
                rx,
                y2
            )
        )

        # -----------------------------------------------------
        # Right center
        # -----------------------------------------------------

        regions.append(
            (
                width - rx,
                y1,
                width,
                y2
            )
        )

        return regions

    # =========================================================
    # REGION PIXELS
    # =========================================================

    @staticmethod
    def _collect_region_pixels(
        image: np.ndarray,
        regions: list[tuple[int, int, int, int]]
    ) -> np.ndarray:
        """
        Collect pixels from all analysis regions.
        """

        pixel_groups = []

        for x1, y1, x2, y2 in regions:

            region = image[
                y1:y2,
                x1:x2
            ]

            if region.size == 0:
                continue

            pixel_groups.append(
                region.reshape(
                    -1,
                    image.shape[2]
                )
            )

        if not pixel_groups:

            return np.empty(
                (0, image.shape[2]),
                dtype=image.dtype
            )

        return np.concatenate(
            pixel_groups,
            axis=0
        )

    # =========================================================
    # UNIFORMITY
    # =========================================================

    def _analyze_uniformity(
        self,
        lab: np.ndarray,
        regions: list[tuple[int, int, int, int]]
    ) -> Dict[str, Any]:
        """
        Measure brightness variation across multiple
        background regions.

        Higher variation means more complex background.
        """

        regional_std = []

        regional_means = []

        for x1, y1, x2, y2 in regions:

            region = lab[
                y1:y2,
                x1:x2
            ]

            if region.size == 0:
                continue

            luminance = region[
                :, :, 0
            ].astype(
                np.float32
            )

            regional_std.append(
                float(
                    np.std(luminance)
                )
            )

            regional_means.append(
                float(
                    np.mean(luminance)
                )
            )

        if not regional_std:

            return {
                "variation": 0.0,
                "regional_variation": 0.0,
                "score": 0.0
            }

        local_variation = float(
            np.mean(regional_std)
        )

        global_variation = float(
            np.std(regional_means)
        )

        variation = (
            0.70 * local_variation
            +
            0.30 * global_variation
        )

        score = np.clip(
            variation / 55.0,
            0.0,
            1.0
        )

        return {
            "variation": round(
                variation,
                2
            ),

            "regional_variation": round(
                global_variation,
                2
            ),

            "score": round(
                float(score),
                4
            )
        }

    # =========================================================
    # COLOR VARIATION
    # =========================================================

    def _analyze_color_variation(
        self,
        lab: np.ndarray,
        regions: list[tuple[int, int, int, int]]
    ) -> Dict[str, Any]:
        """
        Measure color variation across background regions.
        """

        pixels = self._collect_region_pixels(
            lab,
            regions
        )

        if pixels.size == 0:

            return {
                "variation": 0.0,
                "score": 0.0
            }

        a_channel = pixels[
            :, 1
        ].astype(
            np.float32
        )

        b_channel = pixels[
            :, 2
        ].astype(
            np.float32
        )

        a_std = float(
            np.std(a_channel)
        )

        b_std = float(
            np.std(b_channel)
        )

        variation = (
            a_std
            +
            b_std
        ) / 2.0

        score = np.clip(
            variation / 35.0,
            0.0,
            1.0
        )

        return {
            "variation": round(
                variation,
                2
            ),

            "score": round(
                float(score),
                4
            )
        }

    # =========================================================
    # EDGE DENSITY
    # =========================================================

    def _analyze_edge_density(
        self,
        gray: np.ndarray,
        regions: list[tuple[int, int, int, int]]
    ) -> Dict[str, Any]:
        """
        Measure structural complexity across several
        background regions.
        """

        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        edges = cv2.Canny(
            blurred,
            threshold1=50,
            threshold2=150
        )

        ratios = []

        for x1, y1, x2, y2 in regions:

            region_edges = edges[
                y1:y2,
                x1:x2
            ]

            if region_edges.size == 0:
                continue

            ratios.append(
                float(
                    np.mean(
                        region_edges > 0
                    )
                )
            )

        if not ratios:

            return {
                "edge_ratio": 0.0,
                "score": 0.0
            }

        edge_ratio = float(
            np.mean(ratios)
        )

        score = np.clip(
            edge_ratio / 0.18,
            0.0,
            1.0
        )

        return {
            "edge_ratio": round(
                edge_ratio,
                4
            ),

            "score": round(
                float(score),
                4
            )
        }

    # =========================================================
    # TEXTURE
    # =========================================================

    def _analyze_texture(
        self,
        gray: np.ndarray,
        regions: list[tuple[int, int, int, int]]
    ) -> Dict[str, Any]:
        """
        Estimate fine-grained texture in the background.

        Uses Laplacian variance as a lightweight texture signal.
        """

        blurred = cv2.GaussianBlur(
            gray,
            (3, 3),
            0
        )

        laplacian = cv2.Laplacian(
            blurred,
            cv2.CV_64F
        )

        variances = []

        for x1, y1, x2, y2 in regions:

            region = laplacian[
                y1:y2,
                x1:x2
            ]

            if region.size == 0:
                continue

            variances.append(
                float(
                    np.var(region)
                )
            )

        if not variances:

            return {
                "variance": 0.0,
                "score": 0.0
            }

        variance = float(
            np.mean(variances)
        )

        score = np.clip(
            variance / 1200.0,
            0.0,
            1.0
        )

        return {
            "variance": round(
                variance,
                2
            ),

            "score": round(
                float(score),
                4
            )
        }

    # =========================================================
    # SUBJECT / BACKGROUND SEPARATION
    # =========================================================

    def _analyze_subject_separation(
        self,
        lab: np.ndarray
    ) -> Dict[str, Any]:
        """
        Estimate whether the central region differs from
        the surrounding image.

        This is NOT semantic product detection.

        It is only supporting evidence.
        """

        height, width = lab.shape[:2]

        center_ratio = self.CENTER_RATIO

        center_width = int(
            width * center_ratio
        )

        center_height = int(
            height * center_ratio
        )

        x1 = max(
            0,
            (width - center_width) // 2
        )

        y1 = max(
            0,
            (height - center_height) // 2
        )

        x2 = min(
            width,
            x1 + center_width
        )

        y2 = min(
            height,
            y1 + center_height
        )

        center = lab[
            y1:y2,
            x1:x2
        ]

        # -----------------------------------------------------
        # Outer region
        # -----------------------------------------------------

        outer_mask = np.ones(
            (height, width),
            dtype=np.uint8
        )

        outer_mask[
            y1:y2,
            x1:x2
        ] = 0

        center_pixels = center.reshape(
            -1,
            3
        ).astype(
            np.float32
        )

        outer_pixels = lab[
            outer_mask > 0
        ].astype(
            np.float32
        )

        if (
            center_pixels.size == 0
            or outer_pixels.size == 0
        ):

            return {
                "distance": 0.0,
                "score": 0.0
            }

        center_mean = np.mean(
            center_pixels,
            axis=0
        )

        outer_mean = np.mean(
            outer_pixels,
            axis=0
        )

        distance = float(
            np.linalg.norm(
                center_mean
                -
                outer_mean
            )
        )

        # -----------------------------------------------------
        # Small distance means central region looks similar
        # to surrounding image.
        #
        # That can indicate weak subject/background separation.
        # -----------------------------------------------------

        separation_strength = np.clip(
            distance / 70.0,
            0.0,
            1.0
        )

        clutter_score = (
            1.0
            -
            separation_strength
        )

        return {
            "distance": round(
                distance,
                2
            ),

            "score": round(
                float(clutter_score),
                4
            )
        }

    # =========================================================
    # SUBJECT OCCUPANCY
    # =========================================================

    def _estimate_subject_occupancy(
        self,
        image: np.ndarray
    ) -> Dict[str, Any]:
        """
        Estimate how much of the image is visually different
        from the outer regions.

        This is NOT true product segmentation.

        It is only an auxiliary signal.
        """

        height, width = image.shape[:2]

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Use the outer 15% as reference.
        border = max(
            1,
            int(
                min(
                    height,
                    width
                ) * 0.15
            )
        )

        border_mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        border_mask[:border, :] = 255
        border_mask[-border:, :] = 255
        border_mask[:, :border] = 255
        border_mask[:, -border:] = 255

        background_pixels = gray[
            border_mask > 0
        ]

        if background_pixels.size == 0:

            return {
                "foreground_difference_ratio": 0.0
            }

        background_mean = float(
            np.mean(
                background_pixels
            )
        )

        difference = np.abs(
            gray.astype(
                np.float32
            )
            -
            background_mean
        )

        # Pixels sufficiently different from the estimated
        # background are counted as foreground-like.
        foreground_like = (
            difference > 25
        )

        foreground_difference_ratio = float(
            np.mean(
                foreground_like
            )
        )

        return {
            "foreground_difference_ratio": round(
                foreground_difference_ratio,
                4
            )
        }

    # =========================================================
    # FINAL SCORE
    # =========================================================

    def _calculate_background_score(
        self,
        uniformity: float,
        color_variation: float,
        edge_density: float,
        texture: float,
        separation: float
    ) -> float:
        """
        Combine measurements into one background-complexity score.

        Higher score means more evidence that background removal
        may be useful.
        """

        score = (
            self.WEIGHT_UNIFORMITY
            * uniformity
            +
            self.WEIGHT_COLOR_VARIATION
            * color_variation
            +
            self.WEIGHT_EDGE_DENSITY
            * edge_density
            +
            self.WEIGHT_TEXTURE
            * texture
            +
            self.WEIGHT_SEPARATION
            * separation
        )

        return float(
            np.clip(
                score,
                0.0,
                1.0
            )
        )

    # =========================================================
    # CLASSIFICATION
    # =========================================================

    def _classify_background(
        self,
        score: float
    ) -> tuple[str, bool]:
        """
        Convert score into a decision.

        There is an uncertain middle region.

        IMPORTANT:
            The uncertain region currently goes to removal
            because missing a genuinely cluttered background
            is more harmful to the product-photo pipeline than
            sending a questionable image to segmentation.
        """

        if (
            score
            <
            self.BACKGROUND_GOOD_THRESHOLD
        ):

            return (
                "good",
                False
            )

        if (
            score
            >=
            self.BACKGROUND_POOR_THRESHOLD
        ):

            return (
                "poor",
                True
            )

        return (
            "uncertain",
            True
        )

    # =========================================================
    # CONFIDENCE
    # =========================================================

    def _calculate_confidence(
        self,
        score: float,
        quality: str
    ) -> float:
        """
        Estimate heuristic confidence.

        This is NOT a statistical probability.
        """

        if quality == "good":

            distance = (
                self.BACKGROUND_GOOD_THRESHOLD
                -
                score
            )

            confidence = (
                0.55
                +
                distance * 1.2
            )

        elif quality == "poor":

            distance = (
                score
                -
                self.BACKGROUND_POOR_THRESHOLD
            )

            confidence = (
                0.55
                +
                distance * 1.2
            )

        else:

            confidence = 0.50

        return float(
            np.clip(
                confidence,
                0.0,
                0.99
            )
        )

    # =========================================================
    # REASONS
    # =========================================================

    def _generate_reasons(
        self,
        uniformity: Dict[str, Any],
        color_variation: Dict[str, Any],
        edge_density: Dict[str, Any],
        texture: Dict[str, Any],
        separation: Dict[str, Any],
        occupancy: Dict[str, Any],
        score: float
    ) -> list[str]:
        """
        Generate human-readable reasons.
        """

        reasons = []

        # -----------------------------------------------------
        # Uniformity
        # -----------------------------------------------------

        if uniformity["score"] < 0.20:

            reasons.append(
                "background_is_visually_uniform"
            )

        elif uniformity["score"] > 0.55:

            reasons.append(
                "background_has_high_spatial_brightness_variation"
            )

        else:

            reasons.append(
                "background_has_moderate_brightness_variation"
            )

        # -----------------------------------------------------
        # Color
        # -----------------------------------------------------

        if color_variation["score"] > 0.50:

            reasons.append(
                "background_has_high_color_variation"
            )

        elif color_variation["score"] < 0.20:

            reasons.append(
                "background_has_low_color_variation"
            )

        # -----------------------------------------------------
        # Edges
        # -----------------------------------------------------

        if edge_density["score"] > 0.50:

            reasons.append(
                "background_contains_many_structural_edges"
            )

        elif edge_density["score"] < 0.20:

            reasons.append(
                "background_has_low_edge_density"
            )

        # -----------------------------------------------------
        # Texture
        # -----------------------------------------------------

        if texture["score"] > 0.50:

            reasons.append(
                "background_contains_high_texture"
            )

        elif texture["score"] < 0.20:

            reasons.append(
                "background_has_low_texture"
            )

        # -----------------------------------------------------
        # Separation
        # -----------------------------------------------------

        if separation["score"] > 0.60:

            reasons.append(
                "subject_is_not_well_separated_from_background"
            )

        elif separation["score"] < 0.25:

            reasons.append(
                "subject_is_visually_separated_from_background"
            )

        # -----------------------------------------------------
        # Occupancy
        # -----------------------------------------------------

        if (
            occupancy[
                "foreground_difference_ratio"
            ]
            >
            0.65
        ):

            reasons.append(
                "large_part_of_image_differs_from_background_reference"
            )

        # -----------------------------------------------------
        # Final decision
        # -----------------------------------------------------

        if (
            score
            <
            self.BACKGROUND_GOOD_THRESHOLD
        ):

            reasons.append(
                "background_complexity_is_low"
            )

        elif (
            score
            >=
            self.BACKGROUND_POOR_THRESHOLD
        ):

            reasons.append(
                "background_complexity_is_high"
            )

        else:

            reasons.append(
                "background_quality_is_uncertain"
            )

        return reasons


# =============================================================
# SIMPLE FUNCTION API
# =============================================================

def analyze_background(
    image: ImageInput
) -> Dict[str, Any]:
    """
    Convenience function.

    Example:

        result = analyze_background(
            "sample.jpg"
        )
    """

    analyzer = BackgroundAnalyzer()

    return analyzer.analyze(
        image
    )


# =============================================================
# COMMAND LINE TEST
# =============================================================

if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "python background_analyzer.py "
            "<image_path>"
        )

        sys.exit(1)

    image_path = sys.argv[1]

    result = analyze_background(
        image_path
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )