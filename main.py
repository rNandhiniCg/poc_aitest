import os, json
from diff.diff_analyzer import find_changed_functions
from ast_analysis.dependency_extractor import extract_dependencies
from ingestion.build_test_index import build_index
from retrieval.retriever import retrieve_testcases
from llm.explainer import explain
 
# Step 1: Find changed functions
changed_functions = find_changed_functions(
    "data/source_old",
    "data/source_new"
)
 
# Step 2: Find dependencies
dependencies = {}
for file in os.listdir("data/source_new"):
    if file.endswith(".py"):
        with open(f"data/source_new/{file}") as f:
            dependencies.update(extract_dependencies(f.read()))
 
impacted_functions = set(changed_functions)
for fn in changed_functions:
    impacted_functions.update(dependencies.get(fn, []))
 
# Step 3: Build test KB
build_index()
 
# Step 4: Retrieve testcases
docs = retrieve_testcases(list(impacted_functions))
 
# Step 5: Explain & store output
results = []
for i, doc in enumerate(docs, 1):
    results.append({
        "seq": i,
        "testcase_id": doc.metadata["testcase_id"],
        "testcase_name": doc.metadata["testcase_id"],
        "description": doc.metadata["description"],
        "impacted_functions": list(impacted_functions),
        "why_this_testcase": explain(doc.metadata, list(impacted_functions))
    })
 
with open("output/prioritized_testcases.json", "w") as f:
    json.dump(results, f, indent=2)