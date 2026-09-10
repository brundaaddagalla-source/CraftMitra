import {
  Plus,
  Package,
  Eye,
  Edit3,
  Trash2,
  CheckCircle,
  IndianRupee,
  Loader2,
  AlertCircle,
} from "lucide-react";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import "../styles/myProducts.css";

// Turns the nested API shape (Step 11's ProductResponse) into the flat
// shape the rest of these pages (ProductCatalog, EditProduct) already
// expect from `location.state.product`.
function toDisplayProduct(apiProduct) {
  const descriptions = apiProduct.descriptions || {};

  const price =
    apiProduct.pricing?.final_price ??
    apiProduct.pricing?.suggested_price ??
    null;

  return {
    id: apiProduct.id,
    name: apiProduct.product_name,
    category: apiProduct.category,
    description: apiProduct.description,
    descriptions: {
      regional: descriptions.regional || "",
      english: descriptions.english || "",
      hindi: descriptions.hindi || "",
    },
    regionalLanguageLabel: descriptions.regional_language_label || "",
    material: apiProduct.craft_details?.material || "",
    technique: apiProduct.craft_details?.craft_technique || "",
    color: apiProduct.craft_details?.color || "",
    tags: [],
    price: price != null ? `₹${price}` : "₹0",
    confidence:
      apiProduct.ai?.confidence != null
        ? Math.round(apiProduct.ai.confidence * 100)
        : null,
    image: apiProduct.image_url || null,
    enhancedImage: apiProduct.enhanced_image_url || null,
    language: apiProduct.original_language || "",
    status: apiProduct.status,
  };
}

function MyProducts() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const { user } = useAuth();

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  // =====================================================
  // LOAD PUBLISHED PRODUCTS FROM THE BACKEND
  // =====================================================

  const loadProducts = async () => {
    if (!user?.artisanId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setLoadError("");

    try {
      const results = await api.get(
        `/products/artisan/${user.artisanId}`
      );

      // Drafts abandoned mid-flow (photo taken but never confirmed on
      // the Publish screen) shouldn't clutter "My Products" - this
      // page is about what's actually live, per Step 11.
      const publishedOnly = (results || []).filter(
        (item) => item.status === "published"
      );

      setProducts(publishedOnly.map(toDisplayProduct));
    } catch (error) {
      console.error(error);
      setLoadError(
        error.message || t("Couldn't load your products. Please try again.")
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.artisanId]);

  // =====================================================
  // DELETE PRODUCT
  // =====================================================

  const deleteProduct = async (id) => {
    setDeletingId(id);

    try {
      await api.delete(`/products/${id}`);
      setProducts((prev) => prev.filter((product) => product.id !== id));
    } catch (error) {
      console.error(error);
      alert(
        error.message || t("Couldn't delete this product. Please try again.")
      );
    } finally {
      setDeletingId(null);
    }
  };

  // =====================================================
  // VIEW PRODUCT
  // =====================================================

  const viewProduct = (product) => {
    navigate("/product-catalog", {
      state: {
        image: product.enhancedImage || product.image,
        story: product.story || "",
        product: product,
      },
    });
  };

  // =====================================================
  // EDIT PRODUCT
  // =====================================================

  const editProduct = (product) => {
    navigate("/edit-product", {
      state: {
        productId: product.id,
        image: product.image,
        enhancedImage: product.enhancedImage,
        story: product.story || "",
        language: product.language,
        product: product,
      },
    });
  };

  // =====================================================
  // ADD PRODUCT
  // =====================================================

  const addProduct = () => {
    navigate("/add-product");
  };

  return (
  <div className="my-products-layout">

    {/* ================= SIDEBAR ================= */}
    {/* ================= MAIN CONTENT ================= */}

    <main className="my-products-content">

      <div className="my-products-page">

        {/* HEADER */}

        <header className="my-products-header">

          <div></div>

          <div className="my-products-title">
            <Package size={17} />
            {t("My Products")} 
          </div>

          <button
            className="add-product-button"
            onClick={addProduct}
          >
            <Plus size={15} />
            {t("Add Product")}
          </button>

        </header>


        {/* INTRO */}

        <div className="my-products-intro">

          <div className="products-badge">
            {t("YOUR CRAFTS")}
          </div>

          <h1>
            {t("My Products")}
          </h1>

          <p>
            {t("Manage the products you've created and published through CraftMitra.")}
          </p>

        </div>


        {/* PRODUCTS */}

        <div className="products-container">

          {loading ? (

            <div className="empty-products">

              <div className="empty-icon">
                <Loader2 size={28} className="spin" />
              </div>

              <h2>{t("Loading your products...")}</h2>

            </div>

          ) : loadError ? (

            <div className="empty-products">

              <div className="empty-icon">
                <AlertCircle size={28} />
              </div>

              <h2>{t("Something went wrong")}</h2>

              <p>{loadError}</p>

              <button onClick={loadProducts}>
                {t("Try Again")}
              </button>

            </div>

          ) : products.length === 0 ? (

            <div className="empty-products">

              <div className="empty-icon">
                <Package size={28} />
              </div>

              <h2>{t("No products yet")}</h2>

              <p>
                {t("Your published products will appear here.")}
              </p>

              <button onClick={addProduct}>
                <Plus size={15} />
                {t("Add Your First Product")}
              </button>

            </div>

          ) : (

            <div className="products-grid">

              {products.map((product) => (

                <div
                  className="product-card"
                  key={product.id}
                >

                  {/* IMAGE */}

                  <div className="my-product-image">

                    {product.enhancedImage || product.image ? (

                      <img
                        src={product.enhancedImage || product.image}
                        alt={t(product.name || "Product")}
                      />

                    ) : (

                      <div className="product-placeholder">
                        ✦
                      </div>

                    )}

                    <span className="published-badge">

                      <CheckCircle size={11} />

                      {t("Published")}

                    </span>

                  </div>


                  {/* DETAILS */}

                  <div className="my-product-details">

                    <span className="product-category">
                      {t(product.category || "Handicraft")}
                    </span>

                    <h2>
                      {t(product.name || "Untitled Product")}
                    </h2>

                    <p>
                      {t(product.description ||
                        "No description available.")}
                    </p>


                    {/* PRICE */}

                    <div className="product-price">

                      <span>

                        <IndianRupee size={15} />

                        {String(
                          product.price || "0"
                        ).replace("₹", "")}

                      </span>

                      <small>
                        {t(product.material || "")}
                      </small>

                    </div>


                    {/* ACTIONS */}

                    <div className="product-actions">

                      {/* VIEW */}

                      <button
                        onClick={() =>
                          viewProduct(product)
                        }
                      >
                        <Eye size={14} />
                        {t("View")}
                      </button>


                      {/* EDIT */}

                      <button
                        onClick={() =>
                          editProduct(product)
                        }
                      >
                        <Edit3 size={14} />
                        {t("Edit")}
                      </button>


                      {/* DELETE */}

                      <button
                        className="delete-product"
                        onClick={() =>
                          deleteProduct(product.id)
                        }
                        disabled={deletingId === product.id}
                      >
                        <Trash2 size={14} />
                      </button>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          )}

        </div>

      </div>

    </main>

  </div>
);
}

export default MyProducts;