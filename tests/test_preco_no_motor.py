#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRECO-NO-MOTOR — o preco nasce da corrida canonica, pelo MESMO item, ou nao nasce.

    python -m pytest tests/test_preco_no_motor.py -v

Decisao do dono (Diretoria 28/09): «o preco ainda NAO e consumido pelo motor da Intelligence» — PRICE/UNIT
chegavam ao objeto por um script fora do Git. Agora `correr(..., precos=...)` produz o objeto.

    POSITIVO   a linha real do derived:911 (myfruit, Lamponi, Firenze) vira UM objeto de mercado, com
               PRICE/UNIT/PERIOD literais, RAW_SHA256, citacao, MARKET_STAGE = NAO SEI.
    A          item sem linha de preco           -> nenhum objeto de preco
    B          linha ligada a outro RAW          -> nenhum objeto (RAW_DE_OUTRO_ITEM)
    C          sha incompativel                  -> nenhum objeto (SHA_INCOMPATIVEL)
    D          preco so no bloco relacionado     -> nenhum objeto (CITACAO_SO_FORA_DO_ARTIGO)
    E          reprocessar o MESMO item          -> mesma corrida, mesmo objeto, sem duplicar
"""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for g in ("", "motor", "provas", "leis", "pacote"):
    if str(RAIZ / g) not in sys.path:
        sys.path.insert(0, str(RAIZ / g))

import corrida_da_inteligencia as CI          # noqa: E402
import preco_do_item as PR                    # noqa: E402
import porta_da_referencia as PORTA           # noqa: E402

# ── o texto REAL do derived:911 (trechos literais da Sala, 28/09), encurtado nas bordas ──
ARTIGO = (
    "Reparto ortofrutta\n23 settembre 2026\nPiccoli frutti, a Firenze prezzo mirtilli sempre più su\n157\n"
    "L’ Osservatorio Piccoli frutti di myfruit.it a Firenze conferma un quadro sostanzialmente invariato "
    "rispetto alla settimana precedente, ma con prezzi in aumento per tutte le referenze . Questa l'estrema "
    "sintesi dell'Osservatorio Piccoli Frutti a Firenze che, oggi 23 settembre 2026, ha visitato 14 punti "
    "vendita di 14 insegne appartenenti a 9 gruppi della grande distribuzione . Prezzi di vendita Lamponi "
    "(12 rilevazioni): min. 19,90 euro/kg, max. 27,04 euro/kg, media 23,16 euro/kg Mirtilli (33 rilevazioni): "
    "min. 12,48 euro/kg, max. 26,24 euro/kg, media 18,87 euro/kg More (9 rilevazioni): min. 18,90 euro/kg, "
    "max. 27,84 euro/kg, media 24,12 euro/kg .\n")
RELACIONADO = (
    "Potrebbe interessarti anche\nReparto ortofrutta\n"
    "Piccoli frutti, a Firenze prezzo mirtilli sempre più su\n"
    "L’Osservatorio myfruit rileva rincari per tutte le referenze: more a 24,12 euro/kg e lamponi a 23,16 "
    "euro/kg. Qualità disomogenea a scaffale\nInnovazioni, tecnologie e packaging\n")
RODAPE = "NCX Drahorad srl\nVia Prov.le Sassuolo Vignola 315/1\nP.I/C.F. 01041460369 prezzo 9,99 euro/kg\n"
TEXTO = ARTIGO + RELACIONADO + RODAPE
BYTES = TEXTO.encode("utf-8")
SHA = hashlib.sha256(BYTES).hexdigest()
CORRIDA = "XX-T10-2026-09-24-035431-62acfb3dc0158ff7"
CITACAO = ("Lamponi (12 rilevazioni): min. 19,90 euro/kg, max. 27,04 euro/kg, media 23,16 euro/kg")


def item(ordem=2, item_id="derived:911", raw=1406, sha=SHA, texto=TEXTO, **kw):
    b = {"ESTADO": "PRONTO_PARA_INTELIGENCIA", "ITEM_ID": item_id, "SOURCE_ID": "IT-T10-018",
         "RAW_OBSERVATION_ID": raw, "CORRIDA": CORRIDA, "ORDEM": ordem, "UNIVERSO": "T10", "TEXTO": texto,
         "FACT_TIME": "2026-09-23", "FACT_TIME_BASIS": "RELATIVA_A_PUBLICACAO",
         "FACT_LOCATION": "Firenze", "FACT_LOCATION_BASIS": "MERCADO · CITADO · PROVINCE",
         "PUBLISHED_AT": "2026-09-23T14:59:00+00:00", "CAPTURED_AT": "2026-09-24T03:54:44.27Z",
         "RAW_SHA256": sha, "RAW_STORAGE_PATH": "XX/it-t10-018/OBSERVATION/x.html",
         "RAW_DOCUMENT_KEY": "IT-T10-018:URL:news/piccoli-frutti-a-firenze-prezzo-mirtilli-sempre-piu-su",
         "RAW_SOURCE_URL": "https://www.myfruit.it/news/piccoli-frutti-a-firenze-prezzo-mirtilli-sempre-piu-su"}
    b.update(kw)
    return b


def linha(**kw):
    """A linha REAL de `sala_de_espera_precos` do derived:911 (copia R9, 28/09)."""
    b = {"run_id": CORRIDA, "ordem": 2, "indicador": "PRECO", "cultura_literal": "Lamponi", "nivel": "PIAZZA",
         "praca": "Firenze", "valor_texto": "media 23,16 euro/kg", "valor_numerico": 23.16, "unidade": "euro/kg",
         "periodo_inicio": "2026-09-23", "periodo_fim": "2026-09-23", "classe": "CURRENT",
         "citacao_literal": CITACAO,
         "o_que_nao_prova": ("preco de gôndola de grande distribuição em Firenze nao e preco de mercado "
                             "atacadista nem preco nacional"),
         "raw_sha256": SHA, "document_id": "NAO SEI",
         "prova_onde": "tabela «Prezzi di vendita», linha «Lamponi (12 rilevazioni)»",
         "item_id": "derived:911", "universo": "T10", "source_id": "IT-T10-018", "estado_da_fila": "WAITING"}
    b.update(kw)
    return b


def outro_item():
    t = "Mercato di Verona: mele Golden 1,20 euro/kg nella settimana 21-27 settembre 2026, secondo la borsa.\n"
    return item(ordem=5, item_id="derived:950", raw=1500, sha=hashlib.sha256(t.encode()).hexdigest(), texto=t)


def correr(itens, precos, **kw):
    return CI.correr("teste do preco no motor", itens, precos=precos, **kw)


class Positivo(unittest.TestCase):
    def test_a_linha_real_vira_um_objeto_do_motor(self):
        L = correr([item(), outro_item()], [linha()])
        self.assertEqual(L["RESULT_STATE"], "DONE", L["ERRORS"])
        self.assertEqual(L["PRECOS"]["OBJETOS"], 1, L["PRECOS"]["RECUSADOS"])
        o = L["OBJETOS_DE_MERCADO"][0]
        self.assertIs(L["ITENS_POR_FERRAMENTA"]["market"][0], o)
        c = o["CHAVES"]
        self.assertEqual((c["PRICE"], c["UNIT"], c["PERIOD"]), ("media 23,16 euro/kg", "euro/kg",
                                                                "2026-09-23/2026-09-23"))
        self.assertEqual(c["CULTURA_LITERAL"], "Lamponi")
        # nenhuma identidade cunhada; estagio de mercado nao inferido
        self.assertEqual((c["CROP_ID"], c["MARKET_PLACE_ID"], c["MARKET_STAGE"]), ("NAO SEI",) * 3)
        self.assertEqual(c["FACT_LOCATION"], "Firenze")
        self.assertIn("BATE com", c["FACT_TIME_BASIS"])
        p = o["PROVA"][0]
        self.assertEqual((p["ITEM_ID"], p["CORRIDA_UPSTREAM"], p["ORDEM"], p["RAW_SHA256"]),
                         ("derived:911", CORRIDA, 2, SHA))
        self.assertEqual(p["CITACAO"], CITACAO)
        self.assertLess(p["CITACAO_EM"], len(ARTIGO))
        self.assertEqual(o["ESPECIE"], "SINAL")
        self.assertEqual(o["INTELLIGENCE_RUN_ID"], L["INTELLIGENCE_RUN_ID"])
        self.assertEqual(o["G0_DO_ITEM"], "PASSOU")
        self.assertFalse(PORTA.conferir_ligacao(o["LIGACAO_ADAMA"]))

    def test_o_pote_do_dono_transporta_o_objeto_sem_recusa(self):
        import pote_intelligence_casco as POTE
        L = correr([item(), outro_item()], [linha()])
        ent = {k: v for k, v in L.items() if k != "SIGNALS"}
        ent.update({"SOURCE_HEAD": {"MOTOR": "teste"}, "CORTE": {"X": 1}, "SINTETICA": True, "GAPS": []})
        pote = POTE.adaptar(ent)
        objs = pote["COMPARTIMENTOS"]["market"]["OBJETOS"]
        self.assertEqual([o["OBJETO_ID"] for o in objs], [L["OBJETOS_DE_MERCADO"][0]["OBJETO_ID"]],
                         pote["RECUSADOS"])
        self.assertEqual((objs[0]["CHAVES"]["PRICE"], objs[0]["CHAVES"]["UNIT"]), ("media 23,16 euro/kg", "euro/kg"))
        self.assertFalse(POTE.conferir_pote(pote))

    def test_sem_precos_o_livro_e_o_de_antes(self):
        L = correr([item()], None)
        self.assertNotIn("PRECOS", L)
        self.assertNotIn("ITENS_POR_FERRAMENTA", L)
        self.assertEqual(CI.identidade_da_corrida("r", [item()], None),
                         CI.identidade_da_corrida("r", [item()], None, None))

    def test_armazem_confere_os_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "XX/it-t10-018/OBSERVATION/x.html")
            p.parent.mkdir(parents=True)
            p.write_bytes(BYTES)
            self.assertEqual(correr([item()], [linha()], armazem=d)["PRECOS"]["OBJETOS"], 1)
            p.write_bytes(BYTES + b" ")
            L = correr([item()], [linha()], armazem=d)
            self.assertEqual(L["PRECOS"]["OBJETOS"], 0)
            self.assertEqual(L["PRECOS"]["RECUSADOS"][0]["MOTIVO"], "RAW_BYTES_NAO_BATEM")


class Contraprovas(unittest.TestCase):
    def _recusa(self, itens, precos, motivo):
        L = correr(itens, precos)
        self.assertEqual(L["RESULT_STATE"], "DONE", L["ERRORS"])
        self.assertEqual(L["PRECOS"]["OBJETOS"], 0)
        self.assertEqual(L["OBJETOS_DE_MERCADO"], [])
        self.assertEqual([r["MOTIVO"] for r in L["PRECOS"]["RECUSADOS"]], [motivo], L["PRECOS"]["RECUSADOS"])
        return L

    def test_A_item_sem_linha_de_preco_nao_da_objeto(self):
        L = correr([item(), outro_item()], [])
        self.assertEqual((L["PRECOS"]["OBJETOS"], L["PRECOS"]["RECUSADOS"]), (0, []))
        # e a linha do 911 nao se cola ao outro item (ordem 5)
        L = self._recusa([outro_item()], [linha()], "PRECO_SEM_ITEM_NA_CORRIDA")
        # nem por ITEM_ID: mesma ordem noutra corrida upstream nao e o mesmo item
        self._recusa([item(CORRIDA="OUTRA-CORRIDA")], [linha()], "PRECO_SEM_ITEM_NA_CORRIDA")

    def test_B_linha_ligada_a_outro_raw(self):
        o = outro_item()
        self._recusa([item(), o], [linha(raw_sha256=o["RAW_SHA256"])], "RAW_DE_OUTRO_ITEM")
        self._recusa([item(), o], [linha(item_id="derived:950")], "PRECO_DE_OUTRO_ITEM")

    def test_C_sha_incompativel(self):
        self._recusa([item()], [linha(raw_sha256="0" * 64)], "SHA_INCOMPATIVEL")
        self._recusa([item()], [linha(raw_sha256="nao-e-sha")], "SHA_INVALIDO")
        self._recusa([item(RAW_SHA256="NAO SEI")], [linha()], "RAW_SHA256_DO_ITEM_NAO_SEI")

    def test_D_preco_so_no_relacionado_ou_no_rodape(self):
        rel = "lamponi a 23,16 euro/kg"
        self.assertIn(rel, RELACIONADO)
        self._recusa([item()], [linha(citacao_literal=rel, valor_texto="23,16 euro/kg")],
                     "CITACAO_SO_FORA_DO_ARTIGO")
        self._recusa([item()], [linha(citacao_literal="P.I/C.F. 01041460369 prezzo 9,99 euro/kg",
                                      valor_texto="9,99 euro/kg", cultura_literal="C.F.")],
                     "CITACAO_SO_FORA_DO_ARTIGO")
        # o mesmo preco no corpo DE OUTRO item nao e deste
        self._recusa([item(texto=ARTIGO.replace(CITACAO, "") + RELACIONADO)], [linha()], "CITACAO_FORA_DO_TEXTO")

    def test_E_reprocessar_o_mesmo_911_nao_duplica(self):
        a = correr([item(), outro_item()], [linha()])
        b = correr([copy.deepcopy(item()), outro_item()], [linha()])
        self.assertEqual(a["INTELLIGENCE_RUN_ID"], b["INTELLIGENCE_RUN_ID"])
        self.assertEqual([o["OBJETO_ID"] for o in a["OBJETOS_DE_MERCADO"]],
                         [o["OBJETO_ID"] for o in b["OBJETOS_DE_MERCADO"]])
        r = CI.correr("teste do preco no motor", [item(), outro_item()], precos=[linha()],
                      ja_corridas={a["INTELLIGENCE_RUN_ID"]: a})
        self.assertEqual(r["RESULT_STATE"], "REUSED")
        self.assertEqual(len(r["OBJETOS_DE_MERCADO"]), 1)
        # a linha repetida na vista nao vira dois objetos
        d = correr([item()], [linha(), linha()])
        self.assertEqual(d["PRECOS"]["OBJETOS"], 1)
        self.assertEqual([x["MOTIVO"] for x in d["PRECOS"]["DUPLICADOS"]], ["DUPLICADO"])

    def test_outra_linha_e_outra_corrida(self):
        a = correr([item()], [linha()])
        b = correr([item()], [linha(valor_texto="media 23,17 euro/kg")])
        self.assertNotEqual(a["INTELLIGENCE_RUN_ID"], b["INTELLIGENCE_RUN_ID"])
        self.assertNotEqual(a["INTELLIGENCE_RUN_ID"], correr([item()], None)["INTELLIGENCE_RUN_ID"])


class OQueALinhaDizTemDeEstarNaCitacao(unittest.TestCase):
    def test_valor_unidade_cultura_periodo_classe(self):
        casos = [(dict(valor_texto="media 99,99 euro/kg"), "VALOR_FORA_DA_CITACAO"),
                 (dict(unidade="euro/100kg"), "UNIDADE_FORA_DA_CITACAO"),
                 (dict(cultura_literal="Mirtilli"), "CULTURA_FORA_DA_CITACAO"),
                 (dict(periodo_inicio="2026-09-24", periodo_fim="2026-09-23"), "PERIODO_INVALIDO"),
                 (dict(periodo_inicio="2026-10-01", periodo_fim="2026-10-01"), "PERIODO_FUTURO"),
                 (dict(classe="SPOT"), "CLASSE_DESCONHECIDA"),
                 (dict(valor_texto="NAO SEI"), "LINHA_INCOMPLETA"),
                 (dict(citacao_literal="Lamponi (12 rilevazioni): media 99,99 euro/kg"), "CITACAO_FORA_DO_TEXTO")]
        for mud, motivo in casos:
            with self.subTest(motivo=motivo):
                L = correr([item()], [linha(**mud)])
                self.assertEqual([r["MOTIVO"] for r in L["PRECOS"]["RECUSADOS"]], [motivo])

    def test_item_sem_proveniencia(self):
        L = correr([item(RAW_OBSERVATION_ID="NAO SEI")], [linha()])
        self.assertEqual([r["MOTIVO"] for r in L["PRECOS"]["RECUSADOS"]], ["ITEM_SEM_PROVENIENCIA"])

    def test_praca_fora_do_artigo_fica_nao_sei(self):
        L = correr([item()], [linha(praca="Verona")])
        self.assertEqual(L["OBJETOS_DE_MERCADO"][0]["CHAVES"]["FACT_LOCATION"], "NAO SEI")

    def test_item_ambiguo(self):
        L = correr([item(), item(item_id="derived:911b")], [linha(item_id=None)])
        self.assertEqual([r["MOTIVO"] for r in L["PRECOS"]["RECUSADOS"]], ["PRECO_ITEM_AMBIGUO"])


if __name__ == "__main__":
    unittest.main()
