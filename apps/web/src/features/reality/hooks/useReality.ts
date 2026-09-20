import { useQuery } from "@tanstack/react-query";

import { fetchConcept, fetchConcepts, fetchDomains, fetchRelatedConcepts } from "../api/reality";
import type { ConceptFilters } from "../types/reality";

export function useDomains() {
  return useQuery({ queryKey: ["reality", "domains"], queryFn: fetchDomains });
}

export function useConcepts(filters: ConceptFilters = {}) {
  return useQuery({
    queryKey: ["reality", "concepts", filters],
    queryFn: () => fetchConcepts(filters),
  });
}

export function useConcept(slug: string | undefined) {
  return useQuery({
    queryKey: ["reality", "concept", slug],
    queryFn: () => fetchConcept(slug as string),
    enabled: Boolean(slug),
  });
}

export function useRelatedConcepts(slug: string | undefined) {
  return useQuery({
    queryKey: ["reality", "concept", slug, "related"],
    queryFn: () => fetchRelatedConcepts(slug as string),
    enabled: Boolean(slug),
  });
}
