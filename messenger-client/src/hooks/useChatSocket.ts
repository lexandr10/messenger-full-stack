
import { useEffect, useRef, useState, useCallback } from "react";
import { WS_URL } from "../config";
import { useQueryClient, type InfiniteData } from "@tanstack/react-query";
import type { Message } from "../types/chat";
import { qk } from "../api/keys";

type WsConnected = {
  type: "connected";
  conversation_id: number;
  user_id: number;
};
type WsNew = { type: "message:new"; message: Message };
type WsEdited = { type: "message:edited"; message: Message };
type WsDeleted = { type: "message:deleted"; message_ids: number[] };
type WsMsg =
  | WsConnected
  | WsNew
  | WsEdited
  | WsDeleted
  | Record<string, unknown>;

type NewAttachmentIn = {
  file_path: string;
  file_name?: string;
  mime?: string;
  size_bytes?: number;
  storage?: string;
};

function isWsNew(x: unknown): x is WsNew {
  return (
    typeof x === "object" &&
    x !== null &&
    (x as any).type === "message:new" &&
    (x as any).message
  );
}
function isWsEdited(x: unknown): x is WsEdited {
  return (
    typeof x === "object" &&
    x !== null &&
    (x as any).type === "message:edited" &&
    (x as any).message
  );
}
function isWsDeleted(x: unknown): x is WsDeleted {
  return (
    typeof x === "object" &&
    x !== null &&
    (x as any).type === "message:deleted" &&
    Array.isArray((x as any).message_ids)
  );
}

function updateCacheAdd(
  qc: ReturnType<typeof useQueryClient>,
  convId: number,
  msg: Message
) {
  qc.setQueryData<InfiniteData<Message[]>>(qk.messages(convId), (data) => {
    if (!data) return { pageParams: [{}], pages: [[msg]] };
    const pages = [...data.pages];
    if (pages.length === 0) return { pageParams: [{}], pages: [[msg]] };
    const last = pages[pages.length - 1]!;
    pages[pages.length - 1] = [...last, msg];
    return { ...data, pages };
  });
}

function updateCacheEdit(
  qc: ReturnType<typeof useQueryClient>,
  convId: number,
  msg: Message
) {
  qc.setQueryData<InfiniteData<Message[]>>(qk.messages(convId), (data) => {
    if (!data) return data;
    const pages = data.pages.map((arr) =>
      arr.map((m) => (m.id === msg.id ? { ...m, ...msg } : m))
    );
    return { ...data, pages };
  });
}

function updateCacheDelete(
  qc: ReturnType<typeof useQueryClient>,
  convId: number,
  ids: number[]
) {
  const set = new Set(ids);
  qc.setQueryData<InfiniteData<Message[]>>(qk.messages(convId), (data) => {
    if (!data) return data;
    const pages = data.pages.map((arr) => arr.filter((m) => !set.has(m.id)));
    return { ...data, pages };
  });
}

export function useChatSocket(conversationId: number | undefined) {
  const qc = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!conversationId) return;

    let stopped = false;
    let retry = 0;

    const open = () => {
      const token = localStorage.getItem("access_token") ?? "";
      const url = `${WS_URL}/conversation/${conversationId}?token=${encodeURIComponent(
        token
      )}`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        retry = 0;
        setConnected(true);
      };

      ws.onmessage = (ev) => {
        let data: WsMsg;
        try {
          data = JSON.parse(ev.data);
        } catch {
          return;
        }
        if (isWsNew(data)) {
          updateCacheAdd(qc, conversationId, data.message);
        } else if (isWsEdited(data)) {
          updateCacheEdit(qc, conversationId, data.message);
        } else if (isWsDeleted(data)) {
          updateCacheDelete(qc, conversationId, data.message_ids);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        if (stopped) return;
        const delay = Math.min(1000 * 2 ** retry, 10000);
        retry += 1;
        setTimeout(open, delay);
      };

      ws.onerror = () => ws.close();
    };

    open();
    return () => {
      stopped = true;
      wsRef.current?.close();
      wsRef.current = null;
      setConnected(false);
    };
  }, [conversationId, qc]);

  const sendMessage = useCallback(
    (payload: { content: string; attachments?: NewAttachmentIn[] }) => {
      const ws = wsRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      ws.send(JSON.stringify({ type: "send_message", ...payload }));
    },
    []
  );

  return { connected, sendMessage };
}
