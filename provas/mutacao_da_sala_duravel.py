#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTAÇÃO — as leis da sala durável e do preflight mordem, ou não existem.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5432/descartavel \\
        python3 provas/mutacao_da_sala_duravel.py

POR QUE ISTO EXISTE
-------------------
Uma bateria verde prova que o código de hoje passa. Não prova que ela REPROVA
quando a lei é quebrada — e uma prova que não reprova é decoração.

    UMA PROVA QUE NAO MORDE NAO E UMA PROVA. E UM COMENTARIO VERDE.

Cada mutante quebra UMA lei desta missão numa cópia descartável da árvore. Se a
bateria continuar verde com a lei partida, o sobrevivente está a dizer que
aquela lei não tem guarda nenhum.

O QUE NAO CONTA COMO MORTE
--------------------------
Um mutante que rebenta por erro de sintaxe, ou que faz a árvore nascer vermelha
por outra razão, não prova nada. Por isso a cópia é medida VERDE antes de
qualquer mutação.
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SALA = os.path.join("admissao", "sala_de_espera.py")
REDE = os.path.join("superficie", "rede.py")
MIGR = os.path.join("supabase", "migrations",
                    "031_a_sala_de_espera_ganha_dono_duravel.sql")
FLUXO = os.path.join(".github", "workflows", "sintonia-scrap.yml")

PROVA_SALA = os.path.join("provas", "a_sala_sobrevive_ao_processo.py")
PROVA_EGRESSO = os.path.join("provas", "o_egresso_antes_da_aquisicao.py")

# (nome, ficheiro, velho, novo, prova que tem de reprovar, que lei se quebrou)
MUTANTES = [
    # ⚠️ A PRIMEIRA VERSAO DESTE MUTANTE SOBREVIVEU, E NAO POR A LEI SER FRACA.
    # Ela trocava `if escolhido == POSTGRES:` por `if escolhido == POSTGRES and
    # _dsn():` — e sem DSN o fluxo caia no ramo final, que levanta
    # `SalaIndisponivel` por «backend desconhecido». Continuava a FALHAR FECHADO.
    #
    #     UM MUTANTE QUE NAO MUDA O COMPORTAMENTO NAO MEDE A LEI: MEDE O TEXTO.
    #
    # O mutante certo e o que constroi mesmo a queda silenciosa.
    ("M1 · a sala cai para ficheiro quando nao ha DSN", SALA,
     """            raise SalaIndisponivel(
                "SINTONIA_SALA_BACKEND=POSTGRES sem DSN. Defina SINTONIA_SALA_DSN """,
     """            return _Ficheiro()
        if False:
            raise SalaIndisponivel(
                "SINTONIA_SALA_BACKEND=POSTGRES sem DSN. Defina SINTONIA_SALA_DSN """,
     PROVA_SALA,
     "o fallback silencioso para disco efemero — a falha original com outro nome"),

    # ⚠️ O SEGUNDO MUTANTE DA PRIMEIRA VERSAO TAMBEM SOBREVIVEU, E PELA MESMA
    # RAZAO: ele alargava a chave primaria de `(run_id, ordem)` para
    # `(run_id, ordem, item_id)`. Como `ordem` ja e unica dentro da corrida, a
    # unicidade nao mudava — mutante no-op, e trocado por um que morde a lei da
    # fila, que e a que a `§18` desta missao veio fechar.
    ("M2 · o item retirado continua a aparecer nos pendentes", SALA,
     """               "where estado_da_fila = %s order by pousado_em, run_id, ordem"
               % _lit(A_ESPERA))""",
     """               "where estado_da_fila is not null order by pousado_em, run_id, ordem")""",
     PROVA_SALA,
     "WAITING -> NOT_WAITING deixa de existir: a fila passa a ser eterna"),

    ("M3 · a escrita deixa de ser UMA transacao", SALA,
     '"-v", "ON_ERROR_STOP=1", "--single-transaction", self.url, "-f", "-"',
     '"-v", "ON_ERROR_STOP=1", self.url, "-f", "-"',
     PROVA_SALA,
     "sem transacao, metade da corrida fica pousada depois de um erro a meio"),

    ("M4 · o conflito passa a reaproveitar em silencio", SALA,
     """  elsif ja = {sha} then""",
     """  elsif true then""",
     PROVA_SALA,
     "last-write-wins silencioso: uma corrida a contar duas historias"),

    ("M5 · o recibo sai antes de o banco confirmar", SALA,
     """        codigo, saida, erro = self._executar(script)""",
     """        codigo, saida, erro = (0, POUSOU, "")
        self._executar(script)""",
     PROVA_SALA,
     "devolver READY antes de persistir e prometer o que ninguem guardou"),

    ("M6 · o contrato READY passa a aceitar 11 campos", SALA,
     """        faltam = [c for c in CAMPOS_READY if c not in u]""",
     """        faltam = []""",
     PROVA_SALA,
     "COL-LAW-043 fixa 12 campos; 11 e um READY sem linhagem"),

    ("M7 · a trava por corrida desaparece", SALA,
     "  perform pg_advisory_xact_lock(hashtext({run}));",
     "  -- sem trava",
     PROVA_SALA,
     "dois escritores da mesma corrida deixam de ser serializados"),

    ("M8 · a chave estrangeira da observacao cai", MIGR,
     "  raw_observation_id  bigint references public.raw_asset(id) on delete restrict,",
     "  raw_observation_id  bigint,",
     PROVA_SALA,
     "um READY passa a poder apontar para uma observacao que nao existe"),

    ("M9 · UNKNOWN no egresso passa a deixar passar", REDE,
     "    passa = medido == str(exigido).strip().upper()",
     "    passa = medido in (str(exigido).strip().upper(), EGRESSO_DESCONHECIDO)",
     PROVA_EGRESSO,
     "UNKNOWN != IT: adquirir sobre ambiente por medir"),

    ("M10 · o egresso aceita qualquer pais", REDE,
     "    e['EGRESS_GATE'] = 'PASS' if passa else 'BLOCKED'",
     "    e['EGRESS_GATE'] = 'PASS'",
     PROVA_EGRESSO,
     "o portao deixa de fechar"),

    ("M11 · o portao do egresso desaparece do workflow", FLUXO,
     "          PYTHONIOENCODING=utf-8 $PY superficie/rede.py --portao-de-egresso IT",
     "          echo 'egresso: confio'",
     PROVA_EGRESSO,
     "MODULE EXISTS != EDGE EXISTS: um portao que ninguem chama nao e um portao"),

    ("M12b · o portao da sala corre DEPOIS da aquisicao", FLUXO,
     "          PYTHONIOENCODING=utf-8 $PY admissao/sala_de_espera.py --portao",
     "          echo 'a sala fica para depois'",
     PROVA_EGRESSO,
     "um portao depois da porta nao e um portao"),

    ("M12 · o ambiente aprovado deixa de ser o da aquisicao", FLUXO,
     "      SINTONIA_SALA_BACKEND: POSTGRES",
     "      SINTONIA_SALA_BACKEND_DESLIGADO: POSTGRES",
     PROVA_EGRESSO,
     "o preflight aprovaria um ambiente e a aquisicao correria noutro"),

    ("M13 · o IP publico passa a viajar no resultado", REDE,
     """    fora = {'EGRESS_COUNTRY_CODE': EGRESSO_DESCONHECIDO,
            'CHECKED_AT': quando, 'CHECKER': CHECKER_DE_EGRESSO}""",
     """    fora = {'EGRESS_COUNTRY_CODE': EGRESSO_DESCONHECIDO,
            'CHECKED_AT': quando, 'CHECKER': CHECKER_DE_EGRESSO,
            'IP': (json.loads(bruto).get('ip') if bruto else None)}""",
     PROVA_EGRESSO,
     "registar mais do que foi perguntado"),

    ("M14 · a retirada deixa de exigir autor", SALA,
     """        if not por or not str(por).strip():
            raise ValueError("retirar sem autor nao e retirar: `por` vazio")""",
     """        por = por or "alguem\"""",
     PROVA_SALA,
     "RETIRAR E UM ACTO COM AUTOR, OU NAO E UM ACTO"),

    ("M15 · o ITEM_ID ambiguo passa a retirar um a sorte", SALA,
     """        if len(alvo) > 1:""",
     """        if False:""",
     PROVA_SALA,
     "retirar «o item ?» quando ha dois e retirar a sorte"),

    ("M16 · a lista vazia passa a criar registo", SALA,
     """    if not unidades:
        return {"ESTADO": None,""",
     """    if False:
        return {"ESTADO": None,""",
     PROVA_SALA,
     "zero admitidos a dizer «esta corrida chegou a espera»"),
]


def _copia(destino):
    pesadas = {".git", "data", "node_modules", "italia-portale", "__pycache__",
               ".tmp", "build"}
    for nome in os.listdir(RAIZ):
        if nome in pesadas:
            continue
        o, a = os.path.join(RAIZ, nome), os.path.join(destino, nome)
        if os.path.isdir(o):
            shutil.copytree(o, a, symlinks=True,
                            ignore=shutil.ignore_patterns("__pycache__",
                                                          "node_modules"))
        else:
            shutil.copy2(o, a)
    for nome in (".git", "data"):
        os.symlink(os.path.join(RAIZ, nome), os.path.join(destino, nome))


def _banco_novo(admin_url, nome):
    """Cada mutante leva um banco NOVO.

    ⚠️ E ISSO NÃO É LUXO: o livro-razão da cadeia canónica guarda o SHA de cada
    migration aplicada. Um mutante que edita a `031` sobre um banco onde ela já
    entrou seria recusado pela trava de drift — e a recusa seria lida como morte
    do mutante quando na verdade ele nem chegou a correr.
    """
    subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", admin_url,
                    "-c", 'drop database if exists "%s";' % nome],
                   capture_output=True, text=True)
    r = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", admin_url,
                        "-c", 'create database "%s";' % nome],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("nao consegui criar banco do mutante: %s" % r.stderr[:300])
    base = admin_url.rsplit("/", 1)[0]
    return "%s/%s" % (base, nome)


def _correr(arvore, prova, url):
    amb = dict(os.environ, BANCO_DESCARTAVEL_URL=url)
    amb.pop("SINTONIA_SALA_BACKEND", None)
    amb.pop("SINTONIA_SALA_DSN", None)
    p = subprocess.run([sys.executable, prova], cwd=arvore,
                       capture_output=True, text=True, timeout=900, env=amb)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    admin = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not admin:
        print("BANCO_DESCARTAVEL_URL nao definido · NOT_RUN. NOT_RUN NAO E PASS.")
        return 0
    print("MUTAÇÃO · A SALA DURÁVEL E O PREFLIGHT DE EGRESSO")
    print("=" * 74)
    base = tempfile.mkdtemp(prefix="sala-mut-")
    arvore = os.path.join(base, "arvore")
    os.makedirs(arvore)
    sobreviventes, mortos = [], []
    try:
        _copia(arvore)
        # ── A ÁRVORE NASCE VERDE? ──────────────────────────────────────
        url0 = _banco_novo(admin, "mut_base")
        for prova in (PROVA_SALA, PROVA_EGRESSO):
            codigo, saida = _correr(arvore, prova, url0)
            if codigo != 0:
                print("A CÓPIA JÁ NASCE VERMELHA em %s — a mutação não mediria "
                      "nada." % prova)
                print(saida[-2500:])
                return 3
        print("a copia nasce VERDE nas duas baterias. comeca a mutacao.\n")

        for i, (nome, ficheiro, velho, novo, prova, lei) in enumerate(MUTANTES):
            caminho = os.path.join(arvore, ficheiro)
            with open(caminho, encoding="utf-8") as f:
                original = f.read()
            if velho not in original:
                print("  %-56s ANCORA PERDIDA" % nome)
                print("     o texto que este mutante corta ja nao existe. "
                      "Isto NAO e uma morte.")
                sobreviventes.append((nome, "ancora perdida", lei))
                continue
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(original.replace(velho, novo, 1))
            try:
                url = _banco_novo(admin, "mut_%02d" % i)
                codigo, saida = _correr(arvore, prova, url)
            finally:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(original)
            if codigo != 0:
                mortos.append(nome)
                print("  %-56s MORTO" % nome)
            else:
                sobreviventes.append((nome, "a bateria continuou verde", lei))
                print("  %-56s SOBREVIVEU" % nome)
                print("     lei sem guarda: %s" % lei)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print()
    print("=" * 74)
    print("MUTANTES=%d · MORTOS=%d · SOBREVIVENTES=%d"
          % (len(MUTANTES), len(mortos), len(sobreviventes)))
    for nome, porque, lei in sobreviventes:
        print("  · %s — %s" % (nome, porque))
    print("MUTANTES_MORTOS=%s" % ("ALL" if not sobreviventes else "NAO"))
    print("=" * 74)
    return 1 if sobreviventes else 0


if __name__ == "__main__":
    raise SystemExit(main())
