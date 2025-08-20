import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return (
    <div className="min-h-screen grid place-items-center bg-slate-50 text-slate-900 px-4">
      <main className="w-full max-w-md">
        <Outlet />
      </main>
    </div>
  );
}