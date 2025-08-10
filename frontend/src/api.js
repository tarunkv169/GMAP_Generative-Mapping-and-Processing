import axios from "axios";
const API = axios.create({ baseURL: "http://localhost:8000" });

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const r = await API.post("/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
  return r.data;
}

export async function uploadYoutube(url) {
  const form = new FormData();
  form.append("youtube_url", url);
  const r = await API.post("/upload", form);
  return r.data;
}

export async function generateMap(query) {
  const r = await API.post("/generate-map", { query });
  return r.data;
}
