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
import MarkdownIt from "markdown-it";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import {
  createProduct,
  deleteProduct,
  getProducts,
  publishProduct,
  unpublishProduct,
  updateProduct,
  type Product,
  type ProductPayload,
  type ProductStatus,
  type ProductType,
} from "@/lib/api";

const MdEditor = dynamic(() => import("react-markdown-editor-lite"), { ssr: false });
const mdParser = new MarkdownIt({
  breaks: true,
  html: false,
  linkify: true,
});

type FilterValues = {
  keyword?: string;
  validity_days?: number;
  status?: ProductStatus;
  product_type?: ProductType;
};

type ProductFormValues = {
  name: string;
  summary?: string;
  price_yuan: number;
  validity_days?: number;
  product_type: ProductType;
  image_url?: string;
  detail_markdown?: string;
  sort_order?: number;
};

const validityOptions = [
  { label: "30 天", value: 30 },
  { label: "90 天", value: 90 },
  { label: "180 天", value: 180 },
  { label: "365 天", value: 365 },
];

const statusOptions: { label: string; value: ProductStatus }[] = [
  { label: "未上架", value: "draft" },
  { label: "已上架", value: "active" },
  { label: "已下架", value: "inactive" },
];

const statusMeta: Record<ProductStatus, { label: string; color: string }> = {
  draft: { label: "未上架", color: "default" },
  active: { label: "已上架", color: "success" },
  inactive: { label: "已下架", color: "warning" },
};

const productTypeOptions: { label: string; value: ProductType }[] = [
  { label: "会员", value: "membership" },
  { label: "其他", value: "other" },
];

const productTypeMeta: Record<ProductType, string> = {
  membership: "会员",
  other: "其他",
};

function yuanToCents(value: number) {
  return Math.round(Number(value || 0) * 100);
}

function centsToYuan(value: number) {
  return Number((value / 100).toFixed(2));
}

function toPayload(values: ProductFormValues): ProductPayload {
  return {
    name: values.name.trim(),
    summary: values.summary?.trim() ?? "",
    price_cents: yuanToCents(values.price_yuan),
    validity_days: values.product_type === "membership" ? values.validity_days ?? 0 : 0,
    product_type: values.product_type,
    image_url: values.image_url ?? "",
    detail_markdown: values.detail_markdown ?? "",
    sort_order: values.sort_order ?? 0,
  };
}

function fileToBase64(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

export function ProductsPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [productForm] = Form.useForm<ProductFormValues>();
  const selectedProductType = Form.useWatch("product_type", productForm);
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [markdownValue, setMarkdownValue] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  const loadProducts = async (
    nextPage = pagination.current,
    nextPageSize = pagination.pageSize,
  ) => {
    setLoading(true);
    try {
      const filters = filterForm.getFieldsValue();
      const result = await getProducts({
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
      messageApi.error(error instanceof Error ? error.message : "加载产品失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadProducts(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreateModal = () => {
    setEditingProduct(null);
    productForm.setFieldsValue({
      name: "",
      summary: "",
      price_yuan: 0,
      validity_days: undefined,
      product_type: "other",
      image_url: "",
      sort_order: 0,
    });
    setMarkdownValue("");
    setImageUrl("");
    setModalOpen(true);
  };

  const openEditModal = (product: Product) => {
    setEditingProduct(product);
    productForm.setFieldsValue({
      name: product.name,
      summary: product.summary ?? "",
      price_yuan: centsToYuan(product.price_cents),
      validity_days: product.product_type === "membership" ? product.validity_days : undefined,
      product_type: product.product_type,
      image_url: product.image_url ?? "",
      sort_order: product.sort_order,
    });
    setMarkdownValue(product.detail_markdown ?? "");
    setImageUrl(product.image_url ?? "");
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await productForm.validateFields();
    const payload = toPayload({ ...values, detail_markdown: markdownValue });
    setSaving(true);
    try {
      if (editingProduct) {
        await updateProduct(editingProduct.id, payload);
        messageApi.success("保存成功");
      } else {
        await createProduct(payload);
        messageApi.success("创建成功，当前为未上架状态");
      }
      setModalOpen(false);
      await loadProducts(editingProduct ? pagination.current : 1, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (product: Product) => {
    try {
      await deleteProduct(product.id);
      messageApi.success("删除成功");
      const nextPage =
        items.length === 1 && pagination.current > 1
          ? pagination.current - 1
          : pagination.current;
      await loadProducts(nextPage, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "删除失败");
    }
  };

  const handleStatusChange = async (product: Product) => {
    try {
      if (product.status === "active") {
        await unpublishProduct(product.id);
        messageApi.success("已下架");
      } else {
        await publishProduct(product.id);
        messageApi.success("已上架");
      }
      await loadProducts(pagination.current, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "状态更新失败");
    }
  };

  const columns: TableProps<Product>["columns"] = [
    {
      title: "产品图片",
      dataIndex: "image_url",
      key: "image_url",
      width: 110,
      render: (value: string) =>
        value ? (
          <img
            alt="产品图片"
            src={value}
            style={{
              width: 56,
              height: 56,
              borderRadius: 10,
              objectFit: "cover",
            }}
          />
        ) : (
          "-"
        ),
    },
    {
      title: "产品名称",
      dataIndex: "name",
      key: "name",
      ellipsis: true,
    },
    {
      title: "产品简介",
      dataIndex: "summary",
      key: "summary",
      ellipsis: true,
    },
    {
      title: "产品类型",
      dataIndex: "product_type",
      key: "product_type",
      width: 110,
      render: (value: ProductType) => productTypeMeta[value] ?? value,
    },
    {
      title: "价格",
      dataIndex: "price",
      key: "price",
      width: 120,
      render: (value: string) => `¥${value}`,
    },
    {
      title: "有效期",
      dataIndex: "validity_days",
      key: "validity_days",
      width: 110,
      render: (value: number, record) => (record.product_type === "membership" ? `${value} 天` : "-"),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 110,
      render: (value: ProductStatus) => (
        <Tag color={statusMeta[value].color}>{statusMeta[value].label}</Tag>
      ),
    },
    {
      title: "排序",
      dataIndex: "sort_order",
      key: "sort_order",
      width: 90,
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 180,
      render: (value: string | null) => (value ? new Date(value).toLocaleString() : "-"),
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
      width: 210,
      render: (_, record) => (
        <Space size={4}>
          <Button type="link" onClick={() => openEditModal(record)}>
            编辑
          </Button>
          <Button type="link" onClick={() => void handleStatusChange(record)}>
            {record.status === "active" ? "下架" : "上架"}
          </Button>
          <Popconfirm
            title="确认删除该产品？"
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
    void loadProducts(nextPagination.current, nextPagination.pageSize);
  };

  const handleUploadImage = async (file: File) => {
    return fileToBase64(file);
  };

  const handleProductImageUpload = async (file: File) => {
    const base64 = await fileToBase64(file);
    productForm.setFieldValue("image_url", base64);
    setImageUrl(base64);
  };

  const handleRemoveProductImage = () => {
    productForm.setFieldValue("image_url", "");
    setImageUrl("");
  };

  return (
    <>
      {contextHolder}
      <div className="products-page">
        <Flex align="center" justify="space-between" className="products-page__heading">
          <div>
            <Typography.Title level={4}>产品管理</Typography.Title>
          </div>
          <Button type="primary" onClick={openCreateModal}>
            新增产品
          </Button>
        </Flex>

        <Card className="products-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="产品名称">
              <Input allowClear placeholder="请输入产品名称" />
            </Form.Item>
            <Form.Item name="validity_days" label="有效期">
              <Select
                allowClear
                options={validityOptions}
                placeholder="全部"
                style={{ width: 140 }}
              />
            </Form.Item>
            <Form.Item name="product_type" label="产品类型">
              <Select
                allowClear
                options={productTypeOptions}
                placeholder="全部"
                style={{ width: 140 }}
              />
            </Form.Item>
            <Form.Item name="status" label="状态">
              <Select
                allowClear
                options={statusOptions}
                placeholder="全部"
                style={{ width: 140 }}
              />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadProducts(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadProducts(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>

        <Card className="products-page__table">
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
            scroll={{ x: 1230 }}
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
        title={editingProduct ? "编辑产品" : "新增产品"}
        width={860}
      >
        <Form
          className="products-page__form"
          form={productForm}
          layout="vertical"
          preserve={false}
        >
          <Form.Item
            label="产品名称"
            name="name"
            rules={[{ required: true, message: "请输入产品名称" }]}
          >
            <Input maxLength={100} placeholder="例如：季度会员" showCount />
          </Form.Item>
          <Form.Item
            label="产品简介"
            name="summary"
            rules={[{ max: 20, message: "产品简介不能超过 20 个字" }]}
          >
            <Input maxLength={20} placeholder="20 字以内，用于小程序产品卡片" showCount />
          </Form.Item>
          <Flex gap={16}>
            <Form.Item
              label="价格"
              className="products-page__form-item"
            >
              <Space.Compact style={{ width: "100%" }}>
                <Button disabled>¥</Button>
                <Form.Item
                  name="price_yuan"
                  noStyle
                  rules={[{ required: true, message: "请输入价格" }]}
                >
                  <InputNumber
                    min={0}
                    precision={2}
                    placeholder="0.00"
                    style={{ width: "100%" }}
                  />
                </Form.Item>
              </Space.Compact>
            </Form.Item>
            <Form.Item
              label="产品类型"
              name="product_type"
              rules={[{ required: true, message: "请选择产品类型" }]}
              className="products-page__form-item"
            >
              <Select
                options={productTypeOptions}
                onChange={(value: ProductType) => {
                  productForm.setFieldValue("validity_days", value === "membership" ? 30 : undefined);
                }}
              />
            </Form.Item>
            {selectedProductType === "membership" ? (
              <Form.Item
                label="有效期"
                name="validity_days"
                rules={[{ required: true, message: "请选择有效期" }]}
                className="products-page__form-item"
              >
                <Select options={validityOptions} />
              </Form.Item>
            ) : null}
            <Form.Item label="排序" name="sort_order" className="products-page__form-item">
              <InputNumber precision={0} style={{ width: "100%" }} />
            </Form.Item>
          </Flex>
          <Form.Item label="产品图片">
            <Space align="start" size={16}>
              <Upload
                accept="image/*"
                beforeUpload={(file) => {
                  void handleProductImageUpload(file);
                  return Upload.LIST_IGNORE;
                }}
                maxCount={1}
                showUploadList={false}
              >
                <Button>上传图片</Button>
              </Upload>
              {imageUrl ? (
                <Space align="start">
                  <img
                    alt="产品图片预览"
                    src={imageUrl}
                    style={{
                      width: 96,
                      height: 96,
                      borderRadius: 12,
                      objectFit: "cover",
                    }}
                  />
                  <Button danger type="link" onClick={handleRemoveProductImage}>
                    移除
                  </Button>
                </Space>
              ) : null}
            </Space>
          </Form.Item>
          <Form.Item hidden name="image_url">
            <Input />
          </Form.Item>
          <Form.Item label="产品详情">
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
              renderHTML={(text) => mdParser.render(text)}
              style={{ height: 320 }}
              onImageUpload={handleUploadImage}
              value={markdownValue}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
