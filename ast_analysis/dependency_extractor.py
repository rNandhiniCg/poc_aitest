import ast
 
def extract_dependencies(code):
    tree = ast.parse(code)
    deps = {}
 
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            calls = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        calls.add(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        calls.add(child.func.attr)
            deps[node.name] = list(calls)
 
    return deps


'''
class FunctionDependencyExtractor(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}
 
    def visit_FunctionDef(self, node):
        func_name = node.name
        dependencies = set()
 
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    dependencies.add(child.func.attr)
 
        self.functions[func_name] = list(dependencies)
        self.generic_visit(node)
 
def extract_dependencies(code: str):
    tree = ast.parse(code)
    extractor = FunctionDependencyExtractor()
    extractor.visit(tree)
    return extractor.functions
    '''