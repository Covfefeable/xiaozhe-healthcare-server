export type AdminUser = {
  id: number;
  username: string;
  display_name: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
};

export type LoginResult = {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  user: AdminUser;
};

const TOKEN_KEY = "xiaozhe_admin_access_token";
const USER_KEY = "xiaozhe_admin_user";

export function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(TOKEN_KEY);
}

export function saveSession(result: LoginResult) {
  window.localStorage.setItem(TOKEN_KEY, result.access_token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(result.user));
}

export function clearSession() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): AdminUser | null {
  if (typeof window === "undefined") {
    return null;
  }

  const value = window.localStorage.getItem(USER_KEY);
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as AdminUser;
  } catch {
    clearSession();
    return null;
  }
}

