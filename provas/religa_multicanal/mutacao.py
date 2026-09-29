"""RELIGA-MULTICANAL · o ataque: cada defeito plantado, um de cada vez, numa COPIA — e os testes tem de o apanhar.

    py provas/religa_multicanal/mutacao.py [--ref=HEAD] [--so=NOME,NOME]

A copia sai de `git archive <ref>` (o repositorio NAO e tocado). Cada mutante troca UM trecho exacto de um
ficheiro; um trecho que nao exista, ou que exista mais do que uma vez, falha alto (`NAO_APLICOU`) —

    UM MUTANTE QUE NAO MUDA NADA NAO PROVA NADA, e um que passa despercebido conta como teste forte
    sem o ser. Por isso a aplicacao e conferida antes de se correr o que quer que seja.

Cada mutante corre SO os testes que o DEVEM apanhar. MORTO = algum reprova. Resultado em
`provas/religa_multicanal/MUTACAO.json`.

Os defeitos que esta missao pode mesmo cometer, e que este ataque planta:
  · a identidade do canal deixa de ser conferida, ou passa a ler-se do ITEM (a fechadura que nunca tranca);
  · o feed barrado por robots volta a ser alcancavel;
  · zero alvos passa a valer como colheita boa;
  · o SOURCE_ID ausente passa a ser inventado;
  · as listas que o Curator EXCLUIU passam a alimentar linhas;
  · o video do LinkedIn DESCOBERTO passa a contar como video adquirido;
  · o post individual do LinkedIn passa a ser pedido (FETCH_POST esta fechado);
  · a coorte congelada da SITES passa a ser esmagada pela lista do Curator;
  · a porta do contador deixa de reservar, reserva depois, ou nao regista a resposta;
  · as duas rotas do googleapis voltam a partilhar orcamento.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from concurrent.futures import ThreadPoolExecutor

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RM = "coleta/rotas_multicanal.py"
FM = "ferramentas/big_collection/fontes_multicanal.py"
OL = "ferramentas/big_collection/onda_linha.py"
CC = "ferramentas/big_collection/coleta_continua.py"
PORTA = "coleta/reserva_24h.py"
CA = "coleta/cortesia_adaptativa.py"
CP = "coleta/corpus_pesquisador.py"


def U(*mods):
    return [sys.executable, "-m", "unittest"] + ["tests.%s" % m for m in mods]


T = U("test_religa_multicanal")

RESERVA = ("    r = _CA.reservar_ou_esperar(host, run_id=run_id, linha=linha, crawl_delay_s=crawl_delay_s,\n"
           "                                espera_max_s=espera_max_s, url=url)\n")

MUTANTES = [
    # ── YOUTUBE: a identidade ─────────────────────────────────────────────────────────────────────
    ("M01_YT_NAO_CONFERE_A_IDENTIDADE", RM,
     "    if not bate:\n", "    if False:\n", T),
    ("M02_YT_IDENTIDADE_TOLERA_QUALQUER_CANAL", RM,
     "    bate = channel_id in declarados or bool(canonical and channel_id in canonical.group(1))",
     "    bate = True", T),
    ("M03_YT_IDENTIDADE_SO_PELO_CANONICO_AUSENTE", RM,
     "    bate = channel_id in declarados or bool(canonical and channel_id in canonical.group(1))",
     "    bate = channel_id in declarados or canonical is None", T),
    ("M04_YT_ACEITA_CHANNEL_ID_MALFORMADO", RM,
     '    if not isinstance(channel_id, str) or not RE_CHANNEL_ID.match(channel_id or ""):',
     "    if False:", T),
    ("M05_YT_ZERO_VIDEOS_PASSA_COMO_COLHEITA", RM,
     "    if not ids:\n", "    if False:\n", T),
    ("M06_YT_ACEITA_STATUS_DIFERENTE_DE_200", RM,
     '    if r.get("ERRO") or r.get("STATUS") != 200:\n        return {"ERRO": "a pagina publica do canal',
     '    if False:\n        return {"ERRO": "a pagina publica do canal', T),
    ("M07_YT_ROTA_PELO_FEED_BARRADO", RM,
     '    url = "https://www.youtube.com/channel/%s/videos" % channel_id',
     '    url = "https://www.youtube.com/feeds/videos.xml?channel_id=%s" % channel_id', T),
    ("M08_YT_MAX_ALVOS_IGNORADO", RM,
     "    limite = max_alvos if max_alvos is not None else len(ids)", "    limite = len(ids)", T),
    ("M09_YT_INVENTA_TRANSPORTE_QUANDO_FALTA", RM,
     '    if not callable(buscar):\n        return {"ERRO": "SEM_TRANSPORTE: esta rota nao inventa transporte", "PEDIDOS": 0}\n'
     "    # A rota e construida AQUI",
     "    # A rota e construida AQUI", T),
    # ── INSTAGRAM: o que a D22 abre e o que a D19 fecha ───────────────────────────────────────────
    ("M10_IG_ACEITA_A_CONTA_COMO_REEL", RM,
     '    m = RE_IG_SHORTCODE.search(str(url or ""))\n    if not m:', "    m = RE_IG_SHORTCODE.search(str(url or ''))\n    if False:", T),
    ("M11_IG_ZERO_REELS_VIRA_ERRO", RM,
     '    codigos = list(dict.fromkeys(RE_IG_SHORTCODE.findall(html)))',
     '    codigos = list(dict.fromkeys(RE_IG_SHORTCODE.findall(html)))\n'
     '    if not codigos:\n        return {"ERRO": "sem reels", "PEDIDOS": 1}', T),
    ("M12_IG_LISTA_PELO_PERFIL_E_NAO_PELO_EMBED", RM,
     '    url = "https://www.instagram.com/%s/embed/" % handle',
     '    url = "https://www.instagram.com/%s/" % handle', T),
    # ── LINKEDIN: descoberto != adquirido ─────────────────────────────────────────────────────────
    ("M13_LI_VIDEO_DESCOBERTO_VIRA_ADQUIRIDO", OL,
     '        registo["VIDEO_BYTES_ACQUIRED"] = False\n',
     '        registo["VIDEO_BYTES_ACQUIRED"] = True\n', T),
    ("M14_LI_PEDE_O_POST_INDIVIDUAL", OL,
     '        return {"BYTES": corpo, "URL": a.get("URL_DO_POST"), "MEDIA_TYPE": "application/json",\n'
     '                "PEDIDOS": 0,',
     '        return {"BYTES": corpo, "URL": a.get("URL_DO_POST"), "MEDIA_TYPE": "application/json",\n'
     '                "PEDIDOS": 1,', T),
    ("M15_LI_CARTAO_VAZIO_VIRA_ITEM", OL,
     '        if not registo.get("URL_DO_POST") and not registo.get("NATIVE_ID"):\n',
     "        if False:\n", T),
    # ── A ALIMENTACAO ─────────────────────────────────────────────────────────────────────────────
    ("M16_ALIMENTA_PELAS_LISTAS_EXCLUIDAS", FM,
     '    "YOUTUBE": ["YOUTUBE"],', '    "YOUTUBE": ["YOUTUBE", "YOUTUBE_FORA"],', T),
    ("M17_SOURCE_ID_AUSENTE_E_INVENTADO", FM,
     '        base["SOURCE_ID"] = sid                                    # fica como o Curator o escreveu, ou None\n'
     '        base["SOURCE_STATUS"] = "NAO_REGISTRADA_PENDENTE_PORTA_CANONICA"',
     '        base["SOURCE_ID"] = "GERADO-%s-%03d" % (linha, n)\n'
     '        base["SOURCE_STATUS"] = "REGISTRADA"', T),
    ("M18_YT_SEM_CHANNEL_ID_ENTRA_A_MESMA", FM,
     "        if not cid:\n            return None", "        if not cid:\n            pass", T),
    ("M19_PESSOAS_DO_LINKEDIN_ENTRAM_SEMPRE", FM,
     '        if linha == "LINKEDIN" and com_pessoas:', '        if linha == "LINKEDIN":', T),
    ("M20_A_CANDIDATA_PERDE_A_LINHA", FM,
     '        return {"SOURCE_ID": cid or "BUSCA-%03d" % n, "LINHA": linha,',
     '        return {"SOURCE_ID": cid or "BUSCA-%03d" % n, "LINHA": None,', T),
    ("M21_REELS_PROVADOS_NAO_VIAJAM", FM,
     '                        "REELS_CONHECIDOS": [r for r in (x.get("REELS_JA_NO_REPOSITORIO") or [])\n'
     "                                             if isinstance(r, str)],",
     '                        "REELS_CONHECIDOS": [],', T),
    # ── O ORQUESTRADOR ────────────────────────────────────────────────────────────────────────────
    ("M22_SITES_PASSA_A_USAR_O_EXECUTOR_DE_LINHA", CC,
     '    {"LINHA": "SITES", "FAMILIA": "sites e boletins (T2/T3/T5/T7/T8/T9/T10/T12), pela coorte congelada",\n'
     '     "TRANSPORTE": "coleta/italy_pilot_collect.mjs", "SONDA": "ferramentas/big_collection/sonda_ligacao_sites.mjs"},',
     '    {"LINHA": "SITES", "FAMILIA": "sites e boletins (T2/T3/T5/T7/T8/T9/T10/T12), pela coorte congelada",\n'
     '     "TRANSPORTE": "coleta/italy_pilot_collect.mjs", "SONDA": "ferramentas/big_collection/sonda_ligacao_sites.mjs",\n'
     '     "EXECUTOR": "LINHA"},', T),
    ("M23_PESQUISADORES_REAPONTADA_SEM_RECONCILIAR", CC,
     '     "TRANSPORTE": "coleta/seguir.py", "CHAMADA": "reserva_24h.reservar("},',
     '     "TRANSPORTE": "ferramentas/seguir_pesquisadores/seguir.py", "CHAMADA": "reserva_24h.reservar("},', T),
    ("M24_UM_CANAL_SAI_DA_CAMPANHA", CC,
     '    {"LINHA": "LINKEDIN", "FAMILIA": "pagina publica de ORGANIZACAO (D23); FETCH_POST continua fechado",\n'
     '     "TRANSPORTE": "coleta/rotas_multicanal.py", "SONDA_PY": "LINKEDIN", "EXECUTOR": "LINHA"},', "", T),
    # ── A PORTA DO CONTADOR ───────────────────────────────────────────────────────────────────────
    ("M25_PORTA_PEDE_SEM_RESERVA", PORTA, RESERVA,
     '    r = {"ESTADO": "RESERVADO", "DOMINIO": host}\n', T),
    ("M26_PORTA_IGNORA_O_ADIADO", PORTA,
     '    if r["ESTADO"] != "RESERVADO":\n        return r, None\n',
     "    if False:\n        return r, None\n", T),
    ("M27_PORTA_RESERVA_DEPOIS_DO_PEDIDO", PORTA, RESERVA,
     "    _cedo = tuple(fazer())\n    fazer = lambda: _cedo\n" + RESERVA, T),
    ("M28_PORTA_NAO_REGISTA_A_RESPOSTA", PORTA,
     "    _CA.registrar_resposta(host, int(st or 0), dict(cab or {}), marcas=marcas, url=url, corpo=corpo,",
     "    (lambda *a, **k: None)(host, int(st or 0), dict(cab or {}), marcas=marcas, url=url, corpo=corpo,", T),
    ("M29_PORTA_NAO_REGISTA_A_FALHA", PORTA,
     '        _CA.registrar_resposta(host, int(getattr(ex, "code", 0) or 0), dict(cab.items()) if cab else None,',
     '        (lambda *a, **k: None)(host, int(getattr(ex, "code", 0) or 0), dict(cab.items()) if cab else None,', T),
    ("M30_PORTA_TAPA_QUALQUER_DOMINIO", PORTA,
     "        return k is not None and _CA.dominio_do_pedido(host, url) == k", "        return k is not None", T),
    ("M31_AS_DUAS_ROTAS_PARTILHAM_ORCAMENTO", CA,
     "    rotas = (politica()[\"CLASSES\"][\"API_COM_LIMITE_PUBLICADO\"].get(\"ROTAS\") or {}).get(d)",
     "    rotas = None", T),
    ("M32_CIENCIA_PEDE_POR_FORA_DA_PORTA", CP,
     "    R24 = _porta_do_contador()\n    if R24 is None:", "    R24 = _porta_do_contador()\n    if True:", T),
    ("M33_CIENCIA_CHAMA_A_FONTE_MORTA_DE_CONTADOR", CP,
     "        return None, 'CONTADOR_24H %s %s' % (reserva.get('ESTADO'), reserva.get('MOTIVO') or reserva.get('PORQUE') or '')",
     "        return None, 'HTTP 0'", T),
    # ── O RUN_ID ──────────────────────────────────────────────────────────────────────────────────
    ("M34_RUN_ID_FORA_DO_FORMATO_DA_PROVA", OL,
     '    return "%s-%s-%s-%s" % (pais, t, quando, salga)',
     '    return "RELIGA-%s-%s" % (t, salga)', T),
]


def copia(ref):
    d = tempfile.mkdtemp(prefix="mut-religa-")
    tar = subprocess.run(["git", "archive", ref], cwd=RAIZ, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=__import__("io").BytesIO(tar)) as t:
        t.extractall(d)
    return d


def aplicar(base, ficheiro, velho, novo):
    """→ "" se aplicou, ou o motivo. Uma ancora ambigua e tao ma como uma ancora ausente."""
    p = os.path.join(base, ficheiro)
    if not os.path.isfile(p):
        return "FICHEIRO_AUSENTE: %s" % ficheiro
    s = open(p, encoding="utf-8").read()
    n = s.count(velho)
    if n == 0:
        return "ANCORA_AUSENTE em %s" % ficheiro
    if n > 1:
        return "ANCORA_AMBIGUA (%d vezes) em %s" % (n, ficheiro)
    open(p, "w", encoding="utf-8", newline="").write(s.replace(velho, novo))
    return ""


def correr(nome, ficheiro, velho, novo, cmds, ref):
    base = copia(ref)
    try:
        porque = aplicar(base, ficheiro, velho, novo)
        if porque:
            return {"MUTANTE": nome, "ESTADO": "NAO_APLICOU", "PORQUE": porque}
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        env.pop("SINTONIA_CORTESIA_LIVRO", None)
        env.pop("SINTONIA_TETO_24H", None)
        for cmd in ([cmds] if isinstance(cmds[0], str) else cmds):
            r = subprocess.run(cmd, cwd=base, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=600, env=env)
            if r.returncode != 0:
                cauda = (r.stderr or r.stdout or "").strip().splitlines()
                return {"MUTANTE": nome, "ESTADO": "MORTO", "FICHEIRO": ficheiro,
                        "APANHADO_POR": " ".join(cmd[-1:]), "SINAL": cauda[-1][:200] if cauda else ""}
        return {"MUTANTE": nome, "ESTADO": "SOBREVIVEU", "FICHEIRO": ficheiro,
                "PORQUE": "nenhum teste reprovou com o defeito plantado"}
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main(argv):
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    ref = arg.get("ref", "HEAD")
    so = set(x for x in arg.get("so", "").split(",") if x)
    alvos = [m for m in MUTANTES if not so or m[0] in so]
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda m: correr(m[0], m[1], m[2], m[3], m[4], ref), alvos))
    res.sort(key=lambda r: r["MUTANTE"])
    conta = {}
    for r in res:
        conta[r["ESTADO"]] = conta.get(r["ESTADO"], 0) + 1
    doc = {"DATASET": "MUTACAO-RELIGA-MULTICANAL", "REF": ref, "TOTAL": len(res), "CONTA": conta,
           "MUTANTES": res}
    saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO.json")
    with open(saida, "w", encoding="utf-8", newline="") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({"TOTAL": len(res), "CONTA": conta, "SAIDA": saida}, ensure_ascii=False))
    for r in res:
        if r["ESTADO"] != "MORTO":
            print("  %-46s %s  %s" % (r["MUTANTE"], r["ESTADO"], r.get("PORQUE", "")[:90]))
    return 0 if conta.get("MORTO") == len(res) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
