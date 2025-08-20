import { http } from "./http";

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
};

import type { Me } from "../types/user";

export async function fetchMe(): Promise<Me> {
  const res = await http.get("/auth/me");
  return res.data;
}

export async function login(
  username: string,
  password: string
): Promise<AuthResponse> {
  const form = new URLSearchParams();
  form.set("username", username);
  form.set("password", password);

  const res = await http.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    withCredentials: true, 
  });
  return res.data;
}

export async function register(data: {
  email: string;
  username: string;
  password: string;
}): Promise<AuthResponse> {
  const res = await http.post("/auth/register", data);
  return res.data;
}

export async function logout(): Promise<void> {
  await http.post("/auth/logout"); 
}
