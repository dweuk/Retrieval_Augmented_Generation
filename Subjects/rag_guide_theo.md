# Complete Guide to Building a RAG System

> **Retrieval-Augmented Generation (RAG)** is an architecture that gives a language model access to an external knowledge base at inference time, instead of relying solely on what it learned during training.

---

## Table of Contents

1. [Part 1 — Core Concepts You Must Understand First](#part-1--core-concepts-you-must-understand-first)
   - [Why RAG Exists](#1-why-rag-exists)
   - [The LLM Knowledge Problem](#2-the-llm-knowledge-problem)
   - [What a Context Window Is](#3-what-a-context-window-is)
   - [Embeddings and Vector Representations](#4-embeddings-and-vector-representations)
   - [Similarity Search](#5-similarity-search)
   - [Sparse vs Dense Retrieval](#6-sparse-vs-dense-retrieval)
   - [The Full RAG Pipeline](#7-the-full-rag-pipeline)
2. [Part 2 — Concepts in Depth](#part-2--concepts-in-depth)
   - [Document Ingestion](#1-document-ingestion)
   - [Chunking Strategies](#2-chunking-strategies)
   - [Indexing](#3-indexing)
   - [Retrieval Methods](#4-retrieval-methods)
   - [Augmentation & Prompt Construction](#5-augmentation--prompt-construction)
   - [Generation](#6-generation)
   - [Evaluation](#7-evaluation)
3. [Part 3 — Tools & Libraries](#part-3--tools--libraries)
4. [Part 4 — Resources](#part-4--resources)

---

## Part 1 — Core Concepts You Must Understand First

### 1. Why RAG Exists

A standard LLM is a frozen artifact: once trained, its knowledge is fixed. If you ask it about your private codebase, a recent event, or a proprietary document, it has no idea — it was never trained on that data.

Two common solutions exist:

| Approach | How | Downside |
|---|---|---|
| **Fine-tuning** | Retrain the model on your data | Expensive, slow, knowledge still goes stale |
| **RAG** | Feed relevant documents to the model at query time | Requires building a retrieval system |

RAG is almost always the right choice when the knowledge changes, is private, or is too large to fit in a context window.

---

### 2. The LLM Knowledge Problem

LLMs suffer from three core limitations that RAG directly addresses:

- **Knowledge cutoff**: trained on data up to a certain date, unaware of anything after.
- **Hallucination**: when uncertain, models generate plausible-sounding but false information.
- **No private data**: the model has never seen your files, codebase, or internal documents.

RAG does not eliminate hallucination entirely, but grounding the model in real retrieved sources dramatically reduces it, because the model is instructed to answer *only* from the provided context.

---

### 3. What a Context Window Is

Every LLM can only process a fixed amount of text at once — this limit is the **context window**, measured in **tokens** (roughly 0.75 words per token in English). Typical sizes range from 4k to 128k tokens depending on the model.

This is critical for RAG because:
- You cannot dump your entire knowledge base into the prompt.
- You must **retrieve only the most relevant chunks** and fit them in the window.
- If you exceed the limit, the model truncates or errors out.

**Practical implication**: your retrieval step must return a small, high-quality selection of documents, not everything.

---

### 4. Embeddings and Vector Representations

An **embedding** is a list of floating-point numbers (a vector) that represents the semantic meaning of a piece of text. Texts with similar meaning produce vectors that are close together in high-dimensional space.

```
"How do I install Python?" → [0.12, -0.87, 0.45, ..., 0.03]  (768 dimensions)
"Python installation guide" → [0.11, -0.85, 0.46, ..., 0.04]  (close!)
"Recipe for chocolate cake" → [-0.92, 0.33, -0.11, ..., 0.78] (far away)
```

Embedding models (like `sentence-transformers`) are neural networks trained specifically to map text into this semantic space. They are separate from the LLM used for generation.

**Why this matters**: embeddings allow you to find semantically relevant documents even when they use different words from the query.

---

### 5. Similarity Search

Once you have embeddings, you need a way to find the vectors closest to a query vector. The two most common distance metrics are:

**Cosine similarity** — measures the angle between vectors, ignores magnitude. Best for normalized text embeddings.

```
similarity(A, B) = (A · B) / (|A| × |B|)
```
- Result: `-1` (opposite) to `1` (identical)

**Dot product** — measures both direction and magnitude. Faster but sensitive to vector norms.

**Euclidean distance** — straight-line distance in vector space. Less common for text.

For most RAG use cases: use **cosine similarity**. When vectors are pre-normalized (unit length), cosine similarity and dot product are equivalent and very fast.

---

### 6. Sparse vs Dense Retrieval

This is one of the most important conceptual distinctions in RAG:

| | Sparse Retrieval | Dense Retrieval |
|---|---|---|
| **Representation** | Bag-of-words (term frequencies) | Continuous vectors (embeddings) |
| **Examples** | TF-IDF, BM25 | sentence-transformers, OpenAI embeddings |
| **Matches on** | Exact keywords | Semantic meaning |
| **Strengths** | Fast, interpretable, no GPU needed | Handles synonyms, paraphrasing |
| **Weaknesses** | Misses synonyms and paraphrasing | Requires embedding model, can miss rare terms |
| **Best for** | Code search, technical terms, IDs | Natural language questions, prose |

**BM25 is almost always the right sparse baseline to start with.** It is fast, requires no model, and performs surprisingly well on technical corpora.

**Hybrid retrieval** (BM25 + dense) combines both and generally outperforms either alone. A reranker model can then reorder the combined results.

---

### 7. The Full RAG Pipeline

```
Raw Documents
      │
      ▼
┌─────────────────┐
│   INGESTION     │  Load files, parse formats (PDF, Markdown, Python, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    CHUNKING     │  Split documents into smaller, overlapping pieces
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    INDEXING     │  Compute TF-IDF / BM25 weights  OR  embed chunks into vectors
│                 │  Store in an index (disk file, vector DB, etc.)
└────────┬────────┘
         │
   (offline — done once)
─────────┼─────────────────────────────────────────
   (online — done per query)
         │
         ▼
┌─────────────────┐
│    RETRIEVAL    │  Encode query → search index → return top-k chunks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AUGMENTATION   │  Filter/rerank chunks, build a prompt with retrieved context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   GENERATION    │  Pass prompt to LLM → produce the final answer
└─────────────────┘
```

Everything above the dashed line is a one-time **offline** step. Everything below is run **per query** at inference time.

---

## Part 2 — Concepts in Depth

### 1. Document Ingestion

Ingestion is the process of reading raw files and preparing them for chunking. Different file types require different parsers:

| File type | Parsing approach |
|---|---|
| `.py` | Read as text; use AST to extract functions/classes |
| `.md` / `.rst` | Read as text; split on headings |
| `.pdf` | Use a PDF library (pdfplumber, PyMuPDF) |
| `.html` | Strip tags with BeautifulSoup |
| `.txt` | Read directly |

**Key decisions:**
- Which files to include vs skip (e.g., skip `__pycache__`, `.git`, binaries)
- Whether to preserve file path and character offsets in the metadata (required for source attribution)
- Whether to parse code semantically (by function) vs naively (by characters)

Each chunk must carry metadata: at minimum `file_path`, `first_character_index`, `last_character_index`. This is how retrieved results are attributed to their source.

---

### 2. Chunking Strategies

Chunking is splitting a document into pieces small enough to fit in context but large enough to be meaningful. It is one of the highest-leverage decisions in a RAG system.

#### Fixed-size / Character chunking

Split every N characters with optional overlap:

```
[...chunk 1 (0-2000)...]
              [...chunk 2 (1800-3800)...]  ← overlap of 200
```

- Simple and fast.
- **Overlap** (50–200 chars) ensures a sentence split at the boundary appears in at least one chunk.
- Works for plain text and Markdown.

#### Recursive character text splitting

Split on `\n\n`, then `\n`, then ` `, then characters — trying to respect natural document boundaries before resorting to hard cuts.

#### Code-aware chunking (AST-based)

For source code, splitting on characters produces broken functions. Instead, parse the AST and extract complete logical units:

- Functions (`def`)
- Classes (`class`)
- Top-level statements

This ensures each chunk is syntactically complete and semantically self-contained. The `ast` module in Python's standard library handles this.

#### Semantic chunking

Use an embedding model to detect "topic shifts" between consecutive sentences and split there. More accurate but computationally expensive.

#### Chunk size guidance

| Corpus type | Recommended size |
|---|---|
| Code files | Full function / class (~500–1500 chars) |
| Documentation / Markdown | ~500–1000 chars |
| Dense technical prose | ~300–800 chars |

Too small → context-free fragments. Too large → you waste context window space with irrelevant content.

---

### 3. Indexing

Indexing transforms your chunks into a data structure that supports fast similarity queries.

#### TF-IDF (Term Frequency – Inverse Document Frequency)

A classical information retrieval technique. For each term in each chunk:

- **TF (term frequency)**: how often the term appears in *this chunk*
- **IDF (inverse document frequency)**: how rare the term is across *all chunks* (rare = more informative)

```
TF-IDF(term, chunk) = TF(term, chunk) × log(N / df(term))
```

Where `N` is the total number of chunks and `df(term)` is the number of chunks containing the term.

The index is a sparse matrix of shape `(num_chunks × vocabulary_size)`. Queries are encoded the same way; similarity is cosine distance between the query vector and each chunk vector.

**Library**: [`sklearn.feature_extraction.text.TfidfVectorizer`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

#### BM25 (Best Match 25)

BM25 is an improved probabilistic ranking model that addresses two known weaknesses of TF-IDF:

1. **Term frequency saturation**: TF-IDF score grows unboundedly with term frequency; BM25 saturates it.
2. **Document length normalization**: shorter documents are not unfairly disadvantaged.

```
BM25(q, d) = Σ IDF(t) × [TF(t,d) × (k1 + 1)] / [TF(t,d) + k1 × (1 - b + b × |d|/avgdl)]
```

Parameters: `k1 ∈ [1.2, 2.0]` (TF saturation), `b = 0.75` (length normalization). These defaults work well in practice.

BM25 is the standard baseline for sparse retrieval and often outperforms TF-IDF.

**Library**: [`bm25s`](https://github.com/xhluca/bm25s) — a fast, modern BM25 implementation.

#### Dense / Vector Index

Each chunk is embedded into a dense vector by an embedding model. The index stores these vectors and supports approximate nearest-neighbor (ANN) search.

**FAISS** — Meta's library for fast ANN search over dense vectors. Pure in-memory, very fast.
→ [FAISS documentation](https://faiss.ai/index.html)

**ChromaDB** — an embedding database with persistence, metadata filtering, and a Python-native API. Stores both embeddings and raw text together.
→ [ChromaDB documentation](https://docs.trychroma.com/)

**Qdrant**, **Weaviate**, **Pinecone** — managed or self-hosted vector databases with additional features (access control, cloud hosting, etc.).

---

### 4. Retrieval Methods

#### Top-k retrieval

The fundamental operation: given a query, return the `k` most relevant chunks. `k` is a hyperparameter — typical values are 5–20. Larger `k` improves recall but increases context length and LLM cost.

#### Sparse retrieval (BM25 / TF-IDF)

1. Tokenize and encode the query into the same sparse representation.
2. Score every chunk using BM25/TF-IDF similarity.
3. Return the top-k by score.

Best for: keyword-heavy queries, code searches, exact technical terms.

#### Dense retrieval (embedding similarity)

1. Embed the query with the same embedding model used at indexing time.
2. Find the k-nearest vectors in the index (cosine similarity or MIPS).
3. Return the corresponding chunks.

Best for: natural language questions, paraphrasing, conceptual questions.

**Important**: you *must* use the **same embedding model** for indexing and querying. Mixing models breaks the search entirely.

#### Hybrid retrieval

Run both sparse and dense retrieval, then merge the two ranked lists. A common merging strategy is **Reciprocal Rank Fusion (RRF)**:

```
RRF_score(chunk) = Σ 1 / (k + rank_in_list_i)
```

This is robust and requires no calibration. `k = 60` is a standard default.

#### Reranking

After retrieving the initial top-k candidates, a **cross-encoder reranker** re-scores each (query, chunk) pair together (as opposed to encoding them separately). This is more expensive but much more accurate.

Common rerankers: `cross-encoder/ms-marco-MiniLM-L-6-v2` from Sentence-Transformers.

---

### 5. Augmentation & Prompt Construction

Augmentation is the step between retrieval and generation. You have retrieved `k` chunks — now you need to build the prompt.

#### What to do with retrieved chunks

1. **Filter noise**: remove chunks below a relevance threshold.
2. **Deduplicate**: if two chunks overlap heavily, keep only one.
3. **Rerank**: optionally apply a cross-encoder reranker here.
4. **Truncate to fit context**: sort by relevance, add chunks until you hit the token limit.

#### Prompt template

A standard RAG prompt has three parts:

```
SYSTEM: You are a helpful assistant. Answer the question using ONLY the
        information provided in the context below. If the answer is not
        in the context, say so.

CONTEXT:
[Source: path/to/file.py, chars 120-800]
<chunk text here>

[Source: docs/readme.md, chars 0-500]
<chunk text here>

QUESTION: <user's question>

ANSWER:
```

Including the source attribution in the prompt encourages the model to stay grounded and makes it possible to extract sources from the answer.

#### Context window management

- Count tokens, not characters (use `tiktoken` or `transformers`'s tokenizer).
- Leave room for the answer (at least 512–1024 tokens).
- Put the most relevant chunk first — models attend better to content at the beginning.

---

### 6. Generation

Generation is running the LLM on the constructed prompt to produce an answer.

#### Local inference

Running a model on your own hardware. Requires a GPU for anything beyond ~1B parameters at reasonable speed.

**Transformers (HuggingFace)** — the standard Python library for loading and running any open model.
→ [Transformers documentation](https://huggingface.co/docs/transformers/index)

```python
from transformers import pipeline

pipe = pipeline("text-generation", model="Qwen/Qwen3-0.6B")
result = pipe("Your prompt here", max_new_tokens=512)
```

**vLLM** — a high-throughput inference engine for LLMs. Implements PagedAttention for efficient GPU memory use. Much faster than naive HuggingFace inference for batch workloads.
→ [vLLM documentation](https://docs.vllm.ai/en/latest/)

**Ollama** — runs models locally via a REST API, similar to an OpenAI-compatible server. Great for development.
→ [Ollama documentation](https://github.com/ollama/ollama)

#### API-based inference

Use a provider (OpenAI, Anthropic, Mistral) via HTTP. No local GPU required. Good for prototyping; costs money at scale.

#### Structured output with Pydantic

When you need the LLM to return structured data (JSON), use [Pydantic](https://docs.pydantic.dev/latest/) models to define the schema and validate the output:

```python
from pydantic import BaseModel

class Answer(BaseModel):
    answer: str
    sources: list[str]
```

Many inference libraries support constrained decoding to guarantee valid JSON output matching a given schema.

---

### 7. Evaluation

Evaluation is what separates a prototype from a reliable system. You need to measure whether your retrieval is actually returning the right chunks.

#### Recall@k

The primary metric for retrieval quality. For a given question with known ground-truth source(s):

```
Recall@k = (number of correct sources found in top-k results) / (total number of correct sources)
```

A source counts as "found" if the retrieved chunk and the correct source have **at least 5% character overlap** (they don't need to match exactly).

The metric is calculated for each question, then averaged across the dataset.

- **Recall@1**: did the single best result include the answer?
- **Recall@5**: did *any* of the 5 best results include the answer?
- **Recall@10**: did *any* of the 10 best results?

Higher `k` always gives higher or equal recall. The goal is high recall at low `k` — that means your ranking is good.

#### Precision@k

```
Precision@k = (number of correct sources in top-k) / k
```

Measures how noisy your top-k results are. High recall + low precision means you retrieved the right chunk but buried it among irrelevant ones.

#### Mean Reciprocal Rank (MRR)

```
MRR = (1/N) × Σ 1/rank_of_first_correct_result
```

Rewards finding the correct source at a higher rank. Useful when you only need the single best result.

#### RAGAS metrics (end-to-end)

[RAGAS](https://docs.ragas.io/) is a framework for evaluating the full RAG pipeline, including generation quality:

- **Faithfulness**: does the answer contain only claims supported by the context?
- **Answer relevancy**: does the answer actually address the question?
- **Context recall**: does the retrieved context contain all information needed?
- **Context precision**: is the context free of irrelevant information?

---

## Part 3 — Tools & Libraries

### Core RAG Libraries

#### [bm25s](https://github.com/xhluca/bm25s)
A fast, pure-Python BM25 implementation. Supports saving/loading indexes to disk, tokenization customization, and batch querying. The go-to library for sparse retrieval.

```python
import bm25s

corpus = ["chunk 1 text", "chunk 2 text", ...]
retriever = bm25s.BM25()
retriever.index(bm25s.tokenize(corpus))
results, scores = retriever.retrieve(bm25s.tokenize(["my query"]), k=5)
```
→ [bm25s documentation](https://bm25s.github.io/)

#### [sentence-transformers](https://www.sbert.net/)
The standard library for computing text embeddings. Provides 100+ pre-trained models for semantic search, ranging from fast/small to slow/accurate.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["chunk 1", "chunk 2"])
```
→ [Sentence Transformers documentation](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

#### [ChromaDB](https://docs.trychroma.com/)
An embedded vector database. Stores documents, embeddings, and metadata together. Persists to disk. Good for development and medium-scale production.

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("my_docs")
collection.add(documents=["chunk text"], ids=["chunk_1"])
results = collection.query(query_texts=["my question"], n_results=5)
```
→ [ChromaDB documentation](https://docs.trychroma.com/)

#### [LangChain](https://python.langchain.com/)
A framework that provides high-level abstractions for the full RAG pipeline: document loaders, text splitters, vector stores, retrievers, and LLM chains. Good for rapid prototyping; can be complex for custom pipelines.
→ [LangChain RAG documentation](https://python.langchain.com/docs/tutorials/rag/)

#### [DSPy](https://dspy.ai/)
A framework for programming LLM pipelines in a structured, optimizable way. Instead of writing prompt strings, you declare modules that DSPy can automatically optimize.
→ [DSPy documentation](https://dspy.ai/)

#### [Transformers (HuggingFace)](https://huggingface.co/docs/transformers/index)
The standard library for loading, fine-tuning, and running any open-source language model. Supports both inference and training across PyTorch and JAX backends.
→ [Transformers documentation](https://huggingface.co/docs/transformers/index)

#### [FAISS](https://faiss.ai/)
Facebook AI Similarity Search. A library for fast approximate nearest-neighbor search over dense vectors. CPU and GPU support. No built-in persistence — save/load with `faiss.write_index` / `faiss.read_index`.
→ [FAISS documentation](https://faiss.ai/index.html)

---

### Python Tooling

#### [Pydantic](https://docs.pydantic.dev/latest/)
Data validation using Python type hints. Define data models as classes; Pydantic validates input and produces clear errors. Essential for structured LLM output and clean data pipelines.
→ [Pydantic documentation](https://docs.pydantic.dev/latest/)

#### [Python Fire](https://github.com/google/python-fire)
Automatically generates a CLI from any Python object. Expose your classes or functions as command-line commands with zero boilerplate.

```python
import fire

class RAGSystem:
    def index(self, path: str, max_chunk_size: int = 2000): ...
    def search(self, query: str, k: int = 5): ...

if __name__ == "__main__":
    fire.Fire(RAGSystem)
```

```bash
python main.py index --path ./data --max_chunk_size 1500
python main.py search "How does X work?" --k 10
```
→ [Python Fire documentation](https://github.com/google/python-fire/blob/master/docs/guide.md)

#### [tqdm](https://tqdm.github.io/)
Progress bars for loops and iterables. One-line addition to any loop.

```python
from tqdm import tqdm

for chunk in tqdm(chunks, desc="Indexing"):
    ...
```
→ [tqdm documentation](https://tqdm.github.io/)

#### [uv](https://docs.astral.sh/uv/)
A fast Python package and project manager (replaces pip + venv). Manages dependencies via `pyproject.toml`, resolves lockfiles, and creates isolated environments. Always run your code with `uv run` to ensure you use the project environment.

```bash
uv add bm25s pydantic     # add dependencies
uv run python main.py     # run inside the project environment
uv sync                   # install all dependencies from lockfile
```
→ [uv documentation](https://docs.astral.sh/uv/)

---

### Code Quality

#### [flake8](https://flake8.pycqa.org/)
Python style and syntax linter. Checks PEP 8 compliance and catches common errors.
→ [flake8 documentation](https://flake8.pycqa.org/en/latest/)

#### [mypy](https://mypy.readthedocs.io/)
Static type checker for Python. Reads your type hints and reports type errors before runtime.
→ [mypy documentation](https://mypy.readthedocs.io/en/stable/)

---

## Part 4 — Resources

### Foundational Papers

- **Original RAG paper** — [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) (Lewis et al., 2020) — introduces the concept.
- **BM25** — [The Probabilistic Relevance Framework: BM25 and Beyond](https://www.staff.city.ac.uk/~sas/ir_resources/gentle_bm25_intro.pdf) — the definitive BM25 reference.
- **RAGAS** — [RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) — end-to-end RAG evaluation framework.
- **Hybrid Retrieval + RRF** — [Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

### Tutorials & Guides

- **HuggingFace RAG tutorial** — [Building RAG with HuggingFace](https://huggingface.co/learn/cookbook/en/rag_with_hugging_face_gemma_mongodb) — end-to-end walkthrough using open models.
- **LangChain RAG tutorial** — [Build a RAG app](https://python.langchain.com/docs/tutorials/rag/) — complete pipeline with LangChain abstractions.
- **DeepLearning.AI RAG short course** — [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) — free short course covering chunking, evaluation, and advanced retrieval.
- **Pinecone Learn** — [Retrieval Augmented Generation](https://www.pinecone.io/learn/retrieval-augmented-generation/) — visual explanations of key RAG concepts.

### Documentation

| Tool | Documentation |
|---|---|
| HuggingFace Transformers | https://huggingface.co/docs/transformers/index |
| Sentence Transformers | https://www.sbert.net/docs/sentence_transformer/pretrained_models.html |
| bm25s | https://bm25s.github.io/ |
| ChromaDB | https://docs.trychroma.com/ |
| FAISS | https://faiss.ai/index.html |
| LangChain | https://python.langchain.com/docs/introduction/ |
| DSPy | https://dspy.ai/ |
| Pydantic | https://docs.pydantic.dev/latest/ |
| Python Fire | https://github.com/google/python-fire/blob/master/docs/guide.md |
| tqdm | https://tqdm.github.io/ |
| uv | https://docs.astral.sh/uv/ |
| vLLM | https://docs.vllm.ai/en/latest/ |
| RAGAS | https://docs.ragas.io/ |
| scikit-learn TF-IDF | https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html |

### Model Hubs

- **HuggingFace Model Hub** — https://huggingface.co/models — browse and download open models for generation and embedding.
- **Sentence Transformers pre-trained models** — https://www.sbert.net/docs/sentence_transformer/pretrained_models.html — ranking of embedding models by speed and accuracy.
- **MTEB Leaderboard** — https://huggingface.co/spaces/mteb/leaderboard — authoritative benchmark for embedding model quality across retrieval tasks.
