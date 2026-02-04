import ast
import os
import re
 
def extract_testcases(test_dir):
    testcases = []
 
    for file in os.listdir(test_dir):
        if not file.endswith(".py"):
            continue
 
        with open(os.path.join(test_dir, file), encoding="utf-8") as f:
            tree = ast.parse(f.read())
 
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
 
                # 1Try to extract TC_XX pattern
                match = re.search(r"(TC[_-]?\d+)", node.name, re.IGNORECASE)
 
                if match:
                    testcase_id = match.group(1).replace("-", "_")
                else:
                    # Fallback: use full function name
                    testcase_id = node.name
 
                # Docstring → description
                description = ast.get_docstring(node) or "No description provided"
 
                # Extract called functions
                functions = set()
                for call in ast.walk(node):
                    if isinstance(call, ast.Call):
                        if isinstance(call.func, ast.Name):
                            functions.add(call.func.id)
                        elif isinstance(call.func, ast.Attribute):
                            functions.add(call.func.attr)
 
                testcases.append({
                    "testcase_id": testcase_id,
                    "description": description,
                    "functions": sorted(functions),
                    "source_file": file
                })
 
    return testcases
 
"""  #FOr tc_xx str test cases only
import ast
import os
import re
 
def extract_testcases(test_dir):
    testcases = []
 
    for file in os.listdir(test_dir):
        if not file.endswith(".py"):
            continue
 
        with open(os.path.join(test_dir, file)) as f:
            tree = ast.parse(f.read())
 
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
 
                # Extract TC_XX using regex
                match = re.search(r"(TC_\d+)", node.name)
                testcase_id = match.group(1) if match else node.name
 
                description = ast.get_docstring(node) or "No description"
 
                functions = set()
                for call in ast.walk(node):
                    if isinstance(call, ast.Call):
                        if isinstance(call.func, ast.Name):
                            functions.add(call.func.id)
                        elif isinstance(call.func, ast.Attribute):
                            functions.add(call.func.attr)
 
                testcases.append({
                    "testcase_id": testcase_id,
                    "description": description,
                    "functions": list(functions)
                })
 
    return testcases
 """