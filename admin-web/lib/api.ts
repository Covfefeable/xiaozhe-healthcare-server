import { clearSession, getAccessToken, type AdminUser, type LoginResult } from "./auth";

type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5002/api";

async function request<T>(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");

  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });
  const payload = (await response.json()) as ApiResponse<T>;

  if (!response.ok) {
    if (response.status === 401) {
      clearSession();
    }
    throw new Error(payload.message || "请求失败");
  }

  return payload.data;
}

export function getAuthConfig() {
  return request<{ allow_register: boolean }>("/auth/config");
}

export function login(data: { username: string; password: string }) {
  return request<LoginResult>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function register(data: {
  username: string;
  password: string;
  display_name: string;
  email?: string;
  phone?: string;
}) {
  return request<AdminUser>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getMe() {
  return request<AdminUser>("/auth/me");
}

export function logout() {
  return request<null>("/auth/logout", { method: "POST" });
}

