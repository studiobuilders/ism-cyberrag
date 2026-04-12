-- Sprint 2 Migration: Add full-text search and hybrid search RPC
-- Run this against an existing Sprint 1 database to upgrade it.
-- If setting up fresh, use schema.sql instead (it includes everything).

-- 1. Add generated tsvector column for full-text search
alter table chunks
  add column if not exists fts tsvector
  generated always as (to_tsvector('english', content)) stored;

-- 2. Add GIN index for fast full-text search
create index if not exists chunks_fts_idx on chunks using gin (fts);

-- 3. Create hybrid search RPC combining vector + BM25 with RRF
create or replace function hybrid_search(
  query_text text,
  query_embedding vector(768),
  match_count int default 10,
  full_text_weight float default 1,
  semantic_weight float default 1,
  rrf_k int default 50
)
returns table (
  id bigint,
  content text,
  control_id text,
  category text,
  sub_topic text,
  applicability text[],
  essential_8 text,
  revision int,
  similarity float,
  rrf_score float
)
language sql as $$
  with full_text as (
    select c.id,
      row_number() over (order by ts_rank_cd(c.fts, websearch_to_tsquery(query_text)) desc) as rank_ix
    from chunks c
    where c.fts @@ websearch_to_tsquery(query_text)
    limit least(match_count, 30) * 2
  ),
  semantic as (
    select c.id,
      row_number() over (order by c.embedding <=> query_embedding) as rank_ix,
      1 - (c.embedding <=> query_embedding) as similarity
    from chunks c
    order by c.embedding <=> query_embedding
    limit least(match_count, 30) * 2
  )
  select
    c.id, c.content, c.control_id, c.category, c.sub_topic,
    c.applicability, c.essential_8, c.revision,
    coalesce(s.similarity, 0)::float as similarity,
    (coalesce(1.0 / (rrf_k + ft.rank_ix), 0.0) * full_text_weight +
     coalesce(1.0 / (rrf_k + s.rank_ix), 0.0) * semantic_weight)::float as rrf_score
  from full_text ft
  full outer join semantic s on ft.id = s.id
  join chunks c on c.id = coalesce(ft.id, s.id)
  order by rrf_score desc
  limit least(match_count, 30);
$$;
