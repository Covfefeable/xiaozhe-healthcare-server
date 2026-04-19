"use client";

import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, Tabs, Typography, message } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getAuthConfig, login, register } from "@/lib/api";
import { getAccessToken, saveSession } from "@/lib/auth";
import "./styles.css";

type LoginForm = {
  username: string;
  password: string;
};

type RegisterForm = LoginForm & {
  display_name: string;
  email?: string;
  phone?: string;
};

const text = {
  brandMark: "\u54f2",
  title: "\u5c0f\u54f2\u533b\u7597 Admin",
  subtitle: "\u8bf7\u767b\u5f55\u540e\u53f0\u7ba1\u7406\u7cfb\u7edf",
  login: "\u767b\u5f55",
  register: "\u6ce8\u518c",
  username: "\u7528\u6237\u540d",
  password: "\u5bc6\u7801",
  displayName: "\u5c55\u793a\u540d\u79f0",
  email: "\u90ae\u7bb1",
  phone: "\u624b\u673a\u53f7",
  optional: "\u53ef\u9009",
  inputUsername: "\u8bf7\u8f93\u5165\u7528\u6237\u540d",
  inputPassword: "\u8bf7\u8f93\u5165\u5bc6\u7801",
  inputDisplayName: "\u8bf7\u8f93\u5165\u5c55\u793a\u540d\u79f0",
  loginSuccess: "\u767b\u5f55\u6210\u529f",
  loginFailed: "\u767b\u5f55\u5931\u8d25",
  registerSuccess: "\u6ce8\u518c\u6210\u529f\uff0c\u8bf7\u767b\u5f55",
  registerFailed: "\u6ce8\u518c\u5931\u8d25",
};

export default function LoginPage() {
  const router = useRouter();
  const [messageApi, contextHolder] = message.useMessage();
  const [allowRegister, setAllowRegister] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (getAccessToken()) {
      router.replace("/");
      return;
    }

    getAuthConfig()
      .then((config) => setAllowRegister(config.allow_register))
      .catch(() => setAllowRegister(false));
  }, [router]);

  const handleLogin = async (values: LoginForm) => {
    setLoading(true);
    try {
      const result = await login(values);
      saveSession(result);
      messageApi.success(text.loginSuccess);
      router.replace("/");
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : text.loginFailed);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: RegisterForm) => {
    setLoading(true);
    try {
      await register(values);
      messageApi.success(text.registerSuccess);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : text.registerFailed);
    } finally {
      setLoading(false);
    }
  };

  const loginForm = (
    <Form layout="vertical" onFinish={handleLogin}>
      <Form.Item name="username" label={text.username} rules={[{ required: true, message: text.inputUsername }]}>
        <Input prefix={<UserOutlined />} placeholder={text.inputUsername} size="large" />
      </Form.Item>
      <Form.Item name="password" label={text.password} rules={[{ required: true, message: text.inputPassword }]}>
        <Input.Password prefix={<LockOutlined />} placeholder={text.inputPassword} size="large" />
      </Form.Item>
      <Button block htmlType="submit" loading={loading} size="large" type="primary">
        {text.login}
      </Button>
    </Form>
  );

  const registerForm = (
    <Form layout="vertical" onFinish={handleRegister}>
      <Form.Item name="username" label={text.username} rules={[{ required: true, message: text.inputUsername }]}>
        <Input prefix={<UserOutlined />} placeholder={text.inputUsername} size="large" />
      </Form.Item>
      <Form.Item name="display_name" label={text.displayName} rules={[{ required: true, message: text.inputDisplayName }]}>
        <Input placeholder={text.inputDisplayName} size="large" />
      </Form.Item>
      <Form.Item name="password" label={text.password} rules={[{ required: true, message: text.inputPassword }]}>
        <Input.Password prefix={<LockOutlined />} placeholder={text.inputPassword} size="large" />
      </Form.Item>
      <Form.Item name="email" label={text.email}>
        <Input placeholder={text.optional} size="large" />
      </Form.Item>
      <Form.Item name="phone" label={text.phone}>
        <Input placeholder={text.optional} size="large" />
      </Form.Item>
      <Button block htmlType="submit" loading={loading} size="large" type="primary">
        {text.register}
      </Button>
    </Form>
  );

  return (
    <main className="login-page">
      {contextHolder}
      <Card className="login-card">
        <div className="login-brand">
          <div className="login-brand__mark">{text.brandMark}</div>
          <Typography.Title level={2}>{text.title}</Typography.Title>
          <Typography.Text type="secondary">{text.subtitle}</Typography.Text>
        </div>

        <Tabs
          centered
          items={[
            { key: "login", label: text.login, children: loginForm },
            ...(allowRegister ? [{ key: "register", label: text.register, children: registerForm }] : []),
          ]}
        />
      </Card>
    </main>
  );
}

