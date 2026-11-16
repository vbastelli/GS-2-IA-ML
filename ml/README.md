# Estudo de Machine Learning — Água na Rua

**[Abrir no Colab](https://colab.research.google.com/github/vbastelli/GS-2-IA-ML/blob/main/ml/agua_na_rua_colab.ipynb)** · **[Baixar notebook de arquivo único](agua_na_rua_colab.ipynb?raw=1)** · [Guia de avaliação](../docs/GUIA_AVALIACAO.md)

| Arquivo ou pasta | Finalidade |
| --- | --- |
| [agua_na_rua_colab.ipynb](agua_na_rua_colab.ipynb) | Edição para importar e executar no Colab sem anexos; contém todos os dados e prepara dependências |
| [agua_na_rua_ml.ipynb](agua_na_rua_ml.ipynb) | Versão menor para ler no GitHub ou executar localmente, com tabelas e gráficos salvos |
| [estudo.py](estudo.py) | Funções de auditoria, limpeza, associação espacial, atributos, treinamento, gráficos e geração dos documentos |
| [dados/](dados/README.md) | Originais, processados, proveniência e regras de qualidade |
| [resultados/](resultados/README.md) | Galeria de sete figuras e índice das tabelas e verificações |
| [modelos/](modelos/) | Pipeline avaliado salvo com joblib e metadados de versões; ajuste somente no treino |
| [requirements.txt](requirements.txt) | Versões diretas verificadas no Python 3.14.5 local |
| [requirements-lock.txt](requirements-lock.txt) | Snapshot do ambiente local completo |
| [executar_notebook.py](executar_notebook.py) | Executor local em kernel limpo; `--colab` valida a edição de arquivo único localmente |
| [verificar_entrega.py](verificar_entrega.py) | Integridade das saídas, hashes, IDs e coerência de métricas, sem treinar novamente |
| [preparar_colab.py](preparar_colab.py) | Gerador da edição com dados e código embutidos; usar após mudanças no projeto |

Para avaliar, basta abrir o notebook no Colab e escolher **Executar tudo**. Os scripts são auxiliares de manutenção; o professor não precisa executá-los manualmente. Os links externos estarão disponíveis após publicar a branch `main` no repositório da equipe.
