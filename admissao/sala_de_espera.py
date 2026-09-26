#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA DE ESPERA — onde a unidade pronta pousa, quem a põe lá, e quem a tira.

    A COLETA ACABA AQUI. A INTELIGÊNCIA COMEÇA DEPOIS, E NOUTRA MISSÃO.

O QUE ESTE MÓDULO É DONO
------------------------
    A FILA        pousar · ler · listar_pendentes · retirar
    A ESCRITA     atómica, e com trava contra a mesma corrida a duas mãos
    A IDEMPOTÊNCIA  a mesma corrida com o mesmo conteúdo não duplica
    O CONFLITO    a mesma corrida com outro conteúdo não escreve nada

O QUE ELE NÃO É DONO
--------------------
    O CONTRATO    `admissao.pronto_para_inteligencia()` — 12 campos, COL-LAW-043
    A DECISÃO     `admissao.decidir()`
    O RASTRO      `medidas/rastro_da_coleta.py`
    O VEREDITO    a Intelligence. `retirar()` diz «saiu da fila», e mais nada.

⚠️ POR QUE ESTE FICHEIRO NASCEU, E DE ONDE VEIO O CÓDIGO
--------------------------------------------------------
A escrita vivia dentro de `orquestrador/orquestrador.py`. Funcionava — e
contradizia a COL-LAW-012:

    CONTROL PLANE   ENTRADA → PEDIDO → ORQUESTRADOR → EXECUTOR
    DATA PLANE      SOURCE → EXECUTOR → RAW → DERIVAÇÕES → ADMISSÃO → READY

O orquestrador **controla**, não transporta dado.

    ONE CONCEPT → ONE OWNER.

⚠️ E POR QUE O BACKEND MUDOU — O FACTO NOVO
--------------------------------------------
A `ADR-SALA-DE-ESPERA-V1` escolheu o sistema de ficheiros e escolheu bem para o
que sabia. O que ninguém tinha perguntado, e a primeira coleta real perguntou:

    quando o runner acabar, onde é que o READY fica?

Medido em `C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1`, contra o repositório
inteiro:

    git log --all -- 'data/samples/PRONTO-PARA-INTELIGENCIA'   ->   vazio

Nunca, em ramo nenhum. Nenhum workflow lhe faz `git add` — o `sintonia-scrap`
até RECUSA caminhos fora de `INSTAGRAM|YOUTUBE|SCRAP`. Nenhum `upload-artifact`
o apanha. O `actions/checkout` seguinte limpa o que não está versionado.

    MODULE EXISTS != FILE WRITTEN ON RUNNER != PERSISTED AFTER RUN.
    PROVA DENTRO DO PROCESSO != DURABILIDADE OPERACIONAL.

A ADR-V1 previu isto com todas as letras: `BACKEND_CHANGE_ALLOWED_LATER = YES`,
`BACKEND_CHANGE_REQUIRES = PROVA DE NECESSIDADE`. A prova chegou.

⚠️ DOIS BACKENDS, UMA SÓ VERDADE — E A DIFERENÇA ESTÁ DECLARADA
----------------------------------------------------------------
    POSTGRES   CANÓNICO. É aqui que o READY operacional vive.
    FICHEIRO   NÃO CANÓNICO. A V1, preservada, para prova offline.

Nunca os dois ao mesmo tempo: `backend()` escolhe UM por processo, e o recibo
diz sempre qual foi em `CANONICO`. O que **não** acontece é a queda silenciosa
de um para o outro — foi exactamente essa queda que produziu o bloqueio:

    UM FALLBACK SILENCIOSO PARA DISCO EFÉMERO
    É A MESMA FALHA COM OUTRO NOME.

Pedir `POSTGRES` sem DSN levanta `SalaIndisponivel`. **Não** cai para ficheiro.

E quem manda no caminho operacional é `exigir_canonica()`: o portão que se
chama ANTES da aquisição e que recusa arrancar sobre uma sala que não sobrevive.
"""
import errno
import hashlib
import io
import json
import os
import subprocess
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
# ⚠️ QUAL `psql` ESTE PROCESSO USA TEM UM DONO, e ele e `guarda/cliente_postgres.py`.
# O replay canario 3 (run GitHub 35232024024, know-how §135) caiu na primeira
# chamada `["psql", ...]` do runtime com FileNotFoundError — e ESTE portao
# tinha dito PASS sem abrir ligacao. O nome nu confiava no PATH; o dono nao.
from guarda.cliente_postgres import (            # noqa: E402
    ClientePostgresAusente, como_foi_resolvido, resolver_psql)

MORADA = os.path.join(RAIZ, "data", "samples", "PRONTO-PARA-INTELIGENCIA")

# O vocabulário é o que já existe. `PASSED` e `REUSED` são destinos de item em
# `telemetria.DESTINOS_DO_ITEM` — não se inventa um terceiro nome para dizer
# «pousou» e «já lá estava».
POUSOU = tel.DESTINOS_DO_ITEM[0]      # PASSED
JA_ESTAVA = tel.DESTINOS_DO_ITEM[5]   # REUSED

# ── O VOCABULÁRIO DA FILA ────────────────────────────────────────────────
# Procurado antes de criado: `telemetria.DESTINOS_DO_ITEM` fala do DESTINO de um
# item numa etapa, `telemetria.ESTADOS_DE_ETAPA` do estado de uma ETAPA, e
# `leis/falhas.py` de falhas. Nenhum deles nomeia «está à espera» e «já saiu».
# Estas duas palavras nascem aqui porque aqui é que a fila mora.
#
#     A ESPERA E O DESTINO SAO PERGUNTAS DIFERENTES.
A_ESPERA = "WAITING"
RETIRADO = "CONSUMED"
ESTADOS_DA_FILA = (A_ESPERA, RETIRADO)

# Os campos da COL-LAW-043, na ordem em que
# `admissao.pronto_para_inteligencia()` os constrói. Escritos aqui para que a
# travessia para o banco tenha dois lados a comparar — e há prova que reprova se
# o dono mudar e isto não mudar.
#
# ⚠️ ERAM DOZE ATÉ `C-COL-PRESERVE-FACTS-V1`, E PASSARAM A DEZANOVE.
# Os sete que entraram não são conceitos novos: são conceitos que a casa já
# declarava **antes** da execução e que morriam nesta fronteira — a espécie da
# coisa (`admissao.estagio()`), os outros dois tempos
# (`ingresso.FRONTEIRA_TRANSPORTA`), o porquê de cada `NAO SEI` de tempo e de
# lugar (`leis/artefato.py::conferir` já o exigia), a espécie probatória que os
# 13 contratos de fonte declaram, e o próprio fato.
#
#     ACRESCENTAR CAMPO A UM CONTRATO É DÍVIDA.
#     DEIXAR MORRER O QUE A CASA JÁ MEDIU É PIOR: É DÍVIDA INVISÍVEL.
# ── AS COLUNAS DA SALA, POR NOME (QUATRO-CHAVES-V2) ──────────────────────
# Uma lista, uma ordem, um sitio. O `select` de `ler()` e o `insert` de
# `pousar()` nascem daqui; nenhum codigo le ou escreve uma coluna pela posicao.
COLUNAS_LIDAS = (
    "ordem", "item_id", "raw_observation_id", "universo", "texto",
    "source_id", "source_location", "fact_location", "fact_time",
    "captured_at", "admitido_por", "estagio", "fact_time_basis",
    "fact_location_basis", "published_at", "observed_at",
    "source_declared_evidence_class", "fato",
    "published_at_basis", "source_location_basis", "completude_tempo_lugar",
    "tempo_lugar_evidencia", "janela_declarada",
)
# A TABELA UNICA: coluna da Sala <-> campo do contrato READY. `ler()` e
# `pousar()` passam por ELA — um so sitio diz que `published_at_basis` e o
# `PUBLISHED_AT_BASIS`. So COPIA: nenhum valor e calculado aqui (DA-6: quem
# escreve FACT_TIME e o extrator do fato; a Sala so o guarda como veio).
COLUNA_E_CAMPO = (
    ("item_id", "ITEM_ID"), ("universo", "UNIVERSO"), ("texto", "TEXTO"),
    ("source_id", "SOURCE_ID"), ("source_location", "SOURCE_LOCATION"),
    ("fact_location", "FACT_LOCATION"), ("fact_time", "FACT_TIME"),
    ("captured_at", "CAPTURED_AT"), ("admitido_por", "ADMITIDO_POR"),
    ("estagio", "ESTAGIO"), ("fact_time_basis", "FACT_TIME_BASIS"),
    ("fact_location_basis", "FACT_LOCATION_BASIS"),
    ("published_at", "PUBLISHED_AT"), ("observed_at", "OBSERVED_AT"),
    ("source_declared_evidence_class", "SOURCE_DECLARED_EVIDENCE_CLASS"),
    ("published_at_basis", "PUBLISHED_AT_BASIS"),
    ("source_location_basis", "SOURCE_LOCATION_BASIS"),
)
# as que viajam como JSON (chaves ordenadas na ida, `json.loads` na volta)
COLUNA_E_CAMPO_JSON = (
    ("fato", "FATO"), ("completude_tempo_lugar", "COMPLETUDE_TEMPO_LUGAR"),
    ("tempo_lugar_evidencia", "TEMPO_LUGAR_EVIDENCIA"),
    ("janela_declarada", "JANELA_DECLARADA"),
)
# o que `listar_pendentes` le: coluna da Sala -> chave devolvida
COLUNAS_PENDENTES = (
    ("run_id", "RUN_ID"), ("ordem", "ORDEM"), ("item_id", "ITEM_ID"),
)

COLUNAS_ESCRITAS = (
    "run_id", "ordem", "item_id", "raw_observation_id", "universo", "texto",
    "source_id", "source_location", "fact_location", "fact_time", "captured_at",
    "admitido_por", "corrida_sha256",
    "estagio", "fact_time_basis", "fact_location_basis", "published_at",
    "observed_at", "source_declared_evidence_class", "fato",
    "published_at_basis", "source_location_basis", "completude_tempo_lugar",
    "tempo_lugar_evidencia", "janela_declarada",
)


CAMPOS_READY = (
    "ESTADO", "ITEM_ID", "RAW_OBSERVATION_ID", "UNIVERSO", "ESTAGIO", "TEXTO",
    "SOURCE_ID", "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME",
    "FACT_TIME_BASIS", "FACT_LOCATION_BASIS", "PUBLISHED_AT", "OBSERVED_AT",
    # 033 (TEMPO-E-LUGAR, D61/D62): a base dos outros dois valores, e o grau
    # de precisao do item. Sem elas, o VALOR chegava e a BASE parava na porta.
    "PUBLISHED_AT_BASIS", "SOURCE_LOCATION_BASIS", "COMPLETUDE_TEMPO_LUGAR",
    "TEMPO_LUGAR_EVIDENCIA",
    "SOURCE_DECLARED_EVIDENCE_CLASS", "FATO",
    # D58 (QUATRO-CHAVES-NA-SALA): cultura, regiao do fato, fase, janela, cada
    # uma com a proveniencia. Coluna `janela_declarada` (033 unica); o que pousou
    # antes le-se `NAO SEI` nas quatro (`admissao.JANELA_NAO_MEDIDA`).
    "JANELA_DECLARADA",
    "CAPTURED_AT", "CORRIDA", "ADMITIDO_POR",
)

# O nome do estado do CONTRATO (não o da fila). Vive em `admissao`; aqui só se
# confere o que chega e se reconstrói o que sai.
PRONTO = "PRONTO_PARA_INTELIGENCIA"

BACKEND_POSTGRES = "POSTGRES"
BACKEND_FICHEIRO = "FICHEIRO"


# ── 033 · O QUE SE PODE REVER, E ONDE ESTA A BASE ORIGINAL DE CADA UM ──────
# O texto, a fonte, a identidade e a fila NAO se reveem: sao o que pousou, e a
# assinatura da corrida e deles. A lista e a mesma da trava do banco
# (`revisao_so_de_campo_revisivel`), e ha teste que compara as duas.
CAMPOS_REVISIVEIS = {
    "published_at": "published_at_basis",
    "source_location": "source_location_basis",
    "fact_time": "fact_time_basis",
    "fact_location": "fact_location_basis",
    "observed_at": None,
    "completude_tempo_lugar": None,
    "janela_declarada": None,
    "tempo_lugar_evidencia": None,
}
#: A base de um campo que nao tem coluna de base: a original nao foi dita.
AUSENCIA_REVISAO = "NAO SEI"


class ConflitoDeCorrida(Exception):
    """A mesma corrida a contar duas histórias.

        UMA RUN_ID NÃO PODE CONTAR DUAS HISTÓRIAS.

    Sobrescrever em silêncio apagaria a primeira sem ninguém saber que existiu.
    Quem levanta isto não escreveu nada: o que estava antes fica intacto.
    """


class EsperaOcupada(Exception):
    """Outra escrita da MESMA corrida está a decorrer neste instante."""


class SalaIndisponivel(Exception):
    """A sala canónica foi pedida e não está ao alcance.

    ⚠️ ISTO NÃO CAI PARA FICHEIRO. Cair seria escrever o READY num disco que
    morre com o job — a falha original, com cara de sucesso.

        FALHAR ALTO É MELHOR DO QUE PERSISTIR NO SÍTIO ERRADO.
    """


class ItemAmbiguo(Exception):
    """`ITEM_ID` repetido dentro da corrida: não serve de endereço.

    `admissao.decidir()` devolve `"?"` quando o item não traz `id` nem `url`.
    Dois desses na mesma corrida trazem o MESMO `ITEM_ID`, e retirar «o item ?»
    seria retirar um dos dois à sorte.
    """


class ItemDesconhecido(Exception):
    """Pediu-se para retirar algo que a sala não tem."""


# ═════════════════════════════════════════════════════════════════════════
# O CORPO CANÓNICO — a impressão que distingue retry de conflito
# ═════════════════════════════════════════════════════════════════════════

def _corpo(run_id, unidades):
    """O conteúdo canónico. A mesma entrada dá sempre os mesmos bytes.

    ⚠️ ESTA FUNÇÃO NÃO MUDOU AO MUDAR DE BACKEND, e não podia mudar: é ela que
    define o que «a mesma corrida com o mesmo conteúdo» quer dizer. Muda-la
    faria uma corrida antiga passar a conflitar consigo própria.
    """
    return json.dumps({"RUN_ID": run_id, "ITENS": list(unidades)},
                      ensure_ascii=False, indent=2) + "\n"


def impressao_da_corrida(run_id, unidades):
    """O sha256 do corpo canónico. É a chave do REUSED vs CONFLICT."""
    return hashlib.sha256(_corpo(run_id, unidades).encode("utf-8")).hexdigest()


def _conferir_unidades(unidades):
    """O que chega à sala tem de ser READY, e READY tem 12 campos.

        UMA SALA QUE ACEITA QUALQUER DICIONÁRIO NÃO GUARDA READY: GUARDA LIXO.
    """
    for i, u in enumerate(unidades):
        if not isinstance(u, dict):
            raise ValueError("unidade %d nao e um READY: %r" % (i, type(u)))
        faltam = [c for c in CAMPOS_READY if c not in u]
        if faltam:
            raise ValueError(
                "unidade %d nao cumpre o contrato READY (COL-LAW-043): faltam "
                "%s. O construtor unico e admissao.pronto_para_inteligencia()."
                % (i, ", ".join(faltam)))
        se_sobra = [c for c in u if c not in CAMPOS_READY]
        if se_sobra:
            raise ValueError(
                "unidade %d traz campo que o contrato READY nao tem: %s"
                % (i, ", ".join(sorted(se_sobra))))
        if u["ESTADO"] != PRONTO:
            raise ValueError("unidade %d nao esta PRONTA: ESTADO=%r"
                             % (i, u["ESTADO"]))


# ═════════════════════════════════════════════════════════════════════════
# BACKEND · FICHEIRO — a V1, preservada, e NÃO canónica
# ═════════════════════════════════════════════════════════════════════════

def caminho_da_corrida(run_id: str) -> str:
    """A morada desta corrida NO BACKEND DE FICHEIRO. Uma corrida, um ficheiro.

    ⚠️ Isto é endereço do backend não canónico. Quem quiser saber onde o READY
    operacional vive pergunta a `estado_operacional()`.
    """
    if not run_id or not str(run_id).strip():
        raise ValueError("nao ha espera sem corrida: RUN_ID vazio")
    if os.sep in str(run_id) or "/" in str(run_id) or str(run_id).startswith("."):
        # O `run_id` vem de fora. Um `../` aqui escreveria fora da morada.
        raise ValueError("RUN_ID nao pode carregar caminho: %r" % run_id)
    return os.path.join(MORADA, "%s.json" % run_id)


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

    ⚠️ E ISTO É UMA DAS RAZÕES DE O CANÓNICO SER OUTRO. No Postgres a trava é
    `pg_advisory_xact_lock`, que morre com a transação: um processo que caia a
    meio NÃO deixa a corrida presa. A V1 não tinha como fazer isso com um
    ficheiro, e a diferença é medida em `provas/a_sala_sobrevive_ao_processo.py`.
    """

    def __init__(self, caminho):
        self.caminho = caminho + ".lock"
        self.fd = None

    def __enter__(self):
        # ⚠️ `fcntl` NAO EXISTE NO WINDOWS — e a estrada morria na porta, com
        # ModuleNotFoundError, exactamente como ja tinha morrido na admissao.
        # O conserto e o MESMO precedente: `admissao/admissao.py::_prender` —
        # `fcntl.flock` em POSIX, `msvcrt.locking` em Windows, exclusiva e
        # nao-bloqueante nos dois, com o mesmo desfecho (EsperaOcupada).
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)
        self.fd = os.open(self.caminho, os.O_CREAT | os.O_RDWR, 0o644)
        try:
            if os.name != "nt":
                import fcntl                                   # noqa: PLC0415
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                import msvcrt                                  # noqa: PLC0415
                msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
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
        if self.fd is not None:
            if os.name != "nt":
                import fcntl                                   # noqa: PLC0415
                fcntl.flock(self.fd, fcntl.LOCK_UN)
            else:
                import msvcrt                                  # noqa: PLC0415
                try:
                    os.lseek(self.fd, 0, os.SEEK_SET)
                    msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            os.close(self.fd)
            self.fd = None


class _Ficheiro(object):
    """O backend da V1. Guardado inteiro, e declarado NÃO canónico."""

    NOME = BACKEND_FICHEIRO
    CANONICO = False
    PORQUE = ("o ficheiro vive no workspace do runner: nao sobrevive ao job "
              "nem ao checkout seguinte. Serve prova offline, nao operacao.")

    def sondar(self):
        """O ficheiro nao tem servidor para sondar: a pasta existe ou nasce."""
        os.makedirs(MORADA, exist_ok=True)
        return {"SONDA": "OK", "PSQL": None, "PSQL_ORIGEM": "NAO_SE_APLICA"}

    def morada(self, run_id):
        return os.path.relpath(caminho_da_corrida(run_id), RAIZ)

    def ler(self, run_id):
        caminho = caminho_da_corrida(run_id)
        if not os.path.isfile(caminho):
            return None
        with io.open(caminho, encoding="utf-8") as f:
            return json.load(f)

    def pousar(self, run_id, unidades):
        caminho = caminho_da_corrida(run_id)
        corpo = _corpo(run_id, unidades)
        with _Trava(caminho):
            if os.path.isfile(caminho):
                with io.open(caminho, encoding="utf-8") as f:
                    anterior = f.read()
                if anterior == corpo:
                    return JA_ESTAVA
                raise ConflitoDeCorrida(
                    "%s: %s ja existe com conteudo DIFERENTE. NAO foi escrito "
                    "nada — o estado anterior fica intacto. Uma corrida nao "
                    "pode contar duas historias."
                    % (RUN_ID_CONFLICT, self.morada(run_id)))
            _escrever_atomico(caminho, corpo)
        return POUSOU

    def listar_pendentes(self, limite=None):
        """⚠️ O FICHEIRO NÃO SABE DIZER «PENDENTE».

        A V1 não tem estado de fila: um ficheiro ou existe ou não existe. Fingir
        aqui uma lista de pendentes daria à prova offline uma capacidade que o
        backend não tem, e a prova passaria a medir a mentira.

            UM BACKEND QUE NÃO SABE RESPONDER DEVE DIZER QUE NÃO SABE.
        """
        raise SalaIndisponivel(
            "o backend FICHEIRO nao tem estado de fila: nao sabe distinguir "
            "quem espera de quem ja saiu. Use o backend canonico.")

    def retirar(self, run_id, item_id, por):
        raise SalaIndisponivel(
            "o backend FICHEIRO nao sabe retirar: nao tem estado de fila. "
            "Use o backend canonico.")

    def rever(self, run_id, ordem, revisoes, extrator, versao, motivo):
        raise SalaIndisponivel(
            "o backend FICHEIRO nao tem revisoes (migration 033): corrigir "
            "sem historico seria reescrever. Use o backend canonico.")

    def ler_atual(self, run_id):
        return self.ler(run_id)

    def linhas_para_revisao(self):
        raise SalaIndisponivel(
            "o backend FICHEIRO nao tem revisoes (migration 033). Use o "
            "backend canonico.")


# ═════════════════════════════════════════════════════════════════════════
# BACKEND · POSTGRES — o canónico
# ═════════════════════════════════════════════════════════════════════════

def _lit(valor):
    """Um literal SQL, escapado. `None` vira `null`.

    ⚠️ CONCATENAR TEXTO DE FORA EM SQL SEM ESCAPAR É COMO SE ESCREVE UMA PORTA
    DOS FUNDOS. Aqui o escape é o do padrão — a plica dobra — e é suficiente
    porque `standard_conforming_strings` está ligado — e ELE É IMPOSTO, não
    assumido: `_AMBIENTE_PSQL` passa-o em `PGOPTIONS` a cada chamada. Assumi-lo
    por ser o padrão desde o PostgreSQL 9.1 deixava a porta dependente de uma
    definição que alguém pode desligar no servidor.

        UM COMENTÁRIO QUE GARANTE O QUE O CÓDIGO NÃO IMPÕE É UMA PROMESSA.

    O NUL não tem representação em `text` e é recusado antes de chegar ao banco.
    """
    if valor is None:
        return "null"
    s = str(valor)
    if "\x00" in s:
        raise ValueError("texto com NUL nao entra no banco")
    return "'" + s.replace("'", "''") + "'"


def _ambiente_psql():
    """O ambiente de cada chamada ao `psql`.

    ⚠️ `standard_conforming_strings=on` NÃO É DECORAÇÃO. Com ele desligado, a
    barra invertida volta a ser escape dentro da plica — e `_lit()`, que só dobra
    a plica, deixaria de bastar. É a única definição de que o escape depende, e
    por isso viaja com a chamada em vez de ficar à espera do padrão do servidor.
    """
    return dict(os.environ, PGOPTIONS="-c standard_conforming_strings=on")


class _Postgres(object):
    """O backend canónico. Fala pelo `psql`, como o resto da casa.

    ⚠️ NÃO INSTALA DRIVER. `guarda/preservar_coleta.py` já fixou a doutrina
    desta casa: o dono gera SQL auditável e fala pelo cliente que o runner já
    tem. Instalar `psycopg` só para a sala seria uma dependência nova para uma
    capacidade que já existe.
    """

    NOME = BACKEND_POSTGRES
    CANONICO = True
    PORQUE = ("a fila vive numa tabela com unicidade, transacao, chave "
              "estrangeira e consulta: sobrevive ao processo, ao job e ao "
              "checkout.")
    SEP = "\x1f"
    # ⚠️ O SEPARADOR DE LINHA TEM DE SER TAO EXPLICITO COMO O DE CAMPO.
    # Esta classe separava CAMPOS por `\x1f` e LINHAS pelo fim-de-linha. Com
    # colunas curtas — `run_id`, `ordem`, `item_id` — isso nunca falhou.
    #
    # `ler()` traz `texto`, e o texto de um READY documental e a EXTRACCAO DE
    # UM PDF: ele tem dezenas de mudancas de linha la dentro. Cada uma delas
    # virava uma linha nova na saida do `psql`, e a leitura rebentava com
    # `IndexError` ao procurar o sexto campo de um pedaco de frase.
    #
    #     A SALA ESCREVIA O DOCUMENTO E NAO O CONSEGUIA LER DE VOLTA.
    #
    # E era assimetrico da pior maneira: `pousar()` funcionava, `listar_pendentes()`
    # funcionava, e so quem fosse BUSCAR o conteudo descobria. Uma fila que
    # aceita o que nao sabe devolver nao e uma fila.
    #
    # `\x1e` e o RECORD SEPARATOR do ASCII, irmao do `\x1f`. Nenhum dos dois
    # aparece em texto extraido de documento.
    SEP_LINHA = "\x1e"

    def __init__(self, url):
        self.url = url

    # ── qual psql, e a prova de que ele fala com o banco ────────────────
    @staticmethod
    def _psql_exe():
        """O executavel vem do dono (`guarda/cliente_postgres.py`), nunca do
        nome nu. Sem psql utilizavel, a Sala esta INDISPONIVEL — e di-lo."""
        try:
            return resolver_psql()
        except ClientePostgresAusente as ex:
            raise SalaIndisponivel(str(ex))

    def sondar(self):
        """UMA leitura inofensiva, REAL, pelo mesmo psql que o runtime usa.

        ⚠️ ATE 2026-09-17 O PORTAO DA SALA MEDIA CONFIGURACAO, NAO CONETIVIDADE.
        `exigir_canonica()` lia variaveis, construia este objecto e dizia PASS.
        O replay canario 3 (run GitHub 35232024024, know-how §135) passou por
        aqui com PASS e caiu na primeira chamada ao psql do runtime — o
        executavel nao estava no PATH do job. Um portao que aprova um ambiente
        onde o cliente nao lanca nao mediu nada.

            CAN DO != DID DO.  «A sala sobrevive a este job?» so tem resposta
            se alguem lhe falar — e este `select 1` fala.

        Nao cria tabela, nao escreve, nao muda estado. Falha (levanta) se o
        executavel nao existe OU se o banco nao responde — ANTES da rede.
        """
        linhas = self._consultar("select 1")
        if linhas != ["1"]:
            raise SalaIndisponivel(
                "a sonda `select 1` nao devolveu 1 (veio %r)" % (linhas[:3],))
        r = como_foi_resolvido()
        return {"SONDA": "OK", "PSQL": r["PSQL"], "PSQL_ORIGEM": r["ORIGEM"]}

    # ── as duas maneiras de falar com o banco ───────────────────────────
    def _consultar(self, sql):
        """Lê. `-X` para não herdar o `~/.psqlrc` de quem corre isto.

        ⚠️ A DSN VEM POR ÚLTIMO, E ISSO NÃO É ESTILO. O `getopt` do Windows
        não permuta: parado o primeiro argumento posicional, `-c` deixa de
        ser opção. Com a DSN à frente, este método ligava-se, NÃO CORRIA a
        consulta, e saía com ZERO — medido em PostgreSQL 16.4 real nesta
        máquina (2026-09-16): seis avisos `extra command-line argument ...
        ignored` e `rc=0`. A Sala canónica não lia nem escrevia no Windows.

            OPÇÕES PRIMEIRO. DSN POR ÚLTIMO.

        `tests/test_psql_argv.py` reprova quem voltar a trocar a ordem.
        """
        # ⚠️ E O SQL ENTRA POR STDIN, EM UTF-8 EXPLICITO. Texto acentuado em
        # ARGV atravessa a conversao ANSI do Windows e chega em CP1252 — e um
        # WHERE que cite texto italiano rebentava no banco UTF-8. `text=True`
        # sem `encoding` usa a codepage da maquina: o mesmo defeito por outra
        # porta. Medido em 2026-09-16.
        r = subprocess.run(
            [self._psql_exe(), "-X", "-q", "-A", "-t", "-F", self.SEP,
             "-R", self.SEP_LINHA,
             "-v", "ON_ERROR_STOP=1", "-f", "-", self.url],
            input=sql, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=_ambiente_psql())
        if r.returncode != 0:
            raise SalaIndisponivel(_sanitiza(r.stderr))
        # ⚠️ NAO SE USA `splitlines()`. Um `texto` com mudanca de linha dentro
        # daria N pedacos por linha, e o primeiro deles teria menos campos do
        # que o leitor espera.
        #
        # ⚠️ E O ULTIMO REGISTO NAO LEVA SEPARADOR. Com `-R`, o `psql` poe o
        # separador ENTRE os registos e nao depois do ultimo — mas continua a
        # terminar a saida com a mudanca de linha dele. Sem tirar essa, o
        # ULTIMO CAMPO DO ULTIMO REGISTO vinha com um `\n` a mais:
        #
        #     ADMITIDO_POR = 'pertence ao universo v4\n'
        #
        # Um caracter, na ultima linha, no ultimo campo. E chegava para mudar a
        # impressao do CONJUNTO — e entao pousar de novo exactamente o mesmo
        # conteudo lido de volta dava `RUN_ID_CONFLICT`, que e a resposta
        # reservada a «esta corrida ja contou outra historia».
        #
        #     UM RETRY LEGITIMO ACUSADO DE CONTAR DUAS HISTORIAS
        #     E PIOR DO QUE UM RETRY QUE DUPLICA: ELE ENSINA A DESLIGAR A TRAVA.
        #
        # `rstrip` so da mudanca de linha final, e nunca do conteudo: o que se
        # tira e o terminador do `psql`, e ele nao e dado de ninguem.
        bruto = r.stdout
        if bruto.endswith("\n"):
            bruto = bruto[:-1]
        return [l for l in bruto.split(self.SEP_LINHA) if l.strip()]

    def _executar(self, script):
        """Escreve. UMA TRANSAÇÃO, ou nada.

            SEM `--single-transaction`, CADA INSTRUÇÃO CONFIRMA-SE SOZINHA —
            e um erro a meio deixa metade da corrida pousada.
        """
        # ⚠️ A DSN POR ÚLTIMO — mesma razão de `_consultar`, e aqui é a ESCRITA:
        # com a DSN à frente, o `-f -` era ignorado no Windows e o pousar não
        # pousava nada, com cara de sucesso.
        # ⚠️ `encoding="utf-8"` E OBRIGATORIO: `text=True` sozinho codifica o
        # stdin na codepage da maquina (cp1252 no Windows), e o TEXTO de um
        # READY italiano — acentos por todo o lado — chegava mutilado ou
        # recusado pelo banco UTF-8. O pousar escrevia lixo com cara de PASS.
        r = subprocess.run(
            [self._psql_exe(), "-X", "-q", "-A", "-t", "-F", self.SEP,
             "-R", self.SEP_LINHA,
             "-v", "ON_ERROR_STOP=1", "--single-transaction", "-f", "-", self.url],
            input=script, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=_ambiente_psql())
        return r.returncode, r.stdout.replace(self.SEP_LINHA, "\n"), _sanitiza(r.stderr)

    def morada(self, run_id):
        return "postgres:public.sala_de_espera?run_id=%s" % run_id

    # ── ler ─────────────────────────────────────────────────────────────
    def ler(self, run_id):
        # ⚠️ POR NOME, NUNCA POR POSICAO (QUATRO-CHAVES-V2, 25/09). A leitura era
        # `c[18]`, `c[19]`… contra um `select` escrito a parte: cada coluna nova
        # acrescentada de cada lado (033) obrigava a renumerar, e um indice
        # errado NAO da erro — le a coluna vizinha em silencio (AVISO da
        # INSTALACAO-2). Agora o `select` nasce de `COLUNAS_LIDAS` e cada valor
        # volta pelo NOME dela; se o numero de valores nao bater, rebenta.
        linhas = self._consultar(
            "select " + ", ".join(COLUNAS_LIDAS) + " "
            "from public.sala_de_espera where run_id = %s order by ordem"
            % _lit(run_id))
        if not linhas:
            return None
        itens = []
        for l in linhas:
            partes = l.split(self.SEP)
            if len(partes) != len(COLUNAS_LIDAS):
                raise SalaIndisponivel(
                    "a Sala devolveu %d valores para %d colunas pedidas — ler por "
                    "posicao aqui seria ler a coluna errada"
                    % (len(partes), len(COLUNAS_LIDAS)))
            c = dict(zip(COLUNAS_LIDAS, partes))
            # ⚠️ `raw_observation_id` NULO QUER DIZER `NAO SEI`, e é assim que
            # o contrato o escreve. Devolver `None` aqui inventaria uma terceira
            # maneira de dizer a mesma ausência.
            obs = c["raw_observation_id"]
            u = {"ESTADO": PRONTO, "CORRIDA": run_id,
                 "RAW_OBSERVATION_ID": "NAO SEI" if obs == "" else int(obs)}
            for coluna, campo in COLUNA_E_CAMPO:
                u[campo] = c[coluna]
            # ⚠️ `fato` VOLTA POR `json.loads`, SEMPRE — inclusive quando o
            # valor é a palavra `NAO_SE_APLICA` (foi escrita como JSON, com
            # aspas). A JANELA idem: o que pousou antes da 033 traz o default,
            # as quatro chaves em `NAO SEI`.
            for coluna, campo in COLUNA_E_CAMPO_JSON:
                u[campo] = json.loads(c[coluna])
            itens.append(u)
        # A ORDEM DOS CAMPOS É A DO DONO, e não a do `select`. O corpo canónico
        # assina o dicionário como ele está: reconstruí-lo por outra ordem daria
        # outra impressão para o mesmo conteúdo.
        itens = [{c: u[c] for c in CAMPOS_READY} for u in itens]
        return {"RUN_ID": run_id, "ITENS": itens}

    # ── pousar ──────────────────────────────────────────────────────────
    def pousar(self, run_id, unidades):
        """Decide e escreve DENTRO DA MESMA TRANSAÇÃO.

        ⚠️ LER PRIMEIRO E ESCREVER DEPOIS, EM DUAS VIAGENS, É UMA CORRIDA.
        Entre a leitura e a escrita cabe outro processo inteiro. Por isso a
        decisão — pousar, reaproveitar ou recusar — é tomada no banco, debaixo
        de `pg_advisory_xact_lock`, que é a trava por CORRIDA e que **morre com
        a transação**: um processo que caia a meio não deixa a corrida presa.
        """
        impressao = impressao_da_corrida(run_id, unidades)
        valores = []
        for i, u in enumerate(unidades):
            obs = u["RAW_OBSERVATION_ID"]
            # `NAO SEI` é ausência declarada, e vai para o banco como NULL.
            # Nunca se fabrica um id a partir de outra coisa.
            obs_sql = "null" if (obs is None or str(obs).strip().upper()
                                 in ("NAO SEI", "NÃO SEI", "")) else str(int(obs))
            # ⚠️ O ENVELOPE DO FATO VAI COMO JSON, SEMPRE, E COM CHAVES
            # ORDENADAS. `NAO_SE_APLICA` também: ele é escrito como a string
            # JSON `"NAO_SE_APLICA"`. Assim a volta é `json.loads` sem ramo, e
            # a impressão da corrida é reproduzível — que é o que separa um
            # retry legítimo de um conflito.
            # ⚠️ POR NOME (QUATRO-CHAVES-V2): cada valor vai GRUDADO ao nome
            # da sua coluna, pela tabela `COLUNA_E_CAMPO`; a ordem do `insert`
            # sai de `COLUNAS_ESCRITAS`. Duas listas paralelas (nomes num
            # sitio, valores noutro) so batiam por coincidencia de ordem.
            por_nome = {coluna: _lit(u[campo]) for coluna, campo in COLUNA_E_CAMPO}
            por_nome.update({coluna: _lit(json.dumps(u[campo], ensure_ascii=False,
                                                     sort_keys=True))
                             for coluna, campo in COLUNA_E_CAMPO_JSON})
            por_nome.update(run_id=_lit(run_id), ordem=str(i),
                            raw_observation_id=obs_sql,
                            corrida_sha256=_lit(impressao))
            if set(por_nome) != set(COLUNAS_ESCRITAS):
                raise ValueError("colunas a gravar != COLUNAS_ESCRITAS: %s"
                                 % sorted(set(por_nome) ^ set(COLUNAS_ESCRITAS)))
            colunas = [por_nome[n] for n in COLUNAS_ESCRITAS]
            valores.append("(" + ", ".join(colunas) + ")")
        # ⚠️ A INTERPOLAÇÃO AQUI É `str.format`, E NÃO `%`. O corpo plpgsql usa
        # `%` como marcador do `raise exception`, e um `%` do Python em cima
        # disso fez a primeira versão rebentar antes de chegar ao banco:
        #
        #     DOIS DONOS DO MESMO SÍMBOLO NA MESMA STRING.
        # ⚠️ IDEMPOTENTE POR CORRIDA NÃO É IDEMPOTENTE POR DOCUMENTO. Medido na
        # 2.ª passagem do ensaio offline (A2/A3): uma matéria REVALIDADA e igual
        # (o coletor marcou-a SEEN_AGAIN; o derivado foi REUSED) atravessava a
        # Admission outra vez e ganhava uma SEGUNDA linha na Sala, com outro
        # run_id — 4 notícias em dobro. A trava por corrida não via isso.
        #
        #     O MESMO DOCUMENTO NA MESMA VERSÃO = A MESMA LINHA.
        #     VERSÃO NOVA = LINHA NOVA. NUNCA SE APAGA A ANTIGA.
        #
        # A identidade é (item_id, universo): `derived:<n>` é o derivado, que a
        # régua da 022 já deduplica pelos bytes (bytes novos = derivado novo =
        # versão nova); o universo entra porque o mesmo documento reencaminhado
        # (D2, REROUTE) a outra pergunta é outra entrada. A observação nova não
        # se perde: fica em raw_asset e na participação na derivação — só não
        # volta à fila da Inteligência. Uma segunda trava, GLOBAL e sempre
        # depois da da corrida, serializa a pergunta «já está?» entre corridas.
        #
        # ⚠️ DEDUP-DOC (25/09): O DERIVADO NÃO É O DOCUMENTO. Medido na Sala real:
        # 4 páginas com o MESMO endereço e o MESMO texto ganharam 2.ª linha porque
        # o bruto mudou uns bytes (sha novo → derivado novo → item_id novo). E a
        # IT-T9-011 ganhou 3.ª linha a 25/09 só porque o extrator passou a ler o
        # menu. Por isso a pergunta «já está?» também se faz pelo DOCUMENTO:
        # (source_id, document_key) do bruto, no mesmo universo.
        #
        #     SÓ FUNDE QUEM TEM IDENTIDADE PROVADA (FORWARD_IDENTIFIED).
        #     «NÃO SEI QUAL DOCUMENTO» NUNCA FUNDE COM NADA.
        #
        # Consequência declarada: uma versão nova do MESMO documento (conteúdo
        # mudou de verdade) também não ganha 2.ª linha. A observação nova não se
        # perde — fica em raw_asset e no derivado. Nada na Sala é apagado.
        script = """
create temporary table _recibo (resultado text) on commit drop;
create temporary table _entrada (like public.sala_de_espera including defaults) on commit drop;
do $sala$
declare
  ja char(64);
  n integer;
  total integer;
begin
  perform pg_advisory_xact_lock(hashtext({run}));
  perform pg_advisory_xact_lock(hashtext('sala_de_espera:identidade'));
  select corrida_sha256 into ja
    from public.sala_de_espera where run_id = {run} limit 1;
  if ja is null then
    insert into _entrada
      ({colunas})
    values {valores};
    select count(*) into total from _entrada;
    insert into public.sala_de_espera
      ({colunas})
    select {colunas}
      from _entrada e
     where not exists (select 1 from public.sala_de_espera s
                        where s.item_id = e.item_id and s.universo = e.universo
                          and s.run_id <> e.run_id)
       and not exists (select 1
                         from public.raw_asset re
                         join public.raw_asset rs
                           on rs.identity_state = 'FORWARD_IDENTIFIED'
                          and rs.source_id = re.source_id
                          and rs.document_key = re.document_key
                         join public.sala_de_espera s
                           on s.raw_observation_id = rs.id
                        where re.id = e.raw_observation_id
                          and re.identity_state = 'FORWARD_IDENTIFIED'
                          and s.universo = e.universo
                          and s.run_id <> e.run_id)
       and not exists (select 1
                         from _entrada e2
                         join public.raw_asset r2 on r2.id = e2.raw_observation_id
                         join public.raw_asset re on re.id = e.raw_observation_id
                        where e2.ordem < e.ordem
                          and e2.universo = e.universo
                          and re.identity_state = 'FORWARD_IDENTIFIED'
                          and r2.identity_state = 'FORWARD_IDENTIFIED'
                          and r2.source_id = re.source_id
                          and r2.document_key = re.document_key);
    get diagnostics n = row_count;
    if n > 0 then
      insert into _recibo values ('{pousou}:' || n || ':' || (total - n));
    else
      insert into _recibo values ('{ja_estava}:0:' || total);
    end if;
  elsif ja = {sha} then
    insert into _recibo values ('{ja_estava}:0:-1');
  else
    raise exception
      '{conflito}: a corrida % ja pousou conteudo DIFERENTE (impressao %, agora %). NAO foi escrito nada.',
      {run}, ja, {sha};
  end if;
end
$sala$;
select resultado from _recibo;
""".format(run=_lit(run_id), valores=", ".join(valores),
           colunas=", ".join(COLUNAS_ESCRITAS),
           sha=_lit(impressao), pousou=POUSOU, ja_estava=JA_ESTAVA,
           conflito=RUN_ID_CONFLICT)
        codigo, saida, erro = self._executar(script)
        if codigo != 0:
            if RUN_ID_CONFLICT in erro:
                raise ConflitoDeCorrida(erro.strip())
            # A chave primária a morder é `(run_id, ordem)` — e ordem é gerada
            # aqui, por posição. Se ela morder, alguém escreveu por fora.
            raise SalaIndisponivel(erro.strip() or "psql falhou sem dizer porque")
        partes = (saida or "").strip().split(":")
        estado = partes[0]
        if estado not in (POUSOU, JA_ESTAVA) or len(partes) != 3:
            raise SalaIndisponivel(
                "o banco nao devolveu recibo legivel: %r" % saida)
        # -1 = retry da mesma corrida: nao se volta a perguntar item a item.
        self.ultimo_recibo = {"INSERIDAS": int(partes[1]),
                              "JA_NA_SALA_POR_OUTRA_CORRIDA": (None if partes[2] == "-1"
                                                               else int(partes[2]))}
        return estado

    # ── 033 · corrigir sem apagar: as revisoes ────────────────────────
    def rever(self, run_id, ordem, revisoes, extrator, versao, motivo):
        """Acrescenta revisoes a UMA linha da Sala. So INSERT; a linha nao muda.

        `revisoes` = `[{"CAMPO", "VALOR", "BASE"}]`. Uma revisao so entra se
        MUDA alguma coisa: o valor atual (a ultima revisao, senao a coluna
        original) e a base atual sao comparados, e o igual nao se repete.

            REPROCESSAR DUAS VEZES COM O MESMO CODIGO NAO ESCREVE NADA.

        A decisao e tomada no banco, debaixo de uma trava por LINHA, na mesma
        transacao da escrita — pela mesma razao de `pousar`.
        """
        for x in (extrator, versao, motivo):
            if not x or not str(x).strip():
                raise ValueError("revisao sem extrator, versao ou motivo")
        blocos = []
        for r in revisoes:
            campo = r["CAMPO"]
            if campo not in CAMPOS_REVISIVEIS:
                raise ValueError("campo %r nao se reve (033)" % campo)
            coluna_da_base = CAMPOS_REVISIVEIS[campo]
            base_original = ("s." + coluna_da_base if coluna_da_base
                             else _lit(AUSENCIA_REVISAO))
            blocos.append("""
  select r.valor, r.base into v_atual, b_atual
    from public.sala_de_espera_revisao r
   where r.run_id = {run} and r.ordem = {ordem} and r.campo = {campo}
   order by r.revisao desc limit 1;
  if not found then
    select s.{campo_col}::text, {base_original} into v_atual, b_atual
      from public.sala_de_espera s
     where s.run_id = {run} and s.ordem = {ordem};
    if not found then
      raise exception 'SALA_REVISAO_SEM_LINHA: a sala nao tem (%, %)', {run}, {ordem};
    end if;
  end if;
  if v_atual is distinct from {valor} or b_atual is distinct from {base} then
    select coalesce(max(r.revisao), 0) + 1 into prox
      from public.sala_de_espera_revisao r
     where r.run_id = {run} and r.ordem = {ordem} and r.campo = {campo};
    insert into public.sala_de_espera_revisao
      (run_id, ordem, campo, revisao, valor, base, extrator,
       versao_do_extrator, motivo)
    values ({run}, {ordem}, {campo}, prox, {valor}, {base}, {extrator},
            {versao}, {motivo});
    n := n + 1;
  else
    iguais := iguais + 1;
  end if;""".format(run=_lit(run_id), ordem=int(ordem), campo=_lit(campo),
                  campo_col=campo, base_original=base_original,
                  valor=_lit(r["VALOR"]), base=_lit(r["BASE"]),
                  extrator=_lit(extrator), versao=_lit(versao),
                  motivo=_lit(motivo)))
        script = """
create temporary table _recibo (resultado text) on commit drop;
do $rev$
declare
  v_atual text;
  b_atual text;
  prox integer;
  n integer := 0;
  iguais integer := 0;
begin
  perform pg_advisory_xact_lock(hashtext('sala_de_espera_revisao:' || {run} || ':' || {ordem}));
{blocos}
  insert into _recibo values (n || ':' || iguais);
end
$rev$;
select resultado from _recibo;
""".format(run=_lit(run_id), ordem=int(ordem), blocos="".join(blocos))
        codigo, saida, erro = self._executar(script)
        if codigo != 0:
            raise SalaIndisponivel(erro.strip() or "psql falhou sem dizer porque")
        partes = (saida or "").strip().split(":")
        if len(partes) != 2:
            raise SalaIndisponivel("o banco nao devolveu recibo legivel: %r" % saida)
        return {"INSERIDAS": int(partes[0]), "JA_ERAM_ASSIM": int(partes[1])}

    def ler_atual(self, run_id):
        """A corrida como a Intelligence a deve ler: pela vista `sala_de_espera_atual`.

        ⚠️ NAO E `ler`. `ler` devolve o que POUSOU — e e com ele que `pousar`
        distingue um retry de um conflito. Ler aqui as revisoes faria um retry
        honesto parecer outra historia.
        """
        linhas = self._consultar(
            "select ordem, item_id, raw_observation_id, universo, texto, "
            "source_id, source_location, source_location_basis, fact_location, "
            "fact_location_basis, fact_time, fact_time_basis, published_at, "
            "published_at_basis, observed_at, completude_tempo_lugar, "
            "janela_declarada, tempo_lugar_evidencia, captured_at, estagio, revisoes "
            "from public.sala_de_espera_atual where run_id = %s order by ordem"
            % _lit(run_id))
        if not linhas:
            return None
        nomes = ("ORDEM", "ITEM_ID", "RAW_OBSERVATION_ID", "UNIVERSO", "TEXTO",
                 "SOURCE_ID", "SOURCE_LOCATION", "SOURCE_LOCATION_BASIS",
                 "FACT_LOCATION", "FACT_LOCATION_BASIS", "FACT_TIME",
                 "FACT_TIME_BASIS", "PUBLISHED_AT", "PUBLISHED_AT_BASIS",
                 "OBSERVED_AT", "COMPLETUDE_TEMPO_LUGAR", "JANELA_DECLARADA",
                 "TEMPO_LUGAR_EVIDENCIA", "CAPTURED_AT", "ESTAGIO", "REVISOES")
        itens = []
        for l in linhas:
            u = dict(zip(nomes, l.split(self.SEP)))
            u["ORDEM"], u["REVISOES"] = int(u["ORDEM"]), int(u["REVISOES"])
            u["RAW_OBSERVATION_ID"] = ("NAO SEI" if u["RAW_OBSERVATION_ID"] == ""
                                       else int(u["RAW_OBSERVATION_ID"]))
            u["COMPLETUDE_TEMPO_LUGAR"] = json.loads(u["COMPLETUDE_TEMPO_LUGAR"])
            u["JANELA_DECLARADA"] = json.loads(u["JANELA_DECLARADA"])
            u["TEMPO_LUGAR_EVIDENCIA"] = json.loads(u["TEMPO_LUGAR_EVIDENCIA"])
            itens.append(u)
        return {"RUN_ID": run_id, "ITENS": itens}

    def linhas_para_revisao(self):
        """Todas as linhas, pela vista, com o sha256 do bruto (para o livro)."""
        nomes = ("RUN_ID", "ORDEM", "ITEM_ID", "RAW_OBSERVATION_ID", "UNIVERSO",
                 "SOURCE_ID", "CAPTURED_AT", "SHA256", "STORAGE_PATH",
                 "MEDIA_TYPE", "TEXTO")
        fora = []
        for l in self._consultar(
                "select a.run_id, a.ordem, a.item_id, a.raw_observation_id, "
                "a.universo, a.source_id, a.captured_at, coalesce(r.sha256, ''), "
                "coalesce(r.storage_path, ''), coalesce(r.media_type, ''), "
                "a.texto from public.sala_de_espera_atual a "
                "left join public.raw_asset r on r.id = a.raw_observation_id "
                "order by a.pousado_em, a.run_id, a.ordem"):
            u = dict(zip(nomes, l.split(self.SEP)))
            u["ORDEM"] = int(u["ORDEM"])
            u["SHA256"] = u["SHA256"].strip()
            fora.append(u)
        return fora

    # ── a fila ──────────────────────────────────────────────────────────
    def listar_pendentes(self, limite=None):
        # pelo NOME, como `ler`: o select nasce da mesma tabela que a leitura usa
        sql = ("select %s from public.sala_de_espera "
               "where estado_da_fila = %s order by pousado_em, run_id, ordem"
               % (", ".join(c for c, _ in COLUNAS_PENDENTES), _lit(A_ESPERA)))
        if limite is not None:
            sql += " limit %d" % int(limite)
        fora = []
        for l in self._consultar(sql):
            partes = l.split(self.SEP)
            if len(partes) != len(COLUNAS_PENDENTES):
                raise SalaIndisponivel(
                    "listar_pendentes: %d valores para %d colunas"
                    % (len(partes), len(COLUNAS_PENDENTES)))
            u = {campo: v for (_, campo), v in zip(COLUNAS_PENDENTES, partes)}
            u["ORDEM"] = int(u["ORDEM"])
            fora.append(u)
        return fora

    def retirar(self, run_id, item_id, por):
        """WAITING → CONSUMED. Idempotente, e NÃO apaga.

        ⚠️ ISTO NÃO É INTELIGÊNCIA. Não recebe veredito, não conhece KEEP, TEMP
        nem DISCARD, e não tem onde os guardar. Diz «saiu da fila» e diz quem o
        tirou — e é tudo o que a Collection tem o direito de dizer sobre um item
        depois de o entregar.
        """
        if not por or not str(por).strip():
            raise ValueError("retirar sem autor nao e retirar: `por` vazio")
        alvo = self._consultar(
            "select ordem, estado_da_fila from public.sala_de_espera "
            "where run_id = %s and item_id = %s order by ordem"
            % (_lit(run_id), _lit(item_id)))
        if not alvo:
            raise ItemDesconhecido(
                "a sala nao tem (%s, %s)" % (run_id, item_id))
        if len(alvo) > 1:
            raise ItemAmbiguo(
                "ITEM_ID %r aparece %d vezes na corrida %s: nao serve de "
                "endereco. `admissao.decidir()` devolve \"?\" quando o item nao "
                "traz id nem url." % (item_id, len(alvo), run_id))
        ordem, estado = alvo[0].split(self.SEP)
        if estado == RETIRADO:
            return JA_ESTAVA
        codigo, _saida, erro = self._executar(
            "update public.sala_de_espera set estado_da_fila = %s, "
            "consumido_em = now(), consumido_por = %s "
            "where run_id = %s and ordem = %s and estado_da_fila = %s;"
            % (_lit(RETIRADO), _lit(por), _lit(run_id), ordem, _lit(A_ESPERA)))
        if codigo != 0:
            raise SalaIndisponivel(erro.strip())
        return POUSOU


def _sanitiza(texto):
    """A DSN nunca aparece num log. Um erro do `psql` pode trazê-la dentro."""
    import re
    t = texto or ""
    t = re.sub(r"postgres(ql)?://[^\s\"']*", "<URL_OMITIDA>", t)
    return t


# ═════════════════════════════════════════════════════════════════════════
# A ESCOLHA — explícita, e sem queda silenciosa
# ═════════════════════════════════════════════════════════════════════════

def _dsn():
    """⚠️ NÃO NASCE UM SEGUNDO COFRE PARA A MESMA CHAVE.

    `SUPABASE_DB_URL` é o secret que o resto da casa já usa. `SINTONIA_SALA_DSN`
    existe só para apontar a sala para um banco DESCARTÁVEL numa prova, sem
    tocar no nome de produção.
    """
    for nome in ("SINTONIA_SALA_DSN", "SUPABASE_DB_URL"):
        v = os.environ.get(nome)
        if v and v.strip():
            return v.strip()
    return None


def backend():
    """Qual backend está activo NESTE processo. Um só, e declarado.

        SEM VARIÁVEL, O BACKEND É O NÃO CANÓNICO — E O RECIBO DI-LO.

    Isso não é um fallback: é o valor por omissão da PROVA offline, e todo o
    recibo que sai dele carrega `CANONICO: False`. Quem opera não confia na
    omissão — chama `exigir_canonica()`, que recusa exactamente este caso.
    """
    escolhido = (os.environ.get("SINTONIA_SALA_BACKEND") or "").strip().upper()
    if escolhido == BACKEND_POSTGRES:
        url = _dsn()
        if not url:
            raise SalaIndisponivel(
                "SINTONIA_SALA_BACKEND=POSTGRES sem DSN. Defina SINTONIA_SALA_DSN "
                "(descartavel) ou SUPABASE_DB_URL. NAO se cai para ficheiro: "
                "um fallback silencioso para disco efemero e a falha original.")
        return _Postgres(url)
    if escolhido in ("", BACKEND_FICHEIRO):
        return _Ficheiro()
    raise SalaIndisponivel(
        "SINTONIA_SALA_BACKEND=%r nao e um backend conhecido. Conhecidos: %s"
        % (escolhido, ", ".join((BACKEND_POSTGRES, BACKEND_FICHEIRO))))


def estado_operacional():
    """O que a sala é, agora, neste ambiente. Nunca um palpite."""
    try:
        b = backend()
    except SalaIndisponivel as erro:
        return {"BACKEND": (os.environ.get("SINTONIA_SALA_BACKEND") or "").upper()
                           or "NAO SEI",
                "CANONICO": False, "DISPONIVEL": False, "PORQUE": str(erro)}
    return {"BACKEND": b.NOME, "CANONICO": b.CANONICO, "DISPONIVEL": True,
            "PORQUE": b.PORQUE}


def exigir_canonica():
    """O PORTÃO. Chama-se ANTES da aquisição, e fecha por omissão.

        COLETAR MATERIAL REAL PARA UMA SALA QUE NÃO SOBREVIVE
        É PAGAR REDE PARA PRODUZIR NADA.

    Devolve o estado quando pode continuar. Levanta `SalaIndisponivel` quando
    não — e `UNKNOWN` conta como não.
    """
    e = estado_operacional()
    if not e["DISPONIVEL"] or not e["CANONICO"]:
        raise SalaIndisponivel(
            "a sala canonica nao esta activa (BACKEND=%s · CANONICO=%s): %s"
            % (e["BACKEND"], e["CANONICO"], e["PORQUE"]))
    # ⚠️ CONFIGURACAO NAO E CONETIVIDADE. Ate 2026-09-17 o portao parava aqui
    # e dizia PASS; o replay canario 3 passou por ele e morreu na primeira
    # chamada ao psql. Agora o portao FALA com o banco, pelo mesmo psql que o
    # runtime vai usar: `select 1`, inofensivo, antes de qualquer rede. Sem
    # executavel ou sem resposta, levanta — e o workflow para no 5b.
    e.update(backend().sondar())
    return e


# ═════════════════════════════════════════════════════════════════════════
# A API PÚBLICA — igual para os dois backends
# ═════════════════════════════════════════════════════════════════════════

def ler(run_id: str):
    """O que está pousado nesta corrida, ou `None`. Nunca inventa vazio."""
    return backend().ler(run_id)


def pousar(run_id: str, unidades: list) -> dict:
    """A unidade pronta pousa na espera. Devolve o que ACONTECEU, não o pedido.

        POUSOU     escreveu-se agora
        JA ESTAVA  a corrida ja tinha exactamente este conteudo

    E se a corrida já lá estiver com conteúdo DIFERENTE, isto levanta
    `ConflitoDeCorrida` e não escreve nada.

    ⚠️ UMA LISTA VAZIA NÃO É UMA ESPERA. Zero unidades admitidas não produz
    registo: dizer «esta corrida chegou à espera» com zero itens seria dizer
    uma coisa que não aconteceu.
    """
    b = backend()
    if not unidades:
        return {"ESTADO": None, "RUN_ID": run_id, "FICHEIRO": None,
                "MORADA": None, "UNIDADES": 0,
                "BACKEND": b.NOME, "CANONICO": b.CANONICO,
                "PORQUE": "nenhuma unidade admitida: nao ha o que pousar"}
    _conferir_unidades(unidades)
    b.ultimo_recibo = None
    estado = b.pousar(run_id, unidades)
    morada = b.morada(run_id)
    # So o Postgres (canonico) sabe dizer quantas ja estavam por outra corrida;
    # o ficheiro (prova offline) guarda a corrida inteira e diz NAO SEI.
    recibo = getattr(b, "ultimo_recibo", None) or {}
    ja_na_sala = recibo.get("JA_NA_SALA_POR_OUTRA_CORRIDA")
    if estado == POUSOU:
        porque = "escrita publicada nesta execucao"
    elif ja_na_sala:
        porque = "todas as unidades ja estavam na sala por outra corrida"
    else:
        porque = "a corrida ja tinha exactamente este conteudo"
    return {"ESTADO": estado, "RUN_ID": run_id,
            # `FICHEIRO` fica pelo consumidor que já o lê. `MORADA` é o nome
            # novo e é o que não mente quando o backend não é um ficheiro.
            "FICHEIRO": morada, "MORADA": morada,
            "UNIDADES": len(unidades),
            "INSERIDAS": recibo.get("INSERIDAS", "NAO SEI"),
            "JA_NA_SALA_POR_OUTRA_CORRIDA": ("NAO SEI" if ja_na_sala is None else ja_na_sala),
            "BACKEND": b.NOME, "CANONICO": b.CANONICO,
            "PORQUE": porque}


def rever(run_id: str, ordem: int, revisoes: list, *, extrator: str,
          versao: str, motivo: str) -> dict:
    """Corrige campos de UMA linha SEM a mudar: acrescenta revisoes (033).

        O RAW NAO MUDA. A LINHA NAO MUDA. NUNCA HA UPDATE CALADO.

    Devolve `{INSERIDAS, JA_ERAM_ASSIM}`. So a Sala canonica sabe fazer isto.
    """
    return backend().rever(run_id, ordem, revisoes, extrator, versao, motivo)


def ler_atual(run_id: str):
    """A corrida pela vista `sala_de_espera_atual` (ultima revisao, senao o original)."""
    return backend().ler_atual(run_id)


def linhas_para_revisao():
    """Todas as linhas da Sala, pela vista, com o sha256 do bruto."""
    return backend().linhas_para_revisao()


def listar_pendentes(limite=None):
    """Quem ainda espera. O que já foi retirado NÃO aparece aqui."""
    return backend().listar_pendentes(limite)


def retirar(run_id: str, item_id: str, por: str) -> dict:
    """O item sai da fila. Continua na sala, e continua auditável.

        RETIRAR NÃO É APAGAR.

    ⚠️ E NÃO É JULGAR. Esta função não recebe veredito de relevância, e é de
    propósito: `KEEP`/`TEMP`/`DISCARD` são da Intelligence, e a Intelligence é
    outra missão. O que a Collection pode dizer é que entregou, e a quem.
    """
    b = backend()
    estado = b.retirar(run_id, item_id, por)
    return {"ESTADO": estado, "RUN_ID": run_id, "ITEM_ID": item_id,
            "ESTADO_DA_FILA": RETIRADO, "POR": por,
            "BACKEND": b.NOME, "CANONICO": b.CANONICO,
            "PORQUE": ("saiu da fila nesta execucao" if estado == POUSOU
                       else "ja tinha saido da fila")}


def main(argv=None):
    """⚠️ E O PORTAO DA SALA FALA PELA PROPRIA SALA.

        python3 admissao/sala_de_espera.py --portao
        sai 0  a sala canonica esta activa: pode adquirir
        sai 1  nao esta: NAO adquirir

    Houve uma versao intermedia desta missao com um `motor/preflight_da_coleta.py`
    a COMPOR este portao e o do egresso. Foi deitada fora, e o mapa e que a
    apanhou: uma peca nova a morar numa gaveta que nao era a do seu territorio.
    A pergunta certa veio a seguir — para que serve um terceiro ficheiro se cada
    dono ja sabe responder por si, e a ORDEM mora no workflow?

        UM COMPOSITOR QUE SO ENCADEIA DOIS DONOS
        E UM TERCEIRO SITIO ONDE A VERDADE PODE DIVERGIR.

    O workflow chama os dois portoes, um a seguir ao outro, antes da aquisicao.
    """
    argv = sys.argv[1:] if argv is None else argv
    if "--portao" in argv:
        try:
            e = exigir_canonica()
        except SalaIndisponivel as erro:
            print("SALA_DE_ESPERA=BLOCKED")
            print("  %s" % erro)
            print("  COLETAR PARA UMA SALA QUE NAO SOBREVIVE E PAGAR REDE POR NADA.")
            return 1
        print("SALA_DE_ESPERA=PASS · BACKEND=%s · SONDA=%s · PSQL_ORIGEM=%s"
              % (e["BACKEND"], e.get("SONDA"), e.get("PSQL_ORIGEM")))
        print("  %s" % e["PORQUE"])
        if e.get("PSQL"):
            print("  psql: %s" % e["PSQL"])
        return 0
    print(__doc__.strip().split("\n")[0])
    e = estado_operacional()
    print("backend: %s · canonico: %s" % (e["BACKEND"], e["CANONICO"]))
    print("porque: %s" % e["PORQUE"])
    print("morada do backend de ficheiro: %s" % os.path.relpath(MORADA, RAIZ))
    print("estados: %s (pousou) · %s (ja estava)" % (POUSOU, JA_ESTAVA))
    print("fila: %s -> %s" % (A_ESPERA, RETIRADO))
    print("conflito: %s" % RUN_ID_CONFLICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
