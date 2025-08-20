import { http } from "./http";

export type UploadMeta = {
  file_path: string;
  file_name: string;
  mime: string | null;
  size_bytes: number | null;
  storage: string; // "cloudinary"
};

export async function uploadFiles(
  files: File[],
  folder?: string
): Promise<UploadMeta[]> {
  const form = new FormData();
  if (folder) form.append("folder", folder);
  files.forEach((f) => form.append("files", f));
  const res = await http.post(`/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
