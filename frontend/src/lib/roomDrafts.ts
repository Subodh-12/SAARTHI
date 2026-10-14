export type RoomDrafts = {
  title?: string;
  topic?: string;
  msg?: string;
  answer?: string;
  line?: string;
  why?: string;
  join?: string;
  histQ?: string;
  reply?: string;
  chapter?: string;
  language?: string;
  cap?: number;
  vopt?: number;
};

export function syncRoomDraftField(drafts: RoomDrafts, id: string, value: string): RoomDrafts {
  switch (id) {
    case "rTitle":
      drafts.title = value;
      break;
    case "rTopic":
      drafts.topic = value;
      break;
    case "rMsg":
      drafts.msg = value;
      break;
    case "rAnswer":
      drafts.answer = value;
      break;
    case "rLine":
      drafts.line = value;
      break;
    case "rWhy":
      drafts.why = value;
      break;
    case "rJoinCode":
      drafts.join = value;
      break;
    case "rHistQ":
      drafts.histQ = value;
      break;
    case "rChapter":
      drafts.chapter = value;
      break;
    case "rLanguage":
      drafts.language = value;
      break;
    case "rCap":
      drafts.cap = Number(value);
      break;
    case "rVopt":
      drafts.vopt = Number(value);
      break;
    default:
      break;
  }

  return drafts;
}

export function getDraftValue(drafts: RoomDrafts, id: string, fallback = ""): string {
  switch (id) {
    case "rTitle":
      return drafts.title ?? fallback;
    case "rTopic":
      return drafts.topic ?? fallback;
    case "rMsg":
      return drafts.msg ?? fallback;
    case "rAnswer":
      return drafts.answer ?? fallback;
    case "rLine":
      return drafts.line ?? fallback;
    case "rWhy":
      return drafts.why ?? fallback;
    case "rJoinCode":
      return drafts.join ?? fallback;
    case "rHistQ":
      return drafts.histQ ?? fallback;
    case "rChapter":
      return drafts.chapter ?? fallback;
    case "rLanguage":
      return drafts.language ?? fallback;
    default:
      return fallback;
  }
}
