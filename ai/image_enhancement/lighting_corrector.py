"""
CraftMitra - Adaptive Lighting Corrector

Purpose:
    Correct poor or uneven lighting in artisan photographs while
    preserving the original product colors and natural appearance.

Design goals:
    - CPU only
    - No deep-learning model
    - No GPU required
    - Works with arbitrary photographs
    - Uses ImageAnalyzer recommendations
    - Avoids unnecessary processing
    - Preserves product colors
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

import cv2
import numpy as np

from image_analyzer import ImageAnalyzer


ImageInput = Union[str, Path, np.ndarray]


class LightingCorrector:
    """
    Adaptive lighting correction for real-world artisan photographs.

    The corrector does not blindly brighten every image.

    It first analyzes the image and determines whether correction
    is actually necessary.
    """

    # ---------------------------------------------------------
    # SAFETY LIMITS
    # ---------------------------------------------------------

    MAX_ANALYSIS_SIZE = 1280

    # If correction is extremely small, leave image untouched.
    MIN_CORRECTION_STRENGTH = 0.03

    # Maximum strength of global gamma correction.
    MAX_GAMMA_ADJUSTMENT = 0.18

    # Local illumination correction strength.
    LOCAL_CORRECTION_STRENGTH = 0.35

    # Minimum and maximum allowed pixel change.
    # The actual value is calculated adaptively.
    MIN_MAX_CHANGE = 30.0
    MAX_MAX_CHANGE = 90.0

    def __init__(
        self,
        analyzer: Optional[ImageAnalyzer] = None
    ):
        self.analyzer = analyzer or ImageAnalyzer()

    # =========================================================
    # PUBLIC API
    # =========================================================

    def correct(
        self,
        image: ImageInput,
        analysis: Optional[Dict[str, Any]] = None
    ) -> tuple[np.ndarray, Dict[str, Any]]:
        """
        Correct image lighting adaptively.

        Args:
            image:
                Image path or OpenCV NumPy image.

            analysis:
                Optional result from ImageAnalyzer.

        Returns:
            corrected_image, correction_report
        """

        original = self._load_image(image)

        if analysis is None:
            analysis = self.analyzer.analyze(original)

        corrected = original.copy()

        brightness = analysis["brightness"]
        exposure = analysis["exposure"]

        brightness_condition = brightness["condition"]
        exposure_condition = exposure["condition"]

        operations = []

        # -----------------------------------------------------
        # 1. Determine whether correction is required
        # -----------------------------------------------------

        needs_correction = (
            brightness_condition != "normal"
            or exposure_condition in {
                "underexposed",
                "overexposed"
            }
        )

        # Also detect uneven illumination.
        uneven_score = self._calculate_uneven_lighting(
            original
        )

        uneven_lighting = uneven_score > 0.18

        # -----------------------------------------------------
        # IMPORTANT:
        # If image is already well exposed and evenly lit,
        # do not modify it.
        # -----------------------------------------------------

        if not needs_correction and not uneven_lighting:

            report = {
                "correction_applied": False,
                "reason": "Lighting already acceptable",
                "operations": [],
                "uneven_lighting_score": round(
                    uneven_score,
                    4
                )
            }

            return corrected, report

        # -----------------------------------------------------
        # 2. Correct global exposure
        # -----------------------------------------------------

        if exposure_condition == "underexposed":

            corrected = self._correct_underexposure(
                corrected,
                brightness
            )

            operations.append(
                "underexposure_correction"
            )

        elif exposure_condition == "overexposed":

            corrected = self._correct_overexposure(
                corrected
            )

            operations.append(
                "highlight_protection"
            )

        elif brightness_condition == "dark":

            corrected = self._correct_dark_image(
                corrected,
                brightness
            )

            operations.append(
                "brightness_correction"
            )

        elif brightness_condition == "bright":

            corrected = self._correct_bright_image(
                corrected,
                brightness
            )

            operations.append(
                "brightness_reduction"
            )

        # -----------------------------------------------------
        # 3. Correct uneven lighting
        # -----------------------------------------------------

        if uneven_lighting:

            corrected = self._correct_uneven_lighting(
                corrected
            )

            operations.append(
                "local_illumination_correction"
            )

        # -----------------------------------------------------
        # 4. Protect colors
        # -----------------------------------------------------

        corrected = self._preserve_colors(
            original,
            corrected
        )

        # -----------------------------------------------------
        # 5. Prevent extreme changes
        #
        # The maximum allowed change is calculated from the
        # actual lighting severity instead of using one fixed
        # value for every image.
        # -----------------------------------------------------

        max_change = self._calculate_max_change(
            brightness=brightness,
            exposure=exposure,
            uneven_score=uneven_score
        )

        corrected = self._limit_change(
            original,
            corrected,
            max_change
        )

        report = {
            "correction_applied": len(operations) > 0,
            "operations": operations,
            "uneven_lighting_score": round(
                uneven_score,
                4
            ),
            "max_change": round(
                max_change,
                2
            )
        }

        return corrected, report

    # =========================================================
    # IMAGE LOADING
    # =========================================================

    @staticmethod
    def _load_image(
        image: ImageInput
    ) -> np.ndarray:

        if isinstance(image, (str, Path)):

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

        if isinstance(image, np.ndarray):

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
    # UNDEREXPOSURE
    # =========================================================

    def _correct_underexposure(
        self,
        image: np.ndarray,
        brightness: Dict[str, Any]
    ) -> np.ndarray:
        """
        Adaptively brighten a genuinely underexposed image.

        The correction uses:
            - mean brightness
            - median brightness
            - dark-pixel ratio

        This prevents the algorithm from relying on one metric
        alone.

        Very dark images receive stronger correction.
        Moderately dark images receive milder correction.
        """

        mean = float(
            brightness.get("mean", 128)
        )

        median = float(
            brightness.get("median", mean)
        )

        # The analyzer provides this value under exposure,
        # but we use it here only if available.
        dark_ratio = float(
            brightness.get("dark_pixel_ratio", 0.0)
        )

        # -----------------------------------------------------
        # 1. Calculate brightness severity
        #
        # 145 is our desired general working brightness.
        #
        # Values near 145 -> low severity.
        # Very low values -> high severity.
        # -----------------------------------------------------

        mean_severity = np.clip(
            (145.0 - mean) / 125.0,
            0.0,
            1.0
        )

        median_severity = np.clip(
            (145.0 - median) / 125.0,
            0.0,
            1.0
        )

        # -----------------------------------------------------
        # 2. Dark pixel severity
        #
        # 25% is the analyzer's underexposure threshold.
        # More dark pixels means more confidence that the
        # image really needs stronger correction.
        # -----------------------------------------------------

        dark_severity = np.clip(
            (dark_ratio - 0.15) / 0.60,
            0.0,
            1.0
        )

        # -----------------------------------------------------
        # 3. Combine the measurements
        #
        # Mean gets the highest weight.
        # Median helps prevent a few bright regions from
        # hiding a generally dark image.
        # Dark ratio confirms widespread underexposure.
        # -----------------------------------------------------

        severity = (
            0.45 * mean_severity
            +
            0.35 * median_severity
            +
            0.20 * dark_severity
        )

        severity = float(
            np.clip(
                severity,
                0.0,
                1.0
            )
        )

        # -----------------------------------------------------
        # 4. Adaptive gamma
        #
        # severity 0 -> gamma approximately 1.00
        # severity 1 -> gamma approximately 0.55
        #
        # This is intentionally bounded.
        # We never allow an arbitrary extreme gamma.
        # -----------------------------------------------------

        gamma = (
            1.0
            -
            0.45 * severity
        )

        gamma = float(
            np.clip(
                gamma,
                0.55,
                1.0
            )
        )

        return self._apply_gamma(
            image,
            gamma
        )

    # =========================================================
    # DARK IMAGE
    # =========================================================

    def _correct_dark_image(
        self,
        image: np.ndarray,
        brightness: Dict[str, Any]
    ) -> np.ndarray:

        mean = brightness["mean"]

        # Mild adaptive gamma.
        difference = 145 - mean

        strength = np.clip(
            difference / 100.0,
            0.0,
            1.0
        )

        gamma = 1.0 - (
            self.MAX_GAMMA_ADJUSTMENT
            * strength
        )

        return self._apply_gamma(
            image,
            gamma
        )

    # =========================================================
    # OVEREXPOSURE
    # =========================================================

    def _correct_overexposure(
        self,
        image: np.ndarray
    ) -> np.ndarray:

        lab = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2LAB
        )

        l, a, b = cv2.split(lab)

        # Compress highlights gradually rather than simply
        # lowering brightness.
        l_float = l.astype(np.float32)

        highlight_mask = l_float > 190

        excess = (
            l_float[highlight_mask] - 190
        )

        l_float[highlight_mask] = (
            190
            + excess * 0.55
        )

        l = np.clip(
            l_float,
            0,
            255
        ).astype(np.uint8)

        return cv2.cvtColor(
            cv2.merge((l, a, b)),
            cv2.COLOR_LAB2BGR
        )

    # =========================================================
    # BRIGHT IMAGE
    # =========================================================

    def _correct_bright_image(
        self,
        image: np.ndarray,
        brightness: Dict[str, Any]
    ) -> np.ndarray:

        mean = brightness["mean"]

        difference = mean - 175

        strength = np.clip(
            difference / 100.0,
            0.0,
            1.0
        )

        gamma = 1.0 + (
            self.MAX_GAMMA_ADJUSTMENT
            * strength
        )

        return self._apply_gamma(
            image,
            gamma
        )

    # =========================================================
    # GAMMA
    # =========================================================

    @staticmethod
    def _apply_gamma(
        image: np.ndarray,
        gamma: float
    ) -> np.ndarray:

        gamma = float(
            np.clip(
                gamma,
                0.55,
                1.25
            )
        )

        lookup_table = np.array(
            [
                ((i / 255.0) ** gamma) * 255
                for i in range(256)
            ],
            dtype=np.uint8
        )

        return cv2.LUT(
            image,
            lookup_table
        )

    # =========================================================
    # UNEVEN LIGHTING DETECTION
    # =========================================================

    def _calculate_uneven_lighting(
        self,
        image: np.ndarray
    ) -> float:

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Estimate low-frequency illumination.
        illumination = cv2.GaussianBlur(
            gray,
            (0, 0),
            sigmaX=25
        )

        mean = float(
            np.mean(illumination)
        )

        if mean <= 1:
            return 0.0

        std = float(
            np.std(illumination)
        )

        # Coefficient of variation.
        score = std / mean

        return float(
            np.clip(
                score,
                0.0,
                1.0
            )
        )

    # =========================================================
    # UNEVEN LIGHTING CORRECTION
    # =========================================================

    def _correct_uneven_lighting(
        self,
        image: np.ndarray
    ) -> np.ndarray:

        lab = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2LAB
        )

        l, a, b = cv2.split(lab)

        l_float = l.astype(
            np.float32
        )

        # Estimate illumination field.
        illumination = cv2.GaussianBlur(
            l_float,
            (0, 0),
            sigmaX=25
        )

        global_mean = np.mean(
            illumination
        )

        # Avoid division by zero.
        illumination = np.maximum(
            illumination,
            1.0
        )

        # Normalize illumination.
        normalized = (
            l_float
            *
            (
                global_mean /
                illumination
            )
        )

        # Blend rather than fully applying normalization.
        strength = self.LOCAL_CORRECTION_STRENGTH

        corrected_l = (
            l_float * (1.0 - strength)
            +
            normalized * strength
        )

        corrected_l = np.clip(
            corrected_l,
            0,
            255
        ).astype(np.uint8)

        return cv2.cvtColor(
            cv2.merge(
                (
                    corrected_l,
                    a,
                    b
                )
            ),
            cv2.COLOR_LAB2BGR
        )

    # =========================================================
    # COLOR PRESERVATION
    # =========================================================

    @staticmethod
    def _preserve_colors(
        original: np.ndarray,
        corrected: np.ndarray
    ) -> np.ndarray:

        original_lab = cv2.cvtColor(
            original,
            cv2.COLOR_BGR2LAB
        )

        corrected_lab = cv2.cvtColor(
            corrected,
            cv2.COLOR_BGR2LAB
        )

        # Keep original chromatic information.
        #
        # Lighting correction should primarily affect
        # luminance, not the actual product color.
        corrected_lab[:, :, 1] = (
            0.75 * original_lab[:, :, 1]
            +
            0.25 * corrected_lab[:, :, 1]
        ).astype(np.uint8)

        corrected_lab[:, :, 2] = (
            0.75 * original_lab[:, :, 2]
            +
            0.25 * corrected_lab[:, :, 2]
        ).astype(np.uint8)

        return cv2.cvtColor(
            corrected_lab,
            cv2.COLOR_LAB2BGR
        )

    # =========================================================
    # ADAPTIVE SAFETY LIMIT
    # =========================================================

    def _calculate_max_change(
        self,
        brightness: Dict[str, Any],
        exposure: Dict[str, Any],
        uneven_score: float
    ) -> float:
        """
        Calculate the maximum allowed pixel change according
        to the severity of the lighting problem.

        This is intentionally adaptive.

        Mild problem:
            smaller safety limit.

        Severe underexposure:
            larger safety limit.

        Uneven lighting:
            slightly increases the allowed limit.

        The result is always bounded between
        MIN_MAX_CHANGE and MAX_MAX_CHANGE.
        """

        mean = float(
            brightness.get("mean", 128)
        )

        median = float(
            brightness.get("median", mean)
        )

        dark_ratio = float(
            exposure.get("dark_pixel_ratio", 0.0)
        )

        # -----------------------------------------------------
        # Brightness severity
        # -----------------------------------------------------

        mean_severity = np.clip(
            (145.0 - mean) / 125.0,
            0.0,
            1.0
        )

        median_severity = np.clip(
            (145.0 - median) / 125.0,
            0.0,
            1.0
        )

        dark_severity = np.clip(
            (dark_ratio - 0.15) / 0.60,
            0.0,
            1.0
        )

        severity = (
            0.45 * mean_severity
            +
            0.35 * median_severity
            +
            0.20 * dark_severity
        )

        # -----------------------------------------------------
        # Exposure type adjustment
        # -----------------------------------------------------

        if exposure.get("condition") == "underexposed":

            severity += 0.10

        elif exposure.get("condition") == "overexposed":

            severity += 0.02

        # -----------------------------------------------------
        # Uneven lighting adjustment
        #
        # Strongly uneven lighting may need a little more
        # room for local illumination correction.
        # -----------------------------------------------------

        uneven_strength = np.clip(
            (uneven_score - 0.18) / 0.50,
            0.0,
            1.0
        )

        severity += (
            0.10 * uneven_strength
        )

        severity = float(
            np.clip(
                severity,
                0.0,
                1.0
            )
        )

        # -----------------------------------------------------
        # Map severity to pixel-change limit.
        #
        # 0 severity -> 30
        # 1 severity -> 90
        # -----------------------------------------------------

        max_change = (
            self.MIN_MAX_CHANGE
            +
            (
                self.MAX_MAX_CHANGE
                -
                self.MIN_MAX_CHANGE
            )
            * severity
        )

        return float(
            np.clip(
                max_change,
                self.MIN_MAX_CHANGE,
                self.MAX_MAX_CHANGE
            )
        )

    # =========================================================
    # SAFETY LIMIT
    # =========================================================

    @staticmethod
    def _limit_change(
        original: np.ndarray,
        corrected: np.ndarray,
        max_change: float = 45.0
    ) -> np.ndarray:
        """
        Prevent extreme pixel-level changes.

        max_change is supplied by the adaptive lighting
        severity calculation.
        """

        original_float = (
            original.astype(np.float32)
        )

        corrected_float = (
            corrected.astype(np.float32)
        )

        max_change = float(
            np.clip(
                max_change,
                30.0,
                90.0
            )
        )

        difference = (
            corrected_float
            -
            original_float
        )

        difference = np.clip(
            difference,
            -max_change,
            max_change
        )

        result = (
            original_float
            +
            difference
        )

        return np.clip(
            result,
            0,
            255
        ).astype(np.uint8)


# =============================================================
# SIMPLE FUNCTION API
# =============================================================

def correct_lighting(
    image: ImageInput,
    analysis: Optional[Dict[str, Any]] = None
) -> tuple[np.ndarray, Dict[str, Any]]:
    """
    Convenience function.

    Example:

        corrected, report = correct_lighting(
            "samplePottery.png"
        )
    """

    corrector = LightingCorrector()

    return corrector.correct(
        image,
        analysis
    )


# =============================================================
# COMMAND LINE TEST
# =============================================================

if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) != 3:

        print(
            "Usage:"
        )

        print(
            "python lighting_corrector.py "
            "<input_image> <output_image>"
        )

        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    analyzer = ImageAnalyzer()

    analysis = analyzer.analyze(
        input_path
    )

    corrector = LightingCorrector(
        analyzer
    )

    corrected, report = corrector.correct(
        input_path,
        analysis
    )

    success = cv2.imwrite(
        output_path,
        corrected
    )

    if not success:

        raise RuntimeError(
            f"Could not save output: {output_path}"
        )

    print(
        json.dumps(
            report,
            indent=4
        )
    )