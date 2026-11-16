# Relatório de IA & Machine Learning — Água na Rua

Síntese de aproximadamente duas páginas (Markdown não fixa paginação). Detalhes e saídas no [notebook](ml/agua_na_rua_ml.ipynb).

## Problema, dados e preparação

Pergunta: quais distritos de São Paulo apresentam perfis semelhantes de frequência, recorrência e sazonalidade dos registros públicos de alagamento? O aplicativo tem recorte inicial no Jardim Peri; este experimento independente analisa a cidade em resolução distrital.

7032 registros brutos de ALAGAMENTO em 2013–2025; 110 duplicatas removidas; 5 sem associação distrital unívoca; **6917 registros na análise principal**, em 96 distritos.

Após a limpeza, o maior volume anual é 2045 em 2016; janeiro–março concentram 69.8% dos registros. Isso descreve esta base de notificações, sem demonstrar tendência física de alagamentos ou efeito de intervenções.

Foram auditados os 14 arquivos anuais fornecidos: 2013–2025 são independentes pelas datas observadas; 2026 cobre janeiro–setembro e foi excluído. Os quatro tipos encontrados são ALAGAMENTO, INUNDACAO, DESLIZAMENTO e QUEDA DE ARVORE. Apenas ALAGAMENTO entra na análise. As datas de todos os registros são válidas e correspondem ao ano do arquivo. Removeram-se repetições exatas com identificador conhecido, data, tipo, geometria e demais atributos iguais, ignorando o FID; registros com ID vazio foram preservados. A associação espacial usa interseção com 96 distritos, sem duplicar pontos de fronteira.

Fontes: [ocorrências GeoSampa](https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/432c06b1-03a1-4b1f-9210-423e1b58e869) e [distritos GeoSampa](https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/51f75eab-6d90-451e-9f80-c21c1ac72630), catálogos consultados em 12/11/2026. As cópias locais têm SHA-256 no manifesto. Data e URL direta dos downloads originais não foram fornecidas. Os catálogos registram acesso sem restrições, mas o campo genérico de licença não identifica uma licença específica de redistribuição.

## Modelo e avaliação

KMeans + PCA é permitido pelo edital e explora perfis sem rótulo verdadeiro de risco. PCA reduz correlações; KMeans resume perfis por centroides, com sensibilidade à escala e a outliers.

A unidade é o distrito administrativo. O split 80/20 usa IDs ordenados e seed 42. O teste contém outros distritos no mesmo período; não mede previsão temporal. A grade tem 18 combinações de exatamente três hiperparâmetros: número de grupos [2,3,4], reinicializações [10,30] e variância retida pelo PCA [0,80;0,90;0,95]. Mais reinicializações buscam mínimos melhores da inércia. KFold de três partes, embaralhado com seed 42, usa exclusivamente o treino. Cada fold ajusta remoção de constantes, StandardScaler, PCA full e KMeans no subtreino. A validação recebe predict, sem novo ajuste. Silhouette é calculada antes do PCA, no espaço padronizado pelo subtreino, comparável entre configurações. Só candidatos com três folds válidos concorrem; desempates: menor desvio, menor k e ordem determinística. O teste é consultado uma vez após a escolha; o pipeline salvo permanece ajustado somente no treino.

Os atributos são log1p da média anual e da densidade anual por km², fração dos 13 anos com registro, CV anual (desvio populacional/média) e 12 proporções mensais. Área vem da geometria em EPSG:31983. As proporções somam 1 e recebem padronização individual: juntas podem ter peso maior que um atributo de volume. A dependência entre volume e densidade também influencia o resultado. Essas escolhas foram fixadas antes da busca; não houve seleção usando o teste. Distritos sem registros têm sazonalidade e CV indefinidos e ficam fora do modelo, sem imputação de zeros. Identificadores, coordenadas e nomes não entram no treinamento.


Melhor configuração: `n_clusters=2`, `n_init=10`, `pca.n_components=0.9`. Silhouette de validação: **0.1106 ± 0.0464** (3 folds). Dos 18 candidatos, 16 tiveram três folds válidos; candidatos [3, 6] ficaram fora da seleção por terem um fold com somente um grupo previsto (Silhouette indefinida, registrada como N/A).

| Conjunto | n | Grupos | Silhouette | Davies_Bouldin |
| --- | --- | --- | --- | --- |
| treino | 76 | 2 | 0.1442 | 2.5393 |
| teste | 20 | 2 | 0.1642 | 2.0780 |

O PCA reteve 11 componentes, explicando 92.88% da variância do treino. Os grupos são identificadores neutros, sem ordem de perigo. Perfis médios somente do treino:

| grupo | n | media_anual | densidade_anual_km2 | fracao_anos_com_registro | cv_anual |
| --- | --- | --- | --- | --- | --- |
| 0 | 25 | 3.286 | 0.657 | 0.572 | 1.359 |
| 1 | 51 | 6.392 | 0.699 | 0.816 | 1.02 |

## Conclusões e limites

As Silhouettes observadas (treino 0.1442, validação 0.1106 e teste 0.1642) indicam separação fraca: os perfis se sobrepõem e não sustentam uma tipologia forte. O teste ligeiramente superior ao treino não comprova generalização espacial nem ausência de overfitting.

A presença de registros de todos os tipos nos 156 meses sustenta a cobertura observada, mas não comprova captura completa dos alagamentos. Zero significa zero registros na base consultada; não ausência de alagamentos. Notificação, mudanças de sistema, outliers e subnotificação podem dominar os grupos. A amostra é pequena e distritos vizinhos têm dependência espacial. Proximidade entre métricas de treino e teste não demonstra ausência de overfitting; a busca sobre uma amostra pequena também pode superestimar a validação. Grupos pequenos e dispersão dentro dos grupos devem ser considerados. Silhouette maior indica separação mais clara; Davies–Bouldin menor indica maior compactação relativa, sem medir acurácia nem probabilidade de enchente.

A malha única de outubro/2026 foi aplicada retrospectivamente e dois polígonos foram reparados em memória. Pontos fora da malha ou ambíguos não foram deslocados para o distrito mais próximo. Os campos reais são data/ocorrencia/geom; não há nm_distrito. O significado temporal adotado é a data armazenada na exportação de ocorrências, sem documentação que permita distinguir abertura, evento ou encerramento. Os identificadores name não são globalmente únicos, e há ausências em 2025.

O estudo ajuda a investigar áreas para acompanhamento; não identifica passagem segura nem prevê o próximo alagamento. Faltam coordenadas dos pontos candidatos e validação territorial para relacionar a seleção local aos perfis. A escolha dos três pontos exige observação e conversa com moradores. O indicador de tempo de consulta da Ficha não foi medido. ODS 11.5 e 13.1 são relacionados à contribuição informacional e preparação comunitária, sem evidência de redução de danos ou vítimas.


A [Prefeitura, em notícia de 04/05/2017](https://prefeitura.sp.gov.br/web/casa_verde/w/noticias/71913), situa o Jardim Peri em Vila Nova Cachoeirinha; o [quadro oficial de correspondência OD2007](https://drive.prefeitura.sp.gov.br/cidade/secretarias/upload/urbanismo/infocidade/htmls/12_correspondencia_zonas_od_e_distritos_mun_2007_258.html) relaciona a zona Jardim Peri ao distrito Cachoeirinha. Fontes consultadas em 12/11/2026, usadas como contexto territorial, sem substituir a localização dos pontos candidatos. Na malha fornecida, Cachoeirinha tem 33 registros associados no período e recebeu grupo 0 (teste). Esse agregado distrital não descreve uma rua específica.


Gráficos, métricas por fold, IDs, atribuições e modelo avaliado estão em ml/resultados/ e ml/modelos/. A equipe precisa revisar o conteúdo, gravar o vídeo e preencher os links externos.
