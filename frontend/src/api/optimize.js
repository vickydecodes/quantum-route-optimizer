import axios from "axios";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";

export const optimizeRoutes = async (locations) => {
  const res = await axios.post(`${API}/optimize`, { locations });
  return res.data;
};

export const fetchHistory = async (limit = 10) => {
  const res = await axios.get(`${API}/history`, { params: { limit } });
  return res.data.history;
};