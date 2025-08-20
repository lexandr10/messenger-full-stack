import { http } from "./http";
import type { Conversation } from "../types/chat";

export async function fetchConversations(): Promise<Conversation[]> {
  const res = await http.get("/conversations");
  return res.data;
}

export async function createConversation(partner_id: number): Promise<Conversation> {
  const res = await http.post("/conversations", { partner_id });
  return res.data;
}
