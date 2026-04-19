"use client";

import {
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
  theme,
} from "antd";
import { useState } from "react";

import "./admin-shell.css";

const { Header, Sider, Content } = Layout;

export function AdminShell() {
  const [collapsed, setCollapsed] = useState(false);

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
            bodyBg: "#eef4f8",
            headerBg: "rgba(255, 255, 255, 0.84)",
            siderBg: "#10201f",
          },
        },
      }}
    >
      <Layout className="admin-shell">
        <Sider
          className="admin-shell__sider"
          collapsed={collapsed}
          collapsible
          trigger={null}
          width={264}
        >
          <div className="admin-shell__brand">
            <div className="admin-shell__brand-mark">哲</div>
            {!collapsed && (
              <div>
                <Typography.Text className="admin-shell__brand-title">
                  小哲医疗
                </Typography.Text>
                <Typography.Text className="admin-shell__brand-subtitle">
                  Admin Console
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
                  aria-label={collapsed ? "展开菜单" : "收起菜单"}
                  icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                  onClick={() => setCollapsed((value) => !value)}
                  shape="circle"
                  type="text"
                />
                <div>
                  <Breadcrumb
                    items={[
                      { title: "小哲医疗" },
                      { title: "首页" },
                    ]}
                  />
                  <Typography.Title level={4} className="admin-shell__title">
                    首页
                  </Typography.Title>
                </div>
              </Space>

              <Space size={12}>
                <Dropdown
                  menu={{
                    items: [
                      { key: "profile", label: "账号信息" },
                      { key: "logout", label: "退出登录" },
                    ],
                  }}
                  placement="bottomRight"
                >
                  <Space className="admin-shell__user">
                    <Avatar icon={<UserSwitchOutlined />} />
                    <span>管理员</span>
                  </Space>
                </Dropdown>
              </Space>
            </Flex>
          </Header>

          <Content className="admin-shell__content">
            <Card className="admin-shell__blank" />
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}
