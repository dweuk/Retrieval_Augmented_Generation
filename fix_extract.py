import glob

# Fix _extract_text -> extract_text in all files
for py_file in glob.glob("src/files_parser/*.py"):
    with open(py_file, "r") as f:
        content = f.read()
    if "def _extract_text" in content:
        content = content.replace("def _extract_text", "def extract_text")
        with open(py_file, "w") as f:
            f.write(content)
