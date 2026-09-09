#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O DONO CANÔNICO DA ESCRITA — quem guarda o byte também escreve a memória.

POR QUE ISTO EXISTE
-------------------
A Itália tem 195 objetos guardados no armazém e **zero** linhas a dizer quem os
trouxe. Não foi bug: foi um caminho onde os dois passos nunca precisaram andar
juntos. Este ficheiro é a garantia **para a frente** — não conserta o passado,
impede que uma coleta NOVA volte a produzir armazém sem memória em silêncio.

    ARMAZÉM CHEIO + LIVRO DE ENTRADA EM BRANCO
    PARECE SAÚDE E É O CONTRÁRIO.

AS TRÊS CONFUSÕES QUE ESTE FICHEIRO RECUSA
------------------------------------------
A primeira versão disto provava a lógica, e só a lógica. Um red team encontrou
o buraco, e ele é o mesmo buraco três vezes:

    SQL ACEITE            não é      LINHA GRAVADA
    TESTE COM SIMULACRO   não é      RECONCILIAÇÃO DE BANCO
    COMPLETE NO PYTHON    não é      CONCLUIDA NO POSTGRES

Antes, `escrever_memoria(sql)` era dada por bem-sucedida **por não ter
rebentado**, e o número de linhas era o número *esperado*, copiado para o lugar
do *observado*. Com `on conflict do nothing`, o SQL pode correr inteiro, não
gravar nada e não se queixar. A corrida ficava verde sobre um banco vazio — que
é, letra por letra, o estado italiano outra vez.

    LINHAS_OBSERVADAS VEM DE UMA LEITURA. SEMPRE.

E `sql_da_memoria` abria a corrida como `'rodando'` e nunca a promovia. Era
possível ter `RUN_STATE = COMPLETE` no manifesto e `status = 'rodando'` no
banco. **A garantia só fecha quando as duas casas dizem a mesma coisa.**

IDEMPOTÊNCIA NÃO É «NÃO FAÇA NADA E FINJA QUE ESTÁ CERTO»
---------------------------------------------------------
`do nothing` sozinho esconde conflito: se já existe uma linha naquele
`storage_path` com **outro** `sha256`, o SQL passa calado e o acervo fica com
duas verdades. Por isso a linha existente é **lida e comparada** antes de
escrever:

    igual em tudo   →  REUSED_METADATA      (retry legítimo)
    diferente       →  METADATA_CONFLICT    e a corrida NÃO fecha

A DOUTRINA
----------
    EXECUTOR         produz o artefato. Não conhece banco.
    DONO CANÔNICO    persiste o par: byte + memória. É este ficheiro.

E ele continua a **não** falar com o banco: gera SQL auditável, e a mão que o
aplica é injetada como `Memoria`. Isso é o que permite provar contra um banco
descartável sem tocar em produção.
"""
import hashlib
import json
import os


# ─────────────────────────────────────────────────────────────────────────
# VOCABULÁRIO — reusado, não inventado
# ─────────────────────────────────────────────────────────────────────────
# O enum do banco (migration 001) é ('rodando','concluida','vazia','parcial',
# 'falhou'). Ele NÃO tem estado para «byte guardado, memória por escrever» — e
# esta missão NÃO acrescenta um: a pendência mora no manifesto da corrida, do
# lado do Git, e mapeia para `parcial` no banco. Menos esquema, mesma verdade.
COMPLETE, PARTIAL, FAILED = "COMPLETE", "PARTIAL", "FAILED"

RODANDO, CONCLUIDA, PARCIAL, FALHOU = "rodando", "concluida", "parcial", "falhou"

UPLOAD_PENDING_METADATA = "UPLOAD_PENDING_METADATA"
METADATA_PENDING_UPLOAD = "METADATA_PENDING_UPLOAD"
METADATA_CONFLICT = "METADATA_CONFLICT"
RUN_ID_CONFLICT = "RUN_ID_CONFLICT"
RUN_NOT_CLOSED_IN_DB = "RUN_NOT_CLOSED_IN_DB"
PRESERVED_AND_REGISTERED = "PRESERVED_AND_REGISTERED"

# Os campos que fazem de uma linha de `raw_asset` a MESMA linha. `source_url`
# entra porque duas publicações do mesmo byte são dois factos sobre o mundo —
# foi o que os 195 objetos italianos provaram.
IDENTIDADE_DO_OBJETO = ("run_id", "sha256", "bytes", "captured_at", "source_url")

# A linha inteira, para a conferência DEPOIS da escrita. Inclui `media_type` e
# `storage_path`, que a comparação prévia não precisava de olhar — ali o
# caminho era a chave da busca, aqui é uma coisa a confirmar.
CAMPOS_DA_LINHA = ("run_id", "storage_path", "media_type", "bytes", "sha256",
                   "captured_at", "source_url")

# A identidade congelada da corrida (COL-LAW-211). Se ela mudar, não é a mesma
# execução — e aceitar em silêncio deixaria duas corridas partilharem um nome.
IDENTIDADE_DA_CORRIDA = ("actor", "actor_version", "source_country",
                         "started_at", "rule_version", "capture_method")


class Armazem:
    """A porta do armazém. Três perguntas, e nenhuma delas é «apague».

    Não há `remover` de propósito: se a memória falhar depois do envio, apagar
    o byte para fingir atomicidade destruiria a única evidência que sobrou.
    """

    def existe(self, caminho: str) -> bool:
        raise NotImplementedError

    def enviar(self, caminho: str, dados: bytes, media_type: str) -> None:
        raise NotImplementedError

    def ler(self, caminho: str) -> bytes:
        raise NotImplementedError


class Memoria:
    """A porta do banco. Escreve, e sobretudo **deixa ler de volta**.

    `aplicar` não devolve nada de propósito: o que ela devolveria seria a
    opinião do cliente SQL sobre o que aconteceu, e é exatamente essa opinião
    que não vale. Quem conta as linhas é `objetos_da_corrida`, com um `SELECT`.
    """

    def aplicar(self, sql: str) -> None:
        raise NotImplementedError

    def corrida(self, run_id: str) -> dict:
        """A linha de `collection_run`, ou `None`."""
        raise NotImplementedError

    def objeto_em(self, storage_path: str) -> dict:
        """A linha de `raw_asset` naquele caminho, ou `None`."""
        raise NotImplementedError

    def objetos_da_corrida(self, run_id: str) -> list:
        """Todas as linhas de `raw_asset` daquela corrida. É esta leitura que
        produz `LINHAS_OBSERVADAS` — nunca uma contagem esperada."""
        raise NotImplementedError


class ArmazemLocal(Armazem):
    """O armazem em disco. A terceira implementacao, e faltava-lhe o sitio.

    ⚠️ A PORTA DO ARMAZEM TINHA DUAS IMPLEMENTACOES: uma DE MENTIRA, para
    provar, e a da Supabase, que e producao remota. Nao havia nenhuma que
    corresse aqui — e essa e uma das razoes por que nenhum ficheiro de producao
    chamava `preservar()`: para preservar era preciso ou fingir, ou ir a rede.

        UM DONO QUE SO SABE ESCREVER LONGE
        E UM DONO QUE NINGUEM CHAMA DE PERTO.

    Ela nao apaga, como nenhum armazem desta casa apaga: se a memoria falhar
    depois do envio, o byte enviado e a unica evidencia que sobra.
    """

    def __init__(self, raiz):
        self.raiz = str(raiz)
        self.envios = 0

    def _abs(self, caminho):
        # O caminho vem do artefato e e relativo a raiz. Um caminho absoluto ou
        # com `..` escreveria fora do armazem, e um armazem que escreve fora de
        # si nao e um armazem.
        alvo = os.path.normpath(os.path.join(self.raiz, caminho))
        if not alvo.startswith(os.path.normpath(self.raiz) + os.sep):
            raise ValueError("caminho fora do armazem: %s" % caminho)
        return alvo

    def existe(self, caminho):
        return os.path.isfile(self._abs(caminho))

    def enviar(self, caminho, dados, media_type):
        alvo = self._abs(caminho)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "wb") as fh:
            fh.write(dados)
        self.envios += 1

    def ler(self, caminho):
        with open(self._abs(caminho), "rb") as fh:
            return fh.read()


class ArmazemDeMentira(Armazem):
    """Armazém de teste: um dicionário, e uma maneira de o mandar falhar."""

    def __init__(self):
        self.objetos = {}
        self.falhar_a_partir_de = None
        self.envios = 0

    def existe(self, caminho):
        return caminho in self.objetos

    def enviar(self, caminho, dados, media_type):
        if self.falhar_a_partir_de == caminho:
            raise IOError("armazem recusou %s" % caminho)
        self.envios += 1
        self.objetos[caminho] = (dados, media_type)

    def ler(self, caminho):
        return self.objetos[caminho][0]


def sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


# ─────────────────────────────────────────────────────────────────────────
# 1 · O PLANO — que objeto guardar, e quantos
# ─────────────────────────────────────────────────────────────────────────
def caminho_do_objeto(artefato: dict) -> str:
    """O endereço do byte no armazém.

    A chave é `PAIS/FONTE/TIPO/<sha16>-<discriminante>-<nome>`. O `sha16` está
    lá porque um nome repetido não pode sobrescrever bytes diferentes — mas ele
    é **endereço**, nunca identidade: a identidade é o `sha256` inteiro, e um
    prefixo curto não prova conteúdo igual.

    O DISCRIMINANTE separa duas publicações do MESMO byte. Medido nos 195
    objetos italianos: a ADAMA publicou o mesmo PDF em `media/731` e em
    `media/6321`. Dois factos sobre o mundo, um conteúdo só.
    """
    return "%s/%s/%s/%s-%s-%s" % (
        artefato["COUNTRY"], artefato["SOURCE_SLUG"], artefato["ARTIFACT_KIND"],
        artefato["SHA256"][:16], artefato["SOURCE_NATIVE_ID"], artefato["NAME"])


def planear(artefatos: list) -> dict:
    """Decide, ANTES de enviar, quantos objetos deviam existir.

    É esta conta que a reconciliação vai cobrar. Sem plano escrito antes, «o
    que devia ter acontecido» vira o que aconteceu — e aí nenhuma falha é
    detetável.

    ⚠️ E não confunde as espécies:

        CONTEÚDO   os bytes.           identidade = sha256
        OBJETO     uma cópia guardada. identidade = o caminho
        RELAÇÃO    produto usa documento. NÃO exige byte novo.
    """
    por_caminho, conteudos, relacoes = {}, set(), 0
    for a in artefatos:
        caminho = caminho_do_objeto(a)
        conteudos.add(a["SHA256"])
        if caminho in por_caminho:
            relacoes += 1
            por_caminho[caminho]["USADO_POR"].append(a.get("USED_BY"))
            continue
        por_caminho[caminho] = dict(a, STORAGE_PATH=caminho,
                                    USADO_POR=[a.get("USED_BY")])
    return {
        "REGISTOS_DE_ENTRADA": len(artefatos),
        "CONTEUDOS_UNICOS": len(conteudos),
        "OBJETOS_PLANEADOS": len(por_caminho),
        "RELACOES_SEM_BYTE_NOVO": relacoes,
        "PORQUE_OS_TRES_NUMEROS_DIFEREM": (
            "REGISTO nao e CONTEUDO e nao e OBJETO. Dois produtos que usam o "
            "mesmo documento na mesma URL sao DOIS registos, UM conteudo e UM "
            "objeto. O mesmo conteudo publicado em DUAS URLs e UM conteudo e "
            "DOIS objetos. Nenhuma das tres contagens e derivavel das outras."),
        "OBJETOS": list(por_caminho.values()),
    }


# ─────────────────────────────────────────────────────────────────────────
# 2 · O ENVIO E A CONFERÊNCIA DOS BYTES
# ─────────────────────────────────────────────────────────────────────────
def enviar_os_bytes(plano: dict, armazem: Armazem, bytes_de) -> dict:
    """Envia o que falta, e só o que falta.

    Um retry depois de a memória falhar NÃO volta a subir byte nenhum: o objeto
    já lá está e `existe()` decide. Cada envio a mais é uma oportunidade a mais
    de escrever por cima do que estava certo.
    """
    novos, reaproveitados, falhados = [], [], []
    for obj in plano["OBJETOS"]:
        caminho = obj["STORAGE_PATH"]
        if armazem.existe(caminho):
            reaproveitados.append(caminho)
            continue
        try:
            armazem.enviar(caminho, bytes_de(obj), obj["MEDIA_TYPE"])
        except Exception as erro:                      # noqa: BLE001
            falhados.append({"STORAGE_PATH": caminho, "ERRO": str(erro)})
            continue
        novos.append(caminho)
    return {"NOVOS": novos, "REAPROVEITADOS": reaproveitados, "FALHADOS": falhados}


def conferir_os_bytes(plano: dict, armazem: Armazem) -> dict:
    """Lê de volta e confere o `sha256`, um a um.

    «Enviei» não é «chegou». Sem esta leitura, um armazém que aceita e descarta
    em silêncio daria uma corrida verde com o acervo vazio.
    """
    conferidos, divergentes, ausentes = [], [], []
    for obj in plano["OBJETOS"]:
        caminho = obj["STORAGE_PATH"]
        if not armazem.existe(caminho):
            ausentes.append(caminho)
            continue
        if sha256(armazem.ler(caminho)) == obj["SHA256"]:
            conferidos.append(caminho)
        else:
            divergentes.append(caminho)
    return {"CONFERIDOS": conferidos, "DIVERGENTES": divergentes,
            "AUSENTES": ausentes}


# ─────────────────────────────────────────────────────────────────────────
# 3 · O CONFLITO — `do nothing` não pode calar divergência
# ─────────────────────────────────────────────────────────────────────────
def _difere(existente: dict, esperado: dict, campos) -> list:
    fora = []
    for c in campos:
        a, b = existente.get(c), esperado.get(c)
        if a is None and b is None:
            continue
        if str(a) != str(b):
            fora.append({"CAMPO": c, "NO_BANCO": a, "NESTA_CORRIDA": b})
    return fora


def _linha_esperada(run_id: str, obj: dict) -> dict:
    return {"run_id": run_id, "storage_path": obj["STORAGE_PATH"],
            "media_type": obj["MEDIA_TYPE"], "bytes": obj["BYTES"],
            "sha256": obj["SHA256"], "captured_at": obj["CAPTURED_AT"],
            "source_url": obj.get("SOURCE_URL")}


def conferir_o_que_ja_existe(run: dict, plano: dict, memoria: Memoria) -> dict:
    """Lê o banco ANTES de escrever, e decide reencontro ou conflito.

    Esta função é a resposta a «`do nothing` ainda pode esconder conflito?».
    Não pode: a linha existente é lida e comparada campo a campo. Repetir a
    mesma corrida é `REUSED`; encontrar outro `sha256` no mesmo caminho é
    `METADATA_CONFLICT`, e a corrida não fecha.
    """
    reusados, conflitos = [], []
    for obj in plano["OBJETOS"]:
        existente = memoria.objeto_em(obj["STORAGE_PATH"])
        if not existente:
            continue
        fora = _difere(existente, _linha_esperada(run["RUN_ID"], obj),
                       IDENTIDADE_DO_OBJETO)
        if fora:
            conflitos.append({"TIPO": METADATA_CONFLICT,
                              "STORAGE_PATH": obj["STORAGE_PATH"],
                              "DIVERGENCIAS": fora})
        else:
            reusados.append(obj["STORAGE_PATH"])

    corrida = memoria.corrida(run["RUN_ID"])
    conflito_de_corrida = None
    if corrida:
        esperada = {c: run.get(c.upper()) for c in IDENTIDADE_DA_CORRIDA}
        fora = _difere(corrida, esperada, IDENTIDADE_DA_CORRIDA)
        if fora:
            conflito_de_corrida = {"TIPO": RUN_ID_CONFLICT,
                                   "RUN_ID": run["RUN_ID"], "DIVERGENCIAS": fora}
    return {
        "REUSED_METADATA": reusados,
        "CONFLITOS_DE_OBJETO": conflitos,
        "CONFLITO_DE_CORRIDA": conflito_de_corrida,
        "O_QUE_ISTO_IMPEDE": (
            "que `on conflict do nothing` engula uma divergencia. SQL aceite "
            "nao e linha gravada, e linha antiga com outro sha256 no mesmo "
            "caminho e duas verdades no mesmo endereco."),
    }


# ─────────────────────────────────────────────────────────────────────────
# 4 · A MEMÓRIA — SQL auditável, nunca ligação direta
# ─────────────────────────────────────────────────────────────────────────
def _texto(v):
    if v is None:
        return "null"
    return "'" + str(v).replace("'", "''") + "'"


def sql_da_memoria(run: dict, conferidos: list, plano: dict) -> str:
    """A corrida abre `rodando`, e os objetos conferidos entram.

    DUAS TRAVAS, E NENHUMA É DECORATIVA:

    1. **Só entra o que foi CONFERIDO** — lido de volta do armazém e com o hash
       batido. Uma linha para um byte que não voltou seria a mentira italiana
       ao contrário: memória sem byte.
    2. **`on conflict (storage_path) do nothing`** torna o retry seguro. Mas
       sozinho ele calaria conflito — por isso `conferir_o_que_ja_existe()`
       corre **antes**, e o conflito é apanhado lá.
    """
    por_caminho = {o["STORAGE_PATH"]: o for o in plano["OBJETOS"]}
    linhas = [
        "-- MEMORIA OPERACIONAL DA CORRIDA %s" % run["RUN_ID"],
        "-- Gerado por guarda/preservar_coleta.py. NAO EDITAR A MAO.",
        "-- A corrida abre 'rodando'. Ela so e promovida a 'concluida' pelo",
        "-- SQL DE FECHO, e depois da reconciliacao ter sido LIDA do banco.",
        "begin;",
        "insert into public.collection_run (run_id, platform, actor, "
        "actor_version, mission, source_country, started_at, rule_version, "
        "capture_method, status)",
        "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'rodando')" % (
            _texto(run["RUN_ID"]), _texto(run["PLATFORM"]), _texto(run["ACTOR"]),
            _texto(run["ACTOR_VERSION"]), _texto(run.get("MISSION")),
            _texto(run["SOURCE_COUNTRY"]), _texto(run["STARTED_AT"]),
            _texto(run["RULE_VERSION"]), _texto(run.get("CAPTURE_METHOD"))),
        "on conflict (run_id) do nothing;",
    ]
    for caminho in conferidos:
        o = por_caminho[caminho]
        linhas.append(
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, source_url) values "
            "(%s, %s, %s, %d, %s, %s, %s) "
            "on conflict (storage_path) do nothing;" % (
                _texto(run["RUN_ID"]), _texto(caminho), _texto(o["MEDIA_TYPE"]),
                o["BYTES"], _texto(o["SHA256"]), _texto(o["CAPTURED_AT"]),
                _texto(o.get("SOURCE_URL"))))
    linhas.append("commit;")
    return "\n".join(linhas) + "\n"


def conferir_o_que_ficou_escrito(run: dict, plano: dict, memoria: Memoria) -> dict:
    """Lê CADA objeto de volta DEPOIS de escrever, e compara campo a campo.

    POR QUE CONTAR NÃO CHEGA
    ------------------------
    Ler antes de escrever fecha o caso normal, mas deixa uma janela:

        1. a leitura prévia não encontra nada naquele caminho
        2. outro escritor mete lá uma linha DIVERGENTE
        3. o nosso `insert` cai no `on conflict do nothing` — e cala-se
        4. a CONTAGEM bate: há uma linha, e era uma linha que se esperava

    A conta fecharia sobre um conteúdo que não é o nosso.

        CONTAGEM BATER NÃO É METADATA BATER.

    Por isso a última palavra é esta: cada linha esperada é lida do banco e
    comparada nos campos que a identificam. Uma divergência aqui é
    `METADATA_CONFLICT`, e a corrida não fecha.
    """
    conferidos, divergentes, ausentes = [], [], []
    for obj in plano["OBJETOS"]:
        caminho = obj["STORAGE_PATH"]
        escrita = memoria.objeto_em(caminho)
        if not escrita:
            ausentes.append(caminho)
            continue
        esperada = _linha_esperada(run["RUN_ID"], obj)
        fora = _difere(escrita, esperada, CAMPOS_DA_LINHA)
        if fora:
            divergentes.append({"TIPO": METADATA_CONFLICT,
                                "STORAGE_PATH": caminho, "DIVERGENCIAS": fora})
        else:
            conferidos.append(caminho)
    return {
        "POST_WRITE_METADATA_MATCH": len(conferidos),
        "DIVERGENTES": divergentes,
        "AUSENTES": ausentes,
        "CAMPOS_COMPARADOS": list(CAMPOS_DA_LINHA),
        "O_QUE_ISTO_IMPEDE": (
            "que a contagem certa esconda o conteudo errado. Entre a leitura "
            "previa e o nosso insert outro escritor pode meter uma linha "
            "divergente no mesmo caminho; o `do nothing` cala-se e a conta "
            "fecha na mesma. Contar nao e conferir."),
    }


def sql_de_fecho(run_id: str, terminou_em: str, quantos: int) -> str:
    """Promove a corrida a `concluida` — e **só** este SQL o faz.

    Ele corre DEPOIS da reconciliação ter sido lida do banco. É o que impede
    `RUN_STATE = COMPLETE` no manifesto com `status = 'rodando'` no Postgres:
    o fecho não é uma opinião do Python, é um `UPDATE` que a seguir se lê de
    volta para confirmar.

    E a trava está no próprio `where`: a promoção só acontece se a corrida
    ainda estiver `rodando`. Fechar duas vezes não muda nada, e fechar uma
    corrida que outro processo já marcou como falhada não a ressuscita.

    ⚠️ **`STARTED_AT` NÃO É `FINISHED_AT`, e um não se infere do outro.** A
    versão anterior caía para o `started_at` quando não lhe davam hora de fim.
    A corrida passava a dizer que acabou no instante em que começou — falso, e
    com cara de medido, que é pior do que faltar.

    Sem hora declarada, a autoridade do tempo é **o próprio banco**: entra
    `now()`, dentro do `UPDATE`. Um relógio só, e nenhum inventado aqui.
    """
    quando = _texto(terminou_em) if terminou_em else "now()"
    return (
        "-- FECHO DA CORRIDA %s. Corre depois da reconciliacao LIDA do banco.\n"
        "-- finished_at: %s\n"
        "update public.collection_run set status = 'concluida', "
        "finished_at = %s, item_count_raw = %d "
        "where run_id = %s and status = 'rodando';\n"
        % (run_id,
           "declarado por quem fechou" if terminou_em else
           "now() do proprio banco — STARTED_AT nunca e copiado para ca",
           quando, quantos, _texto(run_id)))


# ─────────────────────────────────────────────────────────────────────────
# 5 · A CADEIA, E O FECHO SÓ QUANDO AS DUAS CASAS CONCORDAM
# ─────────────────────────────────────────────────────────────────────────
def preservar(run: dict, artefatos: list, armazem: Armazem, bytes_de,
              memoria: Memoria = None, terminou_em: str = None) -> dict:
    """A cadeia inteira.

        PLANEAR → ENVIAR → CONFERIR BYTES → VER O QUE JÁ EXISTE
        → ESCREVER → LER DE VOLTA → RECONCILIAR → FECHAR NO BANCO → LER OUTRA VEZ

    `memoria` é a porta do banco, injetada. Este ficheiro nunca abre ligação —
    é o que permite prová-lo contra um banco descartável sem tocar em produção.

    O QUE NUNCA ACONTECE AQUI: apagar o byte preservado para fingir que a
    transação foi atómica. Armazém e Postgres não são uma transação só, e
    fingir que são custaria a evidência.
    """
    if not run.get("RUN_ID"):
        # NAO HA CORRIDA GENERICA. Sem run_id nada e preservado canonicamente —
        # e nao existe `LEGACY-IT`, `UNKNOWN-RUN` nem `BACKFILL-RUN` para tapar
        # o buraco. Corrida que nao existiu nao se inventa.
        raise ValueError("artefato sem corrida nao entra: nao ha RUN generica")

    plano = planear(artefatos)
    envio = enviar_os_bytes(plano, armazem, bytes_de)
    prova = conferir_os_bytes(plano, armazem)

    sql = sql_da_memoria(run, prova["CONFERIDOS"], plano)
    ja_la = {"REUSED_METADATA": [], "CONFLITOS_DE_OBJETO": [],
             "CONFLITO_DE_CORRIDA": None}
    memoria_estado = {"TENTADA": False, "APLICADA": False, "ERRO": None,
                      "LINHAS_ESPERADAS": len(prova["CONFERIDOS"]),
                      "LINHAS_OBSERVADAS": None,
                      "COMO_FOI_MEDIDO": "NAO MEDIDO — nao houve leitura do banco"}
    fecho = {"TENTADO": False, "STATUS_NO_BANCO": None, "FINISHED_AT": None}
    pos_escrita = None

    if memoria is not None:
        ja_la = conferir_o_que_ja_existe(run, plano, memoria)
        ha_conflito = bool(ja_la["CONFLITOS_DE_OBJETO"]
                           or ja_la["CONFLITO_DE_CORRIDA"])
        memoria_estado["TENTADA"] = True
        if ha_conflito:
            # NAO SE ESCREVE POR CIMA DE UMA DIVERGENCIA. Parar aqui deixa o
            # banco como estava e a corrida por fechar — que e o resultado
            # honesto de duas verdades no mesmo endereco.
            memoria_estado["ERRO"] = "conflito detetado antes de escrever"
        else:
            try:
                memoria.aplicar(sql)
                memoria_estado["APLICADA"] = True
            except Exception as erro:                  # noqa: BLE001
                memoria_estado["ERRO"] = str(erro)

        # ── A LEITURA QUE VALE ───────────────────────────────────────────
        # LINHAS_OBSERVADAS vem de um SELECT. Nunca de len(CONFERIDOS): com
        # `do nothing`, o SQL pode correr inteiro e nao gravar nada.
        linhas = memoria.objetos_da_corrida(run["RUN_ID"])
        esperados_no_caminho = {o["STORAGE_PATH"] for o in plano["OBJETOS"]}
        memoria_estado["LINHAS_OBSERVADAS"] = len(
            [x for x in linhas if x.get("storage_path") in esperados_no_caminho])
        memoria_estado["COMO_FOI_MEDIDO"] = (
            "SELECT em raw_asset por run_id, filtrado pelos caminhos do plano. "
            "Leitura real do banco, nao contagem esperada.")
        # E A ULTIMA PALAVRA: cada linha lida de volta e comparada campo a
        # campo. Contar nao e conferir.
        pos_escrita = conferir_o_que_ficou_escrito(run, plano, memoria)

    esperados = plano["OBJETOS_PLANEADOS"]
    conferidos = len(prova["CONFERIDOS"])
    observadas = memoria_estado["LINHAS_OBSERVADAS"]

    campos_batem = (pos_escrita is not None
                    and not pos_escrita["DIVERGENTES"]
                    and pos_escrita["POST_WRITE_METADATA_MATCH"] == esperados)
    reconciliou = (observadas is not None and observadas == esperados
                   and conferidos == esperados and campos_batem)

    # ── O FECHO NO BANCO, E SÓ DEPOIS DA RECONCILIAÇÃO ───────────────────
    if memoria is not None and reconciliou and not memoria_estado["ERRO"]:
        fecho["TENTADO"] = True
        # STARTED_AT NAO E FINISHED_AT, e um nao se infere do outro. A versao
        # anterior caia para o `STARTED_AT` quando nao tinha hora de fim — e
        # entao a corrida dizia ter acabado no instante em que comecou, o que
        # e falso e parece medido. Sem hora de fim declarada, PERGUNTA-SE AO
        # BANCO: ele e a autoridade unica do tempo de fecho, e o `now()` mora
        # no proprio UPDATE. Nos testes injeta-se a hora; na operacao nao se
        # fabrica nenhuma.
        fim = terminou_em or run.get("FINISHED_AT")
        fecho["ORIGEM_DO_FINISHED_AT"] = (
            "declarado por quem fechou" if fim else "now() do proprio banco")
        try:
            memoria.aplicar(sql_de_fecho(run["RUN_ID"], fim, observadas))
        except Exception as erro:                      # noqa: BLE001
            fecho["ERRO"] = str(erro)
        corrida = memoria.corrida(run["RUN_ID"]) or {}
        fecho["STATUS_NO_BANCO"] = corrida.get("status")
        fecho["FINISHED_AT"] = corrida.get("finished_at")
    elif memoria is not None:
        corrida = memoria.corrida(run["RUN_ID"]) or {}
        fecho["STATUS_NO_BANCO"] = corrida.get("status")

    condicoes = {
        "plano_feito": esperados > 0 or not artefatos,
        "bytes_no_armazem": not prova["AUSENTES"],
        "bytes_conferidos": not prova["DIVERGENTES"] and conferidos == esperados,
        "nenhum_envio_falhado": not envio["FALHADOS"],
        "sem_conflito_de_metadata": not ja_la["CONFLITOS_DE_OBJETO"],
        "sem_conflito_de_corrida": ja_la["CONFLITO_DE_CORRIDA"] is None,
        "memoria_aplicada": memoria_estado["APLICADA"],
        # A CONDICAO QUE FALTAVA: a conta vem de uma LEITURA do banco.
        "reconciliacao_observada": reconciliou,
        # E ESTA IMPEDE QUE A CONTA CERTA ESCONDA O CONTEUDO ERRADO.
        "campos_batem_apos_escrita": campos_batem,
        # E A OUTRA: as duas casas tem de dizer a mesma coisa.
        "banco_diz_concluida": fecho["STATUS_NO_BANCO"] == CONCLUIDA,
    }
    faltou = sorted(k for k, v in condicoes.items() if not v)

    pendencia = None
    if ja_la["CONFLITO_DE_CORRIDA"]:
        pendencia = RUN_ID_CONFLICT
    elif ja_la["CONFLITOS_DE_OBJETO"]:
        pendencia = METADATA_CONFLICT
    # Divergencia encontrada DEPOIS de escrever tambem e conflito, e tem de vir
    # antes de UPLOAD_PENDING_METADATA na fila. Senao o caso de corrida —
    # contagem certa, conteudo errado — sairia rotulado como «falta escrever»,
    # que e o diagnostico errado e manda o operador repetir o passo errado.
    elif pos_escrita and pos_escrita["DIVERGENTES"]:
        pendencia = METADATA_CONFLICT
    elif condicoes["bytes_conferidos"] and not condicoes["reconciliacao_observada"]:
        pendencia = UPLOAD_PENDING_METADATA
    elif condicoes["reconciliacao_observada"] and not condicoes["banco_diz_concluida"]:
        pendencia = RUN_NOT_CLOSED_IN_DB
    elif condicoes["memoria_aplicada"] and not condicoes["bytes_conferidos"]:
        pendencia = METADATA_PENDING_UPLOAD
    elif not faltou:
        pendencia = PRESERVED_AND_REGISTERED

    return {
        "RUN_ID": run["RUN_ID"],
        "PLANO": {k: v for k, v in plano.items() if k != "OBJETOS"},
        "ENVIO": {"NOVOS": len(envio["NOVOS"]),
                  "REAPROVEITADOS": len(envio["REAPROVEITADOS"]),
                  "FALHADOS": envio["FALHADOS"]},
        "PROVA_DOS_BYTES": {k: len(v) if k == "CONFERIDOS" else v
                            for k, v in prova.items()},
        "JA_EXISTIA_NO_BANCO": {
            "REUSED_METADATA": len(ja_la["REUSED_METADATA"]),
            "CONFLITOS_DE_OBJETO": ja_la["CONFLITOS_DE_OBJETO"],
            "CONFLITO_DE_CORRIDA": ja_la["CONFLITO_DE_CORRIDA"],
        },
        "MEMORIA": memoria_estado,
        "CONFERENCIA_POS_ESCRITA": pos_escrita,
        "FECHO_NO_BANCO": fecho,
        "SQL": sql,
        "RECONCILIACAO": {
            "OBJETOS_ESPERADOS": esperados,
            "OBJETOS_CONFERIDOS": conferidos,
            "LINHAS_OBSERVADAS_NO_BANCO": observadas,
            "A_LEI_DA_CONTA": (
                "OBJETOS_ESPERADOS == OBJETOS_CONFERIDOS == "
                "LINHAS_OBSERVADAS_NO_BANCO. A conta e entre ESPECIES "
                "COMPARAVEIS, e o ultimo numero vem de um SELECT — nunca do "
                "numero esperado copiado para o lugar do observado."),
        },
        "RUN_STATE": COMPLETE if not faltou else PARTIAL,
        "COMPLETION_BASIS": {
            "CONDICOES": condicoes,
            "FALTOU": faltou,
            "PORQUE": ("todas as condicoes de fecho foram medidas e cumpridas, "
                       "e o banco tambem diz concluida"
                       if not faltou else "fecho incompleto: " + ", ".join(faltou)),
        },
        "PENDENCIA": pendencia,
        "AS_DUAS_CASAS_CONCORDAM": (
            (COMPLETE if not faltou else PARTIAL) == COMPLETE
            and fecho["STATUS_NO_BANCO"] == CONCLUIDA),
        "O_QUE_FAZER_A_SEGUIR": (
            "nada — o par byte+memoria esta fechado dos dois lados" if not faltou
            else "repetir SO a etapa em falta. Os bytes ficam onde estao: apagar "
                 "bruto preservado para fingir atomicidade destruiria a evidencia."),
        "BYTE_APAGADO_COMO_COMPENSACAO": "NAO — e nao ha caminho no codigo para isso",
    }


def relatorio(resultado: dict) -> str:
    return json.dumps({k: v for k, v in resultado.items() if k != "SQL"},
                      ensure_ascii=False, indent=1)
