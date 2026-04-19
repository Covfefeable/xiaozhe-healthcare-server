# 小哲医疗项目骨架

当前仓库已按独立项目方式初始化为四个顶层目录：

- `miniapp-server/`：小程序服务端，基于 Flask + Flask-SQLAlchemy + Flask-Migrate
- `admin-server/`：Admin 服务端，架构与小程序服务端保持一致
- `admin-web/`：Admin 后台前端，基于 Next.js App Router + TypeScript
- `docker/`：Docker 与后续 `docker-compose` 配置目录

## 架构约定

- 两套服务端分别独立部署、独立配置、独立迁移
- 两套服务端共用同一个 PostgreSQL 实例
- 两套服务端共用同一个 Redis 实例
- PostgreSQL 中使用同一个数据库，通过不同业务表共同存储
- 后续可在 `docker/compose.yml` 中统一编排四类容器：
  - `miniapp-server`
  - `admin-server`
  - `admin-web`
  - `postgres` / `redis`

## 推荐启动方式

### 1. 小程序服务端

进入 `miniapp-server/` 后：

1. 创建虚拟环境
2. 安装 `requirements.txt`
3. 配置 `.env`
4. 执行 Flask 启动命令

### 2. Admin 服务端

进入 `admin-server/` 后执行同样步骤。

### 3. Admin 前端

进入 `admin-web/` 后：

1. 安装依赖
2. 配置 `.env.local`
3. 执行 `npm run dev`

## 后续可继续补充

- 业务模块拆分
- PostgreSQL/Redis Docker Compose
- API 文档
- 统一鉴权与用户体系
- CI/CD

