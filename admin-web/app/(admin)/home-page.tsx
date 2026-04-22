"use client";

import {
  ArrowRightOutlined,
  FileTextOutlined,
  ProfileOutlined,
  ShoppingOutlined,
  TeamOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Button, Card, Col, Row, Skeleton, Space, Statistic, Typography, message } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getDashboard, type DashboardData } from "@/lib/api";

const overviewItems = [
  { key: "today_new_users", label: "今日新增用户", suffix: "人" },
  { key: "active_members", label: "会员用户", suffix: "人" },
  { key: "today_orders", label: "今日订单", suffix: "单" },
  { key: "today_paid_amount", label: "今日实收", prefix: "¥" },
] as const;

const quickEntries = [
  { title: "产品管理", desc: "维护可售产品和会员服务", path: "/products", icon: <ShoppingOutlined /> },
  { title: "订单管理", desc: "处理订单进度和退款申请", path: "/orders", icon: <ProfileOutlined /> },
  { title: "用户管理", desc: "查看用户资料与会员状态", path: "/users", icon: <UserOutlined /> },
  { title: "人员管理", desc: "维护医生、助理和客服", path: "/assistants", icon: <TeamOutlined /> },
  { title: "协议管理", desc: "维护登录页协议内容", path: "/agreements/user", icon: <FileTextOutlined /> },
];

export function HomePage() {
  const router = useRouter();
  const [messageApi, contextHolder] = message.useMessage();
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);

  useEffect(() => {
    getDashboard()
      .then(setDashboard)
      .catch((error) => {
        messageApi.error(error instanceof Error ? error.message : "首页数据加载失败");
      })
      .finally(() => setLoading(false));
  }, [messageApi]);

  const todos = dashboard
    ? [
        {
          title: "待处理退款",
          count: dashboard.todos.pending_refund_orders,
          desc: "需要后台确认退款结果",
          path: "/orders",
          tone: "danger",
        },
        {
          title: "进行中订单",
          count: dashboard.todos.in_progress_orders,
          desc: "需要持续跟进服务进度",
          path: "/orders",
          tone: "primary",
        },
        {
          title: "待支付订单",
          count: dashboard.todos.pending_payment_orders,
          desc: "用户已创建但尚未支付",
          path: "/orders",
          tone: "muted",
        },
      ]
    : [];

  return (
    <div className="home-page">
      {contextHolder}
      <section className="home-hero">
        <div>
          <Typography.Title level={3}>工作台</Typography.Title>
          <Typography.Text>关注今日经营概览和需要及时处理的事项。</Typography.Text>
        </div>
      </section>

      <Row gutter={[18, 18]}>
        {overviewItems.map((item) => (
          <Col key={item.key} lg={6} md={12} xs={24}>
            <Card className="home-metric-card">
              <Skeleton active loading={loading} paragraph={false}>
                <Statistic
                  title={item.label}
                  value={dashboard?.overview[item.key] ?? 0}
                  prefix={"prefix" in item ? item.prefix : undefined}
                  suffix={"suffix" in item ? item.suffix : undefined}
                />
              </Skeleton>
            </Card>
          </Col>
        ))}
      </Row>

      <Row className="home-section" gutter={[18, 18]}>
        <Col lg={10} xs={24}>
          <Card title="待处理事项" className="home-panel">
            <Skeleton active loading={loading}>
              <Space direction="vertical" size={12} style={{ width: "100%" }}>
                {todos.map((todo) => (
                  <button
                    className={`home-todo home-todo--${todo.tone}`}
                    key={todo.title}
                    onClick={() => router.push(todo.path)}
                    type="button"
                  >
                    <span>
                      <strong>{todo.title}</strong>
                      <small>{todo.desc}</small>
                    </span>
                    <em>{todo.count}</em>
                  </button>
                ))}
              </Space>
            </Skeleton>
          </Card>
        </Col>

        <Col lg={14} xs={24}>
          <Card title="快捷入口" className="home-panel">
            <div className="home-shortcuts">
              {quickEntries.map((entry) => (
                <button
                  className="home-shortcut"
                  key={entry.path}
                  onClick={() => router.push(entry.path)}
                  type="button"
                >
                  <span className="home-shortcut__icon">{entry.icon}</span>
                  <span className="home-shortcut__body">
                    <strong>{entry.title}</strong>
                    <small>{entry.desc}</small>
                  </span>
                  <ArrowRightOutlined />
                </button>
              ))}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
