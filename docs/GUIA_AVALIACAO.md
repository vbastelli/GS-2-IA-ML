# Guia de avaliação — IA & Machine Learning

**Comece pelo [notebook para Colab](EXECUTAR_COLAB.md)** ou leia o [relatório](../RELATORIO_ML.md). As referências acadêmicas são as páginas 31–33 do [edital original](<GS CitizenTech - 3ES Fev - FIAP 2026 - .pdf>). O [prompt da proposta](../prompt-codex-ml-agua-na-rua.md) é material complementar; a rubrica acadêmica vem do edital.

## Rubrica e evidências

| Critério do edital | Peso | O que foi entregue | Onde conferir |
| --- | --- | --- | --- |
| Problema e dados reais | 2,0 | Pergunta distrital, registros reais GeoSampa, fonte, período, esquema, hashes e auditoria de todos os anos | [Ficha original](agua-na-rua.md), [dados](../ml/dados/README.md), [auditoria por arquivo](../ml/resultados/auditoria_arquivos.csv), [manifesto](../ml/resultados/manifesto_fontes.json) |
| Escolha justificada do modelo | 1,0 | KMeans + PCA para agrupar perfis sem rótulo verdadeiro de risco; limites de escala e outliers | [Relatório](../RELATORIO_ML.md), seção “Divisão, pipeline e validação cruzada” dos notebooks e [código](../ml/estudo.py) |
| Preparação e divisão treino/teste | 2,0 | Limpeza, associação geográfica, uma linha por distrito, atributos explícitos; 76 distritos de treino e 20 de teste, seed 42 | [Balanço](../ml/dados/processados/balanco_limpeza.json), [atributos](../ml/dados/processados/atributos_distritos.csv), [IDs da divisão](../ml/resultados/divisao_distritos.csv) |
| Treino com diferentes parâmetros | 2,0 | 18 combinações de exatamente três hiperparâmetros; CV com três folds apenas no treino; 16 candidatos com os três folds válidos | [Busca completa](../ml/resultados/busca_cv.csv), [métricas dos 54 folds](../ml/resultados/metricas_folds.csv), [IDs dos folds](../ml/resultados/ids_folds.csv) |
| Resultados em treino e teste | 2,0 | Silhouette e Davies–Bouldin lado a lado, sete figuras, discussão de overfitting e separação fraca | [Métricas finais](../ml/resultados/metricas_finais.csv), [galeria de resultados](../ml/resultados/README.md), [modelo avaliado](../ml/modelos/) |
| Conclusão e leitura para o cidadão | 1,0 | Apoio à investigação de locais; limites territoriais, subnotificação, ODS 11.5 e 13.1; sem promessa de previsão ou passagem segura | Conclusão do [relatório](../RELATORIO_ML.md), perfis e mapa nos notebooks |

## Conferência dos entregáveis

| Exigência | Evidência ou estado |
| --- | --- |
| Ficha comum às disciplinas e equipe | Ficha integral no início do [README](../README.md), em bloco expansível; original em [agua-na-rua.md](agua-na-rua.md); nomes/RMs em [integrantes.txt](integrantes.txt) |
| Pasta `ml/` com notebook executado | [Versão legível executada](../ml/apoio/agua_na_rua_ml.ipynb) e [versão de arquivo único para Colab](../ml/agua_na_rua_colab.ipynb) |
| Dados públicos, não simulados | 15 GPKGs completos preservados; 2013–2025 na análise principal, 2026 auditado e excluído; nenhuma amostra sintética |
| `dados/README.md` e `requirements.txt` | [Proveniência e reprodução](../ml/dados/README.md), [dependências diretas](../ml/requirements.txt), [ambiente completo](../ml/apoio/requirements-lock.txt) |
| Relatório | [RELATORIO_ML.md](../RELATORIO_ML.md), síntese com extensão aproximada de duas páginas; detalhamento no notebook |
| Pelo menos 10 combinações de 3 hiperparâmetros | 18 candidatas, mantendo N/A quando um fold prevê apenas um grupo; candidatas incompletas não concorrem |
| Transformações sem vazamento | Remoção de constantes, StandardScaler e PCA ajustados no subtreino de cada fold; `predict` na validação e no teste; modelo salvo apenas no treino |
| Métricas apropriadas e gráficos | Silhouette e Davies–Bouldin no espaço padronizado anterior ao PCA; [sete figuras](../ml/resultados/README.md) |
| Registro de apoio da equipe | Mantido localmente pela equipe, fora do repositório público |
| Vídeo de até cinco minutos, não listado | [Vídeo no YouTube](https://www.youtube.com/watch?v=Oy50n6N8uW8) · [Roteiro com resultados reais](ROTEIRO_VIDEO_ML.md) |
| Links do GitHub e vídeo no Teams | Links disponíveis para envio por um integrante até 19/11/2026, 23h55 (São Paulo), conforme edital |

## Integridade e limitações

As verificações executadas estão em [verificacao_entrega.json](../ml/resultados/verificacao_entrega.json) e [verificacao_colab.json](../ml/resultados/verificacao_colab.json). O [verificador](../ml/apoio/verificar_entrega.py) confere execução sem erros, imagens, hashes, separação dos IDs, CV apenas no treino e coerência das contagens e métricas. Não treina novamente nem usa o teste para selecionar parâmetros.

O estudo tem separação fraca entre grupos; esse resultado é parte da entrega, não uma validação de classes de risco. A malha de 2026 foi aplicada retrospectivamente; há subnotificação e dependência espacial. Os cinco pontos sem associação unívoca estão [exportados para revisão](../ml/dados/processados/alagamentos_sem_distrito.csv). Não foram inventadas entrevistas, validação dos pontos locais, previsões ou redução de danos.

O [controle de entrega](ENTREGA.md) distingue o trabalho técnico concluído das informações e ações externas ainda pendentes.
