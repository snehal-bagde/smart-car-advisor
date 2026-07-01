export type ApiResponse<T> = {
  success: boolean;
  message: string | null;
  data: T | null;
  error: { code: string; details: Record<string, unknown> } | null;
};
