import { useState } from "react";

import {
  ArrowLeft,
  ArrowRight,
  Check,
  Sparkles,
  Store,
  ShoppingBag,
  Globe,
  Send
} from "lucide-react";

import {
  useNavigate,
  useLocation
} from "react-router-dom";

import "../styles/publishProduct.css";
import { useLanguage } from "../context/LanguageContext";

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

function PublishProduct() {

  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();

  const [selectedMarketplace, setSelectedMarketplace] =
    useState("craftmitra");

  const [publishing, setPublishing] =
    useState(false);

  const [published, setPublished] =
    useState(false);


  // Get actual product from Product Catalog
  const product =
    location.state?.product || {
      name: "Handwoven Cotton Saree",
      category: "Handloom",
      material: "Cotton",
      technique: "Traditional Hand Weaving",
      color: "Indigo",
      description:
        "A beautiful handcrafted product created by an artisan.",
      price: "₹2,599",
      tags: [
        "Handloom",
        "Handcrafted"
      ],
      confidence: 94
    };


  const productImage =
    location.state?.image;


  const handlePublish = () => {

    setPublishing(true);

    setTimeout(() => {

      const existingProducts =
        JSON.parse(
          localStorage.getItem("myProducts")
        ) || [];


      const newProduct = {

        ...product,

        id: Date.now(),

        image: productImage || "",

        status: "Published",

        marketplace: selectedMarketplace,

        publishedAt:
          new Date().toISOString()

      };


      const updatedProducts = [
        ...existingProducts,
        newProduct
      ];


      localStorage.setItem(
        "myProducts",
        JSON.stringify(updatedProducts)
      );


      setPublishing(false);

      setPublished(true);

    }, 1500);
  };


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
                  alt={t(product.name)}
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
                {t(product.name)}
              </strong>

              <span>
                {t(product.category)} • {product.price}
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
            navigate("/product-catalog", {
              state: {
                image: productImage,
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
                {product.price}
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


          <p className="publish-note">

            You can update your listing details later.

          </p>

        </div>

      </div>

    </div>
  );
}

export default PublishProduct;