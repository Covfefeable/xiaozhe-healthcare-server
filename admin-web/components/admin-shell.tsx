"use client";

import {
  AppstoreOutlined,
  ApartmentOutlined,
  FileTextOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  MessageOutlined,
  PictureOutlined,
  ShoppingOutlined,
  ProfileOutlined,
  TeamOutlined,
  UserSwitchOutlined,
  UserOutlined,
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
  brandName: "\u5c0f\u54f2\u533b\u7597",
  console: "\u540e\u53f0\u7ba1\u7406",
  home: "\u9996\u9875",
  products: "\u4ea7\u54c1\u7ba1\u7406",
  orders: "\u8ba2\u5355\u7ba1\u7406",
  users: "\u7528\u6237\u7ba1\u7406",
  banners: "Banner \u7ba1\u7406",
  news: "\u8d44\u8baf\u7ba1\u7406",
  agreements: "\u534f\u8bae\u7ba1\u7406",
  userAgreement: "\u7528\u6237\u534f\u8bae\u7ba1\u7406",
  privacyPolicy: "\u9690\u79c1\u653f\u7b56\u7ba1\u7406",
  personnel: "\u4eba\u5458\u7ba1\u7406",
  departments: "\u79d1\u5ba4\u7ba1\u7406",
  doctors: "\u533b\u751f\u7ba1\u7406",
  assistants: "\u52a9\u7406\u7ba1\u7406",
  customerServices: "\u5ba2\u670d\u7ba1\u7406",
  customerServiceMessages: "\u5ba2\u670d\u6d88\u606f",
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
    key: "orders",
    icon: <ProfileOutlined />,
    label: text.orders,
  },
  {
    key: "users",
    icon: <UserOutlined />,
    label: text.users,
  },
  {
    key: "banners",
    icon: <PictureOutlined />,
    label: text.banners,
  },
  {
    key: "personnel",
    icon: <TeamOutlined />,
    label: text.personnel,
    children: [
      {
        key: "departments",
        icon: <ApartmentOutlined />,
        label: text.departments,
      },
      {
        key: "doctors",
        icon: <UserSwitchOutlined />,
        label: text.doctors,
      },
      {
        key: "assistants",
        icon: <UserSwitchOutlined />,
        label: text.assistants,
      },
      {
        key: "customer-services",
        icon: <UserSwitchOutlined />,
        label: text.customerServices,
      },
    ],
  },
  {
    key: "customer-service-messages",
    icon: <MessageOutlined />,
    label: text.customerServiceMessages,
  },
  {
    key: "news",
    icon: <FileTextOutlined />,
    label: text.news,
  },
  {
    key: "agreements",
    icon: <FileTextOutlined />,
    label: text.agreements,
    children: [
      {
        key: "agreement-user",
        label: text.userAgreement,
      },
      {
        key: "agreement-privacy",
        label: text.privacyPolicy,
      },
    ],
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
  const activeKey = pathname.startsWith("/agreements")
    ? pathname.startsWith("/agreements/privacy")
      ? "agreement-privacy"
      : "agreement-user"
    : pathname.startsWith("/products")
    ? "products"
    : pathname.startsWith("/orders")
      ? "orders"
    : pathname.startsWith("/users")
      ? "users"
    : pathname.startsWith("/banners")
      ? "banners"
    : pathname.startsWith("/departments")
      ? "departments"
    : pathname.startsWith("/doctors")
      ? "doctors"
    : pathname.startsWith("/assistants")
      ? "assistants"
    : pathname.startsWith("/customer-services")
      ? "customer-services"
    : pathname.startsWith("/customer-service-messages")
      ? "customer-service-messages"
    : pathname.startsWith("/news")
      ? "news"
      : "home";
  const activeTitle =
    activeKey === "products"
      ? text.products
      : activeKey === "orders"
        ? text.orders
      : activeKey === "users"
        ? text.users
      : activeKey === "banners"
        ? text.banners
      : activeKey === "departments"
        ? text.departments
      : activeKey === "doctors"
        ? text.doctors
      : activeKey === "assistants"
        ? text.assistants
      : activeKey === "customer-services"
        ? text.customerServices
      : activeKey === "customer-service-messages"
        ? text.customerServiceMessages
      : activeKey === "news"
        ? text.news
      : activeKey === "agreement-user"
        ? text.userAgreement
      : activeKey === "agreement-privacy"
        ? text.privacyPolicy
        : text.home;

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  useEffect(() => {
    document.title = `${activeTitle} - 小哲医疗管理后台`;
  }, [activeTitle]);

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
    if (key === "orders") {
      router.push("/orders");
      return;
    }
    if (key === "users") {
      router.push("/users");
      return;
    }
    if (key === "banners") {
      router.push("/banners");
      return;
    }
    if (key === "departments") {
      router.push("/departments");
      return;
    }
    if (key === "doctors") {
      router.push("/doctors");
      return;
    }
    if (key === "assistants") {
      router.push("/assistants");
      return;
    }
    if (key === "customer-services") {
      router.push("/customer-services");
      return;
    }
    if (key === "customer-service-messages") {
      router.push("/customer-service-messages");
      return;
    }
    if (key === "news") {
      router.push("/news");
      return;
    }
    if (key === "agreement-user") {
      router.push("/agreements/user");
      return;
    }
    if (key === "agreement-privacy") {
      router.push("/agreements/privacy");
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
            defaultOpenKeys={["personnel", "agreements"]}
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
                      { title: activeTitle },
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
