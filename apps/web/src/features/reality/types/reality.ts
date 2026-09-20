export interface Domain {
  id: string;
  name: string;
  slug: string;
  description: string | null;
}

export interface ContentSection {
  type: string;
  title: string;
  content: string;
}

export interface Source {
  id: string;
  title: string;
  authors: string[];
  url: string | null;
  source_type: string;
  publication_year: number | null;
  publisher: string | null;
  doi: string | null;
  notes: string | null;
}

export interface ConceptSource {
  section_type: string | null;
  source: Source;
}

export interface ConceptSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  difficulty: string;
  evidence_level: string;
  estimated_reading_minutes: number;
  domain: Domain;
}

export interface Concept {
  id: string;
  slug: string;
  title: string;
  summary: string;
  domain: Domain;
  difficulty: string;
  evidence_level: string;
  estimated_reading_minutes: number;
  status: string;
  sections: ContentSection[];
  tags: string[];
  sources: ConceptSource[];
}

export interface ConceptRelation {
  relation_type: string;
  concept: ConceptSummary;
}

export interface ConceptListResponse {
  items: ConceptSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface ConceptFilters {
  page?: number;
  domain?: string;
  difficulty?: string;
  q?: string;
}
