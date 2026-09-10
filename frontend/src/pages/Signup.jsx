import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import "../styles/signup.css";

const LANGUAGE_NAMES = { en: "English", te: "Telugu", hi: "Hindi" };

function Signup() {
  const navigate = useNavigate();
  const { signup, loading } = useAuth();
  const { language: uiLanguage, t } = useLanguage();

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    location: "",
    district: "",
    state: "",
    craftType: "",
  });

  const [error, setError] = useState("");

  const updateField = (field) => (event) => {
    setForm((previous) => ({ ...previous, [field]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    try {
      await signup({
        ...form,
        preferredLanguage: LANGUAGE_NAMES[uiLanguage] || "English",
      });

      navigate("/");
    } catch (submitError) {
      setError(
        submitError.message || t("Something went wrong. Please try again.")
      );
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-card">
        <div className="signup-brand">
          <div className="signup-brand-mark">
            <Sparkles size={20} />
          </div>
          <h1>CraftMitra</h1>
        </div>

        <p className="signup-subtitle">
          {t("Create your artisan account to start listing your craft.")}
        </p>

        <form className="signup-form" onSubmit={handleSubmit}>
          <label>
            {t("Your name")}
            <input
              type="text"
              value={form.name}
              onChange={updateField("name")}
              required
              minLength={2}
              placeholder={t("e.g. Lakshmi Devi")}
            />
          </label>

          <label>
            {t("Email")}
            <input
              type="email"
              value={form.email}
              onChange={updateField("email")}
              required
              placeholder="you@example.com"
            />
          </label>

          <label>
            {t("Phone number")}
            <input
              type="tel"
              value={form.phone}
              onChange={updateField("phone")}
              required
              minLength={5}
              placeholder="9876543210"
            />
          </label>

          <label>
            {t("Password")}
            <input
              type="password"
              value={form.password}
              onChange={updateField("password")}
              required
              minLength={6}
              placeholder={t("At least 6 characters")}
            />
          </label>

          <label>
            {t("Village / Town")}
            <input
              type="text"
              value={form.location}
              onChange={updateField("location")}
              required
              placeholder={t("e.g. Mangalagiri")}
            />
          </label>

          <label>
            {t("District")}
            <input
              type="text"
              value={form.district}
              onChange={updateField("district")}
              required
              placeholder={t("e.g. Guntur")}
            />
          </label>

          <label>
            {t("State")}
            <input
              type="text"
              value={form.state}
              onChange={updateField("state")}
              required
              placeholder={t("e.g. Andhra Pradesh")}
            />
          </label>

          <label>
            {t("What craft do you make?")}
            <input
              type="text"
              value={form.craftType}
              onChange={updateField("craftType")}
              required
              placeholder={t("e.g. Pottery, Weaving, Woodwork")}
            />
          </label>

          {error && <p className="signup-error">{error}</p>}

          <button type="submit" className="signup-submit" disabled={loading}>
            {loading ? t("Creating your account...") : t("Get started")}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Signup;