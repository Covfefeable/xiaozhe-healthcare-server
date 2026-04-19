import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "小哲医疗 Admin",
  description: "小哲医疗后台管理系统基础框架",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}

