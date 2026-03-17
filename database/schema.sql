-- Enable pgvector
create extension if not exists vector;

-- Documents table
create table documents (
  id bigserial primary key,
  title text not null,
  source_file text not null,
  content text,
  metadata jsonb,
  created_at timestamptz default now()
);

-- Chunks table with vector column
create table chunks (
  id bigserial primary key,
  document_id bigint references documents(id),
  content text not null,
  control_id text,
  category text,
  sub_topic text,
  applicability text[],
  essential_8 text,
  revision int,
  embedding vector(768),
  metadata jsonb,
  created_at timestamptz default now()
);

-- Indexes
create index on chunks using hnsw (embedding vector_cosine_ops);

-- Vector search function
create or replace function match_chunks(
  query_embedding vector(768),
  match_count int default 5
)
returns table (
  id bigint, content text, control_id text,
  category text, similarity float
)
language sql as $$
  select id, content, control_id, category,
         1 - (embedding <=> query_embedding) as similarity
  from chunks
  order by embedding <=> query_embedding
  limit match_count;
$$;
