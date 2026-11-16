# Prompt para o Codex — Água na Rua | IA & Machine Learning

Cole o texto abaixo no Codex aberto no repositório da disciplina. Antes, adicione os materiais indicados na lista de preparação ao final deste arquivo.

---

Você está trabalhando no repositório da entrega de Inteligência Artificial & Machine Learning da Global Solution CitizenTech da FIAP, 3º ano de Engenharia de Software, segundo semestre de 2026.

Implemente a entrega completa e reproduzível da disciplina. Crie os arquivos, execute a análise com dados reais, verifique os resultados e documente as conclusões. Não se limite a um plano ou a um notebook vazio. Use português claro, código explicável por estudantes e dependências estritamente necessárias.

## 1. Leia as referências e preserve o projeto

Leia primeiro as instruções AGENTS.md existentes, o conteúdo atual do repositório, `docs/edital-citizentech.pdf` e `docs/agua-na-rua.md`. No edital, concentre-se nas páginas 31–33 e nas regras gerais pertinentes. Leia também eventuais instruções complementares do professor em `docs/`.

A solução é **Água na Rua**, em São Paulo, com recorte cidadão inicial no Jardim Peri. O protótipo organiza observações localizadas e datadas sobre água acumulada nas ruas. O ML é um estudo independente do aplicativo, destinado a explorar o histórico de ocorrências registradas e apoiar a investigação de áreas para monitoramento.

Preserve integralmente a Ficha da CitizenTech fornecida, no começo do README. Preencha o link do repositório somente se for possível identificá-lo. Não altere silenciosamente o território, o cidadão ou as promessas da ficha. Use os nomes, RMs e a turma fornecidos em `docs/equipe.md`; não invente informações ausentes.

Não implemente aplicativo, API, sensores, dashboard web ou infraestrutura das outras disciplinas. Preserve arquivos existentes e evite sobrescrever trabalhos da equipe sem necessidade.

## 2. Exigências acadêmicas

Atenda e documente cada item:

- Dados reais e públicos relacionados à cidade; fonte, URL e período documentados. Dados simulados não são aceitos no estudo.
- Modelo permitido: utilize **KMeans + PCA**, conforme a proposta da equipe, e justifique a escolha.
- Limpeza, preparação e divisão explícita entre treino e teste.
- Pelo menos **10 combinações de 3 hiperparâmetros**, com validação cruzada exclusivamente no treino.
- Métricas apropriadas para agrupamento, com treino e teste lado a lado, gráficos e discussão de overfitting e limitações.
- Pasta `ml/` contendo notebook executado, `dados/README.md` e `requirements.txt`.
- `RELATORIO_ML.md`: adote aproximadamente **duas páginas**, pois uma página do edital indica 2–4 e outra especifica duas. Escreva uma síntese curta; o detalhamento ficará no notebook. Markdown não possui paginação fixa.
- Vídeo de até **5 minutos**, no YouTube como não listado. Prepare roteiro e campo para o link; a gravação e a publicação serão realizadas pela equipe.
- Registro dos prompts em `prompts.md`.
- Entrega dos links do GitHub e do vídeo no Teams até **19/11/2026, às 23h55, horário de São Paulo**, por um integrante.

Rubrica: problema e dados reais (2,0); escolha justificada do modelo (1,0); preparação e treino/teste (2,0); diferentes parâmetros (2,0); resultados em treino/teste (2,0); conclusão para o cidadão (1,0).

## 3. Pergunta de ML e unidade de análise

Use esta pergunta inicial:

**“Quais distritos de São Paulo apresentam perfis semelhantes de frequência, recorrência e sazonalidade das ocorrências públicas registradas de alagamento no período analisado?”**

Use preferencialmente **uma linha por distrito**, com atributos históricos agregados. Analise a cidade para obter unidades suficientes e discuta o território do Jardim Peri apenas na resolução que os dados realmente permitirem. Não treine usando somente os três pontos futuros do aplicativo.

Não confunda bairro e distrito administrativo. Verifique a localização do Jardim Peri com fonte oficial e/ou coordenadas dos pontos fornecidos; não atribua um distrito apenas pelo nome do bairro. Um perfil distrital não comprova a situação de uma rua específica.

Isso é aprendizado não supervisionado: não existe alvo de classificação nem rótulo verdadeiro de risco. Não crie classes artificiais “baixo/médio/alto risco” para calcular acurácia. Os números dos clusters não possuem ordem de perigo. Não prometa prever o próximo alagamento, estimar probabilidade de enchente ou informar passagem segura.

## 4. Dados e rastreabilidade

Fonte principal pretendida: GeoSampa — Alagamento (dados de Ocorrências), Defesa Civil/SIGRC:
https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/432c06b1-03a1-4b1f-9210-423e1b58e869

Portal para consultar e baixar camadas:
https://novogeosampa.prefeitura.sp.gov.br/

O catálogo informa histórico desde 2013, mas a descrição da camada atual se refere a 2026. Não presuma que um download da camada atual contenha todo o histórico.

Recorte desejado: **2013–2025**, a ser confirmado nos arquivos. Não misture 2026 incompleto com anos completos na modelagem. Se o histórico entregue tiver cobertura diferente, registre o período efetivo e o impedimento; não declare anos inexistentes nem modifique a ficha silenciosamente.

Use primeiro os arquivos fornecidos em `ml/dados/brutos/`. Se faltar algo, tente obter da fonte oficial, quando houver acesso de rede. Não invente endpoints, nomes de colunas ou esquemas. Não substitua os dados por notícias, imagens de mapas, amostras sintéticas ou dados de outra cidade.

Se precisar de limites distritais para associação espacial, utilize a camada oficial de distritos:
https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/51f75eab-6d90-451e-9f80-c21c1ac72630

Inspecione os dados antes de programar a transformação. Verifique:

- Formato, arquivos auxiliares, encoding, separadores, identificadores e dicionário de dados.
- Qual campo representa a ocorrência, o registro da solicitação ou seu encerramento. Use a data apropriada e descreva sua semântica.
- Datas válidas e quantidade de registros por ano e mês; falhas de cobertura não devem virar zeros de ocorrência.
- Se os arquivos anuais são independentes ou snapshots cumulativos, para evitar contagem duplicada.
- Duplicatas exatas e repetições de solicitações sobre um mesmo evento. Documente a regra e não remova registros distintos apenas porque compartilham local e data.
- Geometrias, coordenadas e CRS. O catálogo menciona EPSG:31983; confirme o arquivo antes de transformar e não interprete coordenadas UTM como latitude/longitude.
- Campos ausentes, geometrias inválidas, pontos fora do município e ocorrências sem distrito.

Se houver distrito confiável no próprio dado, valide e use esse campo. Caso contrário, associe os pontos aos polígonos oficiais com operação espacial, tratando pontos na fronteira e associações ambíguas sem duplicar ocorrências. Registre a versão dos limites e a limitação de aplicar uma única malha ao histórico.

Produza um balanço de qualidade: registros carregados, duplicados removidos, descartados por motivo e restantes. Registre URL da página de origem e do download efetivamente utilizado, data de acesso real, período observado, arquivos, SHA-256, esquema e eventuais restrições de redistribuição. Não preencha metadados por suposição. Não versione nomes, contatos ou textos com dados pessoais de solicitantes.

Se faltar data com resolução mensal, localização utilizável ou volume suficiente, explique quais análises ficam inviáveis. Conclua o trabalho independente dessa falta e liste o arquivo/campo exato necessário. Não apresente a entrega como executada enquanto houver esse bloqueio.

## 5. Construção das variáveis

Crie agregações determinísticas por distrito usando somente os anos cuja cobertura tiver sido verificada. Documente as fórmulas, denominadores e unidades. Variáveis candidatas:

- Média anual de registros no período observado.
- Proporção dos anos cobertos com ao menos um registro.
- Variabilidade entre as contagens anuais, por exemplo coeficiente de variação, com tratamento explícito de média zero.
- Distribuição proporcional dos registros pelos 12 meses do ano, como descrição de sazonalidade.
- Densidade média anual de registros por km², somente se houver área distrital confiável, calculada em CRS apropriado.

Evite redundâncias óbvias, como incluir simultaneamente total e média anual em um período comum. Explique o peso conjunto das 12 proporções mensais e a possível influência do volume de notificações. Use `log1p` em contagens/densidades não negativas quando tecnicamente justificado, com regra fixa documentada.

Não use nome, código distrital, índice de linha, número do cluster ou texto livre como atributos numéricos. Preserve esses campos apenas para identificação. Não inclua coordenadas na clusterização principal: elas servem à associação territorial e visualização; o objetivo principal é agrupar perfis históricos.

Distinga explicitamente “zero registros na base consultada” de “não houve alagamento” e de “dado ausente”. Para distritos sem registros, sazonalidade é indefinida; não atribua automaticamente doze zeros como um perfil real. Registre e justifique os critérios de inclusão. Se excluir áreas sem informação suficiente, mostre quais foram excluídas e limite a população à qual as conclusões se aplicam.

Defina as fórmulas e os critérios metodológicos antes de avaliar o modelo. Qualquer transformação que aprenda estatísticas, seleção de atributos ou imputação deve ser ajustada apenas no treino e novamente dentro de cada fold.

## 6. Treino, validação e teste sem vazamento

Após as agregações, ordene as unidades por identificador estável e separe aproximadamente 80% dos distritos para treino e 20% para teste, com `random_state=42`. Salve a relação de IDs de cada conjunto. Um distrito deve aparecer em apenas um conjunto.

Explique que esse teste verifica a atribuição de perfis de outros distritos no mesmo período histórico; **não mede previsão de anos futuros**. Reconheça que distritos próximos podem ser dependentes espacialmente e que a amostra é pequena. Se houver várias linhas por unidade por alguma mudança necessária, substitua a divisão e a CV por estratégias que mantenham a mesma unidade sempre no mesmo conjunto.

Use Pipeline do scikit-learn com preparação necessária, StandardScaler, PCA e KMeans. Imputação, remoção de atributos constantes e outras etapas aprendidas, se necessárias, também pertencem ao pipeline. Ajuste cada pipeline somente nos dados de treino do respectivo fold.

Faça busca com **18 combinações de exatamente três hiperparâmetros**:

- `kmeans__n_clusters`: [2, 3, 4]
- `kmeans__n_init`: [10, 30]
- `pca__n_components`: [0.80, 0.90, 0.95]

Use PCA com `svd_solver="full"`, compatível com a escolha por proporção da variância. Fixe os demais parâmetros e `random_state=42`. Explique o significado dos três hiperparâmetros e por que diferentes reinicializações ajudam o KMeans.

Use KFold com três folds, embaralhamento e seed fixa, exclusivamente nos distritos do treino. Verifique antes se a amostra admite esse desenho. Se a grade for inviável, ajuste-a usando apenas informações do treino, preserve pelo menos dez combinações de três hiperparâmetros e justifique.

Implemente avaliação específica para agrupamento: em cada fold, ajuste no subtreino, obtenha rótulos da validação por `pipeline.predict(X_validacao)` e calcule Silhouette. Não use o `score` padrão do KMeans como se fosse Silhouette. Não use `fit_predict` na validação ou no teste.

Para comparar configurações com diferentes dimensões de PCA, calcule a Silhouette principal no **espaço de atributos padronizados anterior ao PCA**, usando a preparação ajustada no subtreino e os rótulos previstos pelo pipeline completo. Mantenha essa definição na avaliação final. Documente-a para evitar comparações entre espaços diferentes.

Silhouette exige entre dois e n_amostras−1 rótulos distintos no conjunto avaliado. Registre folds inválidos como não avaliáveis, com motivo; não invente Silhouette zero. Informe a quantidade de folds válidos e não deixe combinações incompletas vencerem silenciosamente. Se nenhuma combinação tiver avaliação válida suficiente, declare a limitação e não fabrique um vencedor.

Selecione pela maior Silhouette média de validação entre candidatos válidos; desempate por menor desvio-padrão e depois por menor k. Salve todas as combinações, parâmetros, métricas por fold, média, desvio-padrão, falhas e classificação. Não consulte o teste para selecionar parâmetros, sementes ou variáveis.

Depois de fixar a escolha, ajuste o pipeline no treino inteiro e avalie uma vez no teste reservado. Preserve esse modelo como o modelo avaliado; não o sobrescreva com outro ajustado em todos os dados.

## 7. Resultados, gráficos e interpretação

Apresente treino e teste lado a lado: tamanho da amostra, quantidade de clusters efetivamente ocupados, Silhouette e Davies–Bouldin quando matematicamente definidos. Explique que essas métricas descrevem separação/compactação dos grupos, e não acurácia de previsão de alagamentos. Se uma métrica for indefinida, apresente N/A e o motivo.

Discuta diferenças entre treino, validação e teste, instabilidade com poucos distritos, grupos pequenos ou dominados por outliers, dependência espacial e sensibilidade ao volume de notificações. Não declare ausência de overfitting apenas porque duas métricas ficaram próximas. Resultados fracos devem aparecer com clareza.

Gere, com títulos, legendas e unidades:

1. Cobertura e quantidade de registros por ano.
2. Distribuição mensal dos registros, com ressalvas de cobertura.
3. Comparação das configurações da busca em CV.
4. Comparação visual das métricas de treino e teste.
5. Visualização dos clusters nos componentes principais, informando a variância explicada. Se o PCA escolhido tiver apenas um componente, use uma visualização adequada ou uma projeção 2D separada, identificada como ilustrativa e ajustada somente no treino.
6. Perfis dos grupos em atributos interpretáveis, em unidades originais, com tamanhos dos grupos. Use o treino para atribuir descrições aos perfis.
7. Mapa dos distritos e grupos, caso as geometrias estejam disponíveis, com legenda neutra e áreas sem dados distinguidas.

Use paleta acessível para daltonismo, evitando depender de verde/vermelho. Identifique treino/teste quando pertinente e salve as figuras usadas na documentação. Um gráfico deve ser coerente com os valores das tabelas e os arquivos exportados.

Use o modelo treinado para atribuir grupos aos distritos elegíveis e exporte tabela com identificador, distrito, conjunto (treino/teste), grupo e atributos descritivos. Dê nomes descritivos apenas quando apoiados pelos resultados, como “maior volume de registros e concentração sazonal”; não renomeie os grupos como níveis validados de risco.

Explique como os padrões encontrados podem orientar a investigação de locais para acompanhamento. O histórico distrital é apenas um insumo: a escolha dos três pontos do aplicativo exige observação local e conversa com moradores. Não invente entrevistas, obras de drenagem, validação territorial, resultados de testes com usuários ou redução de danos. O indicador de tempo de consulta da ficha não é medido por este notebook e não deve ser confundido com Silhouette.

## 8. Arquivos da entrega

Mantenha esta organização, adaptando nomes apenas quando necessário para preservar o repositório:

- `README.md`: Ficha original no início, equipe, pergunta de ML, resumo, execução, principais resultados, limites e links.
- `RELATORIO_ML.md`: síntese de aproximadamente duas páginas, do problema à conclusão, baseada nos resultados executados.
- `prompts.md`: registre integralmente este prompt e os novos pedidos relevantes realmente recebidos; diferencie decisões tomadas pelo Codex de mensagens do usuário. Não invente conversas.
- `docs/edital-citizentech.pdf`, `docs/agua-na-rua.md` e `docs/equipe.md`: referências fornecidas, preservadas.
- `docs/ROTEIRO_VIDEO_ML.md`: roteiro de até cinco minutos, com tempos sugeridos, células/figuras a mostrar e resultados reais; campo para o link do vídeo.
- `ml/agua_na_rua_ml.ipynb`: notebook com explicações, código, tabelas e gráficos, salvo com as saídas de execução.
- `ml/requirements.txt`: dependências diretas e versões efetivamente usadas e verificadas.
- `ml/dados/README.md`: aquisição reproduzível, proveniência, período, esquema, cobertura, regras de limpeza, licenciamento e limitações.
- `ml/dados/brutos/`: dados oficiais fornecidos/baixados cuja publicação seja permitida, sem dados pessoais.
- `ml/dados/processados/`: base de atributos e balanço da limpeza, gerados por código.
- `ml/resultados/`: busca completa em CSV, métricas finais em JSON/CSV, IDs da divisão, atribuições dos distritos e figuras.
- `ml/modelos/`: pipeline avaliado salvo com joblib e metadados das versões.
- `.gitignore`: ambientes virtuais, caches e temporários, preservando as saídas necessárias para a avaliação.

Não é necessário criar framework, pacote complexo ou testes que apenas repitam o código. Extraia funções auxiliares se isso melhorar a clareza. Arquivos grandes devem ter procedimento de aquisição documentado, respeitando limites do GitHub. A entrega deve permitir obter a base completa; uma amostra não deve ser apresentada como se fosse o histórico integral.

O notebook deve conter: contexto e pergunta; fontes; auditoria; limpeza; agregação; divisão; justificativa do modelo; pipeline; busca/CV; escolha; avaliação final; visualizações; leitura para o cidadão; limitações e conclusão. Os caminhos devem funcionar conforme o comando de execução documentado, sem caminhos absolutos pessoais.

O relatório e o README devem usar métricas e contagens geradas pelo notebook, sem números preenchidos manualmente por estimativa. Relacione ODS 11.5 e 13.1 com a contribuição informacional, sem afirmar que o experimento comprova redução de danos ou vítimas.

## 9. Verificação e encerramento

Instale as dependências no ambiente apropriado e execute o notebook inteiro, do começo ao fim, em kernel limpo. Salve o notebook executado e verifique: ausência de células com erro, IDs únicos por distrito, interseção vazia de treino/teste, pelo menos dez configurações de três hiperparâmetros, CV só no treino e coerência entre métricas, gráficos e relatório. Use assertions úteis para essas propriedades.

Documente os comandos para criar ambiente virtual, instalar dependências e executar o notebook por interface Jupyter ou `nbconvert`. Verifique os comandos informados. Não diga que executou comandos ou gerou evidências se isso não ocorreu.

Deixe placeholders somente para informações externas ausentes, como RMs, URL do repositório ou link do vídeo. Não deixe células de modelagem vazias ou métricas fictícias com aparência de resultado final. Se houver bloqueio de dados ou de ambiente, entregue o que for verificável e destaque claramente a execução pendente e a informação exata necessária.

Ao terminar, apresente um resumo curto dos arquivos criados, dados e período efetivamente usados, número de distritos e de combinações avaliadas, melhor configuração quando houver, métricas reais e pendências externas. Não publique vídeo, faça push ou envie a tarefa no Teams.

---

## Preparação antes de colar o prompt

| O que reunir | Onde colocar | Observação |
| --- | --- | --- |
| PDF do edital anexado nesta conversa | `docs/edital-citizentech.pdf` | Preservar o documento completo. |
| Ficha Água na Rua anexada nesta conversa | `docs/agua-na-rua.md` | Manter a mesma ficha nos repositórios das disciplinas. |
| Nomes completos, RMs e turma | `docs/equipe.md` | Incluir também URL do repositório, se já disponível. |
| Histórico real de ocorrências de alagamento | `ml/dados/brutos/` | Preferencialmente 2013–2025; conferir datas e arquivos, sem presumir que a camada atual contém a série. |
| Dicionário e metadados das ocorrências | `docs/fontes/` | Salvar documento oficial ou texto com campos, significado das datas, CRS, links e data de acesso. |
| Limites oficiais dos distritos | `ml/dados/brutos/distritos/` | Necessários se o histórico não tiver distrito confiável; também permitem mapa e cálculo de área. |
| Orientações complementares do professor, se existirem | `docs/` | Incluir mensagens/rubrica específicas que complementem o PDF. |

No GeoSampa, pesquise “Alagamento (dados de Ocorrências)”, abra as informações da camada e as opções de download. Procure explicitamente os arquivos históricos. Prefira GeoPackage ou GeoJSON quando disponíveis; se usar Shapefile, guarde o ZIP completo com `.shp`, `.shx`, `.dbf`, `.prj` e outros auxiliares. O formato real disponível deve ser confirmado no portal.

O mínimo analítico é data da ocorrência/registro adequadamente identificada e distrito ou localização que permita associá-la a um distrito. Datas com mês são necessárias para a análise mensal. Registre a cobertura real; não é possível garantir antecipadamente que todos os anos desejados estarão utilizáveis.

Se o download exigir interação manual ou não disponibilizar a série como esperado, reúna os arquivos antes de pedir a execução completa ao Codex. Ele pode tentar baixar dados públicos com acesso de rede, mas o prompt não substitui o acesso ao conjunto real.

Para a contextualização local, é útil reunir endereços/coordenadas dos pontos candidatos, evidências públicas atuais e observações de moradores sem identificação pessoal. Isso apoia a escolha dos pontos; não substitui os dados usados no ML.

Não são necessários INMET, sensores reais, backend, dados de usuários ou rótulos de risco para o estudo proposto. Após a análise, a equipe ainda precisará revisar e compreender o trabalho, gravar o vídeo, publicar como não listado, inserir o link e enviar os dois links na tarefa.
