"use client";

import {
  Button,
  Card,
  Flex,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Space,
  Table,
  Typography,
  message,
  type TablePaginationConfig,
  type TableProps,
} from "antd";
import { useEffect, useState } from "react";

import {
  createDepartment,
  deleteDepartment,
  getDepartmentList,
  updateDepartment,
  type DepartmentItem,
  type DepartmentPayload,
} from "@/lib/api";

type FilterValues = { keyword?: string };

type DepartmentFormValues = {
  name: string;
  description?: string;
  sort_order?: number;
};

function toPayload(values: DepartmentFormValues): DepartmentPayload {
  return {
    name: values.name.trim(),
    description: values.description?.trim() ?? "",
    sort_order: values.sort_order ?? 0,
  };
}

export function DepartmentsPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [departmentForm] = Form.useForm<DepartmentFormValues>();
  const [items, setItems] = useState<DepartmentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState<DepartmentItem | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const loadDepartments = async (
    nextPage = pagination.current,
    nextPageSize = pagination.pageSize,
  ) => {
    setLoading(true);
    try {
      const result = await getDepartmentList({
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
      messageApi.error(error instanceof Error ? error.message : "加载科室失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDepartments(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreateModal = () => {
    setEditingDepartment(null);
    departmentForm.setFieldsValue({ name: "", description: "", sort_order: 0 });
    setModalOpen(true);
  };

  const openEditModal = (department: DepartmentItem) => {
    setEditingDepartment(department);
    departmentForm.setFieldsValue({
      name: department.name,
      description: department.description,
      sort_order: department.sort_order,
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await departmentForm.validateFields();
    setSaving(true);
    try {
      if (editingDepartment) {
        await updateDepartment(editingDepartment.id, toPayload(values));
        messageApi.success("保存成功");
      } else {
        await createDepartment(toPayload(values));
        messageApi.success("创建成功");
      }
      setModalOpen(false);
      await loadDepartments(editingDepartment ? pagination.current : 1, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (department: DepartmentItem) => {
    try {
      await deleteDepartment(department.id);
      messageApi.success("删除成功");
      await loadDepartments(pagination.current, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "删除失败");
    }
  };

  const columns: TableProps<DepartmentItem>["columns"] = [
    { title: "科室名称", dataIndex: "name", key: "name", ellipsis: true },
    { title: "科室简介", dataIndex: "description", key: "description", ellipsis: true },
    { title: "排序", dataIndex: "sort_order", key: "sort_order", width: 90 },
    {
      title: "更新时间",
      dataIndex: "updated_at",
      key: "updated_at",
      width: 180,
      render: (value: string | null) => (value ? new Date(value).toLocaleString() : "-"),
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
            title="确认删除该科室？"
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
    void loadDepartments(nextPagination.current, nextPagination.pageSize);
  };

  return (
    <>
      {contextHolder}
      <div className="departments-page">
        <Flex align="center" justify="space-between" className="departments-page__heading">
          <Typography.Title level={4}>科室管理</Typography.Title>
          <Button type="primary" onClick={openCreateModal}>
            新增科室
          </Button>
        </Flex>
        <Card className="departments-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="科室名称">
              <Input allowClear placeholder="请输入科室名称" />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadDepartments(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadDepartments(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
        <Card className="departments-page__table">
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
            scroll={{ x: 780 }}
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
        title={editingDepartment ? "编辑科室" : "新增科室"}
      >
        <Form form={departmentForm} layout="vertical" preserve={false}>
          <Form.Item
            label="科室名称"
            name="name"
            rules={[{ required: true, message: "请输入科室名称" }]}
          >
            <Input maxLength={50} placeholder="例如：内科" showCount />
          </Form.Item>
          <Form.Item label="科室简介" name="description">
            <Input.TextArea maxLength={255} rows={3} showCount />
          </Form.Item>
          <Form.Item label="排序" name="sort_order">
            <InputNumber precision={0} style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
