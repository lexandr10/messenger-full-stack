import { useMemo } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { fetchMessages } from "../api/message";
import type { Message } from "../types/chat";

type PageParam = { before_id?: number };
type Opts = { enabled?: boolean };

export function useMessagesInfinite(
  conversationId: number | undefined,
  pageSize = 50,
  opts: Opts = {}
) {
  const enabled = opts.enabled ?? !!conversationId;

  const query = useInfiniteQuery({
    queryKey: ["messages", conversationId ?? "none"],
    enabled, 
    queryFn: ({ pageParam }: { pageParam?: PageParam }) =>
      fetchMessages({
        conversationId: conversationId!, 
        limit: pageSize,
        before_id: pageParam?.before_id,
      }),
    initialPageParam: {} as PageParam,
    getNextPageParam: (lastPage: Message[]) => {
      if (!lastPage.length) return undefined;
      const firstId = lastPage[0].id;
      return { before_id: firstId };
    },
  });

  const items = useMemo<Message[]>(
    () => (query.data?.pages ?? []).flat(),
    [query.data]
  );

  return { ...query, items };
}
