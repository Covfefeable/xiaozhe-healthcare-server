import { clearSession, getAccessToken, type AdminUser, type LoginResult } from "./auth";

type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5002/api";

function redirectToLogin() {
  if (typeof window === "undefined") {
    return;
  }
  if (window.location.pathname !== "/login") {
    window.location.replace("/login");
  }
}

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
      if (!path.startsWith("/auth/login")) {
        redirectToLogin();
      }
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

export type DashboardData = {
  overview: {
    today_new_users: number;
    active_members: number;
    today_orders: number;
    today_paid_amount_cents: number;
    today_paid_amount: string;
  };
  todos: {
    pending_refund_orders: number;
    in_progress_orders: number;
    pending_payment_orders: number;
  };
};

export function getDashboard() {
  return request<DashboardData>("/dashboard");
}

export type ProductStatus = "draft" | "active" | "inactive";
export type ProductType = "membership" | "other";

export type Product = {
  id: number;
  name: string;
  summary: string;
  price: string;
  price_cents: number;
  validity_days: 0 | 30 | 90 | 180 | 365;
  product_type: ProductType;
  image_object_key: string;
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
  product_type?: ProductType;
  page?: number;
  page_size?: number;
};

export type ProductPayload = {
  name: string;
  summary?: string;
  price_cents: number;
  validity_days: number;
  product_type: ProductType;
  image_object_key?: string;
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
  cover_image_object_key: string;
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
  cover_image_object_key?: string;
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
  image_object_key: string;
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
  image_object_key?: string;
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
  avatar_object_key: string;
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
  avatar_object_key?: string;
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
export type AssistantType = "health_manager" | "medical_assistant";

export type StaffItem = {
  id: number;
  avatar_object_key: string;
  avatar_url: string;
  name: string;
  phone: string;
  status: StaffStatus;
  assistant_type?: AssistantType;
  remark: string;
  created_at: string | null;
  updated_at: string | null;
};

export type StaffPayload = {
  avatar_object_key?: string;
  name: string;
  phone: string;
  status: StaffStatus;
  assistant_type?: AssistantType;
  remark?: string;
};

export type StaffListParams = {
  keyword?: string;
  status?: StaffStatus;
  assistant_type?: AssistantType;
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

export type OrderStatus = "pending_payment" | "in_progress" | "completed" | "pending_refund" | "refunded";

export type AdminOrderRefund = {
  reason: string;
  description: string;
  image_urls: string[];
  requested_at: string | null;
  handled_at: string | null;
  reject_reason: string;
};

export type AdminOrder = {
  id: number;
  order_no: string;
  user_phone: string;
  service_user_name: string;
  status: OrderStatus;
  status_label: string;
  product_type: ProductType;
  product_summary: string;
  total_amount_cents: number;
  total_amount: string;
  payment_method: string;
  paid_at: string | null;
  completed_at: string | null;
  refunded_at: string | null;
  refund: AdminOrderRefund;
  created_at: string | null;
  updated_at: string | null;
  items: AdminOrderItem[];
};

export type AdminOrderItem = {
  id: number;
  product_name: string;
  product_type: ProductType;
  quantity: number;
  subtotal_cents: number;
  subtotal: string;
};

export type AdminOrderListParams = {
  keyword?: string;
  status?: OrderStatus;
  page?: number;
  page_size?: number;
};

export function getOrderList(params: AdminOrderListParams = {}) {
  return request<{
    items: AdminOrder[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/orders${buildQuery(params)}`);
}

export function getAdminOrder(id: number) {
  return request<AdminOrder>(`/orders/${id}`);
}

export function updateOrderStatus(
  id: number,
  status: "completed" | "refunded" | "in_progress",
  data: { refund_reject_reason?: string } = {},
) {
  return request<AdminOrder>(`/orders/${id}/status`, {
    method: "PUT",
    body: JSON.stringify({ status, ...data }),
  });
}

export type AdminMiniappHealthRecord = {
  id: number;
  content: string;
  image_urls: string[];
};

export type AdminMiniappUser = {
  id: number;
  openid: string;
  nickname: string;
  avatar_url: string;
  phone: string;
  real_name: string;
  display_name: string;
  gender: "male" | "female" | "unknown";
  gender_label: string;
  birthday: string;
  age: number | null;
  status: string;
  membership_status: "active" | "none";
  membership_expires_at: string;
  membership_expires_at_datetime: string | null;
  health_manager_id: number | null;
  health_manager_name: string;
  health_manager_phone: string;
  last_login_at: string | null;
  created_at: string | null;
  archive?: {
    medical_histories: AdminMiniappHealthRecord[];
    medication_records: AdminMiniappHealthRecord[];
  };
};

export type AdminMiniappUserListParams = {
  keyword?: string;
  page?: number;
  page_size?: number;
};

export function getMiniappUserList(params: AdminMiniappUserListParams = {}) {
  return request<{
    items: AdminMiniappUser[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/users${buildQuery(params)}`);
}

export function getMiniappUser(id: number) {
  return request<AdminMiniappUser>(`/users/${id}`);
}

export function renewMiniappUserMembership(id: number, membership_expires_at: string) {
  return request<AdminMiniappUser>(`/users/${id}/membership`, {
    method: "PUT",
    body: JSON.stringify({ membership_expires_at }),
  });
}

export function assignMiniappUserHealthManager(
  id: number,
  data: { mode: "random" | "specified"; assistant_id?: number },
) {
  return request<AdminMiniappUser>(`/users/${id}/health-manager`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export type AgreementType = "user_agreement" | "privacy_policy";

export type AgreementItem = {
  id: number;
  agreement_type: AgreementType;
  title: string;
  content_markdown: string;
  created_at: string | null;
  updated_at: string | null;
};

export type AgreementPayload = {
  title: string;
  content_markdown: string;
};

export function getAgreement(type: AgreementType) {
  return request<AgreementItem>(`/agreements/${type}`);
}

export function updateAgreement(type: AgreementType, data: AgreementPayload) {
  return request<AgreementItem>(`/agreements/${type}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export type CustomerServiceChatMessageType = "text" | "image" | "video" | "assistant_card";

export type CustomerServiceChatConversation = {
  id: string;
  conversation_type: string;
  target_type: string;
  target_id: string;
  target_name: string;
  target_title: string;
  target_label: string;
  target_avatar: string;
  last_message_preview: string;
  last_message_type: string;
  last_message_at: string | null;
  unread_count: number;
};

export type CustomerServiceChatConversationListParams = {
  page?: number;
  page_size?: number;
};

export type CustomerServiceChatAttachment = {
  id?: string;
  file_type: "image" | "video";
  file_object_key?: string;
  file_url: string;
  thumbnail_object_key?: string;
  thumbnail_url?: string;
  file_name?: string;
  mime_type?: string;
  file_size?: number;
  duration_seconds?: number;
  width?: number;
  height?: number;
};

export type AssistantCardPayload = {
  assistant_id: string;
  assistant_name: string;
  assistant_type: AssistantType;
  assistant_phone: string;
  assistant_avatar: string;
  assistant_avatar_object_key?: string;
  assistant_title: string;
  message?: string;
};

export type CustomerServiceChatMessage = {
  id: string;
  conversation_id: string;
  sender_type: "user" | "customer_service" | "system";
  sender_id: string;
  sender_name: string;
  sender_avatar: string;
  sender_role_label: string;
  is_mine: boolean;
  message_type: CustomerServiceChatMessageType;
  content: string;
  status: string;
  sent_at: string | null;
  card_payload?: AssistantCardPayload | null;
  attachments: CustomerServiceChatAttachment[];
};

export function getCustomerServiceChatConversations(params: CustomerServiceChatConversationListParams = {}) {
  return request<{
    items: CustomerServiceChatConversation[];
    pagination: { page: number; page_size: number; total: number };
  }>(`/customer-service-chat/conversations${buildQuery(params)}`);
}

export function getCustomerServiceChatMessages(conversationId: string, beforeId?: string) {
  const query = beforeId ? `?before_id=${encodeURIComponent(beforeId)}` : "";
  return request<{ items: CustomerServiceChatMessage[] }>(
    `/customer-service-chat/conversations/${conversationId}/messages${query}`,
  );
}

export function sendCustomerServiceChatMessage(
  conversationId: string,
  data: {
    message_type: "text" | "image" | "video";
    content?: string;
    attachments?: CustomerServiceChatAttachment[];
  },
) {
  return request<CustomerServiceChatMessage>(`/customer-service-chat/conversations/${conversationId}/messages`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function sendCustomerServiceHealthManagerCard(
  conversationId: string,
  data: { mode: "random" | "specified"; assistant_id?: number },
) {
  return request<CustomerServiceChatMessage>(
    `/customer-service-chat/conversations/${conversationId}/health-manager-card`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}

export function markCustomerServiceChatRead(conversationId: string) {
  return request<null>(`/customer-service-chat/conversations/${conversationId}/read`, {
    method: "POST",
  });
}
