"""Execute the trusted local audit notebook sequentially using standard Python.

This is not a Jupyter kernel. It records actual stdout and execution order for
these standard-library cells. Review notebook code before running it.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'notebooks/01_raw_data_audit.ipynb'
notebook = json.loads(path.read_text())
namespace = {'__name__': '__main__'}
os.chdir(ROOT)
count = 0
for cell in notebook['cells']:
    if cell['cell_type'] != 'code':
        continue
    count += 1
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(''.join(cell['source']), f'{path.name}:cell{count}', 'exec'), namespace)
    cell['execution_count'] = count
    cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout',
                        'text': output.getvalue().splitlines(keepends=True)}]
    print(f'CELL {count}\n{output.getvalue()}', end='')
notebook['metadata']['language_info']['version'] = sys.version.split()[0]
path.write_text(json.dumps(notebook, indent=1) + '\n')
print('Saved actual Python execution outputs to', path.relative_to(ROOT))
