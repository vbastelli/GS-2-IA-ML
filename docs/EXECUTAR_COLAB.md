# Executar no Colab — guia do professor

O arquivo para avaliação é **[agua_na_rua_colab.ipynb](../ml/agua_na_rua_colab.ipynb)**.

1. No GitHub, [baixe o notebook](../ml/agua_na_rua_colab.ipynb?raw=1). Se o navegador exibir texto, use o botão **Download raw file** na página do arquivo.
2. Abra [Google Colab](https://colab.research.google.com/), escolha **Arquivo → Fazer upload de notebook** e selecione o `.ipynb` baixado.
3. Selecione **Ambiente de execução → Executar tudo**. Caso o Colab peça confirmação para executar um notebook importado, confirme após conferir sua origem.

**É só esse arquivo.** Não precisa enviar ZIP, anexar GPKGs, montar Google Drive, informar repositório, configurar caminhos ou copiar comandos. O ambiente padrão com CPU é suficiente; GPU não é utilizada pelo estudo.

## O que acontece ao executar

- A primeira célula prepara as bibliotecas necessárias; pode usar internet para instalar as que estiverem ausentes.
- A segunda extrai os **15 GPKGs completos** embutidos e confere o SHA-256 de cada arquivo: 14 anuais (2013–2026) e uma malha distrital.
- As células seguintes auditam a base, selecionam ALAGAMENTO de 2013–2025, associam os distritos, agregam atributos e executam treino, CV e teste. O arquivo de 2026 entra apenas na auditoria.
- As tabelas, os sete gráficos e a conclusão aparecem no próprio notebook. Nenhum modelo pronto é utilizado para substituir o treinamento.
- Ao final, é oferecido o download de `agua-na-rua-resultados.zip`, com os documentos, o modelo e os resultados da nova execução.

Para guardar também o notebook com as novas saídas, use **Arquivo → Fazer download → Fazer download de .ipynb**. Os arquivos da sessão são temporários: guarde as saídas antes de encerrar o ambiente. Essas operações constam da [documentação do Colab](https://research.google.com/colaboratory/faq.html).

## Conferir sem executar

O [notebook de leitura com saídas](../ml/apoio/agua_na_rua_ml.ipynb) é menor e mais fácil de ler no GitHub. O [índice de resultados](../ml/resultados/README.md) mostra os gráficos e aponta para as tabelas. O código comum às duas edições está em [estudo.py](../ml/estudo.py).

## Reprodução e limites da verificação

A equipe forneceu a edição executada no Colab. A revisão realizada em 18/11/2026 confirmou as 12 células de código executadas, sete gráficos e ausência de saídas de erro. As saídas registram Python 3.13.18, e as métricas visíveis e a configuração escolhida conferem com a referência local. O notebook conserva os resultados dessa execução. Os 15 GPKGs completos do pacote embutido tiveram seus SHA-256 conferidos com os originais do repositório. [Verificação da execução](../ml/resultados/verificacao_colab.json).

O pacote embutido conserva o código e os documentos do momento em que o notebook foi preparado. Os documentos externos do repositório também registram a conferência posterior da execução fornecida pela equipe.

O ambiente do Colab pode ter versões diferentes das usadas no Windows; as versões de cada nova execução ficam registradas no modelo e no ZIP. Os resultados de referência estão em [metricas_finais.json](../ml/resultados/metricas_finais.json). As dependências locais fixadas em [requirements.txt](../ml/requirements.txt) se referem ao Python 3.14.5 do ambiente original; o notebook de Colab prepara automaticamente dependências compatíveis com seu ambiente.
