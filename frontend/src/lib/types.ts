export type MediaAsset = {
  id: string;
  type: "photo" | "video_raw" | "audio";
  original_filename: string;
  content_type: string;
  size_bytes: number;
  uploaded_at: string;
  url: string;
};

export type AIJob = {
  id: string;
  type: string;
  status: "queued" | "processing" | "success" | "failed";
  provider: string;
  result_url: string | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type ProjectMode = "product_ad" | "affiliate";

export type Platform = "instagram" | "tiktok" | "youtube";

export type Post = {
  id: string;
  project_id: string;
  project_title: string | null;
  platform: Platform;
  export_status: "queued" | "processing" | "success" | "failed" | null;
  export_error_message: string | null;
  caption: string | null;
  youtube_title: string | null;
  video_url: string | null;
  status: "manual_ready" | "manual_uploaded" | null;
  created_at: string;
};

export type ContentProject = {
  id: string;
  title: string;
  mode: ProjectMode;
  status: "draft" | "ready" | "scheduled" | "published";
  caption: string | null;
  music_track: string | null;
  trim_start_seconds: number | null;
  trim_end_seconds: number | null;
  motion_preset: string | null;
  render_status: "queued" | "processing" | "success" | "failed" | null;
  render_error_message: string | null;
  source_video_url: string;
  final_video_url: string | null;
  created_at: string;
  updated_at: string;
};

export type Template = {
  id: string;
  name: string;
  description: string | null;
  mode: ProjectMode;
  prompt_preset: string;
  thumbnail_url: string | null;
  created_at: string;
};

// Phase 6R-8 — code-defined catalog (backend/app/services/motion_presets/registry.py),
// not per-user data, same shape as backend/app/schemas/motion_preset.py.
export type MotionPreset = {
  id: string;
  name: string;
  description: string;
  aspect_ratio: string;
  min_duration_seconds: number;
  max_duration_seconds: number;
};

// Phase 6R chat agent — see backend/app/schemas/chat.py. `tool` messages carry the raw
// result of whatever agent_tools/* function ran (shape varies per tool_name), which is
// why tool_result stays a loosely-typed record rather than a tool-specific union here.
export type ChatRole = "user" | "assistant" | "tool";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  tool_name: string | null;
  tool_result: Record<string, unknown> | null;
  created_at: string;
};

export type ChatTurn = {
  conversation_id: string;
  messages: ChatMessage[];
};
