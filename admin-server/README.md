# admin-server

小哲医疗 Admin 服务端骨架。

该项目与 `miniapp-server` 保持相同结构，便于共享研发规范、部署方式与工程习惯。

## 技术栈

- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- uv
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
- `manage.py`：开发入口
- `wsgi.py`：WSGI 入口

## 本地开发

```bash
uv sync
uv run flask --app app db upgrade
uv run python manage.py
```

## 后台登录

第一版后台登录只包含账号、密码、启用状态和最近登录时间，不包含角色、权限、超级管理员和头像。

认证接口：

- `POST /api/auth/login`
- `POST /api/auth/register`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/auth/config`

注册接口受环境变量控制：

```env
ALLOW_REGISTER=false
```

创建管理员账号推荐使用 CLI：

```bash
uv run flask --app app admin create-user --username admin --display-name 管理员
```

## 健康检查

`GET /api/health`

## 同库迁移约定

当前项目与 `miniapp-server` 共用同一个 PostgreSQL database。为避免迁移冲突：

- 本服务使用 `admin_alembic_version` 作为 Alembic 版本表
- 本服务业务表名必须使用 `admin_` 前缀
- 迁移自动生成会忽略不符合 `admin_` 前缀的表
