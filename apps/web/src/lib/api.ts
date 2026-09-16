import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api/v1",
});

export function withAuth(token: string) {
  return { headers: { Authorization: `Bearer ${token}` } };
}
