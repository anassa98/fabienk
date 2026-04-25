import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useCities() {
  return useQuery({
    queryKey: ["cities"],
    queryFn: api.listCities,
  });
}

export function useCity(code) {
  return useQuery({
    queryKey: ["city", code],
    queryFn: () => api.getCity(code),
    enabled: !!code,
  });
}

export function useCityRooftops(code) {
  return useQuery({
    queryKey: ["city", code, "rooftops"],
    queryFn: () => api.getCityRooftops(code),
    enabled: !!code,
  });
}

export function useCityRooftopsTable(code) {
  return useQuery({
    queryKey: ["city", code, "rooftops-table"],
    queryFn: () => api.getCityRooftopsTable(code),
    enabled: !!code,
  });
}

export function useCityStats(code) {
  return useQuery({
    queryKey: ["city", code, "stats"],
    queryFn: () => api.getCityStats(code),
    enabled: !!code,
  });
}

export function useCityFinancial(code) {
  return useQuery({
    queryKey: ["city", code, "financial"],
    queryFn: () => api.getCityFinancial(code),
    enabled: !!code,
    retry: false,
  });
}
