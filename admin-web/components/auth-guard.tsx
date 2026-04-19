"use client";

import { Spin } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getMe } from "@/lib/api";
import { clearSession, getAccessToken } from "@/lib/auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    getMe()
      .then(() => setReady(true))
      .catch(() => {
        clearSession();
        router.replace("/login");
      });
  }, [router]);

  if (!ready) {
    return (
      <div className="auth-loading">
        <Spin size="large" />
      </div>
    );
  }

  return children;
}

