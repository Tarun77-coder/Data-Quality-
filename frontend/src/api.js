import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.warn(
    "Supabase environment variables are missing. Create frontend/.env from .env.example."
  );
}

export const supabase = createClient(
  SUPABASE_URL || "https://placeholder.supabase.co",
  SUPABASE_ANON_KEY || "placeholder-anon-key"
);

async function authHeader() {
  const { data, error } = await supabase.auth.getSession();
  if (error) throw new Error(error.message);

  const token = data?.session?.access_token;
  if (!token) throw new Error("You are not authenticated. Please log in again.");

  return { Authorization: `Bearer ${token}` };
}

async function parseError(response, fallback) {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") return body.detail;
    if (Array.isArray(body?.detail)) {
      return body.detail.map((item) => item.msg).join(", ");
    }
  } catch {
    // Response was not JSON.
  }
  return fallback;
}

export async function uploadFile(file) {
  const headers = await authHeader();
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    throw new Error(await parseError(res, "Upload failed"));
  }
  return res.json();
}

export async function runChecks({ runId, expectedColumns, customRule }) {
  const headers = await authHeader();
  const res = await fetch(`${API_BASE_URL}/checks/run`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({
      run_id: runId,
      expected_columns: expectedColumns?.length ? expectedColumns : null,
      custom_rule: customRule,
    }),
  });

  if (!res.ok) {
    throw new Error(await parseError(res, "Checks failed"));
  }
  return res.json();
}

export async function downloadResults(runId, format) {
  const headers = await authHeader();
  const res = await fetch(
    `${API_BASE_URL}/results/${encodeURIComponent(runId)}/export?format=${encodeURIComponent(format)}`,
    { headers }
  );

  if (!res.ok) {
    throw new Error(await parseError(res, "Export failed"));
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `results_${runId}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
