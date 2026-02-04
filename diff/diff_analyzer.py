import ast
import os
 
def extract_functions(code):
    tree = ast.parse(code)
    return {node.name: ast.dump(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)}
 
def find_changed_functions(old_dir, new_dir):
    changed = set()
 
    for file in os.listdir(new_dir):
        if not file.endswith(".py"):
            continue
 
        with open(f"{old_dir}/{file}") as f:
            old_code = f.read()
        with open(f"{new_dir}/{file}") as f:
            new_code = f.read()
 
        old_funcs = extract_functions(old_code)
        new_funcs = extract_functions(new_code)
 
        for fn in new_funcs:
            if fn not in old_funcs or old_funcs[fn] != new_funcs[fn]:
                changed.add(fn)
 
    return list(changed)
 