import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { API_URL } from "../config";

export const http = axios.create({ baseURL: API_URL, withCredentials: true });

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});


const authHttp = axios.create({ baseURL: API_URL, withCredentials: true });

let isRefreshing = false;
let pending: Array<(token: string) => void> = [];

async function refreshAccessToken(): Promise<string> {
  const res = await authHttp.post("/auth/refresh"); 
  const newToken = res.data?.access_token as string;
  if (!newToken) throw new Error("No access_token in refresh response");
  localStorage.setItem("access_token", newToken);
  return newToken;
}
http.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const response = error.response;
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (response?.status === 401 && !original?._retry) {
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          pending.push((newToken: string) => {
            original.headers = original.headers ?? {};
            original.headers.Authorization = `Bearer ${newToken}`;
            resolve(http(original));
          });
        });
      }

      isRefreshing = true;
      try {
        const newToken = await refreshAccessToken();
        http.defaults.headers.common.Authorization = `Bearer ${newToken}`;
        pending.forEach((resume) => resume(newToken));
        pending = [];
        original.headers = original.headers ?? {};
        original.headers.Authorization = `Bearer ${newToken}`;
        return http(original);
      } catch (e) {
        pending = [];
        localStorage.removeItem("access_token");
        window.dispatchEvent(new CustomEvent("auth:logout"));
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);