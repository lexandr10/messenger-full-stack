import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  useConversations,
  useCreateConversation,
} from "../hooks/useConversations";
import type { Conversation } from "../types/chat";

function titleFor(c: Conversation) {
  const peer = c.peer;
  if (peer?.username) return peer.username;
  if (peer?.email) return peer.email;
  return `Chat #${c.id}`;
}

export default function ConversationsPage() {
  const nav = useNavigate();
  const [peerId, setPeerId] = useState<string>("");

  const list = useConversations();
  const create = useCreateConversation();

  const onCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const id = parseInt(peerId, 10);
    if (!id || id <= 0) return;
    create.mutate(id, {
      onSuccess: (conv) => nav(`/c/${conv.id}`),
    });
  };

  return (
    <div className="grid gap-6">
      <form onSubmit={onCreate} className="flex gap-2">
        <input
          className="flex-1 rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="User's ID for new Chat (peer_id)"
          value={peerId}
          onChange={(e) => setPeerId(e.target.value)}
        />
        <button
          className="rounded-xl bg-indigo-600 text-white px-4 py-2 hover:bg-indigo-700"
          disabled={create.isPending}
        >
          {create.isPending ? "Creating…" : "New chat"}
        </button>
      </form>

      <div className="bg-white rounded-xl shadow divide-y">
        <div className="px-4 py-3 font-semibold">Your chats</div>
        {list.isLoading ? (
          <div className="px-4 py-3 text-slate-500">Loading…</div>
        ) : !list.data?.length ? (
          <div className="px-4 py-3 text-slate-500">Empty</div>
        ) : (
          <ul>
            {list.data.map((c) => (
              <li key={c.id} className="px-4 py-3 hover:bg-slate-50">
                <Link
                  to={`/c/${c.id}`}
                  className="flex items-center justify-between"
                >
                  <div className="font-medium">{titleFor(c)}</div>
                  <div className="text-xs text-slate-500">#{c.id}</div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
