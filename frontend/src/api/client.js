import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

export default client;

export const api = {
  listCities: () => client.get("/cities/").then((r) => r.data),
  getCity: (code) => client.get(`/cities/${code}/`).then((r) => r.data),
  getCityRooftops: (code) =>
    client.get(`/cities/${code}/rooftops/`).then((r) => r.data),
  getCityRooftopsTable: (code) =>
    client.get(`/cities/${code}/rooftops-table/`).then((r) => r.data),
  getCityStats: (code) =>
    client.get(`/cities/${code}/stats/`).then((r) => r.data),
  getCityFinancial: (code) =>
    client.get(`/cities/${code}/financial/`).then((r) => r.data),
  getRooftopProductivity: (id) =>
    client.get(`/rooftops/${id}/productivity/`).then((r) => r.data),
  getRooftopSocial: (id) =>
    client.get(`/rooftops/${id}/social/`).then((r) => r.data),
  getRooftopEnvironmental: (id) =>
    client.get(`/rooftops/${id}/environmental/`).then((r) => r.data),
  runScenario: (payload) =>
    client.post("/scenarios/", payload).then((r) => r.data),
};
