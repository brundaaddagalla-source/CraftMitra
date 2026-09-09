"""
CraftMitra - Background Generator

Purpose:
    Generate a clean replacement background for artisan product
    photographs.

Important:
    This module ONLY generates the replacement background.

    It does NOT:
    - detect the product
    - remove the original background
    - generate a foreground mask
    - perform lighting correction
    - composite the product onto the background

Design goals:
    - Reliable
    - Lightweight
    - No external AI model
    - No additional model download
    - Works with arbitrary image dimensions
    - Suitable for artisan product photography
    - Produces something better than a pure white background

The generated background contains:
    1. A soft vertical studio gradient
    2. A subtle floor/background transition
    3. A soft lower-region variation
    4. Optional subtle vignette

The result is intended to be used later by
background_compositor.py together with a refined foreground mask.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple, Union

import cv2
import numpy as np


ImageInput = Union[str, Path, np.ndarray]


class BackgroundGenerator:
    """
    Generate a clean studio-style replacement background.

    The generated background does not depend on the product itself.
    It only depends on the requested output dimensions.
    """

    # =========================================================
    # BACKGROUND CONFIGURATION
    # =========================================================

    # RGB colors used for the upper and lower parts of the
    # background.

    TOP_COLOR = (238, 242, 241)
    MIDDLE_COLOR = (224, 231, 230)
    BOTTOM_COLOR = (205, 214, 213)

    # Position where the floor region begins.
    FLOOR_START = 0.68

    # Strength of the floor transition.
    FLOOR_TRANSITION = 0.18

    # Very subtle vignette.
    VIGNETTE_STRENGTH = 0.08

    # =========================================================
    # PUBLIC API
    # =========================================================

    def generate(
        self,
        image: ImageInput
    ) -> np.ndarray:
        """
        Generate a replacement background having the same
        dimensions as the input image.

        Parameters
        ----------
        image:
            Either:
                - image file path
                - pathlib.Path
                - OpenCV NumPy image

        Returns
        -------
        np.ndarray
            Generated BGR background image.
        """

        source = self._load_image(image)

        height, width = source.shape[:2]

        return self.generate_for_size(
            width=width,
            height=height
        )

    def generate_for_size(
        self,
        width: int,
        height: int
    ) -> np.ndarray:
        """
        Generate a background for explicit dimensions.

        Parameters
        ----------
        width:
            Output width.

        height:
            Output height.

        Returns
        -------
        np.ndarray
            Generated BGR background.
        """

        self._validate_dimensions(
            width,
            height
        )

        background = self._create_vertical_gradient(
            width,
            height
        )

        background = self._add_floor_transition(
            background
        )

        background = self._add_subtle_vignette(
            background
        )

        return np.clip(
            background,
            0,
            255
        ).astype(
            np.uint8
        )

    # =========================================================
    # IMAGE LOADING
    # =========================================================

    @staticmethod
    def _load_image(
        image: ImageInput
    ) -> np.ndarray:
        """
        Load an image only to obtain its dimensions.
        """

        # -----------------------------------------------------
        # IMAGE PATH
        # -----------------------------------------------------

        if isinstance(
            image,
            (str, Path)
        ):

            path = Path(image)

            if not path.exists():

                raise FileNotFoundError(
                    f"Image not found: {path}"
                )

            if not path.is_file():

                raise ValueError(
                    f"Image path is not a file: {path}"
                )

            loaded = cv2.imread(
                str(path),
                cv2.IMREAD_COLOR
            )

            if loaded is None:

                raise ValueError(
                    f"Unable to read image: {path}"
                )

            return loaded

        # -----------------------------------------------------
        # NUMPY IMAGE
        # -----------------------------------------------------

        if isinstance(
            image,
            np.ndarray
        ):

            if image.size == 0:

                raise ValueError(
                    "Image array is empty."
                )

            if image.ndim not in (2, 3):

                raise ValueError(
                    "Unsupported image dimensions."
                )

            return image

        raise TypeError(
            "Image must be a path or NumPy array."
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_dimensions(
        width: int,
        height: int
    ) -> None:
        """
        Validate requested output dimensions.
        """

        if not isinstance(
            width,
            int
        ) or not isinstance(
            height,
            int
        ):

            raise TypeError(
                "Width and height must be integers."
            )

        if width <= 0 or height <= 0:

            raise ValueError(
                "Width and height must be greater than zero."
            )

    # =========================================================
    # VERTICAL GRADIENT
    # =========================================================

    def _create_vertical_gradient(
        self,
        width: int,
        height: int
    ) -> np.ndarray:
        """
        Create a smooth vertical studio gradient.

        The gradient prevents the replacement background from
        looking like a completely flat white canvas.
        """

        top = np.array(
            self.TOP_COLOR,
            dtype=np.float32
        )

        middle = np.array(
            self.MIDDLE_COLOR,
            dtype=np.float32
        )

        bottom = np.array(
            self.BOTTOM_COLOR,
            dtype=np.float32
        )

        result = np.zeros(
            (
                height,
                width,
                3
            ),
            dtype=np.float32
        )

        midpoint = max(
            1,
            int(
                height * 0.55
            )
        )

        # -----------------------------------------------------
        # TOP -> MIDDLE
        # -----------------------------------------------------

        for y in range(midpoint):

            ratio = y / max(
                midpoint - 1,
                1
            )

            color = (
                top * (1.0 - ratio)
                +
                middle * ratio
            )

            result[y, :, :] = color

        # -----------------------------------------------------
        # MIDDLE -> BOTTOM
        # -----------------------------------------------------

        for y in range(
            midpoint,
            height
        ):

            ratio = (
                (y - midpoint)
                /
                max(
                    height - midpoint - 1,
                    1
                )
            )

            color = (
                middle * (1.0 - ratio)
                +
                bottom * ratio
            )

            result[y, :, :] = color

        return result

    # =========================================================
    # FLOOR TRANSITION
    # =========================================================

    def _add_floor_transition(
        self,
        background: np.ndarray
    ) -> np.ndarray:
        """
        Add a subtle floor/background transition.

        This gives the final composition some depth instead of
        making the product appear to float on a completely flat
        background.
        """

        height, width = background.shape[:2]

        start_y = int(
            height * self.FLOOR_START
        )

        transition_height = max(
            1,
            int(
                height * self.FLOOR_TRANSITION
            )
        )

        result = background.copy()

        for y in range(
            start_y,
            height
        ):

            distance = y - start_y

            ratio = np.clip(
                distance /
                transition_height,
                0.0,
                1.0
            )

            # Very subtle darkening toward the lower region.
            factor = 1.0 - (
                0.035 * ratio
            )

            result[y] *= factor

        return result

    # =========================================================
    # VIGNETTE
    # =========================================================

    def _add_subtle_vignette(
        self,
        background: np.ndarray
    ) -> np.ndarray:
        """
        Add a very subtle edge falloff.

        This is intentionally weak so that the generated
        background remains natural.
        """

        height, width = background.shape[:2]

        y_indices, x_indices = np.indices(
            (
                height,
                width
            ),
            dtype=np.float32
        )

        center_x = (
            width - 1
        ) / 2.0

        center_y = (
            height - 1
        ) / 2.0

        normalized_x = (
            x_indices - center_x
        ) / max(
            center_x,
            1.0
        )

        normalized_y = (
            y_indices - center_y
        ) / max(
            center_y,
            1.0
        )

        distance = np.sqrt(
            normalized_x ** 2
            +
            normalized_y ** 2
        )

        distance = np.clip(
            distance,
            0.0,
            1.0
        )

        factor = 1.0 - (
            self.VIGNETTE_STRENGTH
            *
            distance
            *
            distance
        )

        return (
            background
            *
            factor[:, :, None]
        )

    # =========================================================
    # SAVE BACKGROUND
    # =========================================================

    @staticmethod
    def save_background(
        background: np.ndarray,
        output_path: Union[str, Path]
    ) -> None:
        """
        Save a generated background to disk.
        """

        if background is None:

            raise ValueError(
                "Background is None."
            )

        if background.size == 0:

            raise ValueError(
                "Background is empty."
            )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        success = cv2.imwrite(
            str(output_path),
            background
        )

        if not success:

            raise IOError(
                f"Unable to save background: {output_path}"
            )


# =============================================================
# SIMPLE FUNCTION API
# =============================================================

def generate_background(
    image: ImageInput
) -> np.ndarray:
    """
    Convenience function.

    Example:

        background = generate_background(
            "data/sampleImages/BlendBGImage.png"
        )
    """

    generator = BackgroundGenerator()

    return generator.generate(
        image
    )


# =============================================================
# COMMAND LINE TEST
# =============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) != 3:

        print(
            "Usage:"
        )

        print(
            "python background_generator.py "
            "<input_image> "
            "<output_background>"
        )

        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    generator = BackgroundGenerator()

    background = generator.generate(
        input_path
    )

    generator.save_background(
        background,
        output_path
    )

    print(
        "Background generated successfully."
    )

    print(
        f"Output: {output_path}"
    )

    print(
        f"Dimensions: "
        f"{background.shape[1]}x"
        f"{background.shape[0]}"
    )