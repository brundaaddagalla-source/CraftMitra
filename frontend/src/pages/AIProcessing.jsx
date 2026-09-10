import { useEffect, useRef, useState } from "react";
import {
  Sparkles,
  Check,
  Package,
  IndianRupee,
  AlertCircle,
  RotateCcw,
  ArrowRight
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/aiProcessing.css";
import { useLanguage } from "../context/LanguageContext";
import { api } from "../api/client";

// Dynamic pricing isn't built yet - every listing gets this starting
// point and the artisan can edit it on the review screen (Step 10).
const DEFAULT_RECOMMENDED_PRICE = 250;

// The voice pipeline (Step 7/8) already runs synchronously and fully
// finishes before this screen ever loads - by the time we get here,
// `voiceResult` already has the transcript, translations, extracted
// product info and AI-generated description. The one thing that's
// still genuinely running in the background is image enhancement
// (Step 3-5), so that's the only thing this screen actually polls for.
const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 30; // ~60 seconds before giving up

function AIProcessing() {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useLanguage();

  const productId = location.state?.productId;
  const imageId = location.state?.imageId;
  const image = location.state?.image; // original image URL
  const story = location.state?.story;
  const language = location.state?.language || "English";
  const voiceResult = location.state?.voiceResult || null;

  // polling -> completed | failed | timeout | error
  const [imageStatus, setImageStatus] = useState("polling");
  const [errorMessage, setErrorMessage] = useState("");
  const [progress, setProgress] = useState(10);

  const pollTimeoutRef = useRef(null);
  const attemptsRef = useRef(0);
  const cancelledRef = useRef(false);

  // This screen only makes sense after a photo has been uploaded and
  // the voice note has already been processed (Steps 1-8). If someone
  // lands here directly, send them back to start the flow properly.
  useEffect(() => {
    if (!productId || !imageId || !voiceResult) {
      navigate("/add-product", { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // -------------------------------------------------------
  // Build the data the review screen (Step 10) needs, from
  // whatever the voice pipeline + image enhancement produced.
  // -------------------------------------------------------
  const buildEditProductState = (imageRecord) => ({
    productId,
    imageId,
    image,
    enhancedImage: imageRecord?.enhanced_image_url || null,
    story,
    language,
    voiceResult,
    product: {
      name: voiceResult?.extracted_product?.product_name || "",
      category:
        voiceResult?.ai_suggested_category ||
        voiceResult?.extracted_product?.category ||
        "Handicraft",
      material: voiceResult?.extracted_product?.material || "",
      technique: voiceResult?.extracted_product?.craft_technique || "",
      color: voiceResult?.extracted_product?.color || "",
      // The AI description generator only produces English text (no
      // model to compose it in the artisan's own language). For the
      // "regional" tab we honestly show the artisan's own normalized
      // words instead of pretending it's an AI-composed translation.
      descriptions: {
        regional: voiceResult?.regional_text || "",
        english: voiceResult?.ai_generated_description || voiceResult?.english || "",
        hindi: voiceResult?.ai_generated_description_hindi || voiceResult?.hindi || ""
      },
      regionalLanguageLabel: language,
      price: DEFAULT_RECOMMENDED_PRICE,
      confidence:
        voiceResult?.ai_confidence != null
          ? Math.round(voiceResult.ai_confidence * 100)
          : null
    }
  });

  const goToReview = (imageRecord) => {
    if (cancelledRef.current) return;
    navigate("/edit-product", { state: buildEditProductState(imageRecord) });
  };

  const pollImage = async () => {
    if (cancelledRef.current) return;

    try {
      const images = await api.get(`/products/${productId}/images`);
      const imageRecord = images.find((item) => item.id === imageId);

      if (!imageRecord) {
        throw new Error(t("We couldn't find your uploaded photo."));
      }

      if (imageRecord.processing_status === "completed") {
        setProgress(100);
        setImageStatus("completed");
        goToReview(imageRecord);
        return;
      }

      if (imageRecord.processing_status === "failed") {
        setImageStatus("failed");
        return;
      }

      // Still pending/processing - keep the progress bar inching
      // forward so the wait doesn't feel stuck, and poll again.
      attemptsRef.current += 1;
      setProgress((prev) => Math.min(90, prev + 3));

      if (attemptsRef.current >= MAX_POLL_ATTEMPTS) {
        setImageStatus("timeout");
        return;
      }

      pollTimeoutRef.current = setTimeout(pollImage, POLL_INTERVAL_MS);
    } catch (error) {
      console.error(error);
      if (cancelledRef.current) return;
      setErrorMessage(
        error.message || t("Something went wrong while enhancing your photo.")
      );
      setImageStatus("error");
    }
  };

  useEffect(() => {
    if (!productId || !imageId) return undefined;

    cancelledRef.current = false;
    pollImage();

    return () => {
      cancelledRef.current = true;
      if (pollTimeoutRef.current) clearTimeout(pollTimeoutRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [productId, imageId]);

  const retryEnhancement = async () => {
    setErrorMessage("");
    setImageStatus("polling");
    attemptsRef.current = 0;
    setProgress(10);
    cancelledRef.current = false;

    try {
      await api.post(`/products/${productId}/images/${imageId}/enhance`);
      pollImage();
    } catch (error) {
      console.error(error);
      setErrorMessage(
        error.message || t("Couldn't restart enhancement. Please try again.")
      );
      setImageStatus("error");
    }
  };

  const continueWithOriginal = () => {
    goToReview({ enhanced_image_url: null });
  };

  const imageStepStatus =
    imageStatus === "completed"
      ? "completed"
      : imageStatus === "polling"
      ? "active"
      : "stalled";

  const steps = [
    {
      title: t("Enhancing your craft image"),
      description: t("Improving lighting, background and sharpness"),
      icon: <Sparkles size={18} />,
      status: imageStepStatus
    },
    {
      title: t("Understanding your story"),
      description: t(
        `Converted your ${language} voice description into product details`
      ),
      icon: <Sparkles size={18} />,
      status: "completed"
    },
    {
      title: t("Creating your product listing"),
      description: t("Generating a professional product name and description"),
      icon: <Package size={18} />,
      status: "completed"
    },
    {
      title: t("Calculating a fair price"),
      description: t("Preparing a suitable price recommendation"),
      icon: <IndianRupee size={18} />,
      status: "completed"
    }
  ];

  const hasStalled = ["failed", "timeout", "error"].includes(imageStatus);

  return (
    <div className="ai-processing-page">

      {/* TOP BRAND */}

      <div className="ai-processing-brand">
        <Sparkles size={15} />
        <span>{t("CRAFTMITRA AI")}</span>
      </div>


      {/* HEADER */}

      <div className="ai-processing-header">

        <h1>
          Turning your craft into
          <span> a marketplace story</span>
        </h1>

        <p>
          Sit back while CraftMitra transforms your photo and story
          into a professional product listing.
        </p>

      </div>


      {/* MAIN CARD */}

      <div className="processing-card">

        {/* ICON */}

        <div className="processing-main-icon">
          <Sparkles size={32} />
        </div>


        {/* TITLE */}

        <h2>{t("Creating your product...")}</h2>

        <p className="processing-subtitle">
          {t("Our AI is working through your craft details.")}
        </p>


        {/* STEPS */}

        <div className="processing-steps">

          {steps.map((step) => {

            const completed = step.status === "completed";
            const active = step.status === "active";
            const stalled = step.status === "stalled";

            return (
              <div
                className={`processing-step ${
                  completed ? "completed" : ""
                } ${active ? "active" : ""} ${stalled ? "stalled" : ""}`}
                key={step.title}
              >

                {/* STEP ICON */}

                <div className="step-icon">

                  {completed ? (
                    <Check size={19} />
                  ) : stalled ? (
                    <AlertCircle size={19} />
                  ) : (
                    step.icon
                  )}

                </div>


                {/* STEP CONTENT */}

                <div className="step-content">

                  <strong>
                    {step.title}
                  </strong>

                  <span>
                    {step.description}
                  </span>

                </div>


                {/* RIGHT CHECK */}

                <div className="step-status">

                  {completed && (
                    <Check size={17} />
                  )}

                </div>

              </div>
            );

          })}

        </div>


        {/* PROGRESS */}

        <div className="processing-progress">

          <div className="progress-label">

            <span>
              {progress === 100
                ? t("Complete")
                : hasStalled
                ? t("Paused")
                : t("Processing")}
            </span>

            <span>
              {progress}%
            </span>

          </div>


          <div className="progress-track">

            <div
              className="progress-fill"
              style={{
                width: `${progress}%`
              }}
            />

          </div>

        </div>


        {/* IMAGE ENHANCEMENT STALLED - LET THE ARTISAN CHOOSE HOW TO PROCEED */}

        {hasStalled && (

          <div className="processing-error">

            <AlertCircle size={16} />

            <div className="processing-error-text">
              <strong>
                {imageStatus === "timeout"
                  ? t("Photo enhancement is taking longer than expected.")
                  : t("We couldn't enhance your photo.")}
              </strong>

              <span>
                {errorMessage ||
                  t(
                    "You can try again, or continue with your original photo instead."
                  )}
              </span>
            </div>

            <div className="processing-error-actions">

              <button type="button" onClick={retryEnhancement}>
                <RotateCcw size={13} />
                {t("Retry")}
              </button>

              <button type="button" onClick={continueWithOriginal}>
                {t("Continue with original photo")}
                <ArrowRight size={13} />
              </button>

            </div>

          </div>

        )}

      </div>

    </div>
  );
}

export default AIProcessing;