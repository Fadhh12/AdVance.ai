"use client";

import { useSession } from "next-auth/react";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { apiFetch, ApiError } from "@/lib/api-client";
import type { AIJob, ContentProject, MediaAsset, Post, ProjectMode, Template } from "@/lib/types";

const POLL_INTERVAL_MS = 2500;

// Phase 6R-4: single source of truth for the whole /studio workspace, replacing the
// near-identical local state + polling that used to live separately in
// generate/page.tsx, editor/[projectId]/page.tsx and publish/[projectId]/page.tsx.
// UI-triggered actions (the panels below) and chat-triggered actions (applyToolResult,
// called by ChatPanel after each tool result) both converge on this same state, so the
// canvas updates the same way no matter which one drove it.
type WorkspaceContextValue = {
  accessToken: string | undefined;

  photos: MediaAsset[] | null;
  selectedAssetId: string | null;
  selectAsset: (id: string | null) => void;
  uploadFiles: (files: FileList) => Promise<void>;
  isUploading: boolean;
  refreshAssets: () => Promise<void>;

  prompt: string;
  setPrompt: (value: string) => void;
  projectMode: ProjectMode;
  setProjectMode: (mode: ProjectMode) => void;
  applyTemplate: (template: Template) => void;

  job: AIJob | null;
  generate: () => Promise<void>;
  isGenerating: boolean;

  projectTitle: string;
  setProjectTitle: (value: string) => void;
  project: ContentProject | null;
  createProject: () => Promise<void>;
  isCreatingProject: boolean;
  loadProject: (projectId: string) => Promise<void>;

  caption: string;
  setCaption: (value: string) => void;
  musicTrack: string;
  setMusicTrack: (value: string) => void;
  trimStart: string;
  setTrimStart: (value: string) => void;
  trimEnd: string;
  setTrimEnd: (value: string) => void;
  motionPreset: string;
  setMotionPreset: (value: string) => void;
  saveDraft: () => Promise<void>;
  isSavingDraft: boolean;
  render: () => Promise<void>;
  isRendering: boolean;

  posts: Post[] | null;
  preparePublish: () => Promise<void>;
  isPreparingPublish: boolean;
  markUploaded: (postId: string) => Promise<void>;

  error: string | null;
  clearError: () => void;

  applyToolResult: (toolName: string, result: Record<string, unknown>) => Promise<void>;
};

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function useWorkspace(): WorkspaceContextValue {
  const context = useContext(WorkspaceContext);
  if (!context) throw new Error("useWorkspace must be used inside WorkspaceProvider");
  return context;
}

function applyProjectFields(
  project: ContentProject,
  setCaption: (v: string) => void,
  setMusicTrack: (v: string) => void,
  setTrimStart: (v: string) => void,
  setTrimEnd: (v: string) => void,
  setMotionPreset: (v: string) => void,
) {
  setCaption(project.caption ?? "");
  setMusicTrack(project.music_track ?? "");
  setTrimStart(project.trim_start_seconds?.toString() ?? "");
  setTrimEnd(project.trim_end_seconds?.toString() ?? "");
  setMotionPreset(project.motion_preset ?? "");
}

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { data: session } = useSession();
  const accessToken = session?.accessToken;

  const [photos, setPhotos] = useState<MediaAsset[] | null>(null);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const [prompt, setPrompt] = useState("");
  const [projectMode, setProjectMode] = useState<ProjectMode>("product_ad");

  const [job, setJob] = useState<AIJob | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const [projectTitle, setProjectTitle] = useState("");
  const [project, setProject] = useState<ContentProject | null>(null);
  const [isCreatingProject, setIsCreatingProject] = useState(false);

  const [caption, setCaption] = useState("");
  const [musicTrack, setMusicTrack] = useState("");
  const [trimStart, setTrimStart] = useState("");
  const [trimEnd, setTrimEnd] = useState("");
  const [motionPreset, setMotionPreset] = useState("");
  const [isSavingDraft, setIsSavingDraft] = useState(false);
  const [isRendering, setIsRendering] = useState(false);

  const [posts, setPosts] = useState<Post[] | null>(null);
  const [isPreparingPublish, setIsPreparingPublish] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const clearError = useCallback(() => setError(null), []);

  const refreshAssets = useCallback(async () => {
    if (!accessToken) return;
    try {
      const assets = await apiFetch<MediaAsset[]>("/media", { token: accessToken });
      setPhotos(assets.filter((asset) => asset.type === "photo"));
    } catch {
      // Media Library page still shows the authoritative list/errors; the picker here
      // just stays stale until the next successful refresh.
    }
  }, [accessToken]);

  // Initial fetch on mount/session-ready — guarded so a stale response from an
  // unmounted/re-run effect never overwrites newer state.
  useEffect(() => {
    let ignore = false;
    if (accessToken) {
      apiFetch<MediaAsset[]>("/media", { token: accessToken })
        .then((assets) => {
          if (!ignore) setPhotos(assets.filter((asset) => asset.type === "photo"));
        })
        .catch(() => {
          // handled the same way as refreshAssets() below — stays stale, no toast
        });
    }
    return () => {
      ignore = true;
    };
  }, [accessToken]);

  const selectAsset = useCallback((id: string | null) => setSelectedAssetId(id), []);

  const uploadFiles = useCallback(
    async (files: FileList) => {
      if (!accessToken || files.length === 0) return;
      setError(null);
      setIsUploading(true);
      try {
        let lastUploaded: MediaAsset | null = null;
        for (const file of Array.from(files)) {
          const formData = new FormData();
          formData.append("file", file);
          lastUploaded = await apiFetch<MediaAsset>("/media/upload", {
            token: accessToken,
            method: "POST",
            body: formData,
            isForm: true,
          });
        }
        await refreshAssets();
        if (lastUploaded) setSelectedAssetId(lastUploaded.id);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Upload gagal.");
      } finally {
        setIsUploading(false);
      }
    },
    [accessToken, refreshAssets],
  );

  const applyTemplate = useCallback((template: Template) => {
    setPrompt(template.prompt_preset);
    setProjectMode(template.mode);
  }, []);

  const generate = useCallback(async () => {
    if (!accessToken || !selectedAssetId) return;
    setError(null);
    setIsGenerating(true);
    try {
      const created = await apiFetch<AIJob>("/ai/generate-video", {
        token: accessToken,
        method: "POST",
        body: { source_asset_id: selectedAssetId, prompt: prompt || null },
      });
      setJob(created);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Generate gagal.");
    } finally {
      setIsGenerating(false);
    }
  }, [accessToken, selectedAssetId, prompt]);

  const adoptProject = useCallback(
    async (projectId: string) => {
      if (!accessToken) return;
      const loaded = await apiFetch<ContentProject>(`/projects/${projectId}`, {
        token: accessToken,
      });
      setProject(loaded);
      applyProjectFields(loaded, setCaption, setMusicTrack, setTrimStart, setTrimEnd, setMotionPreset);
    },
    [accessToken],
  );

  const loadProject = useCallback(
    async (projectId: string) => {
      try {
        await adoptProject(projectId);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Project tidak ditemukan.");
      }
    },
    [adoptProject],
  );

  const createProject = useCallback(async () => {
    if (!accessToken || !job || job.status !== "success" || !projectTitle.trim()) return;
    setError(null);
    setIsCreatingProject(true);
    try {
      const created = await apiFetch<ContentProject>("/projects", {
        token: accessToken,
        method: "POST",
        body: { title: projectTitle.trim(), mode: projectMode, source_job_id: job.id },
      });
      setProject(created);
      applyProjectFields(created, setCaption, setMusicTrack, setTrimStart, setTrimEnd, setMotionPreset);
      window.history.replaceState(null, "", `/studio/${created.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Membuat project gagal.");
    } finally {
      setIsCreatingProject(false);
    }
  }, [accessToken, job, projectTitle, projectMode]);

  const saveDraft = useCallback(async () => {
    if (!accessToken || !project) return;
    setError(null);
    setIsSavingDraft(true);
    try {
      const updated = await apiFetch<ContentProject>(`/projects/${project.id}`, {
        token: accessToken,
        method: "PATCH",
        body: {
          caption: caption || null,
          music_track: musicTrack || null,
          trim_start_seconds: trimStart === "" ? null : Number(trimStart),
          trim_end_seconds: trimEnd === "" ? null : Number(trimEnd),
          motion_preset: motionPreset || null,
        },
      });
      setProject(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Simpan draft gagal.");
    } finally {
      setIsSavingDraft(false);
    }
  }, [accessToken, project, caption, musicTrack, trimStart, trimEnd, motionPreset]);

  const render = useCallback(async () => {
    if (!accessToken || !project) return;
    setError(null);
    setIsRendering(true);
    try {
      const updated = await apiFetch<ContentProject>(`/projects/${project.id}/render`, {
        token: accessToken,
        method: "POST",
      });
      setProject(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Render gagal.");
    } finally {
      setIsRendering(false);
    }
  }, [accessToken, project]);

  const preparePublish = useCallback(async () => {
    if (!accessToken || !project) return;
    setError(null);
    setIsPreparingPublish(true);
    try {
      const created = await apiFetch<Post[]>(`/projects/${project.id}/posts`, {
        token: accessToken,
        method: "POST",
      });
      setPosts(created);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Menyiapkan publish gagal.");
    } finally {
      setIsPreparingPublish(false);
    }
  }, [accessToken, project]);

  const markUploaded = useCallback(
    async (postId: string) => {
      if (!accessToken) return;
      try {
        const updated = await apiFetch<Post>(`/posts/${postId}/mark-uploaded`, {
          token: accessToken,
          method: "POST",
        });
        setPosts((current) => (current ? current.map((p) => (p.id === postId ? updated : p)) : current));
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Gagal menandai upload.");
      }
    },
    [accessToken],
  );

  // Load posts for the current project once (e.g. when a bookmarked /studio/[id] URL
  // is opened directly on an already-rendered project).
  useEffect(() => {
    if (!accessToken || !project) return;
    apiFetch<Post[]>(`/projects/${project.id}/posts`, { token: accessToken })
      .then(setPosts)
      .catch(() => {
        // no posts prepared yet — normal, leave `posts` as-is
      });
    // Only when the project identity changes, not on every field edit.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken, project?.id]);

  // One centralized poll effect (replaces the 3 near-identical setInterval blocks the
  // old per-stage pages each had) — covers the generate job, a render in flight, and
  // any exports still being prepared, whichever currently apply.
  useEffect(() => {
    if (!accessToken) return;
    const jobActive = job !== null && job.status !== "success" && job.status !== "failed";
    const renderActive =
      project !== null &&
      (project.render_status === "queued" || project.render_status === "processing");
    const postsActive =
      posts?.some((p) => p.export_status === "queued" || p.export_status === "processing") ??
      false;
    if (!jobActive && !renderActive && !postsActive) return;

    const interval = setInterval(async () => {
      try {
        if (jobActive && job) {
          setJob(await apiFetch<AIJob>(`/ai/jobs/${job.id}`, { token: accessToken }));
        }
        if (renderActive && project) {
          setProject(await apiFetch<ContentProject>(`/projects/${project.id}`, { token: accessToken }));
        }
        if (postsActive && project) {
          setPosts(await apiFetch<Post[]>(`/projects/${project.id}/posts`, { token: accessToken }));
        }
      } catch {
        // transient poll failure — next tick retries, no need to surface a toast for it
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [accessToken, job, project, posts]);

  // Bridge from the chat agent (Phase 6R-6): every `role: "tool"` message in a chat
  // turn carries a result shaped exactly like the corresponding UI action's response
  // (see backend/app/services/agent_tools/*), so a chat-driven action updates the same
  // canvas state a button click would.
  const applyToolResult = useCallback(
    async (toolName: string, result: Record<string, unknown>) => {
      if (!accessToken) return;
      try {
        switch (toolName) {
          case "select_media_tool": {
            const id = result.media_asset_id;
            if (typeof id === "string") setSelectedAssetId(id);
            break;
          }
          case "generate_image_tool":
          case "generate_voiceover_tool": {
            await refreshAssets();
            const id = result.media_asset_id;
            if (typeof id === "string" && toolName === "generate_image_tool") {
              setSelectedAssetId(id);
            }
            break;
          }
          case "generate_video_tool": {
            const jobId = result.job_id;
            if (typeof jobId === "string") {
              setJob(await apiFetch<AIJob>(`/ai/jobs/${jobId}`, { token: accessToken }));
            }
            break;
          }
          case "create_project_tool":
          case "render_project_tool": {
            const projectId = result.project_id;
            if (typeof projectId === "string") {
              await adoptProject(projectId);
              window.history.replaceState(null, "", `/studio/${projectId}`);
            }
            break;
          }
          case "prepare_publish_tool": {
            if (project) {
              setPosts(await apiFetch<Post[]>(`/projects/${project.id}/posts`, { token: accessToken }));
            }
            break;
          }
          case "apply_template_tool": {
            if (typeof result.prompt_preset === "string") setPrompt(result.prompt_preset);
            if (result.mode === "product_ad" || result.mode === "affiliate") {
              setProjectMode(result.mode);
            }
            break;
          }
          default:
            break;
        }
      } catch {
        // Best-effort sync — the assistant's reply already told the user what
        // happened; a failed refresh here just means the canvas catches up on the
        // next poll tick instead of immediately.
      }
    },
    [accessToken, project, refreshAssets, adoptProject],
  );

  const value = useMemo<WorkspaceContextValue>(
    () => ({
      accessToken,
      photos,
      selectedAssetId,
      selectAsset,
      uploadFiles,
      isUploading,
      refreshAssets,
      prompt,
      setPrompt,
      projectMode,
      setProjectMode,
      applyTemplate,
      job,
      generate,
      isGenerating,
      projectTitle,
      setProjectTitle,
      project,
      createProject,
      isCreatingProject,
      loadProject,
      caption,
      setCaption,
      musicTrack,
      setMusicTrack,
      trimStart,
      setTrimStart,
      trimEnd,
      setTrimEnd,
      motionPreset,
      setMotionPreset,
      saveDraft,
      isSavingDraft,
      render,
      isRendering,
      posts,
      preparePublish,
      isPreparingPublish,
      markUploaded,
      error,
      clearError,
      applyToolResult,
    }),
    [
      accessToken,
      photos,
      selectedAssetId,
      selectAsset,
      uploadFiles,
      isUploading,
      refreshAssets,
      prompt,
      projectMode,
      applyTemplate,
      job,
      generate,
      isGenerating,
      projectTitle,
      project,
      createProject,
      isCreatingProject,
      loadProject,
      caption,
      musicTrack,
      trimStart,
      trimEnd,
      motionPreset,
      saveDraft,
      isSavingDraft,
      render,
      isRendering,
      posts,
      preparePublish,
      isPreparingPublish,
      markUploaded,
      error,
      clearError,
      applyToolResult,
    ],
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}
