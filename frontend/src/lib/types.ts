export type MediaAsset = {
  id: string;
  type: "photo" | "video_raw";
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

export type ContentProject = {
  id: string;
  title: string;
  mode: ProjectMode;
  status: "draft" | "ready" | "scheduled" | "published";
  caption: string | null;
  music_track: string | null;
  trim_start_seconds: number | null;
  trim_end_seconds: number | null;
  render_status: "queued" | "processing" | "success" | "failed" | null;
  render_error_message: string | null;
  source_video_url: string;
  final_video_url: string | null;
  created_at: string;
  updated_at: string;
};
