export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {}

/** Extracts FastAPI's `{"detail": "..."}` error shape into a plain message. */
export async function readApiError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
  } catch {
    // response body wasn't JSON — fall through to generic message
  }
  return "Terjadi kesalahan. Coba lagi.";
}
