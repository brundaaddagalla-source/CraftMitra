import { Globe } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";
import "../styles/languageSelector.css";

export default function LanguageSelector() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="language-selector" aria-label="Language selector">
      <Globe size={15} aria-hidden="true" />
      <select value={language} onChange={(event) => setLanguage(event.target.value)}>
        <option value="en">English</option>
        <option value="te">తెలుగు</option>
      </select>
    </div>
  );
}
