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

# Os 12 campos da COL-LAW-043, na ordem em que
# `admissao.pronto_para_inteligencia()` os constrói. Escritos aqui para que a
# travessia para o banco tenha dois lados a comparar — e há prova que reprova se
# o dono mudar e isto não mudar.
CAMPOS_READY = (
    "ESTADO", "ITEM_ID", "RAW_OBSERVATION_ID", "UNIVERSO", "TEXTO",
    "SOURCE_ID", "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME",
    "CAPTURED_AT", "CORRIDA", "ADMITIDO_POR",
)

# O nome do estado do CONTRATO (não o da fila). Vive em `admissao`; aqui só se
# confere o que chega e se reconstrói o que sai.
PRONTO = "PRONTO_PARA_INTELIGENCIA"

BACKEND_POSTGRES = "POSTGRES"
BACKEND_FICHEIRO = "FICHEIRO"


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


class _Ficheiro(object):
    """O backend da V1. Guardado inteiro, e declarado NÃO canónico."""

    NOME = BACKEND_FICHEIRO
    CANONICO = False
    PORQUE = ("o ficheiro vive no workspace do runner: nao sobrevive ao job "
              "nem ao checkout seguinte. Serve prova offline, nao operacao.")

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

    # ── as duas maneiras de falar com o banco ───────────────────────────
    def _consultar(self, sql):
        """Lê. `-X` para não herdar o `~/.psqlrc` de quem corre isto."""
        r = subprocess.run(
            ["psql", "-X", "-q", "-A", "-t", "-F", self.SEP,
             "-R", self.SEP_LINHA,
             "-v", "ON_ERROR_STOP=1", self.url, "-c", sql],
            capture_output=True, text=True, env=_ambiente_psql())
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
        r = subprocess.run(
            ["psql", "-X", "-q", "-A", "-t", "-F", self.SEP,
             "-R", self.SEP_LINHA,
             "-v", "ON_ERROR_STOP=1", "--single-transaction", self.url, "-f", "-"],
            input=script, capture_output=True, text=True, env=_ambiente_psql())
        return r.returncode, r.stdout.replace(self.SEP_LINHA, "\n"), _sanitiza(r.stderr)

    def morada(self, run_id):
        return "postgres:public.sala_de_espera?run_id=%s" % run_id

    # ── ler ─────────────────────────────────────────────────────────────
    def ler(self, run_id):
        linhas = self._consultar(
            "select ordem, item_id, raw_observation_id, universo, texto, "
            "source_id, source_location, fact_location, fact_time, "
            "captured_at, admitido_por "
            "from public.sala_de_espera where run_id = %s order by ordem"
            % _lit(run_id))
        if not linhas:
            return None
        itens = []
        for l in linhas:
            c = l.split(self.SEP)
            # ⚠️ `raw_observation_id` NULO QUER DIZER `NAO SEI`, e é assim que
            # o contrato o escreve. Devolver `None` aqui inventaria uma terceira
            # maneira de dizer a mesma ausência.
            obs = c[2]
            itens.append({
                "ESTADO": PRONTO,
                "ITEM_ID": c[1],
                "RAW_OBSERVATION_ID": "NAO SEI" if obs == "" else int(obs),
                "UNIVERSO": c[3],
                "TEXTO": c[4],
                "SOURCE_ID": c[5],
                "SOURCE_LOCATION": c[6],
                "FACT_LOCATION": c[7],
                "FACT_TIME": c[8],
                "CAPTURED_AT": c[9],
                "CORRIDA": run_id,
                "ADMITIDO_POR": c[10],
            })
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
            valores.append(
                "(%s, %d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
                    _lit(run_id), i, _lit(u["ITEM_ID"]), obs_sql,
                    _lit(u["UNIVERSO"]), _lit(u["TEXTO"]), _lit(u["SOURCE_ID"]),
                    _lit(u["SOURCE_LOCATION"]), _lit(u["FACT_LOCATION"]),
                    _lit(u["FACT_TIME"]), _lit(u["CAPTURED_AT"]),
                    _lit(u["ADMITIDO_POR"]), _lit(impressao)))
        # ⚠️ A INTERPOLAÇÃO AQUI É `str.format`, E NÃO `%`. O corpo plpgsql usa
        # `%` como marcador do `raise exception`, e um `%` do Python em cima
        # disso fez a primeira versão rebentar antes de chegar ao banco:
        #
        #     DOIS DONOS DO MESMO SÍMBOLO NA MESMA STRING.
        script = """
create temporary table _recibo (resultado text) on commit drop;
do $sala$
declare
  ja char(64);
begin
  perform pg_advisory_xact_lock(hashtext({run}));
  select corrida_sha256 into ja
    from public.sala_de_espera where run_id = {run} limit 1;
  if ja is null then
    insert into public.sala_de_espera
      (run_id, ordem, item_id, raw_observation_id, universo, texto,
       source_id, source_location, fact_location, fact_time, captured_at,
       admitido_por, corrida_sha256)
    values {valores};
    insert into _recibo values ('{pousou}');
  elsif ja = {sha} then
    insert into _recibo values ('{ja_estava}');
  else
    raise exception
      '{conflito}: a corrida % ja pousou conteudo DIFERENTE (impressao %, agora %). NAO foi escrito nada.',
      {run}, ja, {sha};
  end if;
end
$sala$;
select resultado from _recibo;
""".format(run=_lit(run_id), valores=", ".join(valores),
           sha=_lit(impressao), pousou=POUSOU, ja_estava=JA_ESTAVA,
           conflito=RUN_ID_CONFLICT)
        codigo, saida, erro = self._executar(script)
        if codigo != 0:
            if RUN_ID_CONFLICT in erro:
                raise ConflitoDeCorrida(erro.strip())
            # A chave primária a morder é `(run_id, ordem)` — e ordem é gerada
            # aqui, por posição. Se ela morder, alguém escreveu por fora.
            raise SalaIndisponivel(erro.strip() or "psql falhou sem dizer porque")
        estado = (saida or "").strip()
        if estado not in (POUSOU, JA_ESTAVA):
            raise SalaIndisponivel(
                "o banco nao devolveu recibo legivel: %r" % saida)
        return estado

    # ── a fila ──────────────────────────────────────────────────────────
    def listar_pendentes(self, limite=None):
        sql = ("select run_id, ordem, item_id from public.sala_de_espera "
               "where estado_da_fila = %s order by pousado_em, run_id, ordem"
               % _lit(A_ESPERA))
        if limite is not None:
            sql += " limit %d" % int(limite)
        fora = []
        for l in self._consultar(sql):
            c = l.split(self.SEP)
            fora.append({"RUN_ID": c[0], "ORDEM": int(c[1]), "ITEM_ID": c[2]})
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
    estado = b.pousar(run_id, unidades)
    morada = b.morada(run_id)
    return {"ESTADO": estado, "RUN_ID": run_id,
            # `FICHEIRO` fica pelo consumidor que já o lê. `MORADA` é o nome
            # novo e é o que não mente quando o backend não é um ficheiro.
            "FICHEIRO": morada, "MORADA": morada,
            "UNIDADES": len(unidades),
            "BACKEND": b.NOME, "CANONICO": b.CANONICO,
            "PORQUE": ("escrita publicada nesta execucao" if estado == POUSOU
                       else "a corrida ja tinha exactamente este conteudo")}


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
        print("SALA_DE_ESPERA=PASS · BACKEND=%s" % e["BACKEND"])
        print("  %s" % e["PORQUE"])
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
