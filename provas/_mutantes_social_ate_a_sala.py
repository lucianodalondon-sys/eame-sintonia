"""Mutantes da SOCIAL-ATE-A-SALA · A (desbloqueio) · B (regua por provas) · C (feed sem chave) · D (URL achado).

Cada mutacao planta UM defeito no codigo da missao e corre os testes dela. Se continuarem verdes, a
mutacao sobreviveu — e a lei nao esta guardada. Nenhuma pode sobreviver. O ficheiro e reposto depois de
cada mutacao, e os livros vivos sao conferidos (sha256) antes e depois: nenhum pode mudar.

Corre:  python provas/_mutantes_social_ate_a_sala.py
"""
import hashlib
import io
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
RG, FN, DS = "curadoria/regua_social.py", "candidatas/fonte_nova.py", "curadoria/desbloquear_social.py"
AY, DU = "coleta/adaptador_youtube.py", "coleta/social_por_url_achado.py"
T_B, T_A = "tests/test_regua_social_por_provas.py", "tests/test_desbloquear_social.py"
T_C, T_D = "tests/test_youtube_feed_sem_chave.py", "tests/test_social_por_url_achado.py"
LIVROS = ["candidatas/FONTES-CANDIDATAS.json", "curadoria/LIFECYCLE-LEDGER-V1.json",
          "curadoria/LIFECYCLE-QUEUE-V1.json", "curadoria/LIFECYCLE-EVIDENCE-V1.json",
          "curadoria/SOURCE-ID-ALLOCATION-V1.json", "curadoria/italy_contracts_curator.json"]

MUTACOES = [
    # ── B · a regua por provas ──────────────────────────────────────────────────────────────
    ("B1 a regua volta a reprovar pelo NOME da fase", RG, T_B,
     "        falta = provas_da_equivalencia(env, fase, contrato)", '        falta = ["NOME_DA_FASE"]'),
    ("B2 a pagina da publicacao deixa de ter de nomear o id", RG, T_B,
     "        if pagina is None or str(pubid) not in str(pagina):", "        if False:"),
    ("B3 o slug LinkedIn do contrato deixa de ser a conta", RG, T_B,
     '    if aq.get("LINKEDIN_SLUG"):', "    if False:"),
    ("B4 o handle Instagram do contrato deixa de ser a conta", RG, T_B,
     '    if aq.get("INSTAGRAM_HANDLE"):', "    if False:"),
    ("B5 o id do Reel (REEL.POST_ID) deixa de ser lido", RG, T_B,
     'CAMPOS_DA_PUBLICACAO = ("NATIVE_ID", "REEL.POST_ID", "RAW.ACTIVITY_ID")',
     'CAMPOS_DA_PUBLICACAO = ("NATIVE_ID",)'),
    ("B6 midia com 0 bytes passa a contar", RG, T_B,
     "isinstance(_valor(ob, b), (int, float)) and _valor(ob, b) > 0)",
     "isinstance(_valor(ob, b), (int, float)))"),
    ("B7 NOT_KNOWN (dialecto do Reel) deixa de ser ausencia", RG, T_B,
     'AUSENTES_DO_SCRAP = ("", "NAO SEI", "NAO_SEI", "UNKNOWN", "NOT_KNOWN")',
     'AUSENTES_DO_SCRAP = ("", "NAO SEI", "NAO_SEI", "UNKNOWN")'),
    ("B8 a conta do LinkedIn le-se no bruto de qualquer campo", RG, T_B,
     '    "LINKEDIN": ("RAW.CREATOR_URL",),', '    "LINKEDIN": ("RAW.CREATOR_URL", "SOURCE_ACCOUNT", "URL"),'),
    ("B9 o campo do topo deixa de mandar (alias por cima)", RG, T_B,
     "    if k in ob:\n        v = ob.get(k)", "    if False:\n        v = ob.get(k)"),
    # ── C · o feed sem chave ────────────────────────────────────────────────────────────────
    ("C1 a matriz fechada deixa de travar o pedido", AY, T_C,
     "    if not aberta:\n        # ZERO pedidos", "    if False:\n        # ZERO pedidos"),
    ("C2 a linha da matriz deixa de ser lida", AY, T_C,
     "    if linha.get('PERMITIDA') != 'SIM' or linha.get('ESTADO') in ('ROUTE_NOT_ALLOWED', 'BLOCKED'):",
     "    if False:"),
    ("C3 entrada de OUTRO canal entra", AY, T_C, "        if canal != canal_id:", "        if False:"),
    ("C4 o teto de 15 deixa de valer", AY, T_C,
     "    for v in videos[:int(limit or LIMITE_FEED)]:", "    for v in videos:"),
    ("C5 a recusa do robots vira lista vazia", AY, T_C,
     "        raise _EstadoDaApi({'STATE': 'ROUTE_NOT_ALLOWED', 'NATIVE_REASON': str(e)[:300],",
     "        return []\n        raise _EstadoDaApi({'STATE': 'ROUTE_NOT_ALLOWED', 'NATIVE_REASON': str(e)[:300],"),
    ("C6 DTD/ENTITY deixa de ser recusado", AY, T_C,
     "    if b'<!DOCTYPE' in dados[:4096].upper() or b'<!ENTITY' in dados.upper():", "    if False:"),
    ("C7 a decisao do dono deixa de viajar nomeada", AY, T_C,
     "        if linha.get('OWNER_AUTHORIZED') == 'SIM':", "        if False:"),
    ("C8 sem chave a fase vai ao feed mesmo fechado", AY, T_C,
     "        if aberta:\n            return youtube_canal_sem_chave(", "        if True:\n            return youtube_canal_sem_chave("),
    ("C9 toda data ganha precisao SECOND", AY, T_C,
     "    return 'SECOND' if re.match(r'^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}', publicado or '') else None",
     "    return 'SECOND'"),
    # ── D · a entrada por URL achado ───────────────────────────────────────────────────────
    ("D1 proveniencia incompleta passa", DU, T_D, "    if falta:\n        linha.update(ESTADO=\"REJEITADO\"",
     "    if False:\n        linha.update(ESTADO=\"REJEITADO\""),
    ("D2 posicao < 1 passa", DU, T_D, '            if int(p["POSICAO"]) < 1:', "            if False:"),
    ("D3 instante sem forma passa", DU, T_D,
     '    if "INSTANTE" not in falta and not RE_INSTANTE.match(str(p["INSTANTE"])):', "    if False:"),
    ("D4 perfil vira item", DU, T_D, '    if esp["ESPECIE"] == "NAO_E_PUBLICACAO":', "    if False:"),
    ("D5 o mesmo alvo pede-se duas vezes", DU, T_D, "    if alvo in vistos:", "    if False:"),
    ("D6 conflito de conta ignorado", DU, T_D, "    if conta and no_endereco and conta != no_endereco:",
     "    if False:"),
    ("D7 post de pessoa vira pedido", DU, T_D, "        if pessoa:", "        if False:"),
    ("D8 autor desconhecido de post regista-se adivinhado", DU, T_D,
     '        if not fonte["SOURCE_IDS"] and tipo != "ORGANIZACAO":', "        if False:"),
    ("D9 colisao de identidade ignorada", DU, T_D, '    if len(fonte["SOURCE_IDS"]) > 1:', "    if False:"),
    ("D10 conta sem SOURCE_ID nao espera", DU, T_D, '    if not fonte["SOURCE_IDS"]:\n        cand =',
     '    if False:\n        cand ='),
    # ── A · o desbloqueio pelas portas ─────────────────────────────────────────────────────
    ("A1 decisao que nao cobre o tipo passa", FN, T_A,
     "    if not decisoes or not set(decisoes) <= cobre:", "    if False:"),
    ("A2 sem OWNER_AUTHORIZED=SIM passa", FN, T_A, '    if owner_authorized != "SIM":', "    if False:"),
    ("A3 sem politica medida passa", FN, T_A,
     '    if not str(platform_policy_status or "").strip() or not platform_policy_prova:', "    if False:"),
    ("A4 desbloqueia quem nao esta bloqueado", FN, T_A,
     '    if c.get("ESTADO") != "POLICY_BLOCK":\n        return c, "NAO_ESTA',
     '    if False:\n        return c, "NAO_ESTA'),
    ("A5 o livro do ciclo de vida nao regista", DS, T_A,
     "        if LC.estado_de(c[\"CANDIDATA_ID\"]) == LC.POLICY_BLOCK:",
     "        if False:"),
    ("A6 o QUALIFY nao se enfileira", DS, T_A,
     "        F.enfileirar(c[\"CANDIDATA_ID\"], F.QUALIFY, priority=30, motivo=razao[:160])",
     "        pass"),
    ("A7 sem politica medida desbloqueia na mesma", DS, T_A,
     '        if status == "NAO SEI" and c.get("ESTADO") == "POLICY_BLOCK":', "        if False:"),
    ("A8 a pessoa leva a decisao da organizacao", DS, T_A,
     '        return ["D24", "D106"] if RE_PESSOA.search(c.get("URL") or "") else ["D23", "D106"]',
     '        return ["D23", "D106"]'),
    ("A9 --aplicar sem --copia deixa escrever", DS, T_A,
     "    if not no_vivo and not a.copia:\n        print(\"RECUSADO: fora do vivo, declare --copia\")\n        return 2",
     "    if False:\n        print(\"RECUSADO: fora do vivo, declare --copia\")\n        return 2"),
]


def sha(p):
    f = RAIZ / p
    return hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None


def corre(teste):
    p = subprocess.run([sys.executable, teste], cwd=str(RAIZ), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600,
                       env=dict(__import__("os").environ, HTTPS_PROXY="http://127.0.0.1:9",
                                HTTP_PROXY="http://127.0.0.1:9", https_proxy="http://127.0.0.1:9",
                                http_proxy="http://127.0.0.1:9"))
    return p.returncode


def main() -> int:
    livros_antes = {p: sha(p) for p in LIVROS}
    for t in sorted({m[2] for m in MUTACOES}):
        rc = corre(t)
        print("TESTE SEM MUTACAO %s: rc %d" % (t, rc))
        if rc:
            return 2
    mortes, sobreviventes = 0, []
    for nome, alvo, teste, de, para in MUTACOES:
        f = RAIZ / alvo
        original = io.open(f, encoding="utf-8").read()
        if original.count(de) != 1:
            sobreviventes.append(nome + " (NAO APLICAVEL: %d ocorrencias)" % original.count(de))
            print("  %-60s NAO APLICAVEL" % nome[:60])
            continue
        try:
            io.open(f, "w", encoding="utf-8", newline="").write(original.replace(de, para, 1))
            rc = corre(teste)
        finally:
            io.open(f, "w", encoding="utf-8", newline="").write(original)
        if rc != 0:
            mortes += 1
            print("  %-60s MORTA" % nome[:60])
        else:
            sobreviventes.append(nome)
            print("  %-60s SOBREVIVEU  <-- defeito" % nome[:60])
    mudou = [p for p in LIVROS if sha(p) != livros_antes[p]]
    print("\nMUTACOES %d · MORTAS %d · SOBREVIVENTES %d · LIVROS VIVOS MUDADOS %d"
          % (len(MUTACOES), mortes, len(sobreviventes), len(mudou)))
    for s in sobreviventes:
        print("  SOBREVIVEU:", s)
    for p in mudou:
        print("  LIVRO MUDOU:", p)
    return 0 if not sobreviventes and not mudou else 1


if __name__ == "__main__":
    sys.exit(main())
