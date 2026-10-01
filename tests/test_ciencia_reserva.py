# -*- coding: utf-8 -*-
"""FEEDER-4-LINHAS · ADENDO-RESERVA (01/10/2026): TODO pedido de rede da linha CIENCIA reserva no livro de 24 h.

A falha medida (entrega FEEDER-4-LINHAS, NAO SEI 3, conferida pelo coordenador): em `coleta/pesquisadores_t6.py`
so a porta do OpenAlex (`_pedir`) reservava; os pedidos ao Crossref e ao ORCID iam por `CP._get` direto, nas
duas rodadas (`rodada_com_rede` e `rodada_consulta2`). E a sonda (`sonda_ligacao_linha.py --linha=CIENCIA`)
so exercitava `_pedir` — dava LIGADA com metade das portas sem reserva.

E uma segunda, achada no caminho: `_pedir` reservava e NUNCA registava a resposta. A politica (D124) e um
pedido de cada vez por dominio: a reserva segura o dominio ate a RESPOSTA ou ate LEASE_S (150 s). Com as
rodadas a 3 s entre pedidos, o 2.o pedido ao mesmo dominio saia ADIADO (UM_DE_CADA_VEZ): 1 pedido por
dominio por rodada.

Zero rede: `CP._get` e trocado por um falso que, no instante de cada pedido, le o livro da cortesia
(temporario) e confere que ESTE pedido tem a sua RESERVA escrita antes dele.

    py -3.12 -m unittest tests.test_ciencia_reserva
"""
import json
import os
import subprocess
import sys
import tempfile
import shutil
import unittest
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "coleta"))
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import cortesia_adaptativa as CA  # noqa: E402
import pesquisadores_t6 as T6  # noqa: E402

DOIS = ["10.1000/a", "10.1000/b", "10.1000/c"]
ORCIDS = ["0000-0001-0000-0001", "0000-0001-0000-0002", "0000-0001-0000-0003"]


class _RedeFalsa:
    """O papel de `CP._get`: nada sai. Cada chamada confere no livro que o pedido foi reservado antes."""

    def __init__(self, livro: Path):
        self.livro = livro
        self.chamadas = []
        self.sem_reserva = []

    def __call__(self, url, headers=None):
        host = urllib.parse.urlsplit(url).hostname or ""
        dom = CA.dominio(host)
        feitas = sum(1 for c in self.chamadas if c["DOMINIO"] == dom) + 1
        ev = CA.ler_eventos(self.livro) if self.livro.exists() else []
        reservas = sum(1 for e in ev if e["TIPO"] == "RESERVA" and e["DOMINIO"] == dom)
        self.chamadas.append({"DOMINIO": dom, "URL": url})
        if reservas < feitas:
            self.sem_reserva.append({"DOMINIO": dom, "URL": url[:120], "RESERVAS": reservas, "PEDIDOS": feitas})
        if "crossref" in host:
            return {"message": {"items": []}}, None
        if "orcid" in host:
            return {"group": []}, None
        return {"meta": {"count": 0}, "results": []}, None


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ciencia-reserva-"))
        self.livro = self.tmp / "LIVRO-CORTESIA.ndjson"
        self.saida = self.tmp / "rede"
        self.saida.mkdir()
        self.env = dict(os.environ)
        for k in [k for k in os.environ if k.startswith("SINTONIA_")]:
            del os.environ[k]
        # a pausa minima das APIs a 0 numa COPIA da politica (a pausa mede-se em test_cortesia_adaptativa.py)
        pol = json.loads(CA.POLITICA_F.read_text(encoding="utf-8"))
        for d in pol["CLASSES"]["API_COM_LIMITE_PUBLICADO"]["DOMINIOS"].values():
            d["PAUSA_MINIMA_S"] = 0
        (self.tmp / "POLITICA.json").write_text(json.dumps(pol), encoding="utf-8")
        os.environ["SINTONIA_CORTESIA_POLITICA"] = str(self.tmp / "POLITICA.json")
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(self.livro)
        os.environ["SINTONIA_TETO_POR_HOST"] = "2"
        CA.politica(recarregar=True)
        self.rede = _RedeFalsa(self.livro)
        self.antes = {k: getattr(T6, k) for k in ("ler_pasta", "consultas")}
        self.get_antes = T6.CP._get
        T6.CP._get = self.rede
        T6.ler_pasta = lambda saida, com_provas=True: ([{"DOI": d} for d in DOIS], [], [{"ORCID": o} for o in ORCIDS])
        T6.consultas = lambda: [{"PAR": "vite x peronospora", "URL": "https://api.openalex.org/works?filter=a"},
                                {"PAR": "melo x afidi", "URL": "https://api.openalex.org/works?filter=b"}]

    def tearDown(self):
        T6.CP._get = self.get_antes
        for k, v in self.antes.items():
            setattr(T6, k, v)
        os.environ.clear()
        os.environ.update(self.env)
        CA.politica(recarregar=True)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def por_dominio(self):
        out = {}
        for c in self.rede.chamadas:
            out[c["DOMINIO"]] = out.get(c["DOMINIO"], 0) + 1
        return out

    def conferir(self):
        self.assertEqual(self.rede.sem_reserva, [], "pedido(s) de rede SEM reserva no livro de 24 h")
        # nao passar por vazio: as tres portas foram de facto usadas
        self.assertEqual(set(self.por_dominio()), {"openalex.org", "crossref.org", "orcid.org"}, self.por_dominio())
        ev = CA.ler_eventos(self.livro)
        for dom, n in self.por_dominio().items():
            res = sum(1 for e in ev if e["TIPO"] == "RESERVA" and e["DOMINIO"] == dom)
            resp = sum(1 for e in ev if e["TIPO"] == "RESPOSTA" and e["DOMINIO"] == dom)
            self.assertEqual((res, resp), (n, n), "%s: %d pedidos, %d reservas, %d respostas" % (dom, n, res, resp))


class TodaARedeReserva(Base):
    def test_rodada_com_rede_cada_pedido_tem_a_sua_reserva(self):
        T6.rodada_com_rede(1, str(self.saida), pausa=0)
        self.conferir()

    def test_rodada_consulta2_cada_pedido_tem_a_sua_reserva(self):
        est = {"PESSOAS": {p: {"IDS": ["https://openalex.org/A%d" % i],
                               "CANDIDATOS": [{"ORCID": ORCIDS[i % len(ORCIDS)]}]}
                           for i, (p, _) in enumerate(T6.PESSOAS_CONSULTA2)},
               "OBRAS_FEITAS": [], "ORCID_FEITOS": [], "CROSSREF_DOIS_FEITOS": [], "RODADAS": []}
        (self.saida / "ESTADO-CONSULTA2.json").write_text(json.dumps(est), encoding="utf-8")
        T6.rodada_consulta2(2, str(self.saida), pausa=0)
        self.conferir()

    def test_a_resposta_fecha_a_reserva_e_a_rodada_faz_mais_de_um_pedido_por_dominio(self):
        # com o teto 2, a rodada faz 2 pedidos a cada dominio — so possivel se o 1.o fechou a reserva
        T6.rodada_com_rede(1, str(self.saida), pausa=0)
        self.assertEqual(self.por_dominio(), {"openalex.org": 2, "crossref.org": 1, "orcid.org": 2})

    def test_sem_reserva_o_pedido_nao_sai(self):
        # o livro diz que o crossref esta em pausa de 24 h (2 sinais): nenhum pedido ao crossref sai
        agora = CA.time.time()
        self.livro.write_text("".join(json.dumps({"TIPO": "RESPOSTA", "DOMINIO": "crossref.org", "EM": agora - 10 + i,
                                                  "RUN_ID": "T", "LINHA": "T", "SINAIS": ["HTTP_429"], "STATUS": 429,
                                                  "HOST": "api.crossref.org"}) + "\n" for i in (1, 2)),
                              encoding="utf-8")
        T6.rodada_com_rede(1, str(self.saida), pausa=0)
        self.assertNotIn("crossref.org", self.por_dominio())
        self.assertEqual(self.rede.sem_reserva, [])


class SondaDasPortas(unittest.TestCase):
    """A sonda passa a exercitar TODAS as portas de rede da linha, cada uma contra o seu livro temporario."""

    def test_a_sonda_da_ciencia_mede_cada_porta(self):
        r = subprocess.run([sys.executable, str(RAIZ / "ferramentas" / "big_collection" / "sonda_ligacao_linha.py"),
                            "--linha=CIENCIA"], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=300,
                           env={k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")})
        m = json.loads((r.stdout.strip().splitlines() or ["{}"])[-1])
        portas = (m.get("MEDIDO") or {}).get("PORTAS") or {}
        self.assertEqual(set(portas), set(T6.PORTAS_DE_REDE), m)
        self.assertEqual(set(portas), {"OPENALEX", "CROSSREF", "ORCID"})
        for nome, p in portas.items():
            self.assertEqual(p["RESERVAS_LIVRES"], 1, (nome, p))
            self.assertEqual(p["RESERVAS_NOVAS_B"], 0, (nome, p))
            self.assertTrue(p["RECUSOU_B"], (nome, p))
        self.assertIs(m["LIGADA"], True, m)

    def test_uma_porta_que_nao_reserva_desliga_a_linha(self):
        import sonda_ligacao_linha as S
        env = dict(os.environ)
        antes = T6.PORTAS_DE_REDE["CROSSREF"]
        saida = []
        T6.PORTAS_DE_REDE["CROSSREF"] = lambda host: T6.CP._get("http://%s/works?filter=doi:10.1000/a" % host)
        try:
            import builtins
            p0 = builtins.print
            builtins.print = lambda *a, **k: saida.append(" ".join(map(str, a)))
            try:
                S.main(["--linha=CIENCIA"])
            finally:
                builtins.print = p0
        finally:
            T6.PORTAS_DE_REDE["CROSSREF"] = antes
            os.environ.clear()
            os.environ.update(env)
            CA.politica(recarregar=True)
        m = json.loads(saida[-1])
        self.assertIs(m["LIGADA"], False, m)
        self.assertIn("CROSSREF", m["PORQUE"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
