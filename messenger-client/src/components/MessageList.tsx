import { useState } from "react";
import type { Message } from "../types/chat";

type Props = {
  items: Message[];
  onEdit: (id: number, content: string) => void;
  onDelete: (ids: number[]) => void;
  currentUserId?: number;
};

export default function MessageList({ items, onEdit, onDelete, currentUserId }: Props) {
	const [selected, setSelected] = useState<Set<number>>(new Set());
  const [editingId, setEditingId] = useState<number | null>(null);
	const [editValue, setEditValue] = useState("");

	

	const toggleSelect = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
	};
	const isImage = (mt?: string | null) => !!mt && mt.startsWith("image/");

	function cloudinaryThumb(url: string, { w = 256, h = 256 } = {}) {
    try {
      const u = new URL(url);
      if (!u.pathname.includes("/upload/")) return url;
      u.pathname = u.pathname.replace(
        "/upload/",
        `/upload/c_fill,w_${w},h_${h},q_auto,f_auto/`
      );
      return u.toString();
    } catch {
      return url;
    }
  }
	
	const startEdit = (m: Message) => {

		if (currentUserId && m.sender_id !== currentUserId) return;
    if (m.deleted) return;
    setEditingId(m.id);
    setEditValue(m.content ?? "");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditValue("");
  };

  const saveEdit = () => {
    if (!editingId) return;
    const content = editValue.trim();
    if (!content) return;
    onEdit(editingId, content);
    setEditingId(null);
    setEditValue("");
  };

  const removeSelected = () => {
    if (selected.size === 0) return;
    onDelete([...selected]);
    setSelected(new Set());
  };
	

  return (
    <div className="flex flex-col gap-3">
      {items.length > 0 && (
        <div className="flex justify-between items-center text-sm text-slate-600">
          <div>Messages: {items.length}</div>
          <button
            className="px-3 py-1 rounded-lg bg-rose-600 text-white disabled:opacity-50"
            disabled={selected.size === 0}
            onClick={removeSelected}
            title="Delete selected"
          >
            Delete selected ({selected.size})
          </button>
        </div>
      )}

      {items.map((m) => {
        const mine = currentUserId ? m.sender_id === currentUserId : false;
        const isEditing = editingId === m.id;

        return (
          <div
            key={m.id}
            className={`rounded-xl border p-3 bg-white shadow-sm ${
              mine ? "border-indigo-200" : "border-slate-200"
            }`}
          >
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <input
                type="checkbox"
                className="mr-1"
                checked={selected.has(m.id)}
                onChange={() => toggleSelect(m.id)}
                title="Select to delete"
                disabled={!mine || m.deleted}
              />
              <span>#{m.id}</span>
              <span>•</span>
              <span>from: {m.sender_id}</span>
              {m.created_at && (
                <>
                  <span>•</span>
                  <span>{new Date(m.created_at).toLocaleString()}</span>
                </>
              )}
              {m.is_edited && (
                <span className="ml-2 italic text-amber-600">(edited)</span>
              )}
              {m.deleted && (
                <span className="ml-2 italic text-rose-600">(deleted)</span>
              )}
            </div>

            {!isEditing ? (
              <div
                className={`mt-2 whitespace-pre-wrap ${
                  m.deleted ? "text-slate-400 italic" : ""
                }`}
              >
                {m.deleted ? "(message removed)" : m.content ?? ""}
              </div>
            ) : (
              <div className="mt-2 flex gap-2">
                <input
                  className="flex-1 rounded-lg border px-3 py-2"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                />
                <button
                  className="px-3 py-2 rounded-lg bg-slate-200"
                  onClick={cancelEdit}
                >
                  Cancel
                </button>
                <button
                  className="px-3 py-2 rounded-lg bg-indigo-600 text-white"
                  onClick={saveEdit}
                >
                  Save
                </button>
              </div>
            )}

            {m.attachments && m.attachments.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-3">
                {m.attachments.map((a, idx) => {
                  if (isImage(a.mime_type)) {
                    const thumb = cloudinaryThumb(a.file_path, {
                      w: 256,
                      h: 256,
                    });
                    return (
                      <a
                        key={`${m.id}-${idx}-${a.file_path}`}
                        href={a.file_path}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="group block"
                        title={a.file_name}
                      >
                        <img
                          src={thumb}
                          alt={a.file_name}
                          loading="lazy"
                          className="
                w-36 h-36 sm:w-40 sm:h-40
                object-cover
                rounded-lg border bg-slate-50
                group-hover:opacity-90 transition
              "
                        />
                      </a>
                    );
                  }
                  return (
                    <a
                      key={`${m.id}-${idx}-${a.file_path}`}
                      href={a.file_path}
                      target="_blank"
                      rel="noreferrer noopener"
                      className="text-indigo-600 underline text-sm break-all"
                      title={a.mime_type ?? ""}
                    >
                      {a.file_name}
                    </a>
                  );
                })}
              </div>
            )}
            {mine && !m.deleted && (
              <div className="mt-3 flex gap-2">
                <button
                  className="px-3 py-1 rounded-lg bg-slate-200"
                  onClick={() => (isEditing ? cancelEdit() : startEdit(m))}
                  disabled={m.deleted}
                >
                  {isEditing ? "Cancel edit" : "Edit"}
                </button>
                <button
                  className="px-3 py-1 rounded-lg bg-rose-600 text-white"
                  onClick={() => onDelete([m.id])}
                  disabled={m.deleted}
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
