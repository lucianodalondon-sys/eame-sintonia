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
SEM_IDENTIDADE_DE_FONTE = "SEM_IDENTIDADE_DE_FONTE"
NEW_RUN_SAME_STORAGE_PATH = "NEW_RUN_SAME_STORAGE_PATH"

# ─────────────────────────────────────────────────────────────────────────
# B5B · A IDENTIDADE DA OBSERVAÇÃO (migration 026)
# ─────────────────────────────────────────────────────────────────────────
# Três estados no banco, e ele recusa qualquer quarto. O terceiro — o do
# legado — NÃO TEM NOME NESTE FICHEIRO, e a ausência é a trava:
#
#     LEGADO É UM FACTO SOBRE QUEM JÁ LÁ ESTAVA NO CORTE DA FASE 8.
#     UM WRITER DE HOJE QUE O DECLARASSE MENTIRIA SOBRE QUANDO NASCEU.
#
# Não se escreve o que não se sabe nomear aqui — e o corte pelo surrogate
# recusaria a linha de qualquer maneira.
FORWARD_IDENTIFIED = "FORWARD_IDENTIFIED"
FORWARD_IDENTITY_UNPROVEN = "FORWARD_IDENTITY_UNPROVEN"
SOURCE_DOCUMENT_ID = "SOURCE_DOCUMENT_ID"

# As seis palavras que esta casa usa para confessar. Contadas no repositório,
# não inventadas aqui. Uma confissão preenchida é PIOR do que um campo vazio
# quando há índice em cima: `source_id = 'NAO SEI'` juntaria observações de
# fontes diferentes debaixo de uma palavra que quer dizer «não sei qual».
SENTINELAS = frozenset(("NAO SEI", "NAO_SEI", "NÃO SEI", "NAO_SE_APLICA",
                        "UNKNOWN", "NOT_KNOWN"))

# Os campos que fazem de uma linha de `raw_asset` a MESMA linha. `source_url`
# entra porque duas publicações do mesmo byte são dois factos sobre o mundo —
# foi o que os 195 objetos italianos provaram.
IDENTIDADE_DO_OBJETO = ("run_id", "sha256", "bytes", "captured_at", "source_url")

# E A CHAVE DE IDEMPOTÊNCIA, para a observação que TEM identidade (026).
# `captured_at` e `source_url` saem: um retry da mesma corrida pode trazer
# outra hora e outra URL — um espelho, um redirecionamento, um parâmetro que a
# fonte acrescentou — e continua a ser a MESMA observação. O que mudou foi por
# onde a tentativa passou, e a COL-LAW-206 já diz que a URL não é identidade.
#
#     RETRY DA MESMA CORRIDA  !=  OBSERVAÇÃO NOVA
#
# `run_id` FICA: corrida nova é observação nova, e é isso que a fase 10 vai
# deixar coexistir fisicamente. Até lá, uma corrida nova sobre o mesmo endereço
# continua a bater na trava antiga — de propósito, e com nome próprio.
IDENTIDADE_FORWARD = ("run_id", "source_id", "document_key", "sha256")

# E A CHAVE DA TENTATIVA, para a observação que NÃO tem identidade documental.
# O índice da fase 9 tem predicado `FORWARD_IDENTIFIED`; uma linha sem prova
# não o satisfaz, e por isso ela não tinha chave nenhuma — duplicava a cada
# retry, e duas sessões simultâneas duplicavam-na na mesma.
#
# ESCOLHIDA POR MEDIÇÃO, e não por gosto. Seis candidatas passaram pelos
# mesmos dez cenários em `provas/a_lei_da_fase_10.py`:
#
#     (run, fonte, sha256)                REPROVADA — junta o caso ADAMA
#     (fonte, sha256)                     REPROVADA — apaga a corrida nova
#     (run, fonte, endereço [, sha256])   passa tudo, MAS morre na fase 11
#     (run, fonte, objeto)                REPROVADA — sem objecto não constrange
#     (run, fonte, objeto, sha256)        APROVADA, com `nulls not distinct`
#
# `storage_object_id` e não `storage_path`: o endereço sai de `raw_asset` na
# fase 11, e uma chave construída sobre ele nasceria com dívida. O objecto é a
# espécie certa para responder «que cópia física foi esta».
#
#     UMA TENTATIVA E: esta corrida, desta fonte, sobre esta copia, destes bytes.
IDENTIDADE_SEM_PROVA = ("run_id", "source_id", "storage_object_id", "sha256")

# Os campos que a AFIRMAÇÃO DE IDENTIDADE de uma observação usa — e que por
# isso não podem ser reescritos depois. Os quatro primeiros são a afirmação;
# os três seguintes são o resto das duas chaves de idempotência.
#
#     `storage_path` NÃO está aqui, e isso é a prova de coerência: ele é
#     ENDEREÇO, e endereço muda sem que o facto mude.
IDENTIDADE_IMUTAVEL = ("identity_state", "source_id", "document_key",
                       "document_key_basis", "run_id", "sha256",
                       "storage_object_id")

# A linha inteira, para a conferência DEPOIS da escrita. Inclui `media_type` e
# `storage_path`, que a comparação prévia não precisava de olhar — ali o
# caminho era a chave da busca, aqui é uma coisa a confirmar.
CAMPOS_DA_LINHA = ("run_id", "storage_path", "media_type", "bytes", "sha256",
                   "captured_at", "source_url",
                   # 026: a conferência DEPOIS de escrever também lê a
                   # identidade. Escrever o estado certo e ler outro de volta é
                   # a mesma classe de erro que escrever o sha certo e ler
                   # outro — e essa já era conferida.
                   "identity_state", "source_id", "document_key",
                   "document_key_basis")

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

    def caminho_local(self, caminho: str) -> str:
        """ONDE, NESTE DISCO, ESTAO OS BYTES DESTE ENDERECO — ou `None`.

        ⚠️ ESTA NAO E UMA QUARTA PERGUNTA SOBRE O ARMAZEM: E A MESMA
        PERGUNTA DO `ler`, FEITA POR QUEM NAO PODE RECEBER OS BYTES.

        Uma ferramenta externa — `pdftotext`, por exemplo — nao recebe um
        `bytes`: recebe um CAMINHO e abre-o ela propria. Quem manda derivar
        tem entao duas saidas, e uma delas e pior:

            1. perguntar ao armazem ONDE o byte esta          (isto)
            2. copiar o byte para um sitio temporario         (uma segunda
               copia do bruto, que ninguem preserva e que
               passa a existir sem dono)

        E ha uma terceira, que e a que esta funcao existe para impedir:
        deixar quem chama RECONSTRUIR o caminho por fora, juntando a raiz
        ao `storage_path`. Isso poria a regra de enderecamento — a raiz, a
        travessia com `..`, o separador — em DOIS sitios.

            DOIS DONOS DO MESMO ENDERECO SAO DOIS ENDERECOS,
            E UM DELES VAI ESCREVER FORA DO ARMAZEM.

        `None` e resposta legitima e e a resposta CERTA de qualquer armazem
        que nao seja disco: um armazem de objetos remoto NAO tem caminho
        local, e inventar um ficheiro temporario aqui para poder devolver
        uma string seria responder a pergunta errada. Quem receber `None`
        sabe exactamente o que aconteceu — e nao fica com um caminho que
        parece bom e aponta para nada.

        NAO e identidade, e nao vira identidade: continua a ser um ENDERECO.

            ENDERECO FISICO != IDENTIDADE DA OBSERVACAO
        """
        return None


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

    # ── AS DUAS PERGUNTAS, QUE NUNCA FORAM UMA ──────────────────────────
    # ⚠️ AQUI VIVIA `objeto_em(storage_path)`, E ELE MISTURAVA AS ESPÉCIES:
    # perguntava «que OBJETO há neste endereço?» e ia buscar a resposta a
    # `raw_asset`, que guarda OBSERVAÇÕES. Enquanto o endereço foi único em
    # `raw_asset` o erro não aparecia — havia sempre uma linha, e as três
    # implementações faziam `linhas[0] if linhas else None`.
    #
    # Depois da fase 10 são N linhas, e `linhas[0]` passa a ser «a que o
    # planeador devolver primeiro».
    #
    #     ESCOLHER A PRIMEIRA E ESCOLHER AO ACASO COM CARA DE DETERMINISMO.
    #
    # Por isso a função foi PARTIDA, e não corrigida: cada pergunta tem agora
    # uma chave que a torna determinística por construção.

    def copia_em(self, storage_path: str) -> dict:
        """QUE CÓPIA existe neste endereço? A linha de `storage_object`, ou
        `None`.

        Determinística e assim continua: `unique (storage_object.storage_path)`
        é a identidade do OBJETO, e a fase 10 não lhe toca.
        """
        raise NotImplementedError

    def observacao_identificada(self, run_id, source_id, document_key,
                                sha256) -> dict:
        """QUE OBSERVAÇÃO é esta? A linha de `raw_asset` com esta chave
        forward completa, ou `None`.

        Determinística pelo índice parcial da fase 9.
        """
        raise NotImplementedError

    def tentativa_sem_prova(self, run_id, source_id, storage_object_id,
                            sha256) -> dict:
        """A MESMA pergunta, para quem não tem identidade documental: a linha
        com esta chave de tentativa, ou `None`.

        Determinística pelo índice da fase 10. Antes dela, é o endereço único
        que garante o mesmo resultado — em nenhum momento há zero travas.
        """
        raise NotImplementedError

    def observacoes_em(self, storage_path: str) -> list:
        """TODAS as observações naquele endereço. Uma LISTA, sempre.

        Existe para responder «este endereço já está ocupado?», e devolve
        lista precisamente para que ninguém volte a chamar-lhe uma linha.
        """
        raise NotImplementedError

    def objetos_da_corrida(self, run_id: str) -> list:
        """Todas as linhas de `raw_asset` daquela corrida. É esta leitura que
        produz `LINHAS_OBSERVADAS` — nunca uma contagem esperada.

        E é dela que sai também o `RAW_OBSERVATION_ID`. Por isso cada linha
        **tem de trazer `id`, como inteiro positivo**, em toda implementação
        desta porta. `bigserial` no banco e `"17"` no Python seriam o mesmo
        campo com dois tipos, e quem consome escolheria um e partiria no outro.
        """
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

    def caminho_local(self, caminho):
        """O caminho, pelo MESMO `_abs` que escreve — e so se o byte la esta.

        Passa pelo `_abs` de proposito: a travessia com `..` e recusada aqui
        pela mesma linha que a recusa no `enviar`. E confere que o ficheiro
        existe, porque devolver o caminho de um byte que nao aterrou seria
        entregar um endereco que nao responde.
        """
        alvo = self._abs(caminho)
        return alvo if os.path.isfile(alvo) else None


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


def _identifica(v) -> bool:
    """Um valor que IDENTIFICA — e não uma confissão preenchida.

    Três coisas diferentes, e nenhuma serve de identidade:

        None            o campo não veio
        "   "           veio vazio, com espaço a fingir conteúdo
        "NAO SEI"       veio uma confissão, e ela é honesta — mas é sobre a
                        ausência da resposta, não é a resposta

    O banco recusa as três (migration 026). Aqui recusa-se antes, para que a
    corrida saiba porque parou em vez de morrer com um erro de constraint.
    """
    if v is None:
        return False
    t = str(v).strip()
    return bool(t) and t.upper() not in SENTINELAS


def identidade_da_observacao(artefato: dict) -> dict:
    """Quem e o QUÊ a observação diz ser. LIDO do artefato, nunca deduzido.

    ⚠️ A FONTE E O DOCUMENTO NÃO FALHAM JUNTOS, e essa é a decisão inteira:

        sem SOURCE_ID real    → não há estado nenhum. A Collection SEMPRE soube
                                a que fonte pediu; não saber isso não é uma
                                identidade incompleta, é um pedido sem origem.
        com SOURCE_ID, sem
        DOCUMENT_ID provado   → FORWARD_IDENTITY_UNPROVEN. Os bytes ficam, a
                                chave não se inventa.
        com os dois           → FORWARD_IDENTIFIED, e `basis` diz de onde a
                                chave veio.

    O QUE NUNCA ACONTECE AQUI: cair para o `sha256`, para o `SOURCE_NATIVE_ID`,
    para a URL, para o `storage_path` ou para o nome do ficheiro. Bytes iguais
    não provam unidade documental igual — a ADAMA publicou o mesmo PDF sob
    `media/731` e `media/6321`, e uma chave derivada do conteúdo teria juntado
    duas publicações numa só.
    """
    fonte = artefato.get("SOURCE_ID")
    if not _identifica(fonte):
        return {"IDENTITY_STATE": None, "SOURCE_ID": None,
                "DOCUMENT_KEY": None, "DOCUMENT_KEY_BASIS": None}
    documento = artefato.get("DOCUMENT_ID")
    if _identifica(documento):
        return {"IDENTITY_STATE": FORWARD_IDENTIFIED,
                "SOURCE_ID": str(fonte).strip(),
                "DOCUMENT_KEY": str(documento).strip(),
                "DOCUMENT_KEY_BASIS": SOURCE_DOCUMENT_ID}
    return {"IDENTITY_STATE": FORWARD_IDENTITY_UNPROVEN,
            "SOURCE_ID": str(fonte).strip(),
            "DOCUMENT_KEY": None, "DOCUMENT_KEY_BASIS": None}


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
    # ⚠️ ESTE DICIONARIO ERA INDEXADO SO PELO CAMINHO, e isso colapsava
    # observacoes. Duas FONTES diferentes a observar o mesmo endereco davam
    # UMA entrada, e a segunda era contada como «relacao sem byte novo» —
    # a mesma doenca do `unique (raw_asset.storage_path)`, mas em Python, e
    # portanto invisivel a qualquer migration.
    #
    #     O OBJETO E UM POR ENDERECO. A OBSERVACAO NAO.
    #
    # A chave passa a ser a IDENTIDADE DA OBSERVACAO. Duas entradas colapsam
    # se e so se sao a MESMA observacao — que e o caso do `USED_BY`: dois
    # produtos que usam o mesmo documento da mesma fonte sao dois registos,
    # uma observacao e um objeto.
    por_observacao, caminhos, conteudos, relacoes = {}, set(), set(), 0
    for a in artefatos:
        caminho = caminho_do_objeto(a)
        identidade = identidade_da_observacao(a)
        chave = (caminho, identidade["SOURCE_ID"],
                 identidade["DOCUMENT_KEY"], identidade["IDENTITY_STATE"])
        conteudos.add(a["SHA256"])
        caminhos.add(caminho)
        if chave in por_observacao:
            relacoes += 1
            por_observacao[chave]["USADO_POR"].append(a.get("USED_BY"))
            continue
        por_observacao[chave] = dict(a, STORAGE_PATH=caminho,
                                     USADO_POR=[a.get("USED_BY")],
                                     **identidade)
    return {
        "REGISTOS_DE_ENTRADA": len(artefatos),
        "CONTEUDOS_UNICOS": len(conteudos),
        "OBJETOS_PLANEADOS": len(caminhos),
        # A QUARTA CONTAGEM, e ela faltava. Enquanto uma observacao por
        # endereco era a lei, `OBJETOS_PLANEADOS` respondia pelas duas
        # perguntas por acidente. Deixou de responder.
        "OBSERVACOES_PLANEADAS": len(por_observacao),
        "RELACOES_SEM_BYTE_NOVO": relacoes,
        "PORQUE_OS_TRES_NUMEROS_DIFEREM": (
            "REGISTO nao e CONTEUDO, nao e OBJETO e nao e OBSERVACAO. Dois "
            "produtos que usam o mesmo documento da mesma fonte sao DOIS "
            "registos, UM conteudo, UM objeto e UMA observacao. O mesmo "
            "conteudo publicado em DUAS URLs e UM conteudo e DOIS objetos. "
            "DUAS FONTES a observar o mesmo endereco sao UM objeto e DUAS "
            "observacoes. Nenhuma destas contagens deriva das outras."),
        "OBJETOS": list(por_observacao.values()),
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
    novos, reaproveitados, falhados, vistos = [], [], [], set()
    for obj in plano["OBJETOS"]:
        caminho = obj["STORAGE_PATH"]
        # DUAS OBSERVACOES NO MESMO ENDERECO SAO UM BYTE SO. Subir o mesmo
        # ficheiro duas vezes seria uma oportunidade a mais de escrever por
        # cima do que ja estava certo — que e precisamente o que esta funcao
        # existe para nao fazer.
        if caminho in vistos:
            continue
        vistos.add(caminho)
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
    conferidos, divergentes, ausentes, vistos = [], [], [], set()
    for obj in plano["OBJETOS"]:
        caminho = obj["STORAGE_PATH"]
        if caminho in vistos:      # o byte e um so; conferi-lo duas vezes
            continue               # daria a mesma resposta e contaria duas
        vistos.add(caminho)
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
            "source_url": obj.get("SOURCE_URL"),
            "identity_state": obj.get("IDENTITY_STATE"),
            "source_id": obj.get("SOURCE_ID"),
            "document_key": obj.get("DOCUMENT_KEY"),
            "document_key_basis": obj.get("DOCUMENT_KEY_BASIS")}


def _procurar_a_observacao(run_id, obj, copia, memoria):
    """A observação desta corrida, procurada pela CHAVE que ela tem.

    Duas chaves, porque há dois estados forward — e nenhuma delas é o endereço.
    A linha que volta daqui é sempre a MESMA linha para a mesma pergunta.
    """
    if obj.get("IDENTITY_STATE") == FORWARD_IDENTIFIED:
        return memoria.observacao_identificada(
            run_id, obj.get("SOURCE_ID"), obj.get("DOCUMENT_KEY"),
            obj["SHA256"])
    return memoria.tentativa_sem_prova(
        run_id, obj.get("SOURCE_ID"),
        (copia or {}).get("id"), obj["SHA256"])


def conferir_o_que_ja_existe(run: dict, plano: dict, memoria: Memoria) -> dict:
    """Lê o banco ANTES de escrever, e decide reencontro ou conflito.

    ⚠️ ESTA FUNÇÃO FAZIA UMA PERGUNTA SÓ, E ELA ERA DUAS.

        antes   existente = memoria.objeto_em(STORAGE_PATH)
                e daí saía tudo: a cópia, a observação e o conflito

    Uma chamada por endereço, a `raw_asset`, a devolver a primeira linha. Com
    o endereço único isso funcionava por acidente. Agora são três perguntas
    separadas, e cada uma vai à espécie que sabe responder:

        A CÓPIA        `storage_object` por endereço   — o endereço é dela
        A OBSERVAÇÃO   `raw_asset` pela chave de identidade
        A OCUPAÇÃO     quantas observações há naquele endereço

    E os dois conflitos deixam de se confundir:

        METADATA_CONFLICT        outros bytes no mesmo endereço. É sobre o
                                 MUNDO, e continua a ser conflito depois da
                                 fase 10.
        NEW_RUN_SAME_STORAGE_PATH  a observação é nova e a chave sabe disso;
                                 o que a impede é a trava FÍSICA antiga.
                                 Some sozinho quando a fase 10 entrar.
    """
    reusados, conflitos, notas = [], [], []
    for obj in plano["OBJETOS"]:
        caminho = obj["STORAGE_PATH"]

        # ── 1 · A CÓPIA. Outros bytes no mesmo endereço são duas verdades num
        # sítio só, e isso é conflito em qualquer fase.
        copia = memoria.copia_em(caminho)
        if copia and str(copia.get("sha256")) != str(obj["SHA256"]):
            conflitos.append({
                "TIPO": METADATA_CONFLICT, "STORAGE_PATH": caminho,
                "DIVERGENCIAS": [{"CAMPO": "sha256",
                                  "NO_BANCO": copia.get("sha256"),
                                  "NESTA_CORRIDA": obj["SHA256"]}],
                "PORQUE": ("o armazem ja tem OUTRO conteudo neste endereco. "
                           "Duas verdades no mesmo sitio."),
            })
            continue

        # ── 2 · A OBSERVAÇÃO, pela chave dela. Encontrada e igual: é retry.
        existente = _procurar_a_observacao(run["RUN_ID"], obj, copia, memoria)
        if existente:
            esperada = _linha_esperada(run["RUN_ID"], obj)
            # ⚠️ `storage_object_id` FICA DE FORA DA COMPARACAO, e nao por
            # descuido: ele foi a CHAVE DA BUSCA e veio do proprio banco. O
            # plano nunca o teve — o `id` da copia so existe depois de ela ser
            # escrita — e compara-lo daria sempre `None != 7`, transformando
            # todo reencontro num conflito inventado.
            #
            #     COMPARAR CONTRA O QUE NUNCA SE SOUBE E FABRICAR DIVERGENCIA.
            campos = (IDENTIDADE_FORWARD
                      if obj.get("IDENTITY_STATE") == FORWARD_IDENTIFIED
                      else tuple(c for c in IDENTIDADE_SEM_PROVA
                                 if c != "storage_object_id"))
            fora = _difere(existente, esperada, campos)
            if not fora:
                reusados.append(caminho)
                continue
            # Chegar aqui significa que a chave achou a linha e os campos DA
            # PRÓPRIA CHAVE divergem — o que só é possível se a implementação
            # da porta mentir. Vale mais rebentar com nome do que passar.
            conflitos.append({"TIPO": METADATA_CONFLICT,
                              "STORAGE_PATH": caminho, "DIVERGENCIAS": fora,
                              "PORQUE": ("a chave encontrou a linha e a chave "
                                         "diverge. A porta do banco mentiu.")})
            continue

        # ── 3 · A OCUPAÇÃO. A observação é NOVA, e o endereço já tem outra.
        #
        # ⚠️ ISTO ERA UM CONFLITO, E BLOQUEAVA A ESCRITA. E era o último nó do
        # runtime: com a fase 10 instalada, esta observação PODE entrar — e o
        # escritor recusava-a na mesma, porque a decisão estava em Python e não
        # no banco. O código levava a trava física dentro de si.
        #
        #     UMA TRAVA DO ESQUEMA NAO SE REESCREVE EM PYTHON.
        #     QUEM SABE SE A LINHA CABE E O BANCO.
        #
        # Agora é uma NOTA, e a escrita é tentada. Antes da fase 10 o banco
        # recusa-a, `MEMORIA.ERRO` guarda o motivo dele e a corrida fecha
        # `PARTIAL` — honesto. Depois da fase 10 ela entra, e o mesmo código
        # não muda uma linha. É isso que torna o escritor pronto.
        ocupantes = memoria.observacoes_em(caminho)
        if ocupantes:
            notas.append({
                "TIPO": NEW_RUN_SAME_STORAGE_PATH, "STORAGE_PATH": caminho,
                "OCUPANTES": len(ocupantes),
                "CORRIDAS_QUE_JA_LA_ESTAO": sorted(
                    {str(o.get("run_id")) for o in ocupantes}),
                "PORQUE": ("observacao NOVA sobre um endereco ja ocupado. A "
                           "chave de identidade sabe que ela e nova, e nada "
                           "nesta casa a impede. O que a pode impedir e "
                           "`unique (raw_asset.storage_path)` — uma trava do "
                           "ESQUEMA, que responde no banco e nao aqui."),
            })

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
        # NOTA NAO E CONFLITO. Uma nota diz «o banco vai ter uma palavra a
        # dizer sobre isto»; um conflito diz «nao escrevas». Confundi-las fez
        # o escritor recusar, por sua conta, o caso que a fase 10 abre.
        "OBSERVACOES_NOVAS_EM_ENDERECO_OCUPADO": notas,
        "CONFLITO_DE_CORRIDA": conflito_de_corrida,
        "PERGUNTAS_SEPARADAS": ["copia_em", "observacao_identificada",
                                "tentativa_sem_prova", "observacoes_em"],
        "O_QUE_ISTO_IMPEDE": (
            "que `on conflict do nothing` engula uma divergencia, e que a "
            "pergunta «que copia ha aqui?» seja respondida por uma tabela de "
            "observacoes. SQL aceite nao e linha gravada, e endereco nao e "
            "identidade de observacao."),
    }


# ─────────────────────────────────────────────────────────────────────────
# 4 · A MEMÓRIA — SQL auditável, nunca ligação direta
# ─────────────────────────────────────────────────────────────────────────
def _texto(v):
    if v is None:
        return "null"
    return "'" + str(v).replace("'", "''") + "'"


def _onde_a_observacao_esta(run, o, caminho, prefixo="", objeto=None):
    """A cláusula `where` que nomeia UMA observação — a desta corrida.

    Escrita uma vez e usada nas duas ordens (`update` e `insert ... where not
    exists`). Duas cópias da mesma chave divergiriam, e no dia em que
    divergissem o `update` contaria a tentativa de uma linha e o `insert`
    criaria outra.

        A CHAVE DA IDEMPOTENCIA E UMA. ESCREVE-SE NUM SITIO SO.

    `objeto` é como se nomeia a cópia no contexto de quem chama: dentro do
    `insert` ela é `o.id`, a coluna do `select`; fora dele é uma subconsulta
    pelo endereço, que é a identidade do OBJETO.
    """
    p = prefixo
    copia = objeto or ("(select id from public.storage_object where "
                       "storage_path = %s)" % _texto(caminho))
    comum = "%srun_id = %s and %ssource_id = %s and %ssha256 = %s" % (
        p, _texto(run["RUN_ID"]), p, _texto(o.get("SOURCE_ID")),
        p, _texto(o["SHA256"]))
    if o.get("IDENTITY_STATE") == FORWARD_IDENTIFIED:
        return ("%sidentity_state = %s and %s and %sdocument_key = %s" % (
            p, _texto(FORWARD_IDENTIFIED), comum, p,
            _texto(o.get("DOCUMENT_KEY"))))
    # SEM PROVA: a cópia entra na chave, e o documento não — porque não há.
    return ("%sidentity_state = %s and %s and %sstorage_object_id = %s" % (
        p, _texto(FORWARD_IDENTITY_UNPROVEN), comum, p, copia))


def sql_da_memoria(run: dict, conferidos: list, plano: dict) -> str:
    """A corrida abre `rodando`, e os objetos conferidos entram.

    DESDE A MIGRATION 025 SAO DUAS ESPECIES, e cada linha conferida produz
    duas escritas: a COPIA em `storage_object`, endereçada pelo caminho, e a
    OBSERVACAO em `raw_asset`, que aponta para ela. O `id` da copia nunca e
    calculado aqui — e lido do banco, por endereço, dentro do proprio insert.

    DUAS TRAVAS, E NENHUMA É DECORATIVA:

    1. **Só entra o que foi CONFERIDO** — lido de volta do armazém e com o hash
       batido. Uma linha para um byte que não voltou seria a mentira italiana
       ao contrário: memória sem byte.
    2. **`on conflict (storage_path) do nothing`** torna o retry seguro. Mas
       sozinho ele calaria conflito — por isso `conferir_o_que_ja_existe()`
       corre **antes**, e o conflito é apanhado lá.
    """
    # ⚠️ ISTO ERA `{o["STORAGE_PATH"]: o}`, e perdia observacoes: duas no
    # mesmo endereco, e so a ultima chegava ao SQL. O mapa e agora de caminho
    # para a LISTA das observacoes daquele endereco.
    por_caminho = {}
    for o in plano["OBJETOS"]:
        por_caminho.setdefault(o["STORAGE_PATH"], []).append(o)
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
        for o in por_caminho[caminho]:
            # ── A COPIA PRIMEIRO, A OBSERVACAO DEPOIS ───────────────────────────
            # Sao duas especies desde a migration 025, e a ordem nao e arbitraria:
            # a observacao aponta para a copia, logo a copia tem de existir antes.
            #
            #     GARANTIR A COPIA  ->  GARANTIR A OBSERVACAO  ->  LIGAR
            #
            # `do nothing` no objeto e o que torna a segunda corrida do mesmo
            # endereco barata: a copia ja la esta, e reusa-se. Isto NAO cura o
            # conflito da observacao — `unique (raw_asset.storage_path)` continua
            # de pe, e cai so na fase 10 do plano.
            linhas.append(
                "insert into public.storage_object (storage_path, media_type, "
                "bytes, sha256) values (%s, %s, %d, %s) "
                "on conflict (storage_path) do nothing;" % (
                    _texto(caminho), _texto(o["MEDIA_TYPE"]),
                    o["BYTES"], _texto(o["SHA256"])))
            # E A LIGACAO SAI DO BANCO, NAO DA NOSSA CABECA. O `id` da copia e lido
            # de la por endereco — nunca por `sha256`, que dois objetos podem
            # partilhar, e nunca por um numero que este processo tenha guardado.
            # ── E A OBSERVACAO DIZ QUEM E O QUE ELA E (026) ─────────────────
            # O `on conflict` MUDOU, e a mudanca e a metade que interessa:
            #
            #     ANTES  on conflict (storage_path) do nothing
            #     AGORA  on conflict (run_id, source_id, document_key, sha256)
            #            where identity_state = 'FORWARD_IDENTIFIED' do nothing
            #
            # O alvo antigo engolia QUALQUER colisao de endereco — inclusive a de
            # uma corrida NOVA, que nao e retry nenhum. O novo alvo e o indice
            # parcial da fase 9: ele absorve o retry da mesma observacao e mais
            # nada. Uma colisao de `storage_path` deixa de ser calada e REBENTA,
            # que e o comportamento certo enquanto a fase 10 nao existir.
            #
            #     `DO NOTHING` NAO PODE SER O SITIO ONDE A FASE 10 SE ESCONDE.
            #
            # Uma linha que nao satisfaz o predicado (UNPROVEN) nao pode colidir
            # neste indice — logo, para ela, nao ha `do nothing` nenhum.
            # ── A TENTATIVA CONTA-SE ANTES DE A OBSERVACAO NASCER ───────────
            # `attempts` e `last_attempt_at` nasceram na 026 e ficaram SEM DONO.
            # O dono e este: o escritor canonico, e ninguem mais.
            #
            # O `update` vem PRIMEIRO de proposito. Se a observacao ja existe, ele
            # incrementa; se nao existe, afecta zero linhas e o `insert` a seguir
            # poe `attempts = 1`. Duas ordens, uma semantica, e nenhuma condicao em
            # Python a decidir qual correr.
            #
            #     LER-SOMAR-ESCREVER EM PYTHON PERDERIA INCREMENTOS.
            #
            # `attempts = attempts + 1` acontece DENTRO do banco, debaixo do lock
            # da linha. Dois retries simultaneos serializam e os dois contam.
            linhas.append(
                "update public.raw_asset set attempts = coalesce(attempts, 0) + 1,"
                " last_attempt_at = %s where %s;" % (
                    _texto(o["CAPTURED_AT"]), _onde_a_observacao_esta(run, o, caminho)))
            # ── E A OBSERVACAO ENTRA SE E SO SE AINDA NAO ESTIVER LA ────────
            # ⚠️ O `on conflict` DA FASE 9 NAO SERVIA PARA METADE DAS LINHAS: o
            # indice tem predicado `FORWARD_IDENTIFIED`, e uma linha SEM PROVA nao
            # o satisfaz — para ela nao havia `do nothing` nenhum, e o retry
            # entrava outra vez.
            #
            # `where not exists` cobre os DOIS estados com a MESMA forma, e — o que
            # decide — funciona ANTES e DEPOIS da fase 10. Ele nao inventa trava
            # nenhuma: quem arbitra a corrida entre duas sessoes continua a ser um
            # indice do banco, e ha sempre um.
            #
            #     HOJE      unique (raw_asset.storage_path)
            #     FASE 10   raw_identidade_forward_idx + raw_tentativa_sem_prova_idx
            #
            # Em nenhum momento ha zero travas, e e por isso que o escritor pode
            # mudar antes da migration.
            linhas.append(
                "insert into public.raw_asset (run_id, storage_path, media_type, "
                "bytes, sha256, captured_at, source_url, storage_object_id, "
                "identity_state, source_id, document_key, document_key_basis, "
                "attempts, last_attempt_at) "
                "select %s, %s, %s, %d, %s, %s, %s, o.id, %s, %s, %s, %s, 1, %s "
                "from public.storage_object o where o.storage_path = %s "
                "and not exists (select 1 from public.raw_asset r where %s);" % (
                    _texto(run["RUN_ID"]), _texto(caminho), _texto(o["MEDIA_TYPE"]),
                    o["BYTES"], _texto(o["SHA256"]), _texto(o["CAPTURED_AT"]),
                    _texto(o.get("SOURCE_URL")),
                    _texto(o.get("IDENTITY_STATE")), _texto(o.get("SOURCE_ID")),
                    _texto(o.get("DOCUMENT_KEY")), _texto(o.get("DOCUMENT_KEY_BASIS")),
                    _texto(o["CAPTURED_AT"]), _texto(caminho),
                    _onde_a_observacao_esta(run, o, caminho, prefixo="r.",
                                            objeto="o.id")))
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
        # ⚠️ AQUI TAMBÉM SE LIA POR ENDEREÇO, e pelo mesmo motivo deixou de se
        # ler: a linha que se quer conferir é a linha QUE ESTA CORRIDA
        # ESCREVEU, e quem a nomeia é a chave de identidade dela. Ler por
        # endereço depois da fase 10 poderia conferir a observação de OUTRA
        # corrida e dar-lhe o nosso nome.
        copia = memoria.copia_em(caminho)
        # ── A CÓPIA É CONFERIDA PRIMEIRO, E SOZINHA ─────────────────────
        # ⚠️ SEM ISTO O DIAGNÓSTICO PERDIA-SE. O caso de corrida é: outro
        # escritor chega ao endereço no meio, e a cópia que lá fica é A DELE.
        # A nossa observação nem sequer entra — a chave estrangeira composta
        # recusa-a, porque o `sha256` dela não é o da cópia. Procurá-la e não
        # a encontrar diria «falta escrever», e mandaria o operador repetir o
        # passo errado.
        #
        #     BYTES DIFERENTES NO NOSSO ENDERECO NAO E «FALTA ESCREVER».
        #     E DUAS VERDADES NO MESMO SITIO, e tem esse nome.
        if copia and str(copia.get("sha256")) != str(obj["SHA256"]):
            divergentes.append({
                "TIPO": METADATA_CONFLICT, "STORAGE_PATH": caminho,
                "DIVERGENCIAS": [
                    {"CAMPO": c, "NO_BANCO": copia.get(c),
                     "NESTA_CORRIDA": obj[k]}
                    for c, k in (("sha256", "SHA256"), ("bytes", "BYTES"))
                    if str(copia.get(c)) != str(obj[k])],
                "PORQUE": ("a copia neste endereco tem outro conteudo. A "
                           "observacao desta corrida nao pode apontar-lhe: a "
                           "chave estrangeira composta liga `(objeto, sha256)` "
                           "e recusa-a — e recusou."),
            })
            continue
        escrita = _procurar_a_observacao(run["RUN_ID"], obj, copia, memoria)
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
        # A LISTA, E NAO SO A CONTA. Ela ja era calculada aqui e deitada fora
        # ao virar numero. Quem devolve a identidade de uma observacao precisa
        # de saber QUAIS linhas foram confirmadas, e nao quantas — contar de
        # novo noutro sitio seria uma segunda autoridade sobre a mesma medida.
        "CONFERIDOS": conferidos,
        "DIVERGENTES": divergentes,
        "AUSENTES": ausentes,
        "CAMPOS_COMPARADOS": list(CAMPOS_DA_LINHA),
        "O_QUE_ISTO_IMPEDE": (
            "que a contagem certa esconda o conteudo errado. Entre a leitura "
            "previa e o nosso insert outro escritor pode meter uma linha "
            "divergente no mesmo caminho; o `do nothing` cala-se e a conta "
            "fecha na mesma. Contar nao e conferir."),
    }


def observacoes_confirmadas(run: dict, linhas: list, pos_escrita: dict) -> list:
    """As observacoes desta corrida que o banco confirmou, com o id REAL.

    O `RAW_OBSERVATION_ID` e o surrogate da OBSERVACAO, fechado na C-PLAN-0, e
    o unico sitio de onde ele pode vir e uma linha que o banco devolveu.

        NAO E O sha256      esse e a identidade dos BYTES
        NAO E o storage_path esse e um ENDERECO, e endereco muda
        NAO E o DOCUMENT_ID  esse e a identidade do DOCUMENTO
        NAO E o ARTIFACT_ID  esse e do contrato comum, e nasce do sha

    E nao e calculado de nenhum deles. Um id derivado de qualquer coisa que a
    casa ja tinha em maos seria um id que a casa podia ter escrito sozinha — e
    entao ele nao provaria que a linha existe, que e a unica coisa que ele
    serve para provar.

    ⚠️ DUAS TRAVAS, E A SEGUNDA NASCEU DE UM DEFEITO MEDIDO NO B3.

    O mesmo conteudo, na corrida seguinte, cai no MESMO `storage_path` — o
    endereco e do conteudo e nao da vez em que o vimos. Quem perguntasse
    «que linha vive neste caminho?» receberia a linha da corrida ANTERIOR, com
    o id dela, e daria a observacao de hoje o nome da observacao de ontem.

        UM ID EMPRESTADO DE OUTRA CORRIDA NAO E UM ID ERRADO.
        E UMA OBSERVACAO A FAZER-SE PASSAR POR OUTRA.

    Por isso so entra aqui a linha que cumpre as duas:

        1. o `run_id` dela e o DESTA corrida
        2. o caminho dela passou na conferencia campo a campo depois de escrever

    Sem linha, sem id. Nao se devolve `null`, `UNKNOWN`, `NAO SEI` nem o
    caminho no lugar do id: **ausencia e ausencia**, e ela diz exactamente o
    que aconteceu — esta observacao ainda nao existe no banco.
    """
    confirmados = set(pos_escrita.get("CONFERIDOS") or []) if pos_escrita else set()
    fora = []
    for linha in linhas or []:
        if linha.get("run_id") != run["RUN_ID"]:
            continue
        if linha.get("storage_path") not in confirmados:
            continue
        ident = linha.get("id")
        if not isinstance(ident, int) or isinstance(ident, bool) or ident <= 0:
            # O CONTRATO DA PORTA E QUE ISTO SEJA UM INTEIRO POSITIVO. Uma
            # porta que devolve `"17"` e outra que devolve `17` sao dois
            # contratos com o mesmo nome, e quem os consome escolhe um e parte
            # no outro. Calar aqui esconderia a divergencia dentro de um campo
            # que parece preenchido.
            raise ValueError(
                "porta de memoria fora do contrato: raw_asset.id veio como %r "
                "(%s) para %s. `objetos_da_corrida()` tem de devolver `id` "
                "como inteiro positivo em TODAS as implementacoes."
                % (ident, type(ident).__name__, linha.get("storage_path")))
        fora.append({
            # A IDENTIDADE DA OBSERVACAO.
            "RAW_OBSERVATION_ID": ident,
            # A CORRIDA QUE A PRODUZIU. Nao e a identidade dela; e a
            # proveniencia, e e o que separa duas observacoes do mesmo byte.
            "RUN_ID": linha["run_id"],
            # O LOCATOR. Onde o byte esta, e nao quem a observacao e.
            "STORAGE_PATH": linha["storage_path"],
            # A IDENTIDADE DOS BYTES. Outra especie, outra pergunta.
            "SHA256": linha.get("sha256"),
        })
    return fora


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

    # ── B5B · SEM FONTE NAO HA OBSERVACAO FORWARD ───────────────────────
    # Desde a 026 `identity_state` e NOT NULL e SEM DEFAULT, e os dois estados
    # forward exigem uma fonte REAL. Um artefato que nao a traga nao tem estado
    # possivel:
    #
    #     LEGACY_PRE_IDEMPOTENCY   nao — legado e quem ja la estava no corte,
    #                              e o corte pelo surrogate recusaria a linha
    #     FORWARD_*                nao — os dois exigem fonte real
    #
    # Entao ele nao entra, e a corrida NAO fecha. Recusar aqui da o nome antes
    # de o banco dar um erro de constraint; inventar-lhe um SOURCE_ID daria
    # uma fonte que a casa nunca registou.
    recusados = [a for a in artefatos
                 if not _identifica(a.get("SOURCE_ID"))]
    artefatos = [a for a in artefatos if _identifica(a.get("SOURCE_ID"))]

    plano = planear(artefatos)
    envio = enviar_os_bytes(plano, armazem, bytes_de)
    prova = conferir_os_bytes(plano, armazem)

    sql = sql_da_memoria(run, prova["CONFERIDOS"], plano)
    ja_la = {"REUSED_METADATA": [], "CONFLITOS_DE_OBJETO": [],
             "OBSERVACOES_NOVAS_EM_ENDERECO_OCUPADO": [],
             "CONFLITO_DE_CORRIDA": None}
    memoria_estado = {"TENTADA": False, "APLICADA": False, "ERRO": None,
                      # ⚠️ ERA `len(prova["CONFERIDOS"])`, e isso conta
                      # BYTES conferidos — um por endereco. O que se espera do
                      # banco sao OBSERVACOES, e duas podem partilhar endereco.
                      "LINHAS_ESPERADAS": len(
                          [o for o in plano["OBJETOS"]
                           if o["STORAGE_PATH"] in set(prova["CONFERIDOS"])]),
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

    # ── A IDENTIDADE VOLTA DA MESMA LEITURA QUE JA SUSTENTA A RECONCILIACAO ──
    # `linhas` acima veio de um SELECT por `run_id`. Abrir uma segunda consulta
    # so para buscar ids daria duas autoridades sobre a mesma medida, e no dia
    # em que discordassem nao haveria como saber qual valia.
    #
    #     UMA LEITURA -> reconciliacao E identidade.
    #
    # Sem banco ligado nao ha linha, e sem linha nao ha id. `preservar()`
    # continua a guardar os bytes; o que ele NAO faz e cunhar um surrogate
    # local para tapar o buraco.
    raw_observations = (observacoes_confirmadas(run, linhas, pos_escrita)
                        if memoria is not None else [])

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
        "toda_observacao_tem_fonte": not recusados,
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
    if recusados:
        # Vem PRIMEIRO na fila: uma observacao sem fonte nao chega a ter
        # conflito de metadata, e diagnosticar-lhe outra coisa mandaria o
        # operador repetir o passo errado.
        pendencia = SEM_IDENTIDADE_DE_FONTE
    elif ja_la["CONFLITO_DE_CORRIDA"]:
        pendencia = RUN_ID_CONFLICT
    elif ja_la["CONFLITOS_DE_OBJETO"]:
        # Chegar aqui e «duas verdades no mesmo endereco»: outros bytes na
        # copia. E conflito em qualquer fase, e nao se resolve por antiguidade.
        pendencia = METADATA_CONFLICT
    # Divergencia encontrada DEPOIS de escrever tambem e conflito, e tem de vir
    # antes de UPLOAD_PENDING_METADATA na fila. Senao o caso de corrida —
    # contagem certa, conteudo errado — sairia rotulado como «falta escrever»,
    # que e o diagnostico errado e manda o operador repetir o passo errado.
    elif pos_escrita and pos_escrita["DIVERGENTES"]:
        pendencia = METADATA_CONFLICT
    # ── E O NOME DA TRAVA FISICA, QUANDO E ELA QUE MORDE ─────────────────
    # A observacao nova sobre endereco ocupado deixou de ser CONFLITO — ela e
    # legitima, e a escrita e tentada. Mas se o banco a recusou, o operador
    # tem de saber QUE trava o fez, e nao ouvir «falta escrever».
    #
    #     UPLOAD_PENDING_METADATA mandaria repetir. Repetir nao cura uma
    #     trava de esquema: ela cai na fase 10, ou nao cai.
    #
    # E a condicao e `nao aplicada`, e nao `houve nota`: com a fase 10
    # instalada a nota continua a existir — ela e informacao verdadeira sobre
    # o acervo — e a escrita PASSA. Nesse dia esta linha cala-se sozinha.
    elif (ja_la.get("OBSERVACOES_NOVAS_EM_ENDERECO_OCUPADO")
          and not condicoes["memoria_aplicada"]):
        pendencia = NEW_RUN_SAME_STORAGE_PATH
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
        "RECUSADOS_SEM_IDENTIDADE": [
            {"SHA256": a.get("SHA256"), "NAME": a.get("NAME"),
             "SOURCE_ID_RECEBIDO": a.get("SOURCE_ID"),
             "PORQUE": ("sem SOURCE_ID real nao ha estado de identidade "
                        "possivel, e nenhum se inventa")}
            for a in recusados],
        "PLANO": {k: v for k, v in plano.items() if k != "OBJETOS"},
        "ENVIO": {"NOVOS": len(envio["NOVOS"]),
                  "REAPROVEITADOS": len(envio["REAPROVEITADOS"]),
                  "FALHADOS": envio["FALHADOS"]},
        "PROVA_DOS_BYTES": {k: len(v) if k == "CONFERIDOS" else v
                            for k, v in prova.items()},
        "JA_EXISTIA_NO_BANCO": {
            "REUSED_METADATA": len(ja_la["REUSED_METADATA"]),
            "CONFLITOS_DE_OBJETO": ja_la["CONFLITOS_DE_OBJETO"],
            "OBSERVACOES_NOVAS_EM_ENDERECO_OCUPADO":
                ja_la.get("OBSERVACOES_NOVAS_EM_ENDERECO_OCUPADO", []),
            "CONFLITO_DE_CORRIDA": ja_la["CONFLITO_DE_CORRIDA"],
        },
        "MEMORIA": memoria_estado,
        "CONFERENCIA_POS_ESCRITA": pos_escrita,
        "RAW_OBSERVATIONS": raw_observations,
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
