# admin-server

小哲医疗 Admin 服务端骨架。

该项目与 `miniapp-server` 保持相同结构，便于共享研发规范、部署方式与工程习惯。

## 技术栈

- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- PostgreSQL
- Redis

## 目录说明

- `app/routes/`：路由层，负责 HTTP 入口与参数读取
- `app/controllers/`：控制层，负责请求编排
- `app/services/`：服务层，负责业务逻辑
- `app/models/`：数据模型
- `app/tasks/`：后台任务预留
- `app/utils/`：通用工具，例如统一响应
- `migrations/`：数据库迁移目录

## 健康检查

`GET /api/health`
