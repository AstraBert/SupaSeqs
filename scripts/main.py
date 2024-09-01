from typing import Union
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from pydantic import BaseModel
from encoder import Encoder
from utils import *
from scipy.spatial.distance import cosine


class Seq(BaseModel):
    sequence: str
    description: str | None = None


supabase_client = SupaClient("postgresql://postgres:postgres@127.0.0.1:54322/postgres")
supabase_client.execute_query("CREATE EXTENSION IF NOT EXISTS vector;")
supabase_client.execute_query(
    """CREATE TABLE IF NOT EXISTS public.sequences (
    id SERIAL PRIMARY KEY,
    sequence TEXT,
    description TEXT,
    embedding VECTOR(1024) 
);"""
)

supabase_client.execute_query(
    """drop function public.match_page_sections(vector,double precision,integer);"""
)

supabase_client.execute_query(
    """
create or replace function public.match_page_sections (
  embedding vector(1024),
  match_threshold float,
  match_count int
)
returns setof public.sequences
language sql
as $$
  select *
  from public.sequences
  where public.sequences.embedding <=> embedding < 1 - match_threshold
  order by public.sequences.embedding <=> embedding asc
  limit least(match_count, 1000);
$$;"""
)

encd = Encoder()

app = FastAPI(
    docs_url=None,
    title="SupaSeqs - Swagger UI",
    description="Manage your DNA sequences databases with the power of PostgreSQL",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SupaSeqs - Swagger UI",
        swagger_favicon_url="/static/favicon.png",
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/seqs/")
async def create_item(item: Seq):
    if "." in item.sequence:
        seqsdata = load_data(item.sequence)
        for header in seqsdata:
            embd = encd.kmerize(seqsdata[header]).tolist()
            supabase_client.execute_query(
                f"""INSERT INTO sequences(sequence, description, embedding) VALUES(
                '{seqsdata[header]}',
                '{header}',
                '{embd}'
            );"""
            )
    else:
        embd = encd.kmerize(item.sequence).tolist()
        des = "NONE" if item.description is None else item.description
        supabase_client.execute_query(
            f"""INSERT INTO sequences(sequence, description, embedding) VALUES(
                '{item.sequence}',
                '{des}',
                '{embd}'
            );"""
        )
    return item


@app.get("/seqs/{sequence}")
def read_item(sequence: str, limit: int = 100, threshold: int = 75):
    embd = encd.kmerize(sequence).tolist()
    r = supabase_client.execute_query(
        f"""SELECT * 
        FROM public.match_page_sections(
        '{embd}'::vector,  
        {threshold/100},                                  
        {limit}                                     
        );"""
    )
    results = r.fetchall()
    dictresul = {
        res[0]: {
            "sequence": res[1],
            "description": res[2],
            "cos_dist": cosine(eval(str(res[3])), embd),
        }
        for res in results if cosine(eval(str(res[3])), embd) < 1-threshold/100
    }
    return dictresul
