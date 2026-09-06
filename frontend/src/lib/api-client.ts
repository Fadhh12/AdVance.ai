import { API_BASE_URL, readApiError } from "@/lib/api";

export { API_BASE_URL };

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

type ApiFetchOptions = {
  token?: string;
  method?: string;
  /** JSON-serializable body, or a FormData instance when `isForm` is true. */
  body?: unknown;
  isForm?: boolean;
};

/**
 * Shared fetch wrapper for the workspace (Studio) — replaces the per-page
 * `fetch(..., { headers: { Authorization } })` duplication in the old
 * generate/editor/publish pages. Throws `ApiError` on a non-2xx response so callers
 * can `catch` once instead of checking `response.ok` everywhere.
 */
export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { token, method = "GET", body, isForm } = options;
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined && !isForm) headers["Content-Type"] = "application/json";

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: isForm ? (body as FormData) : body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new ApiError(await readApiError(response), response.status);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/** For endpoints returning a binary body (e.g. the publish QR code). */
export async function apiFetchBlob(path: string, options: { token?: string } = {}): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: options.token ? { Authorization: `Bearer ${options.token}` } : {},
  });
  if (!response.ok) {
    throw new ApiError(await readApiError(response), response.status);
  }
  return response.blob();
}
