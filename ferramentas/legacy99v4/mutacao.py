# -*- coding: utf-8 -*-
"""LEGACY-99 v4 (D, A, C, B, VIDEO) · mutacao: cada guarda, desligada, tem de fazer cair um teste.

Cada mutante troca UM trecho (ancora de uma linha), corre os testes e repoe o
ficheiro original pelo conteudo guardado em memoria (nunca por git). Sem bytecode:
um mutante do mesmo tamanho enganava o .pyc. Cada corrida confere os livros da
arvore: se um mudar, e reposto e o mutante fica marcado ESCREVEU_LIVRO.

Uso: py ferramentas/legacy99v4/mutacao.py [--saida X.json]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTES = ["tests.test_legacy_colchetes", "tests.test_importar_do_coletor", "tests.test_legacy_recheck",
          "tests.test_onboardar_rotas_provadas", "tests.test_youtube_pelo_scrap", "tests.test_rota_video_d53",
          "tests.test_d36_envelope_equivalente", "curadoria.test_regua_social"]
CAN, IMP = "curadoria/canario.py", "curadoria/importar_do_coletor.py"
GD, SUP, RG = "curadoria/gatilho_discovery.py", "curadoria/supervisor.py", "curadoria/regua_social.py"
MUTANTES = [
    # D
    ("D1 o link malformado volta a passar", CAN,
     "            p = urlparse(h)", "            p = urlparse('http://ok/')"),
    # A
    ("A1 o canario 'prova' qualquer estrategia (PDF entra)", IMP,
     '    return aq.get("STRATEGY") == "HTML_LINK_DISCOVERY" and bool(aq.get("INDEX_URL"))',
     "    return True"),
    ("A2 o YouTube deixa de ser reconhecido", IMP,
     '    return (aq.get("STRATEGY") in YOUTUBE or aq.get("PLATFORM") == "YOUTUBE"',
     '    return False and (aq.get("STRATEGY") in YOUTUBE or aq.get("PLATFORM") == "YOUTUBE"'),
    ("A3 a importacao ja nao recusa o canal YouTube", IMP,
     "    if e_youtube(atual, linha):\n        raise",
     "    if False:\n        raise"),
    ("A4 importa sem identidade", IMP,
     '    if not ident or not ident.get("DOCUMENT_ID"):', "    if False:"),
    ("A5 o contrato importado pode diferir da linha", IMP,
     '    if SHA.do_contrato(novo) != SHA.do_contrato(linha):', "    if False:"),
    ("A6 quem ja tem contrato HTML no Curator e reimportado", IMP,
     "        if atual:\n            continue", "        if False:\n            continue"),
    # C
    ("C1 entram fontes que nao sao READY_LEGACY", GD,
     '        if CG.avaliar(sid, **ctx).get("MOTIVO") != CG.READY_LEGACY:', "        if False:"),
    ("C2 entram contratos que o canario nao prova", GD,
     '        if aq.get("STRATEGY") not in ESTRATEGIAS_QUE_O_CANARIO_PROVA or not aq.get("INDEX_URL"):',
     '        if not aq.get("INDEX_URL"):'),
    ("C3 duas do mesmo dominio no lote", GD, '        if c["DOMINIO"] in vistos:', "        if False:"),
    ("C4 lote sem maximo", GD, "        if len(lote) >= maximo:", "        if False:"),
    ("C5 sem intervalo entre lotes", GD,
     "    if ultimo and (agora - ultimo).total_seconds() < LEGACY_INTERVALO_H * 3600:", "    if False:"),
    ("C6 o loop remede por omissao", SUP,
     "def _loop(pausa_worker: float, poll: float, revalidar_legacy: bool = False) -> int:",
     "def _loop(pausa_worker: float, poll: float, revalidar_legacy: bool = True) -> int:"),
    ("C7 o servico nao liga o re-check", SUP,
     "    return supervisionar(a.pausa, a.poll, revalidar_legacy=not a.sem_revalidar_legacy)",
     "    return supervisionar(a.pausa, a.poll)"),
    ("C8 o gancho nao e chamado", SUP, "                _hook_revalidar_legacy()", "                pass"),
    ("C9 a ordem deixa de ser a mais antiga primeiro", GD,
     '    return sorted(out, key=lambda x: (x["PROMOVIDA_EM"], x["SOURCE_ID"]))',
     '    return sorted(out, key=lambda x: x["SOURCE_ID"])'),
    ("C10 remede mesmo sem candidatas", GD, "    if not lote:", "    if False:"),
    # B
    ("B1 grava mesmo quando o bloco 4 salta", IMP,
     "    if saltou or not pedidas <= autorizadas:", "    if False:"),
    ("B2 grava no livro tambem as fontes nao pedidas", IMP,
     '    livro_d = dict(livro, FONTES=[novo_livro[c["SOURCE_ID"]] if c["SOURCE_ID"] in pedidas else c',
     '    livro_d = dict(livro, FONTES=[novo_livro[c["SOURCE_ID"]] if True else c'),
    ("B3 grava na tabela tambem as linhas nao pedidas", IMP,
     '    tabela_d = dict(tabela, FONTES=[nova_tabela[l["SOURCE_ID"]] if l["SOURCE_ID"] in pedidas else l',
     '    tabela_d = dict(tabela, FONTES=[nova_tabela[l["SOURCE_ID"]] if True else l'),
    ("B4 aceita fontes fora do plano", IMP,
     '    fora = [s for s in ids if s not in por]\n    if fora:\n        raise ImportacaoInvalida("fora do plano (nao sao canais',
     '    fora = [s for s in ids if s not in por]\n    if False:\n        raise ImportacaoInvalida("fora do plano (nao sao canais'),
    ("B5 nao manda ao remedir", IMP, "    feitas = remedir_fn(ids)\n    return {\"PELO_SCRAP\"",
     "    feitas = []\n    return {\"PELO_SCRAP\""),
    ("B6 o canal com contrato fica parado em vez de ir pelo Scrap", IMP,
     "            if not atual:\n                fica.append", "            if True:\n                fica.append"),
    ("B7 sem ledger", IMP, "    if minhas:\n        with LEDGER", "    if False:\n        with LEDGER"),
    # VIDEO
    ("V1 a D53 nao se aplica ao canal-youtube", RG,
     'FASES_VIDEO = frozenset({"canal-youtube"})', "FASES_VIDEO = frozenset()"),
    ("V2 a pagina do video nao e conferida", RG,
     '    if not RE_ID_DO_VIDEO.match(vid) or not _nomeia_o_video(_pagina_do_video(ob), vid):',
     "    if False:"),
    ("V3 qualquer host serve de pagina do video", RG,
     r'    return bool(re.match(r"^https://(www\.|m\.)?youtube\.com/(watch\?v=%s(&|$)|shorts/%s([/?]|$))|"',
     r'    return bool(re.match(r"^https://[^/]+/(watch\?v=%s(&|$)|shorts/%s([/?]|$))|"'),
    ("V4 id de video de qualquer forma", RG,
     'RE_ID_DO_VIDEO = re.compile(r"^[A-Za-z0-9_-]{11}$")', 'RE_ID_DO_VIDEO = re.compile(r"^.+$")'),
    ("V5 'Private video' conta como titulo", RG,
     'TITULOS_SEM_VIDEO = frozenset({"private video", "deleted video"})', "TITULOS_SEM_VIDEO = frozenset()"),
    ("V6 UNKNOWN deixa de ser ausencia", RG,
     'AUSENTE = ("", "NAO SEI", "UNKNOWN")', 'AUSENTE = ("", "NAO SEI")'),
    ("V7 o canal nao e conferido", RG,
     "    if not canal_do_contrato or canal != canal_do_contrato:", "    if False:"),
    ("V8 o titulo nao e conferido", RG,
     "    if titulo in AUSENTE or titulo.lower() in TITULOS_SEM_VIDEO:", "    if False:"),
]

LIVROS = ["curadoria/LIFECYCLE-LEDGER-V1.json", "curadoria/LIFECYCLE-QUEUE-V1.json",
          "curadoria/LIFECYCLE-EVIDENCE-V1.json", "curadoria/italy_contracts_curator.json",
          "regras/italy_contracts_onboarded.json", "curadoria/DESBLOQUEIO-LEDGER-V1.jsonl"]
ESCREVEU = []


def _retrato():
    return {p: ((RAIZ / p).read_bytes() if (RAIZ / p).exists() else None) for p in LIVROS}


def correr() -> bool:
    antes = _retrato()
    try:
        return _correr()
    finally:
        for p, b in antes.items():
            f = RAIZ / p
            agora = f.read_bytes() if f.exists() else None
            if agora != b:
                if b is None:
                    f.unlink()
                else:
                    f.write_bytes(b)
                ESCREVEU.append(p)


def _correr() -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-m", "unittest", *TESTES], cwd=RAIZ,
                       capture_output=True, text=True, env=env, timeout=600)
    return r.returncode == 0


def main(argv) -> int:
    assert correr(), "a base tem de estar verde antes de mutar"
    assert not ESCREVEU, "a base escreveu num livro: %s" % ESCREVEU
    out = []
    for nome, rel, velho, novo in MUTANTES:
        f = RAIZ / rel
        original = f.read_bytes()
        texto = original.decode("utf-8")
        crlf = "\r\n" in texto
        v, n = (velho.replace("\n", "\r\n"), novo.replace("\n", "\r\n")) if crlf else (velho, novo)
        if texto.count(v) != 1:
            out.append({"MUTANTE": nome, "RESULTADO": "ANCORA_NAO_CASA"})
            print(nome, "ANCORA_NAO_CASA", flush=True)
            continue
        try:
            f.write_bytes(texto.replace(v, n).encode("utf-8"))
            verde = correr()
        finally:
            f.write_bytes(original)
        out.append({"MUTANTE": nome, "RESULTADO": "SOBREVIVEU" if verde else "MORTO",
                    "ESCREVEU_LIVRO": sorted(set(ESCREVEU))})
        ESCREVEU.clear()
        print(nome, out[-1]["RESULTADO"], flush=True)
    assert correr(), "a base tem de voltar verde depois de mutar"
    mortos = sum(o["RESULTADO"] == "MORTO" for o in out)
    print("MORTOS %d/%d · mutantes que escreveram num livro: %d" % (
        mortos, len(out), sum(1 for o in out if o.get("ESCREVEU_LIVRO"))))
    if "--saida" in argv:
        Path(argv[argv.index("--saida") + 1]).write_text(
            json.dumps({"DATASET": "LEGACY-99-V4-MUTACAO", "MORTOS": mortos, "TOTAL": len(out),
                        "TESTES": TESTES, "MUTANTES": out}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
    return 0 if mortos == len(out) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
