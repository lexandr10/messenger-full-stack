
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { editMessage, deleteMessagesBulk } from "../api/message";
import { qk } from "../api/keys";
import type { Message } from "../types/chat";
import { type InfiniteData } from "@tanstack/react-query";

export function useEditMessageMutation(conversationId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) =>
      editMessage(id, content),
    onSuccess: (msg) => {
      qc.setQueryData<InfiniteData<Message[]>>(
        qk.messages(conversationId),
        (data) => {
          if (!data) return data;
          const pages = data.pages.map((arr) =>
            arr.map((m) => (m.id === msg.id ? { ...m, ...msg } : m))
          );
          return { ...data, pages };
        }
      );
    },
  });
}

export function useDeleteMessagesMutation(conversationId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ids: number[]) => deleteMessagesBulk(ids),
    onSuccess: (res) => {
      const set = new Set(res.deleted);
      qc.setQueryData<InfiniteData<Message[]>>(
        qk.messages(conversationId),
        (data) => {
          if (!data) return data;
          const pages = data.pages.map((arr) =>
            arr.filter((m) => !set.has(m.id))
          );
          return { ...data, pages };
        }
      );
    },
  });
}