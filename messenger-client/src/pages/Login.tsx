import { useState } from "react";
import { useLoginMutation } from "../hooks/useAuthMutations";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const nav = useNavigate();
  const m = useLoginMutation();
  const [username, setU] = useState("");
  const [password, setP] = useState("");

  return (
    <div className="max-w-sm mx-auto">
      <h1 className="text-xl font-semibold mb-4">Login</h1>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          m.mutate({ username, password }, { onSuccess: () => nav("/") });
        }}
      >
        <input
          className="w-full border rounded-xl px-3 py-2"
          placeholder="Username"
          value={username}
          onChange={(e) => setU(e.target.value)}
        />
        <input
          className="w-full border rounded-xl px-3 py-2"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setP(e.target.value)}
        />
        {m.isError && (
          <div className="text-red-600 text-sm">
            {(m.error as any)?.response?.data?.detail ?? "Login failed"}
          </div>
        )}
        <button
          className="w-full rounded-xl bg-indigo-600 text-white py-2"
          disabled={m.isPending}
        >
          {m.isPending ? "Signing in..." : "Sign in"}
        </button>
        <p className="mt-3 text-sm text-slate-600">
          Don’t have an account?{" "}
          <a href="/register" className="text-indigo-600 hover:underline">
            Register
          </a>
        </p>
      </form>
    </div>
  );
}
