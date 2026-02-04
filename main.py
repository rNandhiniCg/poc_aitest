from ast_analysis.dependency_extractor import extract_dependencies
from ingestion.build_index import build_index
from retrieval.retriever import retrieve_testcases
from llm.explainer import explain
import os, json
 
# Load all source files
dependencies = {}
for file in os.listdir("data/source_code"):
    if file.endswith(".py"):
        with open(f"data/source_code/{file}") as f:
            deps = extract_dependencies(f.read())
            dependencies.update(deps)
 
changed_function =  "Product" # "calculateInvoice"   # "applyDiscount"   # 
impacted_functions = [changed_function] + dependencies.get(changed_function, [])
 
build_index()
 
query = f"Testcases related to {impacted_functions}"
docs = retrieve_testcases(query, impacted_functions)
 
results = []
for doc in docs:
    results.append({
        "testcase_id": doc.metadata["testcase_id"],
        "reason": explain(doc.metadata, impacted_functions)
    })
 
with open("output/prioritized_testcases.json", "w") as f:
    json.dump(results, f, indent=2)
    print("Output got saved in \"output/prioritized_testcases.json\"")
 
