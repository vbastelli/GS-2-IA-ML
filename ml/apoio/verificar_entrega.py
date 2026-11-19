"""Verifica os artefatos executados sem treinar ou consultar novamente o teste."""
from pathlib import Path
import json
import hashlib
import nbformat
import pandas as pd
import joblib

root=Path(__file__).resolve().parents[2]
out=root/'ml/resultados'
nb=nbformat.read(root/'ml/apoio/agua_na_rua_ml.ipynb',as_version=4)
nbformat.validate(nb)
code=[c for c in nb.cells if c.cell_type=='code']
assert all(c.execution_count is not None for c in code)
assert not [o for c in code for o in c.outputs if o.output_type=='error']
assert sum('image/png' in o.get('data',{}) for c in code for o in c.outputs)==7
manifest=json.loads((out/'manifesto_fontes.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256((root/f['arquivo']).read_bytes()).hexdigest()==f['sha256'] for f in manifest['arquivos'])
assert (root/'docs/agua-na-rua.md').read_text(encoding='utf-8') in (root/'README.md').read_text(encoding='utf-8')
split=pd.read_csv(out/'divisao_distritos.csv',dtype={'codigo_distrito':str})
folds=pd.read_csv(out/'ids_folds.csv',dtype={'codigo_distrito':str})
train=set(split.loc[split.conjunto.eq('treino'),'codigo_distrito'])
test=set(split.loc[split.conjunto.eq('teste'),'codigo_distrito'])
assert not train&test and split.codigo_distrito.is_unique
assert set(folds.codigo_distrito)<=train
for _,f in folds.groupby('fold'):
    a=set(f.loc[f.papel.eq('subtreino'),'codigo_distrito'])
    b=set(f.loc[f.papel.eq('validacao'),'codigo_distrito'])
    assert not a&b and a|b==train
search=pd.read_csv(out/'busca_cv.csv')
assert len(search)==18
assert search.iloc[0].folds_validos==3
assert search.loc[search.folds_validos.lt(3),'media'].isna().all()
metrics=json.loads((out/'metricas_finais.json').read_text(encoding='utf-8'))
report=(root/'RELATORIO_ML.md').read_text(encoding='utf-8')
assert all(f"{metrics['resultados'][k]['silhouette']:.4f}" in report for k in ['treino','teste'])
model=joblib.load(root/'ml/modelos/pipeline_avaliado.joblib')
assert int(model['escala'].n_samples_seen_)==len(train)
quality=json.loads((root/'ml/dados/processados/balanco_limpeza.json').read_text(encoding='utf-8'))
counts=pd.read_csv(root/'ml/dados/processados/contagens_distrito_ano_mes.csv')
assert len(counts)==96*13*12 and counts.registros.sum()==quality['restantes']
result=dict(notebook_sem_erros=True,celulas_codigo_executadas=len(code),figuras_no_notebook=7,hashes_originais_preservados=len(manifest['arquivos']),ficha_preservada=True,treino=len(train),teste=len(test),cv_somente_treino=True,configuracoes_avaliadas=len(search),configuracoes_com_tres_folds_validos=int(search.folds_validos.eq(3).sum()),modelo_ajustado_em_distritos=int(model['escala'].n_samples_seen_),contagens_e_documentos_coerentes=True)
(out/'verificacao_entrega.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
