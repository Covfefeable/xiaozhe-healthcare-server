# docker

该目录用于本地或服务器容器编排。

## 文件说明

- `.env.example`：Compose 环境变量模板
- `docker-compose.yml`：统一启动小程序服务端、Admin 服务端、Admin 前端、PostgreSQL、Redis
- `docker-compose.dev.yml`：仅启动 PostgreSQL 和 Redis，便于本地调试服务端和前端

各项目的 `Dockerfile` 放在各自项目目录：

- `../miniapp-server/Dockerfile`
- `../admin-server/Dockerfile`
- `../admin-web/Dockerfile`

## 使用方式

完整启动：

```bash
cd docker
cp .env.example .env
docker compose --env-file .env -f docker-compose.yml up --build
```

仅启动本地开发依赖：

```bash
cd docker
cp .env.example .env
docker compose --env-file .env -f docker-compose.dev.yml up -d
```

## 端口

- 小程序服务端：`5001`
- Admin 服务端：`5002`
- Admin 前端：`3000`
- 正式 `docker-compose.yml` 不暴露 PostgreSQL/Redis 端口，服务端只能通过容器网络内的 `postgres:5432` 和 `redis:6379` 访问
- 开发 `docker-compose.dev.yml` 会暴露 PostgreSQL/Redis，便于本地服务通过 `localhost:5432` 和 `localhost:6379` 调试
