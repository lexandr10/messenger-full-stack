import { Navigate, Outlet } from "react-router-dom";
import { useMe } from "../hooks/useMe";


export default function RedirectIfAuth() {
  const { data: me, isLoading } = useMe();

  const hasToken = !!localStorage.getItem("access_token");

  if (isLoading && hasToken) {
    return (
      <div className="min-h-[50vh] grid place-items-center text-slate-500">
        Checking session…
      </div>
    );
  }
  if (me?.id) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
