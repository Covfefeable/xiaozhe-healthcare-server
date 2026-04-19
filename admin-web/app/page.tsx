export default function HomePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: "32px",
      }}
    >
      <section
        style={{
          width: "100%",
          maxWidth: "840px",
          background: "rgba(255,255,255,0.9)",
          border: "1px solid #d8e0ee",
          borderRadius: "24px",
          padding: "40px",
          boxShadow: "0 24px 60px rgba(24, 33, 47, 0.08)",
        }}
      >
        <p style={{ margin: 0, color: "#1366d6", fontWeight: 700 }}>
          XiaoZhe Medical
        </p>
        <h1 style={{ margin: "12px 0 16px", fontSize: "40px", lineHeight: 1.2 }}>
          小哲医疗 Admin 后台基础框架
        </h1>
        <p style={{ margin: 0, fontSize: "16px", lineHeight: 1.8 }}>
          当前已完成 Next.js 项目骨架初始化，后续可以继续接入登录、菜单、权限、
          数据面板与业务模块。
        </p>
      </section>
    </main>
  );
}

