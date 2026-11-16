"""Executa todo o notebook em kernel limpo do Python que chama este script."""
from pathlib import Path
import json
import os
import sys
import tempfile
import argparse
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--colab',action='store_true',help='Validar a edição de arquivo único em kernel limpo local.')
args=parser.parse_args()
path=root/'ml'/('agua_na_rua_colab.ipynb' if args.colab else 'agua_na_rua_ml.ipynb')
with tempfile.TemporaryDirectory(prefix='agua_na_rua_kernel_') as folder:
    kernel=Path(folder)/'kernels'/'agua-na-rua'
    kernel.mkdir(parents=True)
    (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Água na Rua (.venv)','language':'python'}),encoding='utf-8')
    os.environ['JUPYTER_PATH']=folder+os.pathsep+os.environ.get('JUPYTER_PATH','')
    os.environ['JUPYTER_RUNTIME_DIR']=str(Path(folder)/'runtime')
    os.environ['IPYTHONDIR']=str(Path(folder)/'ipython')
    os.environ['MPLCONFIGDIR']=str(Path(folder)/'matplotlib')
    notebook=nbformat.read(path,as_version=4)
    executor=ExecutePreprocessor(timeout=600,kernel_name='agua-na-rua')
    executor.preprocess(notebook,{'metadata':{'path':str(root)}})
    assert all(o.output_type!='error' for c in notebook.cells if c.cell_type=='code' for o in c.get('outputs',[]))
    nbformat.write(notebook,path)
print('Notebook executado e salvo:',path)
