"""Gera um notebook de arquivo único com os GPKGs originais embutidos.

Reexecutar após mudar estudo.py, os dados ou o notebook principal.
Não inclui modelos prontos: o professor executa a análise e o treino reais.
"""
from pathlib import Path
import base64
import hashlib
import io
import json
import zipfile

import nbformat

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT/'ml/agua_na_rua_colab.ipynb'


def build():
    files = sorted((ROOT/'ml/dados').rglob('*.gpkg'))
    files += [ROOT/'ml/estudo.py', ROOT/'ml/requirements.txt',
              *sorted(p for p in (ROOT/'docs').rglob('*') if p.is_file()),
              ROOT/'prompt-codex-ml-agua-na-rua.md']
    manifest = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026,11,13,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info,path.read_bytes())
    payload = buffer.getvalue()
    b64 = base64.b64encode(payload).decode('ascii')
    encoded = '\n'.join(repr(b64[i:i+120]) for i in range(0,len(b64),120))
    notebook = nbformat.read(ROOT/'ml/apoio/agua_na_rua_ml.ipynb',as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == 'markdown':
            # Corrigir caracteres de ligação corrompidos na redação inicial.
            cell.source=cell.source.replace(' → ',' é ')
            cell.source=cell.source.replace('# Água na Rua é perfis','# Água na Rua — perfis')
            cell.source=cell.source.replace('96 distritos é 13 anos é 12 meses','96 distritos × 13 anos × 12 meses')
            cell.source=cell.source.replace('adequado é exploração','adequado à exploração').replace('sensível é escala','sensível à escala')
            cell.source=cell.source.replace('VarianceThreshold é StandardScaler é PCA full é KMeans','VarianceThreshold → StandardScaler → PCA full → KMeans')
            cell.source=cell.source.replace('Para avaliação no Google Colab, use a edição de arquivo único `agua_na_rua_colab.ipynb`. Esta edição principal é destinada à leitura no GitHub e à execução local conforme o README.', 'Esta é a edição de arquivo único. O código de apoio foi extraído automaticamente do pacote embutido; execute as células em sequência.')
    intro = nbformat.v4.new_markdown_cell('''# Água na Rua — execução no Google Colab

**Para o professor: importe somente este arquivo e selecione Ambiente de execução → Executar tudo.**

O notebook prepara as bibliotecas automaticamente e contém os 14 GPKGs anuais,
a malha de 96 distritos e o código de apoio. Não exige envio de pastas, ZIP,
Google Drive, URL de repositório nem edição de caminhos. Use o ambiente padrão com CPU.
A preparação inicial depende de internet se alguma biblioteca precisar ser instalada.

As bases embutidas são cópias completas dos arquivos fornecidos, não amostras.
Seus SHA-256 são conferidos antes da análise. O arquivo de 2026 é auditado e
excluído da modelagem, que usa somente ALAGAMENTO de 2013–2025.
Nenhum modelo ou resultado pronto é carregado: treinamento e avaliação são executados novamente.

Ao terminar, os gráficos e as métricas aparecem abaixo e um ZIP de resultados é
oferecido para download. Para guardar também as saídas deste notebook, use
Arquivo → Fazer download → Fazer download de .ipynb no Colab.

As versões usadas na nova execução são registradas em `ml/modelos/metadados.json`;
diferenças de bibliotecas em relação ao ambiente original podem alterar os resultados.
''')
    dependencies = nbformat.v4.new_code_cell('''#@title 1. Preparar bibliotecas automaticamente
import importlib.metadata as _metadata
import re as _re
import subprocess as _subprocess
import sys as _sys

_dependencies = {
    "numpy": (1, 26), "pandas": (2, 2), "geopandas": (1, 0),
    "shapely": (2, 0), "pyogrio": (0, 8), "pyproj": (3, 6),
    "scikit-learn": (1, 4), "matplotlib": (3, 7), "joblib": (1, 3),
    "threadpoolctl": (3, 1), "nbformat": (5, 9), "nbconvert": (7, 0),
    "ipykernel": (6, 0),
}
_missing = []
for _package, _minimum in _dependencies.items():
    try:
        _installed = tuple(map(int, _re.match(r"(\\d+)\\.(\\d+)", _metadata.version(_package)).groups()))
    except _metadata.PackageNotFoundError:
        _installed = (0, 0)
    if _installed < _minimum:
        _missing.append(f"{_package}>={_minimum[0]}.{_minimum[1]}")
if _missing:
    _subprocess.run([_sys.executable, "-m", "pip", "install", "--quiet", *_missing], check=True)
print("Bibliotecas disponíveis. Python:", _sys.version.split()[0])
''')
    bootstrap = '''#@title 2. Abrir os dados completos embutidos (nenhum upload adicional)
from pathlib import Path
import base64, hashlib, io, json, os, tempfile, zipfile

# ZIP codificado dentro deste arquivo para permitir a execução sem outros anexos.
_DATA = (
''' + encoded + '''
)
_archive = base64.b64decode(_DATA)
assert hashlib.sha256(_archive).hexdigest() == '''+repr(hashlib.sha256(payload).hexdigest())+'''
_manifest = json.loads('''+repr(json.dumps(manifest,ensure_ascii=False))+''')
# Pasta isolada: não depende da localização do notebook nem altera arquivos do repositório.
root = Path(tempfile.mkdtemp(prefix="agua_na_rua_colab_"))
with zipfile.ZipFile(io.BytesIO(_archive)) as _zip:
    assert set(_zip.namelist()) == set(_manifest)
    for _name in _zip.namelist():
        _target = (root / _name).resolve()
        assert _target.is_relative_to(root.resolve())
        _target.parent.mkdir(parents=True, exist_ok=True)
        _content = _zip.read(_name)
        assert hashlib.sha256(_content).hexdigest() == _manifest[_name]
        _target.write_bytes(_content)
os.chdir(root)
print("Arquivos íntegros:", len(_manifest), "— 15 GPKGs completos, código e referências prontos.")
del _DATA, _archive
'''
    packed = nbformat.v4.new_code_cell(bootstrap,metadata={'cellView':'form','jupyter':{'source_hidden':True}})
    notebook.cells = [intro,dependencies,packed] + notebook.cells
    notebook.cells.append(nbformat.v4.new_markdown_cell('''## Salvar os resultados

A célula abaixo reúne relatório, README, roteiro, dados processados, métricas,
gráficos e modelo gerados nesta execução. No Colab, o download começa automaticamente.
O notebook com as saídas deve ser salvo pelo menu Arquivo do Colab.
'''))
    notebook.cells.append(nbformat.v4.new_code_cell('''#@title Baixar resultados desta execução
import zipfile

# Registrar as versões efetivamente usadas, em vez de reutilizar os pins locais.
(root / "ml/requirements-execucao.txt").write_text(
    "".join(f"{package}=={version}\\n" for package, version in sorted(s["versions"].items())),
    encoding="utf-8",
)
_result_zip = root / "agua-na-rua-resultados.zip"
_result_files = [root / "README.md", root / "RELATORIO_ML.md",
                 root / "docs/ROTEIRO_VIDEO_ML.md", root / "ml/requirements-execucao.txt"]
for _folder in [e.PROC, e.OUT, e.MODEL]:
    _result_files.extend(p for p in _folder.rglob("*") if p.is_file())
with zipfile.ZipFile(_result_zip, "w", zipfile.ZIP_DEFLATED) as _zip:
    for _file in sorted(_result_files):
        _zip.write(_file, _file.relative_to(root).as_posix())
print("Análise concluída. Resultados:", _result_zip.name)
try:
    from google.colab import files as _colab_files
except ImportError:
    print("Execução fora do Colab. ZIP salvo em:", _result_zip)
else:
    _colab_files.download(str(_result_zip))
'''))
    notebook.metadata['colab'] = {'name':DEST.name,'provenance':[]}
    notebook.metadata['kernelspec']={'display_name':'Python 3','language':'python','name':'python3'}
    notebook.metadata['agua_na_rua']={'pacote_sha256':hashlib.sha256(payload).hexdigest(),'arquivos_sha256':manifest,'gerador':'ml/apoio/preparar_colab.py'}
    for cell in notebook.cells:
        if cell.cell_type=='code':
            cell.outputs=[]
            cell.execution_count=None
    nbformat.validate(notebook)
    nbformat.write(notebook, DEST)
    print(f'Criado: {DEST.name} ({DEST.stat().st_size/1e6:.2f} MB; dados comprimidos: {len(payload)/1e6:.2f} MB)')


if __name__=='__main__':
    build()
