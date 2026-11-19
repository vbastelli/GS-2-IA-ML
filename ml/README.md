# Estudo de Machine Learning — Água na Rua

**[Abrir no Colab](https://colab.research.google.com/github/vbastelli/GS-2-IA-ML/blob/main/ml/agua_na_rua_colab.ipynb)** · **[Baixar notebook de arquivo único](agua_na_rua_colab.ipynb?raw=1)** · [Guia de avaliação](../docs/GUIA_AVALIACAO.md)

| Arquivo ou pasta | Finalidade |
| --- | --- |
| [agua_na_rua_colab.ipynb](agua_na_rua_colab.ipynb) | Notebook principal para avaliação; contém os dados completos, prepara dependências e executa no Colab |
| [estudo.py](estudo.py) | Funções de auditoria, limpeza, associação espacial, atributos, treinamento, gráficos e geração dos documentos |
| [dados/](dados/README.md) | Originais, processados, proveniência e regras de qualidade |
| [resultados/](resultados/README.md) | Galeria de sete figuras e índice das tabelas e verificações |
| [modelos/](modelos/) | Pipeline avaliado salvo com joblib e metadados de versões; ajuste somente no treino |
| [requirements.txt](requirements.txt) | Versões diretas verificadas no Python 3.14.5 local |
| [apoio/](apoio/) | Notebook de leitura, ferramentas de manutenção e versões completas do ambiente |

Para avaliar, abra o notebook principal no Colab e escolha **Executar tudo**. Para ler a análise no GitHub, use a [versão menor com saídas salvas](apoio/agua_na_rua_ml.ipynb).

A pasta `apoio/` reúne os scripts de [execução local](apoio/executar_notebook.py), [preparação do Colab](apoio/preparar_colab.py), [verificação](apoio/verificar_entrega.py) e o [snapshot das dependências](apoio/requirements-lock.txt).
