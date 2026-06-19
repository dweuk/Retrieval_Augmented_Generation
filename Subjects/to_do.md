Your next priority is not improving the LLM—it is preserving source metadata. The grader evaluates retrieved file paths and character positions, but your chunks are currently plain strings.
You already have:
Working ingestion and chunking.
BM25 + FAISS retrieval and reranking.
Persistent indexes.
Qwen answer generation.
Next milestone: structured chunks and sources
Implement the required Pydantic models from [subject.md (line 603)](/Users/noepapot/informatic/ecole_42/circle_4/RAG/Subjects/subject.md:603), especially:
class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int
You will also benefit from an internal model:
class IndexedChunk(BaseModel):
    text: str
    source: MinimalSource
Then change ingestion conceptually from:
list[str]
to:
list[IndexedChunk]
Each chunk must remember:
chunk text
source filename
start character
end character
Your BM25 and FAISS indexes can still index only chunk.text, but you need a parallel list mapping every indexed position back to its IndexedChunk.
Why this must come next
The required search output is not the retrieved text. It is structured JSON:
{
  "question_id": "q1",
  "retrieved_sources": [
    {
      "file_path": "docs/example.md",
      "first_character_index": 100,
      "last_character_index": 450
    }
  ]
}
If you continue indexing plain strings, you cannot reconstruct reliable source positions afterward.
Be careful: for Python files, character positions should refer to the original file. If your parser rewrites AST nodes into new text, offsets in that rewritten text will not match the original source.
Then separate indexing from searching
Your current index() requires a query and immediately performs retrieval. The subject expects separate commands:
index
search
answer
The grader will call something similar to:
uv run python -m student index --max_chunk_size 2000
Therefore, eventually:
index() should only ingest, build, and save indexes.
search(query, k) should load indexes and retrieve sources.
answer(query, k) should call search and generate an answer.
Also ensure:
max_chunk_size is configurable.
It never exceeds 2000 characters.
The default repository is the provided vLLM source, using a relative—not absolute—path.
Remaining roadmap
After source-aware chunks:
Implement search returning MinimalSearchResults.
Implement search_dataset for the provided JSON datasets.
Implement Recall@k evaluation with the required 5% source overlap.
Measure BM25 alone before adding FAISS/reranking.
Make answer return structured JSON with citations.
Implement answer_dataset.
Add tqdm progress bars.
Handle invalid paths, empty datasets, missing indexes, and invalid k.
Add docstrings and tests.
Complete the README and required Makefile/lint flags.
Important compliance gaps:
The subject requires Python 3.10, while your project currently requires Python ≥3.12.
rag.py still has three Flake8 errors and one mypy error.
The README currently contains only its required opening sentence.
The mandatory CLI commands search, search_dataset, answer_dataset, and evaluate are missing.
Focus only on MinimalSource and IndexedChunk first. Once every chunk retains correct source offsets, the rest of the required system becomes much easier to build correctly.