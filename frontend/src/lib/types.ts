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
