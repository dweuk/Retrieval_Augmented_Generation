# RAG Pre-Computation: The Foundation of Retrieval

Welcome to this crash course on the **Pre-computation** phase of Retrieval-Augmented Generation (RAG). Before a RAG system can accurately answer questions, it needs to organize its knowledge base so it can search through it blazing fast. This preparation phase is called "pre-computation" or "indexing."

When building an advanced RAG system, developers often use a **Hybrid Search** approach, which combines two powerful methods:
1. **Sparse Search (Keyword-based)**
2. **Dense Search (Semantic/Meaning-based)**

Let's break down the pre-computation steps for both.

---

## Part 1: Pre-computation (Sparse) - Building the BM25 Inverted Index

**What it is:** Sparse retrieval is like the index at the back of a textbook. It looks for exact keyword matches between the user's question and the documents.

**The Algorithm (BM25):** BM25 (Best Matching 25) is the industry standard for sparse search. It improves upon basic keyword counting by considering:
- **Term Frequency (TF):** How often does the keyword appear in the document? (More is better).
- **Inverse Document Frequency (IDF):** How rare is the keyword across *all* documents? (Matching a rare word like "photosynthesis" is more important than matching "the").
- **Document Length:** Is the document extremely long? (A keyword appearing 5 times in a short tweet is stronger evidence than 5 times in a 1,000-page book).

### The Steps to Build It:

1. **Tokenization:** Take your text chunks and break them down into individual words or "tokens" (e.g., `"The quick brown fox"` -> `["The", "quick", "brown", "fox"]`).
2. **Preprocessing:** Clean the text by converting it to lowercase, removing punctuation, and often removing "stop words" (common words like "and", "the", "is").
3. **Building the Inverted Index:** This is the core data structure. Instead of a list of documents containing words, you build a dictionary where each word points to a list of documents that contain it.
   - *Example:*
     - `apple` -> [Doc 1, Doc 4, Doc 15]
     - `banana` -> [Doc 2, Doc 4]
4. **Calculating Statistics:** The system calculates and stores the TF and IDF weights for every term so they don't have to be computed at search time.

> [!TIP]
> **Why it's called "Sparse":** If your vocabulary has 50,000 words, a document might only contain 100 unique words. If you represent this document as an array of 50,000 numbers counting word occurrences, 49,900 of those numbers will be exactly `0`. It is a "sparse" representation.

---

## Part 2: Pre-computation (Dense) - Bi-Encoders and FAISS

**What it is:** Dense retrieval searches by *meaning*, not just keywords. If a user asks about "canines," dense search knows to return documents about "dogs" and "wolves," even if the word "canine" is never used.

**The Algorithm (Bi-Encoder):** A Bi-Encoder is a deep learning model (usually based on transformers like BERT) that reads a chunk of text and squashes its entire meaning into a single list of numbers called a **vector embedding**. It's called a *Bi*-Encoder because at search time, the exact same model will independently encode the user's question (query) and the document.

### The Steps to Build It:

1. **Chunking the Data:** You can't feed an entire book into an AI model at once. You must split your corpus into smaller, meaningful chunks (e.g., 250-500 words each).
2. **Generating Embeddings:** Pass every single chunk through the Bi-Encoder model. The model outputs a dense vector for each chunk.
   - *Example:* `[0.124, -0.843, 0.001, 0.993, ...]` (Usually 384, 768, or 1536 numbers long).
3. **Building the FAISS Index:** You now have millions of vectors. Comparing a new user question to every single vector would be way too slow. This is where **FAISS** (Facebook AI Similarity Search) comes in.
   - FAISS doesn't just store the vectors in a list; it organizes them structurally.
   - It clusters similar vectors together in multi-dimensional space.
   - When a user asks a question, FAISS only looks in the "neighborhood" of vectors that are conceptually closest to the question, making the search almost instantaneous.

> [!TIP]
> **Why it's called "Dense":** Unlike sparse arrays where most values are 0, every single number in an embedding vector (all 768 of them, for instance) is a non-zero, floating-point number carrying conceptual weight.

---

## Summary: Why do we need both?

By performing both of these pre-computations, your RAG system is ready for **Hybrid Search**:
- **BM25 (Sparse)** will catch exact terminology, part numbers, names, and specific acronyms perfectly.
- **Bi-Encoder/FAISS (Dense)** will understand the overarching concepts, synonyms, and intent behind the user's question.

When a user asks a question, the system runs both searches simultaneously, merges the results, and hands the best documents to the LLM to generate the final answer!
