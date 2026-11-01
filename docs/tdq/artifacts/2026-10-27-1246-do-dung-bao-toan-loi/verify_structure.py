import ast, json, subprocess, sys
from pathlib import Path
root = Path.cwd()
base = '3e0ef5f8a148cbf8aae1e932995e844e8f62ccd9'
files = ['scripts/tdq_transcript.py','scripts/tdq_test_result.py','scripts/token_audit.py','scripts/tdq_timing.py','scripts/tdq_test.py','scripts/tdq_state.py','scripts/step_audit.py']
def functions(tree):
    return {n.name:n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def estimate(node):
    value = 1
    for n in ast.walk(node):
        if isinstance(n,(ast.If,ast.For,ast.AsyncFor,ast.While,ast.IfExp,ast.ExceptHandler,ast.Assert)):
            value += 1
        elif isinstance(n,ast.BoolOp): value += len(n.values)-1
        elif isinstance(n,ast.comprehension): value += 1+len(n.ifs)
    return value
rows = []
for name in files:
    tree = ast.parse(root.joinpath(name).read_text(encoding='utf-8'))
    proc = subprocess.run(['git','show',base+':'+name],capture_output=True,encoding='utf-8')
    old = functions(ast.parse(proc.stdout)) if proc.returncode == 0 else {}
    imports = sorted({(n.module or '').split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)} | {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names})
    changed = [{'name':name_, 'line':n.lineno, 'cc_ast_estimate':estimate(n)} for name_,n in functions(tree).items() if name_ not in old or ast.dump(n) != ast.dump(old[name_])]
    rows.append({'file':name,'imports':imports,'forbidden_imports':[i for i in imports if i in {'hooks','tests'}],'changed_functions':changed})
result = {'method':'AST structural review; branch count estimate, not ruff/radon/cognitive certification','files':rows,'new_modules_stdlib_only':all(set(row['imports']) <= sys.stdlib_module_names for row in rows[:2]),'forbidden_imports':sum(len(r['forbidden_imports']) for r in rows),'max_cc_ast_estimate':max(f['cc_ast_estimate'] for row in rows for f in row['changed_functions'])}
print(json.dumps(result,ensure_ascii=False,indent=2))
