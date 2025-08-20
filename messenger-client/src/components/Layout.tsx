import { Link, Outlet, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useMe } from "../hooks/useMe";
import { logout as apiLogout } from "../api/auth";

export default function Layout() {
  const { data: me } = useMe();
  const nav = useNavigate();
  const qc = useQueryClient();

  const onLogout = async () => {
    try {
      await apiLogout();
    } catch {
      // ignore
    } finally {
      localStorage.removeItem("access_token");
      await qc.clear();
      nav("/login", { replace: true });
    }
  };

  const initials = (me?.username ?? me?.email ?? "U")
    .split(/\s|@/)[0]
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
          <Link to="/" className="font-semibold">
            Messenger
          </Link>
          <div className="flex items-center gap-3">
            {me && (
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-full bg-indigo-600 text-white grid place-items-center text-xs">
                  {initials}
                </div>
                <div className="hidden sm:block text-sm text-slate-600">
                  {me.username ?? me.email}
                </div>
              </div>
            )}
            <button
              onClick={onLogout}
              className="rounded-lg bg-slate-200 px-3 py-1.5 text-sm hover:bg-slate-300"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
