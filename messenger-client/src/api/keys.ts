export const qk = {
  conversations: () => ["conversations"] as const,
  conversation: (id: number) => ["conversation", id] as const,
  messages: (convId: number) => ["messages", convId] as const,
};
