# -*- coding: utf-8 -*-
"""OS CANDIDATOS, TESTADOS SEM O CORPUS DE AVALIACAO.

Todos os casos aqui sao SINTETICOS. Nenhum veio dos 36, e nenhum foi
escolhido a olhar para eles.

    AJUSTAR UM CANDIDATO COM OS 36 NA MAO
    E ESCREVER A RESPOSTA E CHAMAR-LHE HIPOTESE.
"""
import importlib.util
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

def _carrega(apelido, ficheiro):
    spec = importlib.util.spec_from_file_location(
        apelido, os.path.join(RAIZ, "provas", ficheiro))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


I = _carrega("impl_c", "implementacoes_candidatas.py")
# A lista de campos de caminho tem UM dono: a ficha congelada. Copiar a lista
# para aqui era criar um segundo dono que se desactualiza em silencio.
FICHA = _carrega("cand_t", "candidatos_tematicos.py")

# ── FIXTURES SINTETICOS ───────────────────────────────────────────────────
# Escritos a mao, com nomes cientificos publicos. Nenhum e um documento real
# desta arvore.
SINTETICOS = {
    "vazio": {"id": "s1", "texto": ""},
    "so_espacos": {"id": "s2", "texto": "   \n\t  "},
    "sem_campo": {"id": "s3"},
    "praga_latim": {"id": "s4", "texto":
        "Monitoraggio di Lobesia botrana e Plasmopara viticola su Vitis vinifera"},
    "praga_negada": {"id": "s5", "texto":
        "Nessuna presenza di Lobesia botrana. Assenza di Plasmopara viticola."},
    "outro_universo": {"id": "s6", "texto":
        "Decreto di autorizzazione e registrazione in gazzetta ufficiale, "
        "etichetta e foglietto illustrativo del prodotto"},
    "ambiguo": {"id": "s7", "texto":
        "Bollettino meteorologico con una nota su Erwinia amylovora"},
    "ingles": {"id": "s8", "texto":
        "Survey of Erwinia amylovora and Venturia inaequalis in orchards"},
    "enorme": {"id": "s9", "texto":
        ("Lobesia botrana Plasmopara viticola " * 40000)},
    "sem_conceito": {"id": "s10", "texto":
        "Relazione annuale sui prezzi medi e sul mercato all ingrosso"},
}


def _vivos():
    """So os candidatos que correm neste ambiente."""
    return {cid: c() for cid, c in I.CANDIDATOS_VIVOS.items()
            if cid not in ("C3-LLM-STRUCTURED",)}


class TodoCandidatoRespeitaOContratoDaCasa(unittest.TestCase):

    def test_a_saida_e_sempre_uma_decisao_do_vocabulario_da_porta(self):
        for cid, c in _vivos().items():
            for nome, item in SINTETICOS.items():
                d = c.classificar(item)
                self.assertIn(d.resultado, adm.RESULTADOS,
                              "%s / %s" % (cid, nome))
                self.assertTrue(d.motivo, "%s / %s sem motivo" % (cid, nome))

    def test_a_decisao_diz_quem_a_tomou(self):
        for cid, c in _vivos().items():
            d = c.classificar(SINTETICOS["praga_latim"])
            self.assertEqual(d.evidencia.get("candidato"), cid)

    def test_texto_vazio_e_abstencao_e_nunca_negativo(self):
        for nome in ("vazio", "so_espacos", "sem_campo"):
            for cid, c in _vivos().items():
                d = c.classificar(SINTETICOS[nome])
                self.assertEqual(d.resultado, adm.NAO_SEI,
                                 "%s / %s devolveu %s" % (cid, nome, d.resultado))

    def test_metadata_ausente_nao_rebenta(self):
        for cid, c in _vivos().items():
            d = c.classificar({"texto": "Lobesia botrana"})
            self.assertIn(d.resultado, adm.RESULTADOS, cid)


class ODeterminismoFoiMedido(unittest.TestCase):
    """Correr dez vezes e obter dez respostas iguais nao e obvio: e medido."""

    def test_dez_corridas_dao_a_mesma_resposta(self):
        for cid, c in _vivos().items():
            if not c.DETERMINISTICO:
                continue
            for nome, item in SINTETICOS.items():
                respostas = {c.classificar(item).resultado for _ in range(10)}
                self.assertEqual(len(respostas), 1,
                                 "%s / %s variou: %s" % (cid, nome, respostas))

    def test_instancias_diferentes_concordam(self):
        for cid, classe in I.CANDIDATOS_VIVOS.items():
            if cid == "C3-LLM-STRUCTURED":
                continue
            a, b = classe(), classe()
            for item in SINTETICOS.values():
                self.assertEqual(a.classificar(item).resultado,
                                 b.classificar(item).resultado, cid)


class C1IsolaOCasamento(unittest.TestCase):

    def setUp(self):
        self.c = I.C1LexicalEstruturada()

    def test_a_fronteira_de_palavra_mata_o_substring(self):
        """O defeito historico: `lancio` dentro de `bilancio`."""
        self.assertIsNone(I._por_palavra("lancio", "il bilancio annuale"))
        self.assertIsNotNone(I._por_palavra("lancio", "il lancio del"))

    def test_o_escopo_de_negacao_desconta_o_termo(self):
        afirmado = self.c.classificar(
            {"id": "x", "texto": "presenza di parassita e di malattia"})
        negado = self.c.classificar(
            {"id": "x", "texto": "assenza di parassita e senza malattia"})
        self.assertEqual(afirmado.resultado, adm.SIM)
        self.assertNotEqual(negado.resultado, adm.SIM)

    def test_um_termo_isolado_nao_decide(self):
        d = self.c.classificar({"id": "x", "texto": "una nota su malattia"})
        self.assertEqual(d.resultado, adm.NAO_SEI)

    def test_usa_a_lista_do_dono_e_nao_uma_copia(self):
        self.assertEqual(sorted(self.c.termos), sorted(adm.PERGUNTAS_DO_UNIVERSO))


class C2DecidePorConceito(unittest.TestCase):

    def setUp(self):
        self.c = I.C2TaxonomiaConceito()

    def test_o_vocabulario_tem_tamanho_medido(self):
        self.assertGreater(self.c.total_conceitos, 500)

    def test_o_nome_cientifico_atravessa_a_lingua(self):
        """O mesmo conceito, em italiano e em ingles, da a mesma resposta."""
        it = self.c.classificar(SINTETICOS["praga_latim"])
        en = self.c.classificar(SINTETICOS["ingles"])
        self.assertEqual(it.resultado, adm.SIM)
        self.assertEqual(en.resultado, adm.SIM)

    def test_ausencia_de_conceito_e_abstencao_e_nunca_negativo(self):
        """A cobertura do vocabulario e incompleta e esta medida."""
        d = self.c.classificar(SINTETICOS["sem_conceito"])
        self.assertEqual(d.resultado, adm.NAO_SEI)
        self.assertIn("cobertura", d.motivo)

    def test_o_indice_decide_igual_a_varredura_ingenua(self):
        """⚠️ O INDICE NASCEU DE UMA MEDICAO DE TEMPO, NAO DE UMA IDEIA.

        A versao ingenua corria uma expressao regular POR CONCEITO: 15,8 s
        num texto de 340 mil caracteres, e o corpus real tem um ficheiro de
        7,9 milhoes. Reescrever por velocidade e legitimo; reescrever e mudar
        a DECISAO sem reparar seria trocar o candidato depois de o congelar.

            UMA REESCRITA POR DESEMPENHO
            TEM DE PROVAR QUE DECIDE IGUAL.
        """
        def ingenuo(texto, inventario):
            fora = []
            for codigo, nome in inventario.items():
                if not nome or len(nome) < 5:
                    continue
                if I._por_palavra(nome, texto):
                    fora.append(codigo)
                else:
                    genero = nome.split()[0]
                    if len(genero) >= 6 and I._por_palavra(genero, texto):
                        fora.append(codigo)
            return sorted(set(fora))

        casos = [SINTETICOS[k]["texto"] for k in
                 ("praga_latim", "ingles", "ambiguo", "sem_conceito",
                  "outro_universo", "praga_negada")]
        casos += ["Venturia inaequalis su melo", "Erwinia sp. su pero",
                  "nessun Bactrocera oleae", "Plasmopara e Botrytis cinerea"]
        for texto in casos:
            t = I._normal(texto)
            self.assertEqual(
                sorted({c for c, _n in self.c._conceitos(t, self.c.alvos)}),
                ingenuo(t, self.c.alvos),
                "o indice divergiu da varredura em: %r" % texto[:60])

    def test_o_indice_e_rapido_o_bastante_para_o_corpus_real(self):
        import time
        t0 = time.time()
        self.c.classificar({"id": "x", "texto": "Erwinia amylovora " * 200000})
        gasto = time.time() - t0
        self.assertLess(gasto, 10.0, "%.1fs num texto de ~3,4M" % gasto)

    def test_texto_enorme_nao_rebenta(self):
        d = self.c.classificar(SINTETICOS["enorme"])
        self.assertIn(d.resultado, adm.RESULTADOS)


class C3ConfessaQueNaoCorre(unittest.TestCase):

    def test_sem_credencial_devolve_erro_e_nunca_negativo(self):
        c = I.C3ModeloDeLinguagem()
        if c.disponivel():
            self.skipTest("ha credencial neste ambiente")
        d = c.classificar(SINTETICOS["praga_latim"])
        self.assertEqual(d.resultado, adm.ERRO)
        self.assertNotEqual(d.resultado, adm.NAO)
        self.assertNotEqual(d.resultado, adm.NAO_SEI)

    def test_o_erro_diz_de_que_depende(self):
        c = I.C3ModeloDeLinguagem()
        if c.disponivel():
            self.skipTest("ha credencial neste ambiente")
        d = c.classificar(SINTETICOS["praga_latim"])
        self.assertIn("dependencia", d.evidencia)


class C4DegradaEmVezDeCair(unittest.TestCase):

    def setUp(self):
        self.c = I.C4Cascata()

    def test_o_que_o_primeiro_andar_resolve_mantem_se(self):
        d = self.c.classificar(SINTETICOS["praga_latim"])
        self.assertEqual(d.resultado, adm.SIM)
        self.assertEqual(d.evidencia["andar"], "1-TAXONOMIA")

    def test_o_que_escala_sai_erro_quando_o_segundo_andar_falta(self):
        if self.c.andar2.disponivel():
            self.skipTest("ha credencial neste ambiente")
        d = self.c.classificar(SINTETICOS["sem_conceito"])
        self.assertEqual(d.resultado, adm.ERRO)
        self.assertEqual(d.evidencia["andar"], "2-ESCALADO")

    def test_o_registo_nomeia_o_andar_que_decidiu(self):
        """A propriedade auditavel que so a cascata da."""
        for item in SINTETICOS.values():
            d = self.c.classificar(item)
            self.assertIn(d.evidencia.get("andar"),
                          ("1-TAXONOMIA", "2-ESCALADO"))


class NenhumCandidatoToccaNoCorpusDeAvaliacao(unittest.TestCase):

    def test_o_modulo_nao_abre_ficheiro_proibido(self):
        import ast
        with open(os.path.join(RAIZ, "provas",
                               "implementacoes_candidatas.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        proibidos = ("T3-GROUND-TRUTH-EVAL-V1", "BASELINE-ADMISSION-T3-V1",
                     "T3-HUMAN-REVIEW", "LIVRO-DE-DECISOES")
        arvore = ast.parse(fonte)
        for no in ast.walk(arvore):
            if isinstance(no, ast.Constant) and isinstance(no.value, str):
                for mau in proibidos:
                    self.assertNotIn(mau, no.value)

    def test_nenhum_candidato_le_caminho_nem_fonte(self):
        """O caminho embute o universo declarado: 78 de 78 no atlas.

        ⚠️ ESTE TESTE JA EXISTIU NUMA FORMA QUE NAO MORDIA. A primeira versao
        punha os conceitos no TEXTO e tambem no caminho: o candidato respondia
        SIM pelos dois lados, e um mecanismo que lesse o caminho passava na
        mesma. Uma mutacao que fazia C2 concatenar `BODY_PATH` ao texto
        SOBREVIVEU a suite inteira.

            APRESENTAR A PROVA PROIBIDA AO LADO DA PERMITIDA
            NAO TESTA QUAL DELAS FOI USADA.

        Agora o texto e neutro e os conceitos vivem SO nos metadados. Quem os
        ler muda de resposta, e a mudanca e a falha.
        """
        neutro = ("Relazione trimestrale sui prezzi medi al dettaglio "
                  "e sul mercato all ingrosso, con allegato statistico.")
        envenenado = "data/corpus/aphis-fabae/aphis-gossypii/doc-999.json"
        sem = {"id": "x", "texto": neutro}
        for campo in FICHA.CAMPOS_DE_CAMINHO + ("source_id", "PUBLISHER"):
            item = {"id": "x", "texto": neutro, campo: envenenado}
            for cid, c in _vivos().items():
                self.assertEqual(
                    c.classificar(item).resultado,
                    c.classificar(sem).resultado,
                    "%s mudou de resposta quando o conceito estava so em %s"
                    % (cid, campo))

    def test_um_conceito_so_nao_chega_ao_limiar_de_c2(self):
        """O limiar de C2 vale 2, e o teste tem de sentir a diferenca.

        Uma mutacao que baixava LIMIAR_DE_CONCEITOS para 1 sobreviveu: todos
        os sinteticos tinham zero conceitos ou dois. O limiar nunca foi
        interrogado no unico ponto onde ele decide — o meio.

            UM LIMIAR SO ESTA TESTADO
            SE ALGUM CASO CAIR EXACTAMENTE POR BAIXO DELE.

        Uma mencao unica e uma mencao. Nao e o assunto do documento, e C2 nao
        tem licenca para dizer SIM a partir dela. Diz NAO_SEI — que e o que
        um inventario de cobertura medida e incompleta pode honestamente dizer.
        """
        item = {"id": "u1", "texto":
                "Rilevata Aphis fabae nel campione di ieri, senza altro."}
        c2 = _vivos()["C2-TAXONOMY-CONCEPT"]
        self.assertEqual(len(c2._conceitos(I._normal(item["texto"]), c2.alvos)), 1,
                         "o fixture deixou de ter exactamente um conceito")
        self.assertEqual(I.LIMIAR_DE_CONCEITOS, 2,
                         "o limiar congelado mudou sem passar pelo diario")
        self.assertEqual(c2.classificar(item).resultado, adm.NAO_SEI)

    def test_o_indice_exige_que_o_binomio_esteja_junto(self):
        """Duas palavras separadas por uma negacao nao sao um binomio.

        Mutacao sobrevivente: trocar a comparacao de contiguidade por `True`,
        isto e, dar por encontrado qualquer conceito cuja PRIMEIRA palavra
        aparecesse. Sobreviveu porque o genero sozinho ja conta quando tem 6
        ou mais letras — e todos os sinteticos usavam generos longos, onde o
        ramo do genero tapava o da contiguidade.

            DOIS CAMINHOS QUE DAO A MESMA RESPOSTA EM TODOS OS EXEMPLOS
            SAO UM CAMINHO TESTADO E OUTRO POR TESTAR.

        `aphis` tem cinco letras: o ramo do genero nao dispara, e so a
        contiguidade pode decidir. O texto abaixo contem `aphis` e `gossypii`
        e NAO contem `Aphis gossypii`.
        """
        c2 = _vivos()["C2-TAXONOMY-CONCEPT"]
        junto = "Rilevata Aphis gossypii e Aphis fabae nel campione."
        partido = "Aphis non risulta, gossypii nemmeno, nel rapporto di ieri."
        self.assertEqual(c2.classificar({"id": "j", "texto": junto}).resultado,
                         adm.SIM)
        self.assertEqual(c2.classificar({"id": "p", "texto": partido}).resultado,
                         adm.NAO_SEI,
                         "o indice deu por encontrado um binomio desfeito")


if __name__ == "__main__":
    unittest.main()
