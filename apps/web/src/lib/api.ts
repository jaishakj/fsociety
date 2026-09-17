import axios from "axios";

const apiBaseUrl =
  import.meta.env.VITE_API_URL ??
  "https://api-fsociety.vercel.app/api/v1";

export const api = axios.create({
  baseURL: apiBaseUrl,
});

export function withAuth(token: string) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}
