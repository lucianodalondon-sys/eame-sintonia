#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FRONTEIRA ENTRE A COLETA E A INTELIGENCIA — medida, e nao afirmada.

    python3 provas/a_fronteira_da_coleta.py

POR QUE ISTO EXISTE
-------------------
Tres sitios desta arvore dizem coisas DIFERENTES sobre o mesmo READY, e
nenhum deles estava errado por descuido — cada um foi escrito num momento em
que era verdade, e ninguem tinha um medidor para os confrontar:

    BIBLIA-CANONICA-DA-COLETA.md · COL-LAW-043
        READY e canonico, o contrato de saida e FIXO e tem 11 campos.
        IT: PARTIAL.

    docs/operacao/CENSO-DOS-CONTRATOS-DE-ARTEFATO.md:110
        «E este o READY desta casa (...) ja tem consumidor.»

    coleta/derivacao_forward.py · GAPS
        «READY_NAO_TEM_DONO — nenhuma peca decide que um derivado esta
        PRONTO.»

O primeiro esta certo. Os outros dois exageram, em direccoes opostas: um diz
que ha consumidor e nao ha nenhum; o outro diz que nao ha dono e ha um, com
nome e linha.

    DECLARADO != IMPLEMENTADO != PRODUZIDO != CONSUMIDO.

Sao quatro perguntas, e achata-las em «existe / nao existe» e como se perdeu
a conta. Esta prova responde as quatro, separadas, e deixa de ser preciso
acreditar em qualquer dos tres textos.

O QUE ELA GUARDA (e faz falhar)
-------------------------------
    F1  a lei existe e declara os campos
    F2  o codigo devolve EXACTAMENTE esses campos — nem mais, nem menos
    F3  ha UM dono, e nao dois: ninguem constroi o registo READY fora dele
    F4  a porta recusa o que nao passou

O QUE ELA MEDE E RELATA, SEM FALHAR
-----------------------------------
    quem PRODUZ o registo (runtime? CLI? so teste?)
    quem CONSOME o registo
    quantas outras saidas existem a competir com esta

Nao falha por nao haver consumidor. Isso e um buraco DECLARADO, e o trabalho
desta prova e MEDI-LO — nao fingir que uma lacuna arquitectural e um bug de
codigo. Fazer esta prova ficar verde a inventar um consumidor seria a mesma
doenca que ela veio diagnosticar.

    UM BURACO MEDIDO E UMA DIVIDA COM NOME.
    UM BURACO PINTADO DE VERDE E UMA MENTIRA COM TESTE.
"""
import io
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao  # noqa: E402

BIBLIA = os.path.join(RAIZ, "BIBLIA-CANONICA-DA-COLETA.md")
LEI = "COL-LAW-043"

# Onde a coleta vive. `italia-portale/` e portal, `system-map/` e instrumento.
PASTAS_DA_COLETA = ('coleta', 'guarda', 'admissao', 'leis', 'medidas', 'motor',
                    'fontes', 'candidatas', 'ferramentas', 'orquestrador',
                    'portoes', 'pacote', 'pedido', 'regras', 'superficie')

fora = []


def caso(nome, ok, detalhe=""):
    fora.append((nome, bool(ok), detalhe))
    return bool(ok)


def campos_da_lei():
    """Os campos que a BIBLIA declara para o contrato de saida.

    Lidos do bloco de codigo da COL-LAW-043 — e nao copiados para ca. Copiar
    faria os dois divergirem em silencio, que e o defeito que esta casa mais
    repete.
    """
    txt = io.open(BIBLIA, encoding="utf-8").read()
    i = txt.find("## " + LEI)
    if i < 0:
        return None
    bloco = re.search(r"```\n(.*?)\n```", txt[i:i + 6000], re.S)
    if not bloco:
        return None
    nomes = re.findall(r"[A-Z][A-Z_]+", bloco.group(1))
    return [n for n in nomes if n != "READY_FOR_INTELIGENCIA"]


def campos_do_codigo():
    """Os campos que o dono devolve DE FACTO — chamando-o, e nao lendo-o."""
    item = {"id": "fronteira-1", "texto": "um ensaio publicado com DOI",
            "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
    d = admissao.decidir(item, "T7", corrida="prova-da-fronteira")
    if d.resultado != admissao.SIM:
        return None, d
    return admissao.pronto_para_inteligencia(item, d), d


def _grep(padrao, pastas):
    r = subprocess.run(
        # `-E`: sem ele o `grep` le expressao BASICA, onde `\(` significa
        # ABRIR GRUPO em vez de «um parentese». O primeiro censo devolveu 0
        # produtores por causa disso — e zero por engano de sintaxe e
        # exactamente o «UNKNOWN vestido de ZERO» que esta casa persegue.
        ["grep", "-rnE", "--include=*.py", "--include=*.mjs", "--include=*.js",
         "--include=*.yml", "--include=*.sh", padrao] + list(pastas),
        cwd=RAIZ, capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l.strip()]


def main():
    print("A FRONTEIRA DA COLETA — declarada, implementada, produzida, consumida")
    print("=" * 70)

    # ── F1 · A LEI ───────────────────────────────────────────────────────
    lei = campos_da_lei()
    caso("F1_a_lei_declara_o_contrato_de_saida",
         bool(lei) and len(lei) >= 5,
         "%s declara %d campos" % (LEI, len(lei or [])))

    # ── F2 · O CODIGO ────────────────────────────────────────────────────
    registo, decisao = campos_do_codigo()
    if registo is None:
        caso("F2_o_codigo_devolve_exactamente_os_campos_da_lei", False,
             "a porta nao admitiu o item da prova: %s" % (decisao.resultado,))
        codigo = []
    else:
        codigo = list(registo.keys())
        so_na_lei = sorted(set(lei or []) - set(codigo))
        so_no_codigo = sorted(set(codigo) - set(lei or []))
        caso("F2_o_codigo_devolve_exactamente_os_campos_da_lei",
             not so_na_lei and not so_no_codigo,
             "%d campos, iguais aos da lei" % len(codigo) if not (so_na_lei or so_no_codigo)
             else "so na lei: %s · so no codigo: %s" % (so_na_lei, so_no_codigo))

    # ── F3 · UM DONO, E NAO DOIS ─────────────────────────────────────────
    #
    #     ONE CONCEPT -> ONE OWNER.
    #
    # Qualquer sitio que monte um dicionario com `ESTADO:
    # PRONTO_PARA_INTELIGENCIA` sem passar pelo dono e um SEGUNDO dono a
    # nascer — e dois donos para um conceito e a maneira mais rapida de os
    # dois divergirem.
    #
    # ⚠️ A PRIMEIRA VERSAO DESTE CASO ERA LARGA DEMAIS e acusou o
    # orquestrador. Ele escreve `PRONTO_PARA_INTELIGENCIA` na linha 262 —
    # mas como ESTADO DA CORRIDA num recibo («como e que esta corrida
    # acabou»), e nao como o registo do contrato. Um dono a mais nao se
    # deteta pela palavra: deteta-se por quem CONSTROI O REGISTO, e o
    # registo reconhece-se pelo campo `ESTADO` com aquele valor.
    #
    #     MENCIONAR O NOME DE UM ESTADO != SER DONO DO CONTRATO.
    #
    # `pedido/pedido.py` declara-o como estado legal de um pedido, pela
    # mesma razao, e tambem nao e um segundo dono.
    outros = [l for l in _grep(r'.ESTADO.[[:space:]]*:[[:space:]]*.PRONTO_PARA_INTELIGENCIA',
                               PASTAS_DA_COLETA)
              if not l.startswith('admissao/admissao.py')]
    caso("F3_so_o_dono_constroi_o_registo_READY",
         not outros,
         "o unico construtor e admissao.pronto_para_inteligencia()"
         if not outros else "tambem constroem: %s" % [l.split(':')[0] for l in outros])

    # ── F4 · A PORTA RECUSA O QUE NAO PASSOU ─────────────────────────────
    mau = {"id": "sem-texto"}
    dm = admissao.decidir(mau, "T7", corrida="prova-da-fronteira")
    recusou = False
    try:
        admissao.pronto_para_inteligencia(mau, dm)
    except ValueError:
        recusou = True
    caso("F4_nao_ha_READY_sem_SIM_na_porta", recusou and dm.resultado != admissao.SIM,
         "a porta respondeu %s, e o contrato recusou-se a emitir" % dm.resultado)

    # ═════════════════════════════════════════════════════════════════════
    # O CENSO — medido e relatado, e NAO transformado em falha
    # ═════════════════════════════════════════════════════════════════════
    # QUEM CHAMA O DONO — e uma CHAMADA, nao uma mencao. `leis/artefato.py`
    # fala dele num docstring, e um docstring nao produz registo nenhum.
    # Este proprio ficheiro tambem sai da conta: um medidor que se conta a
    # si proprio inflaciona o que veio medir.
    # ⚠️ E UMA CHAMADA SO SE O FICHEIRO TAMBEM IMPORTAR O DONO.
    # `leis/artefato.py:43` escreve `admissao.pronto_para_inteligencia()`
    # num DOCSTRING — a explicar que o READY desta casa ja existe. O texto
    # casa com o padrao e nao produz registo nenhum. A diferenca entre uma
    # chamada e uma frase sobre a chamada nao se ve no regex; ve-se no
    # `import`. Quem nao importa o modulo nao o pode chamar.
    candidatos = sorted({
        l.split(':')[0] for l in
        _grep(r'\.pronto_para_inteligencia[[:space:]]*\(',
              list(PASTAS_DA_COLETA) + ['provas', 'tests', '.github'])
        if not l.startswith(('admissao/admissao.py',
                             'provas/a_fronteira_da_coleta.py'))})
    produtores = []
    for c in candidatos:
        try:
            fonte = io.open(os.path.join(RAIZ, c), encoding='utf-8').read()
        except OSError:
            continue
        if re.search(r'^\s*(import\s+admissao|from\s+admissao\s+import'
                     r'|import\s+admissao\s+as)', fonte, re.M):
            produtores.append(c)
    runtime = [l for l in produtores if not l.startswith(('provas/', 'tests/'))]
    consumidores = _grep('PRONTO-PARA-INTELIGENCIA',
                         list(PASTAS_DA_COLETA) + ['provas', 'tests', '.github'])
    destino = os.path.join(RAIZ, 'data', 'samples', 'PRONTO-PARA-INTELIGENCIA')

    print()
    print("  CENSO DA FRONTEIRA")
    print("  " + "-" * 66)
    print("  CONTRATO          %s · %d campos" % (LEI, len(lei or [])))
    print("  DONO              admissao/admissao.py :: pronto_para_inteligencia()")
    print("  PRODUTORES        %d chamada(s) ao dono, %d fora de provas/tests:"
          % (len(produtores), len(runtime)))
    for l in produtores:
        print("                      %-38s %s" % (
            l, "(so CLI, nenhum workflow)" if l in runtime else "(prova/teste)"))
    print("  DESTINO DECLARADO data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json")
    print("  DESTINO EXISTE?   %s" % ("SIM" if os.path.isdir(destino) else "NAO"))
    lê = sorted({c.split(':')[0] for c in consumidores
                 if not c.startswith(('orquestrador/', 'provas/a_fronteira'))})
    print("  CONSUMIDORES      %d  %s" % (len(lê), lê or "— ninguem le esta saida"))
    print()
    print("  O QUE ISTO QUER DIZER, sem exagerar para nenhum dos lados:")
    print("    · READY TEM dono e TEM contrato. Dizer «READY_NAO_TEM_DONO» e")
    print("      dizer mais do que se mediu.")
    print("    · E NAO tem consumidor nenhum, e o destino nem sequer existe.")
    print("      Dizer «ja tem consumidor» tambem e dizer mais do que se mediu.")
    print("    · A rota forward (DERIVED -> STRUCTURED -> ADMISSION) termina em")
    print("      ADMISSION e NAO chega aqui: o dono recebe `item`, e a rota")
    print("      produz `derived_artifact`. Sao duas coisas, e liga-las e uma")
    print("      DECISAO DE ARQUITETURA — nao um remendo de codigo.")
    print()
    print("    UMA PORTA POR ONDE NINGUEM PASSA NAO E UMA PORTA.")
    print("    E UMA PAREDE COM MACANETA.   (a propria Biblia, :288)")

    # ── A MUTACAO · o F2 tem de morder ───────────────────────────────────
    #
    # O F2 e a unica coisa que impede a lei e o codigo de divergirem em
    # silencio, que e como esta casa ja perdeu contratos antes. Se ELE
    # estiver cego, o verde dele nao vale nada.
    #
    # Tira-se um campo ao registo que o dono devolveu e pergunta-se se a
    # comparacao com a lei ainda reprova. Nada e escrito no disco: a mutacao
    # e sobre o dicionario em memoria.
    if registo is not None:
        mutante = dict(registo)
        mutante.pop("FACT_LOCATION", None)
        morde = sorted(set(lei or []) - set(mutante)) == ["FACT_LOCATION"]
        caso("F2b_MUTACAO_um_campo_a_menos_e_apanhado", morde,
             "sem FACT_LOCATION, a comparacao com a lei acusa a falta")

    print()
    print("=" * 70)
    for nome, ok, det in fora:
        print("  %s  %-52s %s" % ("PASS" if ok else "FAIL", nome, det))
    mal = [n for n, ok, _ in fora if not ok]
    print("=" * 70)
    print("FRONTEIRA_DA_COLETA=%s" % ("PASS" if not mal else "FAIL"))
    print("  o que isto prova: existe UM contrato de saida, com UM dono, e o")
    print("  codigo devolve exactamente o que a lei declara.")
    print("  o que isto NAO prova: que alguem o produza em runtime ou o")
    print("  consuma. Nao prova porque nao e verdade, e medir a falta e o")
    print("  trabalho — nao pinta-la de verde.")
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
