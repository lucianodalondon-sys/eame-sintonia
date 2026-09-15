#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DA IDENTIDADE DE FONTE — SOURCE_ID

    UM IDENTIFICADOR REPETIDO É PIOR DO QUE NENHUM: ELE FAZ DUAS FONTES
    PARECEREM UMA.

O `SOURCE_ID` é a identidade canônica de uma fonte. O atlas
(`docs/fontes/ATLAS-DE-FONTES-EAME.md`) declara-se dono dele e documenta a
convenção `<PAÍS>-<TERRITÓRIO>-<sequencial>`, com uma regra explícita: **o ID,
uma vez atribuído, não é reciclado**.

Medido em 2026-09-14, antes destes testes existirem: não havia nenhuma
verificação de colisão. `system-map/scripts/scan_sources.py` indexa as fichas
por `fora[SOURCE_ID] = ...` — um ID repetido **sobrescreveria em silêncio**, e
o mapa mostraria uma fonte a menos sem acusar erro nenhum.

Pior: dos 56 `SOURCE_ID` italianos em uso no repositório, só 3 eram ficha no
atlas. Os outros 53 foram cunhados por `candidatas/ITALY-SOURCE-MASTER-V1.json`
e estão presos a contratos (`regras/italy_contracts.mjs`) e a pastas de
evidência (`data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`). Quem alocasse «o
próximo número» lendo só o atlas colidiria de imediato.

Estes testes existem para que a próxima pessoa não descubra isso tarde.

Corre como os outros testes desta casa:  py tests/test_source_id.py
"""
import json
import os
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
MASTER_IT = RAIZ / "candidatas" / "ITALY-SOURCE-MASTER-V1.json"
EVIDENCIA = RAIZ / "data" / "samples" / "IT-SOURCE-SAMPLES"

# A mesma expressão que `system-map/scripts/scan_sources.py` usa para aceitar
# uma ficha. Se as duas divergirem, o mapa e estes testes deixam de falar da
# mesma coisa.
RE_ID = re.compile(r"^(EU|FR|ES|IT)-T\d{1,2}-\d{3}$")
RE_ID_SOLTO = re.compile(r"\b(EU|FR|ES|IT)-T\d{1,2}-\d{3}\b")

BINARIOS = {".png", ".jpg", ".jpeg", ".pdf", ".xlsx", ".woff", ".woff2",
            ".ico", ".zip", ".gz", ".mp4"}


def ids_do_atlas():
    """Os SOURCE_ID que são FICHA no atlas — o dono declarado.

    Uma ficha pode cobrir mais de uma fonte, e o atlas escreve isso na mesma
    linha: `FR-T9-001 / ES-T9-001 / IT-T9-001 (mesma natureza)`. A expansão
    segue a mesma regra de `tests/test_canonico.py::source_ids`, para que os
    dois ficheiros não falem de populações diferentes.
    """
    texto = ATLAS.read_text(encoding="utf-8")
    ids = []
    for m in re.finditer(r"^SOURCE_ID:\s+(\S[^\n#]*)", texto, re.M):
        cru = m.group(1).strip()
        if cru.startswith("#") or "<" in cru:      # linha de template
            continue
        cru = re.sub(r"\(.*?\)", "", cru)
        for parte in re.split(r"[·/]", cru):
            parte = parte.strip()
            if RE_ID.match(parte):
                ids.append(parte)
    return ids


def ids_do_master_italiano():
    """Os SOURCE_ID cunhados fora do atlas, mas em uso operacional."""
    if not MASTER_IT.exists():
        return []
    d = json.loads(MASTER_IT.read_text(encoding="utf-8"))
    return [s["SOURCE_ID"] for s in d.get("sources", [])
            if RE_ID.match(str(s.get("SOURCE_ID", "")))]


def ids_com_pasta_de_evidencia():
    if not EVIDENCIA.is_dir():
        return []
    return [p.name for p in EVIDENCIA.iterdir() if RE_ID.match(p.name)]


def ids_em_uso_no_repositorio():
    """Toda a população, onde quer que viva. É contra ISTO que se aloca."""
    achados = set()
    for raiz, dirs, ficheiros in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        for f in ficheiros:
            if Path(f).suffix.lower() in BINARIOS:
                continue
            try:
                t = (Path(raiz) / f).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            achados.update(m.group(0) for m in RE_ID_SOLTO.finditer(t))
    return achados


class OAtlasNaoRepeteIdentidade(unittest.TestCase):

    def test_nenhum_source_id_duplicado_no_atlas(self):
        ids = ids_do_atlas()
        repetidos = sorted({i for i, n in Counter(ids).items() if n > 1})
        self.assertEqual([], repetidos,
                         f"SOURCE_ID repetido no atlas: {repetidos}. O scanner indexa "
                         "por SOURCE_ID — o segundo apagaria o primeiro em silêncio.")

    def test_toda_linha_de_source_id_rende_pelo_menos_um_id_valido(self):
        """Uma linha que não rende nenhum ID é uma ficha que o scanner ignora.

        O atlas permite linhas compostas e intervalos (`ES-T7-001..027`); o que
        não pode existir é uma linha de ficha da qual não se consiga extrair
        identidade nenhuma.
        """
        texto = ATLAS.read_text(encoding="utf-8")
        mudas = []
        for m in re.finditer(r"^SOURCE_ID:\s+(\S[^\n#]*)", texto, re.M):
            cru = m.group(1).strip()
            if cru.startswith("#") or "<" in cru:
                continue
            if not RE_ID_SOLTO.search(cru):
                mudas.append(cru)
        self.assertEqual([], mudas,
                         f"linhas SOURCE_ID sem identidade extraível: {mudas}")

    def test_o_atlas_nao_colide_com_os_ids_cunhados_fora_dele(self):
        """A colisão que esta casa quase cometeu.

        O atlas tem 3 IDs italianos; o master italiano tem 54. Alocar «o
        próximo» lendo só o atlas escolheria um número já ocupado lá fora.
        """
        atlas = set(ids_do_atlas())
        fora = set(ids_do_master_italiano())
        colisao = sorted(atlas & fora)
        for sid in colisao:
            with self.subTest(source_id=sid):
                # Coincidir é legítimo quando é a MESMA fonte. Só se acusa
                # conflito quando os dois lados declaram URLs e elas divergem —
                # ficha sem URL é lacuna de preenchimento, não colisão.
                conflito = self._urls_divergem(sid)
                self.assertFalse(conflito,
                                 f"{sid} está no atlas E no master italiano apontando "
                                 f"para fontes diferentes: {conflito}")

    def _urls_divergem(self, sid):
        texto = ATLAS.read_text(encoding="utf-8")
        bloco = re.search(rf"^SOURCE_ID:\s+{re.escape(sid)}\b(.*?)(?=^SOURCE_ID:|\Z)",
                          texto, re.M | re.S)
        url_atlas = ""
        if bloco:
            m = re.search(r"^URL:\s+(\S+)", bloco.group(1), re.M)
            url_atlas = (m.group(1) if m else "").rstrip("/")
        d = json.loads(MASTER_IT.read_text(encoding="utf-8"))
        url_master = next((s.get("URL", "") for s in d.get("sources", [])
                           if s.get("SOURCE_ID") == sid), "").rstrip("/")
        def n(u):
            return re.sub(r"^https?://(www\.)?", "", (u or "").lower()).rstrip("/")
        if not url_atlas or not url_master:
            return None          # lacuna de campo, não conflito de identidade
        if n(url_atlas) == n(url_master) or n(url_master).startswith(n(url_atlas)) \
           or n(url_atlas).startswith(n(url_master)):
            return None
        return f"atlas={url_atlas} master={url_master}"

    def test_pasta_de_evidencia_pertence_a_um_source_id_conhecido(self):
        """Uma pasta `IT-Tx-NNN/` sem dono é evidência órfã."""
        conhecidos = set(ids_do_atlas()) | set(ids_do_master_italiano())
        orfas = sorted(set(ids_com_pasta_de_evidencia()) - conhecidos)
        self.assertEqual([], orfas,
                         f"pastas de evidência sem SOURCE_ID correspondente: {orfas}")


class AAlocacaoDeIdentidadeEhSegura(unittest.TestCase):
    """O que uma missão que atribui SOURCE_ID novo tem de respeitar."""

    def test_nenhum_id_em_uso_aparece_duas_vezes_com_donos_diferentes(self):
        atlas = Counter(ids_do_atlas())
        master = Counter(ids_do_master_italiano())
        for sid, n in master.items():
            with self.subTest(source_id=sid):
                self.assertEqual(1, n, f"{sid} repetido dentro do master italiano")
        for sid, n in atlas.items():
            with self.subTest(source_id=sid):
                self.assertEqual(1, n, f"{sid} repetido dentro do atlas")

    def test_a_alocacao_tem_de_olhar_a_populacao_inteira(self):
        """Trava de método: o atlas NÃO é a população completa.

        Se um dia passar a ser — porque o master foi fundido nele — este teste
        cai, e a mensagem diz o que mudou. Enquanto não cair, quem alocar tem
        de usar a união, nunca o atlas isolado.
        """
        atlas = set(ids_do_atlas())
        todos = ids_em_uso_no_repositorio()
        fora = todos - atlas
        self.assertTrue(fora,
                        "já não há SOURCE_ID em uso fora do atlas — o registo deixou "
                        "de estar partido. Reveja a regra de alocação: a partir de "
                        "agora o atlas pode ser a população completa.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
