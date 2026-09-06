"use client";

import { useSession } from "next-auth/react";
import { useEffect, useRef, useState } from "react";

import { TallyDot } from "@/components/ui/tally-dot";
import { useWorkspace } from "@/components/workspace/workspace-context";
import { apiFetch, ApiError } from "@/lib/api-client";
import type { ChatMessage, ChatTurn, MediaAsset } from "@/lib/types";

const TOOL_LABELS: Record<string, string> = {
  select_media_tool: "Memilih foto",
  generate_video_tool: "Generate video",
  generate_image_tool: "Generate gambar",
  generate_voiceover_tool: "Generate voiceover",
  create_project_tool: "Membuat project",
  render_project_tool: "Render video",
  prepare_publish_tool: "Menyiapkan publish",
  apply_template_tool: "Menerapkan template",
};

// Persistent across all 4 studio stages (DESIGN_SYSTEM.md-compliant "tally light" tool
// activity instead of a plain text log). Docked as a column on large screens; a
// floating-button + full-screen drawer below `lg` (see the single-instance note on
// `panelClasses` — it must stay one mounted component, not two, or the conversation
// would fork into two histories).
export function ChatPanel() {
  const { data: session } = useSession();
  const token = session?.accessToken;
  const workspace = useWorkspace();

  const [open, setOpen] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pendingAssetId, setPendingAssetId] = useState<string | null>(null);
  const [attachedName, setAttachedName] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function handleAttach(files: FileList | null) {
    const file = files?.[0];
    if (!file || !token) return;
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const asset = await apiFetch<MediaAsset>("/media/upload", {
        token,
        method: "POST",
        body: formData,
        isForm: true,
      });
      setPendingAssetId(asset.id);
      setAttachedName(asset.original_filename);
      workspace.refreshAssets();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload gagal.");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleSend() {
    const content = input.trim();
    if (!token || !content || isSending) return;

    setInput("");
    setIsSending(true);
    setError(null);
    setMessages((current) => [
      ...current,
      {
        id: `local-${Date.now()}`,
        role: "user",
        content,
        tool_name: null,
        tool_result: null,
        created_at: new Date().toISOString(),
      },
    ]);

    try {
      const turn = await apiFetch<ChatTurn>("/chat/messages", {
        token,
        method: "POST",
        body: { content, conversation_id: conversationId, media_asset_id: pendingAssetId },
      });
      setConversationId(turn.conversation_id);
      // `handle_turn` (backend) always persists the just-sent user message first, so
      // `turn.messages[0]` is the same message already appended optimistically above —
      // drop it here instead of rendering it twice.
      const [, ...rest] = turn.messages;
      setMessages((current) => [...current, ...rest]);
      for (const message of rest) {
        if (message.role === "tool" && message.tool_name && message.tool_result) {
          workspace.applyToolResult(message.tool_name, message.tool_result);
        }
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Gagal mengirim pesan.");
    } finally {
      setIsSending(false);
      setPendingAssetId(null);
      setAttachedName(null);
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Buka asisten AI"
        className="fixed bottom-5 right-5 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-rec text-sm font-medium text-canvas shadow-lg transition-transform hover:scale-105 lg:hidden"
      >
        AI
      </button>

      <div
        className={`${
          open ? "flex" : "hidden"
        } fixed inset-0 z-50 flex-col bg-canvas lg:static lg:z-auto lg:flex lg:h-[calc(100vh-8rem)] lg:w-96 lg:shrink-0 lg:rounded-md lg:border lg:border-panel lg:bg-panel`}
      >
        <div className="flex items-center justify-between border-b border-panel px-4 py-3">
          <div>
            <p className="font-display text-sm text-ink">Asisten AI</p>
            <p className="text-xs text-ink-muted">
              Bisa generate, render, sampai siapkan publish untukmu.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="text-sm text-ink-muted hover:text-ink lg:hidden"
          >
            Tutup
          </button>
        </div>

        <div ref={scrollRef} className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4">
          {messages.length === 0 && (
            <p className="text-sm text-ink-muted">
              Coba: &quot;generate video dari foto ini&quot; atau &quot;buatkan gambar produk
              minimalis&quot;.
            </p>
          )}
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))}
          {isSending && (
            <div className="flex items-center gap-2 text-xs text-ink-muted">
              <TallyDot status="processing" /> Memproses…
            </div>
          )}
        </div>

        {error && (
          <p className="mx-4 mb-2 rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-xs text-alert">
            {error}
          </p>
        )}

        <div className="border-t border-panel p-3">
          {attachedName && (
            <p className="mb-2 truncate text-xs text-signal">Terlampir: {attachedName}</p>
          )}
          <div className="flex items-end gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => handleAttach(e.target.files)}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              aria-label="Lampirkan foto"
              className="shrink-0 rounded-md border border-panel-raised px-2.5 py-2 text-xs text-ink-muted transition-colors hover:bg-panel-raised hover:text-ink"
            >
              +
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              rows={1}
              placeholder="Tulis perintah untuk asisten…"
              className="flex-1 resize-none rounded-md border border-panel-raised bg-canvas px-3 py-2 text-sm text-ink outline-none focus:border-rec"
            />
            <button
              type="button"
              onClick={handleSend}
              disabled={!input.trim() || isSending}
              className="shrink-0 rounded-md bg-rec px-3 py-2 text-xs font-medium text-canvas transition-colors hover:bg-rec/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Kirim
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function ChatBubble({ message }: { message: ChatMessage }) {
  if (message.role === "tool") {
    return (
      <div className="flex items-center gap-2 self-start rounded-md bg-panel-raised px-3 py-1.5 text-xs text-ink-muted">
        <TallyDot status="success" />
        {TOOL_LABELS[message.tool_name ?? ""] ?? message.tool_name}
      </div>
    );
  }

  const isUser = message.role === "user";
  return (
    <div
      className={`max-w-[85%] rounded-md px-3 py-2 text-sm ${
        isUser ? "self-end bg-rec text-canvas" : "self-start bg-panel-raised text-ink"
      }`}
    >
      {isUser ? message.content : <FormattedReply text={message.content} />}
    </div>
  );
}

// Gemini/Claude replies come back as light markdown (**bold**, "1. "/"- " lists). No
// markdown-rendering dependency is worth adding for this alone (the frontend
// deliberately stays dependency-light, see workspace-context.tsx) — this covers the
// two patterns that actually show up, building React nodes directly rather than
// injecting HTML.
function FormattedReply({ text }: { text: string }) {
  const lines = text.split("\n");
  return (
    <div className="flex flex-col gap-1.5">
      {lines.map((line, index) => {
        const listMatch = line.match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
        const body = listMatch ? listMatch[1] : line;
        return (
          <p key={index} className={listMatch ? "pl-3" : undefined}>
            {listMatch ? "• " : ""}
            {renderBoldSegments(body)}
          </p>
        );
      })}
    </div>
  );
}

function renderBoldSegments(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }
    return <span key={index}>{part}</span>;
  });
}
