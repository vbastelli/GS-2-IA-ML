"""Estudo reproduzível: funções chamadas, em sequência, pelo notebook."""
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import sqlite3
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.validation import explain_validity
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.model_selection import KFold, ParameterGrid, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
import joblib

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'ml/dados/processados'
OUT = ROOT / 'ml/resultados'
FIG = OUT / 'figuras'
MODEL = ROOT / 'ml/modelos'
YEARS = list(range(2013, 2026))
OCC_URL = 'https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/432c06b1-03a1-4b1f-9210-423e1b58e869'
DIST_URL = 'https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/51f75eab-6d90-451e-9f80-c21c1ac72630'
COLORS = ['#0072B2', '#E69F00', '#CC79A7', '#009E73']


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def csv(df, path):
    df.to_csv(path, index=False, encoding='utf-8-sig')


def normalize(value):
    if pd.isna(value):
        return ''
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value)) if not unicodedata.combining(c)).strip().upper()


def polygon_parts(geom):
    if geom.geom_type in ('Polygon', 'MultiPolygon'):
        return geom
    return shapely.union_all([polygon_parts(g) for g in geom.geoms if g.geom_type in ('Polygon', 'MultiPolygon', 'GeometryCollection')])


def audit():
    for folder in [PROC, OUT, FIG, MODEL]:
        folder.mkdir(parents=True, exist_ok=True)
    inventory, overview, types, months, frames = [], [], [], [], []
    for path in sorted((ROOT / 'ml/dados').rglob('*.gpkg')):
        with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True) as db:
            table, srs = db.execute("SELECT table_name,srs_id FROM gpkg_contents WHERE data_type='features'").fetchone()
            schema = db.execute(f'PRAGMA table_info("{table}")').fetchall()
        fields = [r[1] for r in schema]
        inventory.append(dict(arquivo=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size, camada=table, epsg=srs, esquema=[dict(nome=r[1], tipo=r[2]) for r in schema], url_origem=DIST_URL if 'distrito' in path.name else OCC_URL, url_download_efetivo=None, data_download=None))
        if 'riscoocorrencia' not in path.name:
            continue
        # Lista explícita: não exportar textos livres nem informações de solicitantes.
        use = [c for c in ['data', 'ocorrencia', 'name', 'subprefeit', 'subpreit', 'nm_distrito'] if c in fields]
        df = gpd.read_file(path, layer=table, columns=use, fid_as_index=True)
        assert df.crs.to_epsg() == srs == 31983
        df['fid_origem'] = df.index
        df = df.reset_index(drop=True)
        df['arquivo'] = path.name
        df['ano_arquivo'] = int(path.stem.rsplit('_', 1)[1])
        df['data_original'] = df['data'].astype('string')
        df['data'] = pd.to_datetime(df['data'], errors='coerce', format='%Y-%m-%d')
        df['tipo'] = df.ocorrencia.map(normalize)
        df['ano'] = df.data.dt.year
        df['mes'] = df.data.dt.month
        for tipo, n in df.groupby('tipo', dropna=False).size().items():
            types.append(dict(ano_arquivo=int(df.ano_arquivo.iloc[0]), tipo=tipo, registros=int(n)))
        for (ano, mes), n in df.dropna(subset=['data']).groupby(['ano','mes']).size().items():
            months.append(dict(ano_arquivo=int(df.ano_arquivo.iloc[0]), ano=int(ano), mes=int(mes), registros_todos_tipos=int(n)))
        overview.append(dict(arquivo=path.name, ano_arquivo=int(df.ano_arquivo.iloc[0]), total=len(df), data_min=str(df.data.min().date()), data_max=str(df.data.max().date()), datas_invalidas=int(df.data.isna().sum()), ano_divergente=int((df.ano.notna() & df.ano.ne(df.ano_arquivo)).sum()), meses_todos_tipos=int(df.data.dt.to_period('M').nunique()), alagamentos=int(df.tipo.eq('ALAGAMENTO').sum()), identificadores_vazios=int(df['name'].fillna('').str.strip().eq('').sum()), campo_distrito='nm_distrito' in fields))
        frames.append(df)
    overview = pd.DataFrame(overview)
    coverage = pd.DataFrame(months)
    csv(overview, OUT/'auditoria_arquivos.csv')
    csv(pd.DataFrame(types), OUT/'tipos_por_arquivo.csv')
    csv(coverage, OUT/'cobertura_mensal_todos_tipos.csv')
    save_json(OUT/'manifesto_fontes.json', dict(data_inspecao=datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(), consulta_catalogos='2026-11-12', arquivos=inventory, nota='Arquivos fornecidos pelo usuário. Data e URL direta do download não informadas; hashes permitem verificar as cópias locais.'))
    assert overview.datas_invalidas.sum() == 0
    assert overview.ano_divergente.sum() == 0, 'Investigar sobreposição de snapshots antes de contar.'
    assert set(YEARS).issubset(set(overview.ano_arquivo))
    # Presença de outros tipos em todos os meses permite zeros observados de ALAGAMENTO;
    # não comprova exaustividade do sistema de notificações.
    assert all(len(coverage[(coverage.ano == y) & (coverage.ano_arquivo == y)]) == 12 for y in YEARS)
    return dict(raw=gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=31983), overview=overview, coverage=coverage)


def prepare(s):
    raw = s['raw']
    scoped = raw[raw.ano.between(2013, 2025)].copy()
    floods = scoped[scoped.tipo.eq('ALAGAMENTO')].copy()
    floods['id_registro'] = floods['name'].fillna('').astype(str).str.strip()
    floods['subprefeitura_original'] = floods['subprefeit'].fillna(floods.get('subpreit', pd.Series(index=floods.index, dtype=str))).fillna('')
    floods['distrito_original'] = floods.get('nm_distrito', pd.Series('', index=floods.index)).fillna('')
    floods['wkb'] = floods.geometry.to_wkb(hex=True)
    keys = ['ano_arquivo','id_registro','data','tipo','subprefeitura_original','distrito_original','wkb']
    # Só colapsar repetições exatas com identificador conhecido; IDs reiniciam entre anos.
    duplicates = floods.id_registro.ne('') & floods.duplicated(keys, keep='first')
    csv(floods.loc[duplicates, ['arquivo','fid_origem','id_registro','data']], PROC/'duplicatas_removidas.csv')
    n_dup = int(duplicates.sum())
    floods = floods.loc[~duplicates].drop(columns='wkb').copy().reset_index(drop=True)
    floods['chave_registro'] = floods.arquivo + ':' + floods.fid_origem.astype(str)
    districts = gpd.read_file(ROOT/'ml/dados/distritos/distrito_municipal_v2.gpkg', columns=['cd_distrito_municipal','nm_distrito_municipal','qt_area_quilometro'])
    assert districts.crs.to_epsg() == 31983
    districts = districts.rename(columns={'cd_distrito_municipal':'codigo_distrito','nm_distrito_municipal':'distrito'})
    districts['codigo_distrito'] = districts.codigo_distrito.astype(str).str.zfill(2)
    repairs = []
    for idx in districts.index[~districts.is_valid]:
        old = districts.loc[idx, 'geometry']
        new = polygon_parts(shapely.make_valid(old))
        repairs.append(dict(distrito=districts.loc[idx,'distrito'], motivo=explain_validity(old), area_antes_m2=old.area, area_depois_m2=new.area, tipo_depois=new.geom_type))
        districts.loc[idx, 'geometry'] = new
    csv(pd.DataFrame(repairs), OUT/'reparos_malha.csv')
    assert len(districts) == 96 and districts.codigo_distrito.is_unique
    assert districts.is_valid.all() and not districts.is_empty.any()
    districts['area_km2'] = districts.area / 1e6
    valid = floods.geometry.notna() & ~floods.geometry.is_empty & floods.geometry.is_valid & floods.geom_type.eq('Point')
    floods['situacao_distrito'] = 'geometria_inutilizavel'
    floods['codigo_distrito'] = pd.Series(index=floods.index, dtype='string')
    floods['distrito'] = pd.Series(index=floods.index, dtype='string')
    lookup = districts.set_index(districts.distrito.map(normalize))
    # intersects inclui a fronteira. Mais de um polígono => não escolher arbitrariamente.
    joined = gpd.sjoin(floods.loc[valid, ['geometry']], districts[['codigo_distrito','distrito','geometry']], how='left', predicate='intersects')
    for idx in floods.index[valid]:
        candidates = joined.loc[[idx]].dropna(subset=['codigo_distrito']).drop_duplicates('codigo_distrito')
        name = normalize(floods.loc[idx,'distrito_original'])
        if name and name in lookup.index:
            row = lookup.loc[name]
            floods.loc[idx, ['codigo_distrito','distrito','situacao_distrito']] = [row.codigo_distrito, row.distrito, 'campo_validado' if row.codigo_distrito in candidates.codigo_distrito.values else 'campo_divergente']
        elif len(candidates) == 1:
            row = candidates.iloc[0]
            floods.loc[idx, ['codigo_distrito','distrito','situacao_distrito']] = [row.codigo_distrito, row.distrito, 'cruzamento_espacial']
        else:
            floods.loc[idx,'situacao_distrito'] = 'fora_da_malha' if len(candidates) == 0 else 'ambiguo_na_fronteira'
    unresolved = floods.codigo_distrito.isna()
    floods['distancia_malha_m'] = np.nan
    for idx in floods.index[unresolved & valid]:
        floods.loc[idx,'distancia_malha_m'] = districts.distance(floods.loc[idx,'geometry']).min()
    safe_cols = ['chave_registro','arquivo','fid_origem','id_registro','data','ano','mes','tipo','distrito_original','codigo_distrito','distrito','situacao_distrito','distancia_malha_m']
    csv(floods.loc[unresolved,safe_cols], PROC/'alagamentos_sem_distrito.csv')
    clean = floods.loc[~unresolved].copy()
    clean['x_utm_m'] = clean.geometry.x
    clean['y_utm_m'] = clean.geometry.y
    csv(clean[safe_cols+['x_utm_m','y_utm_m']], PROC/'alagamentos_2013_2025.csv')
    grid = pd.MultiIndex.from_product([districts.codigo_distrito.sort_values(), YEARS, range(1,13)], names=['codigo_distrito','ano','mes'])
    counts = clean.groupby(['codigo_distrito','ano','mes']).size().reindex(grid, fill_value=0).rename('registros').reset_index()
    csv(counts, PROC/'contagens_distrito_ano_mes.csv')
    annual = counts.groupby(['codigo_distrito','ano']).registros.sum().unstack('ano')
    month = counts.groupby(['codigo_distrito','mes']).registros.sum().unstack('mes')
    features = districts[['codigo_distrito','distrito','area_km2']].set_index('codigo_distrito').sort_index()
    features['total_registros'] = annual.sum(axis=1)
    features['media_anual'] = annual.mean(axis=1)
    features['fracao_anos_com_registro'] = annual.gt(0).mean(axis=1)
    features['cv_anual'] = annual.std(axis=1, ddof=0).div(features.media_anual.replace(0,np.nan))
    features['densidade_anual_km2'] = features.media_anual / features.area_km2
    for m in range(1,13):
        features[f'prop_mes_{m:02}'] = month[m].div(features.total_registros.replace(0,np.nan))
    features['elegivel'] = features.total_registros.gt(0)
    features = features.reset_index()
    csv(features, PROC/'atributos_distritos.csv')
    quality = dict(carregados=len(raw), excluidos_fora_2013_2025=len(raw)-len(scoped), outros_tipos_no_periodo=len(scoped)-int(scoped.tipo.eq('ALAGAMENTO').sum()), alagamentos_brutos=int(scoped.tipo.eq('ALAGAMENTO').sum()), duplicatas_removidas=n_dup, apos_deduplicacao=len(floods), sem_distrito=int(unresolved.sum()), restantes=len(clean), distritos_com_registros=int(features.elegivel.sum()), identificadores_vazios_preservados=int(floods.id_registro.eq('').sum()), associacao={str(k):int(v) for k,v in floods.situacao_distrito.value_counts().items()})
    assert quality['alagamentos_brutos'] == n_dup+quality['sem_distrito']+len(clean)
    assert clean.chave_registro.is_unique and features.codigo_distrito.is_unique
    save_json(PROC/'balanco_limpeza.json', quality)
    s.update(clean=clean, districts=districts, features=features, quality=quality)
    return s


def model_data(df):
    x = df[['media_anual','fracao_anos_com_registro','cv_anual','densidade_anual_km2']+[f'prop_mes_{m:02}' for m in range(1,13)]].copy()
    x[['media_anual','densidade_anual_km2']] = np.log1p(x[['media_anual','densidade_anual_km2']])
    return x


def pipeline(params):
    return Pipeline([('constantes', VarianceThreshold()), ('escala', StandardScaler()), ('pca', PCA(svd_solver='full', random_state=42)), ('kmeans', KMeans(random_state=42, max_iter=300, algorithm='lloyd'))]).set_params(**params)


def metrics(pipe, x):
    labels = pipe.predict(x)
    z = pipe[:2].transform(x)
    k = len(np.unique(labels))
    ok = 1 < k < len(x)
    return dict(n=len(x), clusters_ocupados=k, silhouette=float(silhouette_score(z,labels)) if ok else None, davies_bouldin=float(davies_bouldin_score(z,labels)) if ok else None, motivo=None if ok else 'Número de rótulos incompatível com a métrica.')


def train(s):
    features = s['features'].loc[s['features'].elegivel].sort_values('codigo_distrito').reset_index(drop=True)
    x = model_data(features)
    assert np.isfinite(x.to_numpy()).all()
    tr, te = train_test_split(np.arange(len(x)), test_size=.2, random_state=42)
    assert not set(tr)&set(te)
    split = features[['codigo_distrito','distrito']].copy()
    split['conjunto'] = np.where(split.index.isin(tr),'treino','teste')
    csv(split, OUT/'divisao_distritos.csv')
    cv = list(KFold(n_splits=3,shuffle=True,random_state=42).split(tr))
    rows, fold_rows, fold_ids = [], [], []
    for fold,(a,b) in enumerate(cv,1):
        assert not set(tr[a])&set(te) and not set(tr[b])&set(te)
        for kind, ids in [('subtreino',tr[a]),('validacao',tr[b])]:
            fold_ids.extend(dict(fold=fold,papel=kind,codigo_distrito=features.iloc[i].codigo_distrito) for i in ids)
    csv(pd.DataFrame(fold_ids), OUT/'ids_folds.csv')
    grid = list(ParameterGrid({'kmeans__n_clusters':[2,3,4],'kmeans__n_init':[10,30],'pca__n_components':[.80,.90,.95]}))
    assert len(grid)==18 and all(len(g)==3 for g in grid)
    with threadpool_limits(limits=1):
        for candidate, params in enumerate(grid,1):
            scores=[]
            for fold,(a,b) in enumerate(cv,1):
                pipe=pipeline(params).fit(x.iloc[tr[a]])
                result=metrics(pipe,x.iloc[tr[b]])
                fold_rows.append(dict(candidato=candidate,fold=fold,**params,**result))
                if result['silhouette'] is not None: scores.append(result['silhouette'])
            rows.append(dict(candidato=candidate,**params,folds_validos=len(scores),media=float(np.mean(scores)) if len(scores)==3 else np.nan,desvio=float(np.std(scores)) if len(scores)==3 else np.nan))
        search=pd.DataFrame(rows).sort_values(['media','desvio','kmeans__n_clusters','candidato'],ascending=[False,True,True,True],na_position='last')
        search['classificacao']=range(1,len(search)+1)
        csv(search, OUT/'busca_cv.csv')
        csv(pd.DataFrame(fold_rows), OUT/'metricas_folds.csv')
        valid=search[search.folds_validos.eq(3)]
        if valid.empty: raise RuntimeError('Nenhuma configuração com três folds válidos. Não selecionar vencedor.')
        best=valid.iloc[0]
        params={'kmeans__n_clusters':int(best['kmeans__n_clusters']),'kmeans__n_init':int(best['kmeans__n_init']),'pca__n_components':float(best['pca__n_components'])}
        pipe=pipeline(params).fit(x.iloc[tr])
        # Uma única avaliação do conjunto reservado, após encerrar a escolha.
        results={'treino':metrics(pipe,x.iloc[tr]),'teste':metrics(pipe,x.iloc[te])}
    joblib.dump(pipe, MODEL/'pipeline_avaliado.joblib')
    versions={p:metadata.version(p) for p in ['pandas','numpy','geopandas','shapely','pyogrio','pyproj','scikit-learn','matplotlib','joblib','threadpoolctl','nbformat','nbconvert','ipykernel']}
    save_json(MODEL/'metadados.json',dict(versoes=versions,parametros=params,treinado_em='Somente distritos do treino; não reajustado no conjunto completo.',atributos=list(x.columns),log1p=['media_anual','densidade_anual_km2'],seed=42))
    save_json(OUT/'metricas_finais.json',dict(parametros=params,cv_media=float(best.media),cv_desvio=float(best.desvio),resultados=results,variancia_explicada=pipe['pca'].explained_variance_ratio_.tolist(),n_componentes=int(pipe['pca'].n_components_)))
    csv(pd.DataFrame(results).T.reset_index(names='conjunto'),OUT/'metricas_finais.csv')
    assignments=features.merge(split,on=['codigo_distrito','distrito'],validate='one_to_one')
    assignments['grupo']=pipe.predict(x)
    csv(assignments,OUT/'distritos_grupos.csv')
    profiles=assignments[assignments.conjunto.eq('treino')].groupby('grupo').agg(n=('distrito','size'),media_anual=('media_anual','mean'),densidade_anual_km2=('densidade_anual_km2','mean'),fracao_anos_com_registro=('fracao_anos_com_registro','mean'),cv_anual=('cv_anual','mean'))
    csv(profiles.reset_index(),OUT/'perfis_grupos_treino.csv')
    s.update(x=x,tr=tr,te=te,pipe=pipe,search=search,params=params,metrics=results,best=best,assignments=assignments,profiles=profiles,versions=versions)
    return s


def figure(name):
    plt.tight_layout()
    plt.savefig(FIG/name,dpi=160,bbox_inches='tight')
    plt.close()


def plots(s):
    annual=s['clean'].groupby('ano').size().reindex(YEARS,fill_value=0)
    raw=s['overview'].set_index('ano_arquivo').alagamentos.reindex(YEARS)
    fig,ax=plt.subplots(figsize=(10,4))
    ax.bar(YEARS,raw,color='#999999',label='ALAGAMENTO bruto')
    ax.bar(YEARS,annual,color=COLORS[0],label='Após limpeza e associação')
    ax.set(xlabel='Ano (12 meses com registros de todos os tipos em cada ano)',ylabel='Registros',title='Cobertura observada e ALAGAMENTO — 2013–2025'); ax.legend()
    figure('01_registros_ano.png')
    fig,ax=plt.subplots(figsize=(9,4)); monthly=s['clean'].groupby('mes').size().reindex(range(1,13),fill_value=0)
    ax.bar(monthly.index,monthly,color=COLORS[0]); ax.set(xticks=range(1,13),xlabel='Mês',ylabel='Registros (soma de 13 anos)',title='Distribuição mensal dos registros associados — não indica risco futuro')
    figure('02_registros_mes.png')
    fig,ax=plt.subplots(figsize=(10,4)); search=s['search'].sort_values('candidato')
    ax.errorbar(search.candidato,search.media,yerr=search.desvio,fmt='o',color=COLORS[0],capsize=3); ax.set(xlabel='Candidato (parâmetros em busca_cv.csv)',ylabel='Silhouette média ± desvio dos 3 folds',title='Validação exclusivamente no treino — espaço padronizado anterior ao PCA',xticks=search.candidato)
    figure('03_busca_cv.png')
    fig,axes=plt.subplots(1,2,figsize=(9,4))
    for ax,key,title in zip(axes,['silhouette','davies_bouldin'],['Silhouette (maior é melhor)','Davies–Bouldin (menor é melhor)']):
        vals=[s['metrics'][part][key] for part in ['treino','teste']]
        ax.bar(['Treino','Teste'],[v if v is not None else 0 for v in vals],color=COLORS[:2]); ax.set_title(title)
        for i,v in enumerate(vals): ax.text(i,v or 0,'N/A' if v is None else f'{v:.3f}',ha='center',va='bottom')
    figure('04_metricas.png')
    p=s['pipe']; z=p[:2].transform(s['x']); projection=p['pca'].transform(z)
    extra=''
    if projection.shape[1]<2:
        illustrative=PCA(n_components=2,svd_solver='full').fit(z[s['tr']]); projection=illustrative.transform(z); variance=illustrative.explained_variance_ratio_; extra=' (PCA 2D ilustrativo, ajustado só no treino)'
    else: variance=p['pca'].explained_variance_ratio_
    fig,ax=plt.subplots(figsize=(9,5))
    for group in sorted(s['assignments'].grupo.unique()):
        for part,marker in [('treino','o'),('teste','^')]:
            mask=s['assignments'].grupo.eq(group)&s['assignments'].conjunto.eq(part)
            ax.scatter(projection[mask,0],projection[mask,1],color=COLORS[int(group)],marker=marker,label=f'Grupo {group} · {part}',edgecolor='black',linewidth=.4)
    ax.set(xlabel=f'PC1 ({variance[0]:.1%} da variância)',ylabel=f'PC2 ({variance[1]:.1%})',title='Perfis históricos distritais'+extra); ax.legend(fontsize=8)
    figure('05_componentes.png')
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,key,label in zip(axes,['media_anual','densidade_anual_km2','cv_anual'],['Registros/ano','Registros/ano/km²','CV anual (adimensional)']):
        prof=s['profiles']; ax.bar([f'G{i}\n(n={int(r.n)})' for i,r in prof.iterrows()],prof[key],color=[COLORS[int(i)] for i in prof.index]); ax.set_ylabel(label)
    fig.suptitle('Médias dos perfis dos grupos — somente treino, unidades originais')
    figure('06_perfis.png')
    mapped=s['districts'].merge(s['assignments'][['codigo_distrito','grupo']],on='codigo_distrito',how='left',validate='one_to_one')
    fig,ax=plt.subplots(figsize=(8,8))
    mapped.plot(ax=ax,color='#dddddd',edgecolor='white',linewidth=.3)
    from matplotlib.patches import Patch
    handles=[]
    for group in sorted(s['assignments'].grupo.unique()):
        mapped[mapped.grupo.eq(group)].plot(ax=ax,color=COLORS[int(group)],edgecolor='white',linewidth=.3); handles.append(Patch(facecolor=COLORS[int(group)],label=f'Grupo {group}'))
    handles.append(Patch(facecolor='#dddddd',label='Sem perfil elegível'))
    ax.legend(handles=handles); ax.set(title='Grupos de perfis históricos — São Paulo\nMalha fornecida, revisão de outubro/2026',xlabel='UTM 23S — leste (m)',ylabel='UTM 23S — norte (m)'); ax.set_aspect('equal')
    figure('07_mapa.png')
    s['annual']=annual
    return s


def markdown_table(df):
    # Evita dependência opcional tabulate.
    rows=[list(df.columns)]+[[str(v) for v in row] for row in df.itertuples(index=False,name=None)]
    return '\n'.join(['| '+' | '.join(rows[0])+' |','| '+' | '.join(['---']*len(rows[0]))+' |']+['| '+' | '.join(r)+' |' for r in rows[1:]])


def documents(s):
    q=s['quality']; m=s['metrics']; best=s['best']; p=s['params']
    delivery_path=ROOT/'docs/entrega.json'
    delivery=json.loads(delivery_path.read_text(encoding='utf-8')) if delivery_path.exists() else {}
    repo=delivery.get('repositorio') or '[URL não informada]'
    turma=delivery.get('turma') or 'Não informada'
    video=delivery.get('video') or 'Pendente de gravação e publicação pela equipe'
    video_status=f'[Assistir no YouTube]({video})' if delivery.get('video') else 'Gravação e publicação pendentes da equipe'
    video_nav=f' · **[Vídeo no YouTube]({video})**' if delivery.get('video') else ''
    evidence_path=OUT/'verificacao_colab.json'
    evidence=json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else {}
    colab_status=('A equipe forneceu o notebook executado no Colab. A revisão confirmou células executadas, sete gráficos, ausência de saídas de erro e resultados compatíveis com a execução local.'
                  if evidence.get('colab_hospedado_testado') else
                  'A edição de Colab foi validada em kernel limpo local. A conferência na interface hospedada está pendente.')
    repo_path=repo.removeprefix('https://github.com/').removesuffix('.git')
    colab_url=f'https://colab.research.google.com/github/{repo_path}/blob/main/ml/agua_na_rua_colab.ipynb' if repo.startswith('https://github.com/') else 'https://colab.research.google.com/'
    def fmt(v): return 'N/A' if v is None else f'{v:.4f}'
    mt=markdown_table(pd.DataFrame([dict(Conjunto=k,n=v['n'],Grupos=v['clusters_ocupados'],Silhouette=fmt(v['silhouette']),Davies_Bouldin=fmt(v['davies_bouldin'])) for k,v in m.items()]))
    stats=f"{q['alagamentos_brutos']} registros brutos de ALAGAMENTO em 2013–2025; {q['duplicatas_removidas']} duplicatas removidas; {q['sem_distrito']} sem associação distrital unívoca; **{q['restantes']} registros na análise principal**, em {q['distritos_com_registros']} distritos."
    config=f"`n_clusters={p['kmeans__n_clusters']}`, `n_init={p['kmeans__n_init']}`, `pca.n_components={p['pca__n_components']}`. Silhouette de validação: **{best.media:.4f} ± {best.desvio:.4f}** (3 folds)."
    incomplete=s['search'].loc[s['search'].folds_validos.lt(3),'candidato'].tolist()
    config+=f" Dos 18 candidatos, {18-len(incomplete)} tiveram três folds válidos; candidatos {incomplete} ficaram fora da seleção por terem um fold com somente um grupo previsto (Silhouette indefinida, registrada como N/A)."
    local=s['assignments'].loc[s['assignments'].distrito.eq('CACHOEIRINHA')].iloc[0]
    local_note=f"A [Prefeitura, em notícia de 04/05/2017](https://prefeitura.sp.gov.br/web/casa_verde/w/noticias/71913), situa o Jardim Peri em Vila Nova Cachoeirinha; o [quadro oficial de correspondência OD2007](https://drive.prefeitura.sp.gov.br/cidade/secretarias/upload/urbanismo/infocidade/htmls/12_correspondencia_zonas_od_e_distritos_mun_2007_258.html) relaciona a zona Jardim Peri ao distrito Cachoeirinha. Fontes consultadas em 12/11/2026, usadas como contexto territorial, sem substituir a localização dos pontos candidatos. Na malha fornecida, Cachoeirinha tem {int(local.total_registros)} registros associados no período e recebeu grupo {int(local.grupo)} ({local.conjunto}). Esse agregado distrital não descreve uma rua específica."
    annual=s['clean'].groupby('ano').size()
    early=float(s['clean'].mes.isin([1,2,3]).mean())
    observed=f"Após a limpeza, o maior volume anual é {int(annual.max())} em {int(annual.idxmax())}; janeiro–março concentram {early:.1%} dos registros. Isso descreve esta base de notificações, sem demonstrar tendência física de alagamentos ou efeito de intervenções."
    method="""A unidade é o distrito administrativo. O split 80/20 usa IDs ordenados e seed 42. O teste contém outros distritos no mesmo período; não mede previsão temporal. A grade tem 18 combinações de exatamente três hiperparâmetros: número de grupos [2,3,4], reinicializações [10,30] e variância retida pelo PCA [0,80;0,90;0,95]. Mais reinicializações buscam mínimos melhores da inércia. KFold de três partes, embaralhado com seed 42, usa exclusivamente o treino. Cada fold ajusta remoção de constantes, StandardScaler, PCA full e KMeans no subtreino. A validação recebe predict, sem novo ajuste. Silhouette é calculada antes do PCA, no espaço padronizado pelo subtreino, comparável entre configurações. Só candidatos com três folds válidos concorrem; desempates: menor desvio, menor k e ordem determinística. O teste é consultado uma vez após a escolha; o pipeline salvo permanece ajustado somente no treino.

Os atributos são log1p da média anual e da densidade anual por km², fração dos 13 anos com registro, CV anual (desvio populacional/média) e 12 proporções mensais. Área vem da geometria em EPSG:31983. As proporções somam 1 e recebem padronização individual: juntas podem ter peso maior que um atributo de volume. A dependência entre volume e densidade também influencia o resultado. Essas escolhas foram fixadas antes da busca; não houve seleção usando o teste. Distritos sem registros têm sazonalidade e CV indefinidos e ficam fora do modelo, sem imputação de zeros. Identificadores, coordenadas e nomes não entram no treinamento.
"""
    interpretation=f"As Silhouettes observadas (treino {fmt(m['treino']['silhouette'])}, validação {best.media:.4f} e teste {fmt(m['teste']['silhouette'])}) indicam separação fraca: os perfis se sobrepõem e não sustentam uma tipologia forte. O teste ligeiramente superior ao treino não comprova generalização espacial nem ausência de overfitting."
    limits=interpretation+"\n\n"+"""A presença de registros de todos os tipos nos 156 meses sustenta a cobertura observada, mas não comprova captura completa dos alagamentos. Zero significa zero registros na base consultada; não ausência de alagamentos. Notificação, mudanças de sistema, outliers e subnotificação podem dominar os grupos. A amostra é pequena e distritos vizinhos têm dependência espacial. Proximidade entre métricas de treino e teste não demonstra ausência de overfitting; a busca sobre uma amostra pequena também pode superestimar a validação. Grupos pequenos e dispersão dentro dos grupos devem ser considerados. Silhouette maior indica separação mais clara; Davies–Bouldin menor indica maior compactação relativa, sem medir acurácia nem probabilidade de enchente.

A malha única de outubro/2026 foi aplicada retrospectivamente e dois polígonos foram reparados em memória. Pontos fora da malha ou ambíguos não foram deslocados para o distrito mais próximo. Os campos reais são data/ocorrencia/geom; não há nm_distrito. O significado temporal adotado é a data armazenada na exportação de ocorrências, sem documentação que permita distinguir abertura, evento ou encerramento. Os identificadores name não são globalmente únicos, e há ausências em 2025.

O estudo ajuda a investigar áreas para acompanhamento; não identifica passagem segura nem prevê o próximo alagamento. Faltam coordenadas dos pontos candidatos e validação territorial para relacionar a seleção local aos perfis. A escolha dos três pontos exige observação e conversa com moradores. O indicador de tempo de consulta da Ficha não foi medido. ODS 11.5 e 13.1 são relacionados à contribuição informacional e preparação comunitária, sem evidência de redução de danos ou vítimas.
"""
    limits += '\n\n'+local_note+'\n'
    report=f"""# Relatório de IA & Machine Learning — Água na Rua

Síntese de aproximadamente duas páginas (Markdown não fixa paginação). Detalhes e saídas no [notebook](ml/apoio/agua_na_rua_ml.ipynb).

## Problema, dados e preparação

Pergunta: quais distritos de São Paulo apresentam perfis semelhantes de frequência, recorrência e sazonalidade dos registros públicos de alagamento? O aplicativo tem recorte inicial no Jardim Peri; este experimento independente analisa a cidade em resolução distrital.

{stats}

{observed}

Foram auditados os 14 arquivos anuais fornecidos: 2013–2025 são independentes pelas datas observadas; 2026 cobre janeiro–setembro e foi excluído. Os quatro tipos encontrados são ALAGAMENTO, INUNDACAO, DESLIZAMENTO e QUEDA DE ARVORE. Apenas ALAGAMENTO entra na análise. As datas de todos os registros são válidas e correspondem ao ano do arquivo. Removeram-se repetições exatas com identificador conhecido, data, tipo, geometria e demais atributos iguais, ignorando o FID; registros com ID vazio foram preservados. A associação espacial usa interseção com 96 distritos, sem duplicar pontos de fronteira.

Fontes: [ocorrências GeoSampa]({OCC_URL}) e [distritos GeoSampa]({DIST_URL}), catálogos consultados em 12/11/2026. As cópias locais têm SHA-256 no manifesto. Data e URL direta dos downloads originais não foram fornecidas. Os catálogos registram acesso sem restrições, mas o campo genérico de licença não identifica uma licença específica de redistribuição.

## Modelo e avaliação

KMeans + PCA é permitido pelo edital e explora perfis sem rótulo verdadeiro de risco. PCA reduz correlações; KMeans resume perfis por centroides, com sensibilidade à escala e a outliers.

{method}

Melhor configuração: {config}

{mt}

O PCA reteve {s['pipe']['pca'].n_components_} componentes, explicando {sum(s['pipe']['pca'].explained_variance_ratio_):.2%} da variância do treino. Os grupos são identificadores neutros, sem ordem de perigo. Perfis médios somente do treino:

{markdown_table(s['profiles'].round(3).reset_index())}

## Conclusões e limites

{limits}

Gráficos, métricas por fold, IDs, atribuições e modelo avaliado estão em ml/resultados/ e ml/modelos/. A equipe precisa revisar o conteúdo, gravar o vídeo e preencher os links externos.
"""
    (ROOT/'RELATORIO_ML.md').write_text(report,encoding='utf-8')
    commands="""**Google Colab (arquivo único):** abra `ml/agua_na_rua_colab.ipynb` no Colab e selecione **Ambiente de execução → Executar tudo**. Essa edição contém os GPKGs completos e o código de apoio, prepara as bibliotecas automaticamente e oferece os resultados para download no final. Não é necessário enviar outros arquivos nem alterar caminhos. A primeira preparação pode precisar de internet para instalar bibliotecas. As versões da nova execução ficam registradas nos metadados do modelo.

**Execução local:**

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r ml/requirements.txt
.\\.venv\\Scripts\\python.exe ml/apoio/executar_notebook.py
```

O executor usa o Python do próprio ambiente em kernel limpo, sem instalar kernels globais. Alternativa na interface: abrir `ml/apoio/agua_na_rua_ml.ipynb`, selecionar esse ambiente Python e executar todas as células. Para nbconvert, o executor fornece um kernelspec temporário; não depende de um kernel global com nome específico.
"""
    ficha=(ROOT/'docs/agua-na-rua.md').read_text(encoding='utf-8')
    team=[]
    for line in (ROOT/'docs/integrantes.txt').read_text(encoding='utf-8').splitlines():
        if '| RM:' in line:
            name,rm=line.split('| RM:',1)
            team.append(dict(Integrante=name.removeprefix('NOME:').strip(),RM=rm.strip()))
    readme=f"""# Água na Rua — IA & Machine Learning

Global Solution CitizenTech · Engenharia de Software · **{turma}** · FIAP 2026.2

**[Abrir no Colab]({colab_url})** · **[Baixar notebook para Colab](ml/agua_na_rua_colab.ipynb?raw=1)**{video_nav} · [Relatório](RELATORIO_ML.md) · [Requisitos e evidências](docs/GUIA_AVALIACAO.md) · [Todos os resultados](ml/resultados/README.md)

<details>
<summary><strong>Ficha da CitizenTech — texto integral da proposta comum às disciplinas</strong></summary>

{ficha}
</details>

## Para o professor

1. **Executar:** use o botão **Abrir no Colab** acima e selecione **Ambiente de execução → Executar tudo**. Alternativamente, baixe o `.ipynb` e importe pelo menu Arquivo do Colab.
2. **Conferir a análise:** o [notebook de leitura com saídas](ml/apoio/agua_na_rua_ml.ipynb) é a versão legível no GitHub, com tabelas e sete figuras já salvas. O [relatório](RELATORIO_ML.md) apresenta a síntese.
3. **Conferir os requisitos:** o [guia de avaliação](docs/GUIA_AVALIACAO.md) relaciona cada critério do edital às evidências correspondentes.

O notebook de Colab é **um único arquivo com os 15 GPKGs completos e o código de apoio embutidos**. Não exige outros uploads, Google Drive, clonagem ou edição de caminhos. As bibliotecas são preparadas automaticamente; a instalação pode usar internet. O treinamento é executado novamente, usando CPU. Ao terminar, há download dos resultados. [Instruções detalhadas e limites da validação](docs/EXECUTAR_COLAB.md).

Os atalhos externos passam a funcionar depois que estes arquivos estiverem publicados na branch `main` do repositório indicado. Se a prévia do arquivo grande não carregar no GitHub, use **Download raw file**.

## Pergunta e resultados

**Quais distritos de São Paulo apresentam perfis semelhantes de frequência, recorrência e sazonalidade dos registros públicos de alagamento em 2013–2025?**

Este repositório entrega o estudo de ML independente do aplicativo, com uma linha por distrito. O território inicial do produto é o Jardim Peri; o experimento analisa a cidade em resolução distrital.

{stats}

Foram auditados os 14 arquivos anuais de 2013–2026. Os dados de 2026 cobrem janeiro–setembro e ficam fora da modelagem. As datas dos históricos correspondem ao ano de cada arquivo; a base contém quatro tipos, dos quais somente **ALAGAMENTO** entra no estudo. Os dois polígonos inválidos da malha foram reparados em memória. [Proveniência e regras completas](ml/dados/README.md).

KMeans + PCA, com {m['treino']['n']} distritos no treino e {m['teste']['n']} no teste, seed 42. Foram avaliadas 18 combinações de três hiperparâmetros, em três folds exclusivamente no treino. Melhor configuração: {config}

{mt}

**A separação dos grupos é fraca.** Os perfis se sobrepõem; os resultados não validam classes de risco nem previsão de alagamentos. Teste ligeiramente superior ao treino não demonstra ausência de overfitting. Subnotificação, amostra pequena, dependência espacial e uso retrospectivo da malha de 2026 limitam as conclusões.

![Silhouette e Davies–Bouldin no treino e no teste](ml/resultados/figuras/04_metricas.png)

[Ver cobertura anual e mensal, busca, componentes, perfis e mapa](ml/resultados/README.md).

## Requisitos e arquivos

| O que avaliar | Onde encontrar |
| --- | --- |
| Rubrica e exigências das páginas 31–33 do edital | [Guia de avaliação](docs/GUIA_AVALIACAO.md), com links por critério |
| Notebook para executar com um único arquivo | [agua_na_rua_colab.ipynb](ml/agua_na_rua_colab.ipynb?raw=1) |
| Notebook legível, executado e com saídas | [agua_na_rua_ml.ipynb](ml/apoio/agua_na_rua_ml.ipynb) |
| Relatório de aproximadamente duas páginas | [RELATORIO_ML.md](RELATORIO_ML.md) |
| Fonte, datas, tipos, CRS, limpeza e hashes | [Dados](ml/dados/README.md), [auditoria](ml/resultados/auditoria_arquivos.csv), [manifesto](ml/resultados/manifesto_fontes.json) |
| Grade completa, métricas por fold e IDs | [Busca](ml/resultados/busca_cv.csv), [folds](ml/resultados/metricas_folds.csv), [divisão](ml/resultados/divisao_distritos.csv) |
| Código, dependências e modelo avaliado | [estudo.py](ml/estudo.py), [requirements.txt](ml/requirements.txt), [metadados do modelo](ml/modelos/metadados.json) |
| Vídeo de até cinco minutos | {video_status} · [Roteiro](docs/ROTEIRO_VIDEO_ML.md) |

## Equipe e entrega

{markdown_table(pd.DataFrame(team))}

**Turma:** {turma}. **Repositório:** {repo}. **Vídeo:** {video}.

O prazo do edital é **19/11/2026, às 23h55 de São Paulo**: um integrante envia no Teams os links do GitHub e do vídeo YouTube não listado. A publicação do código, a gravação do vídeo e o envio ao Teams são ações da equipe. [Controle da entrega](docs/ENTREGA.md).

## Reprodução local

{commands}

Após a execução, rode `python ml/apoio/verificar_entrega.py` usando o mesmo ambiente. [Evidências da verificação](ml/resultados/verificacao_entrega.json).

{colab_status} [Verificação da edição de Colab](ml/resultados/verificacao_colab.json).

## Limites para o cidadão

O histórico distrital apoia a investigação de áreas, sem garantir passagem segura ou prever o próximo alagamento. Ausência de registros não significa ausência de alagamentos. A escolha dos três pontos exige observação local e conversa com moradores; o indicador de tempo de consulta da Ficha não foi medido. ODS 11.5 e 13.1 representam contribuição informacional, sem comprovação de redução de danos.

{local_note}
"""
    (ROOT/'README.md').write_text(readme,encoding='utf-8')
    data_doc=f"""# Dados — proveniência, auditoria e reprodução

{stats}

Arquivos originais preservados em brutos/ e distritos/. Os 14 GPKGs anuais e a malha são inventariados com SHA-256, tamanhos, camada, CRS e esquema em [manifesto_fontes.json](../resultados/manifesto_fontes.json). Usaram-se as cópias fornecidas, sem downloads de dados adicionais. Data e endereço direto do download original desconhecidos; não inferidos a partir de nomes ou datas de modificação.

Origem: [GeoSampa — ocorrências]({OCC_URL}); [GeoSampa — distrito]({DIST_URL}); [portal de aquisição manual](https://novogeosampa.prefeitura.sp.gov.br/). Consultas aos catálogos: 12/11/2026. Para nova aquisição, abrir a camada e baixar os históricos anuais 2013–2025 e Distrito em GPKG, manter os nomes e conferir hashes. O portal pode fornecer versões diferentes; nesse caso, reexecutar e revisar a auditoria. Os arquivos fornecidos têm menos de 3 MB cada. Os catálogos indicam acesso sem restrições e uso sob licença genérica sem nome específico; confirmar termos antes de redistribuição externa. Nenhuma coluna de solicitante ou relato livre é exportada.

## Esquema efetivamente observado

- 2013–2025: id (FID local), geom (POINT), data (DATE), ocorrencia (TEXT), subprefeit (subprefeitura, não distrito), name (identificador textual, pode faltar ou repetir).
- 2026: primaryindex, geom, data, ocorrencia, subpreit, name. Auditado, excluído da análise.
- Nenhum GPKG anual tem dt_ocorrencia, dc_tipo_ocorrencia, ge_ponto, nm_distrito ou cd_identificador. A tabela prevista na referência docs/fontes/geosampa.md não descreve estas exportações.
- Malha: distrito_municipal_v2, código cd_distrito_municipal, nome nm_distrito_municipal, geometria ge_poligono, 96 distritos. Revisão catalogada em 27/10/2026. Todos os arquivos em EPSG:31983 (metros); não são latitude/longitude.

Data é interpretada como data registrada na exportação de ocorrências, sem comprovação documental de equivalência à abertura, evento ou encerramento. Não há outra data de ocorrência nos arquivos. Datas e tipos completos por arquivo estão em auditoria_arquivos.csv e tipos_por_arquivo.csv. Não há datas inválidas nem anos divergentes: não são snapshots cumulativos de vários anos. Todos os 156 meses de 2013–2025 têm registros de algum tipo; meses sem ALAGAMENTO são zeros observados desse tipo, sem garantia de completude.

## Regras executadas

Filtrar pelo ano da data, entre 2013 e 2025, e tipo normalizado exatamente ALAGAMENTO; não juntar INUNDACAO. Deduplicar somente quando o identificador não vazio e todos os atributos substantivos coincidem dentro do mesmo ano, incluindo geometria. IDs não são globalmente únicos; coincidência de local/data com IDs distintos é preservada, assim como IDs vazios. Não é possível identificar notificações diferentes do mesmo evento físico sem informação adicional.

São Miguel e Lajeado têm geometrias inválidas. make_valid e extração das partes poligonais foram aplicados em memória, com razões e áreas em reparos_malha.csv. Associação por intersects, em CRS comum: um único candidato é aceito; múltiplos candidatos ou nenhum ficam fora da agregação. Sem snapping nem atribuição ao vizinho mais próximo. Distância à malha é exportada para revisão dos não associados. Uma única versão atual da malha aplicada ao passado introduz limitação histórica.

Balanço: {json.dumps(q,ensure_ascii=False)}

Processados: alagamentos_2013_2025.csv contém apenas registros atribuídos; alagamentos_sem_distrito.csv lista exceções; duplicatas_removidas.csv permite rastrear remoções. Chave_registro é arquivo:FID. Contagens distrito/ano/mês usam grade completa 96×13×12; zeros representam ausência de registros associados. atributos_distritos.csv preserva todos os distritos e indica elegibilidade.

{method}

{commands}

Todas as saídas são regeneradas pelo notebook. requirements.txt fixa dependências diretas verificadas; apoio/requirements-lock.txt captura também dependências transitivas. Não há dados simulados no estudo.
"""
    (ROOT/'ml/dados/README.md').write_text(data_doc,encoding='utf-8')
    video=f"""# Roteiro — vídeo de IA & ML (até 5 minutos)

Turma: {turma}. Repositório: {repo}.

Link YouTube não listado: {video}.

- 0:00–0:35 — Mostrar Ficha no README: cidadão, Jardim Peri, informação recente sobre água nas ruas; ML independente e distrital.
- 0:35–1:20 — Notebook, auditoria e limpeza: {stats} Mostrar 01_registros_ano.png e 02_registros_mes.png; 2026 excluído; campos reais, duplicatas, dois polígonos reparados e exceções de associação.
- 1:20–2:10 — Notebook, atributos e divisão: uma linha por distrito, atributos históricos, log1p, treino/teste 80/20 com seed 42, escalonamento aprendido apenas no treino. PCA e KMeans não têm rótulo de risco.
- 2:10–3:00 — Notebook, busca: 18 combinações de três parâmetros, três folds apenas no treino, rótulos por predict e Silhouette no espaço anterior ao PCA. Mostrar 03_busca_cv.png. Melhor: {config}
- 3:00–3:45 — Mostrar 04_metricas.png e a tabela abaixo. Explicar diferenças entre treino, validação e teste e a possibilidade de overfitting; não alegar precisão de previsão de enchentes.
- 3:45–4:25 — Mostrar 05_componentes.png, 06_perfis.png e 07_mapa.png. Ler os tamanhos e médias reais em perfis_grupos_treino.csv. Números dos grupos não representam níveis de perigo.
- 4:25–4:55 — Conclusão: padrões orientam investigação e observação local, mas não comprovam segurança de ruas. Dependência espacial, subnotificação, malha de 2026 e amostra pequena limitam conclusões. Pontos locais e indicador de tempo da Ficha ainda precisam de validação própria. ODS 11.5 e 13.1 como contribuição informacional.

{mt}

Contexto local para a fala: {local_note}

Antes de enviar: conferir duração ≤5 minutos, link não listado acessível, nomes/RMs e link do GitHub; um integrante envia os dois links na tarefa do Teams até 19/11/2026, 23h55 (São Paulo).
"""
    (ROOT/'docs/ROTEIRO_VIDEO_ML.md').write_text(video,encoding='utf-8')
    gallery=f"""# Resultados executados — Água na Rua

[Voltar ao projeto](../../README.md) · [Relatório](../../RELATORIO_ML.md) · [Requisitos](../../docs/GUIA_AVALIACAO.md) · [Executar no Colab](../../docs/EXECUTAR_COLAB.md)

{stats}

{observed}

## Avaliação

Melhor configuração: {config}

{mt}

{interpretation}

## Figuras

### 1. Cobertura e registros por ano

Os 13 anos têm registros de algum tipo nos 12 meses. As barras comparam ALAGAMENTO bruto e após limpeza/associação; cobertura observada não comprova registro de todos os eventos.

![Cobertura anual, 2013–2025](figuras/01_registros_ano.png)

### 2. Distribuição mensal

Soma de notificações associadas ao longo dos 13 anos; não é previsão ou taxa ajustada por exposição.

![Registros por mês](figuras/02_registros_mes.png)

### 3. Busca de hiperparâmetros

Silhouette média e desvio-padrão de CV, no espaço padronizado anterior ao PCA. Candidatas com folds incompletos têm N/A e não concorrem; seus detalhes continuam exportados.

![Busca no treino](figuras/03_busca_cv.png)

### 4. Treino e teste

![Comparação das métricas](figuras/04_metricas.png)

### 5. Componentes principais

Cores identificam grupos; círculos e triângulos distinguem treino e teste. Os dois primeiros componentes são uma projeção parcial do espaço utilizado pelo modelo.

![Perfis nos componentes principais](figuras/05_componentes.png)

### 6. Perfis interpretáveis

Médias em unidades originais e tamanhos calculados somente no treino, sem ordenar grupos por perigo.

![Perfis dos grupos no treino](figuras/06_perfis.png)

### 7. Mapa dos grupos

Perfis históricos distritais na malha fornecida. Todos os distritos têm perfil elegível nesta execução; nenhum perfil comprova a condição de uma rua.

![Mapa de São Paulo](figuras/07_mapa.png)

## Tabelas e rastreabilidade

| Arquivo | Conteúdo |
| --- | --- |
| [auditoria_arquivos.csv](auditoria_arquivos.csv) | Datas, cobertura, tipos, campos e volume por arquivo anual |
| [tipos_por_arquivo.csv](tipos_por_arquivo.csv) | Contagens de todos os tipos nos 14 anos |
| [cobertura_mensal_todos_tipos.csv](cobertura_mensal_todos_tipos.csv) | Presença de registros por mês, antes do filtro por ALAGAMENTO |
| [manifesto_fontes.json](manifesto_fontes.json) | SHA-256, esquema, CRS, tamanho e origem dos 15 GPKGs |
| [reparos_malha.csv](reparos_malha.csv) | Polígonos inválidos, motivo e área antes/depois do reparo |
| [busca_cv.csv](busca_cv.csv) | Todas as combinações, folds válidos, média, desvio e classificação |
| [metricas_folds.csv](metricas_folds.csv) | Métricas e motivos de N/A nas 54 avaliações |
| [divisao_distritos.csv](divisao_distritos.csv) e [ids_folds.csv](ids_folds.csv) | IDs do treino/teste e da validação exclusivamente no treino |
| [metricas_finais.csv](metricas_finais.csv) e [JSON](metricas_finais.json) | Métricas finais e configuração escolhida |
| [distritos_grupos.csv](distritos_grupos.csv) | Distrito, conjunto, grupo e atributos originais |
| [perfis_grupos_treino.csv](perfis_grupos_treino.csv) | Tamanhos e médias dos perfis somente no treino |
| [Balanço da limpeza](../dados/processados/balanco_limpeza.json) | Entradas, exclusões e registros finais |
| [Modelo e versões](../modelos/metadados.json) | Pipeline avaliado, ajustado somente no treino |

As verificações do repositório ficam em [verificacao_entrega.json](verificacao_entrega.json) e [verificacao_colab.json](verificacao_colab.json). Elas são geradas após a execução dos notebooks, sem alterar o treinamento.
"""
    (OUT/'README.md').write_text(gallery,encoding='utf-8')
    return report
