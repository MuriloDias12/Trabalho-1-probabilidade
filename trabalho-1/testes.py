"""
Validação automatizada do simulador (extra de 3 pontos).
Executar com:  python testes.py
"""

import itertools
import random
import unittest
from fractions import Fraction

import simulador as sim


class TestRegras(unittest.TestCase):

    def test_pagamento_das_cinco_triplas(self):
        esperado = {"A": 5, "B": 10, "C": 15, "D": 25, "E": 50}
        for s, valor in esperado.items():
            self.assertEqual(sim.calcular_premio((s, s, s)), valor)

    def test_premio_zero_nas_outras_120_triplas(self):
        triplas = list(itertools.product(sim.ROLO, repeat=3))
        self.assertEqual(len(triplas), 125)
        nao_premiadas = [t for t in triplas if len(set(t)) > 1]
        self.assertEqual(len(nao_premiadas), 120)
        for t in nao_premiadas:
            self.assertEqual(sim.calcular_premio(t), 0)

    def test_lucro_desconta_a_aposta(self):
        for p in (0, 5, 10, 15, 25, 50):
            self.assertEqual(sim.calcular_lucro(p), p - 1)

    def test_caso_limite_parada_4_volta_ao_inicio(self):
        # Figura 3 do enunciado: K = 4 mostra E, A, B
        self.assertEqual(sim.montar_coluna(4), ("E", "A", "B"))
        self.assertEqual(sim.montar_coluna(3), ("D", "E", "A"))

    def test_esperanca_exata_por_enumeracao(self):
        # percorre as 125 triplas, cada uma com probabilidade 1/125
        e_p = sum(Fraction(sim.calcular_premio(t), 125)
                  for t in itertools.product(sim.ROLO, repeat=3))
        self.assertEqual(e_p, Fraction(84, 100))
        self.assertEqual(e_p - 1, Fraction(-16, 100))

    def test_tabela_mais_10_tem_rtp_92_4(self):
        self.assertAlmostEqual(sim.esperanca_premio(sim.TABELA_MAIS_10), 0.924)


class TestReproducaoETotais(unittest.TestCase):

    def test_mesma_semente_reproduz_sequencia(self):
        a = sim.simular_rodadas(100, 2026)
        b = sim.simular_rodadas(100, 2026)
        self.assertEqual(a, b)

    def test_sementes_diferentes_geram_sequencias_diferentes(self):
        self.assertNotEqual(sim.simular_rodadas(100, 10), sim.simular_rodadas(100, 2026))

    def test_e1_contagens_somam_10000(self):
        sim.DIR_RESULTADOS.mkdir(exist_ok=True)
        tabela, resumo = sim.experimento_1(sim.simular_rodadas(10_000, 2026))
        self.assertEqual(sum(l["contagem"] for l in tabela), 10_000)

    def test_e3_categorias_somam_100(self):
        sim.DIR_RESULTADOS.mkdir(exist_ok=True)
        r = sim.experimento_3()
        self.assertEqual(r["ganho_n"] + r["empate_n"] + r["perda_n"], 100)
        self.assertLessEqual(r["esgotamento_n"], r["perda_n"])

    def test_e4_tem_9999_pares(self):
        sim.DIR_RESULTADOS.mkdir(exist_ok=True)
        tabela, n_pares = sim.experimento_4(sim.simular_rodadas(10_000, 2026))
        self.assertEqual(n_pares, 9_999)
        self.assertEqual(sum(l["total_pares"] for l in tabela), 9_999)

    def test_simbolo_central_aproximadamente_uniforme(self):
        rng = random.Random(7)
        cont = {s: 0 for s in sim.ROLO}
        for _ in range(50_000):
            cont[sim.montar_coluna(sim.sortear_parada(rng))[1]] += 1
        for s in sim.ROLO:
            self.assertAlmostEqual(cont[s] / 50_000, 0.2, delta=0.01)


if __name__ == "__main__":
    unittest.main(verbosity=2)
