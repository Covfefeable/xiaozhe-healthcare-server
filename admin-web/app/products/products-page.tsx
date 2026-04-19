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
  message,
  type TablePaginationConfig,
  type TableProps,
} from "antd";
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
} from "@/lib/api";

const MarkdownEditor = dynamic(() => import("@uiw/react-md-editor"), { ssr: false });

type FilterValues = {
  keyword?: string;
  validity_days?: number;
  status?: ProductStatus;
};

type ProductFormValues = {
  name: string;
  price_yuan: number;
  validity_days: number;
  detail_markdown?: string;
  sort_order?: number;
};

const validityOptions = [
  { label: "30 天", value: 30 },
  { label: "90 天", value: 90 },
  { label: "180 天", value: 180 },
  { label: "360 天", value: 360 },
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

function yuanToCents(value: number) {
  return Math.round(Number(value || 0) * 100);
}

function centsToYuan(value: number) {
  return Number((value / 100).toFixed(2));
}

function toPayload(values: ProductFormValues): ProductPayload {
  return {
    name: values.name.trim(),
    price_cents: yuanToCents(values.price_yuan),
    validity_days: values.validity_days,
    detail_markdown: values.detail_markdown ?? "",
    sort_order: values.sort_order ?? 0,
  };
}

export function ProductsPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [productForm] = Form.useForm<ProductFormValues>();
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [markdownValue, setMarkdownValue] = useState("");
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
      price_yuan: 0,
      validity_days: 30,
      sort_order: 0,
    });
    setMarkdownValue("");
    setModalOpen(true);
  };

  const openEditModal = (product: Product) => {
    setEditingProduct(product);
    productForm.setFieldsValue({
      name: product.name,
      price_yuan: centsToYuan(product.price_cents),
      validity_days: product.validity_days,
      sort_order: product.sort_order,
    });
    setMarkdownValue(product.detail_markdown ?? "");
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
      title: "产品名称",
      dataIndex: "name",
      key: "name",
      ellipsis: true,
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
      render: (value: number) => `${value} 天`,
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
            scroll={{ x: 1120 }}
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
          <Flex gap={16}>
            <Form.Item
              label="价格"
              name="price_yuan"
              rules={[{ required: true, message: "请输入价格" }]}
              className="products-page__form-item"
            >
              <InputNumber
                addonBefore="¥"
                min={0}
                precision={2}
                placeholder="0.00"
                style={{ width: "100%" }}
              />
            </Form.Item>
            <Form.Item
              label="有效期"
              name="validity_days"
              rules={[{ required: true, message: "请选择有效期" }]}
              className="products-page__form-item"
            >
              <Select options={validityOptions} />
            </Form.Item>
            <Form.Item label="排序" name="sort_order" className="products-page__form-item">
              <InputNumber precision={0} style={{ width: "100%" }} />
            </Form.Item>
          </Flex>
          <Form.Item label="产品详情">
            <MarkdownEditor
              data-color-mode="light"
              height={320}
              onChange={(value) => setMarkdownValue(value ?? "")}
              preview="edit"
              value={markdownValue}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
