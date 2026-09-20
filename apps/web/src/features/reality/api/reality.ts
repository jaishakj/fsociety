import { api } from "@/lib/api";

import type {
  Concept,
  ConceptFilters,
  ConceptListResponse,
  ConceptRelation,
  Domain,
} from "../types/reality";

export async function fetchDomains(): Promise<Domain[]> {
  const { data } = await api.get<Domain[]>("/reality/topics");
  return data;
}

export async function fetchConcepts(filters: ConceptFilters = {}): Promise<ConceptListResponse> {
  const { data } = await api.get<ConceptListResponse>("/reality/concepts", { params: filters });
  return data;
}

export async function fetchConcept(slug: string): Promise<Concept> {
  const { data } = await api.get<Concept>(`/reality/concepts/${slug}`);
  return data;
}

export async function fetchRelatedConcepts(slug: string): Promise<ConceptRelation[]> {
  const { data } = await api.get<ConceptRelation[]>(`/reality/concepts/${slug}/related`);
  return data;
}
