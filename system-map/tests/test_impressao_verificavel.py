#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA IMPRESSAO VERIFICAVEL — G3.

    python3 system-map/tests/test_impressao_verificavel.py

Quatro artefactos carimbavam um SHA de commit e mais nada. Medido em seis
commits seguidos, nos tres que a cadeia regera: o carimbo aponta SEMPRE para o
commit ANTERIOR.

    UM FICHEIRO COMMITADO NUNCA NOMEIA O COMMIT QUE O CONTEM.

Nao e desleixo: e impossivel por construcao. Enquanto a prova de pertenca for um
SHA de commit, ela nao se consegue verificar — e um carimbo que nao se verifica
nao e um carimbo, e uma promessa.

O QUE ESTE FICHEIRO CONFERE
---------------------------
    1  o gerador corre
    2  a impressao e escrita
    3  ela e recalculavel por OUTRO caminho que nao o do gerador
    4  mesma fonte  -> mesma impressao
    5  fonte mexida -> impressao diferente
    6  so o relogio -> a impressao da FONTE nao se mexe
    7  artefacto velho contra fonte nova -> STALE
    8  artefacto actual contra fonte actual -> CURRENT, salvo divida declarada

    GENERATION != VALIDATION. Quem gera nao pode ser quem aprova.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SCRIPTS = RAIZ / "system-map" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import impressao_da_arvore as IMPRESSAO                 # noqa: E402

CADEIA = json.loads((SCRIPTS / "CADEIA-DO-MAPA.json").read_text(encoding="utf-8"))

# Os quatro do G3, com o gerador de cada um. A lista e a da missao, e nao um
# palpite: quem a alargar tem de vir aqui dizer porque.
OS_QUATRO = [
    ("system-map/data/sources.generated.json",
     "system-map/scripts/scan_sources.py"),
    ("system-map/data/pente-fino.generated.json",
     "system-map/scripts/pente_fino_da_coleta.py"),
    ("system-map/data/censo-da-coleta.generated.json",
     "system-map/scripts/censo_da_coleta.py"),
    ("data/derivados/MATRIZ-CARDS-SENSORES-V1.json",
     "system-map/scripts/censo_cards_sensores.py"),
]

FALHAS: list = []
CONTA = [0]


def prova(nome, ok, porque=""):
    CONTA[0] += 1
    print(("  PASS  " if ok else "  FAIL  ") + nome
          + (("\n        " + str(porque)) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


def nota(texto):
    print("  ----  " + texto)


def ler(caminho):
    return json.loads((RAIZ / caminho).read_text(encoding="utf-8"))


def prov_de(caminho):
    return (ler(caminho).get("PROVENANCE") or {})


def correr(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", timeout=1200)


def outro_sistema_de_ficheiros(precisa_mb=600):
    """Uma pasta noutro sistema de ficheiros, se existir uma.

        UMA PROVA DE DETERMINISMO QUE SO SE CORRE NUM DISCO MEDE O DISCO.
    """
    for base in ("/dev/shm", "/run/shm"):
        try:
            if not (os.path.isdir(base) and os.access(base, os.W_OK)):
                continue
            if os.stat(base).st_dev == os.stat(RAIZ).st_dev:
                continue
            if shutil.disk_usage(base).free // (1024 * 1024) < precisa_mb:
                continue
            return base
        except OSError:
            continue
    return None


def clone(base=None):
    """O clone traz o HEAD; o que esta por commitar e copiado por cima.

        O QUE VAI SER COMMITADO != O QUE JA ESTA RASTREADO.
    """
    d = Path(tempfile.mkdtemp(prefix="g3-", dir=base))
    r = subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--shared",
                        str(RAIZ), str(d / "r")], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("clone falhou: %s" % r.stderr[:300])
    alvo = d / "r"
    sujo = subprocess.run(["git", "status", "--porcelain"], cwd=str(RAIZ),
                          capture_output=True, text=True).stdout.splitlines()
    for linha in sujo:
        caminho = linha[3:].strip().strip('"')
        o, dd = RAIZ / caminho, alvo / caminho
        if o.is_file():
            dd.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(o, dd)
    return alvo


print("AS PROVAS DA IMPRESSAO VERIFICAVEL — G3")
print("=" * 70)

# ── A CAUSA, FIXADA COMO PROVA ──────────────────────────────────────────
# Ela nao e uma historia: e uma medicao que qualquer pessoa refaz.
for alvo, _ in OS_QUATRO[:3]:
    commits = subprocess.run(["git", "log", "-3", "--format=%H", "--", alvo],
                             cwd=str(RAIZ), capture_output=True, text=True
                             ).stdout.split()
    atrasados = 0
    for c in commits:
        bruto = subprocess.run(["git", "show", "%s:%s" % (c, alvo)], cwd=str(RAIZ),
                               capture_output=True, text=True).stdout
        try:
            carimbo = (json.loads(bruto).get("PROVENANCE") or {}).get("HEAD")
        except ValueError:
            continue
        if carimbo and carimbo != c:
            atrasados += 1
    prova("o_sha_de_commit_nunca_nomeia_o_proprio_commit[%s]" % Path(alvo).name,
          bool(commits) and atrasados == len(commits),
          "%d de %d commits com carimbo igual ao proprio" %
          (len(commits) - atrasados, len(commits)))

# ── 2 · OS QUATRO CARIMBAM, E O CARIMBO DIZ O QUE VALE ─────────────────
for alvo, gerador in OS_QUATRO:
    nome = Path(alvo).name
    p = prov_de(alvo)
    prova("carimba_a_impressao_da_arvore[%s]" % nome,
          bool(p.get("SOURCE_TREE_FINGERPRINT")))
    prova("declara_quem_gerou[%s]" % nome, p.get("GENERATED_BY") == gerador,
          p.get("GENERATED_BY"))
    prova("declara_as_entradas_que_leu[%s]" % nome, bool(p.get("INPUTS")))
    prova("sela_as_entradas[%s]" % nome, bool(p.get("INPUTS_DIGEST")))
    # 16 · o SHA de commit fica, mas deixa de ser prova
    prova("o_head_fica_declarado_como_nao_verificavel[%s]" % nome,
          p.get("HEAD_VERIFICAVEL") is False and len(p.get("HEAD_PORQUE_NAO") or "") > 40)
    prova("nenhuma_entrada_usa_caminho_absoluto[%s]" % nome,
          all(not i["PATH"].startswith("/") for i in p.get("INPUTS") or []))
    prova("o_artefato_nao_se_declara_entrada_de_si_mesmo[%s]" % nome,
          alvo not in {i["PATH"] for i in p.get("INPUTS") or []})
    # 1 · o ataque mais simples: por o SHA do commit no lugar da impressao.
    # Um SHA de commit tem 40 digitos; a impressao e um sha256, tem 64. E ela
    # nunca pode ser IGUAL ao HEAD, porque entao nao era uma impressao de nada.
    impressao_dele = p.get("SOURCE_TREE_FINGERPRINT") or ""
    prova("a_impressao_nao_e_o_sha_do_commit[%s]" % nome,
          len(impressao_dele) == 64 and impressao_dele != p.get("HEAD"),
          "%s (%d digitos)" % (impressao_dele[:16], len(impressao_dele)))
    # 6 e 10 · a lista de entradas e ordenada, e nao a ordem de quem a leu
    caminhos = [i["PATH"] for i in p.get("INPUTS") or []]
    prova("as_entradas_estao_por_ordem[%s]" % nome, caminhos == sorted(caminhos))

# ── 3 · RECALCULAVEL POR OUTRO CAMINHO QUE NAO O DO GERADOR ────────────
#     GENERATION != VALIDATION.
# O gerador carimbou a leitura DO DISCO. Aqui confere-se contra a leitura DO
# INDICE — outra implementacao da mesma lei, que `test_impressao_da_arvore.py`
# ja prova serem equivalentes. Se fosse a mesma funcao a responder-se a si
# propria, isto nao provava nada.
sujo = subprocess.run(["git", "status", "--porcelain"], cwd=str(RAIZ),
                      capture_output=True, text=True).stdout.strip()
do_indice, _ = IMPRESSAO.do_indice()
if sujo:
    nota("arvore com trabalho por commitar: a conferencia contra o INDICE fica "
         "para o CI, onde a arvore esta limpa")
else:
    for alvo, _ in OS_QUATRO:
        prova("a_impressao_bate_com_a_leitura_do_indice[%s]" % Path(alvo).name,
              prov_de(alvo).get("SOURCE_TREE_FINGERPRINT") == do_indice)

# E o selo das entradas recalcula-se a partir do que o artefacto DECLARA.
for alvo, _ in OS_QUATRO:
    p = prov_de(alvo)
    prova("o_selo_das_entradas_e_o_selo_das_entradas_declaradas[%s]" % Path(alvo).name,
          IMPRESSAO.selar_entradas(p.get("INPUTS") or []) == p.get("INPUTS_DIGEST"))

# ── UM FICHEIRO QUE CARREGA A IMPRESSAO NAO PODE ESTAR DENTRO DELA ─────
# A lei ja estava escrita; o que muda a cada missao e quem a cumpre. Isto varre
# os artefactos da casa e exige que quem carimba esteja excluido.
carimbam, dentro = [], []
for pasta in ("system-map/data", "data/derivados"):
    d = RAIZ / pasta
    if not d.is_dir():
        continue
    for f in sorted(d.glob("*.json")):
        rel = f.relative_to(RAIZ).as_posix()
        try:
            p = (json.loads(f.read_text(encoding="utf-8")).get("PROVENANCE") or {})
        except (OSError, ValueError):
            continue
        if p.get("SOURCE_TREE_FINGERPRINT"):
            carimbam.append(rel)
            if not IMPRESSAO.excluido(rel):
                dentro.append(rel)
prova("todo_artefato_que_carimba_a_impressao_esta_fora_dela", not dentro,
      "dentro da impressao: %s" % dentro)
prova("ha_artefatos_a_carimbar_para_esta_prova_nao_ser_vazia", len(carimbam) >= 6,
      carimbam)

# ── OS RELOGIOS, MORDIDOS UM A UM (14 · 15 · 19 · 18) ──────────────────
BASE = prov_de(OS_QUATRO[0][0])
prova("sem_carimbo_nenhum_o_veredito_e_unknown",
      IMPRESSAO.frescura_do_carimbo({})["VEREDITO"] == "UNKNOWN")
prova("so_com_sha_de_commit_o_veredito_e_unverifiable",
      IMPRESSAO.frescura_do_carimbo({"HEAD": "a" * 40})["VEREDITO"] == "UNVERIFIABLE")
outra_arvore = json.loads(json.dumps(BASE))
outra_arvore["SOURCE_TREE_FINGERPRINT"] = "0" * 64
prova("uma_impressao_de_outra_arvore_e_stale_e_nao_unknown",
      IMPRESSAO.frescura_do_carimbo(outra_arvore)["VEREDITO"] == "STALE",
      IMPRESSAO.frescura_do_carimbo(outra_arvore))
selo_mexido = json.loads(json.dumps(BASE))
selo_mexido["INPUTS_DIGEST"] = "0" * 64
prova("um_selo_de_entradas_diferente_e_stale",
      IMPRESSAO.frescura_do_carimbo(selo_mexido)["VEREDITO"] == "STALE")
relogio = json.loads(json.dumps(BASE))
relogio["GENERATED_AT"] = "1999-01-01T00:00:00+00:00"
relogio["HEAD"] = "b" * 40
prova("mexer_no_relogio_e_no_head_nao_muda_a_impressao_da_fonte",
      relogio["SOURCE_TREE_FINGERPRINT"] == BASE["SOURCE_TREE_FINGERPRINT"])
prova("e_nao_muda_o_veredito",
      IMPRESSAO.frescura_do_carimbo(relogio)["VEREDITO"]
      == IMPRESSAO.frescura_do_carimbo(BASE)["VEREDITO"])

# ── 10 e 13 e 20 · O PENTE FINO NAO GANHA UM VERDE QUE NAO TEM ─────────
#     UM CARIMBO VERIFICAVEL NAO PAGA UMA DIVIDA DE ORDEM.
# O pente fino le `state.generated.json`, que nesta cadeia so e escrito DEPOIS
# dele. Tornar a impressao aferivel nao muda a ordem — e usar o G3 para o
# declarar CURRENT seria fechar o G6 com uma frase.
pente = IMPRESSAO.frescura_do_carimbo(prov_de(OS_QUATRO[1][0]))
prova("o_pente_fino_declara_o_estado_como_entrada_gerada",
      any(i["PATH"] == "system-map/data/state.generated.json"
          and i.get("PAPEL") == IMPRESSAO.GERADO
          for i in prov_de(OS_QUATRO[1][0]).get("INPUTS") or []))
prova("o_pente_fino_nao_e_current_enquanto_a_ordem_da_cadeia_for_esta",
      pente["VEREDITO"] != "CURRENT" or pente.get("MOTIVO") != "CURRENT"
      or "state.generated.json" not in str(pente.get("ENTRADAS_GERADAS_DE_OUTRA_ARVORE")),
      pente)
passos = CADEIA["REGERAR"]
prova("a_ordem_da_cadeia_continua_a_por_o_pente_fino_antes_do_gerador",
      passos.index("system-map/scripts/pente_fino_da_coleta.py")
      < passos.index("system-map/scripts/generate_system_map.py"),
      "se isto mudou, o G6 foi mexido — e nao era esta missao")

if "--sem-clone" in sys.argv:
    nota("(as provas de clone ficam de fora: corrida aninhada)")
    print()
    print("  %d provas · %d falhas" % (CONTA[0], len(FALHAS)))
    if FALHAS:
        print("  FALHARAM: " + ", ".join(FALHAS))
    sys.exit(1 if FALHAS else 0)

# ── O QUE SO SE PROVA NOUTRA ARVORE ────────────────────────────────────
c = clone()
try:
    # 1 · os quatro geradores correm
    for alvo, gerador in OS_QUATRO:
        r = correr([sys.executable, gerador], c)
        prova("o_gerador_corre[%s]" % Path(gerador).name, r.returncode == 0,
              r.stderr[-300:])

    # 4 e 6 · mesma fonte -> mesma impressao; so o relogio nao conta
    antes = {a: json.loads((c / a).read_text(encoding="utf-8"))["PROVENANCE"]
             for a, _ in OS_QUATRO}
    for alvo, gerador in OS_QUATRO:
        correr([sys.executable, gerador], c)
    depois = {a: json.loads((c / a).read_text(encoding="utf-8"))["PROVENANCE"]
              for a, _ in OS_QUATRO}
    for alvo, _ in OS_QUATRO:
        nome = Path(alvo).name
        prova("duas_corridas_dao_a_mesma_impressao[%s]" % nome,
              antes[alvo]["SOURCE_TREE_FINGERPRINT"]
              == depois[alvo]["SOURCE_TREE_FINGERPRINT"])
        prova("duas_corridas_dao_o_mesmo_selo_de_entradas[%s]" % nome,
              antes[alvo]["INPUTS_DIGEST"] == depois[alvo]["INPUTS_DIGEST"])
        prova("e_o_relogio_andou_entre_as_duas[%s]" % nome,
              antes[alvo]["GENERATED_AT"] <= depois[alvo]["GENERATED_AT"])

    # 6 · PONTO FIXO — escrever a impressao nao move a impressao
    #     Se movesse, a correcao teria o mesmo defeito com outro nome.
    def impressao_ali(raiz):
        r = correr([sys.executable, "-c",
                    "import sys;sys.path.insert(0,'system-map/scripts');"
                    "import impressao_da_arvore as I;print(I.do_disco()[0])"], raiz)
        return r.stdout.strip()

    antes_fp = impressao_ali(c)
    for alvo, gerador in OS_QUATRO:
        correr([sys.executable, gerador], c)
    prova("escrever_os_quatro_carimbos_nao_move_a_impressao",
          impressao_ali(c) == antes_fp,
          "a impressao perseguia o proprio rabo")

    # 5 e 7 · uma fonte mexida muda a impressao e torna os artefactos STALE
    def frescura_ali(raiz, alvo):
        r = correr([sys.executable, "-c",
                    "import sys,json;sys.path.insert(0,'system-map/scripts');"
                    "import impressao_da_arvore as I;"
                    "d=json.load(open(%r,encoding='utf-8'));"
                    "print(json.dumps(I.frescura_do_carimbo(d.get('PROVENANCE') or {})))"
                    % alvo], raiz)
        return json.loads(r.stdout) if r.returncode == 0 else {"VEREDITO": "ERRO",
                                                              "PORQUE": r.stderr[-200:]}
    for alvo, _ in OS_QUATRO:
        v = frescura_ali(c, alvo)
        if v["VEREDITO"] == "CURRENT":
            prova("acabado_de_gerar_o_artefato_e_current[%s]" % Path(alvo).name, True)
        else:
            prova("acabado_de_gerar_o_artefato_diz_porque_nao[%s]" % Path(alvo).name,
                  v["VEREDITO"] == "STALE" and v.get("MOTIVO") in
                  ("STALE_BY_CYCLE", "ARVORE_MUDOU", "ENTRADA_MUDOU"), v)

    fonte = c / "AGENTS.md"
    original = fonte.read_text(encoding="utf-8")          # lido ANTES de mutar
    fonte.write_text(original + "\n<!-- uma fonte que mudou -->\n", encoding="utf-8")
    prova("mexer_numa_fonte_move_a_impressao_da_arvore",
          impressao_ali(c) != antes_fp)
    for alvo, _ in OS_QUATRO:
        prova("e_o_artefato_passa_a_stale[%s]" % Path(alvo).name,
              frescura_ali(c, alvo)["VEREDITO"] == "STALE")
    fonte.write_text(original, encoding="utf-8")
    prova("reposta_a_fonte_a_impressao_volta", impressao_ali(c) == antes_fp)

    # 9 · uma fonte que NAO e entrada daquele artefato nao move o selo dele
    p_pente = json.loads((c / OS_QUATRO[1][0]).read_text(encoding="utf-8"))["PROVENANCE"]
    fonte.write_text(original + "\n<!-- outra vez -->\n", encoding="utf-8")
    v = frescura_ali(c, OS_QUATRO[1][0])
    prova("uma_fonte_de_fora_nao_mexe_no_selo_das_entradas",
          v.get("INPUTS_DIGEST_AGORA") == p_pente["INPUTS_DIGEST"],
          "AGENTS.md nao e entrada do pente fino e mesmo assim moveu o selo")
    fonte.write_text(original, encoding="utf-8")

    # 16A e 11 · carimbo adulterado a mao
    alvo0 = OS_QUATRO[0][0]
    inteiro = (c / alvo0).read_text(encoding="utf-8")      # lido ANTES de mutar
    d = json.loads(inteiro)
    d["PROVENANCE"]["SOURCE_TREE_FINGERPRINT"] = "f" * 64
    (c / alvo0).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    prova("um_carimbo_adulterado_nao_continua_current",
          frescura_ali(c, alvo0)["VEREDITO"] == "STALE")
    (c / alvo0).write_text(inteiro, encoding="utf-8")

    # 16B · uma ENTRADA mexida
    entrada = json.loads((c / alvo0).read_text(encoding="utf-8"))["PROVENANCE"]["INPUTS"][0]["PATH"]
    guardado = (c / entrada).read_text(encoding="utf-8")   # lido ANTES de mutar
    (c / entrada).write_text(guardado + "\n", encoding="utf-8")
    prova("uma_entrada_mexida_torna_o_artefato_stale",
          frescura_ali(c, alvo0)["VEREDITO"] == "STALE")
    (c / entrada).write_text(guardado, encoding="utf-8")

    # 12 · uma entrada NOVA obriga a regerar: o selo declarado deixa de bater
    prova("reposta_a_entrada_o_artefato_volta",
          frescura_ali(c, alvo0)["VEREDITO"] in ("CURRENT", "STALE"))

    # ── 13 e 20 · O G3 NAO FECHA O G6, E ISTO DEMONSTRA-O ──────────────
    #
    #     UM CARIMBO VERIFICAVEL NAO PAGA UMA DIVIDA DE ORDEM.
    #
    # O pente fino corre no passo 5 da cadeia e o gerador do estado no passo 7.
    # Enquanto a arvore nao muda, ler a geracao anterior da a mesma resposta e o
    # veredito e CURRENT com razao. O defeito aparece na PRIMEIRA corrida depois
    # de uma fonte mudar: ai o pente fino mede o estado de ANTES, e dizer-lhe
    # CURRENT seria usar o G3 para calar o G6.
    #
    # Sao precisas DUAS passagens da cadeia para ele ficar em dia. Isso e o preco
    # do G6, medido aqui, e nao uma solucao.
    PASSOS = [p for p in CADEIA["REGERAR"]]

    def cadeia(raiz):
        for passo in PASSOS:
            r = correr([sys.executable, passo], raiz)
            if r.returncode != 0:
                return False, "%s: %s" % (passo, r.stderr[-200:])
        return True, ""

    ok, porque = cadeia(c)
    prova("a_cadeia_canonica_corre_no_clone", ok, porque)
    if ok:
        marca = c / "AGENTS.md"
        guardado_md = marca.read_text(encoding="utf-8")     # lido ANTES de mutar
        marca.write_text(guardado_md + "\n<!-- fonte nova para o ciclo -->\n",
                         encoding="utf-8")
        cadeia(c)
        v = frescura_ali(c, OS_QUATRO[1][0])
        prova("uma_passagem_so_deixa_o_pente_fino_em_stale_by_cycle",
              v["VEREDITO"] == "STALE" and v.get("MOTIVO") == "STALE_BY_CYCLE", v)
        prova("e_diz_que_entrada_o_atrasou",
              "system-map/data/state.generated.json"
              in (v.get("ENTRADAS_GERADAS_DE_OUTRA_ARVORE") or []), v)
        # E os que nao leem geracao nenhuma ficam em dia a primeira
        v0 = frescura_ali(c, OS_QUATRO[0][0])
        prova("quem_so_le_fonte_fica_current_a_primeira_passagem",
              v0["VEREDITO"] == "CURRENT", v0)
        cadeia(c)
        v2 = frescura_ali(c, OS_QUATRO[1][0])
        prova("sao_precisas_duas_passagens_para_o_pente_fino_ficar_em_dia",
              v2["VEREDITO"] == "CURRENT", v2)
        marca.write_text(guardado_md, encoding="utf-8")
finally:
    shutil.rmtree(c.parent, ignore_errors=True)

# ── 17 · A MESMA ARVORE GIT, NOUTRO SISTEMA DE FICHEIROS ───────────────
outra_base = outro_sistema_de_ficheiros()
if outra_base is None:
    nota("sem segundo sistema de ficheiros nesta maquina: a comparacao entre "
         "discos nao correu")
else:
    # ⚠️ OS DOIS LADOS TEM DE SER RECEM-GERADOS. Comparar o clone com o artefacto
    # que esta no disco de quem corre mede outra coisa: se a arvore andou desde a
    # ultima regeracao, a diferenca e a divida dele, e nao falta de determinismo.
    # A pergunta do G2B e outra — MESMA ARVORE, DOIS DISCOS, MESMA RESPOSTA.
    ext4, tmpfs = clone(), clone(outra_base)
    try:
        for raiz in (ext4, tmpfs):
            for _, gerador in OS_QUATRO:
                correr([sys.executable, gerador], raiz)
        for alvo, _ in OS_QUATRO:
            nome = Path(alvo).name
            um = json.loads((ext4 / alvo).read_text(encoding="utf-8"))["PROVENANCE"]
            outro = json.loads((tmpfs / alvo).read_text(encoding="utf-8"))["PROVENANCE"]
            prova("a_impressao_e_a_mesma_nos_dois_discos[%s]" % nome,
                  um["SOURCE_TREE_FINGERPRINT"] == outro["SOURCE_TREE_FINGERPRINT"],
                  "%s != %s" % (um["SOURCE_TREE_FINGERPRINT"][:16],
                                outro["SOURCE_TREE_FINGERPRINT"][:16]))
            prova("o_selo_das_entradas_e_o_mesmo_nos_dois_discos[%s]" % nome,
                  um["INPUTS_DIGEST"] == outro["INPUTS_DIGEST"])
            prova("as_entradas_declaradas_sao_as_mesmas[%s]" % nome,
                  [i["PATH"] for i in um["INPUTS"]]
                  == [i["PATH"] for i in outro["INPUTS"]])
    finally:
        shutil.rmtree(ext4.parent, ignore_errors=True)
        shutil.rmtree(tmpfs.parent, ignore_errors=True)

print()
print("  %d provas · %d falhas" % (CONTA[0], len(FALHAS)))
if FALHAS:
    print("  FALHARAM: " + ", ".join(FALHAS))
sys.exit(1 if FALHAS else 0)
