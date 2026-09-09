"""
background_compositor.py

Purpose:
    Composite the detected artisan product onto a generated replacement
    background using the refined foreground mask.

Flow:
    Lighting-corrected image
            +
       Refined mask
            +
    Generated background
            ↓
       Final image

This module does NOT:
    - analyze the image
    - generate a mask
    - refine the mask
    - generate the background

It only performs the final compositing operation.
"""

import os
import cv2
import numpy as np


class BackgroundCompositor:
    """
    Combines a foreground/product image with a generated background
    using a refined grayscale mask.
    """

    def __init__(
        self,
        edge_blur=1.0,
        mask_threshold=None,
    ):
        """
        Parameters
        ----------
        edge_blur : float
            Small blur applied to the mask to create natural edges.

        mask_threshold : int or None
            Optional threshold for converting the mask into a hard mask.

            None:
                Keep the mask as a soft alpha mask.

            Integer (0-255):
                Threshold the mask before compositing.

        For our project, None is recommended because the refined mask
        already contains useful edge information.
        """

        self.edge_blur = float(edge_blur)
        self.mask_threshold = mask_threshold

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def composite(
        self,
        foreground_image,
        mask,
        background,
    ):
        """
        Composite the foreground product onto the background.

        Parameters
        ----------
        foreground_image :
            Image path or BGR NumPy array.

        mask :
            Mask path or grayscale NumPy array.

            White (255) = keep foreground/product
            Black (0)   = use background

        background :
            Background path or BGR NumPy array.

        Returns
        -------
        np.ndarray
            Final composited BGR image.
        """

        foreground = self._load_image(foreground_image, "foreground")
        background_image = self._load_image(background, "background")
        mask_image = self._load_mask(mask)

        # --------------------------------------------------------------
        # Make sure all images have the same dimensions
        # --------------------------------------------------------------

        height, width = foreground.shape[:2]

        if background_image.shape[:2] != (height, width):
            background_image = cv2.resize(
                background_image,
                (width, height),
                interpolation=cv2.INTER_LINEAR,
            )

        if mask_image.shape[:2] != (height, width):
            mask_image = cv2.resize(
                mask_image,
                (width, height),
                interpolation=cv2.INTER_LINEAR,
            )

        # --------------------------------------------------------------
        # Prepare the mask
        # --------------------------------------------------------------

        mask_image = self._prepare_mask(mask_image)

        # --------------------------------------------------------------
        # Convert mask to alpha range [0, 1]
        # --------------------------------------------------------------

        alpha = mask_image.astype(np.float32) / 255.0

        # Add channel dimension so it can multiply BGR images.
        alpha = alpha[:, :, np.newaxis]

        # --------------------------------------------------------------
        # Convert images to float
        # --------------------------------------------------------------

        foreground_float = foreground.astype(np.float32)
        background_float = background_image.astype(np.float32)

        # --------------------------------------------------------------
        # Alpha compositing
        #
        # final = foreground * alpha
        #       + background * (1 - alpha)
        # --------------------------------------------------------------

        final = (
            foreground_float * alpha
            + background_float * (1.0 - alpha)
        )

        # --------------------------------------------------------------
        # Keep valid image range
        # --------------------------------------------------------------

        final = np.clip(final, 0, 255).astype(np.uint8)

        return final

    def composite_and_save(
        self,
        foreground_image,
        mask,
        background,
        output_path,
    ):
        """
        Composite the images and save the final result.
        """

        final_image = self.composite(
            foreground_image=foreground_image,
            mask=mask,
            background=background,
        )

        self.save_image(final_image, output_path)

        return final_image

    # ------------------------------------------------------------------
    # MASK PROCESSING
    # ------------------------------------------------------------------

    def _prepare_mask(self, mask):
        """
        Prepare the refined mask before compositing.

        We intentionally keep this conservative.

        The refined mask is already the output of the mask-quality
        refinement stage, so we do not perform aggressive morphology
        here.

        A tiny Gaussian blur is optionally applied only to soften
        jagged edges.
        """

        mask = np.asarray(mask)

        # Ensure grayscale
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        # Make sure values are uint8.
        if mask.dtype != np.uint8:
            mask = np.clip(mask, 0, 255).astype(np.uint8)

        # Optional threshold.
        if self.mask_threshold is not None:
            _, mask = cv2.threshold(
                mask,
                int(self.mask_threshold),
                255,
                cv2.THRESH_BINARY,
            )

        # Very small blur for smoother product boundaries.
        if self.edge_blur > 0:
            # Convert blur amount into a valid odd kernel size.
            kernel_size = max(
                1,
                int(round(self.edge_blur * 2)) + 1,
            )

            if kernel_size % 2 == 0:
                kernel_size += 1

            mask = cv2.GaussianBlur(
                mask,
                (kernel_size, kernel_size),
                0,
            )

        return mask

    # ------------------------------------------------------------------
    # IMAGE LOADING
    # ------------------------------------------------------------------

    def _load_image(self, image, name):
        """
        Load a BGR image from either a file path or NumPy array.
        """

        if isinstance(image, np.ndarray):
            if image.size == 0:
                raise ValueError(f"{name} image is empty.")

            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            elif len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

            elif len(image.shape) != 3 or image.shape[2] != 3:
                raise ValueError(
                    f"{name} image must have 1, 3, or 4 channels."
                )

            return image.copy()

        if not isinstance(image, (str, os.PathLike)):
            raise TypeError(
                f"{name} must be a file path or NumPy array."
            )

        image_path = os.fspath(image)

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"{name} image not found: {image_path}"
            )

        loaded = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if loaded is None:
            raise ValueError(
                f"Unable to read {name} image: {image_path}"
            )

        return loaded

    def _load_mask(self, mask):
        """
        Load a grayscale mask from a file path or NumPy array.
        """

        if isinstance(mask, np.ndarray):
            if mask.size == 0:
                raise ValueError("Mask is empty.")

            if len(mask.shape) == 3:
                if mask.shape[2] == 4:
                    mask = cv2.cvtColor(
                        mask,
                        cv2.COLOR_BGRA2GRAY,
                    )
                else:
                    mask = cv2.cvtColor(
                        mask,
                        cv2.COLOR_BGR2GRAY,
                    )

            return mask.copy()

        if not isinstance(mask, (str, os.PathLike)):
            raise TypeError(
                "Mask must be a file path or NumPy array."
            )

        mask_path = os.fspath(mask)

        if not os.path.exists(mask_path):
            raise FileNotFoundError(
                f"Mask not found: {mask_path}"
            )

        loaded = cv2.imread(
            mask_path,
            cv2.IMREAD_GRAYSCALE,
        )

        if loaded is None:
            raise ValueError(
                f"Unable to read mask: {mask_path}"
            )

        return loaded

    # ------------------------------------------------------------------
    # SAVING
    # ------------------------------------------------------------------

    @staticmethod
    def save_image(image, output_path):
        """
        Save the final composited image.
        """

        output_path = os.fspath(output_path)

        output_dir = os.path.dirname(output_path)

        if output_dir:
            os.makedirs(
                output_dir,
                exist_ok=True,
            )

        success = cv2.imwrite(
            output_path,
            image,
        )

        if not success:
            raise IOError(
                f"Failed to save image: {output_path}"
            )


# ======================================================================
# CONVENIENCE FUNCTION
# ======================================================================

def composite_background(
    foreground_image,
    mask,
    background,
    output_path=None,
):
    """
    Simple function interface for background compositing.
    """

    compositor = BackgroundCompositor()

    result = compositor.composite(
        foreground_image=foreground_image,
        mask=mask,
        background=background,
    )

    if output_path is not None:
        compositor.save_image(
            result,
            output_path,
        )

    return result


# ======================================================================
# COMMAND LINE INTERFACE
# ======================================================================

def main():
    """
    Command-line usage:

    python background_compositor.py \
        <foreground_image> \
        <refined_mask> \
        <background_image> \
        <output_image>
    """

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Composite an artisan product onto a generated "
            "replacement background."
        )
    )

    parser.add_argument(
        "foreground_image",
        help="Lighting-corrected foreground/product image.",
    )

    parser.add_argument(
        "refined_mask",
        help="Refined foreground mask.",
    )

    parser.add_argument(
        "background_image",
        help="Generated replacement background.",
    )

    parser.add_argument(
        "output_image",
        help="Path for the final composited image.",
    )

    args = parser.parse_args()

    compositor = BackgroundCompositor(
        edge_blur=1.0,
        mask_threshold=None,
    )

    compositor.composite_and_save(
        foreground_image=args.foreground_image,
        mask=args.refined_mask,
        background=args.background_image,
        output_path=args.output_image,
    )

    print("\nBackground compositing completed.")
    print(f"Foreground : {args.foreground_image}")
    print(f"Mask       : {args.refined_mask}")
    print(f"Background : {args.background_image}")
    print(f"Output     : {args.output_image}")


if __name__ == "__main__":
    main()