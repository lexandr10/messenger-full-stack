export type Attachment = {
  id: number;
  file_name: string;
  mime_type?: string | null;
  size_bytes?: number | null;
  storage: string;
  file_path: string;
};

export type Message = {
  id: number;
  conversation_id: number;
  sender_id: number;
  content: string | null;
  is_edited: boolean;
  deleted: boolean;
  created_at?: string;
  attachments?: Attachment[];
};
export type NewAttachmentIn = {
  file_path: string;
  file_name?: string;
  mime?: string;
  size_bytes?: number;
  storage?: string; 
};

export type UserLite = { id: number; username?: string; email?: string };

export type Conversation = {
  id: number;
  user1_id: number;
  user2_id: number;
  created_at?: string;
  peer?: UserLite | null;
};