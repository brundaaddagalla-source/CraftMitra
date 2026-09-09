import { useEffect, useState } from "react";
import { Sparkles, Check, Package, IndianRupee } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/aiProcessing.css";
import { useLanguage } from "../context/LanguageContext";

function AIProcessing() {
  const location = useLocation();
  const navigate = useNavigate();

  const { t } = useLanguage();

  const image = location.state?.image;
  const story = location.state?.story;
  const language = location.state?.language || "English";

  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const steps = [
    {
      title: "Analyzing your craft image",
      description: "Identifying the product, materials and craft characteristics",
      icon: <Sparkles size={18} />
    },
    {
      title: "Understanding your story",
      description: `Converting your ${language} voice description into product details`,
      icon: <Sparkles size={18} />
    },
    {
      title: "Creating your product listing",
      description: "Generating a professional product name and description",
      icon: <Package size={18} />
    },
    {
      title: "Calculating a fair price",
      description: "Preparing a suitable price recommendation",
      icon: <IndianRupee size={18} />
    }
  ];

  useEffect(() => {
    const timers = [
      setTimeout(() => {
        setCurrentStep(1);
        setProgress(25);
      }, 1200),

      setTimeout(() => {
        setCurrentStep(2);
        setProgress(50);
      }, 2400),

      setTimeout(() => {
        setCurrentStep(3);
        setProgress(75);
      }, 3600),

      setTimeout(() => {
        setCurrentStep(4);
        setProgress(100);
      }, 4800),

      setTimeout(() => {
        navigate("/edit-product", {
          state: {
            image,
            story,
            language,
            product: {
              name: "Handwoven Cotton Saree",
              description: "A beautifully handwoven cotton saree crafted using traditional weaving techniques. Its elegant indigo tones and handcrafted texture reflect the skill and heritage of the artisan.",
              category: "Handloom",
              material: "Cotton",
              technique: "Traditional Hand Weaving",
              color: "Indigo",
              tags: [
                "Handloom",
                "Cotton",
                "Handcrafted",
                "Traditional"
              ],
              price: "₹2599",
              confidence: 94
            }
          }
        });
      }, 5600)
    ];

    return () => {
      timers.forEach(clearTimeout);
    };
  }, [navigate, image, story, language]);

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

          {steps.map((step, index) => {

            const completed = index < currentStep;
            const active = index === currentStep;

            return (
              <div
                className={`processing-step ${
                  completed ? "completed" : ""
                } ${active ? "active" : ""}`}
                key={step.title}
              >

                {/* STEP ICON */}

                <div className="step-icon">

                  {completed ? (
                    <Check size={19} />
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

      </div>

    </div>
  );
}

export default AIProcessing;