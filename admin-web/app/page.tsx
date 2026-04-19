import { AdminShell } from "@/components/admin-shell";
import { AuthGuard } from "@/components/auth-guard";


export default function HomePage() {
  return (
    <AuthGuard>
      <AdminShell />
    </AuthGuard>
  );
}
