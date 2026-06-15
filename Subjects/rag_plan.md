# RAG System Implementation Plan

## 1. Data Ingestion & Indexing (Offline Phase)
> **Note:** Must have a flag for chunk size.

- Implement compatibility for `text`, `markdown`, `python`, and `pdf-to-text` files.
- Utilize an NLP parser (such as **spaCy** or **NLTK**).
- *Must be completed before any query is received.*
- **Parsing:** Ingest, clean, and validate the raw input data.
- **Chunking:** Split the text into optimal, overlapping segments.
- **Pre-computation (Sparse):** Build the BM25 inverted index for the corpus.
- **Pre-computation (Dense):** Pass all chunks through the Bi-Encoder, generate embeddings, and build the FAISS index.

## 2. Hybrid Retrieval (Online Phase - Stage 1)
> **Note:** Must have a flag for top-k chunks found.

- **Execution:** Parallel execution.
- Receive the user's prompt.
- Vectorize the prompt only.
- Execute the **BM25** search to retrieve the top `k` lexical matches.
- Execute the **FAISS** search to retrieve the top `k` semantic matches.
- **Fusion:** Combine the two sets of results (taking the union of the sets) to create a candidate pool of up to `2k` chunks.

## 3. Cross-Encoder Re-ranking (Online Phase - Stage 2)

- **Goal:** Precision filtering.
- Pass the prompt and each of the candidate chunks from Stage 1 simultaneously through the Cross-Encoder.
- Sort the chunks by the output scores to establish the absolute most relevant matches.

## 4. Generation (Online Phase - Stage 3)

- **Goal:** Context injection.
- Extract the top `n` chunks from the Cross-Encoder (e.g., the top 1 to 3, depending on your context window limits).
- Inject these chunks into the final prompt structure.
- Send the structured prompt to your **vLLM** instance to generate the final response.
