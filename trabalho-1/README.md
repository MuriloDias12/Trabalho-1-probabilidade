# Trabalho I – Máquina Estatística
Probabilidade e Estatística I – IFES Campus Serra – 2026/2

> Simulador acadêmico - somente créditos fictícios

## Integrante
- Murilo Dias de Oliveira – 20221bsi0099

## Requisitos
- Python 3.10 ou superior (resultados gerados com Python 3.12.3)
- matplotlib (`pip install matplotlib`)

## Como executar
```bash
python simulador.py                    # mostra uma rodada e executa os 5 experimentos
python simulador.py --rodada           # mostra apenas uma rodada
python simulador.py --rodada --semente 7
python simulador.py --jogar            # modo interativo (Enter = rodar, q = sair)
python testes.py                       # 12 verificações automatizadas
```

## Onde estão os resultados
Todos os arquivos são gerados na pasta `resultados/`:

| Arquivo | Conteúdo |
|---|---|
| `ambiente.json` | versão do Python, gerador, sementes e parâmetros |
| `e1_rodadas_semente_2026.csv` | as 10.000 rodadas do E1 (reutilizadas no E2, E4 e E5) |
| `e1_frequencias.csv`, `e1_resumo.csv`, `e1_teoria_vs_observado.png` | Experimento 1 |
| `e2_medias_acumuladas.csv`, `e2_medias_acumuladas.png`, `e2_reproducao_semente_2026.csv` | Experimento 2 |
| `e3_participantes.csv`, `e3_resumo.csv`, `e3_trajetorias_5_primeiros.png`, `e3_saldos_finais.png` | Experimento 3 |
| `e4_condicional.csv` | Experimento 4 |
| `e5_tabelas_pagamento.csv` | Experimento 5 |

## Gerador e sementes
`random.Random` da biblioteca padrão (Mersenne Twister), com `randrange(5)` para cada rolo.
Sementes: E1 = 2026; E2 = 10, 2026 e 123456; E3 = 42 (aplicada uma única vez, sequência contínua entre participantes); E4 e E5 reutilizam as rodadas do E1.

## Pontos extras
- Validação automatizada: `testes.py` (pagamentos, lucro, semente, totais do E1/E3/E4 e caso-limite K = 4).

## Declaração de uso de IA
O assistente Claude (Anthropic) foi usado para gerar a primeira versão do código e dos testes. Eu revisei e executei o código, conferi os resultados com as contas de referência do enunciado (E[X] = −0,16; RTP = 84%; 92,4% na tabela +10%) e escrevi o relatório com minhas palavras.
