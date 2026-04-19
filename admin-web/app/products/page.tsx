import { AdminShell } from "@/components/admin-shell";
import { AuthGuard } from "@/components/auth-guard";
import { ProductsPage } from "./products-page";
import "./styles.css";


export default function Page() {
  return (
    <AuthGuard>
      <AdminShell activeKey="products">
        <ProductsPage />
      </AdminShell>
    </AuthGuard>
  );
}
