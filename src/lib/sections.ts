interface Section {
  id: string;
  num: string;
  key: string;
  en: string;
  ml: string;
  /** Standalone page for this section, if one exists. Falls back to a homepage anchor. */
  page?: string;
}

export const sections: Section[] = [
  { id: "history", num: "01", key: "rice", en: "History", ml: "ചരിത്രം", page: "/history" },
  { id: "administration", num: "02", key: "turmeric", en: "Administration", ml: "ഭരണം" },
  { id: "geography", num: "03", key: "vaka", en: "Geography", ml: "ഭൂമിശാസ്ത്രം" },
  { id: "culture", num: "04", key: "kumkum", en: "Life & culture", ml: "സംസ്കാരം" },
  { id: "focus", num: "05", key: "ink3", en: "Development focus", ml: "വികസന കാഴ്ചപ്പാട്" },
];
