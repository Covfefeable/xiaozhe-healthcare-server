"use client";

import {
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  message,
  type TablePaginationConfig,
  type TableProps,
} from "antd";
import { useEffect, useState } from "react";

import {
  getAdminOrder,
  getOrderList,
  updateOrderStatus,
  type AdminOrder,
  type OrderStatus,
} from "@/lib/api";

type FilterValues = {
  keyword?: string;
  status?: OrderStatus;
};

const statusOptions: { label: string; value: OrderStatus }[] = [
  { label: "待支付", value: "pending_payment" },
  { label: "进行中", value: "in_progress" },
  { label: "已完成", value: "completed" },
  { label: "已退款", value: "refunded" },
];

const statusColor: Record<OrderStatus, string> = {
  pending_payment: "warning",
  in_progress: "processing",
  completed: "success",
  refunded: "default",
};

const productTypeLabel = {
  membership: "会员",
  other: "其他",
};

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "-";
}

export function OrdersPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [items, setItems] = useState<AdminOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [currentOrder, setCurrentOrder] = useState<AdminOrder | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const loadOrders = async (nextPage = pagination.current, nextPageSize = pagination.pageSize) => {
    setLoading(true);
    try {
      const result = await getOrderList({
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
      messageApi.error(error instanceof Error ? error.message : "订单加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadOrders(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleUpdateStatus = async (order: AdminOrder, status: "completed" | "refunded") => {
    try {
      await updateOrderStatus(order.id, status);
      messageApi.success("保存成功");
      await loadOrders(pagination.current, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    }
  };

  const handleOpenDetail = async (order: AdminOrder) => {
    setDetailOpen(true);
    setCurrentOrder(order);
    setDetailLoading(true);
    try {
      const detail = await getAdminOrder(order.id);
      setCurrentOrder(detail);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "订单详情加载失败");
    } finally {
      setDetailLoading(false);
    }
  };

  const columns: TableProps<AdminOrder>["columns"] = [
    { title: "订单号", dataIndex: "order_no", key: "order_no", width: 180 },
    { title: "用户手机号", dataIndex: "user_phone", key: "user_phone", width: 140 },
    { title: "商品", dataIndex: "product_summary", key: "product_summary", ellipsis: true },
    {
      title: "类型",
      dataIndex: "product_type",
      key: "product_type",
      width: 90,
      render: (value: "membership" | "other") => productTypeLabel[value],
    },
    {
      title: "金额",
      dataIndex: "total_amount",
      key: "total_amount",
      width: 110,
      render: (value: string) => `¥${value}`,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 110,
      render: (value: OrderStatus, record) => <Tag color={statusColor[value]}>{record.status_label}</Tag>,
    },
    { title: "支付时间", dataIndex: "paid_at", key: "paid_at", width: 180, render: formatDate },
    { title: "创建时间", dataIndex: "created_at", key: "created_at", width: 180, render: formatDate },
    {
      title: "操作",
      key: "action",
      fixed: "right",
      width: 190,
      render: (_, record) => {
        const canOperate = record.status === "in_progress";
        const canComplete = canOperate && record.product_type !== "membership";
        return (
          <Space size={4}>
            <Button type="link" onClick={() => void handleOpenDetail(record)}>
              查看详情
            </Button>
            {canComplete ? (
              <Popconfirm
                title="确认将订单标记为已完成？"
                okText="确认"
                cancelText="取消"
                onConfirm={() => void handleUpdateStatus(record, "completed")}
              >
                <Button type="link">完成</Button>
              </Popconfirm>
            ) : null}
            {canOperate ? (
              <Popconfirm
                title="确认将订单标记为已退款？"
                okText="确认"
                cancelText="取消"
                onConfirm={() => void handleUpdateStatus(record, "refunded")}
              >
                <Button danger type="link">
                  退款
                </Button>
              </Popconfirm>
            ) : null}
          </Space>
        );
      },
    },
  ];

  const handleTableChange = (nextPagination: TablePaginationConfig) => {
    void loadOrders(nextPagination.current, nextPagination.pageSize);
  };

  return (
    <>
      {contextHolder}
      <div className="orders-page">
        <Card className="orders-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="关键词">
              <Input allowClear placeholder="订单号、手机号或就诊人" />
            </Form.Item>
            <Form.Item name="status" label="状态">
              <Select allowClear options={statusOptions} placeholder="全部" style={{ width: 140 }} />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadOrders(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadOrders(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
        <Card className="orders-page__table">
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
            scroll={{ x: 1300 }}
          />
        </Card>
        <Modal
          title="订单详情"
          open={detailOpen}
          onCancel={() => setDetailOpen(false)}
          footer={null}
          width={760}
          loading={detailLoading}
        >
          {currentOrder ? (
            <Space direction="vertical" size={18} style={{ width: "100%" }}>
              <Descriptions bordered column={2} size="small">
                <Descriptions.Item label="订单号" span={2}>
                  {currentOrder.order_no}
                </Descriptions.Item>
                <Descriptions.Item label="用户手机号">{currentOrder.user_phone || "-"}</Descriptions.Item>
                <Descriptions.Item label="就诊人">{currentOrder.service_user_name || "-"}</Descriptions.Item>
                <Descriptions.Item label="订单状态">
                  <Tag color={statusColor[currentOrder.status]}>{currentOrder.status_label}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="产品类型">{productTypeLabel[currentOrder.product_type]}</Descriptions.Item>
                <Descriptions.Item label="订单金额">￥{currentOrder.total_amount}</Descriptions.Item>
                <Descriptions.Item label="支付方式">{currentOrder.payment_method || "-"}</Descriptions.Item>
                <Descriptions.Item label="支付时间">{formatDate(currentOrder.paid_at)}</Descriptions.Item>
                <Descriptions.Item label="完成时间">{formatDate(currentOrder.completed_at)}</Descriptions.Item>
                <Descriptions.Item label="创建时间" span={2}>
                  {formatDate(currentOrder.created_at)}
                </Descriptions.Item>
              </Descriptions>
              <Table
                columns={[
                  { title: "商品名称", dataIndex: "product_name", key: "product_name" },
                  {
                    title: "类型",
                    dataIndex: "product_type",
                    key: "product_type",
                    width: 100,
                    render: (value: "membership" | "other") => productTypeLabel[value],
                  },
                  { title: "数量", dataIndex: "quantity", key: "quantity", width: 90 },
                  {
                    title: "小计",
                    dataIndex: "subtotal",
                    key: "subtotal",
                    width: 120,
                    render: (value: string) => `￥${value}`,
                  },
                ]}
                dataSource={currentOrder.items || []}
                pagination={false}
                rowKey="id"
                size="small"
              />
            </Space>
          ) : null}
        </Modal>
      </div>
    </>
  );
}
