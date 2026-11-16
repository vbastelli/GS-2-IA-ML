# Fontes de dados — Água na Rua

## Ocorrências de alagamento

- **Fonte:** GeoSampa, Prefeitura de São Paulo.
- **Origem dos registros:** Defesa Civil Municipal, via SIGRC.
- **Metadados:** [Alagamento (dados de Ocorrências)](https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/432c06b1-03a1-4b1f-9210-423e1b58e869)
- **Formato:** GeoPackage (`.gpkg`).
- **Arquivos:** `SIRGAS_GPKG_riscoocorrencia_*.gpkg`.
- **Período confirmado da análise principal:** 2013–2025, verificado pelas datas dos registros.
- **Data do download original:** não informada; os arquivos foram fornecidos localmente.

### Esquema previsto inicialmente — não corresponde aos GPKGs fornecidos

**Para os campos efetivos, use a seção de conferência abaixo.** Esta tabela registra a expectativa inicial, não o esquema utilizado pelo código.

| Campo observado no GPKG de 2026 | Uso no projeto |
|---|---|
| `dt_ocorrencia` | Extrair o ano e o mês registrados. |
| `dc_tipo_ocorrencia` | Selecionar os registros do tipo `ALAGAMENTO`. |
| `ge_ponto` | Localizar a ocorrência e associá-la a um distrito. |
| `nm_distrito` | Conferir o distrito quando preenchido. |
| `cd_identificador` | Verificar possíveis registros duplicados. |

Os nomes e tipos foram conferidos nos 13 arquivos históricos e em 2026.
Todos usam EPSG:31983; o campo `nm_distrito` não existe nessas exportações.

## Limites dos distritos

- **Fonte:** [Camada Distrito — GeoSampa](https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/51f75eab-6d90-451e-9f80-c21c1ac72630)
- **Uso:** associar os pontos de alagamento aos distritos de São Paulo.

## Conferência dos arquivos fornecidos — 12/11/2026

A tabela acima era uma expectativa de esquema. **Estas exportações não possuem aqueles campos**, inclusive a de 2026. Os campos reais são `data`, `ocorrencia`, `geom`, `name` e `subprefeit` (2013–2025); em 2026, `subpreit` substitui `subprefeit`. Não há campo de distrito em nenhum anual. `name` é tratado como identificador da exportação, sem garantia de unicidade global.

Todos os GPKGs usam EPSG:31983. Os arquivos de 2013–2025 têm registros nos 12 meses e somente no ano indicado pelo nome; 2026 cobre janeiro–setembro e foi excluído da análise principal. Os quatro tipos observados são `ALAGAMENTO`, `INUNDACAO`, `DESLIZAMENTO` e `QUEDA DE ARVORE`; apenas o primeiro entra na modelagem. A semântica comprovável de `data` é a data armazenada na exportação de ocorrências; não há documentação adicional que permita separar momento do evento, abertura e encerramento.

Os distritos são atribuídos por cruzamento com `distrito_municipal_v2.gpkg`, camada de 96 distritos em EPSG:31983. A malha tem revisão de outubro/2026 e dois polígonos inválidos, reparados em memória. Pontos externos ou ambíguos permanecem sem distrito. O balanço executado, os esquemas e hashes estão em `ml/resultados/` e `ml/dados/processados/`.

Os catálogos oficiais foram consultados em 12/11/2026. Os dados foram fornecidos localmente; data de download e URL direta originais não informadas. Não substituir esses metadados por suposições.
