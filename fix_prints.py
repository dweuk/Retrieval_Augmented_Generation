import glob

for py_file in glob.glob("src/files_parser/*.py"):
    with open(py_file, "r") as f:
        content = f.read()
    if "print(f\"Error reading " in content or "print(f\"Error reading" in content:
        lines = content.split('\n')
        new_lines = [line for line in lines if "print(f\"Error" not in line]
        with open(py_file, "w") as f:
            f.write('\n'.join(new_lines))
