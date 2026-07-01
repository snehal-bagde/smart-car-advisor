import type { ApiResponse } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  code: string;
  details: Record<string, unknown>;

  constructor(message: string, code: string, details: Record<string, unknown>) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...options?.headers },
      ...options,
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Check your connection and try again.",
      "network_error",
      {},
    );
  }

  let body: ApiResponse<T>;
  try {
    body = await response.json();
  } catch {
    throw new ApiError("The server returned an unexpected response.", "invalid_response", {});
  }

  if (!body.success) {
    throw new ApiError(
      body.message ?? "Request failed",
      body.error?.code ?? "unknown_error",
      body.error?.details ?? {},
    );
  }

  return body.data as T;
}
