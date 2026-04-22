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
import MarkdownIt from "markdown-it";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import {
  createNews,
  deleteNews,
  getNewsList,
  updateNews,
  type NewsItem,
  type NewsPayload,
} from "@/lib/api";
import { uploadFile } from "@/lib/upload";

const MdEditor = dynamic(() => import("react-markdown-editor-lite"), { ssr: false });
const mdParser = new MarkdownIt({
  breaks: true,
  html: false,
  linkify: true,
});

type FilterValues = {
  keyword?: string;
};

type NewsFormValues = {
  cover_image_object_key?: string;
  title: string;
  published_at: string;
  content_markdown?: string;
};

function toPayload(values: NewsFormValues, content: string): NewsPayload {
  return {
    cover_image_object_key: values.cover_image_object_key ?? "",
    title: values.title.trim(),
    published_at: new Date(values.published_at).toISOString(),
    content_markdown: content,
  };
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

export function NewsPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [filterForm] = Form.useForm<FilterValues>();
  const [newsForm] = Form.useForm<NewsFormValues>();
  const [items, setItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingNews, setEditingNews] = useState<NewsItem | null>(null);
  const [coverImageUrl, setCoverImageUrl] = useState("");
  const [markdownValue, setMarkdownValue] = useState("");
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  const loadNews = async (
    nextPage = pagination.current,
    nextPageSize = pagination.pageSize,
  ) => {
    setLoading(true);
    try {
      const filters = filterForm.getFieldsValue();
      const result = await getNewsList({
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
      messageApi.error(error instanceof Error ? error.message : "加载资讯失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadNews(1, pagination.pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreateModal = () => {
    setEditingNews(null);
    newsForm.setFieldsValue({
      cover_image_object_key: "",
      title: "",
      published_at: toDatetimeLocalValue(),
    });
    setCoverImageUrl("");
    setMarkdownValue("");
    setModalOpen(true);
  };

  const openEditModal = (news: NewsItem) => {
    setEditingNews(news);
    newsForm.setFieldsValue({
      cover_image_object_key: news.cover_image_object_key ?? "",
      title: news.title,
      published_at: toDatetimeLocalValue(news.published_at),
    });
    setCoverImageUrl(news.cover_image_url ?? "");
    setMarkdownValue(news.content_markdown ?? "");
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await newsForm.validateFields();
    const payload = toPayload(values, markdownValue);
    setSaving(true);
    try {
      if (editingNews) {
        await updateNews(editingNews.id, payload);
        messageApi.success("保存成功");
      } else {
        await createNews(payload);
        messageApi.success("创建成功");
      }
      setModalOpen(false);
      await loadNews(editingNews ? pagination.current : 1, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (news: NewsItem) => {
    try {
      await deleteNews(news.id);
      messageApi.success("删除成功");
      const nextPage =
        items.length === 1 && pagination.current > 1
          ? pagination.current - 1
          : pagination.current;
      await loadNews(nextPage, pagination.pageSize);
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "删除失败");
    }
  };

  const handleTableChange = (nextPagination: TablePaginationConfig) => {
    void loadNews(nextPagination.current, nextPagination.pageSize);
  };

  const handleCoverUpload = async (file: File) => {
    const result = await uploadFile(file, "news");
    newsForm.setFieldValue("cover_image_object_key", result.object_key);
    setCoverImageUrl(result.url);
  };

  const handleRemoveCover = () => {
    newsForm.setFieldValue("cover_image_object_key", "");
    setCoverImageUrl("");
  };

  const handleEditorImageUpload = async (file: File) => {
    const result = await uploadFile(file, "markdown");
    return result.url;
  };

  const columns: TableProps<NewsItem>["columns"] = [
    {
      title: "封面图",
      dataIndex: "cover_image_url",
      key: "cover_image_url",
      width: 110,
      render: (value: string) =>
        value ? <img alt="资讯封面" className="news-page__cover-preview" src={value} /> : "-",
    },
    {
      title: "标题",
      dataIndex: "title",
      key: "title",
      ellipsis: true,
    },
    {
      title: "发布时间",
      dataIndex: "published_at",
      key: "published_at",
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
      width: 150,
      render: (_, record) => (
        <Space size={4}>
          <Button type="link" onClick={() => openEditModal(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确认删除该资讯？"
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
      <div className="news-page">
        <Flex align="center" justify="space-between" className="news-page__heading">
          <Typography.Title level={4}>资讯管理</Typography.Title>
          <Button type="primary" onClick={openCreateModal}>
            新增资讯
          </Button>
        </Flex>

        <Card className="news-page__filter">
          <Form form={filterForm} layout="inline">
            <Form.Item name="keyword" label="资讯标题">
              <Input allowClear placeholder="请输入资讯标题" />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={() => void loadNews(1, pagination.pageSize)}>
                  查询
                </Button>
                <Button
                  onClick={() => {
                    filterForm.resetFields();
                    void loadNews(1, pagination.pageSize);
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>

        <Card className="news-page__table">
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
        title={editingNews ? "编辑资讯" : "新增资讯"}
        width={860}
      >
        <Form className="news-page__form" form={newsForm} layout="vertical" preserve={false}>
          <Form.Item
            label="资讯标题"
            name="title"
            rules={[{ required: true, message: "请输入资讯标题" }]}
          >
            <Input maxLength={120} placeholder="请输入资讯标题" showCount />
          </Form.Item>
          <Form.Item
            label="发布时间"
            name="published_at"
            rules={[{ required: true, message: "请选择发布时间" }]}
          >
            <Input type="datetime-local" />
          </Form.Item>
          <Form.Item label="封面图">
            <Space align="start" size={16}>
              <Upload
                accept="image/*"
                beforeUpload={(file) => {
                  void handleCoverUpload(file);
                  return Upload.LIST_IGNORE;
                }}
                maxCount={1}
                showUploadList={false}
              >
                <Button>上传封面图</Button>
              </Upload>
              {coverImageUrl ? (
                <Space align="start">
                  <img
                    alt="资讯封面预览"
                    className="news-page__cover-preview"
                    src={coverImageUrl}
                  />
                  <Button danger type="link" onClick={handleRemoveCover}>
                    移除
                  </Button>
                </Space>
              ) : null}
            </Space>
          </Form.Item>
          <Form.Item hidden name="cover_image_object_key">
            <Input />
          </Form.Item>
          <Form.Item label="资讯内容">
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
              onImageUpload={handleEditorImageUpload}
              renderHTML={(text) => mdParser.render(text)}
              style={{ height: 360 }}
              value={markdownValue}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
