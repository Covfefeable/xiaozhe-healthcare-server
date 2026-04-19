# miniapp-server

小哲医疗小程序服务端骨架。

## 技术栈

- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- PostgreSQL
- Redis

## 目录说明

- `app/`：应用主目录
- `app/routes/`：路由层，负责 HTTP 入口与参数读取
- `app/controllers/`：控制层，负责请求编排
- `app/services/`：服务层，负责业务逻辑
- `app/models/`：数据模型
- `app/tasks/`：后台任务预留
- `app/utils/`：通用工具，例如统一响应
- `migrations/`：数据库迁移目录
- `wsgi.py`：WSGI 入口
- `manage.py`：开发入口

## 健康检查

`GET /api/health`
