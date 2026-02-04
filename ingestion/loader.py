from pathlib import Path
 
def load_files(folder):
    docs = []
    for file in Path(folder).rglob("*.*"):
        try:
            content = file.read_text(encoding="utf-8")
            docs.append({
                "content": content,
                "metadata": {
                    "file": str(file),
                    "type": "test" if "test" in str(file).lower() else "source"
                }
            })
        except:
            pass
    return docs
