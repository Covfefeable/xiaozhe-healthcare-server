# 小哲医疗项目骨架

当前仓库按独立项目方式组织为四个顶层目录：

- `miniapp-server/`：小程序服务端，基于 Flask + Flask-SQLAlchemy + Flask-Migrate，使用 uv 管理依赖
- `admin-server/`：Admin 服务端，与小程序服务端保持同构，使用 uv 管理依赖
- `admin-web/`：Admin 后台前端，基于 Next.js App Router + TypeScript + Ant Design
- `docker/`：Docker Compose 编排配置目录

## 架构约定

- 两套服务端分别独立部署、独立配置、独立迁移
- 两套服务端共用同一个 PostgreSQL 实例和同一个 Redis 实例
- PostgreSQL 使用同一个数据库：`xiaozhe_medical`
- 小程序服务端使用 `miniapp_alembic_version` 作为 Alembic 版本表，业务表名使用 `miniapp_` 前缀
- Admin 服务端使用 `admin_alembic_version` 作为 Alembic 版本表，业务表名使用 `admin_` 前缀
- 公共表建议使用 `shared_` 前缀，并明确只由一个迁移入口负责创建和变更
- 两套 Flask 服务端采用相同分层：`routes`、`controllers`、`services`、`models`、`tasks`、`utils`

## Docker Compose

进入 `docker/` 后：

```bash
cp .env.example .env
docker compose --env-file .env -f docker-compose.yml up --build
```

默认端口：

- 小程序服务端：`http://localhost:5001/api/health`
- Admin 服务端：`http://localhost:5002/api/health`
- Admin 前端：`http://localhost:3000`
- PostgreSQL：`localhost:5432`
- Redis：`localhost:6379`

## 本地开发

服务端进入对应目录后：

```bash
uv sync
uv run python manage.py
```

前端进入 `admin-web/` 后：

```bash
pnpm install
pnpm dev
```

