"""
CraftMitra - Image Analyzer

Lightweight computer-vision based image analysis.

Purpose:
    Analyze an artisan's product photograph before enhancement.

The analyzer does NOT modify the image.
It only measures image properties and recommends which
enhancement operations may be useful.

Designed to:
    - Run on CPU
    - Work without a GPU
    - Require no AI model
    - Handle arbitrary image dimensions
    - Be inexpensive enough for real-world deployment
"""

from pathlib import Path
from typing import Any, Dict, Union

import cv2
import numpy as np


ImageInput = Union[str, Path, np.ndarray]


class ImageAnalyzer:
    """
    Lightweight analyzer for real-world artisan photographs.
    """

    # We do not need the full-resolution image for analysis.
    # Limiting the largest dimension keeps processing lightweight.
    MAX_ANALYSIS_SIZE = 1280

    # Conservative thresholds.
    # These are intentionally not aggressive because different
    # artisan products naturally have different appearances.
    DARK_MEAN_THRESHOLD = 75
    BRIGHT_MEAN_THRESHOLD = 205

    LOW_CONTRAST_THRESHOLD = 35

    HIGH_DARK_PIXEL_RATIO = 0.25
    HIGH_BRIGHT_PIXEL_RATIO = 0.25

    # Laplacian variance is used as a blur/sharpness indicator.
    # These values are only heuristic indicators, not absolute truth.
    VERY_BLURRY_THRESHOLD = 50
    BLURRY_THRESHOLD = 100

    def __init__(self, max_analysis_size: int = MAX_ANALYSIS_SIZE):
        self.max_analysis_size = max_analysis_size

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def analyze(self, image: ImageInput) -> Dict[str, Any]:
        """
        Analyze an image.

        Args:
            image:
                Either:
                    - image file path
                    - pathlib.Path
                    - OpenCV/Numpy image array

        Returns:
            Dictionary containing:
                - dimensions
                - brightness
                - contrast
                - sharpness
                - exposure
                - color information
                - quality assessment
                - enhancement recommendations
        """

        img = self._load_image(image)

        original_height, original_width = img.shape[:2]

        analysis_img = self._resize_for_analysis(img)

        gray = cv2.cvtColor(analysis_img, cv2.COLOR_BGR2GRAY)

        hsv = cv2.cvtColor(analysis_img, cv2.COLOR_BGR2HSV)

        brightness = self._analyze_brightness(gray)

        contrast = self._analyze_contrast(gray)

        sharpness = self._analyze_sharpness(gray)

        exposure = self._analyze_exposure(gray)

        color = self._analyze_color(hsv)

        resolution = self._analyze_resolution(
            original_width,
            original_height
        )

        quality = self._assess_quality(
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            exposure=exposure,
            resolution=resolution
        )

        recommendations = self._generate_recommendations(
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            exposure=exposure,
            resolution=resolution
        )

        return {
            "image": {
                "width": original_width,
                "height": original_height,
                "aspect_ratio": round(
                    original_width / original_height,
                    3
                ),
                "orientation": self._get_orientation(
                    original_width,
                    original_height
                ),
            },

            "brightness": brightness,

            "contrast": contrast,

            "sharpness": sharpness,

            "exposure": exposure,

            "color": color,

            "resolution": resolution,

            "quality": quality,

            "recommendations": recommendations,
        }

    # ---------------------------------------------------------
    # IMAGE LOADING
    # ---------------------------------------------------------

    def _load_image(self, image: ImageInput) -> np.ndarray:
        """
        Load and validate an image.
        """

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

        elif isinstance(image, np.ndarray):

            img = image

            if img.size == 0:
                raise ValueError("Image array is empty.")

            if img.ndim == 2:
                img = cv2.cvtColor(
                    img,
                    cv2.COLOR_GRAY2BGR
                )

            elif img.ndim == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(
                    img,
                    cv2.COLOR_BGRA2BGR
                )

            elif img.ndim != 3 or img.shape[2] != 3:
                raise ValueError(
                    "Unsupported image array format."
                )

        else:
            raise TypeError(
                "Image must be a file path or NumPy array."
            )

        return img

    # ---------------------------------------------------------
    # RESIZING
    # ---------------------------------------------------------

    def _resize_for_analysis(
        self,
        image: np.ndarray
    ) -> np.ndarray:
        """
        Resize only for analysis.

        The original image is NEVER modified.
        """

        height, width = image.shape[:2]

        largest_dimension = max(
            height,
            width
        )

        if largest_dimension <= self.max_analysis_size:
            return image

        scale = (
            self.max_analysis_size /
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

    # ---------------------------------------------------------
    # BRIGHTNESS
    # ---------------------------------------------------------

    def _analyze_brightness(
        self,
        gray: np.ndarray
    ) -> Dict[str, Any]:

        mean = float(np.mean(gray))

        median = float(np.median(gray))

        percentile_10 = float(
            np.percentile(gray, 10)
        )

        percentile_90 = float(
            np.percentile(gray, 90)
        )

        if mean < self.DARK_MEAN_THRESHOLD:
            condition = "dark"

        elif mean > self.BRIGHT_MEAN_THRESHOLD:
            condition = "bright"

        else:
            condition = "normal"

        return {
            "mean": round(mean, 2),
            "median": round(median, 2),
            "percentile_10": round(
                percentile_10,
                2
            ),
            "percentile_90": round(
                percentile_90,
                2
            ),
            "condition": condition,
        }

    # ---------------------------------------------------------
    # CONTRAST
    # ---------------------------------------------------------

    def _analyze_contrast(
        self,
        gray: np.ndarray
    ) -> Dict[str, Any]:

        standard_deviation = float(
            np.std(gray)
        )

        dynamic_range = float(
            np.percentile(gray, 95)
            -
            np.percentile(gray, 5)
        )

        if standard_deviation < self.LOW_CONTRAST_THRESHOLD:
            condition = "low"

        else:
            condition = "normal"

        return {
            "standard_deviation": round(
                standard_deviation,
                2
            ),
            "dynamic_range": round(
                dynamic_range,
                2
            ),
            "condition": condition,
        }

    # ---------------------------------------------------------
    # SHARPNESS
    # ---------------------------------------------------------

    def _analyze_sharpness(
        self,
        gray: np.ndarray
    ) -> Dict[str, Any]:

        laplacian = cv2.Laplacian(
            gray,
            cv2.CV_64F
        )

        laplacian_variance = float(
            laplacian.var()
        )

        if laplacian_variance < self.VERY_BLURRY_THRESHOLD:
            condition = "very_blurry"

        elif laplacian_variance < self.BLURRY_THRESHOLD:
            condition = "blurry"

        else:
            condition = "acceptable"

        return {
            "laplacian_variance": round(
                laplacian_variance,
                2
            ),
            "condition": condition,
        }

    # ---------------------------------------------------------
    # EXPOSURE
    # ---------------------------------------------------------

    def _analyze_exposure(
        self,
        gray: np.ndarray
    ) -> Dict[str, Any]:

        total_pixels = gray.size

        dark_pixels = np.sum(gray <= 20)

        bright_pixels = np.sum(gray >= 235)

        dark_ratio = (
            float(dark_pixels) /
            total_pixels
        )

        bright_ratio = (
            float(bright_pixels) /
            total_pixels
        )

        underexposed = (
            dark_ratio >= self.HIGH_DARK_PIXEL_RATIO
        )

        overexposed = (
            bright_ratio >= self.HIGH_BRIGHT_PIXEL_RATIO
        )

        if underexposed and overexposed:
            condition = "high_dynamic_range"

        elif underexposed:
            condition = "underexposed"

        elif overexposed:
            condition = "overexposed"

        else:
            condition = "balanced"

        return {
            "dark_pixel_ratio": round(
                dark_ratio,
                3
            ),
            "bright_pixel_ratio": round(
                bright_ratio,
                3
            ),
            "condition": condition,
        }

    # ---------------------------------------------------------
    # COLOR
    # ---------------------------------------------------------

    def _analyze_color(
        self,
        hsv: np.ndarray
    ) -> Dict[str, Any]:

        saturation = hsv[:, :, 1]

        mean_saturation = float(
            np.mean(saturation)
        )

        return {
            "mean_saturation": round(
                mean_saturation,
                2
            )
        }

    # ---------------------------------------------------------
    # RESOLUTION
    # ---------------------------------------------------------

    def _analyze_resolution(
        self,
        width: int,
        height: int
    ) -> Dict[str, Any]:

        megapixels = (
            width * height
        ) / 1_000_000

        minimum_dimension = min(
            width,
            height
        )

        if minimum_dimension < 480:
            condition = "low"

        elif minimum_dimension < 720:
            condition = "moderate"

        else:
            condition = "good"

        return {
            "megapixels": round(
                megapixels,
                2
            ),
            "minimum_dimension": minimum_dimension,
            "condition": condition,
        }

    # ---------------------------------------------------------
    # OVERALL QUALITY
    # ---------------------------------------------------------

    def _assess_quality(
        self,
        brightness: Dict[str, Any],
        contrast: Dict[str, Any],
        sharpness: Dict[str, Any],
        exposure: Dict[str, Any],
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:

        issues = []

        if brightness["condition"] == "dark":
            issues.append("low_brightness")

        if brightness["condition"] == "bright":
            issues.append("high_brightness")

        if contrast["condition"] == "low":
            issues.append("low_contrast")

        if sharpness["condition"] in {
            "blurry",
            "very_blurry"
        }:
            issues.append("low_sharpness")

        if exposure["condition"] == "underexposed":
            issues.append("underexposure")

        if exposure["condition"] == "overexposed":
            issues.append("overexposure")

        if resolution["condition"] == "low":
            issues.append("low_resolution")

        if not issues:
            overall = "good"

        elif len(issues) <= 2:
            overall = "needs_improvement"

        else:
            overall = "poor"

        return {
            "overall": overall,
            "issues": issues,
        }

    # ---------------------------------------------------------
    # RECOMMENDATIONS
    # ---------------------------------------------------------

    def _generate_recommendations(
        self,
        brightness: Dict[str, Any],
        contrast: Dict[str, Any],
        sharpness: Dict[str, Any],
        exposure: Dict[str, Any],
        resolution: Dict[str, Any]
    ) -> Dict[str, bool]:

        return {
            "lighting_correction": (
                brightness["condition"] != "normal"
                or
                exposure["condition"] in {
                    "underexposed",
                    "overexposed"
                }
            ),

            "contrast_enhancement": (
                contrast["condition"] == "low"
            ),

            "sharpness_enhancement": (
                sharpness["condition"] in {
                    "blurry",
                    "very_blurry"
                }
            ),

            "upscaling": (
                resolution["condition"] == "low"
            ),
        }

    # ---------------------------------------------------------
    # ORIENTATION
    # ---------------------------------------------------------

    @staticmethod
    def _get_orientation(
        width: int,
        height: int
    ) -> str:

        if width > height:
            return "landscape"

        if height > width:
            return "portrait"

        return "square"


# -------------------------------------------------------------
# SIMPLE FUNCTION API
# -------------------------------------------------------------

def analyze_image(
    image: ImageInput
) -> Dict[str, Any]:
    """
    Convenience function.

    Example:

        result = analyze_image("sample.jpg")
    """

    analyzer = ImageAnalyzer()

    return analyzer.analyze(image)


# -------------------------------------------------------------
# COMMAND LINE TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python image_analyzer.py <image_path>"
        )
        sys.exit(1)

    image_path = sys.argv[1]

    result = analyze_image(image_path)

    print(
        json.dumps(
            result,
            indent=4
        )
    )