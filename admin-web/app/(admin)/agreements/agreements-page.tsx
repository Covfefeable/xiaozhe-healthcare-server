"use client";

import { Button, Card, Form, Input, Space, Tabs, Typography, message } from "antd";
import MarkdownIt from "markdown-it";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import {
  getAgreement,
  updateAgreement,
  type AgreementItem,
  type AgreementType,
} from "@/lib/api";
import { uploadFile } from "@/lib/upload";

const MdEditor = dynamic(() => import("react-markdown-editor-lite"), { ssr: false });
const mdParser = new MarkdownIt({
  breaks: true,
  html: false,
  linkify: true,
});

type AgreementFormValues = {
  title: string;
};

const agreementTabs: { key: AgreementType; label: string }[] = [
  { key: "user_agreement", label: "用户协议管理" },
  { key: "privacy_policy", label: "隐私政策管理" },
];

type AgreementsPageProps = {
  initialType: AgreementType;
};

export function AgreementsPage({ initialType }: AgreementsPageProps) {
  const router = useRouter();
  const [messageApi, contextHolder] = message.useMessage();
  const [form] = Form.useForm<AgreementFormValues>();
  const [agreement, setAgreement] = useState<AgreementItem | null>(null);
  const [markdownValue, setMarkdownValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const activeType = initialType;
  const activeTabLabel = useMemo(
    () => agreementTabs.find((item) => item.key === activeType)?.label ?? "协议管理",
    [activeType],
  );

  useEffect(() => {
    let ignore = false;

    async function loadAgreement() {
      setLoading(true);
      try {
        const data = await getAgreement(activeType);
        if (ignore) {
          return;
        }
        setAgreement(data);
        setMarkdownValue(data.content_markdown ?? "");
        form.setFieldsValue({
          title: data.title,
        });
      } catch (error) {
        if (!ignore) {
          messageApi.error(error instanceof Error ? error.message : "加载协议失败");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    void loadAgreement();

    return () => {
      ignore = true;
    };
  }, [activeType, form, messageApi]);

  const handleTabChange = (key: string) => {
    router.replace(key === "privacy_policy" ? "/agreements/privacy" : "/agreements/user");
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    setSaving(true);
    try {
      const data = await updateAgreement(activeType, {
        title: values.title.trim(),
        content_markdown: markdownValue,
      });
      setAgreement(data);
      setMarkdownValue(data.content_markdown ?? "");
      messageApi.success("保存成功");
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleEditorImageUpload = async (file: File) => {
    const result = await uploadFile(file, "markdown");
    return result.url;
  };

  return (
    <>
      {contextHolder}
      <div className="agreements-page">
        <div className="agreements-page__heading">
          <Typography.Title level={4}>协议管理</Typography.Title>
          <div className="agreements-page__meta">
            {agreement?.updated_at ? `最后更新时间：${new Date(agreement.updated_at).toLocaleString()}` : activeTabLabel}
          </div>
        </div>

        <Card className="agreements-page__card" loading={loading}>
          <Tabs
            activeKey={activeType}
            items={agreementTabs}
            onChange={handleTabChange}
          />

          <Form className="agreements-page__form" form={form} layout="vertical">
            <Form.Item
              label="协议标题"
              name="title"
              rules={[
                { required: true, message: "请输入协议标题" },
                { max: 80, message: "协议标题不能超过 80 个字符" },
              ]}
            >
              <Input maxLength={80} placeholder="请输入协议标题" showCount />
            </Form.Item>
            <Form.Item label="协议内容">
              <MdEditor
                config={{
                  canView: {
                    fullScreen: false,
                    hideMenu: false,
                    html: true,
                    menu: true,
                    md: true,
                  },
                }}
                onChange={({ text }) => setMarkdownValue(text)}
                onImageUpload={handleEditorImageUpload}
                renderHTML={(text) => mdParser.render(text)}
                style={{ height: 520 }}
                value={markdownValue}
              />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" loading={saving} onClick={() => void handleSave()}>
                  保存
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      </div>
    </>
  );
}
