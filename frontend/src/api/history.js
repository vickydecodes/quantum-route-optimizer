import axios from "axios";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";

export const fetchHistory = async () => {
  const res = await axios.get(`${API}/history`);
  return res.data.history;
};
