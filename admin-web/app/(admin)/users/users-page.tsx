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
  Space,
  Table,
  Tag,
  Typography,
  message,
  type TablePaginationConfig,
  type TableProps,
} from "antd";
import { useEffect, useState } from "react";

import {
  getMiniappUser,
  getMiniappUserList,
  type AdminMiniappHealthRecord,
  type AdminMiniappUser,
} from "@/lib/api";

type FilterValues = {
  keyword?: string;
};

function formatDateTime(value: string | null) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "-";
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
  const [items, setItems] = useState<AdminMiniappUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<AdminMiniappUser | null>(null);
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
      title: "操作",
      key: "action",
      fixed: "right",
      width: 110,
      render: (_, record) => (
        <Button type="link" onClick={() => void openDetail(record)}>
          查看详情
        </Button>
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
              <Descriptions.Item label="性别">{currentUser.gender_label || "-"}</Descriptions.Item>
              <Descriptions.Item label="出生日期">{currentUser.birthday || "-"}</Descriptions.Item>
              <Descriptions.Item label="年龄">{currentUser.age === null ? "-" : `${currentUser.age}岁`}</Descriptions.Item>
              <Descriptions.Item label="会员状态">
                {currentUser.membership_status === "active" ? "会员" : "普通用户"}
              </Descriptions.Item>
              <Descriptions.Item label="会员有效期">{currentUser.membership_expires_at || "-"}</Descriptions.Item>
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
