#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUEM LIGA A MEMÓRIA DA COLETA AO BANCO — a composição do runtime, num sítio só.

O DEFEITO QUE ISTO FECHA
------------------------
O replay canário pelo workflow real (run GitHub 35215565657, 2026-09-17,
know-how §132) provou uma coisa que quinze testes de YAML não conseguiam ver:
o workflow criava um PostgreSQL descartável, aplicava 31 migrations, o portão
da Sala aprovava-o — e a corrida nunca lhe escrevia uma linha. Porquê:

    orquestrador.main()  chamava  correr(p, ...)  sem memoria= e sem
    banco_do_rastro=. Ninguém lia o ambiente. O adaptador Postgres só
    existia em provas/. A primeira coleta (§130) passou porque o CORREDOR
    DE PROVA ligava o banco em processo — outra porta, que o workflow não usa.

    DEPENDÊNCIA DECLARADA != DEPENDÊNCIA LIGADA.
    A PORTA QUE A PROVA USOU NÃO É A PORTA QUE O WORKFLOW USA.

Esta peça é a resposta: a porta de linha de comando compõe as dependências de
persistência AQUI, antes de chamar `correr()`. O orquestrador continua a ser o
dono da RUN e do fluxo; o workflow continua a chamar só o orquestrador; e o
adaptador Postgres continua a não decidir nada. O que muda é que a ligação
passa a existir — e a existir num só sítio.

O SINAL, E SÓ ELE
-----------------
A memória liga-se quando, e apenas quando, o ambiente DECLARA a bancada:

    BANCO_DESCARTAVEL_URL=postgresql://...@localhost:54329/descartavel

Nada mais é sinal. `SUPABASE_DB_URL` é o cofre da produção; `SINTONIA_SALA_DSN`
é a configuração da SALA (outro dono, outra pergunta); um hostname parecido,
uma URL parecida ou o nome do workflow não declaram nada. Sem a variável, a
corrida corre como sempre correu — RAW em ficheiro, `RAW_OBSERVATIONS` vazio,
`RASTRO = NAO_EMITIDO` — e o recibo DIZ que correu sem memória canónica.

    NÃO SE INFERE BANCO. NÃO SE INVENTA DSN. NÃO SE CAI PARA PRODUÇÃO.
    AUSÊNCIA DIZ-SE; NÃO SE PREENCHE.

E quando a variável existe mas não prova ser descartável — hostname remoto,
`?host=` a apontar para fora, banco com nome de produção, URL malformada — a
recusa acontece ANTES de qualquer escrita, e a corrida não nasce:

    FALHA FECHADA. PRODUÇÃO NÃO É LABORATÓRIO.

Quem decide o que é descartável é `guarda/banco_descartavel.py` — um dono, o
mesmo que as provas usam. Aqui só se pergunta.

SEM EFEITO NO IMPORT
--------------------
Importar este módulo não lê ambiente, não abre ligação, não cria nada. Tudo
acontece dentro de `dependencias_do_runtime()`, com o ambiente que lhe derem —
e é isso que a torna testável sem banco e sem rede.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

from guarda.banco_descartavel import (  # noqa: E402
    AMBIENTE_QUE_MUDA_O_DESTINO, BancoNaoDescartavel, ambiente_sem_desvio,
    morada_sem_segredo, porque_nao_e_descartavel)

#: A ÚNICA variável que liga a memória da Collection. Ver o cabeçalho.
VARIAVEL = "BANCO_DESCARTAVEL_URL"

#: Os dois estados que o recibo pode declarar. Não há terceiro: «liguei a
#: produção» não é um estado desta peça, é o defeito que ela existe para
#: impedir.
DESCARTAVEL = "DESCARTAVEL"
AUSENTE = "AUSENTE"


class BancoRecusado(BancoNaoDescartavel):
    """`BANCO_DESCARTAVEL_URL` está declarada e NÃO prova ser descartável."""


class Persistencia:
    """O que a porta CLI entrega a `correr()`: as duas dependências, e a
    declaração honesta de onde vieram."""

    def __init__(self, memoria, banco_do_rastro, estado, porque, morada="",
                 retiradas=()):
        self.memoria = memoria
        self.banco_do_rastro = banco_do_rastro
        self.ESTADO = estado
        self.PORQUE = porque
        self.MORADA = morada
        self.AMBIENTE_RETIRADO = tuple(retiradas)

    def para_json(self) -> dict:
        return {"ESTADO": self.ESTADO, "MORADA": self.MORADA or None,
                "PORQUE": self.PORQUE, "VARIAVEL": VARIAVEL,
                "AMBIENTE_RETIRADO": list(self.AMBIENTE_RETIRADO),
                "MEMORIA": type(self.memoria).__name__ if self.memoria else None,
                "BANCO_DO_RASTRO": (type(self.banco_do_rastro).__name__
                                    if self.banco_do_rastro else None)}


def dependencias_do_runtime(env=None) -> Persistencia:
    """Compõe a persistência a partir do ambiente. Fail closed.

    → `Persistencia` com memória e banco do rastro quando `BANCO_DESCARTAVEL_URL`
      existe e prova ser descartável;
    → `Persistencia` AUSENTE (dependências `None`) quando a variável não existe;
    → levanta `BancoRecusado` quando existe e não prova — antes de qualquer
      escrita, antes de a corrida nascer.
    """
    e = os.environ if env is None else env
    url = (e.get(VARIAVEL) or "").strip()
    if not url:
        return Persistencia(
            None, None, AUSENTE,
            "%s nao declarada: a corrida corre sem memoria canonica — RAW fica "
            "em ficheiro, RAW_OBSERVATIONS sai vazio e RASTRO=NAO_EMITIDO. Nunca "
            "se cai para SUPABASE_DB_URL nem para SINTONIA_SALA_DSN." % VARIAVEL)
    motivo = porque_nao_e_descartavel(url)
    if motivo:
        raise BancoRecusado(
            "BANCO_RECUSADO: %s esta declarada e nao prova ser um banco "
            "descartavel local (%s). Nada foi escrito; a corrida nao nasce. "
            "PRODUCAO NAO E LABORATORIO." % (VARIAVEL, motivo))
    # Os imports vivem aqui, e não no topo, de propósito: compor é o único
    # momento em que esta peça precisa deles, e importar este módulo não
    # deve arrastar o adaptador para quem só quer perguntar «há banco?».
    # ── E OS BILHETES NA PAREDE SAEM — 2026-09-17, red team de arquitetura ──
    # A libpq lê `PGHOSTADDR`, `PGSERVICE`, `PGSERVICEFILE`, `PGOPTIONS`… por
    # baixo da URL: `PGHOSTADDR=52.1.2.3` mandava a ligação para fora com a
    # URL a dizer localhost. A trava olha para a URL; o `psql` que o adaptador,
    # o rastro e a Sala lançam herda o ambiente DESTE processo. Por isso a
    # composição — e só ela, e só quando a bancada está declarada — tira
    # essas variáveis do ambiente do processo. É o único efeito colateral
    # desta peça, é deliberado, e fica escrito no recibo (`AMBIENTE_RETIRADO`).
    retiradas = ()
    if e is os.environ:
        _, retiradas = ambiente_sem_desvio(os.environ)
        for nome in retiradas:
            os.environ.pop(nome, None)
    else:
        retiradas = tuple(n for n in AMBIENTE_QUE_MUDA_O_DESTINO if n in e)
    from guarda.memoria_postgres import MemoriaPostgres
    import coleta_checkpoint as cc
    return Persistencia(
        MemoriaPostgres(url), cc.Banco(url), DESCARTAVEL,
        "%s declarada e provada descartavel; memoria e rastro ligados ao "
        "mesmo banco." % VARIAVEL, morada_sem_segredo(url), retiradas)
