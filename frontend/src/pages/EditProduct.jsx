import { useMemo, useState } from "react";

import {
  ArrowLeft,
  Sparkles,
  Plus,
  X,
  Save,
  RotateCcw,
  Image as ImageIcon,
  Wand2
} from "lucide-react";

import {
  useLocation,
  useNavigate
} from "react-router-dom";

import "../styles/editProduct.css";
import { useLanguage } from "../context/LanguageContext";

// Same placeholder used by Step 9 - dynamic pricing isn't built yet.
const DEFAULT_PRICE = 250;

function EditProduct() {

  const navigate = useNavigate();
  const location = useLocation();

  const { t } = useLanguage();

  const productId = location.state?.productId;
  const imageId = location.state?.imageId;
  const voiceResult = location.state?.voiceResult;

  const previousProduct =
    location.state?.product || {};

  // Real photos from Steps 3-5: the original upload, and the AI
  // enhanced version (may be missing if enhancement failed/was
  // skipped - see the "continue with original photo" path in
  // AIProcessing.jsx).
  const originalImage =
    location.state?.image ||
    previousProduct.image ||
    null;

  const enhancedImage =
    location.state?.enhancedImage ||
    previousProduct.enhancedImage ||
    null;

  const story =
    location.state?.story ||
    previousProduct.story ||
    "";

  const language =
    location.state?.language ||
    previousProduct.language ||
    "English";

  // Which photo is currently shown - defaults to the enhanced one
  // when we have it, since that's the point of Step 4/5.
  const [showEnhanced, setShowEnhanced] =
    useState(Boolean(enhancedImage));

  const displayedImage =
    showEnhanced && enhancedImage
      ? enhancedImage
      : originalImage;


  const [productName, setProductName] =
    useState(
      t(previousProduct.name || "Handcrafted Product")
    );


  // -------------------------------------------------------
  // DESCRIPTION - in regional language / English / Hindi
  // -------------------------------------------------------
  // The AI description generator only produces English text (no
  // model to compose it in the artisan's own language yet), so the
  // "regional" tab shows the artisan's own normalized words instead
  // of pretending it's an AI translation. Each tab is independently
  // editable since the artisan may want to word things differently
  // per language.

  const regionalLabel =
    previousProduct.regionalLanguageLabel ||
    language ||
    "Regional";

  const initialDescriptions =
    previousProduct.descriptions || {
      regional: previousProduct.description || story || "",
      english: previousProduct.description || story || "",
      hindi: ""
    };

  const [descriptions, setDescriptions] =
    useState(initialDescriptions);

  const languageTabs = useMemo(() => {
    const tabs = [];

    // Skip a separate "regional" tab when the artisan already spoke
    // English - it would just duplicate the English tab.
    if (
      regionalLabel &&
      regionalLabel.toLowerCase() !== "english" &&
      descriptions.regional
    ) {
      tabs.push({ key: "regional", label: t(regionalLabel) });
    }

    tabs.push({ key: "english", label: t("English") });

    if (descriptions.hindi) {
      tabs.push({ key: "hindi", label: t("Hindi") });
    }

    return tabs;
  }, [regionalLabel, descriptions.regional, descriptions.hindi, t]);

  const [activeLang, setActiveLang] = useState(
    languageTabs.some((tab) => tab.key === "english") ? "english" : languageTabs[0]?.key
  );

  const updateActiveDescription = (value) => {
    setDescriptions((prev) => ({
      ...prev,
      [activeLang]: value
    }));
  };


  const [category, setCategory] =
    useState(
      previousProduct.category ||
      "Handicraft"
    );


  const [material, setMaterial] =
    useState(
      t(previousProduct.material || "")
    );


  const [technique, setTechnique] =
    useState(
      t(previousProduct.technique || "")
    );


  const [color, setColor] =
    useState(
      t(previousProduct.color || "")
    );


  const [tags, setTags] =
    useState(
      (previousProduct.tags || []).map((tag) => t(tag))
    );


  const [newTag, setNewTag] =
    useState("");


  const [price, setPrice] =
    useState(
      String(
        previousProduct.price ||
        DEFAULT_PRICE
      ).replace("₹", "")
    );


  const addTag = () => {

    const tag =
      newTag.trim();

    if (
      tag &&
      !tags.includes(tag)
    ) {

      setTags([
        ...tags,
        tag
      ]);

      setNewTag("");
    }
  };


  const removeTag = (tag) => {

    setTags(
      tags.filter(
        (item) => item !== tag
      )
    );
  };


  // =====================================================
  // SAVE -> continue to Publish (Step 11)
  // =====================================================

  const handleSave = () => {

    const updatedProduct = {

      ...previousProduct,

      id:
        previousProduct.id ||
        productId,

      name:
        productName.trim(),

      // Keep the canonical single-language description in sync with
      // whichever tab the artisan was last editing, but carry the
      // full multi-language set forward too.
      description:
        descriptions[activeLang]?.trim() || "",

      descriptions,

      regionalLanguageLabel: regionalLabel,

      category,

      material:
        material.trim(),

      technique:
        technique.trim(),

      color:
        color.trim(),

      tags,

      price:
        `₹${price}`,

      confidence:
        previousProduct.confidence ??
        null,

      image:
        originalImage,

      enhancedImage,

      story,

      language
    };


    navigate(
      "/publish",
      {
        state: {

          productId,
          imageId,
          voiceResult,

          image:
            displayedImage,

          story,

          language,

          product:
            updatedProduct

        }
      }
    );
  };


  const backTarget = () =>
    navigate(
      "/add-product",
      {
        replace: true
      }
    );


  return (

    <div className="edit-product-page">

      {/* HEADER */}

      <header className="edit-header">

        <button
          className="edit-back-button"
          onClick={backTarget}
        >

          <ArrowLeft size={16} />

          {t("Back to listing")}

        </button>


        <div className="edit-ai-label">

          <Sparkles size={14} />

          {t("AI GENERATED DETAILS")}

        </div>

        <div></div>

      </header>


      {/* INTRO */}

      <div className="edit-intro">

        <div className="edit-badge">

          <Sparkles size={12} />

          {t("REVIEW & EDIT")}

        </div>

        <h1>

          {t("Make it")} <span>{t("yours.")}</span>

        </h1>

        <p>

          Review the details generated by
          CraftMitra AI and make any changes.

        </p>

      </div>


      {/* MAIN */}

      <div className="edit-container">

        {/* IMAGE */}

        <div className="edit-image-section">

          <div className="edit-image-card">

            <div className="edit-image-placeholder">

              {displayedImage ? (

                <img
                  src={displayedImage}
                  alt={t(productName)}
                  className="edit-product-image"
                />

              ) : (

                <>

                  <div className="edit-craft-symbol">
                    ✦
                  </div>

                  <span>
                    {t("Product Image")}
                  </span>

                </>

              )}

            </div>


            {showEnhanced && enhancedImage && (

              <div className="enhanced-badge">

                <Sparkles size={12} />

                {t("AI enhanced")}

              </div>

            )}


            {/* ORIGINAL / ENHANCED TOGGLE */}

            {originalImage && (

              <div className="image-toggle">

                <button
                  type="button"
                  className={!showEnhanced || !enhancedImage ? "selected" : ""}
                  onClick={() => setShowEnhanced(false)}
                >
                  <ImageIcon size={12} />
                  {t("Original")}
                </button>

                <button
                  type="button"
                  className={showEnhanced && enhancedImage ? "selected" : ""}
                  onClick={() => enhancedImage && setShowEnhanced(true)}
                  disabled={!enhancedImage}
                >
                  <Wand2 size={12} />
                  {t("AI Enhanced")}
                </button>

              </div>

            )}


            {!enhancedImage && (

              <p className="image-toggle-note">
                {t(
                  "Enhancement isn't available for this photo - showing the original."
                )}
              </p>

            )}

          </div>


          <div className="ai-tip">

            <Sparkles size={15} />

            <div>

              <strong>
                {t("AI suggestion")}
              </strong>

              <p>
                Product details were generated
                from your photo and story.
              </p>

            </div>

          </div>

        </div>


        {/* FORM */}

        <div className="edit-form-card">

          <div className="form-heading">

            <div>

              <h2>
                Product Details
              </h2>

              <p>
                {t("Everything customers will see.")}
              </p>

            </div>

            <span className="ai-generated-pill">
              {t("AI generated")}
            </span>

          </div>


          {/* NAME */}

          <div className="form-field">

            <label>
              {t("Product Name")}
            </label>

            <input
              value={productName}
              onChange={(e) =>
                setProductName(
                  e.target.value
                )
              }
              placeholder={t("Give your product a name")}
            />

          </div>


          {/* DESCRIPTION - LANGUAGE TABS */}

          <div className="form-field">

            <label>
              {t("Description")}
            </label>

            {languageTabs.length > 1 && (

              <div className="description-lang-tabs">

                {languageTabs.map((tab) => (

                  <button
                    key={tab.key}
                    type="button"
                    className={activeLang === tab.key ? "selected" : ""}
                    onClick={() => setActiveLang(tab.key)}
                  >
                    {tab.label}
                  </button>

                ))}

              </div>

            )}

            <textarea
              value={descriptions[activeLang] || ""}
              onChange={(e) =>
                updateActiveDescription(e.target.value)
              }
              rows="5"
            />

            <span className="character-count">

              {(descriptions[activeLang] || "").length} {t("characters")}

            </span>

          </div>


          {/* CATEGORY + MATERIAL */}

          <div className="form-row">

            <div className="form-field">

              <label>
                {t("Category")}
              </label>

              <select
                value={category}
                onChange={(e) =>
                  setCategory(
                    e.target.value
                  )
                }
              >

                <option value="Handloom">{t("Handloom")}</option>
                <option value="Handicraft">{t("Handicraft")}</option>
                <option value="Pottery">{t("Pottery")}</option>
                <option value="Jewellery">{t("Jewellery")}</option>
                <option value="Wood Craft">{t("Wood Craft")}</option>
                <option value="Other">{t("Other")}</option>

              </select>

            </div>


            <div className="form-field">

              <label>
                {t("Material")}
              </label>

              <input
                value={material}
                onChange={(e) =>
                  setMaterial(
                    e.target.value
                  )
                }
              />

            </div>

          </div>


          {/* TECHNIQUE + COLOR */}

          <div className="form-row">

            <div className="form-field">

              <label>
                {t("Craft Technique")}
              </label>

              <input
                value={technique}
                onChange={(e) =>
                  setTechnique(
                    e.target.value
                  )
                }
              />

            </div>


            <div className="form-field">

              <label>
                {t("Primary Color")}
              </label>

              <input
                value={color}
                onChange={(e) =>
                  setColor(
                    e.target.value
                  )
                }
              />

            </div>

          </div>


          {/* TAGS */}

          <div className="form-field">

            <label>
              {t("Product Tags")}
            </label>

            <div className="edit-tags">

              {tags.map((tag) => (

                <span key={tag}>

                  #{tag}

                  <button
                    type="button"
                    onClick={() =>
                      removeTag(tag)
                    }
                  >

                    <X size={11} />

                  </button>

                </span>

              ))}

            </div>


            <div className="tag-input">

              <input
                value={newTag}
                onChange={(e) =>
                  setNewTag(
                    e.target.value
                  )
                }
                onKeyDown={(e) => {

                  if (e.key === "Enter") {

                    e.preventDefault();

                    addTag();

                  }

                }}
                placeholder={t("Add a tag...")}
              />


              <button
                type="button"
                onClick={addTag}
              >

                <Plus size={14} />

              </button>

            </div>

          </div>


          {/* PRICE */}

          <div className="price-edit-section">

            <div>

              <label>
                {t("Suggested Price")}
              </label>

              <div className="price-input">

                <span>₹</span>

                <input
                  type="number"
                  value={price}
                  onChange={(e) =>
                    setPrice(
                      e.target.value
                    )
                  }
                />

              </div>

            </div>

            <div className="price-note">

              <Sparkles size={13} />

              {t("AI suggested")}

            </div>

          </div>


          {/* ACTIONS */}

          <div className="edit-actions">

            <button
              className="cancel-edit"
              onClick={backTarget}
            >

              <RotateCcw size={14} />

              {t("Discard")}

            </button>


            <button
              className="save-edit"
              onClick={handleSave}
            >

              <Save size={15} />

              {t("Continue to Publish")}

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}

export default EditProduct;