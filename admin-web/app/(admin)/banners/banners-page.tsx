"use client";

import {
  Button,
  Card,
  Flex,
  Form,
  Input,
  Modal,
  Popconfirm,
  Space,
  Table,
  Typography,
  Upload,
  message,
  type TablePaginationConfig,
  type TableProps,
} from "antd";
import { useEffect, useState } from "react";

import {
  createBanner,
  deleteBanner,
  getBannerList,
  updateBanner,
  type BannerItem,
  type BannerPayload,
} from "@/lib/api";

type FilterValues = {
  keyword?: string;
};

type BannerFormValues = {
  image_url?: string;
  title: string;
  description?: string;
};

function fileToBase64(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

function toPayload(values: BannerFormValues): BannerPayload {
  return {
    image_url: values.image_url ?? "",
    title: values.title.trim(),
    description: values.description?.trim() ?? "",
  };
}

export function BannersPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [bannerForm] = Form.useForm<BannerFormValues>();
  const [items, setItems] = useState<BannerItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingBanner, setEditingBanner] = useState<BannerItem | null>(null);
  const [imageUrl, setImageUrl] = useState("");
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  const loadBanners = async (
    nextPage = pagination.current,
    nextPageSize = pagination.pageSize,
  ) => {
    setLoading(true);
    try {
      const filters = filterForm.getFieldsValue();
      const result = await getBannerList({
        ...filters,
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
      messageApi.error(error instanceof Error ? error.message : "加载 Banner 失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadBanners(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreateModal = () => {
    setEditingBanner(null);
    bannerForm.setFieldsValue({
      image_url: "",
      title: "",
      description: "",
    });
    setImageUrl("");
    setModalOpen(true);
  };

  const openEditModal = (banner: BannerItem) => {
    setEditingBanner(banner);
    bannerForm.setFieldsValue({
      image_url: banner.image_url ?? "",
      title: banner.title,
      description: banner.description ?? "",
    });
    setImageUrl(banner.image_url ?? "");
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await bannerForm.validateFields();
    const payload = toPayload(values);
    setSaving(true);
    try {
      if (editingBanner) {
        await updateBanner(editingBanner.id, payload);
        messageApi.success("保存成功");
      } else {
        await createBanner(payload);
        messageApi.success("创建成功");
      }
      setModalOpen(false);
      await loadBanners(editingBanner ? pagination.current : 1, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (banner: BannerItem) => {
    try {
      await deleteBanner(banner.id);
      messageApi.success("删除成功");
      const nextPage =
        items.length === 1 && pagination.current > 1
          ? pagination.current - 1
          : pagination.current;
      await loadBanners(nextPage, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "删除失败");
    }
  };

  const handleTableChange = (nextPagination: TablePaginationConfig) => {
    void loadBanners(nextPagination.current, nextPagination.pageSize);
  };

  const handleImageUpload = async (file: File) => {
    const base64 = await fileToBase64(file);
    bannerForm.setFieldValue("image_url", base64);
    setImageUrl(base64);
  };

  const handleRemoveImage = () => {
    bannerForm.setFieldValue("image_url", "");
    setImageUrl("");
  };

  const columns: TableProps<BannerItem>["columns"] = [
    {
      title: "图片",
      dataIndex: "image_url",
      key: "image_url",
      width: 190,
      render: (value: string) =>
        value ? <img alt="Banner 图片" className="banners-page__preview" src={value} /> : "-",
    },
    {
      title: "标题",
      dataIndex: "title",
      key: "title",
      ellipsis: true,
    },
    {
      title: "描述",
      dataIndex: "description",
      key: "description",
      ellipsis: true,
    },
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
            title="确认删除该 Banner？"
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

  return (
    <>
      {contextHolder}
      <div className="banners-page">
        <Flex align="center" justify="space-between" className="banners-page__heading">
          <Typography.Title level={4}>Banner 管理</Typography.Title>
          <Button type="primary" onClick={openCreateModal}>
            新增 Banner
          </Button>
        </Flex>

        <Card className="banners-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="标题">
              <Input allowClear placeholder="请输入 Banner 标题" />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadBanners(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadBanners(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>

        <Card className="banners-page__table">
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
            scroll={{ x: 900 }}
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
        title={editingBanner ? "编辑 Banner" : "新增 Banner"}
        width={720}
      >
        <Form className="banners-page__form" form={bannerForm} layout="vertical" preserve={false}>
          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: "请输入 Banner 标题" }]}
          >
            <Input maxLength={80} placeholder="请输入 Banner 标题" showCount />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea maxLength={255} placeholder="请输入 Banner 描述" rows={3} showCount />
          </Form.Item>
          <Form.Item label="图片">
            <Space align="start" size={16}>
              <Upload
                accept="image/*"
                beforeUpload={(file) => {
                  void handleImageUpload(file);
                  return Upload.LIST_IGNORE;
                }}
                maxCount={1}
                showUploadList={false}
              >
                <Button>上传图片</Button>
              </Upload>
              {imageUrl ? (
                <Space align="start">
                  <img alt="Banner 预览" className="banners-page__preview" src={imageUrl} />
                  <Button danger type="link" onClick={handleRemoveImage}>
                    移除
                  </Button>
                </Space>
              ) : null}
            </Space>
          </Form.Item>
          <Form.Item hidden name="image_url">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
