import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

export function useRunScenario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.runScenario,
    onSuccess: (data) => {
      const code = data?.city?.city_code;
      if (code) {
        qc.invalidateQueries({ queryKey: ["city", code] });
      }
    },
  });
}
