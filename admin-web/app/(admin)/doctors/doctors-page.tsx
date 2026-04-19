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

import {
  createDoctor,
  deleteDoctor,
  getDepartmentList,
  getDoctorList,
  updateDoctor,
  type DepartmentItem,
  type DoctorItem,
  type DoctorPayload,
} from "@/lib/api";

type FilterValues = {
  keyword?: string;
  department_id?: number;
};

type DoctorFormValues = {
  department_id: number;
  avatar_url?: string;
  name: string;
  phone: string;
  title?: string;
  hospital?: string;
  summary?: string;
  specialty_tags_text?: string;
  introduction?: string;
  sort_order?: number;
};

function fileToBase64(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

function parseTags(value?: string) {
  return (value || "")
    .split(/[，,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function toPayload(values: DoctorFormValues): DoctorPayload {
  return {
    department_id: values.department_id,
    avatar_url: values.avatar_url ?? "",
    name: values.name.trim(),
    phone: values.phone.trim(),
    title: values.title?.trim() ?? "",
    hospital: values.hospital?.trim() ?? "",
    summary: values.summary?.trim() ?? "",
    specialty_tags: parseTags(values.specialty_tags_text),
    introduction: values.introduction ?? "",
    sort_order: values.sort_order ?? 0,
  };
}

export function DoctorsPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [doctorForm] = Form.useForm<DoctorFormValues>();
  const [departments, setDepartments] = useState<DepartmentItem[]>([]);
  const [items, setItems] = useState<DoctorItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState<DoctorItem | null>(null);
  const [avatarUrl, setAvatarUrl] = useState("");
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const departmentOptions = departments.map((item) => ({
    label: item.name,
    value: item.id,
  }));

  const loadDepartments = async () => {
    try {
      const result = await getDepartmentList({ page: 1, page_size: 100 });
      setDepartments(result.items);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "加载科室失败");
    }
  };

  const loadDoctors = async (
    nextPage = pagination.current,
    nextPageSize = pagination.pageSize,
  ) => {
    setLoading(true);
    try {
      const result = await getDoctorList({
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
      messageApi.error(error instanceof Error ? error.message : "加载医生失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDepartments();
    void loadDoctors(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreateModal = () => {
    setEditingDoctor(null);
    doctorForm.setFieldsValue({
      department_id: departments[0]?.id,
      avatar_url: "",
      name: "",
      phone: "",
      title: "",
      hospital: "",
      summary: "",
      specialty_tags_text: "",
      introduction: "",
      sort_order: 0,
    });
    setAvatarUrl("");
    setModalOpen(true);
  };

  const openEditModal = (doctor: DoctorItem) => {
    setEditingDoctor(doctor);
    doctorForm.setFieldsValue({
      department_id: doctor.department_id,
      avatar_url: doctor.avatar_url ?? "",
      name: doctor.name,
      phone: doctor.phone,
      title: doctor.title,
      hospital: doctor.hospital,
      summary: doctor.summary,
      specialty_tags_text: doctor.specialty_tags.join("，"),
      introduction: doctor.introduction,
      sort_order: doctor.sort_order,
    });
    setAvatarUrl(doctor.avatar_url ?? "");
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await doctorForm.validateFields();
    setSaving(true);
    try {
      if (editingDoctor) {
        await updateDoctor(editingDoctor.id, toPayload(values));
        messageApi.success("保存成功");
      } else {
        await createDoctor(toPayload(values));
        messageApi.success("创建成功");
      }
      setModalOpen(false);
      await loadDoctors(editingDoctor ? pagination.current : 1, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (doctor: DoctorItem) => {
    try {
      await deleteDoctor(doctor.id);
      messageApi.success("删除成功");
      await loadDoctors(pagination.current, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "删除失败");
    }
  };

  const handleAvatarUpload = async (file: File) => {
    const base64 = await fileToBase64(file);
    doctorForm.setFieldValue("avatar_url", base64);
    setAvatarUrl(base64);
  };

  const handleRemoveAvatar = () => {
    doctorForm.setFieldValue("avatar_url", "");
    setAvatarUrl("");
  };

  const columns: TableProps<DoctorItem>["columns"] = [
    {
      title: "头像",
      dataIndex: "avatar_url",
      key: "avatar_url",
      width: 90,
      render: (value: string) =>
        value ? <img alt="医生头像" className="doctors-page__avatar" src={value} /> : "-",
    },
    { title: "姓名", dataIndex: "name", key: "name", width: 110 },
    { title: "手机号", dataIndex: "phone", key: "phone", width: 140 },
    { title: "科室", dataIndex: "department_name", key: "department_name", width: 120 },
    { title: "职称", dataIndex: "title", key: "title", width: 120 },
    { title: "医院", dataIndex: "hospital", key: "hospital", ellipsis: true },
    {
      title: "擅长方向",
      dataIndex: "specialty_tags",
      key: "specialty_tags",
      width: 220,
      render: (tags: string[]) => (
        <Space size={[4, 4]} wrap>
          {(tags || []).map((tag) => (
            <Tag key={tag}>{tag}</Tag>
          ))}
        </Space>
      ),
    },
    { title: "排序", dataIndex: "sort_order", key: "sort_order", width: 80 },
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
            title="确认删除该医生？"
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
    void loadDoctors(nextPagination.current, nextPagination.pageSize);
  };

  return (
    <>
      {contextHolder}
      <div className="doctors-page">
        <Flex align="center" justify="space-between" className="doctors-page__heading">
          <Typography.Title level={4}>医生管理</Typography.Title>
          <Button type="primary" onClick={openCreateModal}>
            新增医生
          </Button>
        </Flex>
        <Card className="doctors-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="关键词">
              <Input allowClear placeholder="医生、科室、医院或擅长方向" />
            </Form.Item>
            <Form.Item name="department_id" label="科室">
              <Select allowClear options={departmentOptions} placeholder="全部" style={{ width: 160 }} />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadDoctors(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadDoctors(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
        <Card className="doctors-page__table">
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
            scroll={{ x: 1250 }}
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
        title={editingDoctor ? "编辑医生" : "新增医生"}
        width={860}
      >
        <Form form={doctorForm} layout="vertical" preserve={false}>
          <Flex gap={16}>
            <Form.Item
              className="doctors-page__form-item"
              label="所属科室"
              name="department_id"
              rules={[{ required: true, message: "请选择所属科室" }]}
            >
              <Select options={departmentOptions} placeholder="请选择科室" />
            </Form.Item>
            <Form.Item
              className="doctors-page__form-item"
              label="医生姓名"
              name="name"
              rules={[{ required: true, message: "请输入医生姓名" }]}
            >
              <Input maxLength={50} placeholder="例如：张伟" showCount />
            </Form.Item>
            <Form.Item
              className="doctors-page__form-item"
              label="手机号"
              name="phone"
              rules={[{ required: true, message: "请输入手机号" }]}
            >
              <Input maxLength={20} placeholder="请输入手机号" />
            </Form.Item>
          </Flex>
          <Flex gap={16}>
            <Form.Item className="doctors-page__form-item" label="职称" name="title">
              <Input maxLength={50} placeholder="例如：主治医师" showCount />
            </Form.Item>
            <Form.Item className="doctors-page__form-item" label="医院" name="hospital">
              <Input maxLength={100} placeholder="例如：上海市第六人民医院" showCount />
            </Form.Item>
            <Form.Item className="doctors-page__form-item" label="排序" name="sort_order">
              <InputNumber precision={0} style={{ width: "100%" }} />
            </Form.Item>
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
                  <img alt="医生头像预览" className="doctors-page__avatar-preview" src={avatarUrl} />
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
          <Form.Item label="列表简介" name="summary">
            <Input.TextArea maxLength={120} rows={2} showCount />
          </Form.Item>
          <Form.Item label="擅长方向" name="specialty_tags_text">
            <Input placeholder="多个标签用逗号分隔，例如：术后恢复，复查规划，创口管理" />
          </Form.Item>
          <Form.Item label="医生介绍" name="introduction">
            <Input.TextArea rows={5} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
