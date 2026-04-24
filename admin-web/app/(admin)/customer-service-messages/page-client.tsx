"use client";

import {
  Avatar,
  Button,
  Card,
  Descriptions,
  Empty,
  Form,
  Image,
  Input,
  List,
  Modal,
  Pagination,
  Radio,
  Select,
  Space,
  Spin,
  Tag,
  Typography,
  message,
} from "antd";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  getMiniappUser,
  getAssistantList,
  getCustomerServiceChatConversations,
  getCustomerServiceChatMessages,
  markCustomerServiceChatRead,
  sendCustomerServiceChatMessage,
  sendCustomerServiceHealthManagerCard,
  type AdminMiniappHealthRecord,
  type AdminMiniappUser,
  type CustomerServiceChatAttachment,
  type CustomerServiceChatConversation,
  type CustomerServiceChatMessage,
  type StaffItem,
} from "@/lib/api";
import { uploadFile } from "@/lib/upload";

function formatTime(value: string | null) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "";
}

type CardFormValues = {
  mode: "random" | "specified";
  assistant_id?: number;
};

function RecordList({ items }: { items?: AdminMiniappHealthRecord[] }) {
  if (!items?.length) {
    return <Empty description="暂未填写" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
  }
  return (
    <Space direction="vertical" size={12} style={{ width: "100%" }}>
      {items.map((item) => (
        <Card key={item.id} size="small">
          <Typography.Paragraph style={{ marginBottom: item.image_urls.length ? 12 : 0, whiteSpace: "pre-wrap" }}>
            {item.content || "未填写文字说明"}
          </Typography.Paragraph>
          {item.image_urls.length ? (
            <Image.PreviewGroup>
              <Space wrap>
                {item.image_urls.map((url, index) => (
                  <Image
                    key={`${item.id}-${index}`}
                    src={url}
                    width={72}
                    height={72}
                    style={{ borderRadius: 10, objectFit: "cover" }}
                    alt="档案图片"
                  />
                ))}
              </Space>
            </Image.PreviewGroup>
          ) : null}
        </Card>
      ))}
    </Space>
  );
}

export function CustomerServiceMessagesPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [cardForm] = Form.useForm<CardFormValues>();
  const imageInputRef = useRef<HTMLInputElement | null>(null);
  const videoInputRef = useRef<HTMLInputElement | null>(null);
  const [conversations, setConversations] = useState<CustomerServiceChatConversation[]>([]);
  const [conversationPage, setConversationPage] = useState(1);
  const [conversationTotal, setConversationTotal] = useState(0);
  const [selectedConversationId, setSelectedConversationId] = useState<string>("");
  const [messages, setMessages] = useState<CustomerServiceChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [cardModalOpen, setCardModalOpen] = useState(false);
  const [cardSending, setCardSending] = useState(false);
  const [healthManagers, setHealthManagers] = useState<StaffItem[]>([]);
  const [healthManagersLoading, setHealthManagersLoading] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState<AdminMiniappUser | null>(null);

  const selectedConversation = useMemo(
    () => conversations.find((item) => item.id === selectedConversationId) ?? null,
    [conversations, selectedConversationId],
  );
  const assignMode = Form.useWatch("mode", cardForm) ?? "random";

  const loadConversations = async (keepSelection = true, silent = false) => {
    if (!silent) {
      setLoading(true);
    }
    try {
      const result = await getCustomerServiceChatConversations({ page: conversationPage, page_size: 20 });
      const items = result.items;
      setConversations(items);
      setConversationTotal(result.pagination.total);
      setSelectedConversationId((current) => {
        if (keepSelection && current && items.some((item) => item.id === current)) {
          return current;
        }
        return items[0]?.id ?? "";
      });
    } catch (error) {
      if (!silent) {
        messageApi.error(error instanceof Error ? error.message : "会话加载失败");
      }
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  };

  const loadMessages = async (conversationId: string, silent = false) => {
    if (!conversationId) {
      setMessages([]);
      return;
    }
    if (!silent) {
      setMessagesLoading(true);
    }
    try {
      const result = await getCustomerServiceChatMessages(conversationId);
      setMessages(result.items);
      await markCustomerServiceChatRead(conversationId);
    } catch (error) {
      if (!silent) {
        messageApi.error(error instanceof Error ? error.message : "消息加载失败");
      }
    } finally {
      if (!silent) {
        setMessagesLoading(false);
      }
    }
  };

  useEffect(() => {
    void loadConversations(false);
  }, [conversationPage]);

  useEffect(() => {
    if (!selectedConversationId) {
      setMessages([]);
      return;
    }
    void loadMessages(selectedConversationId);
  }, [selectedConversationId]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      void loadConversations(true, true);
      if (selectedConversationId) {
        void loadMessages(selectedConversationId, true);
      }
    }, 3000);
    return () => window.clearInterval(timer);
  }, [conversationPage, selectedConversationId]);

  const handleSendText = async () => {
    const content = inputValue.trim();
    if (!selectedConversationId || !content) {
      return;
    }
    setSending(true);
    try {
      const nextMessage = await sendCustomerServiceChatMessage(selectedConversationId, {
        message_type: "text",
        content,
      });
      setInputValue("");
      setMessages((value) => [...value, nextMessage]);
      await loadConversations(true, true);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "发送失败");
    } finally {
      setSending(false);
    }
  };

  const handleUpload = async (file: File, kind: "image" | "video") => {
    if (!selectedConversationId) {
      return;
    }
    setSending(true);
    try {
      const result = await uploadFile(
        file,
        kind === "image" ? "customer_service_chat_image" : "customer_service_chat_video",
      );
      const attachment: CustomerServiceChatAttachment = {
        file_type: kind,
        file_object_key: result.object_key,
        file_url: result.url,
        file_name: result.file_name,
        mime_type: result.mime_type,
        file_size: result.size,
      };
      const nextMessage = await sendCustomerServiceChatMessage(selectedConversationId, {
        message_type: kind,
        attachments: [attachment],
      });
      setMessages((value) => [...value, nextMessage]);
      await loadConversations(true, true);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "发送失败");
    } finally {
      setSending(false);
    }
  };

  const openCardModal = async () => {
    cardForm.setFieldsValue({ mode: "random", assistant_id: undefined });
    setCardModalOpen(true);
    setHealthManagersLoading(true);
    try {
      const result = await getAssistantList({
        assistant_type: "health_manager",
        status: "active",
        page: 1,
        page_size: 100,
      });
      setHealthManagers(result.items);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "健康管家加载失败");
    } finally {
      setHealthManagersLoading(false);
    }
  };

  const handleSendCard = async () => {
    if (!selectedConversationId) {
      return;
    }
    const values = await cardForm.validateFields();
    setCardSending(true);
    try {
      const nextMessage = await sendCustomerServiceHealthManagerCard(selectedConversationId, values);
      setCardModalOpen(false);
      setMessages((value) => [...value, nextMessage]);
      await loadConversations(true, true);
      messageApi.success("已发送健康管家名片");
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "发送失败");
    } finally {
      setCardSending(false);
    }
  };

  const openUserDetail = async () => {
    if (!selectedConversation?.target_id) {
      return;
    }
    setDetailOpen(true);
    setDetailLoading(true);
    try {
      setCurrentUser(await getMiniappUser(Number(selectedConversation.target_id)));
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "用户详情加载失败");
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <>
      {contextHolder}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "320px 1fr",
          gap: 20,
          alignItems: "start",
        }}
      >
        <Card
          title="客服消息"
          bodyStyle={{ padding: 0, maxHeight: 720, display: "flex", flexDirection: "column" }}
        >
          {loading ? (
            <div style={{ padding: 24, textAlign: "center" }}>
              <Spin />
            </div>
          ) : conversations.length ? (
            <>
              <div style={{ overflow: "auto" }}>
                <List
                  dataSource={conversations}
                  renderItem={(item) => (
                    <List.Item
                      style={{
                        padding: "14px 16px",
                        cursor: "pointer",
                        background: item.id === selectedConversationId ? "#f0f7f7" : "#fff",
                      }}
                      onClick={() => setSelectedConversationId(item.id)}
                    >
                      <List.Item.Meta
                        avatar={<Avatar src={item.target_avatar || undefined}>{item.target_name.slice(0, 1)}</Avatar>}
                        title={
                          <Space size={8}>
                            <span>{item.target_name}</span>
                            {item.unread_count ? <Tag color="error">{item.unread_count}</Tag> : null}
                          </Space>
                        }
                        description={
                          <div>
                            <div style={{ color: "#6b7280", fontSize: 12 }}>{item.target_label || item.target_title}</div>
                            <div style={{ color: "#111827", marginTop: 4 }}>{item.last_message_preview || "暂无消息"}</div>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
              <div style={{ borderTop: "1px solid #f0f0f0", padding: 12, display: "flex", justifyContent: "center" }}>
                <Pagination
                  current={conversationPage}
                  pageSize={20}
                  total={conversationTotal}
                  size="small"
                  showSizeChanger={false}
                  onChange={(page) => setConversationPage(page)}
                />
              </div>
            </>
          ) : (
            <div style={{ padding: 24 }}>
              <Empty description="暂无客服会话" />
            </div>
          )}
        </Card>

        <Card
          title={selectedConversation ? `${selectedConversation.target_name} · ${selectedConversation.target_label || "就诊者"}` : "会话详情"}
          extra={
            selectedConversation ? (
              <Space>
                <Button onClick={() => void openUserDetail()}>查看用户详情</Button>
                <Button onClick={() => void openCardModal()}>发送管家名片</Button>
                <Button onClick={() => imageInputRef.current?.click()}>发图片</Button>
                <Button onClick={() => videoInputRef.current?.click()}>发视频</Button>
              </Space>
            ) : null
          }
          bodyStyle={{ padding: 24 }}
        >
          <input
            accept="image/*"
            hidden
            ref={imageInputRef}
            type="file"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) {
                void handleUpload(file, "image");
              }
              event.currentTarget.value = "";
            }}
          />
          <input
            accept="video/*"
            hidden
            ref={videoInputRef}
            type="file"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) {
                void handleUpload(file, "video");
              }
              event.currentTarget.value = "";
            }}
          />
          {selectedConversation ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div
                style={{
                  height: "clamp(420px, calc(100vh - 340px), 620px)",
                  overflow: "auto",
                  paddingRight: 4,
                }}
              >
                {messagesLoading ? (
                  <div style={{ padding: 40, textAlign: "center" }}>
                    <Spin />
                  </div>
                ) : messages.length ? (
                  <Space direction="vertical" size={14} style={{ width: "100%" }}>
                    {messages.map((item) => {
                      const isMine = item.is_mine;
                      return (
                        <div
                          key={item.id}
                          style={{
                            display: "flex",
                            justifyContent: isMine ? "flex-end" : "flex-start",
                          }}
                        >
                          <div style={{ maxWidth: 520 }}>
                            {!isMine && item.sender_name ? (
                              <div style={{ marginBottom: 6, color: "#6b7280", fontSize: 12 }}>
                                {item.sender_name}
                                {item.sender_role_label ? ` · ${item.sender_role_label}` : ""}
                              </div>
                            ) : null}
                            {item.message_type === "image" && item.attachments[0]?.file_url ? (
                              <Image
                                src={item.attachments[0].file_url}
                                width={220}
                                style={{ borderRadius: 16, overflow: "hidden" }}
                              />
                            ) : item.message_type === "video" && item.attachments[0]?.file_url ? (
                              <video
                                controls
                                src={item.attachments[0].file_url}
                                style={{ width: 280, borderRadius: 16, display: "block" }}
                              />
                            ) : item.message_type === "assistant_card" && item.card_payload ? (
                              <Card size="small" style={{ width: 320, borderRadius: 16 }}>
                                <Space align="start">
                                  <Avatar shape="square" size={56} src={item.card_payload.assistant_avatar || undefined}>
                                    {item.card_payload.assistant_name.slice(0, 1)}
                                  </Avatar>
                                  <div>
                                    <div style={{ fontWeight: 600 }}>{item.card_payload.assistant_name}</div>
                                    <div style={{ color: "#0f766e", fontSize: 12, marginTop: 4 }}>
                                      {item.card_payload.assistant_title || "健康管家"}
                                    </div>
                                    <div style={{ color: "#6b7280", fontSize: 12, marginTop: 6 }}>
                                      {item.card_payload.message || "已为用户分配专属健康管家"}
                                    </div>
                                  </div>
                                </Space>
                              </Card>
                            ) : (
                              <div
                                style={{
                                  padding: "12px 16px",
                                  borderRadius: 16,
                                  background: isMine ? "#0f766e" : "#f3f4f6",
                                  color: isMine ? "#fff" : "#111827",
                                  whiteSpace: "pre-wrap",
                                  wordBreak: "break-word",
                                }}
                              >
                                {item.content}
                              </div>
                            )}
                            <div style={{ marginTop: 6, color: "#9ca3af", fontSize: 12 }}>
                              {formatTime(item.sent_at)}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </Space>
                ) : (
                  <Empty description="暂无消息" />
                )}
              </div>

              <div style={{ paddingTop: 8 }}>
                <Space.Compact style={{ width: "100%" }}>
                <Input
                  placeholder="输入要发送的内容"
                  value={inputValue}
                  onChange={(event) => setInputValue(event.target.value)}
                  onPressEnter={() => void handleSendText()}
                />
                <Button loading={sending} type="primary" onClick={() => void handleSendText()}>
                  发送
                </Button>
                </Space.Compact>
              </div>
            </div>
          ) : (
            <Empty description="请选择左侧会话" />
          )}
        </Card>
      </div>

      <Modal
        title="发送健康管家名片"
        open={cardModalOpen}
        confirmLoading={cardSending}
        okText="发送"
        cancelText="取消"
        onCancel={() => setCardModalOpen(false)}
        onOk={() => void handleSendCard()}
      >
        <Form form={cardForm} layout="vertical" initialValues={{ mode: "random" }}>
          <Form.Item label="分配方式" name="mode" rules={[{ required: true, message: "请选择分配方式" }]}>
            <Radio.Group>
              <Space direction="vertical">
                <Radio value="random">随机分配</Radio>
                <Radio value="specified">指定健康管家</Radio>
              </Space>
            </Radio.Group>
          </Form.Item>
          {assignMode === "specified" ? (
            <Form.Item label="健康管家" name="assistant_id" rules={[{ required: true, message: "请选择健康管家" }]}>
              <Select
                loading={healthManagersLoading}
                options={healthManagers.map((item) => ({
                  label: `${item.name}${item.phone ? `（${item.phone}）` : ""}`,
                  value: item.id,
                }))}
                placeholder="请选择健康管家"
                showSearch
                optionFilterProp="label"
              />
            </Form.Item>
          ) : null}
        </Form>
      </Modal>

      <Modal
        title="用户详情"
        open={detailOpen}
        onCancel={() => setDetailOpen(false)}
        footer={null}
        width={860}
        loading={detailLoading}
      >
        {currentUser ? (
          <Space direction="vertical" size={18} style={{ width: "100%" }}>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="用户" span={2}>
                <Space>
                  <Avatar src={currentUser.avatar_url || undefined}>{currentUser.display_name.slice(0, 1)}</Avatar>
                  {currentUser.display_name}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="手机号">{currentUser.phone || "-"}</Descriptions.Item>
              <Descriptions.Item label="OpenID">{currentUser.openid || "-"}</Descriptions.Item>
              <Descriptions.Item label="性别">{currentUser.gender_label || "-"}</Descriptions.Item>
              <Descriptions.Item label="出生日期">{currentUser.birthday || "-"}</Descriptions.Item>
              <Descriptions.Item label="年龄">{currentUser.age === null ? "-" : `${currentUser.age}岁`}</Descriptions.Item>
              <Descriptions.Item label="最近登录">{formatTime(currentUser.last_login_at)}</Descriptions.Item>
              <Descriptions.Item label="会员状态">
                {currentUser.membership_status === "active" ? "会员" : "普通用户"}
              </Descriptions.Item>
              <Descriptions.Item label="会员有效期">{currentUser.membership_expires_at || "-"}</Descriptions.Item>
              <Descriptions.Item label="健康管家">
                {currentUser.health_manager_name
                  ? `${currentUser.health_manager_name}${currentUser.health_manager_phone ? `（${currentUser.health_manager_phone}）` : ""}`
                  : "-"}
              </Descriptions.Item>
            </Descriptions>

            <Typography.Title level={5}>既往病史</Typography.Title>
            <RecordList items={currentUser.archive?.medical_histories} />

            <Typography.Title level={5}>用药记录</Typography.Title>
            <RecordList items={currentUser.archive?.medication_records} />
          </Space>
        ) : null}
      </Modal>
    </>
  );
}
