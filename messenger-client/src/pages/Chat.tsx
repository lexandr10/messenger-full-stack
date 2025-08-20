import { useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import MessageList from "../components/MessageList";
import MessageInput from "../components/MessageInput";
import { useMessagesInfinite } from "../hooks/useMessagesInfinite";
import { useChatSocket } from "../hooks/useChatSocket";
import {
  useEditMessageMutation,
  useDeleteMessagesMutation,
} from "../hooks/useMessageMutations";
import { useMe } from "../hooks/useMe";

export default function Chat() {
  const { id } = useParams();
  const convId = id ? Number(id) : undefined;
  const valid = !!convId && convId > 0;
  const me = useMe();

  const {
    items: messages,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
  } = useMessagesInfinite(convId, 50, { enabled: valid });

  const { connected, sendMessage } = useChatSocket(valid ? convId : undefined);

  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!valid) return;
    const el = listRef.current;
    if (!el) return;
    const onScroll = () => {
      if (el.scrollTop < 50 && hasNextPage && !isFetchingNextPage)
        fetchNextPage();
    };
    el.addEventListener("scroll", onScroll);
    return () => el.removeEventListener("scroll", onScroll);
  }, [valid, hasNextPage, isFetchingNextPage, fetchNextPage]);

  const editMut = useEditMessageMutation(convId ?? 0);
  const delMut = useDeleteMessagesMutation(convId ?? 0);

  if (!valid) {
    return (
      <div className="text-slate-600">
        Выберите беседу на{" "}
        <Link to="/" className="underline text-indigo-600">
          главной
        </Link>
        .
      </div>
    );
  }
  const currentUserId = me.data?.id;

  return (
    <div className="grid gap-4">
      <div className="text-sm text-slate-500">
        WS: {connected ? "connected" : "disconnected"}
      </div>

      <div ref={listRef} className="h-[65vh] overflow-auto">
        {status === "pending" ? (
          <div className="text-slate-500">Loading…</div>
        ) : (
          <MessageList
            items={messages}
            onEdit={(id, content) => editMut.mutate({ id, content })}
            onDelete={(ids) => delMut.mutate(ids)}
            currentUserId={currentUserId}
          />
        )}
        {hasNextPage && (
          <button
            disabled={isFetchingNextPage}
            className="mt-3 text-sm text-indigo-600 underline"
            onClick={() => fetchNextPage()}
          >
            {isFetchingNextPage ? "Loading…" : "Load older"}
          </button>
        )}
      </div>

      <MessageInput conversationId={convId} onSend={(payload) => sendMessage(payload)} />
    </div>
  );
}
