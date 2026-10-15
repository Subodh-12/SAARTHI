// Canonical Bloom's Taxonomy definitions and helpers for SAARTHI frontend.
// Parity with backend/app/domain/bloom.py.

export type BloomLevel = "remember" | "understand" | "apply" | "analyze" | "evaluate" | "create";

export const BLOOM_ORDER: BloomLevel[] = [
  "remember",
  "understand",
  "apply",
  "analyze",
  "evaluate",
  "create",
];

export const BLOOM_LEVEL_INDEX: Record<BloomLevel, number> = {
  remember: 0,
  understand: 1,
  apply: 2,
  analyze: 3,
  evaluate: 4,
  create: 5,
};

export const BLOOM_LABELS_OR: Record<BloomLevel, string> = {
  remember: "ମନେରଖିବା",
  understand: "ବୁଝିବା",
  apply: "ପ୍ରୟୋଗ",
  analyze: "ବିଶ୍ଳେଷଣ",
  evaluate: "ମୂଲ୍ୟାଙ୍କନ",
  create: "ନିର୍ମାଣ",
};

export const BLOOM_LABELS_EN: Record<BloomLevel, string> = {
  remember: "Remember",
  understand: "Understand",
  apply: "Apply",
  analyze: "Analyze",
  evaluate: "Evaluate",
  create: "Create",
};

export const BLOOM_DESCRIPTIONS_OR: Record<BloomLevel, string> = {
  remember: "ତଥ୍ୟ, ସଂଜ୍ଞା ଓ ସୂତ୍ର ମନେପକାଅ",
  understand: "ଧାରଣା ବୁଝ ଓ ନିଜ ଭାଷାରେ ବ୍ୟାଖ୍ୟା କର",
  apply: "ନୂତନ ପରିସ୍ଥିତିରେ ନିୟମ ଓ ସୂତ୍ର ପ୍ରୟୋଗ କର",
  analyze: "ଅଂଶଗୁଡ଼ିକ ତୁଳନା କର ଓ ସମ୍ପର୍କ ଚିହ୍ନଟ କର",
  evaluate: "ପ୍ରମାଣ ଆଧାରରେ ଯୁକ୍ତି ଓ ସିଦ୍ଧାନ୍ତର ବିଚାର କର",
  create: "ନୂତନ ସମାଧାନ, ମଡେଲ ବା ପରିକଳ୍ପନା ତିଆରି କର",
};

export const BLOOM_DESCRIPTIONS_EN: Record<BloomLevel, string> = {
  remember: "Recall facts, definitions, terminology, and formulas",
  understand: "Explain ideas, interpret information, or classify examples",
  apply: "Use rules or formulas to solve problems in new situations",
  analyze: "Distinguish components, compare evidence, and diagnose errors",
  evaluate: "Assess claims, compare approaches, and justify judgments",
  create: "Develop an original solution, model, or explanation",
};

export function isValidBloomLevel(val: any): val is BloomLevel {
  return typeof val === "string" && val.toLowerCase() in BLOOM_LEVEL_INDEX;
}

export function parseBloomLevel(val: any): BloomLevel {
  if (typeof val === "string") {
    const clean = val.toLowerCase().trim() as BloomLevel;
    if (clean in BLOOM_LEVEL_INDEX) return clean;
  }
  throw new Error(`Invalid Bloom level: ${val}`);
}

export function bloomComplexity(level: BloomLevel): number {
  return BLOOM_LEVEL_INDEX[level] ?? 0;
}

export function compareBloom(a: BloomLevel, b: BloomLevel): number {
  const ca = bloomComplexity(a);
  const cb = bloomComplexity(b);
  return ca < cb ? -1 : ca > cb ? 1 : 0;
}

export function nextHigherLevel(level: BloomLevel): BloomLevel | null {
  const idx = bloomComplexity(level);
  if (idx + 1 < BLOOM_ORDER.length) return BLOOM_ORDER[idx + 1];
  return null;
}

export function nextLowerLevel(level: BloomLevel): BloomLevel | null {
  const idx = bloomComplexity(level);
  if (idx > 0) return BLOOM_ORDER[idx - 1];
  return null;
}

export function bloomLabel(level: BloomLevel, lang: "or" | "en" = "or"): string {
  return lang === "en" ? BLOOM_LABELS_EN[level] : BLOOM_LABELS_OR[level];
}

export function bloomDescription(level: BloomLevel, lang: "or" | "en" = "or"): string {
  return lang === "en" ? BLOOM_DESCRIPTIONS_EN[level] : BLOOM_DESCRIPTIONS_OR[level];
}
