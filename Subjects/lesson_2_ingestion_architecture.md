# Lesson 2: Object-Oriented Data Ingestion Architecture

Your intuition is **100% correct**. While writing one giant `extract_text` function with a bunch of `if/else` statements works for a quick script, it becomes a nightmare to maintain. 

If you want to build a robust system from scratch where you can easily add support for `.docx`, `.html`, or `.csv` in the future, you should use **Object-Oriented Programming (OOP)**. Specifically, this approach is often called the **Strategy Pattern**.

Here is a lesson on how to architect your ingestion phase using classes.

---

## 1. The Base Parser (The Blueprint)

First, we create a base class. Think of this as a strict blueprint that says: *"Any parser you create MUST have an `extract_text` method."*

We use Python's `abc` (Abstract Base Classes) module to enforce this rule.

```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseParser(ABC):
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """
        Takes a file path and returns the extracted text as a string.
        Every specific parser MUST implement this method.
        """
        pass
```

## 2. The Specific Parsers (The Strategies)

Now, we create specific classes for each format type. Each of these classes inherits from `BaseParser` and implements its own version of `extract_text`.

### The Text & Markdown Parser
Since `.txt`, `.md`, and `.py` files are all just plain text under the hood, one class can handle them all.

```python
class TextParser(BaseParser):
    
    def extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return ""
```

### The PDF Parser
PDFs require a completely different logic. We keep that messy logic isolated inside its own class.

```python
import pdfplumber

class PDFParser(BaseParser):
    
    def extract_text(self, file_path: Path) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""
```

*Notice how clean this is? If you ever need to change how PDFs are parsed (e.g., switching from `pdfplumber` to `PyMuPDF`), you ONLY touch the `PDFParser` class. Nothing else breaks.*

## 3. The Parser Factory (The Router)

Now you need a system that looks at a file, checks its extension, and hands it over to the correct class. This is called a **Factory**.

```python
class ParserFactory:
    def __init__(self):
        # A dictionary mapping file extensions to their respective parser classes
        self.parsers = {
            '.txt': TextParser(),
            '.md': TextParser(),
            '.py': TextParser(),
            '.pdf': PDFParser()
        }
        
    def get_parser(self, file_path: Path) -> BaseParser:
        extension = file_path.suffix.lower()
        
        # Return the correct parser, or None if the format isn't supported
        return self.parsers.get(extension, None)
```

If you want to add `.csv` support tomorrow, you just write a `CSVParser` class and add `'.csv': CSVParser()` to this dictionary. It takes 30 seconds and guarantees you won't break the PDF or Text parsers.

## 4. The Ingestion Manager (Putting it Together)

Finally, we create a class that manages the whole pipeline: walking the directory, asking the Factory for the right parser, and storing the data.

```python
class IngestionManager:
    def __init__(self, directory_path: str):
        self.directory_path = Path(directory_path)
        self.factory = ParserFactory()
        self.raw_documents = [] # Store parsed text here before chunking
        
    def run_ingestion(self):
        # 1. Walk the directory
        for file_path in self.directory_path.rglob("*"):
            if not file_path.is_file():
                continue
                
            # 2. Get the right parser for this file type
            parser = self.factory.get_parser(file_path)
            
            if parser is None:
                print(f"Skipping unsupported file: {file_path.name}")
                continue
                
            # 3. Extract the text!
            text = parser.extract_text(file_path)
            
            if text.strip():
                # Store it with metadata for the chunking phase
                self.raw_documents.append({
                    "source": str(file_path),
                    "raw_text": text
                })
                
        print(f"Successfully ingested {len(self.raw_documents)} documents.")
        return self.raw_documents

# Example Usage:
# manager = IngestionManager("./my_data")
# docs = manager.run_ingestion()
# Next step -> pass 'docs' into your Chunking class!
```

## Why this is better:
1. **Extensible:** Want to add HTML support? Create `HTMLParser`, add it to the factory. Done.
2. **Testable:** You can write a unit test *just* for the `PDFParser` without having to run the whole directory ingestion.
3. **Clean:** No massive nested `if/elif/else` blocks taking up 100 lines of code.
