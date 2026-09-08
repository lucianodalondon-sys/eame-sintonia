#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O DONO CANÔNICO DA ESCRITA — quem guarda o byte também escreve a memória.

POR QUE ISTO EXISTE
-------------------
A Itália tem 195 objetos guardados no armazém e **zero** linhas a dizer quem os
trouxe. Não foi bug: foi um caminho onde os dois passos nunca precisaram andar
juntos. Quem enviou os bytes vive fora deste repositório; quem escreveria a
memória só sabe falar espanhol. Ninguém era dono do par.

    ARMAZÉM CHEIO + LIVRO DE ENTRADA EM BRANCO
    PARECE SAÚDE E É O CONTRÁRIO.

Este ficheiro é a garantia **para a frente**. Ele não conserta o passado — o
passado fica preservado e explicado, com a dívida no nome. Ele impede que uma
coleta NOVA volte a produzir armazém sem memória em silêncio.

A DOUTRINA QUE ELE APLICA
-------------------------
    EXECUTOR              produz o artefato. Não conhece banco.
    DONO CANÔNICO         persiste o par: byte + memória. É este ficheiro.

Nenhum executor deve gravar no banco só porque conhece a `SUPABASE_URL`. Foi
assim que a Espanha acabou com cinco escritores diferentes e a Itália com zero.

E ELE NÃO FALA COM O BANCO
--------------------------
Segue o padrão que esta casa já provou em `guarda/catalogo_importar.py`: gera
**SQL auditável**, que entra no Git e passa por `guarda/sql_conferir.py` antes
de qualquer produção o ver. O primeiro a olhar não pode ser a produção.

O ARMAZÉM É UMA PORTA, NÃO UMA BIBLIOTECA
-----------------------------------------
`Armazem` é uma interface de três métodos. A implementação real fala HTTP e
vive noutro sítio; a de teste é um dicionário. É isso que permite provar os
casos de falha — upload passa e memória falha, processo morre a meio, retry —
sem tocar em produção e sem instalar nada.

O QUE ELE NÃO FAZ, DE PROPÓSITO
-------------------------------
Não aplica migration, não abre ligação, não apaga byte nenhum. E **não inventa
corrida**: um artefato sem corrida não entra — não há `RUN` genérica, nem
`LEGACY`, nem `BACKFILL`.
"""
import hashlib
import json


# ─────────────────────────────────────────────────────────────────────────
# VOCABULÁRIO — reusado, não inventado
# ─────────────────────────────────────────────────────────────────────────
# O enum do banco (migration 001) é ('rodando','concluida','vazia','parcial',
# 'falhou'). Ele NÃO tem estado para «byte guardado, memória por escrever» — e
# esta missão NÃO acrescenta um: a pendência mora no manifesto da corrida, do
# lado do Git, e mapeia para `parcial` no banco. Menos esquema, mesma verdade.
COMPLETE, PARTIAL, FAILED = "COMPLETE", "PARTIAL", "FAILED"

UPLOAD_PENDING_METADATA = "UPLOAD_PENDING_METADATA"
METADATA_PENDING_UPLOAD = "METADATA_PENDING_UPLOAD"
PRESERVED_AND_REGISTERED = "PRESERVED_AND_REGISTERED"


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


class ArmazemDeMentira(Armazem):
    """Armazém de teste: um dicionário, e uma maneira de o mandar falhar.

    Existe para que os casos difíceis — envio passa e memória falha, processo
    morre a meio, retry — sejam PROVADOS em vez de descritos num comentário.
    """

    def __init__(self):
        self.objetos = {}
        self.falhar_a_partir_de = None   # nome do caminho que rebenta
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
    lá porque um nome de ficheiro repetido não pode sobrescrever bytes
    diferentes — mas ele é **endereço**, nunca identidade: a identidade é o
    `sha256` inteiro, e um prefixo curto não prova conteúdo igual.

    O DISCRIMINANTE é o que separa duas publicações do MESMO byte. Medido nos
    195 objetos italianos: a ADAMA publicou o mesmo PDF em dois endereços
    (`media/731` e `media/6321`), e por isso ele está guardado duas vezes. São
    dois factos sobre o mundo — as duas páginas publicaram — e um conteúdo só.
    """
    return "%s/%s/%s/%s-%s-%s" % (
        artefato["COUNTRY"], artefato["SOURCE_SLUG"], artefato["ARTIFACT_KIND"],
        artefato["SHA256"][:16], artefato["SOURCE_NATIVE_ID"], artefato["NAME"])


def planear(artefatos: list) -> dict:
    """Decide, ANTES de enviar, quantos objetos deviam existir.

    É esta conta que a reconciliação vai cobrar no fim. Sem plano escrito
    antes, «o que devia ter acontecido» vira o que aconteceu — e aí nenhuma
    falha é detetável.

    ⚠️ E não confunde as espécies:

        CONTEÚDO   os bytes.        identidade = sha256
        OBJETO     uma cópia guardada. identidade = o caminho
        RELAÇÃO    produto usa documento. NÃO exige byte novo.
    """
    por_caminho, conteudos, relacoes = {}, set(), 0
    for a in artefatos:
        caminho = caminho_do_objeto(a)
        conteudos.add(a["SHA256"])
        if caminho in por_caminho:
            # Mesmo byte, mesma publicação, outro produto: é RELAÇÃO LÓGICA.
            # Duplicar o byte aqui seria gastar armazém para representar uma
            # linha de tabela.
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
# 2 · O ENVIO — idempotente por endereço
# ─────────────────────────────────────────────────────────────────────────
def enviar_os_bytes(plano: dict, armazem: Armazem, bytes_de) -> dict:
    """Envia o que falta, e só o que falta.

    Um retry depois de a memória falhar NÃO volta a subir byte nenhum: o
    objeto já lá está, e `existe()` decide. Subir de novo custaria banda para
    obter exatamente o mesmo estado — e cada envio a mais é uma oportunidade a
    mais de escrever por cima do que estava certo.
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
    return {"NOVOS": novos, "REAPROVEITADOS": reaproveitados,
            "FALHADOS": falhados}


def conferir_os_bytes(plano: dict, armazem: Armazem) -> dict:
    """Lê de volta e confere o `sha256`, um a um.

    «Enviei» não é «chegou». Sem esta leitura, um armazém que aceita e descarta
    silenciosamente daria uma corrida verde com o acervo vazio.
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
# 3 · A MEMÓRIA — SQL auditável, nunca ligação direta
# ─────────────────────────────────────────────────────────────────────────
def _texto(v):
    if v is None:
        return "null"
    return "'" + str(v).replace("'", "''") + "'"


def sql_da_memoria(run: dict, conferidos: list, plano: dict) -> str:
    """Escreve a memória operacional como SQL que uma pessoa consegue ler.

    DUAS TRAVAS ESTÃO AQUI, E NENHUMA É DECORATIVA:

    1. **Só entra o que foi CONFERIDO.** Uma linha de `raw_asset` para um byte
       que não voltou do armazém seria a mentira exata que a Itália nos
       ensinou, ao contrário: memória sem byte em vez de byte sem memória.

    2. **`on conflict (storage_path) do nothing`.** É o que torna o retry
       seguro: repetir a escrita não duplica linha nem inventa `captured_at`
       novo. `storage_path` é `UNIQUE`; `sha256` não é — e não deve ser, porque
       o mesmo conteúdo pode estar guardado em dois endereços.
    """
    por_caminho = {o["STORAGE_PATH"]: o for o in plano["OBJETOS"]}
    linhas = [
        "-- MEMORIA OPERACIONAL DA CORRIDA %s" % run["RUN_ID"],
        "-- Gerado por guarda/preservar_coleta.py. NAO EDITAR A MAO.",
        "-- So entram objetos CONFERIDOS: lidos de volta do armazem e com o",
        "-- sha256 batido. Byte que nao voltou nao vira linha.",
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


# ─────────────────────────────────────────────────────────────────────────
# 4 · A RECONCILIAÇÃO E O FECHO — COMPLETE é o último passo
# ─────────────────────────────────────────────────────────────────────────
def preservar(run: dict, artefatos: list, armazem: Armazem, bytes_de,
              escrever_memoria=None) -> dict:
    """A cadeia inteira, e o fecho só no fim.

        PLANEAR → ENVIAR → CONFERIR → MEMÓRIA → RECONCILIAR → FECHAR

    `escrever_memoria` é a mão que leva o SQL ao banco. Ela é injetada — este
    ficheiro nunca abre ligação. Se ela falhar, ou se não existir, a corrida
    NÃO fica `COMPLETE`: fica `PARTIAL`, com `UPLOAD_PENDING_METADATA` escrito
    com todas as letras, e os bytes ficam onde estão.

    O QUE NUNCA ACONTECE AQUI: apagar o byte preservado para fingir que a
    transação foi atómica. Armazém e Postgres não são uma transação só, e
    fingir que são custaria a evidência.
    """
    if not run.get("RUN_ID"):
        # NAO HA CORRIDA GENERICA. Sem run_id nada e preservado canonicamente —
        # e nao existe `LEGACY-IT`, `UNKNOWN-RUN` nem `BACKFILL-RUN` para
        # tapar o buraco. Corrida que nao existiu nao se inventa.
        raise ValueError("artefato sem corrida nao entra: nao ha RUN generica")

    plano = planear(artefatos)
    envio = enviar_os_bytes(plano, armazem, bytes_de)
    prova = conferir_os_bytes(plano, armazem)

    sql = sql_da_memoria(run, prova["CONFERIDOS"], plano)
    memoria = {"TENTADA": False, "ESCRITA": False, "ERRO": None,
               "LINHAS_ESPERADAS": len(prova["CONFERIDOS"])}
    if escrever_memoria is not None:
        memoria["TENTADA"] = True
        try:
            escrever_memoria(sql)
            memoria["ESCRITA"] = True
        except Exception as erro:                      # noqa: BLE001
            memoria["ERRO"] = str(erro)

    esperados = plano["OBJETOS_PLANEADOS"]
    conferidos = len(prova["CONFERIDOS"])
    escritas = conferidos if memoria["ESCRITA"] else 0

    # ── AS CONDIÇÕES DE FECHO, CADA UMA MEDIDA ──────────────────────────────
    # É a COL-LAW-210 aplicada ao par byte+memória. Duas condições novas em
    # relação ao fecho da estrada do PDF: os bytes chegaram, e a memória foi
    # escrita. Sem elas, «a corrida acabou» voltaria a poder significar «há
    # ficheiros numa pasta» — só que agora numa pasta remota.
    condicoes = {
        "plano_feito": esperados > 0 or not artefatos,
        "bytes_no_armazem": not prova["AUSENTES"],
        "bytes_conferidos": not prova["DIVERGENTES"] and conferidos == esperados,
        "nenhum_envio_falhado": not envio["FALHADOS"],
        "memoria_escrita": memoria["ESCRITA"],
        "reconciliacao_bate": escritas == esperados,
    }
    faltou = sorted(k for k, v in condicoes.items() if not v)

    pendencia = None
    if condicoes["bytes_conferidos"] and not condicoes["memoria_escrita"]:
        pendencia = UPLOAD_PENDING_METADATA
    elif condicoes["memoria_escrita"] and not condicoes["bytes_conferidos"]:
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
        "MEMORIA": memoria,
        "SQL": sql,
        "RECONCILIACAO": {
            "OBJETOS_ESPERADOS": esperados,
            "OBJETOS_CONFERIDOS": conferidos,
            "LINHAS_DE_MEMORIA": escritas,
            "A_LEI_DA_CONTA": (
                "OBJETOS_ESPERADOS == OBJETOS_CONFERIDOS == LINHAS_DE_MEMORIA. "
                "A conta e entre ESPECIES COMPARAVEIS: objeto guardado com "
                "objeto guardado. NAO se compara registo de manifesto com "
                "objeto de armazem — sao especies diferentes e a igualdade "
                "seria falsa."),
        },
        "RUN_STATE": COMPLETE if not faltou else PARTIAL,
        "COMPLETION_BASIS": {
            "CONDICOES": condicoes,
            "FALTOU": faltou,
            "PORQUE": ("todas as condicoes de fecho foram medidas e cumpridas"
                       if not faltou else "fecho incompleto: " + ", ".join(faltou)),
        },
        "PENDENCIA": pendencia,
        "O_QUE_FAZER_A_SEGUIR": (
            "nada — o par byte+memoria esta fechado" if not faltou else
            "repetir SO a etapa em falta. Os bytes ficam onde estao: apagar "
            "bruto preservado para fingir atomicidade destruiria a evidencia."),
        "BYTE_APAGADO_COMO_COMPENSACAO": "NAO — e nao ha caminho no codigo para isso",
    }


def relatorio(resultado: dict) -> str:
    return json.dumps({k: v for k, v in resultado.items() if k != "SQL"},
                      ensure_ascii=False, indent=1)
