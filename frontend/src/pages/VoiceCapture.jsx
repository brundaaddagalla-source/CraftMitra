import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  Sparkles,
  Mic,
  Square,
  RotateCcw,
  AlertCircle,
  Loader2
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { api } from "../api/client";
import "../styles/addProduct.css";
import "../styles/voiceCapture.css";

// Keep a recording from running forever if the artisan forgets to stop it.
const MAX_RECORDING_SECONDS = 120;

// MediaRecorder support (and the exact mime string) varies by browser.
// Try the ones the backend actually accepts (see ALLOWED_AUDIO_TYPES in
// app/ai/audio/audio_processor.py) in order of preference.
const MIME_TYPE_CANDIDATES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/ogg;codecs=opus",
  "audio/ogg"
];

function pickSupportedMimeType() {
  if (typeof MediaRecorder === "undefined") return null;

  return (
    MIME_TYPE_CANDIDATES.find((type) => {
      try {
        return MediaRecorder.isTypeSupported(type);
      } catch {
        return false;
      }
    }) || null
  );
}

function extensionForMimeType(mimeType) {
  if (!mimeType) return "webm";
  if (mimeType.includes("mp4")) return "m4a";
  if (mimeType.includes("ogg")) return "ogg";
  return "webm";
}

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

// Shown to the artisan, and used as the human-readable label once the
// backend tells us which language it actually processed the audio in.
const LANGUAGE_DISPLAY_NAMES = {
  te: "Telugu",
  en: "English",
  hi: "Hindi"
};

// Languages the voice pipeline can currently handle end to end
// (speech-to-text + translation into English/Hindi). The artisan
// picks one of these before recording so the backend knows which
// language model to use - see SUPPORTED_SPOKEN_LANGUAGES in
// ai_product_pipeline_service.py.
const SPOKEN_LANGUAGE_OPTIONS = [
  { code: "te", label: "Telugu" },
  { code: "en", label: "English" }
];

function VoiceCapture() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();

  const productId = location.state?.productId;
  const imageId = location.state?.imageId;
  const image = location.state?.image;

  // idle -> requesting -> recording -> recorded -> uploading
  // (uploading either succeeds and navigates away, or drops back to
  // "recorded" with uploadError set so the artisan can retry).
  const [status, setStatus] = useState("idle");
  const [spokenLanguage, setSpokenLanguage] = useState("te");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [permissionError, setPermissionError] = useState("");
  const [uploadError, setUploadError] = useState("");

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);
  const audioBlobRef = useRef(null);
  const mimeTypeRef = useRef(null);
  const timerRef = useRef(null);
  const recordedSecondsRef = useRef(0);

  // This screen only makes sense once a photo has actually been
  // uploaded (Step 2/3) - if someone lands here directly, send them
  // back to start the flow properly.
  useEffect(() => {
    if (!productId || !imageId) {
      navigate("/add-product", { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Clean up the microphone stream / timer / object URL on unmount.
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }
  };

  const startTimer = () => {
    setElapsedSeconds(0);
    recordedSecondsRef.current = 0;

    timerRef.current = setInterval(() => {
      recordedSecondsRef.current += 1;
      setElapsedSeconds(recordedSecondsRef.current);

      if (recordedSecondsRef.current >= MAX_RECORDING_SECONDS) {
        stopRecording();
      }
    }, 1000);
  };

  const startRecording = async () => {
    setPermissionError("");
    setUploadError("");

    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setPermissionError(
        t("Voice recording is not available on this device or browser. This can also happen if the page isn't loaded over HTTPS.")
      );
      return;
    }

    setStatus("requesting");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = pickSupportedMimeType();
      mimeTypeRef.current = mimeType;

      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        stopTimer();

        streamRef.current?.getTracks().forEach((track) => track.stop());
        streamRef.current = null;

        const blob = new Blob(chunksRef.current, {
          type: mimeTypeRef.current?.split(";")[0] || "audio/webm"
        });

        audioBlobRef.current = blob;
        setAudioUrl(URL.createObjectURL(blob));
        setStatus("recorded");
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setStatus("recording");
      startTimer();
    } catch (error) {
      console.error(error);
      setStatus("idle");
      setPermissionError(
        t("Microphone access was blocked. Please allow microphone permission in your browser.")
      );
    }
  };

  const reRecord = () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);

    audioBlobRef.current = null;
    setAudioUrl(null);
    setElapsedSeconds(0);
    setUploadError("");
    setStatus("idle");
  };

  // =====================================================
  // UPLOAD RECORDING -> /ai/process-product-audio
  // =====================================================

  const uploadAndContinue = async () => {
    if (!audioBlobRef.current) return;

    setStatus("uploading");
    setUploadError("");

    try {
      const extension = extensionForMimeType(mimeTypeRef.current);

      const file = new File(
        [audioBlobRef.current],
        `product-voice.${extension}`,
        { type: audioBlobRef.current.type }
      );

      // Field name must match the FastAPI parameter name
      // (`audio_file: UploadFile = File(...)`), not the default "file".
      // `language` tells the backend which speech-to-text/translation
      // path to use - see SUPPORTED_SPOKEN_LANGUAGES on the backend.
      const result = await api.uploadFile(
        "/ai/process-product-audio",
        file,
        "audio_file",
        { language: spokenLanguage }
      );

      navigate("/ai-processing", {
        state: {
          productId,
          imageId,
          image,
          story: result.regional_text || result.normalized_telugu || result.transcript,
          language:
            LANGUAGE_DISPLAY_NAMES[result.processed_language] || "English",
          voiceResult: result
        }
      });
    } catch (error) {
      console.error(error);
      setStatus("recorded");
      setUploadError(
        error.message || t("Couldn't process your recording. Please try again.")
      );
    }
  };

  const isRequesting = status === "requesting";
  const isRecording = status === "recording";
  const isRecorded = status === "recorded";
  const isUploading = status === "uploading";
  const hasRecording = isRecorded || isUploading;

  return (
    <div className="add-product-page">

      {/* =================================================
          TOPBAR
      ================================================= */}

      <header className="add-product-topbar">

        <button
          type="button"
          className="back-button"
          onClick={() =>
            navigate("/add-product")
          }
        >
          <ArrowLeft size={16} />
          {t("Back to Photo")}
        </button>

        <div className="add-product-brand">
          <div className="brand-symbol">
            <Sparkles size={16} />
          </div>
          <span>CraftMitra</span>
        </div>

        <div className="save-draft">
          <div className="save-dot"></div>
          {t("Auto-saving")}
        </div>

      </header>


      {/* =================================================
          PROGRESS
      ================================================= */}

      <div className="creation-progress">

        <div className="progress-step">
          <div className="progress-number">1</div>
          <span>{t("Product")}</span>
        </div>

        <div className="progress-line"></div>

        <div className="progress-step active">
          <div className="progress-number">2</div>
          <span>{t("Voice Story")}</span>
        </div>

        <div className="progress-line"></div>

        <div className="progress-step">
          <div className="progress-number">3</div>
          <span>{t("AI Processing")}</span>
        </div>

        <div className="progress-line"></div>

        <div className="progress-step">
          <div className="progress-number">4</div>
          <span>{t("Review")}</span>
        </div>

      </div>


      {/* =================================================
          MAIN
      ================================================= */}

      <main className="add-product-main">

        <div className="creation-header">

          <div className="creation-badge">
            <Sparkles size={12} />
            AI-POWERED PRODUCT CREATION
          </div>

          <h1>
            {t("Tell us your story")}
            <span> {t("in your own words.")}</span>
          </h1>

          <p>
            {t("Speak naturally about your craft. CraftMitra will turn your voice note into a product description.")}
          </p>

        </div>


        {/* =================================================
            VOICE CARD
        ================================================= */}

        <div className="creation-grid single-card">

          <div className="creation-card">

            <div className="card-heading">

              <div className="heading-icon voice-heading-icon">
                <Mic size={22} />
              </div>

              <div>
                <h2>{t("Record your voice note")}</h2>
                <p>{t("Speak for 20-60 seconds about your craft")}</p>
              </div>

            </div>


            <div className="spoken-language-picker">
              <span className="spoken-language-label">
                {t("Which language will you speak in?")}
              </span>

              <div className="spoken-language-options">
                {SPOKEN_LANGUAGE_OPTIONS.map((option) => (
                  <button
                    key={option.code}
                    type="button"
                    className={`spoken-language-option ${
                      spokenLanguage === option.code ? "selected" : ""
                    }`}
                    onClick={() => setSpokenLanguage(option.code)}
                    disabled={isRecording || isRequesting || hasRecording}
                  >
                    {t(option.label)}
                  </button>
                ))}
              </div>
            </div>


            {!hasRecording ? (

              <div className="voice-area">

                <button
                  type="button"
                  className={`voice-button ${isRecording ? "recording" : ""}`}
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isRequesting}
                >
                  <span className="voice-ring"></span>

                  {isRequesting ? (
                    <Loader2 size={24} className="spin" />
                  ) : isRecording ? (
                    <Square size={20} />
                  ) : (
                    <Mic size={26} />
                  )}
                </button>

                <div className="voice-status">
                  <strong>
                    {isRequesting
                      ? t("Starting microphone...")
                      : isRecording
                      ? `${t("Recording...")} ${formatDuration(elapsedSeconds)}`
                      : t("Tap to record")}
                  </strong>

                  <span>
                    {isRecording
                      ? t("Tap to stop")
                      : t('Try: "This saree is handwoven from pure cotton using a traditional technique. It took me a week to make."')}
                  </span>
                </div>

                {isRecording && (
                  <div className="sound-wave">
                    <span></span><span></span><span></span><span></span>
                    <span></span><span></span><span></span>
                  </div>
                )}

              </div>

            ) : (

              <div className="recorded-audio-card">

                <div className="recorded-audio-info">

                  <div className="recorded-audio-icon">
                    <Mic size={16} />
                  </div>

                  <div>
                    <strong>{t("Voice note recorded")}</strong>
                    <span>{formatDuration(elapsedSeconds)} {t("duration")}</span>
                  </div>

                </div>

                <audio
                  controls
                  src={audioUrl}
                  className="recorded-audio-player"
                />

                <div className="recorded-audio-actions">
                  <button
                    type="button"
                    className="rerecord-button"
                    onClick={reRecord}
                    disabled={isUploading}
                  >
                    <RotateCcw size={13} />
                    {t("Re-record")}
                  </button>
                </div>

                {isUploading && (
                  <div className="image-uploading voice-inline-status">
                    <Loader2 size={13} className="spin" />
                    {t("Processing your voice...")}
                  </div>
                )}

                {uploadError && !isUploading && (
                  <div className="image-upload-error voice-inline-status">
                    <AlertCircle size={13} />
                    {uploadError}
                    <button type="button" onClick={uploadAndContinue}>
                      {t("Retry")}
                    </button>
                  </div>
                )}

              </div>

            )}


            {permissionError && (
              <div className="image-upload-error voice-inline-status">
                <AlertCircle size={13} />
                {permissionError}
              </div>
            )}


            {!hasRecording && (
              <div className="voice-example">
                <Sparkles size={12} />
                <span>
                  {t("Mention the material, technique, how long it took, and what makes it special.")}
                </span>
              </div>
            )}

          </div>

        </div>


        {/* =================================================
            FOOTER
        ================================================= */}

        <div className="creation-footer">

          <div className="footer-info">

            <div className="footer-ai-icon">
              <Sparkles size={21} />
            </div>

            <div>
              <strong>
                {t("CraftMitra AI will handle the rest")}
              </strong>
              <span>
                {t("Transcription \u00b7 Translation \u00b7 Description \u00b7 Pricing")}
              </span>
            </div>

          </div>

          <button
            type="button"
            className="generate-button"
            onClick={uploadAndContinue}
            disabled={!isRecorded}
          >
            <Sparkles size={18} />
            {isUploading ? t("Processing...") : t("Continue to AI Processing")}
            <span>&rarr;</span>
          </button>

        </div>

      </main>

    </div>
  );
}

export default VoiceCapture;