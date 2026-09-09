"""
CraftMitra - Mask Applier

Purpose:
    Apply foreground masks to product images and generate
    transparent-background foreground images.

This module is used to visually compare:
    1. Original image
    2. Raw U²-Net mask result
    3. Refined mask result

It does NOT:
    - generate a new background
    - analyze the background
    - generate the mask
    - modify the original image

Input:
    image + foreground mask

Output:
    RGBA image with background made transparent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import cv2
import numpy as np


ImageInput = Union[str, Path, np.ndarray]
MaskInput = Union[str, Path, np.ndarray]


class MaskApplier:

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def apply_mask(
        self,
        image: ImageInput,
        mask: MaskInput
    ) -> np.ndarray:
        """
        Apply a grayscale foreground mask to an image.

        Mask meaning:

            0   = transparent/background
            255 = foreground/product

        Returns:
            RGBA image.
        """

        image_array = self._load_image(image)
        mask_array = self._load_mask(mask)

        # -----------------------------------------------------
        # Ensure mask matches image dimensions
        # -----------------------------------------------------

        image_height, image_width = image_array.shape[:2]

        if mask_array.shape[:2] != (
            image_height,
            image_width
        ):

            mask_array = cv2.resize(
                mask_array,
                (image_width, image_height),
                interpolation=cv2.INTER_LINEAR
            )

        # -----------------------------------------------------
        # Convert BGR -> BGRA
        # -----------------------------------------------------

        rgba = cv2.cvtColor(
            image_array,
            cv2.COLOR_BGR2BGRA
        )

        # -----------------------------------------------------
        # Use mask directly as alpha channel
        # -----------------------------------------------------

        rgba[:, :, 3] = mask_array

        return rgba

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

            result = cv2.imread(
                str(path),
                cv2.IMREAD_COLOR
            )

            if result is None:
                raise ValueError(
                    f"Unable to read image: {path}"
                )

            return result

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

            if image.ndim == 3:

                if image.shape[2] == 3:
                    return image.copy()

                if image.shape[2] == 4:

                    return cv2.cvtColor(
                        image,
                        cv2.COLOR_BGRA2BGR
                    )

        raise TypeError(
            "Image must be a path or NumPy array."
        )

    # =========================================================
    # MASK LOADING
    # =========================================================

    @staticmethod
    def _load_mask(
        mask: MaskInput
    ) -> np.ndarray:

        if isinstance(mask, (str, Path)):

            path = Path(mask)

            if not path.exists():
                raise FileNotFoundError(
                    f"Mask not found: {path}"
                )

            result = cv2.imread(
                str(path),
                cv2.IMREAD_GRAYSCALE
            )

            if result is None:
                raise ValueError(
                    f"Unable to read mask: {path}"
                )

            return result

        if isinstance(mask, np.ndarray):

            if mask.size == 0:
                raise ValueError(
                    "Mask array is empty."
                )

            if mask.ndim == 2:
                return mask.copy()

            if mask.ndim == 3:

                return cv2.cvtColor(
                    mask,
                    cv2.COLOR_BGR2GRAY
                )

        raise TypeError(
            "Mask must be a path or NumPy array."
        )

    # =========================================================
    # SAVE RESULT
    # =========================================================

    @staticmethod
    def save_result(
        image: np.ndarray,
        output_path: Union[str, Path]
    ) -> None:

        if image is None or image.size == 0:
            raise ValueError(
                "Result image is empty."
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
            image
        )

        if not success:
            raise IOError(
                f"Unable to save result: {output_path}"
            )


# =============================================================
# SIMPLE FUNCTION API
# =============================================================

def apply_foreground_mask(
    image: ImageInput,
    mask: MaskInput
) -> np.ndarray:

    applier = MaskApplier()

    return applier.apply_mask(
        image,
        mask
    )


# =============================================================
# COMMAND LINE
# =============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) != 4:

        print(
            "Usage:"
        )

        print(
            "python mask_applier.py "
            "<image_path> "
            "<mask_path> "
            "<output_path>"
        )

        sys.exit(1)

    image_path = sys.argv[1]
    mask_path = sys.argv[2]
    output_path = sys.argv[3]

    result = apply_foreground_mask(
        image_path,
        mask_path
    )

    MaskApplier.save_result(
        result,
        output_path
    )

    print(
        f"Foreground image saved to: {output_path}"
    )