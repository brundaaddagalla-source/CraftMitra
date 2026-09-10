import { useRef, useState, useEffect } from "react";
import {
  ArrowLeft,
  Camera,
  Sparkles,
  X,
  Check,
  Upload,
  AlertCircle,
  Loader2
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import "../styles/addProduct.css";

// Convert the base64 data URL we get from <canvas>.toDataURL() (camera
// capture) or FileReader (file picker preview) into a real Blob/File
// that can be sent as multipart form data.
function dataUrlToFile(dataUrl, filename) {
  const [header, base64Data] = dataUrl.split(",");
  const mimeMatch = header.match(/:(.*?);/);
  const mimeType = mimeMatch ? mimeMatch[1] : "image/jpeg";

  const binary = atob(base64Data);
  const bytes = new Uint8Array(binary.length);

  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }

  return new File([bytes], filename, { type: mimeType });
}

function AddProduct() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const { user } = useAuth();

  // Local preview of the captured/selected photo (base64 data URL).
  const [image, setImage] = useState(null);

  // Server-side state for that photo, once it's been uploaded.
  const [productId, setProductId] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const [showCamera, setShowCamera] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const hasAutoOpenedCameraRef = useRef(false);

  // Guards against creating two draft products if the artisan somehow
  // triggers two uploads in quick succession before the first
  // "create product" call has resolved.
  const draftProductPromiseRef = useRef(null);

  // =====================================================
  // DRAFT PRODUCT
  // =====================================================
  //
  // A ProductImage row can't exist without a Product row to belong to
  // (product_id is a required foreign key), but the artisan hasn't
  // entered any product details yet at this point in the flow - that
  // only happens later, at the review screen (Step 10) and publish
  // step (Step 11). So we silently create a draft product the moment
  // the first photo is captured, then Step 11 will PATCH this same
  // row with the real details instead of creating a new one.

  const ensureDraftProduct = async () => {
    if (productId) return productId;

    if (!draftProductPromiseRef.current) {
      draftProductPromiseRef.current = (async () => {
        if (!user?.artisanId) {
          throw new Error(
            t("Your artisan profile could not be found. Please sign in again.")
          );
        }

        const product = await api.post("/products", {
          artisan_id: user.artisanId,
          product_name: "Untitled product",
          category: "uncategorized",
          craft_details: {},
          status: "draft"
        });

        setProductId(product.id);
        return product.id;
      })();
    }

    return draftProductPromiseRef.current;
  };

  // =====================================================
  // UPLOAD PHOTO
  // =====================================================

  const uploadPhoto = async (dataUrl) => {
    setUploading(true);
    setUploadError("");

    try {
      const id = await ensureDraftProduct();
      const file = dataUrlToFile(dataUrl, "product-photo.jpg");

      const image = await api.uploadFile(
        `/products/${id}/images/upload`,
        file
      );

      setUploadedImage(image);
    } catch (error) {
      console.error(error);
      setUploadError(
        error.message || t("Couldn't upload your photo. Please try again.")
      );
    } finally {
      setUploading(false);
    }
  };

  const retryUpload = () => {
    if (image) uploadPhoto(image);
  };

  // =====================================================
  // IMAGE UPLOAD (FILE PICKER)
  // =====================================================

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onloadend = () => {
      setImage(reader.result);
      uploadPhoto(reader.result);
    };

    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setImage(null);
    setUploadError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    // Best-effort cleanup - if the photo already made it to the
    // server, remove that row too rather than leaving an orphaned
    // image behind on the draft product.
    if (uploadedImage && productId) {
      api
        .delete(`/products/${productId}/images/${uploadedImage.id}`)
        .catch((error) => console.error("Failed to remove image:", error));
    }

    setUploadedImage(null);
  };

  // =====================================================
  // CAMERA
  // =====================================================

  const openCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      alert(
        t("Camera is not available on this device or browser. This can also happen if the page isn't loaded over HTTPS. Please upload a photo instead.")
      );
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment"
        },
        audio: false
      });

      streamRef.current = stream;
      setIsCameraReady(false);
      setShowCamera(true);
    } catch (error) {
      console.error(error);

      alert(
        t("Camera access was blocked. Please allow camera permission in your browser.")
      );
    }
  };

  // Launch the camera the moment this page opens - Add Product should
  // go straight to the camera, not to a form. If the artisan already
  // has a captured photo (e.g. they navigated back to this screen),
  // don't reopen it on top of what they already took.
  useEffect(() => {
    if (hasAutoOpenedCameraRef.current) return;
    if (image) return;

    hasAutoOpenedCameraRef.current = true;
    openCamera();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Attach the stream once the <video> element actually exists in the DOM,
  // and wait for real video data before allowing a capture. Using a fixed
  // setTimeout here was unreliable — on slower devices the video element
  // wasn't mounted yet, or metadata hadn't loaded, so captures came out blank.
  useEffect(() => {
    if (!showCamera) return;

    const video = videoRef.current;
    const stream = streamRef.current;

    if (!video || !stream) return;

    video.srcObject = stream;

    const handleLoadedMetadata = () => {
      video
        .play()
        .then(() => setIsCameraReady(true))
        .catch((error) => {
          console.error("Video play failed:", error);
        });
    };

    video.addEventListener("loadedmetadata", handleLoadedMetadata);

    return () => {
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
    };
  }, [showCamera]);

  const closeCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });

      streamRef.current = null;
    }

    setShowCamera(false);
    setIsCameraReady(false);
  };

  // Stop the camera if the user navigates away without closing it
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    if (!video.videoWidth || !video.videoHeight) {
      // Video hasn't produced a real frame yet - avoid capturing a blank image.
      console.warn("Camera not ready yet, ignoring capture request.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    const capturedImage = canvas.toDataURL(
      "image/jpeg",
      0.9
    );

    setImage(capturedImage);
    closeCamera();
    uploadPhoto(capturedImage);
  };

  // =====================================================
  // CONTINUE
  // =====================================================
  //
  // Step 6: the photo has been captured and (hopefully) already
  // finished uploading/enhancing in the background. Next stop is the
  // voice recording screen - AI processing (Step 9) happens after
  // that, once both the image and the voice pipeline have run.

  const continueToVoiceCapture = () => {
    if (!image) {
      alert(t("Please upload a product photo or take a photo."));
      return;
    }

    if (!uploadedImage) {
      alert(t("Please wait for your photo to finish uploading."));
      return;
    }

    navigate("/voice-capture", {
      state: {
        productId,
        imageId: uploadedImage.id,
        image: uploadedImage.image_url
      }
    });
  };

  return (
    <div className="add-product-page">

      {/* =================================================
          TOPBAR
      ================================================= */}

      <header className="add-product-topbar">

        <button
          type="button"
          className="back-button"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>

        <div className="add-product-brand">

          <div className="brand-symbol">
            <Sparkles size={16} />
          </div>

          <span>CraftMitra</span>

        </div>

        <div className="save-draft">

          <div className="save-dot"></div>

          Auto-saving

        </div>

      </header>


      {/* =================================================
          PROGRESS
      ================================================= */}

      <div className="creation-progress">

        <div className="progress-step active">
          <div className="progress-number">1</div>
          <span>Product</span>
        </div>

        <div className="progress-line"></div>

        <div className="progress-step">
          <div className="progress-number">2</div>
          <span>Voice Story</span>
        </div>

        <div className="progress-line"></div>

        <div className="progress-step">
          <div className="progress-number">3</div>
          <span>AI Processing</span>
        </div>

        <div className="progress-line"></div>

        <div className="progress-step">
          <div className="progress-number">4</div>
          <span>Review</span>
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
            Let's bring your craft
            <span> to the world.</span>
          </h1>

          <p>
            Share a clear photo of your craft. CraftMitra will enhance
            it and walk you through the rest next.
          </p>

        </div>


        {/* =================================================
            PHOTO
        ================================================= */}

        <div className="creation-grid single-card">

          <div className="creation-card">

            <div className="card-heading">

              <div className="heading-icon">
                <Camera size={22} />
              </div>

              <div>
                <h2>Show us your craft</h2>
                <p>Upload a photo or take one now</p>
              </div>

            </div>


            {image ? (

              <div className="selected-image">

                <img
                  src={image}
                  alt="Product"
                />

                <button
                  type="button"
                  className="remove-image"
                  onClick={removeImage}
                  disabled={uploading}
                >
                  <X size={20} />
                </button>

                {uploading && (
                  <div className="image-uploading">
                    <Loader2 size={13} className="spin" />
                    Uploading...
                  </div>
                )}

                {!uploading && uploadedImage && (
                  <div className="image-success">
                    <Check size={13} />
                    Photo uploaded
                  </div>
                )}

                {!uploading && uploadError && (
                  <div className="image-upload-error">
                    <AlertCircle size={13} />
                    {uploadError}
                    <button type="button" onClick={retryUpload}>
                      Retry
                    </button>
                  </div>
                )}

              </div>

            ) : (

              <div className="upload-area">

                <div className="upload-icon">
                  <Camera size={28} />
                </div>

                <h3>Add product photo</h3>

                <p>
                  Upload an existing photo or take one now
                </p>


                {/* TWO OPTIONS */}

                <div className="upload-options">

                  <button
                    type="button"
                    onClick={() =>
                      fileInputRef.current?.click()
                    }
                  >
                    <Upload size={13} />
                    Upload File
                  </button>


                  <button
                    type="button"
                    onClick={openCamera}
                  >
                    <Camera size={13} />
                    Take Photo
                  </button>

                </div>


                <small>
                  JPG, PNG or WEBP · Clear product photos work best
                </small>

              </div>

            )}


            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={handleImageUpload}
            />

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
                CraftMitra AI will handle the rest
              </strong>

              <span>
                Image enhancement · Catalog · Translation · Pricing
              </span>

            </div>

          </div>


          <button
            type="button"
            className="generate-button"
            onClick={continueToVoiceCapture}
            disabled={uploading || !uploadedImage}
          >

            <Sparkles size={18} />

            {uploading ? "Uploading..." : "Continue to Voice Story"}

            <span>→</span>

          </button>

        </div>

      </main>


      {/* =================================================
          CAMERA MODAL
      ================================================= */}

      {showCamera && (

        <div className="camera-overlay">

          <div className="camera-modal">

            <div className="camera-header">

              <div>
                <span>CRAFTMITRA CAMERA</span>
                <h2>Take product photo</h2>
              </div>

              <button
                type="button"
                className="camera-close"
                onClick={closeCamera}
              >
                <X size={18} />
              </button>

            </div>


            <div className="camera-preview">

              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
              />

              <div className="camera-frame"></div>

              <div className="camera-tip">
                {isCameraReady
                  ? "Position your craft inside the frame"
                  : "Starting camera..."}
              </div>

            </div>


            <div className="camera-controls">

              <button
                type="button"
                className="camera-cancel"
                onClick={closeCamera}
              >
                Cancel
              </button>

              <button
                type="button"
                className="capture-button"
                onClick={capturePhoto}
                disabled={!isCameraReady}
              >

                <div className="capture-inner">
                  <Camera size={22} />
                </div>

                {isCameraReady ? "Take Photo" : "Starting..."}

              </button>

              <div className="camera-placeholder"></div>

            </div>

          </div>

        </div>

      )}

      <canvas
        ref={canvasRef}
        style={{ display: "none" }}
      />

    </div>
  );
}

export default AddProduct;