"use client";

import {
  Button,
  Card,
  Flex,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  Typography,
  Upload,
  message,
  type TablePaginationConfig,
  type TableProps,
} from "antd";
import { useEffect, useState } from "react";

import type { AssistantType, StaffItem, StaffListParams, StaffPayload, StaffStatus } from "@/lib/api";
import "./staff.css";

type StaffFormValues = {
  avatar_url?: string;
  name: string;
  phone: string;
  status: StaffStatus;
  assistant_type?: AssistantType;
  remark?: string;
};

type StaffManagementPageProps = {
  title: string;
  createText: string;
  entityName: string;
  getList: (params?: StaffListParams) => Promise<{
    items: StaffItem[];
    pagination: { page: number; page_size: number; total: number };
  }>;
  createItem: (data: StaffPayload) => Promise<StaffItem>;
  updateItem: (id: number, data: StaffPayload) => Promise<StaffItem>;
  deleteItem: (id: number) => Promise<null>;
  staffTypeOptions?: { label: string; value: AssistantType }[];
};

const statusOptions = [
  { label: "启用", value: "active" },
  { label: "禁用", value: "inactive" },
];

function fileToBase64(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

function toPayload(values: StaffFormValues): StaffPayload {
  const payload: StaffPayload = {
    avatar_url: values.avatar_url ?? "",
    name: values.name.trim(),
    phone: values.phone.trim(),
    status: values.status,
    remark: values.remark?.trim() ?? "",
  };
  if (values.assistant_type) {
    payload.assistant_type = values.assistant_type;
  }
  return payload;
}

function formatDate(value: string | null) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "-";
  }
  return date.toLocaleString("zh-CN", { hour12: false });
}

export function StaffManagementPage({
  title,
  createText,
  entityName,
  getList,
  createItem,
  updateItem,
  deleteItem,
  staffTypeOptions,
}: StaffManagementPageProps) {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<StaffListParams>();
  const [staffForm] = Form.useForm<StaffFormValues>();
  const [items, setItems] = useState<StaffItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingItem, setEditingItem] = useState<StaffItem | null>(null);
  const [avatarUrl, setAvatarUrl] = useState("");
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const loadItems = async (
    nextPage = pagination.current,
    nextPageSize = pagination.pageSize,
  ) => {
    setLoading(true);
    try {
      const result = await getList({
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
      messageApi.error(error instanceof Error ? error.message : `加载${entityName}失败`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadItems(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreateModal = () => {
    setEditingItem(null);
    staffForm.setFieldsValue({
      avatar_url: "",
      name: "",
      phone: "",
      status: "active",
      assistant_type: staffTypeOptions?.[0]?.value,
      remark: "",
    });
    setAvatarUrl("");
    setModalOpen(true);
  };

  const openEditModal = (item: StaffItem) => {
    setEditingItem(item);
    staffForm.setFieldsValue({
      avatar_url: item.avatar_url ?? "",
      name: item.name,
      phone: item.phone,
      status: item.status,
      assistant_type: item.assistant_type ?? staffTypeOptions?.[0]?.value,
      remark: item.remark,
    });
    setAvatarUrl(item.avatar_url ?? "");
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await staffForm.validateFields();
    setSaving(true);
    try {
      if (editingItem) {
        await updateItem(editingItem.id, toPayload(values));
        messageApi.success("保存成功");
      } else {
        await createItem(toPayload(values));
        messageApi.success("创建成功");
      }
      setModalOpen(false);
      await loadItems(editingItem ? pagination.current : 1, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (item: StaffItem) => {
    try {
      await deleteItem(item.id);
      messageApi.success("删除成功");
      await loadItems(pagination.current, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "删除失败");
    }
  };

  const handleAvatarUpload = async (file: File) => {
    const base64 = await fileToBase64(file);
    staffForm.setFieldValue("avatar_url", base64);
    setAvatarUrl(base64);
  };

  const handleRemoveAvatar = () => {
    staffForm.setFieldValue("avatar_url", "");
    setAvatarUrl("");
  };

  const columns: TableProps<StaffItem>["columns"] = [
    {
      title: "头像",
      dataIndex: "avatar_url",
      key: "avatar_url",
      width: 90,
      render: (value: string) =>
        value ? <img alt={`${entityName}头像`} className="staff-page__avatar" src={value} /> : "-",
    },
    { title: "姓名", dataIndex: "name", key: "name", width: 140 },
    { title: "手机号", dataIndex: "phone", key: "phone", width: 160 },
    ...(staffTypeOptions
      ? [
          {
            title: "助理类型",
            dataIndex: "assistant_type",
            key: "assistant_type",
            width: 130,
            render: (value: AssistantType) =>
              staffTypeOptions.find((option) => option.value === value)?.label ?? "-",
          },
        ]
      : []),
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: (value: StaffStatus) => (
        <Tag color={value === "active" ? "green" : "default"}>
          {value === "active" ? "启用" : "禁用"}
        </Tag>
      ),
    },
    { title: "备注", dataIndex: "remark", key: "remark", ellipsis: true },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 180,
      render: formatDate,
    },
    {
      title: "操作",
      key: "action",
      fixed: "right",
      width: 150,
      render: (_, record) => (
        <Space size={4}>
          <Button type="link" onClick={() => openEditModal(record)}>
            编辑
          </Button>
          <Popconfirm
            title={`确认删除该${entityName}？`}
            okText="删除"
            cancelText="取消"
            onConfirm={() => void handleDelete(record)}
          >
            <Button danger type="link">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleTableChange = (nextPagination: TablePaginationConfig) => {
    void loadItems(nextPagination.current, nextPagination.pageSize);
  };

  return (
    <>
      {contextHolder}
      <div className="staff-page">
        <Flex align="center" justify="space-between" className="staff-page__heading">
          <Typography.Title level={4}>{title}</Typography.Title>
          <Button type="primary" onClick={openCreateModal}>
            {createText}
          </Button>
        </Flex>
        <Card className="staff-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="关键词">
              <Input allowClear placeholder={`搜索${entityName}姓名、手机号或备注`} />
            </Form.Item>
            <Form.Item name="status" label="状态">
              <Select allowClear options={statusOptions} placeholder="全部" style={{ width: 140 }} />
            </Form.Item>
            {staffTypeOptions ? (
              <Form.Item name="assistant_type" label="助理类型">
                <Select allowClear options={staffTypeOptions} placeholder="全部" style={{ width: 160 }} />
              </Form.Item>
            ) : null}
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadItems(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadItems(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
        <Card className="staff-page__table">
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
            scroll={{ x: 980 }}
          />
        </Card>
      </div>
      <Modal
        cancelText="取消"
        confirmLoading={saving}
        destroyOnHidden
        forceRender
        okText="保存"
        onCancel={() => setModalOpen(false)}
        onOk={() => void handleSave()}
        open={modalOpen}
        title={editingItem ? `编辑${entityName}` : `新增${entityName}`}
        width={720}
      >
        <Form form={staffForm} layout="vertical" preserve={false}>
          <Flex gap={16}>
            <Form.Item
              className="staff-page__form-item"
              label="姓名"
              name="name"
              rules={[{ required: true, message: `请输入${entityName}姓名` }]}
            >
              <Input maxLength={50} placeholder={`请输入${entityName}姓名`} showCount />
            </Form.Item>
            <Form.Item
              className="staff-page__form-item"
              label="手机号"
              name="phone"
              rules={[{ required: true, message: "请输入手机号" }]}
            >
              <Input maxLength={20} placeholder="请输入手机号" />
            </Form.Item>
            <Form.Item
              className="staff-page__form-item"
              label="状态"
              name="status"
              rules={[{ required: true, message: "请选择状态" }]}
            >
              <Select options={statusOptions} />
            </Form.Item>
            {staffTypeOptions ? (
              <Form.Item
                className="staff-page__form-item"
                label="助理类型"
                name="assistant_type"
                rules={[{ required: true, message: "请选择助理类型" }]}
              >
                <Select options={staffTypeOptions} />
              </Form.Item>
            ) : null}
          </Flex>
          <Form.Item label="头像">
            <Space align="start" size={16}>
              <Upload
                accept="image/*"
                beforeUpload={(file) => {
                  void handleAvatarUpload(file);
                  return Upload.LIST_IGNORE;
                }}
                maxCount={1}
                showUploadList={false}
              >
                <Button>上传头像</Button>
              </Upload>
              {avatarUrl ? (
                <Space align="start">
                  <img alt={`${entityName}头像预览`} className="staff-page__avatar-preview" src={avatarUrl} />
                  <Button danger type="link" onClick={handleRemoveAvatar}>
                    移除
                  </Button>
                </Space>
              ) : null}
            </Space>
          </Form.Item>
          <Form.Item hidden name="avatar_url">
            <Input />
          </Form.Item>
          <Form.Item label="备注" name="remark">
            <Input.TextArea maxLength={255} rows={4} showCount />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
