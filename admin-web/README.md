# admin-web

小哲医疗 Admin 后台前端骨架，基于 Next.js App Router + TypeScript + Ant Design。

## 功能

- `/login`：后台登录页
- `/`：登录后进入空白后台首页
- 登录态使用 `localStorage` 保存 access token
- 请求 Admin API 时自动携带 `Authorization: Bearer <token>`

## 本地开发

```bash
pnpm install
pnpm dev
```
