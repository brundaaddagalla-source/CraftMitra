// import { useState, useRef, useEffect } from "react";
// import {
//   ArrowLeft,
//   Camera,
//   Mic,
//   Sparkles,
//   X,
//   Check,
//   Globe,
//   Upload
// } from "lucide-react";
// import { useNavigate } from "react-router-dom";
// import { useLanguage } from "../context/LanguageContext";
// import "../styles/addProduct.css";

// function AddProduct() {
//   const navigate = useNavigate();
//   const { language: uiLanguage, t } = useLanguage();

//   const [image, setImage] = useState(null);
//   const [story, setStory] = useState("");
//   const [isRecording, setIsRecording] = useState(false);
//   const [language, setLanguage] = useState(uiLanguage === "te" ? "Telugu" : "English");

//   useEffect(() => {
//     setLanguage(uiLanguage === "te" ? "Telugu" : "English");
//   }, [uiLanguage]);

//   const [showCamera, setShowCamera] = useState(false);

//   const fileInputRef = useRef(null);
//   const videoRef = useRef(null);
//   const canvasRef = useRef(null);
//   const recognitionRef = useRef(null);
//   const streamRef = useRef(null);

//   // =====================================================
//   // IMAGE UPLOAD
//   // =====================================================

//   const handleImageUpload = (e) => {
//     const file = e.target.files?.[0];

//     if (!file) return;

//     const reader = new FileReader();

//     reader.onloadend = () => {
//       setImage(reader.result);
//     };

//     reader.readAsDataURL(file);
//   };

//   const removeImage = () => {
//     setImage(null);

//     if (fileInputRef.current) {
//       fileInputRef.current.value = "";
//     }
//   };

//   // =====================================================
//   // CAMERA
//   // =====================================================

//   const openCamera = async () => {
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({
//         video: {
//           facingMode: "environment"
//         },
//         audio: false
//       });

//       streamRef.current = stream;
//       setShowCamera(true);

//       setTimeout(() => {
//         if (videoRef.current) {
//           videoRef.current.srcObject = stream;
//         }
//       }, 100);

//     } catch (error) {
//       console.error(error);

//       alert(
//         t("Camera access was blocked. Please allow camera permission in your browser.")
//       );
//     }
//   };

//   const closeCamera = () => {
//     if (streamRef.current) {
//       streamRef.current.getTracks().forEach((track) => {
//         track.stop();
//       });

//       streamRef.current = null;
//     }

//     setShowCamera(false);
//   };

//   const capturePhoto = () => {
//     const video = videoRef.current;
//     const canvas = canvasRef.current;

//     if (!video || !canvas) return;

//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;

//     const context = canvas.getContext("2d");

//     context.drawImage(
//       video,
//       0,
//       0,
//       canvas.width,
//       canvas.height
//     );

//     const capturedImage = canvas.toDataURL(
//       "image/jpeg",
//       0.9
//     );

//     setImage(capturedImage);

//     closeCamera();
//   };

//   // =====================================================
//   // VOICE
//   // =====================================================

//   const getSpeechLanguage = () => {
//     const languages = {
//       English: "en-IN",
//       Telugu: "te-IN",
//       Hindi: "hi-IN",
//       Tamil: "ta-IN",
//       Kannada: "kn-IN"
//     };

//     return languages[language] || "en-IN";
//   };

//   const toggleRecording = () => {
//     const SpeechRecognition =
//       window.SpeechRecognition ||
//       window.webkitSpeechRecognition;

//     if (!SpeechRecognition) {
//       alert(
//         t("Voice recognition is not supported in this browser. Please use Google Chrome.")
//       );
//       return;
//     }

//     if (isRecording) {
//       recognitionRef.current?.stop();
//       setIsRecording(false);
//       return;
//     }

//     const recognition = new SpeechRecognition();

//     recognition.continuous = true;
//     recognition.interimResults = false;
//     recognition.lang = getSpeechLanguage();

//     recognition.onstart = () => {
//       setIsRecording(true);
//     };

//     recognition.onresult = (event) => {
//       let finalText = "";

//       for (
//         let i = event.resultIndex;
//         i < event.results.length;
//         i++
//       ) {
//         if (event.results[i].isFinal) {
//           finalText += event.results[i][0].transcript;
//         }
//       }

//       if (finalText.trim()) {
//         setStory((previous) =>
//           previous
//             ? `${previous} ${finalText.trim()}`
//             : finalText.trim()
//         );
//       }
//     };

//     recognition.onerror = (event) => {
//       console.error(
//         "Speech recognition error:",
//         event.error
//       );

//       setIsRecording(false);
//     };

//     recognition.onend = () => {
//       setIsRecording(false);
//     };

//     recognitionRef.current = recognition;

//     try {
//       recognition.start();
//     } catch (error) {
//       console.error(error);
//     }
//   };

//   // =====================================================
//   // CREATE WITH AI
//   // =====================================================

//   const createWithAI = () => {
//     if (!image) {
//       alert("Please upload a product photo or take a photo.");
//       return;
//     }

//     if (!story.trim()) {
//       alert("Please tell us about your product first.");
//       return;
//     }

//     navigate("/ai-processing", {
//       state: {
//         image: image,
//         story: story.trim(),
//         language: language
//       }
//     });
//   };

//   return (
//     <div className="add-product-page">

//       {/* =================================================
//           TOPBAR
//       ================================================= */}

//       <header className="add-product-topbar">

//         <button
//           type="button"
//           className="back-button"
//           onClick={() => navigate("/")}
//         >
//           <ArrowLeft size={16} />
//           Back to Dashboard
//         </button>

//         <div className="add-product-brand">

//           <div className="brand-symbol">
//             <Sparkles size={16} />
//           </div>

//           <span>CraftMitra</span>

//         </div>

//         <div className="save-draft">

//           <div className="save-dot"></div>

//           Auto-saving

//         </div>

//       </header>


//       {/* =================================================
//           PROGRESS
//       ================================================= */}

//       <div className="creation-progress">

//         <div className="progress-step active">
//           <div className="progress-number">1</div>
//           <span>Product</span>
//         </div>

//         <div className="progress-line"></div>

//         <div className="progress-step">
//           <div className="progress-number">2</div>
//           <span>AI Processing</span>
//         </div>

//         <div className="progress-line"></div>

//         <div className="progress-step">
//           <div className="progress-number">3</div>
//           <span>Review</span>
//         </div>

//       </div>


//       {/* =================================================
//           MAIN
//       ================================================= */}

//       <main className="add-product-main">

//         <div className="creation-header">

//           <div className="creation-badge">
//             <Sparkles size={12} />
//             AI-POWERED PRODUCT CREATION
//           </div>

//           <h1>
//             Let's bring your craft
//             <span> to the world.</span>
//           </h1>

//           <p>
//             Share a photo and tell us about your product.
//             CraftMitra will create a professional listing for you.
//           </p>

//         </div>


//         {/* =================================================
//             PHOTO + STORY
//         ================================================= */}

//         <div className="creation-grid">

//           {/* =================================================
//               PHOTO
//           ================================================= */}

//           <div className="creation-card">

//             <div className="card-heading">

//               <div className="heading-icon">
//                 <Camera size={22} />
//               </div>

//               <div>
//                 <h2>Show us your craft</h2>
//                 <p>Upload a photo or take one now</p>
//               </div>

//             </div>


//             {image ? (

//               <div className="selected-image">

//                 <img
//                   src={image}
//                   alt="Product"
//                 />

//                 <button
//                   type="button"
//                   className="remove-image"
//                   onClick={removeImage}
//                 >
//                   <X size={20} />
//                 </button>

//                 <div className="image-success">
//                   <Check size={13} />
//                   Photo added
//                 </div>

//               </div>

//             ) : (

//               <div className="upload-area">

//                 <div className="upload-icon">
//                   <Camera size={28} />
//                 </div>

//                 <h3>Add product photo</h3>

//                 <p>
//                   Upload an existing photo or take one now
//                 </p>


//                 {/* TWO OPTIONS */}

//                 <div className="upload-options">

//                   <button
//                     type="button"
//                     onClick={() =>
//                       fileInputRef.current?.click()
//                     }
//                   >
//                     <Upload size={13} />
//                     Upload File
//                   </button>


//                   <button
//                     type="button"
//                     onClick={openCamera}
//                   >
//                     <Camera size={13} />
//                     Take Photo
//                   </button>

//                 </div>


//                 <small>
//                   JPG, PNG or WEBP · Clear product photos work best
//                 </small>

//               </div>

//             )}


//             <input
//               ref={fileInputRef}
//               type="file"
//               accept="image/*"
//               hidden
//               onChange={handleImageUpload}
//             />

//           </div>


//           {/* =================================================
//               STORY
//           ================================================= */}

//           <div className="creation-card">

//             <div className="card-heading">

//               <div className="heading-icon voice-heading-icon">
//                 <Mic size={22} />
//               </div>

//               <div>

//                 <h2>Tell us your story</h2>

//                 <p>
//                   No typing required — just speak naturally
//                 </p>

//               </div>

//             </div>


//             <div className="voice-area">

//               <button
//                 type="button"
//                 className={`voice-button ${
//                   isRecording ? "recording" : ""
//                 }`}
//                 onClick={toggleRecording}
//               >

//                 <div className="voice-ring"></div>

//                 <Mic size={29} />

//               </button>


//               <div className="voice-status">

//                 <strong>
//                   {isRecording
//                     ? "Listening..."
//                     : "Tap to speak"}
//                 </strong>

//                 <span>
//                   {isRecording
//                     ? `Speaking in ${language}`
//                     : "Tell us what makes your craft special"}
//                 </span>

//               </div>


//               {isRecording && (

//                 <div className="sound-wave">

//                   <span></span>
//                   <span></span>
//                   <span></span>
//                   <span></span>
//                   <span></span>
//                   <span></span>
//                   <span></span>

//                 </div>

//               )}

//             </div>


//             {/* STORY TEXT */}

//             <div className="voice-example">

//               <Sparkles size={15} />

//               <span>
//                 {story
//                   ? `What you said: "${story}"`
//                   : 'Example: "This is a handwoven cotton saree made using traditional techniques..."'}
//               </span>

//             </div>

//           </div>

//         </div>


        

//         {/* <section className="language-section">

//           <div className="language-heading">

//             <div className="language-title">

//               <div className="language-icon">
//                 <Globe size={18} />
//               </div>

//               <div>

//                 <h2>Product language</h2>

//                 <p>
//                   Choose the language used for your product story
//                 </p>

//               </div>

//             </div>

//             <div className="language-ai">
//               AI translation available
//             </div>

//           </div>


//           <div className="language-options">

//             {[
//               "English",
//               "Telugu",
//               "Hindi",
//               "Tamil",
//               "Kannada"
//             ].map((lang) => (

//               <button
//                 key={lang}
//                 type="button"
//                 className={`language-option ${
//                   language === lang
//                     ? "selected"
//                     : ""
//                 }`}
//                 onClick={() => setLanguage(lang)}
//               >
//                 {lang}
//               </button>

//             ))}

//           </div>

//         </section> */}


//         {/* =================================================
//             FOOTER
//         ================================================= */}

//         <div className="creation-footer">

//           <div className="footer-info">

//             <div className="footer-ai-icon">
//               <Sparkles size={21} />
//             </div>

//             <div>

//               <strong>
//                 CraftMitra AI will handle the rest
//               </strong>

//               <span>
//                 Image enhancement · Catalog · Translation · Pricing
//               </span>

//             </div>

//           </div>


//           <button
//             type="button"
//             className="generate-button"
//             onClick={createWithAI}
//           >

//             <Sparkles size={18} />

//             Create with AI

//             <span>→</span>

//           </button>

//         </div>

//       </main>


//       {/* =================================================
//           CAMERA MODAL
//       ================================================= */}

//       {showCamera && (

//         <div className="camera-overlay">

//           <div className="camera-modal">

//             <div className="camera-header">

//               <div>
//                 <span>CRAFTMITRA CAMERA</span>
//                 <h2>Take product photo</h2>
//               </div>

//               <button
//                 type="button"
//                 className="camera-close"
//                 onClick={closeCamera}
//               >
//                 <X size={18} />
//               </button>

//             </div>


//             <div className="camera-preview">

//               <video
//                 ref={videoRef}
//                 autoPlay
//                 playsInline
//               />

//               <div className="camera-frame"></div>

//               <div className="camera-tip">
//                 Position your craft inside the frame
//               </div>

//             </div>


//             <div className="camera-controls">

//               <button
//                 type="button"
//                 className="camera-cancel"
//                 onClick={closeCamera}
//               >
//                 Cancel
//               </button>

//               <button
//                 type="button"
//                 className="capture-button"
//                 onClick={capturePhoto}
//               >

//                 <div className="capture-inner">
//                   <Camera size={22} />
//                 </div>

//                 Take Photo

//               </button>

//               <div className="camera-placeholder"></div>

//             </div>

//           </div>

//         </div>

//       )}

//       <canvas
//         ref={canvasRef}
//         style={{ display: "none" }}
//       />

//     </div>
//   );
// }

// export default AddProduct;

import { useState, useRef, useEffect } from "react";
import {
  ArrowLeft,
  Camera,
  Mic,
  Sparkles,
  X,
  Check,
  Globe,
  Upload
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import "../styles/addProduct.css";

function AddProduct() {
  const navigate = useNavigate();
  const { language: uiLanguage, t } = useLanguage();

  const [image, setImage] = useState(null);
  const [story, setStory] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState(uiLanguage === "te" ? "Telugu" : "English");

  useEffect(() => {
    setLanguage(uiLanguage === "te" ? "Telugu" : "English");
  }, [uiLanguage]);

  const [showCamera, setShowCamera] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const recognitionRef = useRef(null);
  const streamRef = useRef(null);

  // =====================================================
  // IMAGE UPLOAD
  // =====================================================

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onloadend = () => {
      setImage(reader.result);
    };

    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setImage(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
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
  };

  // =====================================================
  // VOICE
  // =====================================================

  const getSpeechLanguage = () => {
    const languages = {
      English: "en-IN",
      Telugu: "te-IN",
      Hindi: "hi-IN",
      Tamil: "ta-IN",
      Kannada: "kn-IN"
    };

    return languages[language] || "en-IN";
  };

  const toggleRecording = () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        t("Voice recognition is not supported in this browser. Please use Google Chrome.")
      );
      return;
    }

    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = getSpeechLanguage();

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onresult = (event) => {
      let finalText = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        if (event.results[i].isFinal) {
          finalText += event.results[i][0].transcript;
        }
      }

      if (finalText.trim()) {
        setStory((previous) =>
          previous
            ? `${previous} ${finalText.trim()}`
            : finalText.trim()
        );
      }
    };

    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );

      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (error) {
      console.error(error);
    }
  };

  // =====================================================
  // CREATE WITH AI
  // =====================================================

  const createWithAI = () => {
    if (!image) {
      alert("Please upload a product photo or take a photo.");
      return;
    }

    if (!story.trim()) {
      alert("Please tell us about your product first.");
      return;
    }

    navigate("/ai-processing", {
      state: {
        image: image,
        story: story.trim(),
        language: language
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
          <span>AI Processing</span>
        </div>

        <div className="progress-line"></div>

        <div className="progress-step">
          <div className="progress-number">3</div>
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
            Share a photo and tell us about your product.
            CraftMitra will create a professional listing for you.
          </p>

        </div>


        {/* =================================================
            PHOTO + STORY
        ================================================= */}

        <div className="creation-grid">

          {/* =================================================
              PHOTO
          ================================================= */}

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
                >
                  <X size={20} />
                </button>

                <div className="image-success">
                  <Check size={13} />
                  Photo added
                </div>

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


          {/* =================================================
              STORY
          ================================================= */}

          <div className="creation-card">

            <div className="card-heading">

              <div className="heading-icon voice-heading-icon">
                <Mic size={22} />
              </div>

              <div>

                <h2>Tell us your story</h2>

                <p>
                  No typing required — just speak naturally
                </p>

              </div>

            </div>


            <div className="voice-area">

              <button
                type="button"
                className={`voice-button ${
                  isRecording ? "recording" : ""
                }`}
                onClick={toggleRecording}
              >

                <div className="voice-ring"></div>

                <Mic size={29} />

              </button>


              <div className="voice-status">

                <strong>
                  {isRecording
                    ? "Listening..."
                    : "Tap to speak"}
                </strong>

                <span>
                  {isRecording
                    ? `Speaking in ${language}`
                    : "Tell us what makes your craft special"}
                </span>

              </div>


              {isRecording && (

                <div className="sound-wave">

                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              )}

            </div>


            {/* STORY TEXT */}

            <div className="voice-example">

              <Sparkles size={15} />

              <span>
                {story
                  ? `What you said: "${story}"`
                  : 'Example: "This is a handwoven cotton saree made using traditional techniques..."'}
              </span>

            </div>

          </div>

        </div>


        

        {/* <section className="language-section">

          <div className="language-heading">

            <div className="language-title">

              <div className="language-icon">
                <Globe size={18} />
              </div>

              <div>

                <h2>Product language</h2>

                <p>
                  Choose the language used for your product story
                </p>

              </div>

            </div>

            <div className="language-ai">
              AI translation available
            </div>

          </div>


          <div className="language-options">

            {[
              "English",
              "Telugu",
              "Hindi",
              "Tamil",
              "Kannada"
            ].map((lang) => (

              <button
                key={lang}
                type="button"
                className={`language-option ${
                  language === lang
                    ? "selected"
                    : ""
                }`}
                onClick={() => setLanguage(lang)}
              >
                {lang}
              </button>

            ))}

          </div>

        </section> */}


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
            onClick={createWithAI}
          >

            <Sparkles size={18} />

            Create with AI

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