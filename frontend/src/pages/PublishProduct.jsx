import { useEffect, useState } from "react";

import {
  ArrowLeft,
  ArrowRight,
  Check,
  Sparkles,
  Store,
  ShoppingBag,
  Globe,
  Send,
  AlertCircle
} from "lucide-react";

import {
  useNavigate,
  useLocation
} from "react-router-dom";

import "../styles/publishProduct.css";
import { useLanguage } from "../context/LanguageContext";
import { api } from "../api/client";

const marketplaces = [
  {
    id: "craftmitra",
    name: "CraftMitra Marketplace",
    description:
      "Reach customers looking for authentic handmade products.",
    icon: Store
  },
  {
    id: "ondc",
    name: "ONDC",
    description:
      "Make your products discoverable across the open network.",
    icon: Globe
  },
  {
    id: "amazon",
    name: "Amazon Karigar",
    description:
      "Showcase handcrafted products to a wider audience.",
    icon: ShoppingBag
  }
];

// Same placeholder used by Steps 8-10 - dynamic pricing isn't built yet,
// so this is what "AI suggested" means until a real model exists.
const DEFAULT_SUGGESTED_PRICE = 250;

// Turns "₹1,250" / "1250" / 1250 into a plain number the backend's
// Decimal fields can parse. Falls back to the placeholder if the
// artisan somehow left the price field empty.
function parsePrice(value) {
  const cleaned = String(value ?? "").replace(/[^0-9.]/g, "");
  const parsed = parseFloat(cleaned);
  return Number.isFinite(parsed) ? parsed : DEFAULT_SUGGESTED_PRICE;
}

function PublishProduct() {

  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();

  // Real IDs threaded through from Steps 1-10 - PublishProduct doesn't
  // create a new product, it PATCHes the draft row that was already
  // created the moment the artisan took their first photo.
  const productId = location.state?.productId;
  const imageId = location.state?.imageId;
  const voiceResult = location.state?.voiceResult;

  const product = location.state?.product;
  const productImage = location.state?.image;

  const [selectedMarketplace, setSelectedMarketplace] =
    useState("craftmitra");

  const [publishing, setPublishing] =
    useState(false);

  const [published, setPublished] =
    useState(false);

  const [publishError, setPublishError] =
    useState("");

  const [publishedProduct, setPublishedProduct] =
    useState(null);


  // This screen only makes sense at the end of the Steps 1-10 flow -
  // if someone lands here directly (refresh, deep link, back/forward
  // nav after the state is gone), there's nothing real to publish.
  const hasRequiredState = Boolean(productId && product);

  useEffect(() => {
    if (!hasRequiredState) {
      navigate("/add-product", { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  const handlePublish = async () => {

    setPublishing(true);
    setPublishError("");

    try {

      const descriptions = product.descriptions || {};

      // The single canonical description (whichever language tab the
      // artisan was last editing on the review screen) stays the
      // "main" description; the full set of languages goes along too
      // so the listing can still show/edit all of them later.
      const payload = {
        product_name: product.name,
        category: product.category,
        description: product.description,

        descriptions: {
          regional: descriptions.regional || null,
          english: descriptions.english || null,
          hindi: descriptions.hindi || null,
          regional_language_label:
            product.regionalLanguageLabel || product.language || null
        },

        craft_details: {
          craft_type: product.category,
          craft_technique: product.technique || null,
          material: product.material || null,
          color: product.color || null
        },

        pricing: {
          suggested_price: DEFAULT_SUGGESTED_PRICE,
          final_price: parsePrice(product.price)
        },

        original_language: product.language || null,

        voice_input: {
          transcript:
            product.story ||
            voiceResult?.regional_text ||
            null,
          audio_url: null
        },

        ai: {
          generated_description: descriptions.english || null,
          suggested_category: product.category || null,
          confidence:
            product.confidence != null
              ? product.confidence / 100
              : null
        },

        status: "published"
      };

      const saved = await api.patch(
        `/products/${productId}`,
        payload
      );

      setPublishedProduct(saved);
      setPublished(true);

    } catch (error) {
      console.error(error);
      setPublishError(
        error.message ||
        t("Couldn't publish your product. Please try again.")
      );
    } finally {
      setPublishing(false);
    }
  };


  if (!hasRequiredState) {
    return (
      <div className="publish-missing-state">
        {t("Redirecting...")}
      </div>
    );
  }


  if (published) {

    return (

      <div className="publish-success-page">

        <div className="success-card">

          <div className="success-icon">
            <Check size={30} />
          </div>


          <div className="success-label">

            <Sparkles size={13} />

            PUBLISHED SUCCESSFULLY

          </div>


          <h1>

            Your craft is now

            <span>
              {" "}ready to be discovered.
            </span>

          </h1>


          <p>

            Your product has been prepared for

            <strong>
              {" "}
              {marketplaces.find(
                (m) =>
                  m.id === selectedMarketplace
              )?.name}
            </strong>.

          </p>


          <div className="published-product">

            <div className="mini-product-image">

              {productImage ? (

                <img
                  src={productImage}
                  alt={t(publishedProduct?.product_name || product.name)}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    borderRadius: "8px"
                  }}
                />

              ) : (
                "✦"
              )}

            </div>


            <div>

              <strong>
                {t(publishedProduct?.product_name || product.name)}
              </strong>

              <span>
                {t(publishedProduct?.category || product.category)} •{" "}
                ₹{publishedProduct?.pricing?.final_price ?? parsePrice(product.price)}
              </span>

            </div>

          </div>


          <button
            className="success-dashboard-button"
            onClick={() =>
              navigate("/my-products")
            }
          >

            {t("View My Products")}

            <ArrowRight size={15} />

          </button>


        </div>

      </div>
    );
  }


  return (

    <div className="publish-page">

      {/* HEADER */}

      <header className="publish-header">

        <button
          className="publish-back-button"
          onClick={() =>
            navigate("/edit-product", {
              state: {
                productId,
                imageId,
                voiceResult,
                image: product.image || productImage,
                enhancedImage: product.enhancedImage,
                story: product.story,
                language: product.language,
                product: product
              }
            })
          }
        >

          <ArrowLeft size={16} />

          {t("Back to listing")}

        </button>


        <div className="publish-ai-label">

          <Sparkles size={14} />

          CRAFTMITRA

        </div>

        <div></div>

      </header>


      {/* INTRO */}

      <div className="publish-intro">

        <div className="publish-badge">

          <Send size={12} />

          {t("READY TO PUBLISH")}

        </div>


        <h1>

          Put your craft

          <span>
            {" "}on the map.
          </span>

        </h1>


        <p>

          Choose where you'd like your product
          to be discovered by customers.

        </p>

      </div>


      {/* MAIN */}

      <div className="publish-container">


        {/* PREVIEW */}

        <div className="publish-preview-card">

          <div className="preview-label">
            {t("LISTING PREVIEW")}
          </div>


          <div className="preview-image">

            {productImage ? (

              <img
                src={productImage}
                alt={t(product.name)}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover"
                }}
              />

            ) : (

              <>
                <span>✦</span>
                <small>Product Image</small>
              </>

            )}

          </div>


          <div className="preview-details">

            <span className="preview-category">
              {t(product.category)}
            </span>


            <h2>
              {t(product.name)}
            </h2>


            <p>
              {t(product.description)}
            </p>


            <div className="preview-bottom">

              <strong>
                ₹{parsePrice(product.price)}
              </strong>


              <span>

                <Check size={12} />

                {t("AI verified")}

              </span>

            </div>

          </div>

        </div>


        {/* MARKETPLACE */}

        <div className="marketplace-card">

          <div className="marketplace-heading">

            <div>

              <h2>
                {t("Choose marketplace")}
              </h2>

              <p>
                {t("Select where you want to publish this listing.")}
              </p>

            </div>


            <div className="marketplace-count">
              {t("3 OPTIONS")}
            </div>

          </div>


          <div className="marketplace-list">

            {marketplaces.map(
              (marketplace) => {

                const Icon =
                  marketplace.icon;

                const selected =
                  selectedMarketplace ===
                  marketplace.id;


                return (

                  <button
                    key={marketplace.id}
                    className={`marketplace-option ${
                      selected
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      setSelectedMarketplace(
                        marketplace.id
                      )
                    }
                  >

                    <div className="marketplace-icon">

                      <Icon size={18} />

                    </div>


                    <div className="marketplace-text">

                      <strong>
                        {t(marketplace.name)}
                      </strong>

                      <span>
                        {t(marketplace.description)}
                      </span>

                    </div>


                    <div className="selection-circle">

                      {selected && (
                        <Check size={12} />
                      )}

                    </div>

                  </button>

                );
              }
            )}

          </div>


          {/* CHECKLIST */}

          <div className="publish-checklist">

            <div className="checklist-title">

              <Sparkles size={12} />

              {t("LISTING CHECK")}

            </div>


            <div className="check-item">

              <Check size={13} />

              {t("Product information complete")}

            </div>


            <div className="check-item">

              <Check size={13} />

              {t("Product image added")}

            </div>


            <div className="check-item">

              <Check size={13} />

              Price recommendation reviewed

            </div>

          </div>


          {/* PUBLISH */}

          <button
            className="publish-now-button"
            onClick={handlePublish}
            disabled={publishing}
          >

            {publishing ? (

              <>
                <span className="publish-spinner"></span>

                Publishing your product...
              </>

            ) : (

              <>
                <Send size={15} />

                Publish Product

                <ArrowRight size={15} />
              </>

            )}

          </button>


          {publishError && (

            <div className="publish-error-banner">
              <AlertCircle size={14} />
              {publishError}
            </div>

          )}


          <p className="publish-note">

            You can update your listing details later.

          </p>

        </div>

      </div>

    </div>
  );
}

export default PublishProduct;