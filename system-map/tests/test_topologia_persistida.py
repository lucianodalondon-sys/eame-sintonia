#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DO CENSO DA TOPOLOGIA PERSISTIDO.

    python3 system-map/tests/test_topologia_persistida.py

O censo da topologia publicava 111, 65, 590 e mais catorze numeros, e nao
escrevia ficheiro nenhum.

    STDOUT NAO E MEMORIA DURAVEL.

Agora escreve. E um artefacto que ninguem confere e pior do que nenhum: ele
tem ar de prova. Estas provas nao leem o ficheiro a procura de confirmacao —
elas REGENERAM, ADULTERAM e COMPARAM.

O QUE ESTE FICHEIRO CONFERE
---------------------------
    A  o censo corre
    B  o artefacto nasce — e volta a nascer se alguem o apagar
    C  o esquema esta inteiro
    D  cada COUNT tem MEMBERS, e sao esses
    E  a coleta e os vizinhos de fronteira continuam duas populacoes
    F  duas corridas na mesma arvore dizem o mesmo
    G  a frescura responde, e responde com um dos quatro estados
    H  um artefacto adulterado reprova
    I  uma entrada noutra versao torna o artefacto STALE

    UMA GUARDA QUE NUNCA VIU UM DEFEITO NAO E UMA GUARDA: E UMA FRASE.

Por isso cada regra desta lista e mordida: fabrica-se o defeito que ela devia
apanhar e exige-se que ela reclame. Uma guarda que passa com o defeito na mao
esta a dizer que nao serve.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SCRIPTS = RAIZ / "system-map" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import censo_da_topologia as CENSO                      # noqa: E402
import impressao_da_arvore as IMPRESSAO                 # noqa: E402

ARTEFATO = Path(CENSO.SAIDA)
CADEIA = json.loads((SCRIPTS / "CADEIA-DO-MAPA.json").read_text(encoding="utf-8"))
WORKFLOW = RAIZ / ".github" / "workflows" / "system-map.yml"
ESTADO = RAIZ / "system-map" / "data" / "state.generated.json"

FALHAS = []
CONTA = [0]


def prova(nome, ok, porque=""):
    CONTA[0] += 1
    print(("  PASS  " if ok else "  FAIL  ") + nome
          + (("\n        " + str(porque)) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


def morde(nome, doc, estragar, queixa_esperada):
    """FABRICA O DEFEITO E EXIGE A QUEIXA. Sempre sobre uma COPIA.

        UM BACKUP TIRADO DEPOIS DA MUTACAO NAO E UM BACKUP: E UMA COPIA DO
        DEFEITO.

    A copia e feita por `json.loads(json.dumps(...))` ANTES de `estragar` tocar
    em alguma coisa, e o original nunca sai daqui mexido.
    """
    copia = json.loads(json.dumps(doc, ensure_ascii=False))
    estragar(copia)
    queixas = CENSO.conferir(copia)
    achou = any(queixa_esperada in q for q in queixas)
    prova(nome, achou,
          "esperava uma queixa com %r; vieram: %s" % (queixa_esperada, queixas[:4]))


def onde_diverge(a, b, limite=6):
    """QUE CAMPO MUDOU — porque «a medicao mudou» nao diz onde procurar.

    ⚠️ UMA PROVA QUE SO DIZ «DIFERENTE» MANDA A PROXIMA PESSOA PROCURAR
    NUM FICHEIRO DE 700 KB. Ela sabe a resposta; so nao a estava a dizer.
    """
    fora = []
    for bloco in CENSO.BLOCOS_MEDIDOS:
        x, y = a.get(bloco), b.get(bloco)
        if x == y:
            continue
        if bloco == "FICHAS":
            fx = {f["CARD_ID"]: f for f in x or []}
            fy = {f["CARD_ID"]: f for f in y or []}
            for card in sorted(set(fx) | set(fy)):
                for campo in sorted(set(fx.get(card, {})) | set(fy.get(card, {}))):
                    if fx.get(card, {}).get(campo) != fy.get(card, {}).get(campo):
                        fora.append("FICHAS[%s].%s: %r != %r"
                                    % (card, campo,
                                       fx.get(card, {}).get(campo),
                                       fy.get(card, {}).get(campo)))
                        if len(fora) >= limite:
                            return fora
        elif isinstance(x, dict) and isinstance(y, dict):
            for k in sorted(set(x) | set(y)):
                if x.get(k) != y.get(k):
                    fora.append("%s.%s: %r != %r" % (bloco, k, x.get(k), y.get(k)))
                    if len(fora) >= limite:
                        return fora
        else:
            fora.append("%s difere" % bloco)
    return fora


def clone():
    """UM CLONE DA ARVORE QUE VAI SER COMMITADA, NAO DA QUE JA FOI.

    ⚠️ `git clone` traz o HEAD, e o HEAD nao tem o trabalho por commitar. Uma
    prova que so ve o commit anterior aprova a alteracao que ainda nao existe e
    reprova a que esta na mao de quem a corre — e a licao e a mesma que a
    impressao da arvore ja aprendeu:

        O QUE VAI SER COMMITADO != O QUE JA ESTA RASTREADO.

    Por isso o que o `git status` mostra por commitar e copiado por cima. Numa
    arvore limpa — o CI, sempre — isto nao copia nada.
    """
    d = Path(tempfile.mkdtemp(prefix="topologia-"))
    r = subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--shared",
                        str(RAIZ), str(d / "r")], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("clone falhou: %s" % r.stderr[:300])
    alvo = d / "r"
    sujo = subprocess.run(["git", "status", "--porcelain"], cwd=str(RAIZ),
                          capture_output=True, text=True).stdout.splitlines()
    for linha in sujo:
        estado, caminho = linha[:2], linha[3:].strip().strip('"')
        origem, destino = RAIZ / caminho, alvo / caminho
        if "D" in estado and not origem.exists():
            destino.unlink(missing_ok=True)
        elif origem.is_file():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)
    return alvo


def correr(raiz, *args):
    return subprocess.run([sys.executable, "system-map/scripts/censo_da_topologia.py",
                           *args], cwd=str(raiz), capture_output=True, text=True,
                          encoding="utf-8")


def frescura_ali(raiz):
    """A MESMA `frescura()`, corrida na arvore de la. Sem segunda formula."""
    r = subprocess.run([sys.executable, "-c",
                        "import sys,json;sys.path.insert(0,'system-map/scripts');"
                        "import censo_da_topologia as C;"
                        "print(json.dumps(C.frescura()))"],
                       cwd=str(raiz), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("frescura falhou em %s: %s" % (raiz, r.stderr[-400:]))
    return json.loads(r.stdout)


print("AS PROVAS DO CENSO DA TOPOLOGIA PERSISTIDO")
print("=" * 70)

# ── B · O ARTEFACTO EXISTE ───────────────────────────────────────────────
prova("o_artefato_existe", ARTEFATO.exists(),
      "corra: py system-map/scripts/censo_da_topologia.py")
if not ARTEFATO.exists():
    raise SystemExit(1)
COMMITADO = json.loads(ARTEFATO.read_text(encoding="utf-8"))

# ── C · O ESQUEMA ESTA INTEIRO ───────────────────────────────────────────
prova("o_artefato_commitado_passa_no_proprio_portao", not CENSO.conferir(COMMITADO),
      CENSO.conferir(COMMITADO)[:5])
prova("declara_schema", COMMITADO.get("SCHEMA") == CENSO.SCHEMA, COMMITADO.get("SCHEMA"))
prova("declara_limitacoes_nao_vazias", bool(COMMITADO.get("LIMITATIONS")))

P = COMMITADO.get("PROVENANCE") or {}
for campo in ("GENERATED_BY", "GENERATED_AT", "SOURCE_TREE_FINGERPRINT",
              "INPUTS", "INPUTS_DIGEST", "MEASUREMENT_HASH", "SEMANTIC_HASH"):
    prova("proveniencia_declara_%s" % campo.lower(), bool(P.get(campo)))

# ── K · OS INPUTS SAO OS QUE O CODIGO ABRE, E NAO UMA LISTA DE DESEJOS ───
# Nao basta a lista existir: ela tem de ser a que o censo produz nesta arvore.
# Uma lista escrita a mao envelhece sem ninguem reparar, e proveniencia
# envelhecida e pior do que nenhuma — parece que alguem conferiu.
declarados = {i["PATH"] for i in P.get("INPUTS") or []}
prova("os_dois_generated_que_o_censo_le_estao_nos_inputs",
      {"system-map/data/state.generated.json",
       "system-map/data/architecture.generated.json"} <= declarados,
      sorted(declarados)[:5])
prova("nenhum_input_declarado_falta_ao_disco",
      all((RAIZ / c).is_file() for c in declarados),
      [c for c in sorted(declarados) if not (RAIZ / c).is_file()][:5])
prova("o_artefato_nao_se_declara_entrada_de_si_mesmo",
      "system-map/data/topologia.generated.json" not in declarados)

# ── #9 · UM FICHEIRO QUE CARREGA A IMPRESSAO NAO PODE ESTAR DENTRO DELA ──
prova("o_artefato_esta_fora_da_impressao_da_arvore",
      IMPRESSAO.excluido("system-map/data/topologia.generated.json"),
      "acrescente-o a IMPRESSAO_DA_ARVORE.EXCLUIDO em CADEIA-DO-MAPA.json")

# ── D · CONTAGEM TEM MEMBROS, E A CONTA NAO E A DO PROPRIO ARTEFACTO ─────
# ⚠️ CONFERIR O ARTEFACTO CONTRA ELE PROPRIO NAO E CONFERIR NADA. As tres
# populacoes sao recalculadas AQUI, a partir de `state.generated.json`, com a
# regra de entrada importada do censo. Se o censo passar a contar outra coisa,
# esta prova nao acompanha em silencio: reprova.
S = json.loads(ESTADO.read_text(encoding="utf-8"))
NOS = {n["id"]: n for n in S["NODES"]}
col = sorted(i for i, n in NOS.items() if n.get("family") in CENSO.LADO_DA_COLETA)
toca = set()
for e in S["EDGES"]:
    if e["from"] in set(col):
        toca.add(e["to"])
    if e["to"] in set(col):
        toca.add(e["from"])
viz = sorted(toca - set(col))
exp = sorted(set(col) | toca)

prova("a_coleta_do_artefato_e_a_que_o_estado_diz",
      COMMITADO["UNIVERSE"]["MEMBERS"] == col,
      "%d no artefato, %d no estado" % (COMMITADO["UNIVERSE"]["COUNT"], len(col)))
prova("os_vizinhos_do_artefato_sao_os_que_o_estado_diz",
      COMMITADO["BOUNDARY_NEIGHBORS"]["MEMBERS"] == viz,
      "%d no artefato, %d no estado" % (COMMITADO["BOUNDARY_NEIGHBORS"]["COUNT"], len(viz)))
prova("o_expandido_do_artefato_e_o_que_o_estado_diz",
      COMMITADO["EXPANDED"]["MEMBERS"] == exp)
for bloco in ("UNIVERSE", "BOUNDARY_NEIGHBORS", "EXPANDED"):
    b = COMMITADO[bloco]
    prova("count_igual_a_members_em_%s" % bloco.lower(), b["COUNT"] == len(b["MEMBERS"]))
    prova("%s_declara_especie" % bloco.lower(), bool(b.get("ENTITY_SPECIES")))

# ── E · O VIZINHO NAO VIRA MEMBRO DA COLETA ──────────────────────────────
prova("coleta_e_fronteira_nao_partilham_um_membro",
      not (set(COMMITADO["UNIVERSE"]["MEMBERS"])
           & set(COMMITADO["BOUNDARY_NEIGHBORS"]["MEMBERS"])))
A = COMMITADO["ARITMETICA"]
prova("a_aritmetica_fecha", A["COLLECTION"] + A["BOUNDARY"] == A["EXPANDED"] and A["FECHA"],
      A)
prova("as_duas_populacoes_tem_ids_de_universo_diferentes",
      COMMITADO["UNIVERSE"]["UNIVERSE_ID"] != COMMITADO["BOUNDARY_NEIGHBORS"]["UNIVERSE_ID"])

# ── AS ARESTAS CONTINUAM NO MODELO G1 ────────────────────────────────────
#     ANALISE ESTATICA PROVA CAN DO. SO TELEMETRIA PROVA DID DO.
# Achatar isto num `status=PROVEN` era desfazer o G1 dentro do G2, em silencio.
arestas = COMMITADO["EDGES"]["MEMBERS"]
prova("edges_count_igual_a_members", COMMITADO["EDGES"]["COUNT"] == len(arestas))
prova("cada_aresta_carrega_os_quatro_planos",
      all(all(a.get(p) in ("YES", "NO", "UNKNOWN") for p in CENSO.PLANOS) for a in arestas))
prova("nenhuma_aresta_voltou_a_ter_status_como_verdade_unica",
      not any("status" in a for a in arestas))
prova("a_evidencia_continua_a_dizer_que_afirmacao_sustenta",
      all(all("ASSERTION_EDGE_ID" in v and "SUPPORTS" in v
              for v in a.get("EVIDENCE_BINDING") or []) for a in arestas))
esperadas = sorted("%s--%s-->%s" % (e["from"], e["type"], e["to"]) for e in S["EDGES"]
                   if e["from"] in set(exp) or e["to"] in set(exp))
prova("as_arestas_do_artefato_sao_as_que_o_estado_diz",
      sorted(a["EDGE_ID"] for a in arestas) == esperadas,
      "%d no artefato, %d no estado" % (len(arestas), len(esperadas)))

# ── G · A FRESCURA RESPONDE, E COM UM DOS QUATRO ESTADOS ─────────────────
F = CENSO.frescura(COMMITADO)
prova("a_frescura_responde_com_um_dos_quatro_estados",
      F["VEREDITO"] in ("CURRENT", "STALE", "UNVERIFIABLE", "UNKNOWN"), F["VEREDITO"])
prova("o_artefato_commitado_e_desta_arvore", F["VEREDITO"] == "CURRENT",
      "%s · %s" % (F["VEREDITO"], F.get("PORQUE")))

# ── #8 · O ATAQUE DO STALE FALSO ─────────────────────────────────────────
# Mudar so `GENERATED_AT` nao pode mover nada: ele e volatil por declaracao do
# proprio artefacto. Um relogio que acusa stale por causa da hora e um relogio
# que ensina a gente a ignorar o alarme.
copia = json.loads(json.dumps(COMMITADO, ensure_ascii=False))
copia["PROVENANCE"]["GENERATED_AT"] = "1999-01-01T00:00:00+00:00"
prova("mexer_so_no_relogio_nao_inventa_stale",
      CENSO.frescura(copia)["VEREDITO"] == F["VEREDITO"])
prova("mexer_so_no_relogio_nao_move_o_hash_semantico",
      CENSO.hash_semantico(copia) == CENSO.hash_semantico(COMMITADO))
prova("generated_at_esta_declarado_como_volatil",
      "GENERATED_AT" in (P.get("CAMPOS_VOLATEIS") or []))

# ── OS TRES RELOGIOS, MORDIDOS UM A UM ──────────────────────────────────
# ⚠️ A MUTACAO ENCONTROU ISTO, E VALE A PENA ESCREVE-LO. As provas de frescura
# corriam todas sobre uma arvore mexida — e numa arvore mexida OS TRES relogios
# tocam ao mesmo tempo. Apagar um deles nao reprovava nada: os outros dois
# tapavam o buraco, e a prova dizia PASS sobre uma guarda que ja nao existia.
#
#     TRES ALARMES QUE SO SE TESTAM JUNTOS SAO UM ALARME SO,
#     COM TRES INTERRUPTORES E NENHUM TESTADO.
#
# Aqui cada relogio e mordido SOZINHO, mexendo no carimbo que so ele le.
for carimbo, nome in (("SOURCE_TREE_FINGERPRINT", "a_impressao_de_outra_arvore"),
                      ("INPUTS_DIGEST", "um_selo_de_entradas_diferente")):
    so_este = json.loads(json.dumps(COMMITADO, ensure_ascii=False))
    so_este["PROVENANCE"][carimbo] = "0" * 64
    veredito = CENSO.frescura(so_este)
    prova("%s_torna_o_artefato_stale" % nome, veredito["VEREDITO"] == "STALE",
          veredito)

# E o terceiro: uma entrada gerada que carimba outra arvore, com o resto intacto.
so_ciclo = json.loads(json.dumps(COMMITADO, ensure_ascii=False))
prova("o_relogio_do_ciclo_atrasado_existe_e_esta_ligado",
      "ENTRADAS_GERADAS_DE_OUTRA_ARVORE" in CENSO.frescura(so_ciclo))

# ── H · O ARTEFACTO ADULTERADO REPROVA — UMA MORDIDA POR REGRA ───────────
morde("apanha_count_sem_members",
      COMMITADO, lambda d: d["UNIVERSE"].update(COUNT=d["UNIVERSE"]["COUNT"] + 1),
      "UNIVERSE.COUNT")
morde("apanha_membro_removido_com_count_intacto",
      COMMITADO, lambda d: d["UNIVERSE"]["MEMBERS"].pop(0), "UNIVERSE.COUNT")
morde("apanha_membro_duplicado",
      COMMITADO, lambda d: d["UNIVERSE"]["MEMBERS"].append(d["UNIVERSE"]["MEMBERS"][0]),
      "duplicado")
morde("apanha_vizinho_contado_como_coleta",
      COMMITADO, lambda d: d["UNIVERSE"]["MEMBERS"].append(
          d["BOUNDARY_NEIGHBORS"]["MEMBERS"][0]), "VIZINHO_CONTADO_COMO_COLETA")
morde("apanha_aresta_duplicada",
      COMMITADO, lambda d: d["EDGES"]["MEMBERS"].append(d["EDGES"]["MEMBERS"][0]),
      "EDGE_ID duplicado")
morde("apanha_membros_fora_de_ordem",
      COMMITADO, lambda d: d["UNIVERSE"]["MEMBERS"].reverse(), "fora de ordem")
morde("apanha_schema_trocado",
      COMMITADO, lambda d: d.update(SCHEMA="sintonia.qualquer-coisa/9"), "SCHEMA=")
morde("apanha_bloco_inteiro_apagado",
      COMMITADO, lambda d: d.pop("BOUNDARY_NEIGHBORS"), "BLOCO_EM_FALTA")
morde("apanha_plano_fora_do_vocabulario",
      COMMITADO, lambda d: d["EDGES"]["MEMBERS"][0].update(OBSERVED="TALVEZ"),
      "plano fora do vocabulario")
morde("apanha_edge_id_que_nao_descreve_a_aresta",
      COMMITADO, lambda d: d["EDGES"]["MEMBERS"][0].update(TO="C-INVENTADO"),
      "EDGE_ID nao descreve")
morde("apanha_proveniencia_amputada",
      COMMITADO, lambda d: d["PROVENANCE"].pop("INPUTS_DIGEST"),
      "PROVENANCE sem INPUTS_DIGEST")
morde("apanha_input_com_versao_mexida",
      COMMITADO, lambda d: d["PROVENANCE"]["INPUTS"][0].update(VERSAO="0" * 40),
      "INPUTS_DIGEST nao e o selo")
morde("apanha_ficha_removida",
      COMMITADO, lambda d: d["FICHAS"].pop(), "FICHAS nao cobrem")
morde("apanha_resumo_a_discordar_das_arestas",
      COMMITADO, lambda d: d["RESUMO"].update(ARESTAS_RELACIONADAS=1),
      "RESUMO.ARESTAS_RELACIONADAS")
morde("apanha_limitacoes_apagadas",
      COMMITADO, lambda d: d.update(LIMITATIONS=[]), "LIMITATIONS vazio")
morde("apanha_medicao_mexida_a_mao",
      COMMITADO, lambda d: d["RESUMO"].update(TRAVESSIAS_QUE_LEVAM_DADO=99),
      "MEASUREMENT_HASH nao bate")

morde("apanha_texto_reescrito_fora_da_medicao",
      COMMITADO, lambda d: d["NOTA"].append("uma linha que gerador nenhum escreveu"),
      "SEMANTIC_HASH nao bate")

# Uma mordida que tem de NAO reclamar: a copia intacta.
prova("a_copia_intacta_nao_e_acusada_de_nada",
      not CENSO.conferir(json.loads(json.dumps(COMMITADO, ensure_ascii=False))))

# ── OS DOIS NUMEROS SAO DOIS, E CADA UM RESPONDE PELO SEU ───────────────
# Um hash que nunca muda passa em toda a comparacao que se lhe faca — e uma
# comparacao entre dois numeros constantes da sempre igual. Aqui exige-se
# SENSIBILIDADE a um e INSENSIBILIDADE ao outro, na mesma mordida:
#
#     MEXER NA MEDICAO   move MEASUREMENT_HASH e SEMANTIC_HASH
#     MEXER NO TEXTO     move SEMANTIC_HASH e SO ELE
medido = json.loads(json.dumps(COMMITADO, ensure_ascii=False))
medido["RESUMO"]["CARTOES_NO_UNIVERSO"] = 0
prova("mexer_na_medicao_move_o_hash_da_medicao",
      CENSO.hash_da_medicao(medido) != P.get("MEASUREMENT_HASH"))
prova("mexer_na_medicao_tambem_move_o_hash_semantico",
      CENSO.hash_semantico(medido) != CENSO.hash_semantico(COMMITADO))
textual = json.loads(json.dumps(COMMITADO, ensure_ascii=False))
textual["NOTA"] = ["outra coisa"]
prova("mexer_so_no_texto_move_o_hash_semantico",
      CENSO.hash_semantico(textual) != CENSO.hash_semantico(COMMITADO))
prova("mexer_so_no_texto_nao_move_o_hash_da_medicao",
      CENSO.hash_da_medicao(textual) == P.get("MEASUREMENT_HASH"))

# ── #10 · O STDOUT E O ARTEFACTO, E NAO UM PRIMO DELE ───────────────────
r = correr(RAIZ, "--json", "--nao-escrever")
prova("o_censo_corre", r.returncode == 0, r.stderr[-300:])
if r.returncode == 0:
    saida = json.loads(r.stdout)
    prova("o_stdout_mede_o_mesmo_que_o_ficheiro",
          CENSO.hash_da_medicao(saida) == P.get("MEASUREMENT_HASH"),
          onde_diverge(COMMITADO, saida))
    prova("o_stdout_traz_o_artefacto_inteiro",
          set(saida) == set(COMMITADO), sorted(set(saida) ^ set(COMMITADO)))
    prova("nao_escrever_nao_escreve",
          json.loads(ARTEFATO.read_text(encoding="utf-8"))[
              "PROVENANCE"]["GENERATED_AT"] == P["GENERATED_AT"])

# ── ANTI-DRIFT · O COMMITADO E O QUE ESTA ARVORE PRODUZ HOJE ────────────
if r.returncode == 0:
    prova("o_artefato_commitado_e_o_que_esta_arvore_mede_hoje",
          CENSO.hash_da_medicao(json.loads(r.stdout)) == P.get("MEASUREMENT_HASH"),
          "corra: py system-map/scripts/censo_da_topologia.py · "
          + str(onde_diverge(COMMITADO, json.loads(r.stdout))))

# ── #15 · A PERSISTENCIA TEM DE ESTAR GARANTIDA POR ALGUEM ──────────────
# O artefacto so continua a existir porque alguma corrida o refaz. Se o passo do
# workflow desaparecer, ou passar a correr com `--nao-escrever`, o ficheiro
# congela e ninguem repara — ele continua la, com ar de recente.
linhas = [l.strip() for l in WORKFLOW.read_text(encoding="utf-8").splitlines()
          if "censo_da_topologia.py" in l and not l.strip().startswith("#")]
prova("o_workflow_corre_o_censo", bool(linhas), "nenhuma linha no workflow")
prova("o_workflow_nao_corre_o_censo_com_a_persistencia_desligada",
      all("--nao-escrever" not in l for l in linhas), linhas)

# ── A · F · I · O QUE SO SE PROVA NOUTRA ARVORE ─────────────────────────
# Tudo o que segue mexe em ficheiros. Mexe num CLONE DESCARTAVEL, sempre:
# uma prova que suja a arvore de quem a corre muda aquilo que mede.
if "--sem-clone" in sys.argv:
    print("  ----  (as provas de clone ficam de fora: corrida aninhada)")
    print()
    print("  %d provas · %d falhas" % (CONTA[0], len(FALHAS)))
    if FALHAS:
        print("  FALHARAM: " + ", ".join(FALHAS))
    sys.exit(1 if FALHAS else 0)

c = clone()
try:
    # B · o artefacto volta a nascer depois de apagado (#13)
    (c / "system-map" / "data" / "topologia.generated.json").unlink()
    antes = frescura_ali(c)
    prova("sem_artefato_a_frescura_diz_unknown", antes["VEREDITO"] == "UNKNOWN", antes)
    x1 = correr(c, "--json")
    prova("o_censo_corre_no_clone", x1.returncode == 0, x1.stderr[-300:])
    prova("o_artefato_volta_a_nascer",
          (c / "system-map" / "data" / "topologia.generated.json").exists())

    # ── A MEDICAO NAO PODE DEPENDER DE ONDE A ARVORE ESTA ────────────────
    # O censo varre o repositorio com `grep -r`, e a ordem de travessia do
    # `grep` e do sistema de ficheiros, nao do codigo. Se a medicao dependesse
    # dessa ordem, ela batia aqui e falhava no CI — noutra maquina, noutro
    # disco, noutra ordem. Esta prova mede o mesmo conteudo NOUTRA PASTA.
    #
    #     DETERMINISTICO NA MESMA PASTA NAO E DETERMINISTICO.
    if x1.returncode == 0:
        prova("a_medicao_e_a_mesma_noutra_pasta",
              json.loads(x1.stdout)["PROVENANCE"]["MEASUREMENT_HASH"]
              == P.get("MEASUREMENT_HASH"),
              "a medicao mudou so por a arvore estar noutro sitio: "
              + str(onde_diverge(COMMITADO, json.loads(x1.stdout))))

    # F · determinismo: duas corridas, a mesma arvore, o mesmo conteudo
    x2 = correr(c, "--json")
    if x1.returncode == 0 and x2.returncode == 0:
        d1, d2 = json.loads(x1.stdout), json.loads(x2.stdout)
        prova("duas_corridas_medem_o_mesmo",
              d1["PROVENANCE"]["MEASUREMENT_HASH"] == d2["PROVENANCE"]["MEASUREMENT_HASH"])
        prova("duas_corridas_dizem_o_mesmo_sem_os_campos_volateis",
              CENSO.hash_semantico(d1) == CENSO.hash_semantico(d2))
        prova("e_o_relogio_andou_entre_as_duas",
              d1["PROVENANCE"]["GENERATED_AT"] <= d2["PROVENANCE"]["GENERATED_AT"])

    # G · acabado de gerar, na arvore dele, o veredito e CURRENT
    recem = frescura_ali(c)
    prova("acabado_de_gerar_o_artefato_e_current",
          recem["VEREDITO"] == "CURRENT", recem)

    # I · uma entrada noutra versao torna o artefacto STALE
    #     Duas entradas, dois caminhos diferentes ate ao mesmo veredito.
    alvo = c / "system-map" / "data" / "state.generated.json"
    guardado = alvo.read_text(encoding="utf-8")      # lido ANTES de mutar
    d = json.loads(guardado)
    d["PROVENANCE"]["SOURCE_TREE_FINGERPRINT"] = "f" * 64
    alvo.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    depois = frescura_ali(c)
    prova("entrada_gerada_noutra_arvore_torna_o_artefato_stale",
          depois["VEREDITO"] == "STALE" and depois.get("MOTIVO") == "STALE_BY_CYCLE",
          depois)
    alvo.write_text(guardado, encoding="utf-8")
    prova("reposta_a_entrada_o_artefato_volta_a_current",
          frescura_ali(c)["VEREDITO"] == "CURRENT")

    fonte = c / "system-map" / "scripts" / "censo_da_topologia.py"
    original = fonte.read_text(encoding="utf-8")     # lido ANTES de mutar
    fonte.write_text(original + "\n# uma fonte que mudou depois da medicao\n",
                     encoding="utf-8")
    mexida = frescura_ali(c)
    prova("fonte_mexida_depois_da_medicao_torna_o_artefato_stale",
          mexida["VEREDITO"] == "STALE", mexida)
    fonte.write_text(original, encoding="utf-8")

    # UNVERIFIABLE TAMBEM E UM DOS QUATRO, E TEM DE SER ALCANCAVEL
    # Um artefacto ilegivel nao pode responder CURRENT nem STALE: nenhuma das
    # duas se consegue verificar. Dizer STALE seria adivinhar o lado errado.
    art = c / "system-map" / "data" / "topologia.generated.json"
    bom = art.read_text(encoding="utf-8")            # lido ANTES de mutar
    art.write_text(bom[:len(bom) // 2], encoding="utf-8")
    partido = frescura_ali(c)
    prova("um_artefato_ilegivel_diz_unverifiable",
          partido["VEREDITO"] == "UNVERIFIABLE", partido)
    art.write_text(bom, encoding="utf-8")

    # E UMA ESCRITA INTERROMPIDA NAO PODE DEIXAR ISSO NO LUGAR DO ARTEFACTO
    prova("a_escrita_nao_deixa_ficheiro_a_meio_no_lugar_do_artefato",
          "os.replace" in (RAIZ / "system-map" / "scripts"
                           / "censo_da_topologia.py").read_text(encoding="utf-8"),
          "escrever() tem de trocar o ficheiro de uma vez, nao escrever por cima")

    # #12 · JSON adulterado a mao, no disco, e apanhado por quem o le
    inteiro = art.read_text(encoding="utf-8")        # lido ANTES de mutar
    adulterado = json.loads(inteiro)
    adulterado["RESUMO"]["CARTOES_NO_UNIVERSO"] = 9999
    art.write_text(json.dumps(adulterado, ensure_ascii=False), encoding="utf-8")
    # `--sem-clone` e o travao da recursao: sem ele esta corrida clonava outra
    # vez, e essa outra vez clonava outra vez.
    y = subprocess.run([sys.executable, "system-map/tests/test_topologia_persistida.py",
                        "--sem-clone"],
                       cwd=str(c), capture_output=True, text=True, encoding="utf-8")
    prova("um_artefato_adulterado_no_disco_reprova_a_propria_prova",
          y.returncode != 0, "a prova passou com o ficheiro mexido")
    art.write_text(inteiro, encoding="utf-8")
finally:
    shutil.rmtree(c.parent, ignore_errors=True)

print()
print("  %d provas · %d falhas" % (CONTA[0], len(FALHAS)))
if FALHAS:
    print("  FALHARAM: " + ", ".join(FALHAS))
sys.exit(1 if FALHAS else 0)
