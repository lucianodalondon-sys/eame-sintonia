#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ENCANAMENTO DA COLETA — pequenos invariantes, cada um com dentes.

    python3 provas/o_encanamento_tem_uma_porta.py

NAO E UM PORTAO GIGANTE. Sao invariantes separados, porque quando dois portoes
partilham resultado o vermelho de um esconde o verde do outro.

O QUE ELES SEGURAM
------------------
    UMA UNIDADE DE INFORMACAO ENTRA UMA VEZ NA COLLECTION.

Cada caso aqui existe porque a coisa que ele proibe JA ACONTECIA, ou porque ela
aconteceria no dia em que alguem ligasse uma peca nova com pressa.
"""
import ast
import io
import json
import os
import re
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import artefato as art          # noqa: E402
import ingresso as ing          # noqa: E402

fora = []


def caso(nome, ok, detalhe=""):
    fora.append((nome, bool(ok), detalhe))
    print("  %-5s %-52s %s" % ("PASS" if ok else "FALHA", nome,
                               "" if ok else detalhe[:110]))


def _codigo(caminho):
    """A fonte sem prosa: comentario e docstring nao sao chamadas."""
    import tokenize
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            texto = f.read()
        pedacos = [t.string for t in tokenize.generate_tokens(io.StringIO(texto).readline)
                   if t.type not in (tokenize.COMMENT, tokenize.STRING)]
        return " ".join(pedacos)
    except (OSError, SyntaxError, IndentationError, tokenize.TokenError):
        return ""


def _coletores():
    """Os ficheiros que COLHEM: vivem em `coleta/` e falam com o mundo."""
    fora_ = []
    d = os.path.join(RAIZ, "coleta")
    for nome in sorted(os.listdir(d)):
        if not nome.endswith(".py") or nome in ("ingresso.py",):
            continue
        c = _codigo(os.path.join(d, nome))
        if any(s in c for s in ("urlopen", "urllib", "requests", "apify_pool")):
            fora_.append("coleta/" + nome)
    return fora_


print("O ENCANAMENTO DA COLETA")
print("=" * 70)

# ── 1 · A PORTA EXISTE, E E UMA SO ─────────────────────────────────────────
caso("P1_a_porta_de_entrada_existe",
     hasattr(ing, "receber") and hasattr(ing, "ficha"),
     "coleta/ingresso.py tem de expor `receber` e `ficha`")

# ── 2 · A PORTA DELEGA AO DONO DO RAW, e nao reimplementa o armazem ────────
# Uma porta que escrevesse ela propria na `raw_asset` seria um SEGUNDO dono do
# RAW, e dois donos do mesmo conceito e o defeito que esta casa mais paga.
c_ing = _codigo(os.path.join(RAIZ, "coleta", "ingresso.py"))
cru_ing = open(os.path.join(RAIZ, "coleta", "ingresso.py"),
               encoding="utf-8").read()
# ⚠️ AQUI LE-SE O FICHEIRO CRU, e nao o codigo-sem-prosa. O SQL vive DENTRO de
# uma string, e um ataque que injectasse `insert into raw_asset` passava
# invisivel pela leitura que tira as strings. Neste caso a string E o risco:
# uma tabela nomeada dentro da porta e a porta a escrever SQL.
# E procura-se SQL, e nao a PALAVRA. O docstring desta porta explica que ela
# «nao sabe como a tabela `raw_asset` e feita por dentro» — e uma frase que diz
# o contrario do defeito seria acusada de o ser.
#
#     UMA FRASE SOBRE UMA TABELA NAO E UMA ESCRITA NUMA TABELA.
#
# O sinal e o VERBO ao lado do nome: `insert into`, `update`, `from <tabela>`.
sql_na_porta = re.findall(
    r"\b(?:insert\s+into|update|delete\s+from|from)\s+(raw_asset|collection_run)\b",
    cru_ing.lower())
caso("P2_a_porta_delega_ao_dono_do_raw",
     re.search(r"\bpreservar\s*\(", c_ing) and not sql_na_porta,
     "a porta chama `preservar()` e NAO conhece a tabela: %s" % sql_na_porta)

# ── 3 · NENHUM COLETOR ESCREVE NO ARMAZEM POR FORA ─────────────────────────
#     COLETOR OBSERVA. PORTA PRESERVA. Um coletor que chama `preservar()` ou
#     que enderec,a o armazem sozinho abre uma segunda entrada.
por_fora = [f for f in _coletores()
            if re.search(r"\bpreservar\s*\(", _codigo(os.path.join(RAIZ, f)))]
caso("P3_nenhum_coletor_preserva_por_fora", not por_fora, ", ".join(por_fora))

# ── 4 · A PORTA NAO JULGA ──────────────────────────────────────────────────
# Ingresso responde «posso preservar?». Admissao responde «pode entrar?». Se a
# porta comec,ar a decidir universo, as duas perguntas viram uma, e a resposta
# deixa de poder ser auditada.
caso("P4_a_porta_nao_decide_admissao",
     not re.search(r"\bdecidir\s*\(", c_ing) and "pronto_para_inteligencia" not in c_ing,
     "a porta de entrada nao pode chamar a admissao")

# ── 5 · A PORTA NAO INVENTA O TEMPO NEM O LUGAR DO FATO ────────────────────
#     FACT_TIME != PUBLICATION_TIME != OBSERVED_TIME != COLLECTED_TIME
#     SOURCE_LOCATION != FACT_LOCATION
f = ing.ficha({"SOURCE_ID": "X", "COUNTRY_SCOPE": "IT", "T": 1},
              corrida={"RUN_ID": "R", "STARTED_AT": "2026-09-09T10:00:00Z"})
caso("P5_fact_time_nao_e_inventado", f.FACT_TIME == art.NAO_SEI, f.FACT_TIME)
caso("P5_fact_location_nao_e_inventado", f.FACT_LOCATION == art.NAO_SEI,
     f.FACT_LOCATION)
caso("P5_collected_at_veio_da_corrida",
     f.COLLECTED_AT == "2026-09-09T10:00:00Z", f.COLLECTED_AT)

# ── 6 · SEM CORRIDA NAO HA RAW ─────────────────────────────────────────────
# Corrida que nao existiu nao se inventa: nao ha `LEGACY-RUN` nem `UNKNOWN-RUN`.
r = ing.receber([{"A": 1}], corrida={"RUN_ID": ""},
                armazem=ing.ArmazemLocal(tempfile.mkdtemp()))
caso("P6_sem_corrida_nao_entra",
     [x["PORQUE"] for x in r["RECUSAS"]] == [ing.SEM_CORRIDA], str(r["RECUSAS"]))

# ── 7 · UM ITEM MAU NAO APAGA A COLHEITA ───────────────────────────────────
d = tempfile.mkdtemp()
r = ing.receber([{}, {"SOURCE_ID": "X", "COUNTRY_SCOPE": "IT", "T": 1}],
                corrida={"RUN_ID": "R7", "STARTED_AT": "2026-09-09T10:00:00Z"},
                armazem=ing.ArmazemLocal(d), raiz=d)
caso("P7_recusa_de_um_nao_derruba_os_outros",
     len(r["ACEITES"]) == 1 and len(r["RECUSAS"]) == 1,
     "aceites %d recusas %d" % (len(r["ACEITES"]), len(r["RECUSAS"])))

# ── 8 · A RECUSA DA PORTA TEM NOME PROPRIO ─────────────────────────────────
#     RECUSA_NA_PORTA != REJEITADO_NA_ADMISSAO != ERRO != NAO_CORREU.
caso("P8_a_recusa_tem_vocabulario_proprio",
     set(ing.RECUSAS) == {ing.SEM_CORRIDA, ing.SEM_CONTEUDO,
                          ing.CONTRATO_QUEBRADO}
     and not (set(ing.RECUSAS) & {"NAO", "ERRO", "NOT_RUN", "REJEITADO"}),
     str(ing.RECUSAS))

# ── 9 · A MESMA ENTRADA DUAS VEZES NAO DUPLICA ─────────────────────────────
# REOBSERVAR != DUPLICAR. O mesmo byte tem a mesma identidade; observa-lo outra
# vez nao cria um segundo objecto.
d = tempfile.mkdtemp()
itens = [{"SOURCE_ID": "X", "COUNTRY_SCOPE": "IT", "T": 1}]
corr = {"RUN_ID": "R9", "STARTED_AT": "2026-09-09T10:00:00Z"}
a1 = ing.receber(itens, corrida=corr, armazem=ing.ArmazemLocal(d), raiz=d)
a2 = ing.receber(itens, corrida=corr, armazem=ing.ArmazemLocal(d), raiz=d)
n = sum(len(fs) for _r, _d, fs in os.walk(d))
caso("P9_reobservar_nao_duplica",
     [x.ARTIFACT_ID for x in a1["ACEITES"]] == [x.ARTIFACT_ID for x in a2["ACEITES"]]
     and n == 1, "ficheiros no armazem: %d" % n)

# ── 10 · O ORQUESTRADOR PASSA PELA PORTA ANTES DA ADMISSAO ─────────────────
# Este e o invariante que fecha o bypass medido: ate esta missao, a colheita ia
# de `a_colheita()` directamente a `pela_porta()` (admissao), sem RAW.
orq = _codigo(os.path.join(RAIZ, "orquestrador", "orquestrador.py"))
fonte_orq = open(os.path.join(RAIZ, "orquestrador", "orquestrador.py"),
                 encoding="utf-8").read()
# ⚠️ DEFINIR NAO E CHAMAR. Este caso dizia PASS com a chamada trocada por
# `pass`, porque `def pela_entrada` continuava no ficheiro e o teste procurava
# o NOME. Agora procura-se a CHAMADA, e por AST — que nao confunde as duas.
_arv = ast.parse(fonte_orq)
_chamadas = {getattr(n.func, "id", getattr(n.func, "attr", ""))
             for n in ast.walk(_arv) if isinstance(n, ast.Call)}
caso("P10_o_orquestrador_chama_a_porta",
     "pela_entrada" in _chamadas and "receber" in _codigo(
         os.path.join(RAIZ, "coleta", "ingresso.py")),
     "o orquestrador tem de CHAMAR a porta, e nao so declara-la")
i_ent = fonte_orq.find("pela_entrada(itens")
i_adm = fonte_orq.find("pela_porta(itens")
caso("P10_a_porta_vem_ANTES_da_admissao",
     0 < i_ent < i_adm, "entrada em %d, admissao em %d" % (i_ent, i_adm))

# ── 11 · O DONO DO RAW CONTINUA A SER UM SO ────────────────────────────────
donos = []
for pasta, _sub, fs in os.walk(RAIZ):
    p = pasta.replace("\\", "/").split("/")
    if any(x in p for x in (".git", "tests", "provas", "node_modules")):
        continue
    for nome in fs:
        if not nome.endswith(".py") or nome in ("preservar_coleta.py",
                                                "memoria_descartavel.py"):
            continue
        cam = os.path.join(pasta, nome)
        if re.search(r"\bpreservar\s*\(", _codigo(cam)):
            donos.append(os.path.relpath(cam, RAIZ).replace("\\", "/"))
caso("P11_um_so_caminho_de_producao_chama_o_raw",
     donos == ["coleta/ingresso.py"], "chamam preservar(): %s" % donos)

print()
maus = [n for n, ok, _ in fora if not ok]
if maus:
    print("ENCANAMENTO=FALHA · %d invariante(s): %s" % (len(maus), ", ".join(maus)))
    raise SystemExit(1)
print("ENCANAMENTO=PASS · %d invariantes, e cada um foi visto a morder" % len(fora))
