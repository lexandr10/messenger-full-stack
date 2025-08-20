import { http } from "./http";
import type { Message } from "../types/chat";

export type ListMessagesParams = {
  conversationId: number;
  limit?: number;
  before_id?: number; 
  after_id?: number; 
};

export async function fetchMessages(
  params: ListMessagesParams
): Promise<Message[]> {
  const { conversationId, limit = 50, before_id, after_id } = params;
  const res = await http.get(`/conversations/${conversationId}/messages`, {
    params: { limit, before_id, after_id },
  });
  return res.data;
}

export async function editMessage(
  messageId: number,
  content: string
): Promise<Message> {
  const res = await http.patch(`/messages/${messageId}`, { content });
  return res.data;
}

export type BulkDeleteResult = {
  deleted: number[];
  forbidden: number[];
  not_found: number[];
};

export async function deleteMessagesBulk(
  ids: number[]
): Promise<BulkDeleteResult> {
  const res = await http.delete(`/messages/bulk`, { data: { ids } });
  return res.data;
}
