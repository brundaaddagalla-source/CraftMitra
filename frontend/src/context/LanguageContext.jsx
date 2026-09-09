// import { createContext, useContext, useEffect, useMemo, useState } from "react";
// import { translations } from "./translations";

// const LanguageContext = createContext(null);

// function normalize(value) {
//   return String(value || "").replace(/\s+/g, " ").trim();
// }

// function translateDom(language) {
//   const dictionary = translations[language] || translations.en;
//   const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
//   const nodes = [];
//   let node;

//   while ((node = walker.nextNode())) nodes.push(node);

//   for (const textNode of nodes) {
//     const parent = textNode.parentElement;
//     if (!parent || ["SCRIPT", "STYLE", "OPTION"].includes(parent.tagName)) continue;

//     const current = normalize(textNode.nodeValue);
//     if (!current || current.startsWith("#")) continue;

//     const original = textNode.dataset?.craftMitraOriginalText || current;
//     if (textNode.dataset) textNode.dataset.craftMitraOriginalText = original;

//     const translated = dictionary[original] || original;
//     if (translated !== current && textNode.nodeValue != null) {
//       textNode.nodeValue = textNode.nodeValue.replace(current, translated);
//     }
//   }

//   document.querySelectorAll("input[placeholder], textarea[placeholder]").forEach((element) => {
//     const current = normalize(element.getAttribute("placeholder"));
//     const original = element.dataset.craftMitraOriginalPlaceholder || current;
//     element.dataset.craftMitraOriginalPlaceholder = original;
//     element.setAttribute("placeholder", dictionary[original] || original);
//   });

//   document.querySelectorAll("[aria-label], [title]").forEach((element) => {
//     for (const attribute of ["aria-label", "title"]) {
//       if (!element.hasAttribute(attribute)) continue;
//       const current = normalize(element.getAttribute(attribute));
//       const dataKey = attribute === "aria-label" ? "craftMitraOriginalAria" : "craftMitraOriginalTitle";
//       const original = element.dataset[dataKey] || current;
//       element.dataset[dataKey] = original;
//       element.setAttribute(attribute, dictionary[original] || original);
//     }
//   });
// }

// export function LanguageProvider({ children }) {
//   const [language, setLanguage] = useState(() => localStorage.getItem("app_language") || "en");

//   useEffect(() => {
//     localStorage.setItem("app_language", language);
//     document.documentElement.lang = language;
//   }, [language]);

//   const t = useMemo(() => {
//     return (key) => translations[language]?.[key] ?? translations.en[key] ?? key;
//   }, [language]);

//   // Keep translation in sync with React-rendered text, while preventing
//   // the observer from reacting to its own DOM updates.
//   useEffect(() => {
//     let translating = false;
//     let scheduled = false;

//     const runTranslation = () => {
//       if (translating) return;
//       translating = true;
//       try {
//         translateDom(language);
//       } finally {
//         translating = false;
//       }
//     };

//     const scheduleTranslation = () => {
//       if (scheduled) return;
//       scheduled = true;
//       requestAnimationFrame(() => {
//         scheduled = false;
//         runTranslation();
//       });
//     };

//     runTranslation();

//     const observer = new MutationObserver((mutations) => {
//       if (translating) return;
//       if (mutations.some((mutation) => mutation.type === "childList" || mutation.type === "characterData")) {
//         scheduleTranslation();
//       }
//     });

//     observer.observe(document.body, { childList: true, subtree: true, characterData: true });
//     return () => observer.disconnect();
//   }, [language]);

//   return (
//     <LanguageContext.Provider value={{ language, setLanguage, t }}>
//       {children}
//     </LanguageContext.Provider>
//   );
// }

// export function useLanguage() {
//   const context = useContext(LanguageContext);
//   if (!context) throw new Error("useLanguage must be used inside LanguageProvider");
//   return context;
// }

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { translations } from "./translations";

const LanguageContext = createContext(null);

function normalize(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

// Text nodes don't have `.dataset` (that's Element-only), so we can't
// stash the original English text on the node itself the way we do
// for placeholder/aria-label/title. Use a WeakMap instead — keyed by
// the actual Text node object, so it survives re-renders as long as
// the node itself isn't replaced.
const originalTextCache = new WeakMap();

function translateDom(language) {
  const dictionary = translations[language] || translations.en;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  let node;

  while ((node = walker.nextNode())) nodes.push(node);

  for (const textNode of nodes) {
    const parent = textNode.parentElement;
    if (!parent || ["SCRIPT", "STYLE", "OPTION"].includes(parent.tagName)) continue;

    const current = normalize(textNode.nodeValue);
    if (!current || current.startsWith("#")) continue;

    let original = originalTextCache.get(textNode);
    if (!original) {
      original = current;
      originalTextCache.set(textNode, original);
    }

    const translated = dictionary[original] || original;
    if (translated !== current && textNode.nodeValue != null) {
      textNode.nodeValue = textNode.nodeValue.replace(current, translated);
    }
  }

  document.querySelectorAll("input[placeholder], textarea[placeholder]").forEach((element) => {
    const current = normalize(element.getAttribute("placeholder"));
    const original = element.dataset.craftMitraOriginalPlaceholder || current;
    element.dataset.craftMitraOriginalPlaceholder = original;
    element.setAttribute("placeholder", dictionary[original] || original);
  });

  document.querySelectorAll("[aria-label], [title]").forEach((element) => {
    for (const attribute of ["aria-label", "title"]) {
      if (!element.hasAttribute(attribute)) continue;
      const current = normalize(element.getAttribute(attribute));
      const dataKey = attribute === "aria-label" ? "craftMitraOriginalAria" : "craftMitraOriginalTitle";
      const original = element.dataset[dataKey] || current;
      element.dataset[dataKey] = original;
      element.setAttribute(attribute, dictionary[original] || original);
    }
  });
}

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => localStorage.getItem("app_language") || "en");

  useEffect(() => {
    localStorage.setItem("app_language", language);
    document.documentElement.lang = language;
  }, [language]);

  const t = useMemo(() => {
    return (key) => translations[language]?.[key] ?? translations.en[key] ?? key;
  }, [language]);

  useEffect(() => {
    let translating = false;
    let scheduled = false;

    const runTranslation = () => {
      if (translating) return;
      translating = true;
      try {
        translateDom(language);
      } finally {
        translating = false;
      }
    };

    const scheduleTranslation = () => {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(() => {
        scheduled = false;
        runTranslation();
      });
    };

    runTranslation();

    const observer = new MutationObserver((mutations) => {
      if (translating) return;
      if (mutations.some((mutation) => mutation.type === "childList" || mutation.type === "characterData")) {
        scheduleTranslation();
      }
    });

    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    return () => observer.disconnect();
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used inside LanguageProvider");
  return context;
}