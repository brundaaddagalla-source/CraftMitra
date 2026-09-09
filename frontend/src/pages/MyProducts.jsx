import {
  Plus,
  Package,
  Eye,
  Edit3,
  Trash2,
  CheckCircle,
  IndianRupee,
  ShoppingBag,
} from "lucide-react";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import "../styles/myProducts.css";

function MyProducts() {
  const navigate = useNavigate();
  const { t } = useLanguage();

  const [products, setProducts] = useState([]);

  // =====================================================
  // LOAD ALL PUBLISHED PRODUCTS
  // =====================================================

  useEffect(() => {
    const savedProducts =
      JSON.parse(localStorage.getItem("myProducts")) || [];

    setProducts(savedProducts);
  }, []);

  // =====================================================
  // DELETE PRODUCT
  // =====================================================

  const deleteProduct = (id) => {
    const updatedProducts = products.filter(
      (product) => product.id !== id
    );

    setProducts(updatedProducts);

    localStorage.setItem(
      "myProducts",
      JSON.stringify(updatedProducts)
    );
  };

  // =====================================================
  // VIEW PRODUCT
  // =====================================================

  const viewProduct = (product) => {
    navigate("/product-catalog", {
      state: {
        image: product.image,
        story: product.story || "",
        product: product
      }
    });
  };

  // =====================================================
  // EDIT PRODUCT
  // =====================================================

  const editProduct = (product) => {
    navigate("/edit-product", {
      state: {
        image: product.image,
        story: product.story || "",
        product: product
      }
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

          {products.length === 0 ? (

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

                    {product.image ? (

                      <img
                        src={product.image}
                        alt={t(product.name || "Product")}
                      />

                    ) : (

                      <div className="product-placeholder">
                        ✦
                      </div>

                    )}

                    <span className="published-badge">

                      <CheckCircle size={11} />

                      {t(product.status || "Published")}

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
