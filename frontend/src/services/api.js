/**
 * API helper — all calls to the Flask backend go through here.
 */

const BASE_URL = process.env.NODE_ENV === "development" ? "http://localhost:5000/api" : "/api";

/** Get list of all files with tags */
export async function getFiles() {
  const res = await fetch(`${BASE_URL}/files`);
  return res.json();
}

/** Upload a file */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

/** Analyze a file (extract text + generate tags) */
export async function analyzeFile(filePath) {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path: filePath }),
  });
  return res.json();
}

/** Analyze multiple files at once */
export async function analyzeBatch(paths) {
  const res = await fetch(`${BASE_URL}/analyze/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paths }),
  });
  return res.json();
}

/** Search files by query */
export async function searchFiles(query) {
  const res = await fetch(`${BASE_URL}/search?q=${encodeURIComponent(query)}`);
  return res.json();
}

/** Update tags for a file */
export async function updateFileTags(filePath, tags) {
  const res = await fetch(`${BASE_URL}/tags/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path: filePath, tags }),
  });
  return res.json();
}

/** Open file locally on the computer */
export async function openFileLocal(filePath) {
  const res = await fetch(`${BASE_URL}/open`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path: filePath }),
  });
  return res.json();
}

/** Bulk delete files */
export async function deleteFiles(paths) {
  const res = await fetch(`${BASE_URL}/files/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paths }),
  });
  return res.json();
}

