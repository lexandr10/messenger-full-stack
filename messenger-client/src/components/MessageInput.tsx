import { useState } from "react";
import { uploadFiles, type UploadMeta } from "../api/uploads";
import type { NewAttachmentIn } from "../types/chat";

type Props = {
  conversationId: number;
  onSend: (payload: {
    content: string;
    attachments?: NewAttachmentIn[];
  }) => void;
  maxFiles?: number;
};

const ACCEPT = "image/*,application/pdf,text/plain";
const MAX_MB = 20; // синхронизировано с бэком

export default function MessageInput({ conversationId, onSend, maxFiles = 10 }: Props) {
	const [text, setText] = useState("");
	const [localFiles, setLocalFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
	const [err, setErr] = useState<string | null>(null);

	const onPick: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const files = Array.from(e.target.files ?? []);
    const next = [...localFiles, ...files].slice(0, maxFiles);
    // простая валидация
    const bad = next.find((f) => f.size > MAX_MB * 1024 * 1024);
    if (bad) {
      setErr(`"${bad.name}" exceeds ${MAX_MB}MB`);
      return;
    }
    setErr(null);
    setLocalFiles(next);
    e.currentTarget.value = ""; // чтобы можно было выбрать те же файлы снова
  };

  const removeAt = (i: number) => {
    const next = [...localFiles];
    next.splice(i, 1);
    setLocalFiles(next);
  };

  const doSend = async () => {
    if (!text.trim() && localFiles.length === 0) return;

    setBusy(true);
    setErr(null);
    try {
      let attachments: NewAttachmentIn[] | undefined = undefined;
      if (localFiles.length) {
        const metas: UploadMeta[] = await uploadFiles(
          localFiles,
          conversationId
        );
        attachments = metas.map((m) => ({
          file_path: m.file_path,
          file_name: m.file_name,
          mime: m.mime, // бэк ждёт "mime"
          size_bytes: m.size_bytes,
          storage: m.storage,
        }));
      }

      onSend({ content: text.trim(), attachments });
      setText("");
      setLocalFiles([]);
    } catch (e: any) {
      setErr(e?.response?.data?.detail ?? String(e));
    } finally {
      setBusy(false);
    }
  };
	
  return (
    <div className="rounded-xl border bg-white p-3 flex flex-col gap-2">
      <textarea
        className="w-full resize-none rounded-lg border px-3 py-2"
        rows={3}
        placeholder="Write a message…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={busy}
      />

      {localFiles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {localFiles.map((f, i) => (
            <div
              key={`${f.name}-${i}`}
              className="flex items-center gap-2 rounded-lg border px-2 py-1"
            >
              <span className="text-sm">{f.name}</span>
              <button
                className="text-xs text-rose-600"
                onClick={() => removeAt(i)}
                type="button"
              >
                remove
              </button>
            </div>
          ))}
        </div>
      )}

      {err && <div className="text-sm text-rose-600">{err}</div>}

      <div className="flex items-center justify-between">
        <label className="inline-flex items-center gap-2 text-sm">
          <span className="rounded-lg border px-3 py-1 bg-slate-100">
            Attach
          </span>
          <input
            type="file"
            multiple
            accept={ACCEPT}
            onChange={onPick}
            className="hidden"
          />
        </label>

        <button
          className="rounded-lg bg-indigo-600 text-white px-4 py-2 disabled:opacity-50"
          onClick={doSend}
          disabled={busy || (!text.trim() && localFiles.length === 0)}
          type="button"
        >
          Send
        </button>
      </div>
    </div>
  );
}
