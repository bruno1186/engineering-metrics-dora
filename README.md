# engineering-metrics-dora

![CI](https://github.com/bruno1186/engineering-metrics-dora/actions/workflows/ci.yml/badge.svg)

Calculadora de metricas DORA (DevOps Research and Assessment) em Python: Deployment Frequency, Lead Time for Changes, Change Failure Rate e MTTR, com classificacao automatica em Elite / High / Medium / Low.

> Caso de uso de referencia: instrumentar a esteira de entrega de qualquer time de engenharia (fintech, healthtech, banco, varejo ou mobilitech) e transformar dados brutos de deploy/incidente em um relatorio que a lideranca tecnica usa para decisao.

## Por que isso importa para lideranca tecnica

As quatro metricas DORA sao o padrao de mercado para medir performance de entrega de software sem depender de proxies fracos como "linhas de codigo" ou "horas trabalhadas". Este repositorio fecha o ciclo de dados ate a decisao: entrada em JSON (exportavel de qualquer pipeline de CI/CD ou sistema de incidentes) -> metricas -> classificacao -> relatorio textual pronto para 1:1 com stakeholders.

## Metricas calculadas

| Metrica | O que mede | Como e calculada aqui |
| --- | --- | --- |
| Deployment Frequency | Com que frequencia o time entrega em producao | Numero de deploys dividido pelo periodo (dias) |
| Lead Time for Changes | Tempo entre commit e producao | Mediana de `deployed_at - committed_at` |
| Change Failure Rate | % de deploys que causam incidente | Deploys com `caused_incident=true` / total |
| MTTR | Tempo medio de recuperacao de incidente | Mediana de `resolved_at - opened_at` |

Cada metrica recebe uma classificacao (Elite/High/Medium/Low) com faixas inspiradas nos benchmarks do relatorio State of DevOps (DORA). O nivel geral do time é o pior nivel entre as quatro métricas — propositalmente conservador.

## Estrutura

```
src/dora/
  models.py      # Deployment e Incident (entidades de dominio)
  metrics.py     # calculo das 4 metricas + classificacao
  report.py      # relatorio textual + nivel geral
  cli.py         # CLI (dora-report / python -m dora.cli)
data/sample_events.json  # dataset de exemplo (12 deploys, 2 incidentes)
tests/test_metrics.py    # testes unitarios e parametrizados
```

## Como rodar

```bash
pip install -e .
pip install pytest

pytest

python -m dora.cli data/sample_events.json --period-days 30
```

Saida esperada (com o dataset de exemplo):

```
Periodo analisado: 30 dias
Deployment Frequency: 0.40/dia -> High
Lead Time for Changes (mediana): 3.5h -> Elite
Change Failure Rate: 16.7% -> High
MTTR (mediana): 3.3h -> High
Classificacao geral (pior indicador): High
```

## Integrando com dados reais

O formato de entrada é um JSON simples (`deployments` + `incidents`) que pode ser gerado a partir da API do GitHub Actions, GitLab CI, Jenkins ou do seu sistema de incidentes (PagerDuty, Opsgenie). Basta um job agendado que exporta os eventos do periodo para este formato e roda `dora-report` como parte do pipeline de observabilidade de engenharia.

## Stack

Python 3.10+ · dataclasses · pytest (testes parametrizados) · GitHub Actions (matrix 3.10/3.11/3.12)
