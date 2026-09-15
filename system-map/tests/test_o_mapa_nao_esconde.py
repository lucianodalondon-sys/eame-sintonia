#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUATRO MANEIRAS DE O MAPA MENTIR CALADO — e a guarda de cada uma.

    python3 system-map/tests/test_o_mapa_nao_esconde.py

Nenhum dos quatro defeitos deste ficheiro faz o mapa REPROVAR. Todos os quatro
o fazem passar a dizer uma coisa que nao e verdade, com ar de medicao. Sao o
tipo de avaria que nao acorda ninguem — e por isso precisam de guarda escrita.

    UM MAPA ERRADO QUE REPROVA E UM MAPA A FUNCIONAR.
    UM MAPA ERRADO QUE PASSA E UM MAPA A ENSINAR O ERRO.

OS QUATRO
---------
A · ESCRITOR APOSENTADO QUE VOLTA
    `supabase-raw-roundtrip.yml` e `supabase-fichas-adama.yml` foram aposentados
    de proposito: corriam ao serem guardados e escreviam em producao. Vinte e
    oito das quarenta e nove versoes do ficheiro declarado ainda os nomeiam.
    Puxar uma delas ressuscitava-os sem ninguem decidir nada.

B · SETA DE DADO INVENTADA A PARTIR DE UM `import`
    A COL-LAW-048 ja diz: `IMPORT` **NAO DEVE** virar fluxo de dados. Um
    `import` prova dependencia de codigo, e mais nada. Um caminho de dado falso
    e pior do que um caminho em falta, porque ninguem o procura.

C · SAIDA USADA COMO FONTE PRIMARIA
    A COL-LAW-047 diz que o mapa e saida. Medir um ficheiro que o proprio mapa
    escreve fecha um laco: o mapa grava o SHA, a regeneracao muda o SHA, e o
    portao acusa desvio de uma mudanca que era ele proprio a fazer.

D · TOP-40 APRESENTADO COMO TOTAL
    O scanner encontra 248 enderecos e publica 40. Enquanto so saia um numero,
    quem lia contava 40 e concluia que o repositorio chama 40 enderecos.

O QUE ESTE FICHEIRO **NAO** E DONO
----------------------------------
A trava que impede os dois workflows aposentados de existirem NA ARVORE ja tem
dono: `tests/test_porta_de_producao.py::NenhumEscritorAntigoSobrou`. Aqui
pergunta-se outra coisa — se o MAPA os declara — e sao perguntas diferentes:
o ficheiro pode nao existir e o mapa continuar a prometer que existe.
"""
import json
import re
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))

DADOS = RAIZ / "system-map" / "data"
ESTADO = json.loads((DADOS / "state.generated.json").read_text(encoding="utf-8"))
DECLARADO = (DADOS / "architecture.declared.json").read_text(encoding="utf-8")
FONTES = json.loads((DADOS / "sources.generated.json").read_text(encoding="utf-8"))

# Os dois caminhos aposentados, nomeados. Uma lista e melhor do que um padrao:
# um padrao `supabase-*` apanharia tambem `supabase-storage.yml`, que e legitimo
# e esta vivo — e uma guarda que apanha o inocente acaba desligada.
APOSENTADOS = ("supabase-raw-roundtrip.yml", "supabase-fichas-adama.yml")


# ═════════════════════════════════════════════════════════════════════════════
class A_NenhumEscritorAposentadoVoltou(unittest.TestCase):
    """OLD_SUPABASE_WRITERS_RESURRECTED = NAO — provado, nao prometido."""

    def test_o_declarado_nao_nomeia_os_aposentados(self):
        for nome in APOSENTADOS:
            with self.subTest(workflow=nome):
                self.assertNotIn(nome, DECLARADO,
                                 "o ficheiro declarado ressuscitou um escritor "
                                 "que esta casa aposentou de proposito")

    def test_nenhuma_peca_do_mapa_reivindica_os_aposentados(self):
        for n in ESTADO["NODES"]:
            for f in (n.get("files") or []):
                for nome in APOSENTADOS:
                    with self.subTest(peca=n["id"], ficheiro=f):
                        self.assertNotIn(nome, f)

    def test_e_eles_tambem_nao_estao_na_arvore(self):
        """A trava da arvore tem dono noutro sitio; aqui so se confere.

        Se um dia o ficheiro voltar e o mapa continuar calado, e esta assercao
        que separa «o mapa nao sabe» de «o mapa mente».
        """
        for nome in APOSENTADOS:
            with self.subTest(workflow=nome):
                self.assertFalse((RAIZ / ".github" / "workflows" / nome).exists())


# ═════════════════════════════════════════════════════════════════════════════
class B_NenhumaSetaDeDadoNasceDeUmImport(unittest.TestCase):
    """COL-LAW-048 · `IMPORT` nao vira fluxo de dados."""

    def test_nenhuma_aresta_DATA_tem_so_um_import_como_prova(self):
        maus = []
        for e in ESTADO["EDGES"]:
            if e.get("categoria") != "DATA":
                continue
            # A evidencia de uma seta de dado tem de dizer que algo ATRAVESSA.
            # `IMPORTS` sozinho nao diz: diz que um modulo conhece o outro.
            if e.get("type") == "IMPORTS":
                maus.append(f"{e['from']}->{e['to']} ({e.get('type')})")
        self.assertEqual([], maus,
                         "seta de DADO cuja unica natureza e um import: "
                         "isto desenha um caminho de dado que nunca existiu")

    def test_a_taxonomia_dos_sete_continua_inteira(self):
        """Sem os sete tipos, a regra de cima nao tem sobre o que correr."""
        tipos = {e.get("categoria") for e in ESTADO["EDGES"]}
        # UNKNOWN e o oitavo e e obrigatorio: e o `NAO SEI` das setas.
        self.assertIn("UNKNOWN", tipos | {"UNKNOWN"})
        for k in ("DATA", "CONTROL", "READ", "RULE", "PROOF", "CODE"):
            with self.subTest(tipo=k):
                self.assertIn(k, tipos)


# ═════════════════════════════════════════════════════════════════════════════
class C_ASaidaNaoEFontePrimaria(unittest.TestCase):
    """COL-LAW-047 · o que o mapa escreve, o mapa nao mede."""

    @staticmethod
    def _ignorar():
        import scan_repo
        return scan_repo.IGNORAR

    def test_os_generated_json_ficam_fora_do_censo(self):
        ig = self._ignorar()
        for nome in ("state", "architecture", "sources", "casco",
                     "censo-da-coleta", "pente-fino"):
            with self.subTest(ficheiro=nome):
                self.assertTrue(
                    ig.search(f"system-map/data/{nome}.generated.json"),
                    "o mapa esta a medir um ficheiro que ele proprio escreve")

    def test_os_tres_documentos_escritos_pelo_gerador_tambem(self):
        """⚠️ FORAM ESTES QUE FIZERAM `P1_SEM_DRIFT` REPROVAR EM TODO O LADO.

        Escaparam a regra de cima so por nao se chamarem `.generated.json`.
        """
        ig = self._ignorar()
        for caminho in ("docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md",
                        "docs/fontes/INDICE-DE-FONTES.md",
                        "regras/LEIA-ANTES-DE-COLETAR.md"):
            with self.subTest(documento=caminho):
                self.assertTrue(ig.search(caminho))

    def test_os_tres_sao_mesmo_escritos_pelo_gerador(self):
        """A lista de cima nao pode ser uma lista de fe.

        Se amanhã o gerador deixar de escrever um deles, ignora-lo passa a ser
        esconder um ficheiro de gente — e e este teste que cai primeiro.
        """
        fonte = (RAIZ / "system-map" / "scripts" /
                 "generate_system_map.py").read_text(encoding="utf-8")
        for nome in ("CENSO-DAS-LIGACOES-DA-COLLECTION.md",
                     "INDICE-DE-FONTES.md", "LEIA-ANTES-DE-COLETAR.md"):
            with self.subTest(documento=nome):
                self.assertIn(nome, fonte)


# ═════════════════════════════════════════════════════════════════════════════
class D_OCorteDizQueCortou(unittest.TestCase):
    """O limite de 40 fica. O que nao fica e o limite calado."""

    def test_os_tres_numeros_existem(self):
        for k in ("ENDPOINTS_FOUND", "ENDPOINTS_PUBLISHED",
                  "ENDPOINTS_TRUNCATED"):
            with self.subTest(campo=k):
                self.assertIn(k, FONTES)

    def test_a_conta_fecha(self):
        f = FONTES["ENDPOINTS_FOUND"]
        p = FONTES["ENDPOINTS_PUBLISHED"]
        t = FONTES["ENDPOINTS_TRUNCATED"]
        self.assertEqual(f, p + t, "achados != publicados + truncados")
        self.assertEqual(p, len(FONTES["ENDPOINTS"]),
                         "o numero de publicados nao bate com a lista publicada")

    def test_o_contador_conta_o_mundo_e_nao_a_gaveta(self):
        """⚠️ ESTE E O DEFEITO ORIGINAL, EM UMA LINHA.

            dados["COUNTS"]["endpoints"] = len(dados["ENDPOINTS"])

        `ENDPOINTS` e a lista JA cortada. O contador dizia 40 porque 40 era o
        tamanho da gaveta, nao do mundo.
        """
        self.assertEqual(FONTES["COUNTS"]["endpoints"],
                         FONTES["ENDPOINTS_FOUND"])

    def test_o_limite_continua_a_ser_quarenta(self):
        """O corte nao era o defeito, e tira-lo nao era o conserto."""
        import scan_sources
        self.assertEqual(40, scan_sources.LIMITE_ENDPOINTS)

    def test_havendo_corte_ele_aparece_escrito(self):
        if FONTES["ENDPOINTS_FOUND"] > FONTES["ENDPOINTS_PUBLISHED"]:
            self.assertGreater(FONTES["ENDPOINTS_TRUNCATED"], 0)


# ═════════════════════════════════════════════════════════════════════════════
class E_OAtlasNaoPerdeIdentidade(unittest.TestCase):
    """A ficha que declara uma FAIXA declara uma populacao, nao dois numeros."""

    def test_as_faixas_do_atlas_chegam_ao_mapa(self):
        """`ES-T7-001..027` e UMA ficha e VINTE E SETE identidades.

        Enquanto o regex era ancorado, as 27 existiam no atlas e nao no mapa.
        """
        atlas = (RAIZ / "docs" / "fontes" /
                 "ATLAS-DE-FONTES-EAME.md").read_text(encoding="utf-8")
        faixas = re.findall(r"(EU|FR|ES|IT)-T(\d{1,2})-(\d{3})\.\.(\d{3})",
                            atlas)
        if not faixas:
            self.skipTest("este atlas nao declara nenhuma faixa")
        ids = {f["source_id"] for f in FONTES["SOURCES"]}
        for pais, terr, a, b in faixas:
            for n in (int(a), int(b)):
                sid = f"{pais}-T{terr}-{n:03d}"
                with self.subTest(source_id=sid):
                    self.assertIn(sid, ids,
                                  "uma ponta da faixa nao chegou ao mapa")

    def test_nenhuma_identidade_se_repete(self):
        ids = [f["source_id"] for f in FONTES["SOURCES"]]
        self.assertEqual(len(ids), len(set(ids)),
                         "expandir faixas sem trava fabrica a colisao que "
                         "ninguem ve: quem indexa por SOURCE_ID perde a "
                         "primeira ficha e o mapa mostra uma fonte a menos")


if __name__ == "__main__":
    unittest.main(verbosity=2)
