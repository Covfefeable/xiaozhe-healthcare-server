# docker

该目录用于本地或服务器容器编排。

## 文件说明

- `.env.example`：Compose 环境变量模板
- `docker-compose.yml`：统一启动小程序服务端、Admin 服务端、Admin 前端、PostgreSQL、Redis

各项目的 `Dockerfile` 放在各自项目目录：

- `../miniapp-server/Dockerfile`
- `../admin-server/Dockerfile`
- `../admin-web/Dockerfile`

## 使用方式

```bash
cd docker
cp .env.example .env
docker compose --env-file .env -f docker-compose.yml up --build
```

## 端口

- 小程序服务端：`5001`
- Admin 服务端：`5002`
- Admin 前端：`3000`
- PostgreSQL：`5432`
- Redis：`6379`
