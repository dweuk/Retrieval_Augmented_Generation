# Lesson 1: Data Ingestion & Indexing in Python

Building the Offline Phase of your RAG pipeline requires robust data ingestion. This lesson covers how to implement directory traversal, file parsing (for `.txt`, `.md`, `.py`, and `.pdf`), cleaning, and chunking in Python.

## 1. Directory Traversal (The Gathering Phase)

To process a large, nested folder, you can use Python's built-in `pathlib` or `os` modules. `pathlib.Path.rglob()` is highly recommended as it provides a clean way to perform recursive searches.

**Imports you can use:**
```python
import os
from pathlib import Path
```

**Example Approach:**
```python
def get_all_files(directory_path: str):
    root_dir = Path(directory_path)
    # Recursively find all files in all subfolders
    for file_path in root_dir.rglob("*"):
        if file_path.is_file():
            yield file_path
```

## 2. Data Extraction and Parsing

Your pipeline needs to handle `.txt`, `.md`, `.py`, and `.pdf` files. Plain text, markdown, and python files can be read natively. PDF files require a dedicated parser.

**Imports you can use:**
```python
# For PDF parsing (You will need to run: pip install pdfplumber)
import pdfplumber 
# Alternatives: PyPDF2, pdfminer.six

# For general text/markdown/python, built-in open() is sufficient.
```

**Example Approach:**
```python
def extract_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    
    # Handle text-based formats
    if extension in ['.txt', '.md', '.py']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
            
    # Handle PDFs
    elif extension == '.pdf':
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        return text
        
    else:
        return "" # Ignore unsupported file types
```

## 3. Data Cleaning with NLP

Raw text often contains messy formatting, excessive whitespace, or garbage characters. You can use an NLP library like **spaCy** to clean and validate the text, ensuring it forms coherent sentences.

**Imports you can use:**
```python
import re
import spacy

# Load the spaCy English model
# You must run this in your terminal first: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")
```

**Example Approach:**
```python
def clean_text(raw_text: str) -> str:
    # Remove multiple newlines and excessive spaces using Regex
    cleaned = re.sub(r'\n+', '\n', raw_text)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    
    # Optional Validation: Use spaCy to ensure the text has valid sentence structures
    # doc = nlp(cleaned)
    # valid_sentences = [sent.text for sent in doc.sents if len(sent.text) > 5]
    # return " ".join(valid_sentences)
    
    return cleaned.strip()
```

## 4. Tokenization and Chunking

As per your plan, you need to split the text into optimal, overlapping segments based on a max chunk size. 

**Example Approach (Fixed-size chunking with overlap):**
This is the simplest way to chunk text while ensuring context is maintained across cuts.

```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end])
        # Move the start pointer forward, but step back by the 'overlap' amount
        start += (chunk_size - overlap)
        
    return chunks
```

**Example Approach (Semantic Chunking with spaCy):**
If you want to ensure you never cut a sentence in half, use spaCy's sentence boundaries.

```python
def chunk_by_sentences(text: str, max_tokens: int = 2000) -> list[str]:
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sent in doc.sents:
        # Rough token estimation (For exact token limits, use libraries like 'tiktoken')
        sent_length = len(sent.text.split()) 
        
        if current_length + sent_length > max_tokens:
            # Chunk is full, save it
            chunks.append(" ".join(current_chunk))
            # Start a new chunk, keeping the current sentence
            current_chunk = [sent.text]
            current_length = sent_length
        else:
            # Add to current chunk
            current_chunk.append(sent.text)
            current_length += sent_length
            
    # Add the final trailing chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
```

## Summary: The Ingestion Loop

Putting it all together, your offline ingestion function (which will eventually feed into your BM25 and FAISS indexes) will look like this:

```python
def ingest_directory(directory_path: str, chunk_size: int, overlap: int):
    all_chunks = []
    
    # 1. Traverse
    for file_path in get_all_files(directory_path):
        
        # 2. Parse
        raw_text = extract_text(file_path)
        if not raw_text:
            continue
            
        # 3. Clean
        cleaned_text = clean_text(raw_text)
        
        # 4. Chunk
        file_chunks = chunk_text(cleaned_text, chunk_size, overlap)
        
        # 5. Prepare for Indexing (Attach Metadata)
        for i, chunk in enumerate(file_chunks):
            metadata = {
                "source": str(file_path),
                "chunk_index": i,
                "text": chunk
            }
            all_chunks.append(metadata)
            
    return all_chunks

# Example execution:
# my_corpus = ingest_directory("./my_data", chunk_size=1500, overlap=250)
```
