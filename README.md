# 小哲医疗项目

本仓库是小哲医疗的服务端与后台管理端工程，当前包含小程序服务端、Admin 服务端、Admin 后台前端以及 Docker 编排配置。小程序端代码在同级目录 `../xiaozhe-healthcare` 中。

## 目录结构

```text
xiaozhe-server/
├── miniapp-server/   # 小程序服务端，Flask + Flask-SQLAlchemy + Flask-Migrate，使用 uv 管理依赖
├── admin-server/     # Admin 服务端，Flask + Flask-SQLAlchemy + Flask-Migrate，使用 uv 管理依赖
├── admin-web/        # Admin 后台前端，Next.js App Router + TypeScript + Ant Design
└── docker/           # Docker Compose、环境变量样例与本地数据卷目录
```

## 架构约定

- 两个 Flask 服务端相对独立，各自拥有应用配置、依赖、迁移目录、路由、控制器、服务层和模型层。
- 两个服务端共用同一个 PostgreSQL 数据库和同一个 Redis 实例。
- 当前数据库名默认为 `xiaozhe_medical`。
- 小程序服务端表名以 `miniapp_` 为前缀，Alembic 版本表为 `miniapp_alembic_version`。
- Admin 服务端表名以 `admin_` 为前缀，Alembic 版本表为 `admin_alembic_version`。
- 金额字段统一使用 cent 方案，例如 `price_cents`、`total_amount_cents`。
- 主键当前保持数据库自增 integer/bigint 方案，接口层对外通常序列化为字符串，方便小程序和前端统一处理。
- 正式 `docker-compose.yml` 中 PostgreSQL 和 Redis 不暴露宿主机端口，服务间通过 `postgres:5432` 和 `redis:6379` 访问。
- 本地调试使用 `docker-compose.dev.yml`，只启动 PostgreSQL 和 Redis，并暴露到 `localhost:5432`、`localhost:6379`。

## 当前模块

Admin 后台已包含：

- 登录与注册开关配置
- 产品管理
- 资讯管理
- Banner 管理
- 人员管理：科室、医生、助理、客服
- 用户管理与会员续期
- 订单管理与退款处理
- 协议管理：用户协议、隐私政策

小程序服务端已包含：

- 微信登录、手机号登录、用户资料
- 产品、购物车、下单、支付模拟、取消订单、申请退款
- 首页 Banner、资讯、产品查询
- 用户健康档案
- 医生、助理、客服相关查询
- 单聊和群聊基础能力，支持文字、图片、视频消息

小程序端 `../xiaozhe-healthcare` 已接入：

- 产品中心、首页产品展示、购物车、订单详情、退款申请
- 登录缓存、我的页面、健康档案
- 用户端、医生端、助理端角色切换
- 聊天列表、聊天详情、群聊邀请与成员资料查看

## Docker 启动

首次启动前复制环境变量：

```powershell
cd C:\Users\admin\WeChatProjects\xiaozhe-server\docker
copy .env.example .env
```

启动完整环境：

```powershell
docker compose --env-file .env -f docker-compose.yml up --build
```

完整环境会启动：

- `miniapp-server`: `http://localhost:5001/api/health`
- `admin-server`: `http://localhost:5002/api/health`
- `admin-web`: `http://localhost:3000`
- `postgres`: 仅 Docker 网络内部访问
- `redis`: 仅 Docker 网络内部访问

## 本地调试

如果前后端在本机直接运行，建议只启动数据库和 Redis：

```powershell
cd C:\Users\admin\WeChatProjects\xiaozhe-server\docker
docker compose --env-file .env -f docker-compose.dev.yml up -d
```

本地调试环境会暴露：

- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

本地服务端需要使用本机地址：

```text
DATABASE_URL=postgresql+psycopg://postgres:xiaozhe123456@localhost:5432/xiaozhe_medical
REDIS_URL=redis://localhost:6379/0
```

Docker 内服务端使用容器地址：

```text
DATABASE_URL=postgresql+psycopg://postgres:xiaozhe123456@postgres:5432/xiaozhe_medical
REDIS_URL=redis://redis:6379/0
```

## 服务端开发命令

小程序服务端：

```powershell
cd C:\Users\admin\WeChatProjects\xiaozhe-server\miniapp-server
uv sync
uv run flask --app app db upgrade
uv run flask --app app run --host 0.0.0.0 --port 5001
```

Admin 服务端：

```powershell
cd C:\Users\admin\WeChatProjects\xiaozhe-server\admin-server
uv sync
uv run flask --app app db upgrade
uv run flask --app app run --host 0.0.0.0 --port 5002
```

常用检查：

```powershell
uv run python -m compileall -q app
uv run flask --app app routes
```

## Admin 前端开发命令

```powershell
cd C:\Users\admin\WeChatProjects\xiaozhe-server\admin-web
pnpm install
pnpm dev
```

类型检查：

```powershell
.\node_modules\.bin\tsc.CMD --noEmit --incremental false
```

## 迁移说明

当前两个服务端使用同一个数据库，但迁移版本表不同：

- 小程序服务端：`miniapp_alembic_version`
- Admin 服务端：`admin_alembic_version`

因此初始化或重建数据库后，两个服务端都需要执行迁移：

```powershell
cd C:\Users\admin\WeChatProjects\xiaozhe-server\admin-server
uv run flask --app app db upgrade

cd C:\Users\admin\WeChatProjects\xiaozhe-server\miniapp-server
uv run flask --app app db upgrade
```

注意：部分小程序表会引用 Admin 表，例如产品、医生、助理等。全新数据库初始化时，建议先执行 Admin 服务端迁移，再执行小程序服务端迁移。

## 环境变量重点

核心变量位于 `docker/.env.example`：

- `DB_USERNAME`、`DB_PASSWORD`、`DB_DATABASE`、`DB_PORT`
- `REDIS_URL`
- `CELERY_BROKER_URL`、`CELERY_RESULT_BACKEND`
- `MINIAPP_API_PORT`、`ADMIN_API_PORT`、`ADMIN_WEB_PORT`
- `ADMIN_ALLOW_REGISTER`
- `ADMIN_JWT_SECRET_KEY`、`ADMIN_JWT_ACCESS_TOKEN_EXPIRES`
- `NEXT_PUBLIC_API_BASE_URL`

PostgreSQL 和 Gunicorn 保留了基础性能参数：

- `POSTGRES_MAX_CONNECTIONS`
- `POSTGRES_SHARED_BUFFERS`
- `POSTGRES_WORK_MEM`
- `POSTGRES_MAINTENANCE_WORK_MEM`
- `POSTGRES_EFFECTIVE_CACHE_SIZE`
- `POSTGRES_STATEMENT_TIMEOUT`
- `POSTGRES_IDLE_IN_TRANSACTION_SESSION_TIMEOUT`
- `SERVER_WORKER_AMOUNT`
- `SERVER_WORKER_CLASS`
- `SERVER_WORKER_CONNECTIONS`
- `GUNICORN_TIMEOUT`

## 异步任务约定

当前 Admin 服务端不使用 Celery。小程序服务端保留 Celery/Redis 配置，后续如果需要异步任务或定时任务，建议放在小程序服务端内：

- `app/tasks/` 放任务定义
- Redis 作为 broker 和 result backend
- 定时任务可以通过 Celery Beat 或独立调度容器接入
- 长耗时任务不要阻塞 Flask 请求，应由接口写入任务并快速返回任务状态

## 数据与文件

- `docker/volumes/` 为本地 Docker 数据卷目录，已加入 `.gitignore`。
- 当前图片字段多处暂以 base64 或 URL 字符串存储，后续生产环境建议接入 OSS/S3 类对象存储。
- 聊天、产品、资讯、Banner 等文件资源后续建议统一抽象上传服务，业务表只保存 URL 和必要元信息。

