export interface ChapterItem {
  id: string;
  t: { en: string; or: string };
}

export interface ConceptItem {
  id: string;
  ch: string;
  pre: string[];
  t: { en: string; or: string };
  s: string[];
  ex: string;
  src: string;
}

export const CHAPTERS: ChapterItem[];
export const CONCEPTS: ConceptItem[];
export const PACK: any;
export const QB: any;
export const GL: any;
export const CHUNKS: any;
