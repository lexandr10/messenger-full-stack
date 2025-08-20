import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchConversations, createConversation } from "../api/conversations";
import { qk } from "../api/keys";

export function useConversations() {
  return useQuery({
    queryKey: qk.conversations(),
    queryFn: fetchConversations,
  });
}

export function useCreateConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (partner_id: number) => createConversation(partner_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.conversations() });
    },
  });
}
