import { clearSession, getAccessToken } from "./auth";

type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};

export type UploadResult = {
  object_key: string;
  url: string;
  file_name: string;
  mime_type: string;
  size: number;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5002/api";

function redirectToLogin() {
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.replace("/login");
  }
}

export async function uploadFile(file: File, bizType: string) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("biz_type", bizType);

  const headers = new Headers();
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}/uploads`, {
    method: "POST",
    headers,
    body: formData,
  });
  const payload = (await response.json()) as ApiResponse<UploadResult>;

  if (!response.ok || payload.code !== 0) {
    if (response.status === 401) {
      clearSession();
      redirectToLogin();
    }
    throw new Error(payload.message || "上传失败");
  }

  return payload.data;
}
