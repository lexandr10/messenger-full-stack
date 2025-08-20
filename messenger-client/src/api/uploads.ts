import { http } from "./http";

export type UploadMeta = {
  file_path: string;
  file_name: string;
  mime: string;
  size_bytes: number;
  storage: string; // "cloudinary"
  provider_id: string;
  resource_type?: string;
};

export async function uploadFiles(
  files: File[],
  conversationId?: number
): Promise<UploadMeta[]> {
  const fd = new FormData();
  files.forEach((f) => fd.append("files", f)); 

  const url = conversationId
    ? `/upload?conversation_id=${conversationId}`
    : `/upload`;
  const { data } = await http.post<UploadMeta[]>(url, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
