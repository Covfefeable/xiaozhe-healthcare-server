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
  Modal,
  Radio,
  Space,
  Select,
  Table,
  Tag,
  Typography,
  message,
  type TablePaginationConfig,
  type TableProps,
} from "antd";
import { useEffect, useState } from "react";

import {
  assignMiniappUserHealthManager,
  getAssistantList,
  getMiniappUser,
  getMiniappUserList,
  renewMiniappUserMembership,
  type StaffItem,
  type AdminMiniappHealthRecord,
  type AdminMiniappUser,
} from "@/lib/api";

type FilterValues = {
  keyword?: string;
};

function formatDateTime(value: string | null) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "-";
}

function toDatetimeLocalValue(value?: string | null) {
  const date = value ? new Date(value) : new Date();
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - offset * 60 * 1000);
  return localDate.toISOString().slice(0, 16);
}

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

export function UsersPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [renewForm] = Form.useForm<{ membership_expires_at: string }>();
  const [assignForm] = Form.useForm<{ mode: "random" | "specified"; assistant_id?: number }>();
  const [items, setItems] = useState<AdminMiniappUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [renewOpen, setRenewOpen] = useState(false);
  const [renewLoading, setRenewLoading] = useState(false);
  const [assignOpen, setAssignOpen] = useState(false);
  const [assignLoading, setAssignLoading] = useState(false);
  const [healthManagers, setHealthManagers] = useState<StaffItem[]>([]);
  const [healthManagersLoading, setHealthManagersLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState<AdminMiniappUser | null>(null);
  const [renewUser, setRenewUser] = useState<AdminMiniappUser | null>(null);
  const [assignUser, setAssignUser] = useState<AdminMiniappUser | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const loadUsers = async (nextPage = pagination.current, nextPageSize = pagination.pageSize) => {
    setLoading(true);
    try {
      const result = await getMiniappUserList({
        ...filterForm.getFieldsValue(),
        page: nextPage,
        page_size: nextPageSize,
      });
      setItems(result.items);
      setPagination({
        current: result.pagination.page,
        pageSize: result.pagination.page_size,
        total: result.pagination.total,
      });
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "用户加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadUsers(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openDetail = async (user: AdminMiniappUser) => {
    setCurrentUser(user);
    setDetailOpen(true);
    setDetailLoading(true);
    try {
      setCurrentUser(await getMiniappUser(user.id));
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "用户详情加载失败");
    } finally {
      setDetailLoading(false);
    }
  };

  const openRenewModal = (user: AdminMiniappUser) => {
    setRenewUser(user);
    renewForm.setFieldsValue({
      membership_expires_at: toDatetimeLocalValue(user.membership_expires_at_datetime),
    });
    setRenewOpen(true);
  };

  const loadHealthManagers = async () => {
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

  const openAssignModal = async (user: AdminMiniappUser) => {
    setAssignUser(user);
    assignForm.setFieldsValue({
      mode: user.health_manager_id ? "specified" : "random",
      assistant_id: user.health_manager_id ?? undefined,
    });
    setAssignOpen(true);
    await loadHealthManagers();
  };

  const handleRenew = async () => {
    if (!renewUser) {
      return;
    }
    const values = await renewForm.validateFields();
    setRenewLoading(true);
    try {
      const updatedUser = await renewMiniappUserMembership(
        renewUser.id,
        values.membership_expires_at,
      );
      messageApi.success("续期成功");
      setRenewOpen(false);
      setRenewUser(null);
      setCurrentUser((value) => (value?.id === updatedUser.id ? updatedUser : value));
      await loadUsers(pagination.current, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "续期失败");
    } finally {
      setRenewLoading(false);
    }
  };

  const assignMode = Form.useWatch("mode", assignForm) ?? "random";

  const handleAssignHealthManager = async () => {
    if (!assignUser) {
      return;
    }
    const values = await assignForm.validateFields();
    setAssignLoading(true);
    try {
      const updatedUser = await assignMiniappUserHealthManager(assignUser.id, values);
      messageApi.success("分配成功");
      setAssignOpen(false);
      setAssignUser(null);
      setCurrentUser((value) => (value?.id === updatedUser.id ? updatedUser : value));
      await loadUsers(pagination.current, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "分配失败");
    } finally {
      setAssignLoading(false);
    }
  };

  const columns: TableProps<AdminMiniappUser>["columns"] = [
    {
      title: "用户",
      dataIndex: "display_name",
      key: "display_name",
      render: (_, record) => (
        <Space>
          <Avatar src={record.avatar_url || undefined}>{record.display_name.slice(0, 1)}</Avatar>
          <span>{record.display_name}</span>
        </Space>
      ),
    },
    { title: "手机号", dataIndex: "phone", key: "phone", width: 140, render: (value: string) => value || "-" },
    { title: "性别", dataIndex: "gender_label", key: "gender_label", width: 90 },
    { title: "年龄", dataIndex: "age", key: "age", width: 90, render: (value: number | null) => (value === null ? "-" : `${value}岁`) },
    {
      title: "会员",
      dataIndex: "membership_status",
      key: "membership_status",
      width: 110,
      render: (value: string) => (value === "active" ? <Tag color="success">会员</Tag> : <Tag>普通用户</Tag>),
    },
    { title: "最近登录", dataIndex: "last_login_at", key: "last_login_at", width: 180, render: formatDateTime },
    { title: "注册时间", dataIndex: "created_at", key: "created_at", width: 180, render: formatDateTime },
    {
      title: "健康管家",
      dataIndex: "health_manager_name",
      key: "health_manager_name",
      width: 180,
      render: (_: string, record) => record.health_manager_name || "-",
    },
    {
      title: "操作",
      key: "action",
      fixed: "right",
      width: 240,
      render: (_, record) => (
        <Space size={4}>
          <Button type="link" onClick={() => void openDetail(record)}>
            查看详情
          </Button>
          <Button type="link" onClick={() => void openAssignModal(record)}>
            分配健康管家
          </Button>
          <Button type="link" onClick={() => openRenewModal(record)}>
            续期
          </Button>
        </Space>
      ),
    },
  ];

  const handleTableChange = (nextPagination: TablePaginationConfig) => {
    void loadUsers(nextPagination.current, nextPagination.pageSize);
  };

  return (
    <>
      {contextHolder}
      <div className="users-page">
        <Card className="users-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="关键词">
              <Input allowClear placeholder="姓名、昵称或手机号" />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadUsers(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadUsers(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>

        <Card className="users-page__table">
          <Table
            columns={columns}
            dataSource={items}
            loading={loading}
            onChange={handleTableChange}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条`,
            }}
            rowKey="id"
            scroll={{ x: 1120 }}
          />
        </Card>
      </div>

      <Modal
        title="用户详情"
        open={detailOpen}
        onCancel={() => setDetailOpen(false)}
        footer={
          currentUser ? (
            <Button type="primary" onClick={() => openRenewModal(currentUser)}>
              续期
            </Button>
          ) : null
        }
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
              <Descriptions.Item label="最近登录">{formatDateTime(currentUser.last_login_at)}</Descriptions.Item>
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

      <Modal
        title="会员续期"
        open={renewOpen}
        confirmLoading={renewLoading}
        okText="保存"
        cancelText="取消"
        onCancel={() => setRenewOpen(false)}
        onOk={() => void handleRenew()}
      >
        <Form form={renewForm} layout="vertical">
          <Form.Item label="用户">
            {renewUser ? `${renewUser.display_name}（${renewUser.phone || "无手机号"}）` : "-"}
          </Form.Item>
          <Form.Item
            label="会员有效期"
            name="membership_expires_at"
            rules={[{ required: true, message: "请选择会员有效期" }]}
          >
            <Input type="datetime-local" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="分配健康管家"
        open={assignOpen}
        confirmLoading={assignLoading}
        okText="保存"
        cancelText="取消"
        onCancel={() => setAssignOpen(false)}
        onOk={() => void handleAssignHealthManager()}
      >
        <Form form={assignForm} layout="vertical">
          <Form.Item label="用户">
            {assignUser ? `${assignUser.display_name}（${assignUser.phone || "无手机号"}）` : "-"}
          </Form.Item>
          <Form.Item label="分配方式" name="mode" initialValue="random" rules={[{ required: true, message: "请选择分配方式" }]}>
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
                placeholder="请选择健康管家"
                options={healthManagers.map((item) => ({
                  label: `${item.name}${item.phone ? `（${item.phone}）` : ""}`,
                  value: item.id,
                }))}
                showSearch
                optionFilterProp="label"
              />
            </Form.Item>
          ) : null}
        </Form>
      </Modal>
    </>
  );
}
