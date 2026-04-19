"use client";

import {
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
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
  Space,
  Typography,
  message,
  theme,
} from "antd";
import { useRouter } from "next/navigation";
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
  emptyTitle: "\u6682\u65e0\u5185\u5bb9",
  emptyDescription: "\u8bf7\u4ece\u4e1a\u52a1\u9700\u6c42\u5f00\u59cb\u9010\u6b65\u642d\u5efa\u9875\u9762\u3002",
  collapse: "\u6536\u8d77\u83dc\u5355",
  expand: "\u5c55\u5f00\u83dc\u5355",
  logout: "\u9000\u51fa\u767b\u5f55",
  logoutDone: "\u5df2\u9000\u51fa\u767b\u5f55",
  admin: "\u7ba1\u7406\u5458",
};

export function AdminShell() {
  const router = useRouter();
  const [messageApi, contextHolder] = message.useMessage();
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<AdminUser | null>(null);

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

  return (
    <ConfigProvider
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
                      { title: text.home },
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
            <Card className="admin-shell__blank">
              <div className="admin-shell__empty">
                <Typography.Title level={4}>{text.emptyTitle}</Typography.Title>
                <Typography.Text type="secondary">
                  {text.emptyDescription}
                </Typography.Text>
              </div>
            </Card>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}
