from langchain_community.vectorstores import FAISS
from ingestion.embeddings import get_embeddings
 
def retrieve_testcases(impacted_functions):
    embeddings = get_embeddings()
 
    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    query= f"Tests related to functions {impacted_functions}"
    docs = vectorstore.similarity_search(query, k=10)
 
    return [
        doc for doc in docs
        if set(doc.metadata["functions"]) & set(impacted_functions)
    ]