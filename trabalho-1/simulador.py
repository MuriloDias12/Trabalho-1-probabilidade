"""
Simulador acadêmico - somente créditos fictícios
Trabalho I - Probabilidade e Estatística I - IFES Campus Serra - 2026/2

Uso:
    python simulador.py            -> mostra uma rodada e executa os 5 experimentos
    python simulador.py --rodada   -> mostra apenas uma rodada (semente opcional: --semente 7)
    python simulador.py --jogar    -> modo interativo, uma rodada por Enter
"""

import argparse
import csv
import json
import platform
import random
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # gera arquivos de imagem sem abrir janelas
import matplotlib.pyplot as plt

# =====================================================================
# 1. REGRAS DO MODELO (Seção 5 do enunciado)
# =====================================================================

AVISO = "Simulador acadêmico - somente créditos fictícios"
ROLO = ("A", "B", "C", "D", "E")  # sequência circular R, posições 0 a 4
APOSTA = 1  # crédito fictício por rodada

TABELA_BASE = {"A": 5, "B": 10, "C": 15, "D": 25, "E": 50}
TABELA_MAIS_10 = {"A": 5.5, "B": 11, "C": 16.5, "D": 27.5, "E": 55}

PROB_TRIPLA = (1 / 5) ** 3          # 1/125
PROB_PREMIO = 5 * PROB_TRIPLA       # 5/125 = 4%

DIR_RESULTADOS = Path(__file__).resolve().parent / "resultados"


def sortear_parada(rng):
    """Sorteia a parada K de um rolo: 0, 1, 2, 3 ou 4, cada uma com prob. 1/5."""
    return rng.randrange(len(ROLO))


def montar_coluna(k):
    """Janela do rolo para a parada K: (topo, centro, base) = R_K, R_(K+1) mod 5, R_(K+2) mod 5."""
    return tuple(ROLO[(k + i) % len(ROLO)] for i in range(3))


def rodar(rng):
    """Uma rodada: três sorteios independentes, um por rolo.
    Devolve as paradas, as três colunas e a linha central."""
    paradas = tuple(sortear_parada(rng) for _ in range(3))
    colunas = tuple(montar_coluna(k) for k in paradas)
    linha_central = tuple(coluna[1] for coluna in colunas)
    return paradas, colunas, linha_central


def calcular_premio(linha, tabela=TABELA_BASE):
    """Prêmio bruto P: paga só se os três símbolos da linha central forem iguais."""
    if linha[0] == linha[1] == linha[2]:
        return tabela[linha[0]]
    return 0


def calcular_lucro(premio, aposta=APOSTA):
    """Lucro líquido X = P - aposta."""
    return premio - aposta


def esperanca_premio(tabela):
    """E[P] teórico: cada tripla premiada tem probabilidade 1/125."""
    return sum(valor * PROB_TRIPLA for valor in tabela.values())


# =====================================================================
# 2. EXIBIÇÃO E REGISTRO
# =====================================================================

def exibir_rodada(colunas, linha, premio, lucro):
    print(f"\n  {AVISO}")
    print("        Rolo 1  Rolo 2  Rolo 3")
    for i, nome in enumerate(("topo  ", "centro", "base  ")):
        seta = "->" if i == 1 else "  "
        simbolos = "       ".join(c[i] for c in colunas)
        print(f"  {nome}{seta}  {simbolos}   {'<-' if i == 1 else ''}")
    print(f"  Linha central: {'-'.join(linha)} | Prêmio P = {premio} | Lucro X = {lucro}")


def simular_rodadas(n, semente, tabela=TABELA_BASE):
    """Executa n rodadas. A semente é aplicada UMA vez, no início da execução."""
    rng = random.Random(semente)
    registros = []
    for i in range(1, n + 1):
        paradas, _, linha = rodar(rng)
        p = calcular_premio(linha, tabela)
        registros.append({
            "rodada": i,
            "k1": paradas[0], "k2": paradas[1], "k3": paradas[2],
            "linha_central": "".join(linha),
            "P": p,
            "X": calcular_lucro(p),
        })
    return registros


def salvar_csv(nome, linhas):
    caminho = DIR_RESULTADOS / nome
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def salvar_figura(fig, nome):
    fig.tight_layout()
    fig.savefig(DIR_RESULTADOS / nome, dpi=200)
    plt.close(fig)


def medias_acumuladas(valores):
    soma, medias = 0, []
    for i, v in enumerate(valores, start=1):
        soma += v
        medias.append(soma / i)
    return medias


# =====================================================================
# 3. EXPERIMENTOS
# =====================================================================

COMBINACAO_POR_LUCRO = {4: "A-A-A", 9: "B-B-B", 14: "C-C-C",
                        24: "D-D-D", 49: "E-E-E", -1: "Qualquer outra"}
PROB_POR_LUCRO = {-1: 120 / 125, 4: 1 / 125, 9: 1 / 125,
                  14: 1 / 125, 24: 1 / 125, 49: 1 / 125}


def experimento_1(registros):
    """As frequências acompanham as probabilidades?"""
    n = len(registros)
    X = [r["X"] for r in registros]
    P = [r["P"] for r in registros]
    contagem = Counter(X)

    tabela = []
    for valor in sorted(PROB_POR_LUCRO):
        tabela.append({
            "lucro_X": valor,
            "combinacao": COMBINACAO_POR_LUCRO[valor],
            "prob_teorica": round(PROB_POR_LUCRO[valor], 6),
            "contagem": contagem.get(valor, 0),
            "freq_relativa": round(contagem.get(valor, 0) / n, 6),
        })
    total = sum(linha["contagem"] for linha in tabela)
    assert total == n, f"Contagens somam {total}, esperado {n}"
    salvar_csv("e1_frequencias.csv", tabela)

    # desvio-padrão teórico, para referência
    ex = sum(x * p for x, p in PROB_POR_LUCRO.items())
    ex2 = sum(x ** 2 * p for x, p in PROB_POR_LUCRO.items())
    dp_teorico = (ex2 - ex ** 2) ** 0.5

    resumo = {
        "N": n,
        "soma_contagens": total,
        "lucro_medio": round(statistics.fmean(X), 4),
        "lucro_esperado_teorico": round(ex, 4),
        "RTP_observado_%": round(100 * statistics.fmean(P) / APOSTA, 2),
        "RTP_teorico_%": round(100 * esperanca_premio(TABELA_BASE) / APOSTA, 2),
        "prop_rodadas_premiadas_%": round(100 * sum(p > 0 for p in P) / n, 2),
        "prob_premio_teorica_%": round(100 * PROB_PREMIO, 2),
        "desvio_padrao_amostral_s": round(statistics.stdev(X), 4),  # divisor N-1
        "desvio_padrao_teorico": round(dp_teorico, 4),
    }
    salvar_csv("e1_resumo.csv", [resumo])

    # Gráfico: teoria x observação. Painel (b) amplia os resultados premiados.
    fig, eixos = plt.subplots(1, 2, figsize=(11, 4.2))
    rotulos = [str(l["lucro_X"]) for l in tabela]
    teor = [100 * l["prob_teorica"] for l in tabela]
    obs = [100 * l["freq_relativa"] for l in tabela]
    for ax, ini, titulo in ((eixos[0], 0, "(a) todos os resultados"),
                            (eixos[1], 1, "(b) apenas resultados premiados")):
        pos = range(len(rotulos[ini:]))
        b1 = ax.bar([p - 0.2 for p in pos], teor[ini:], 0.4, label="Teórica", color="#2f4f4f")
        b2 = ax.bar([p + 0.2 for p in pos], obs[ini:], 0.4, label="Observada", color="#5fa88a")
        ax.bar_label(b1, labels=[f"{v:.2f}".replace(".", ",") for v in teor[ini:]], fontsize=7)
        ax.bar_label(b2, labels=[f"{v:.2f}".replace(".", ",") for v in obs[ini:]], fontsize=7)
        ax.set_ylim(0, max(teor[ini:] + obs[ini:]) * 1.3)
        ax.set_xticks(list(pos), rotulos[ini:])
        ax.set_xlabel("Lucro X por rodada (créditos)")
        ax.set_ylabel("Percentual das rodadas (%)")
        ax.text(0.02, 0.97, titulo, transform=ax.transAxes, va="top", fontsize=9)
        ax.legend(loc="upper right", fontsize=8, ncol=2)
    salvar_figura(fig, "e1_teoria_vs_observado.png")
    return tabela, resumo


def experimento_2(registros_2026):
    """O que muda quando aumentamos a amostra?"""
    sementes = (10, 2026, 123456)
    marcos = (100, 1_000, 10_000)
    execucoes = {2026: registros_2026}  # reutiliza a sequência do E1
    for s in sementes:
        if s not in execucoes:
            execucoes[s] = simular_rodadas(10_000, s)

    tabela, trajetorias = [], {}
    for s in sementes:
        medias = medias_acumuladas([r["X"] for r in execucoes[s]])
        trajetorias[s] = medias
        linha = {"semente": s}
        for m in marcos:
            linha[f"media_apos_{m}"] = round(medias[m - 1], 4)
        tabela.append(linha)
    salvar_csv("e2_medias_acumuladas.csv", tabela)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for s, cor in zip(sementes, ("#c0504d", "#2f4f4f", "#4f81bd")):
        ax.plot(range(1, 10_001), trajetorias[s], label=f"Semente {s}", color=cor, lw=1.2)
    ax.axhline(-0.16, color="black", ls="--", lw=1, label="E[X] = -0,16")
    ax.set_xscale("log")
    ax.set_xlabel("Número de rodadas (escala logarítmica)")
    ax.set_ylabel("Lucro médio acumulado (créditos)")
    ax.legend()
    salvar_figura(fig, "e2_medias_acumuladas.png")

    # Reprodução: repetir a semente 2026 e comparar as 10 primeiras rodadas
    repeticao = simular_rodadas(10_000, 2026)
    comparacao = []
    for a, b in zip(registros_2026[:10], repeticao[:10]):
        comparacao.append({
            "rodada": a["rodada"],
            "linha_execucao_1": a["linha_central"], "X_execucao_1": a["X"],
            "linha_execucao_2": b["linha_central"], "X_execucao_2": b["X"],
            "igual": a == b,
        })
    salvar_csv("e2_reproducao_semente_2026.csv", comparacao)
    reproduzido = all(c["igual"] for c in comparacao)
    return tabela, reproduzido


def experimento_3(n_participantes=100, saldo_inicial=100, max_rodadas=500, semente=42):
    """O que acontece com um saldo limitado?"""
    rng = random.Random(semente)  # semente aplicada uma vez; sequência continua entre participantes
    participantes, trajetorias = [], []
    for pid in range(1, n_participantes + 1):
        saldo, rodadas, traj = saldo_inicial, 0, [saldo_inicial]
        while rodadas < max_rodadas and saldo >= APOSTA:
            _, _, linha = rodar(rng)
            saldo += calcular_lucro(calcular_premio(linha))
            rodadas += 1
            traj.append(saldo)
        participantes.append({
            "participante": pid,
            "saldo_final": saldo,
            "rodadas": rodadas,
            "esgotou": saldo < APOSTA,
        })
        trajetorias.append(traj)
    salvar_csv("e3_participantes.csv", participantes)

    finais = [p["saldo_final"] for p in participantes]
    ganho = sum(f > saldo_inicial for f in finais)
    empate = sum(f == saldo_inicial for f in finais)
    perda = sum(f < saldo_inicial for f in finais)
    esgot = sum(p["esgotou"] for p in participantes)
    assert ganho + empate + perda == n_participantes
    assert all(p["saldo_final"] < saldo_inicial for p in participantes if p["esgotou"])

    resumo = {
        "participantes": n_participantes,
        "ganho_n": ganho, "ganho_%": 100 * ganho / n_participantes,
        "empate_n": empate, "empate_%": 100 * empate / n_participantes,
        "perda_n": perda, "perda_%": 100 * perda / n_participantes,
        "esgotamento_n": esgot, "esgotamento_%_do_total": 100 * esgot / n_participantes,
        "esgotamento_%_das_perdas": round(100 * esgot / perda, 2) if perda else "não estimável",
        "media_saldo_final": round(statistics.fmean(finais), 2),
        "mediana_saldo_final": statistics.median(finais),
        "menor_saldo_final": min(finais),
        "maior_saldo_final": max(finais),
        "media_rodadas": round(statistics.fmean(p["rodadas"] for p in participantes), 1),
    }
    salvar_csv("e3_resumo.csv", [resumo])

    # Trajetórias dos 5 primeiros (sem seleção); após a parada, saldo constante
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for i in range(5):
        traj = trajetorias[i] + [trajetorias[i][-1]] * (max_rodadas + 1 - len(trajetorias[i]))
        ax.plot(range(max_rodadas + 1), traj, lw=1.2, label=f"Participante {i + 1}")
    ax.axhline(saldo_inicial, color="gray", ls=":", lw=1, label="Saldo inicial")
    ax.set_xlabel("Rodada")
    ax.set_ylabel("Saldo (créditos)")
    ax.legend(fontsize=8)
    salvar_figura(fig, "e3_trajetorias_5_primeiros.png")

    # Distribuição dos saldos finais (apoio para comparar média e mediana)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.hist(finais, bins=20, color="#5fa88a", edgecolor="white")
    ax.axvline(resumo["media_saldo_final"], color="#c0504d", ls="--", label="Média")
    ax.axvline(resumo["mediana_saldo_final"], color="#2f4f4f", ls="-", label="Mediana")
    ax.axvline(saldo_inicial, color="gray", ls=":", label="Saldo inicial")
    ax.set_xlabel("Saldo final (créditos)")
    ax.set_ylabel("Número de participantes")
    ax.legend()
    salvar_figura(fig, "e3_saldos_finais.png")
    return resumo


def experimento_4(registros):
    """Depois de perder, aumenta a chance de ganhar?"""
    premiada = [r["P"] > 0 for r in registros]
    pares = list(zip(premiada[:-1], premiada[1:]))
    assert len(pares) == len(registros) - 1

    tabela = []
    for anterior, rotulo in ((False, "sem prêmio"), (True, "com prêmio")):
        grupo = [seguinte for ant, seguinte in pares if ant == anterior]
        total, premios = len(grupo), sum(grupo)
        tabela.append({
            "resultado_anterior": rotulo,
            "total_pares": total,
            "premios_na_seguinte": premios,
            "proporcao_%": round(100 * premios / total, 2) if total else "não estimável",
            "referencia_modelo_%": round(100 * PROB_PREMIO, 2),
        })
    salvar_csv("e4_condicional.csv", tabela)
    return tabela, len(pares)


def experimento_5(registros):
    """Prêmios maiores tornam o jogo favorável? Mesmos 10.000 resultados do E1."""
    n = len(registros)
    tabela = []
    for nome, tab in (("Base", TABELA_BASE), ("Prêmios +10%", TABELA_MAIS_10)):
        P = [calcular_premio(r["linha_central"], tab) for r in registros]
        X = [calcular_lucro(p) for p in P]
        premiados = [p for p in P if p > 0]
        e_p = esperanca_premio(tab)
        tabela.append({
            "configuracao": nome,
            "prob_premio_teorica_%": round(100 * PROB_PREMIO, 2),
            "freq_premio_observada_%": round(100 * len(premiados) / n, 2),
            "premio_medio_por_rodada": round(statistics.fmean(P), 4),
            "premio_medio_quando_premiado": round(statistics.fmean(premiados), 4) if premiados else "não estimável",
            "lucro_esperado_teorico": round(e_p - APOSTA, 4),
            "lucro_medio_observado": round(statistics.fmean(X), 4),
            "RTP_teorico_%": round(100 * e_p / APOSTA, 2),
            "RTP_observado_%": round(100 * statistics.fmean(P) / APOSTA, 2),
        })
    salvar_csv("e5_tabelas_pagamento.csv", tabela)
    return tabela


# =====================================================================
# 4. EXECUÇÃO
# =====================================================================

def registrar_ambiente():
    meta = {
        "aviso": AVISO,
        "data_execucao": datetime.now().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "implementacao": platform.python_implementation(),
        "sistema": platform.platform(),
        "gerador": "random.Random (biblioteca padrão; Mersenne Twister MT19937)",
        "sorteio": "random.Random.randrange(5) para cada rolo",
        "matplotlib": matplotlib.__version__,
        "sementes": {"E1": 2026, "E2": [10, 2026, 123456], "E3": 42,
                     "E4": "reutiliza E1", "E5": "reutiliza E1"},
        "parametros": {"aposta": APOSTA, "tabela_base": TABELA_BASE,
                       "tabela_mais_10": TABELA_MAIS_10, "E3_saldo_inicial": 100,
                       "E3_max_rodadas": 500, "E3_participantes": 100},
    }
    with open(DIR_RESULTADOS / "ambiente.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def executar_tudo():
    DIR_RESULTADOS.mkdir(exist_ok=True)
    registrar_ambiente()

    print("=" * 60)
    print(f"  {AVISO}")
    print("=" * 60)

    print("\nRodada de demonstração (semente 1):")
    _, colunas, linha = rodar(random.Random(1))
    p = calcular_premio(linha)
    exibir_rodada(colunas, linha, p, calcular_lucro(p))

    registros_2026 = simular_rodadas(10_000, 2026)
    salvar_csv("e1_rodadas_semente_2026.csv", registros_2026)

    print("\n--- Experimento 1 ---")
    tabela1, resumo1 = experimento_1(registros_2026)
    for linha in tabela1:
        print(f"  X={linha['lucro_X']:>3}  teórica={linha['prob_teorica']:.4f}  "
              f"contagem={linha['contagem']:>5}  freq={linha['freq_relativa']:.4f}")
    for k, v in resumo1.items():
        print(f"  {k}: {v}")

    print("\n--- Experimento 2 ---")
    tabela2, reproduzido = experimento_2(registros_2026)
    for linha in tabela2:
        print("  ", linha)
    print(f"  Semente 2026 reproduziu as 10 primeiras rodadas: {'SIM' if reproduzido else 'NÃO'}")

    print("\n--- Experimento 3 ---")
    for k, v in experimento_3().items():
        print(f"  {k}: {v}")

    print("\n--- Experimento 4 ---")
    tabela4, n_pares = experimento_4(registros_2026)
    print(f"  Pares analisados: {n_pares}")
    for linha in tabela4:
        print("  ", linha)

    print("\n--- Experimento 5 ---")
    for linha in experimento_5(registros_2026):
        print("  ", linha)

    print(f"\nResultados salvos em: {DIR_RESULTADOS}")


def modo_interativo(semente):
    rng = random.Random(semente)
    saldo = 100
    print(f"\n{AVISO}\nSaldo fictício inicial: {saldo}. Enter = rodar, q = sair.")
    while saldo >= APOSTA:
        if input("> ").strip().lower() == "q":
            break
        _, colunas, linha = rodar(rng)
        p = calcular_premio(linha)
        x = calcular_lucro(p)
        saldo += x
        exibir_rodada(colunas, linha, p, x)
        print(f"  Saldo fictício: {saldo}")
    print("Fim da sessão.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=AVISO)
    parser.add_argument("--rodada", action="store_true", help="mostra apenas uma rodada")
    parser.add_argument("--jogar", action="store_true", help="modo interativo")
    parser.add_argument("--semente", type=int, default=1, help="semente para --rodada/--jogar")
    args = parser.parse_args()

    if args.rodada:
        _, colunas, linha = rodar(random.Random(args.semente))
        p = calcular_premio(linha)
        exibir_rodada(colunas, linha, p, calcular_lucro(p))
    elif args.jogar:
        modo_interativo(args.semente)
    else:
        executar_tudo()
