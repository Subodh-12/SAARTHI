// Shared Karana Study Rooms types (frontend view of backend contracts).

export interface RoomMember {
  learner_id: string;
  display_label: string;
  role: "host" | "member";
  online: boolean;
}

export interface RoomSummaryView {
  room_id: string;
  room_code: string;
  title: string;
  subject: string;
  chapter_id: string;
  chapter_title: string;
  learning_topic: string;
  language: string;
  capacity: number;
  member_count: number;
  members: RoomMember[];
  is_member: boolean;
  status: string;
  created_at: number;
  last_activity_at: number;
  expires_at: number | null;
  recent_activity: string[];
}

export interface RoomMessage {
  message_id: string;
  room_id: string;
  learner_id: string | null;
  sender_label: string;
  sender_kind: "member" | "karana" | "system";
  kind: "chat" | "reply" | "system" | "summary";
  reply_to: string | null;
  body: string;
  created_at: number;
}

export interface RoomSessionSummary {
  summary_id: string;
  activity_type: string;
  original_question: string;
  explanation: string;
  verification: Record<string, unknown>;
  unresolved: string[];
  created_at: number;
}

export interface RoomDetail {
  room: RoomSummaryView;
  messages: RoomMessage[];
  summaries: RoomSessionSummary[];
}

export interface RelaySubmissionView {
  learner_id: string;
  display_label: string;
  content: string | null;
  created_at: number;
}

export interface VerificationQuestion {
  question: string;
  options: string[];
  correct_option?: number;
  group?: { total: number; correct: number };
}

export interface RelayState {
  activity_id: string;
  activity_type: "doubt_relay";
  status: "collecting" | "revealed" | "followup" | "discussion"
    | "verification" | "completed";
  question: string;
  my_submission: string | null;
  submission_count: number;
  eligible_count: number;
  submissions: RelaySubmissionView[];
  followup: { text: string } | null;
  explanation: string | null;
  pattern: string | null;
  verification: VerificationQuestion | null;
  verification_result: { correct: boolean } | null;
  trace: { step: string; detail: string }[];
  created_at: number;
  updated_at: number;
}

export interface GameState {
  activity_id: string;
  activity_type: "find_the_mistake";
  status: "collecting" | "revealed" | "followup" | "discussion"
    | "verification" | "completed";
  problem: { problem_id: string; title: string; lines: string[] } | null;
  my_submission: { mistake_line: string; reasoning: string } | null;
  submission_count: number;
  eligible_count: number;
  submissions: (RelaySubmissionView & { mistake_line?: string; reasoning?: string })[];
  expected: { mistake_index: number; answer: string; explanation: string } | null;
  followup: { text: string } | null;
  group_stats: { found: number; reasoned: number; total: number } | null;
  created_at: number;
  updated_at: number;
}
