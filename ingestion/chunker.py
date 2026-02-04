from langchain_text_splitters import RecursiveCharacterTextSplitter
 
def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
 
    chunks = []
    for d in docs:
        for chunk in splitter.split_text(d["content"]):
            chunks.append({
                "content": chunk,
                "metadata": d["metadata"]
            })
    return chunks