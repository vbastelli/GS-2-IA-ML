# Roteiro — vídeo de IA & ML (até 5 minutos)

Turma: 3ESPZ. Repositório: https://github.com/vbastelli/GS-2-IA-ML.

Vídeo no YouTube: https://www.youtube.com/watch?v=Oy50n6N8uW8

- 0:00–0:35 — Mostrar Ficha no README: cidadão, Jardim Peri, informação recente sobre água nas ruas; ML independente e distrital.
- 0:35–1:20 — Notebook, auditoria e limpeza: 7032 registros brutos de ALAGAMENTO em 2013–2025; 110 duplicatas removidas; 5 sem associação distrital unívoca; **6917 registros na análise principal**, em 96 distritos. Mostrar 01_registros_ano.png e 02_registros_mes.png; 2026 excluído; campos reais, duplicatas, dois polígonos reparados e exceções de associação.
- 1:20–2:10 — Notebook, atributos e divisão: uma linha por distrito, atributos históricos, log1p, treino/teste 80/20 com seed 42, escalonamento aprendido apenas no treino. PCA e KMeans não têm rótulo de risco.
- 2:10–3:00 — Notebook, busca: 18 combinações de três parâmetros, três folds apenas no treino, rótulos por predict e Silhouette no espaço anterior ao PCA. Mostrar 03_busca_cv.png. Melhor: `n_clusters=2`, `n_init=10`, `pca.n_components=0.9`. Silhouette de validação: **0.1106 ± 0.0464** (3 folds). Dos 18 candidatos, 16 tiveram três folds válidos; candidatos [3, 6] ficaram fora da seleção por terem um fold com somente um grupo previsto (Silhouette indefinida, registrada como N/A).
- 3:00–3:45 — Mostrar 04_metricas.png e a tabela abaixo. Explicar diferenças entre treino, validação e teste e a possibilidade de overfitting; não alegar precisão de previsão de enchentes.
- 3:45–4:25 — Mostrar 05_componentes.png, 06_perfis.png e 07_mapa.png. Ler os tamanhos e médias reais em perfis_grupos_treino.csv. Números dos grupos não representam níveis de perigo.
- 4:25–4:55 — Conclusão: padrões orientam investigação e observação local, mas não comprovam segurança de ruas. Dependência espacial, subnotificação, malha de 2026 e amostra pequena limitam conclusões. Pontos locais e indicador de tempo da Ficha ainda precisam de validação própria. ODS 11.5 e 13.1 como contribuição informacional.

| Conjunto | n | Grupos | Silhouette | Davies_Bouldin |
| --- | --- | --- | --- | --- |
| treino | 76 | 2 | 0.1442 | 2.5393 |
| teste | 20 | 2 | 0.1642 | 2.0780 |

Contexto local para a fala: A [Prefeitura, em notícia de 04/05/2017](https://prefeitura.sp.gov.br/web/casa_verde/w/noticias/71913), situa o Jardim Peri em Vila Nova Cachoeirinha; o [quadro oficial de correspondência OD2007](https://drive.prefeitura.sp.gov.br/cidade/secretarias/upload/urbanismo/infocidade/htmls/12_correspondencia_zonas_od_e_distritos_mun_2007_258.html) relaciona a zona Jardim Peri ao distrito Cachoeirinha. Fontes consultadas em 12/11/2026, usadas como contexto territorial, sem substituir a localização dos pontos candidatos. Na malha fornecida, Cachoeirinha tem 33 registros associados no período e recebeu grupo 0 (teste). Esse agregado distrital não descreve uma rua específica.

Antes de enviar: conferir duração ≤5 minutos, link não listado acessível, nomes/RMs e link do GitHub; um integrante envia os dois links na tarefa do Teams até 19/11/2026, 23h55 (São Paulo).
