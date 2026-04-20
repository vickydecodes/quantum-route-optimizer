import axios from "axios";

export const fetchHistory = async () => {
  const res = await axios.get("http://127.0.0.1:8000/api/history");
  return res.data.history;
};
