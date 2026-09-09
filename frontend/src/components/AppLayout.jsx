import { Plus, Package, ShoppingBag } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import LanguageSelector from "./LanguageSelector";
import "../styles/appLayout.css";

export default function AppLayout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();

  const items = [
    { path: "/my-products", icon: Package, label: "My Products" },
    { path: "/add-product", icon: Plus, label: "Add Product" },
    { path: "/orders", icon: ShoppingBag, label: "Orders" },
  ];

  const isActive = (item) =>
    item.path === "/my-products"
      ? location.pathname === "/" || location.pathname === "/my-products"
      : location.pathname === item.path;

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="app-brand">
          <div className="app-brand-mark">✦</div>
          <div>
            <h2>CraftMitra</h2>
            <span>{t("Virtual Artisan Manager")}</span>
          </div>
        </div>

        <nav className="app-sidebar-nav" aria-label={t("MENU")}>
          <p className="app-nav-label">{t("MENU")}</p>
          {items.map(({ path, icon: Icon, label }) => (
            <button
              key={path}
              type="button"
              className={`app-nav-item ${isActive({ path }) ? "active" : ""}`}
              onClick={() => navigate(path === "/my-products" ? "/my-products" : path)}
            >
              <Icon size={19} />
              <span>{t(label)}</span>
            </button>
          ))}
        </nav>
      </aside>

      <div className="app-shell-main">
        <LanguageSelector />
        {children}
      </div>
    </div>
  );
}
