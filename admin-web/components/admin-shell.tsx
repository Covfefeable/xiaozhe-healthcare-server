"use client";

import {
  AppstoreOutlined,
  FileTextOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PictureOutlined,
  ShoppingOutlined,
  UserSwitchOutlined,
} from "@ant-design/icons";
import {
  Avatar,
  Breadcrumb,
  Button,
  Card,
  ConfigProvider,
  Dropdown,
  Flex,
  Layout,
  Menu,
  Space,
  Typography,
  message,
  theme,
} from "antd";
import zhCN from "antd/locale/zh_CN";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { logout } from "@/lib/api";
import { clearSession, getStoredUser, type AdminUser } from "@/lib/auth";
import "./admin-shell.css";

const { Header, Sider, Content } = Layout;

const text = {
  brandMark: "\u54f2",
  brandName: "\u5c0f\u54f2\u533b\u7597",
  console: "\u540e\u53f0\u7ba1\u7406",
  home: "\u9996\u9875",
  products: "\u4ea7\u54c1\u7ba1\u7406",
  banners: "Banner \u7ba1\u7406",
  news: "\u8d44\u8baf\u7ba1\u7406",
  emptyTitle: "\u6682\u65e0\u5185\u5bb9",
  emptyDescription: "\u8bf7\u4ece\u4e1a\u52a1\u9700\u6c42\u5f00\u59cb\u9010\u6b65\u642d\u5efa\u9875\u9762\u3002",
  collapse: "\u6536\u8d77\u83dc\u5355",
  expand: "\u5c55\u5f00\u83dc\u5355",
  logout: "\u9000\u51fa\u767b\u5f55",
  logoutDone: "\u5df2\u9000\u51fa\u767b\u5f55",
  admin: "\u7ba1\u7406\u5458",
};

const menuItems = [
  {
    key: "home",
    icon: <AppstoreOutlined />,
    label: text.home,
  },
  {
    key: "products",
    icon: <ShoppingOutlined />,
    label: text.products,
  },
  {
    key: "banners",
    icon: <PictureOutlined />,
    label: text.banners,
  },
  {
    key: "news",
    icon: <FileTextOutlined />,
    label: text.news,
  },
];

type AdminShellProps = {
  children?: React.ReactNode;
};

export function AdminShell({ children }: AdminShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [messageApi, contextHolder] = message.useMessage();
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<AdminUser | null>(null);
  const activeKey = pathname.startsWith("/products")
    ? "products"
    : pathname.startsWith("/banners")
      ? "banners"
    : pathname.startsWith("/news")
      ? "news"
      : "home";

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // Local cleanup is enough for stateless token logout.
    } finally {
      clearSession();
      messageApi.success(text.logoutDone);
      router.replace("/login");
    }
  };

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === "products") {
      router.push("/products");
      return;
    }
    if (key === "banners") {
      router.push("/banners");
      return;
    }
    if (key === "news") {
      router.push("/news");
      return;
    }
    router.push("/");
  };

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: "#0f766e",
          colorInfo: "#0f766e",
          borderRadius: 14,
          fontFamily: "\"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif",
        },
        components: {
          Layout: {
            bodyBg: "#f4f7f7",
            headerBg: "#ffffff",
            siderBg: "#102421",
          },
        },
      }}
    >
      {contextHolder}
      <Layout className="admin-shell">
        <Sider
          className="admin-shell__sider"
          collapsed={collapsed}
          collapsible
          trigger={null}
          width={264}
        >
          <div className="admin-shell__brand">
            <div className="admin-shell__brand-mark">{text.brandMark}</div>
            {!collapsed && (
              <div>
                <Typography.Text className="admin-shell__brand-title">
                  {text.brandName}
                </Typography.Text>
                <Typography.Text className="admin-shell__brand-subtitle">
                  {text.console}
                </Typography.Text>
              </div>
            )}
          </div>
          <Menu
            className="admin-shell__menu"
            items={menuItems}
            mode="inline"
            onClick={handleMenuClick}
            selectedKeys={[activeKey]}
            theme="dark"
          />
        </Sider>

        <Layout className="admin-shell__main">
          <Header className="admin-shell__header">
            <Flex align="center" justify="space-between" gap={16}>
              <Space size={16}>
                <Button
                  aria-label={collapsed ? text.expand : text.collapse}
                  icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                  onClick={() => setCollapsed((value) => !value)}
                  shape="circle"
                  type="text"
                />
                <div>
                  <Breadcrumb
                    items={[
                      { title: text.brandName },
                      {
                        title:
                          activeKey === "products"
                            ? text.products
                            : activeKey === "banners"
                              ? text.banners
                            : activeKey === "news"
                              ? text.news
                              : text.home,
                      },
                    ]}
                  />
                </div>
              </Space>

              <Dropdown
                menu={{
                  items: [
                    {
                      key: "logout",
                      icon: <LogoutOutlined />,
                      label: text.logout,
                      onClick: handleLogout,
                    },
                  ],
                }}
                placement="bottomRight"
              >
                <Space className="admin-shell__user">
                  <Avatar icon={<UserSwitchOutlined />} />
                  <span>{user?.display_name ?? text.admin}</span>
                </Space>
              </Dropdown>
            </Flex>
          </Header>

          <Content className="admin-shell__content">
            {children ?? (
              <Card className="admin-shell__blank">
                <div className="admin-shell__empty">
                  <Typography.Title level={4}>{text.emptyTitle}</Typography.Title>
                  <Typography.Text type="secondary">
                    {text.emptyDescription}
                  </Typography.Text>
                </div>
              </Card>
            )}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}
