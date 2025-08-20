import { useMutation } from "@tanstack/react-query";
import { login, register, logout } from "../api/auth";
import { useAuthToken } from "../hooks/useAuthToken";

export function useLoginMutation() {
  const { save } = useAuthToken();
  return useMutation({
    mutationFn: ({
      username,
      password,
    }: {
      username: string;
      password: string;
    }) => login(username, password),
    onSuccess: (data) => {
      save(data.access_token);
    },
  });
}

export function useRegisterMutation() {
  const { save } = useAuthToken();
  return useMutation({
    mutationFn: ({
      email,
      username,
      password,
    }: {
      email: string;
      username: string;
      password: string;
    }) => register({ email, username, password }),
    onSuccess: (data) => save(data.access_token),
  });
}

export function useLogoutMutation() {
  const { clear } = useAuthToken();
  return useMutation({
    mutationFn: () => logout(),
    onSuccess: () => clear(),
  });
}
