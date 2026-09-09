"""
CraftMitra - AI Image Enhancement Pipeline

Complete image enhancement flow:

    Original Image
          |
          v
    Image Analyzer
          |
          v
    Lighting Corrector
          |
          v
    Background Analyzer
          |
          +-----------------------------+
          |                             |
     Good Background              Poor Background
          |                             |
          |                             v
          |                    Background Remover
          |                             |
          |                             v
          |                       Refined Mask
          |                             |
          |                             v
          |                    Background Generator
          |                             |
          |                             v
          |                    Background Compositor
          |                             |
          +--------------+--------------+
                         |
                         v
                    Final Image

The pipeline does not replace the individual modules.
It connects the modules that have already been developed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np


# ---------------------------------------------------------------------
# IMPORT EXISTING MODULES
# ---------------------------------------------------------------------

try:
    from image_analyzer import ImageAnalyzer
    from lighting_corrector import LightingCorrector
    from background_analyzer import BackgroundAnalyzer
    from background_remover_mask import BackgroundRemoverMask
    from mask_quality_refiner import MaskQualityRefiner
    from background_generator import BackgroundGenerator
    from background_compositor import BackgroundCompositor

except ImportError:
    # Allows the file to be imported as a package as well.
    from .image_analyzer import ImageAnalyzer
    from .lighting_corrector import LightingCorrector
    from .background_analyzer import BackgroundAnalyzer
    from .background_remover_mask import BackgroundRemoverMask
    from .mask_quality_refiner import MaskQualityRefiner
    from .background_generator import BackgroundGenerator
    from .background_compositor import BackgroundCompositor


class ImageEnhancementPipeline:
    """
    Complete CraftMitra image enhancement pipeline.

    The pipeline keeps the responsibilities of each module separate.

    Analyzer:
        Understands the image.

    LightingCorrector:
        Corrects lighting only when necessary.

    BackgroundAnalyzer:
        Decides whether the existing background should be preserved
        or sent for removal.

    BackgroundRemoverMask:
        Generates the raw foreground mask.

    MaskQualityRefiner:
        Refines the raw mask.

    BackgroundGenerator:
        Creates the replacement studio-style background.

    BackgroundCompositor:
        Combines the corrected product image, refined mask,
        and generated background.
    """

    # -----------------------------------------------------------------
    # CONSTRUCTOR
    # -----------------------------------------------------------------

    def __init__(
        self,
        image_analyzer: Optional[ImageAnalyzer] = None,
        lighting_corrector: Optional[LightingCorrector] = None,
        background_analyzer: Optional[BackgroundAnalyzer] = None,
        background_remover: Optional[BackgroundRemoverMask] = None,
        mask_refiner: Optional[MaskQualityRefiner] = None,
        background_generator: Optional[BackgroundGenerator] = None,
        background_compositor: Optional[BackgroundCompositor] = None,
    ):
        """
        Create all processing components.

        Components can be supplied externally for testing or future
        customization.
        """

        self.image_analyzer = (
            image_analyzer
            or ImageAnalyzer()
        )

        self.lighting_corrector = (
            lighting_corrector
            or LightingCorrector(
                self.image_analyzer
            )
        )

        self.background_analyzer = (
            background_analyzer
            or BackgroundAnalyzer()
        )

        self.background_remover = (
            background_remover
            or BackgroundRemoverMask()
        )

        self.mask_refiner = (
            mask_refiner
            or MaskQualityRefiner()
        )

        self.background_generator = (
            background_generator
            or BackgroundGenerator()
        )

        self.background_compositor = (
            background_compositor
            or BackgroundCompositor()
        )

    # -----------------------------------------------------------------
    # MAIN PIPELINE
    # -----------------------------------------------------------------

    def process(
        self,
        image,
        output_path: Optional[str | Path] = None,
        save_intermediate: bool = False,
        intermediate_dir: Optional[str | Path] = None,
    ) -> Dict[str, Any]:
        """
        Process one image through the complete enhancement pipeline.

        Parameters
        ----------
        image:
            Input image path or NumPy image.

        output_path:
            Optional path for the final enhanced image.

        save_intermediate:
            If True, intermediate outputs are saved.

        intermediate_dir:
            Directory where intermediate files are saved.

        Returns
        -------
        Dict[str, Any]
            Complete pipeline result containing:
                - final image
                - analysis
                - lighting report
                - background report
                - mask information
                - processing status
        """

        # =============================================================
        # 0. PREPARE INPUT
        # =============================================================

        original = self._load_image(image)

        input_path = None

        if isinstance(image, (str, Path)):
            input_path = Path(image)

        # Create intermediate directory if requested.
        if save_intermediate:
            if intermediate_dir is None:

                if input_path is not None:
                    intermediate_dir = (
                        input_path.parent
                        / f"{input_path.stem}_pipeline"
                    )
                else:
                    intermediate_dir = Path("pipeline_output")

            intermediate_dir = Path(intermediate_dir)

            intermediate_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

        # =============================================================
        # 1. IMAGE ANALYSIS
        # =============================================================

        print("\n[1/6] Analyzing image...")

        analysis = self.image_analyzer.analyze(
            original
        )

        self._print_stage(
            "Image analysis completed."
        )

        # =============================================================
        # 2. LIGHTING CORRECTION
        # =============================================================

        print("\n[2/6] Correcting lighting...")

        corrected_image, lighting_report = (
            self.lighting_corrector.correct(
                original,
                analysis,
            )
        )

        self._print_stage(
            "Lighting correction completed."
        )

        if save_intermediate:
            lighting_path = (
                Path(intermediate_dir)
                / "01_lighting_corrected.png"
            )

            self._save_image(
                corrected_image,
                lighting_path,
            )

        # =============================================================
        # 3. BACKGROUND ANALYSIS
        # =============================================================

        print("\n[3/6] Analyzing background...")

        background_report = (
            self.background_analyzer.analyze(
                corrected_image
            )
        )

        self._print_stage(
            "Background analysis completed."
        )

        # -------------------------------------------------------------
        # Determine whether background removal is required.
        # -------------------------------------------------------------

        remove_background = self._should_remove_background(
            background_report
        )

        # =============================================================
        # BRANCH A:
        # BACKGROUND IS ALREADY ACCEPTABLE
        # =============================================================

        if not remove_background:

            print(
                "\nBackground is acceptable."
            )

            print(
                "Skipping background removal."
            )

            final_image = corrected_image

            pipeline_result = {
                "success": True,
                "background_removed": False,
                "final_image": final_image,
                "analysis": analysis,
                "lighting": lighting_report,
                "background": background_report,
                "mask": None,
                "background_generation": None,
                "compositing": None,
            }

            if output_path is not None:
                self._save_image(
                    final_image,
                    output_path,
                )

            if save_intermediate:
                final_path = (
                    Path(intermediate_dir)
                    / "final_image.png"
                )

                self._save_image(
                    final_image,
                    final_path,
                )

            print(
                "\nPipeline completed successfully."
            )

            return pipeline_result

        # =============================================================
        # BRANCH B:
        # BACKGROUND REMOVAL REQUIRED
        # =============================================================

        print(
            "\nBackground requires replacement."
        )

        # =============================================================
        # 4. GENERATE RAW MASK
        # =============================================================

        print(
            "\n[4/6] Generating foreground mask..."
        )

        raw_mask = (
            self.background_remover.generate_mask(
                corrected_image
            )
        )

        if raw_mask is None:
            raise RuntimeError(
                "Background remover returned no mask."
            )

        self._validate_mask(
            raw_mask,
            corrected_image,
        )

        self._print_stage(
            "Raw foreground mask generated."
        )

        if save_intermediate:
            raw_mask_path = (
                Path(intermediate_dir)
                / "02_raw_mask.png"
            )

            self._save_mask(
                raw_mask,
                raw_mask_path,
            )

        # =============================================================
        # 5. REFINE MASK
        # =============================================================

        print(
            "\n[5/6] Refining foreground mask..."
        )

        refined_mask, mask_report = (
            self._refine_mask(
                corrected_image,
                raw_mask,
            )
        )

        self._validate_mask(
            refined_mask,
            corrected_image,
        )

        self._print_stage(
            "Refined foreground mask generated."
        )

        if save_intermediate:
            refined_mask_path = (
                Path(intermediate_dir)
                / "03_refined_mask.png"
            )

            self._save_mask(
                refined_mask,
                refined_mask_path,
            )

        # =============================================================
        # 6. GENERATE BACKGROUND
        # =============================================================

        print(
            "\n[6/6] Generating replacement background..."
        )

        height, width = corrected_image.shape[:2]

        generated_background = (
            self.background_generator.generate_for_size(
                width,
                height,
            )
        )

        self._print_stage(
            "Replacement background generated."
        )

        if save_intermediate:
            background_path = (
                Path(intermediate_dir)
                / "04_generated_background.png"
            )

            self._save_image(
                generated_background,
                background_path,
            )

        # =============================================================
        # 7. COMPOSITE
        # =============================================================

        print(
            "\nCompositing product with new background..."
        )

        final_image = (
            self.background_compositor.composite(
                foreground_image=corrected_image,
                mask=refined_mask,
                background=generated_background,
            )
        )

        self._print_stage(
            "Final image composited."
        )

        if output_path is not None:
            self._save_image(
                final_image,
                output_path,
            )

        if save_intermediate:
            final_path = (
                Path(intermediate_dir)
                / "final_image.png"
            )

            self._save_image(
                final_image,
                final_path,
            )

        # =============================================================
        # FINAL RESULT
        # =============================================================

        pipeline_result = {
            "success": True,
            "background_removed": True,
            "final_image": final_image,
            "analysis": analysis,
            "lighting": lighting_report,
            "background": background_report,
            "mask": mask_report,
            "background_generation": {
                "width": width,
                "height": height,
            },
            "compositing": {
                "completed": True,
            },
        }

        print(
            "\n========================================"
        )

        print(
            "CraftMitra Image Enhancement Completed"
        )

        print(
            "========================================"
        )

        return pipeline_result

    # -----------------------------------------------------------------
    # BACKGROUND DECISION
    # -----------------------------------------------------------------

    @staticmethod
    def _should_remove_background(
        background_report: Dict[str, Any]
    ) -> bool:
        """
        Determine whether the background should be replaced.

        The existing BackgroundAnalyzer already provides the
        recommendation. This method keeps the pipeline compatible
        with that result.

        Expected field:

            recommendation:
                True / False

        Some versions may use:

            remove_background

        Therefore both are supported.
        """

        if "recommendation" in background_report:

            recommendation = (
                background_report["recommendation"]
            )

            if isinstance(
                recommendation,
                bool,
            ):
                return recommendation

        if "remove_background" in background_report:

            remove_background = (
                background_report[
                    "remove_background"
                ]
            )

            if isinstance(
                remove_background,
                bool,
            ):
                return remove_background

        # Some analyzer implementations may put the decision
        # inside another dictionary.
        if isinstance(
            background_report.get("recommendation"),
            dict,
        ):

            nested = background_report[
                "recommendation"
            ]

            if "remove_background" in nested:

                return bool(
                    nested["remove_background"]
                )

        # If no recognized decision is available,
        # fail safely instead of silently removing the background.
        return False

    # -----------------------------------------------------------------
    # MASK REFINEMENT
    # -----------------------------------------------------------------

    def _refine_mask(
        self,
        image: np.ndarray,
        raw_mask: np.ndarray,
    ):
        """
        Call the existing MaskQualityRefiner.

        Different development versions of the refiner may expose
        slightly different method names/signatures.

        The preferred interface is:

            refine(image, raw_mask)

        The fallback handles the common:

            refine_mask(image, raw_mask)

        interface.
        """

        # Preferred API.
        if hasattr(
            self.mask_refiner,
            "refine",
        ):

            result = self.mask_refiner.refine(
                image,
                raw_mask,
            )

            return self._normalize_refiner_result(
                result,
                raw_mask,
            )

        # Alternative API.
        if hasattr(
            self.mask_refiner,
            "refine_mask",
        ):

            result = self.mask_refiner.refine_mask(
                image,
                raw_mask,
            )

            return self._normalize_refiner_result(
                result,
                raw_mask,
            )

        raise AttributeError(
            "MaskQualityRefiner does not provide "
            "'refine' or 'refine_mask'."
        )

    @staticmethod
    def _normalize_refiner_result(
        result,
        fallback_mask,
    ):
        """
        Normalize different refiner return formats.

        Supported:

            refined_mask

        or:

            refined_mask, report

        or:

            {
                "mask": refined_mask,
                ...
            }
        """

        # Tuple/list:
        if isinstance(
            result,
            (tuple, list),
        ):

            if len(result) >= 2:

                refined_mask = result[0]
                report = result[1]

                return (
                    refined_mask,
                    report,
                )

            if len(result) == 1:

                return (
                    result[0],
                    {
                        "selected_mask":
                            "refined_mask"
                    },
                )

        # Dictionary:
        if isinstance(
            result,
            dict,
        ):

            possible_keys = [
                "mask",
                "refined_mask",
                "selected_mask",
            ]

            for key in possible_keys:

                if key in result:

                    value = result[key]

                    # selected_mask can sometimes be a string
                    # rather than an actual mask.
                    if isinstance(
                        value,
                        np.ndarray,
                    ):

                        return (
                            value,
                            result,
                        )

        # Direct NumPy mask:
        if isinstance(
            result,
            np.ndarray,
        ):

            return (
                result,
                {
                    "selected_mask":
                        "refined_mask"
                },
            )

        raise ValueError(
            "Unable to determine the refined mask "
            "from MaskQualityRefiner output."
        )

    # -----------------------------------------------------------------
    # IMAGE LOADING
    # -----------------------------------------------------------------

    @staticmethod
    def _load_image(
        image,
    ) -> np.ndarray:
        """
        Load image from path or NumPy array.
        """

        if isinstance(
            image,
            np.ndarray,
        ):

            if image.size == 0:
                raise ValueError(
                    "Input image is empty."
                )

            if image.ndim == 2:

                return cv2.cvtColor(
                    image,
                    cv2.COLOR_GRAY2BGR,
                )

            if (
                image.ndim == 3
                and image.shape[2] == 4
            ):

                return cv2.cvtColor(
                    image,
                    cv2.COLOR_BGRA2BGR,
                )

            if (
                image.ndim == 3
                and image.shape[2] == 3
            ):

                return image.copy()

            raise ValueError(
                "Unsupported image array shape."
            )

        path = Path(image)

        if not path.exists():
            raise FileNotFoundError(
                f"Input image not found: {path}"
            )

        loaded = cv2.imread(
            str(path),
            cv2.IMREAD_COLOR,
        )

        if loaded is None:
            raise ValueError(
                f"Unable to read input image: {path}"
            )

        return loaded

    # -----------------------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------------------

    @staticmethod
    def _validate_mask(
        mask: np.ndarray,
        image: np.ndarray,
    ):
        """
        Validate that the generated mask can be used for compositing.
        """

        if not isinstance(
            mask,
            np.ndarray,
        ):

            raise TypeError(
                "Mask must be a NumPy array."
            )

        if mask.size == 0:

            raise ValueError(
                "Mask is empty."
            )

        if mask.ndim == 3:

            mask = cv2.cvtColor(
                mask,
                cv2.COLOR_BGR2GRAY,
            )

        if mask.ndim != 2:

            raise ValueError(
                "Mask must be a 2D grayscale image."
            )

        if mask.shape != image.shape[:2]:

            raise ValueError(
                "Mask dimensions do not match "
                "the image dimensions."
            )

    # -----------------------------------------------------------------
    # SAVE HELPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _save_image(
        image: np.ndarray,
        path: str | Path,
    ):
        """
        Save a BGR image.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        success = cv2.imwrite(
            str(path),
            image,
        )

        if not success:

            raise IOError(
                f"Could not save image: {path}"
            )

    @staticmethod
    def _save_mask(
        mask: np.ndarray,
        path: str | Path,
    ):
        """
        Save a grayscale mask.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if mask.ndim == 3:

            mask = cv2.cvtColor(
                mask,
                cv2.COLOR_BGR2GRAY,
            )

        success = cv2.imwrite(
            str(path),
            mask,
        )

        if not success:

            raise IOError(
                f"Could not save mask: {path}"
            )

    # -----------------------------------------------------------------
    # LOGGING
    # -----------------------------------------------------------------

    @staticmethod
    def _print_stage(
        message: str,
    ):
        print(
            f"    ✓ {message}"
        )


# =====================================================================
# SIMPLE FUNCTION API
# =====================================================================

def enhance_image(
    image,
    output_path: Optional[str | Path] = None,
    save_intermediate: bool = False,
    intermediate_dir: Optional[str | Path] = None,
):
    """
    Convenience function for running the complete pipeline.
    """

    pipeline = ImageEnhancementPipeline()

    return pipeline.process(
        image=image,
        output_path=output_path,
        save_intermediate=save_intermediate,
        intermediate_dir=intermediate_dir,
    )


# =====================================================================
# COMMAND LINE INTERFACE
# =====================================================================

def main():
    """
    Command-line usage:

        python image_enhancement_pipeline.py <input_image>

    Or:

        python image_enhancement_pipeline.py \
            <input_image> \
            <output_image>

    To also save intermediate results:

        python image_enhancement_pipeline.py \
            <input_image> \
            <output_image> \
            --save-intermediate
    """

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Run the complete CraftMitra "
            "AI image enhancement pipeline."
        )
    )

    parser.add_argument(
        "input_image",
        help="Path to the input artisan product image.",
    )

    parser.add_argument(
        "output_image",
        nargs="?",
        default=None,
        help=(
            "Optional path for the final enhanced image."
        ),
    )

    parser.add_argument(
        "--save-intermediate",
        action="store_true",
        help=(
            "Save intermediate images and masks."
        ),
    )

    parser.add_argument(
        "--intermediate-dir",
        default=None,
        help=(
            "Optional directory for intermediate files."
        ),
    )

    args = parser.parse_args()

    # ---------------------------------------------------------------
    # Run pipeline
    # ---------------------------------------------------------------

    result = enhance_image(
        image=args.input_image,
        output_path=args.output_image,
        save_intermediate=args.save_intermediate,
        intermediate_dir=args.intermediate_dir,
    )

    # ---------------------------------------------------------------
    # Print compact report
    # ---------------------------------------------------------------

    report = {
        "success": result["success"],
        "background_removed": result[
            "background_removed"
        ],
        "lighting": result["lighting"],
        "background": result["background"],
    }

    if result["mask"] is not None:
        report["mask"] = result["mask"]

    if result["background_generation"] is not None:
        report["background_generation"] = (
            result["background_generation"]
        )

    if result["compositing"] is not None:
        report["compositing"] = (
            result["compositing"]
        )

    print("\nPipeline report:")
    print(
        json.dumps(
            report,
            indent=4,
            default=str,
        )
    )


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    main()