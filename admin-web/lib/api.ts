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
  summary: string;
  price: string;
  price_cents: number;
  validity_days: 30 | 90 | 180 | 360;
  image_url: string;
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
  summary?: string;
  price_cents: number;
  validity_days: number;
  image_url?: string;
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

export type NewsItem = {
  id: number;
  cover_image_url: string;
  title: string;
  published_at: string | null;
  content_markdown: string;
  created_at: string | null;
  updated_at: string | null;
};

export type NewsListParams = {
  keyword?: string;
  page?: number;
  page_size?: number;
};

export type NewsPayload = {
  cover_image_url?: string;
  title: string;
  published_at: string;
  content_markdown?: string;
};

export function getNewsList(params: NewsListParams = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return request<{
    items: NewsItem[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/news${query ? `?${query}` : ""}`);
}

export function createNews(data: NewsPayload) {
  return request<NewsItem>("/news", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateNews(id: number, data: NewsPayload) {
  return request<NewsItem>(`/news/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteNews(id: number) {
  return request<null>(`/news/${id}`, { method: "DELETE" });
}

export type BannerItem = {
  id: number;
  image_url: string;
  title: string;
  description: string;
  created_at: string | null;
  updated_at: string | null;
};

export type BannerListParams = {
  keyword?: string;
  page?: number;
  page_size?: number;
};

export type BannerPayload = {
  image_url?: string;
  title: string;
  description?: string;
};

export function getBannerList(params: BannerListParams = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return request<{
    items: BannerItem[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/banners${query ? `?${query}` : ""}`);
}

export function createBanner(data: BannerPayload) {
  return request<BannerItem>("/banners", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateBanner(id: number, data: BannerPayload) {
  return request<BannerItem>(`/banners/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteBanner(id: number) {
  return request<null>(`/banners/${id}`, { method: "DELETE" });
}

export type DepartmentItem = {
  id: number;
  name: string;
  description: string;
  sort_order: number;
  created_at: string | null;
  updated_at: string | null;
};

export type DepartmentPayload = {
  name: string;
  description?: string;
  sort_order?: number;
};

export type DepartmentListParams = {
  keyword?: string;
  page?: number;
  page_size?: number;
};

export function getDepartmentList(params: DepartmentListParams = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return request<{
    items: DepartmentItem[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/departments${query ? `?${query}` : ""}`);
}

export function createDepartment(data: DepartmentPayload) {
  return request<DepartmentItem>("/departments", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateDepartment(id: number, data: DepartmentPayload) {
  return request<DepartmentItem>(`/departments/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteDepartment(id: number) {
  return request<null>(`/departments/${id}`, { method: "DELETE" });
}

export type DoctorItem = {
  id: number;
  department_id: number;
  department_name: string;
  avatar_url: string;
  name: string;
  phone: string;
  title: string;
  hospital: string;
  summary: string;
  specialty_tags: string[];
  introduction: string;
  sort_order: number;
  created_at: string | null;
  updated_at: string | null;
};

export type DoctorPayload = {
  department_id: number;
  avatar_url?: string;
  name: string;
  phone: string;
  title?: string;
  hospital?: string;
  summary?: string;
  specialty_tags?: string[];
  introduction?: string;
  sort_order?: number;
};

export type DoctorListParams = {
  keyword?: string;
  department_id?: number;
  page?: number;
  page_size?: number;
};

export function getDoctorList(params: DoctorListParams = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return request<{
    items: DoctorItem[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/doctors${query ? `?${query}` : ""}`);
}

export function createDoctor(data: DoctorPayload) {
  return request<DoctorItem>("/doctors", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateDoctor(id: number, data: DoctorPayload) {
  return request<DoctorItem>(`/doctors/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteDoctor(id: number) {
  return request<null>(`/doctors/${id}`, { method: "DELETE" });
}

export type StaffStatus = "active" | "inactive";

export type StaffItem = {
  id: number;
  avatar_url: string;
  name: string;
  phone: string;
  status: StaffStatus;
  remark: string;
  created_at: string | null;
  updated_at: string | null;
};

export type StaffPayload = {
  avatar_url?: string;
  name: string;
  phone: string;
  status: StaffStatus;
  remark?: string;
};

export type StaffListParams = {
  keyword?: string;
  status?: StaffStatus;
  page?: number;
  page_size?: number;
};

function buildQuery(params: Record<string, string | number | undefined>) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

function getStaffList(path: string, params: StaffListParams = {}) {
  return request<{
    items: StaffItem[];
    pagination: { page: number; page_size: number; total: number };
  }>(`${path}${buildQuery(params)}`);
}

function createStaff(path: string, data: StaffPayload) {
  return request<StaffItem>(path, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

function updateStaff(path: string, id: number, data: StaffPayload) {
  return request<StaffItem>(`${path}/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

function deleteStaff(path: string, id: number) {
  return request<null>(`${path}/${id}`, { method: "DELETE" });
}

export function getAssistantList(params: StaffListParams = {}) {
  return getStaffList("/assistants", params);
}

export function createAssistant(data: StaffPayload) {
  return createStaff("/assistants", data);
}

export function updateAssistant(id: number, data: StaffPayload) {
  return updateStaff("/assistants", id, data);
}

export function deleteAssistant(id: number) {
  return deleteStaff("/assistants", id);
}

export function getCustomerServiceList(params: StaffListParams = {}) {
  return getStaffList("/customer-services", params);
}

export function createCustomerService(data: StaffPayload) {
  return createStaff("/customer-services", data);
}

export function updateCustomerService(id: number, data: StaffPayload) {
  return updateStaff("/customer-services", id, data);
}

export function deleteCustomerService(id: number) {
  return deleteStaff("/customer-services", id);
}
