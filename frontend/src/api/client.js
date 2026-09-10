// Shared API client for talking to the CraftMitra backend.
//
// Set VITE_API_BASE_URL in frontend/.env to point at your deployed
// backend, e.g.:
//   VITE_API_BASE_URL=https://your-backend.example.com

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const TOKEN_KEY = "craftmitra_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

async function request(path, { method = "GET", body, auth = true, isForm = false } = {}) {
  const headers = {};

  if (!isForm) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body !== undefined ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    // No JSON body (e.g. 204 No Content) - that's fine.
  }

  if (!response.ok) {
    const message = data?.detail || `Request failed (${response.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}

export const api = {
  get: (path, options) => request(path, { ...options, method: "GET" }),
  post: (path, body, options) => request(path, { ...options, method: "POST", body }),
  patch: (path, body, options) => request(path, { ...options, method: "PATCH", body }),
  delete: (path, options) => request(path, { ...options, method: "DELETE" }),

  // For uploading a captured photo or recorded audio clip. `fields` lets
  // callers attach extra form fields alongside the file (e.g. the spoken
  // language for a voice recording).
  uploadFile: (path, file, fieldName = "file", fields = {}, options) => {
    const formData = new FormData();
    formData.append(fieldName, file);

    Object.entries(fields || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value);
      }
    });

    return request(path, { ...options, method: "POST", body: formData, isForm: true });
  },
};

export { API_BASE_URL };