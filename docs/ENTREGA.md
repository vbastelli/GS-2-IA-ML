# Controle da entrega

## Arquivos prontos para avaliação

- [README com entrada para o professor](../README.md).
- [Guia de requisitos e evidências](GUIA_AVALIACAO.md).
- [Notebook de arquivo único para baixar e executar no Colab](../ml/agua_na_rua_colab.ipynb?raw=1).
- [Notebook principal executado](../ml/agua_na_rua_ml.ipynb), [relatório](../RELATORIO_ML.md), [resultados](../ml/resultados/README.md) e [roteiro](ROTEIRO_VIDEO_ML.md).
- Dados completos, código e modelo preservados no repositório.

## Informações e ações externas pendentes

| Item | Estado |
| --- | --- |
| URL do repositório | [vbastelli/GS-2-IA-ML](https://github.com/vbastelli/GS-2-IA-ML), fornecida pela equipe |
| Turma | 3ESPZ, informada pela equipe |
| Vídeo YouTube não listado, até cinco minutos | Gravação, publicação e link pendentes da equipe |
| Conferência da execução no Colab | Notebook executado fornecido pela equipe e revisado em 18/11/2026, com 12 células de código, sete gráficos e resultados coerentes |
| Envio dos links na tarefa do Teams | A realizar por um integrante até 19/11/2026, às 23h55 de São Paulo |

Nomes e RMs estão em [integrantes.txt](integrantes.txt). A turma e a URL foram fornecidas posteriormente pela equipe. A Ficha foi preservada, preenchendo apenas o campo previsto para o link do repositório.

Os campos de publicação ficam centralizados em [entrega.json](entrega.json). Quando os links e a turma estiverem disponíveis, preencha esse arquivo. A geração do README e do roteiro lê esses campos; para manter o notebook de Colab atualizado, gere-o novamente após alterar os arquivos de apoio.

## Publicar no GitHub

Suba as pastas `docs/` e `ml/`, os documentos da raiz e os arquivos `.gitignore` e `.gitattributes`, mantendo a estrutura. Não envie `.venv/`, caches ou o antigo ZIP local de transferência: esses arquivos estão ignorados pelo Git. O notebook de Colab já contém tudo que o professor precisa para executar a análise.

O conteúdo pode ser enviado pelo GitHub Desktop ou por **Add file → Upload files** em um repositório criado pela equipe. Todos os arquivos da entrega ficam abaixo do limite de 25 MiB por arquivo do envio pelo navegador; esse limite e as instruções estão na [documentação do GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository). O `.gitignore` é aplicado pelo Git, não pelo seletor de upload do navegador: na publicação manual, selecione apenas os arquivos da entrega.

Após publicar, abra o README no próprio GitHub, confirme que o professor tem acesso ao repositório e confira os atalhos de Colab e download do notebook. Se a prévia do notebook não carregar, use **Download raw file**; o notebook menor continua disponível para leitura. O professor não precisa clonar o repositório ou baixar seu ZIP completo para executar no Colab.
