# Dados — proveniência, auditoria e reprodução

7032 registros brutos de ALAGAMENTO em 2013–2025; 110 duplicatas removidas; 5 sem associação distrital unívoca; **6917 registros na análise principal**, em 96 distritos.

Arquivos originais preservados em brutos/ e distritos/. Os 14 GPKGs anuais e a malha são inventariados com SHA-256, tamanhos, camada, CRS e esquema em [manifesto_fontes.json](../resultados/manifesto_fontes.json). Usaram-se as cópias fornecidas, sem downloads de dados adicionais. Data e endereço direto do download original desconhecidos; não inferidos a partir de nomes ou datas de modificação.

Origem: [GeoSampa — ocorrências](https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/432c06b1-03a1-4b1f-9210-423e1b58e869); [GeoSampa — distrito](https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/51f75eab-6d90-451e-9f80-c21c1ac72630); [portal de aquisição manual](https://novogeosampa.prefeitura.sp.gov.br/). Consultas aos catálogos: 12/11/2026. Para nova aquisição, abrir a camada e baixar os históricos anuais 2013–2025 e Distrito em GPKG, manter os nomes e conferir hashes. O portal pode fornecer versões diferentes; nesse caso, reexecutar e revisar a auditoria. Os arquivos fornecidos têm menos de 3 MB cada. Os catálogos indicam acesso sem restrições e uso sob licença genérica sem nome específico; confirmar termos antes de redistribuição externa. Nenhuma coluna de solicitante ou relato livre é exportada.

## Esquema efetivamente observado

- 2013–2025: id (FID local), geom (POINT), data (DATE), ocorrencia (TEXT), subprefeit (subprefeitura, não distrito), name (identificador textual, pode faltar ou repetir).
- 2026: primaryindex, geom, data, ocorrencia, subpreit, name. Auditado, excluído da análise.
- Nenhum GPKG anual tem dt_ocorrencia, dc_tipo_ocorrencia, ge_ponto, nm_distrito ou cd_identificador. A tabela prevista na referência docs/fontes/geosampa.md não descreve estas exportações.
- Malha: distrito_municipal_v2, código cd_distrito_municipal, nome nm_distrito_municipal, geometria ge_poligono, 96 distritos. Revisão catalogada em 27/10/2026. Todos os arquivos em EPSG:31983 (metros); não são latitude/longitude.

Data é interpretada como data registrada na exportação de ocorrências, sem comprovação documental de equivalência à abertura, evento ou encerramento. Não há outra data de ocorrência nos arquivos. Datas e tipos completos por arquivo estão em auditoria_arquivos.csv e tipos_por_arquivo.csv. Não há datas inválidas nem anos divergentes: não são snapshots cumulativos de vários anos. Todos os 156 meses de 2013–2025 têm registros de algum tipo; meses sem ALAGAMENTO são zeros observados desse tipo, sem garantia de completude.

## Regras executadas

Filtrar pelo ano da data, entre 2013 e 2025, e tipo normalizado exatamente ALAGAMENTO; não juntar INUNDACAO. Deduplicar somente quando o identificador não vazio e todos os atributos substantivos coincidem dentro do mesmo ano, incluindo geometria. IDs não são globalmente únicos; coincidência de local/data com IDs distintos é preservada, assim como IDs vazios. Não é possível identificar notificações diferentes do mesmo evento físico sem informação adicional.

São Miguel e Lajeado têm geometrias inválidas. make_valid e extração das partes poligonais foram aplicados em memória, com razões e áreas em reparos_malha.csv. Associação por intersects, em CRS comum: um único candidato é aceito; múltiplos candidatos ou nenhum ficam fora da agregação. Sem snapping nem atribuição ao vizinho mais próximo. Distância à malha é exportada para revisão dos não associados. Uma única versão atual da malha aplicada ao passado introduz limitação histórica.

Balanço: {"carregados": 68946, "excluidos_fora_2013_2025": 2579, "outros_tipos_no_periodo": 59335, "alagamentos_brutos": 7032, "duplicatas_removidas": 110, "apos_deduplicacao": 6922, "sem_distrito": 5, "restantes": 6917, "distritos_com_registros": 96, "identificadores_vazios_preservados": 238, "associacao": {"cruzamento_espacial": 6917, "fora_da_malha": 5}}

Processados: alagamentos_2013_2025.csv contém apenas registros atribuídos; alagamentos_sem_distrito.csv lista exceções; duplicatas_removidas.csv permite rastrear remoções. Chave_registro é arquivo:FID. Contagens distrito/ano/mês usam grade completa 96×13×12; zeros representam ausência de registros associados. atributos_distritos.csv preserva todos os distritos e indica elegibilidade.

A unidade é o distrito administrativo. O split 80/20 usa IDs ordenados e seed 42. O teste contém outros distritos no mesmo período; não mede previsão temporal. A grade tem 18 combinações de exatamente três hiperparâmetros: número de grupos [2,3,4], reinicializações [10,30] e variância retida pelo PCA [0,80;0,90;0,95]. Mais reinicializações buscam mínimos melhores da inércia. KFold de três partes, embaralhado com seed 42, usa exclusivamente o treino. Cada fold ajusta remoção de constantes, StandardScaler, PCA full e KMeans no subtreino. A validação recebe predict, sem novo ajuste. Silhouette é calculada antes do PCA, no espaço padronizado pelo subtreino, comparável entre configurações. Só candidatos com três folds válidos concorrem; desempates: menor desvio, menor k e ordem determinística. O teste é consultado uma vez após a escolha; o pipeline salvo permanece ajustado somente no treino.

Os atributos são log1p da média anual e da densidade anual por km², fração dos 13 anos com registro, CV anual (desvio populacional/média) e 12 proporções mensais. Área vem da geometria em EPSG:31983. As proporções somam 1 e recebem padronização individual: juntas podem ter peso maior que um atributo de volume. A dependência entre volume e densidade também influencia o resultado. Essas escolhas foram fixadas antes da busca; não houve seleção usando o teste. Distritos sem registros têm sazonalidade e CV indefinidos e ficam fora do modelo, sem imputação de zeros. Identificadores, coordenadas e nomes não entram no treinamento.


**Google Colab (arquivo único):** abra `ml/agua_na_rua_colab.ipynb` no Colab e selecione **Ambiente de execução → Executar tudo**. Essa edição contém os GPKGs completos e o código de apoio, prepara as bibliotecas automaticamente e oferece os resultados para download no final. Não é necessário enviar outros arquivos nem alterar caminhos. A primeira preparação pode precisar de internet para instalar bibliotecas. As versões da nova execução ficam registradas nos metadados do modelo.

**Execução local:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ml/requirements.txt
.\.venv\Scripts\python.exe ml/apoio/executar_notebook.py
```

O executor usa o Python do próprio ambiente em kernel limpo, sem instalar kernels globais. Alternativa na interface: abrir `ml/apoio/agua_na_rua_ml.ipynb`, selecionar esse ambiente Python e executar todas as células. Para nbconvert, o executor fornece um kernelspec temporário; não depende de um kernel global com nome específico.


Todas as saídas são regeneradas pelo notebook. requirements.txt fixa dependências diretas verificadas; apoio/requirements-lock.txt captura também dependências transitivas. Não há dados simulados no estudo.
