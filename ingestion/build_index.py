from langchain_community.vectorstores import FAISS
from ingestion.embeddings import get_embeddings
from ast_analysis.test_extractor import extract_testcases
 
def build_index():
    testcases = extract_testcases("data/test_scripts")
    embeddings = get_embeddings()
 
    texts = [tc["description"] for tc in testcases]
    metadatas = testcases
 
    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )
 
    vectorstore.save_local("faiss_index")