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

  if (!response.ok || payload.code !== 0) {
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

export type ProductStatus = "draft" | "active" | "inactive";

export type Product = {
  id: number;
  name: string;
  price: string;
  price_cents: number;
  validity_days: 30 | 90 | 180 | 360;
  detail_markdown: string;
  status: ProductStatus;
  sort_order: number;
  created_at: string | null;
  updated_at: string | null;
};

export type ProductListParams = {
  keyword?: string;
  validity_days?: number;
  status?: ProductStatus;
  page?: number;
  page_size?: number;
};

export type ProductPayload = {
  name: string;
  price_cents: number;
  validity_days: number;
  detail_markdown?: string;
  sort_order?: number;
};

export function getProducts(params: ProductListParams = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return request<{
    items: Product[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/products${query ? `?${query}` : ""}`);
}

export function createProduct(data: ProductPayload) {
  return request<Product>("/products", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateProduct(id: number, data: ProductPayload) {
  return request<Product>(`/products/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteProduct(id: number) {
  return request<null>(`/products/${id}`, { method: "DELETE" });
}

export function publishProduct(id: number) {
  return request<Product>(`/products/${id}/publish`, { method: "POST" });
}

export function unpublishProduct(id: number) {
  return request<Product>(`/products/${id}/unpublish`, { method: "POST" });
}
