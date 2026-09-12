#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA DE ESPERA — onde a unidade pronta pousa, e quem a põe lá.

    A COLETA ACABA AQUI. A INTELIGÊNCIA COMEÇA DEPOIS, E NOUTRA MISSÃO.

O QUE ESTE MÓDULO É DONO
------------------------
    A MORADA      `data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json`
    A ESCRITA     atómica, e com trava contra a mesma corrida a duas mãos
    A IDEMPOTÊNCIA  a mesma corrida com o mesmo conteúdo não duplica

O QUE ELE NÃO É DONO
--------------------
    O CONTRATO    `admissao.pronto_para_inteligencia()` — 11 campos, COL-LAW-043
    A DECISÃO     `admissao.decidir()`
    O RASTRO      `medidas/rastro_da_coleta.py`

⚠️ POR QUE ESTE FICHEIRO NASCEU, E DE ONDE VEIO O CÓDIGO
--------------------------------------------------------
A escrita vivia dentro de `orquestrador/orquestrador.py`. Funcionava — e
contradizia a COL-LAW-012:

    CONTROL PLANE   ENTRADA → PEDIDO → ORQUESTRADOR → EXECUTOR
    DATA PLANE      SOURCE → EXECUTOR → RAW → DERIVAÇÕES → ADMISSÃO → READY

O orquestrador **controla**, não transporta dado. Enquanto a única escrita
estava lá dentro, a rota forward não tinha como pousar a unidade sem escrever
uma segunda — e duas escritas da mesma espera são duas verdades à espera de
divergir.

    ONE CONCEPT → ONE OWNER.

Nada foi reimplementado: o corpo é o mesmo que o orquestrador já corria,
mudado de casa e com as três travas que um ficheiro exige e que ele não tinha.

⚠️ O BACKEND É UMA ESCOLHA, E NÃO O ESTADO
-------------------------------------------
A COL-LAW-044 separa **onde está** de **em que estado está**. `READY` é o
estado; `data/samples` é o meio. Decidido em `C-CLOSE-READY-WITH-CANONICAL-
WAITING-ROOM-V1`: o meio é o sistema de ficheiros, porque a morada já existia
e não há necessidade medida que exija banco. Trocar de meio mais tarde não
redefine `READY` — exige prova de necessidade, migração canónica, e continua a
exigir UM dono.
"""
import errno
import io
import json
import os
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import telemetria as tel                           # noqa: E402
# ⚠️ O NOME DO CONFLITO TEM DONO, e ele e `guarda/preservar_coleta.py`.
# Escrever aqui outra palavra para «esta corrida ja contou outra historia»
# daria duas palavras para o mesmo facto.
from preservar_coleta import RUN_ID_CONFLICT     # noqa: E402

MORADA = os.path.join(RAIZ, "data", "samples", "PRONTO-PARA-INTELIGENCIA")

# O vocabulário é o que já existe. `PASSED` e `REUSED` são destinos de item em
# `telemetria.DESTINOS_DO_ITEM` — não se inventa um terceiro nome para dizer
# «pousou» e «já lá estava».
POUSOU = tel.DESTINOS_DO_ITEM[0]      # PASSED
JA_ESTAVA = tel.DESTINOS_DO_ITEM[5]   # REUSED


class ConflitoDeCorrida(Exception):
    """A mesma corrida a contar duas histórias.

        UMA RUN_ID NÃO PODE CONTAR DUAS HISTÓRIAS.

    Sobrescrever em silêncio apagaria a primeira sem ninguém saber que existiu.
    Quem levanta isto não escreveu nada: o ficheiro anterior fica intacto.
    """


class EsperaOcupada(Exception):
    """Outra escrita da MESMA corrida está a decorrer neste instante."""


def caminho_da_corrida(run_id: str) -> str:
    """A morada desta corrida. Uma corrida, um ficheiro."""
    if not run_id or not str(run_id).strip():
        raise ValueError("nao ha espera sem corrida: RUN_ID vazio")
    if os.sep in str(run_id) or "/" in str(run_id) or str(run_id).startswith("."):
        # O `run_id` vem de fora. Um `../` aqui escreveria fora da morada.
        raise ValueError("RUN_ID nao pode carregar caminho: %r" % run_id)
    return os.path.join(MORADA, "%s.json" % run_id)


def ler(run_id: str):
    """O que está pousado nesta corrida, ou `None`. Nunca inventa vazio."""
    caminho = caminho_da_corrida(run_id)
    if not os.path.isfile(caminho):
        return None
    with io.open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _corpo(run_id, unidades):
    """O conteúdo canónico. A mesma entrada dá sempre os mesmos bytes."""
    return json.dumps({"RUN_ID": run_id, "ITENS": list(unidades)},
                      ensure_ascii=False, indent=2) + "\n"


def _escrever_atomico(caminho, corpo):
    """⚠️ UM CRASH A MEIO NÃO PODE DEIXAR JSON PELA METADE.

    Escrever direto no ficheiro canónico deixa-o truncado se o processo morrer
    a meio — e um JSON truncado não é «quase o estado»: é um estado que ninguém
    consegue ler, no sítio onde o anterior estava bom.

        FICHEIRO PARCIAL NÃO É ESTADO LEGÍTIMO.

    Por isso: corpo inteiro num temporário NA MESMA filesystem, `fsync` para os
    bytes saírem do buffer, e só então `os.replace` — que é atómico no POSIX.
    Quem ler durante a escrita vê o ficheiro ANTERIOR, inteiro.
    """
    pasta = os.path.dirname(caminho)
    os.makedirs(pasta, exist_ok=True)
    fd, temporario = tempfile.mkstemp(prefix=".espera-", suffix=".json",
                                      dir=pasta)
    try:
        with io.open(fd, "w", encoding="utf-8") as f:
            f.write(corpo)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, caminho)
        temporario = None
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)


class _Trava:
    """A trava da corrida, e ela é por CORRIDA — não pela sala inteira.

    Duas corridas diferentes escrevem ao mesmo tempo, cada uma na sua morada:
    travá-las juntas seria serializar trabalho que não colide. O que colide é a
    MESMA corrida a duas mãos, e é só isso que esta trava impede.

    ⚠️ E ELA NÃO INVENTA RECUPERAÇÃO. Se um processo morrer com a trava presa,
    o ficheiro de trava fica — e a escrita seguinte FALHA ALTO, com o caminho
    na mensagem. Para a V1 isso é o certo: um estado preso e auditável é melhor
    do que uma limpeza automática que não sabe se o outro lado ainda corre.
    """

    def __init__(self, caminho):
        self.caminho = caminho + ".lock"
        self.fd = None

    def __enter__(self):
        import fcntl
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)
        self.fd = os.open(self.caminho, os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as erro:
            os.close(self.fd)
            self.fd = None
            if erro.errno in (errno.EACCES, errno.EAGAIN):
                raise EsperaOcupada(
                    "outra escrita da mesma corrida esta a decorrer: %s"
                    % self.caminho) from erro
            raise
        return self

    def __exit__(self, *_):
        import fcntl
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None


def pousar(run_id: str, unidades: list) -> dict:
    """A unidade pronta pousa na espera. Devolve o que ACONTECEU, não o pedido.

        POUSOU     escreveu-se agora
        JA ESTAVA  a corrida ja tinha exactamente este conteudo

    E se a corrida já lá estiver com conteúdo DIFERENTE, isto levanta
    `ConflitoDeCorrida` e não escreve nada.

    ⚠️ UMA LISTA VAZIA NÃO É UMA ESPERA. Zero unidades admitidas não produz
    ficheiro: um ficheiro com `ITENS: []` diria «esta corrida chegou à espera»,
    e ela não chegou.
    """
    if not unidades:
        return {"ESTADO": None, "RUN_ID": run_id, "FICHEIRO": None,
                "UNIDADES": 0,
                "PORQUE": "nenhuma unidade admitida: nao ha o que pousar"}

    caminho = caminho_da_corrida(run_id)
    corpo = _corpo(run_id, unidades)
    with _Trava(caminho):
        if os.path.isfile(caminho):
            with io.open(caminho, encoding="utf-8") as f:
                anterior = f.read()
            if anterior == corpo:
                return {"ESTADO": JA_ESTAVA, "RUN_ID": run_id,
                        "FICHEIRO": os.path.relpath(caminho, RAIZ),
                        "UNIDADES": len(unidades),
                        "PORQUE": "a corrida ja tinha exactamente este conteudo"}
            raise ConflitoDeCorrida(
                "%s: %s ja existe com conteudo DIFERENTE. NAO foi escrito "
                "nada — o ficheiro anterior fica intacto. Uma corrida nao "
                "pode contar duas historias."
                % (RUN_ID_CONFLICT, os.path.relpath(caminho, RAIZ)))
        _escrever_atomico(caminho, corpo)
    return {"ESTADO": POUSOU, "RUN_ID": run_id,
            "FICHEIRO": os.path.relpath(caminho, RAIZ),
            "UNIDADES": len(unidades),
            "PORQUE": "escrita atomica publicada nesta execucao"}


def main():
    print(__doc__.strip().split("\n")[0])
    print("morada: %s" % os.path.relpath(MORADA, RAIZ))
    print("estados: %s (pousou) · %s (ja estava)" % (POUSOU, JA_ESTAVA))
    print("conflito: %s" % RUN_ID_CONFLICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
