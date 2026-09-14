#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PORTAS LIGADAS À PRODUÇÃO — adaptadores, não donos.

O QUE ISTO É
------------
Os donos da escrita (`preservar_coleta.py`, `preservar_derivado.py`) nunca
falaram com banco nem com armazém: falam com duas **portas**, `Armazem` e
`Memoria`. Até hoje só existiam implementações descartáveis — um dicionário e
um SQLite. Este ficheiro é a primeira implementação **real**.

    ISTO NÃO É UM DONO. É UMA PORTA.

Não decide nada, não tem regra de negócio, não sabe o que é uma derivação.
Traduz chamadas para HTTP e para `psql`, e mais nada. Toda a lei continua nos
donos — que é o que permite prová-los sem tocar em produção.

POR QUE MORA EM `guarda/`
-------------------------
Na gaveta do dono, ao lado das portas que implementa. Pô-lo no executor faria
o executor conhecer o banco, e a doutrina desta casa é a oposta: o executor
produz o artefato, o dono persiste.

CREDENCIAIS
-----------
Vêm do ambiente e **nunca são impressas**. Um erro do `psql` pode trazer a URL
dentro da mensagem, e por isso ela é limpa antes de sair.
"""
import json
import os
import re
import subprocess
import urllib.error
import urllib.request

from guarda.preservar_coleta import Armazem
from guarda.preservar_derivado import MemoriaDoDerivado

SEGREDO = re.compile(r"postgres(ql)?://[^\s]*")


def _sem_segredo(texto: str) -> str:
    return SEGREDO.sub("<URL_OMITIDA>", texto or "")


class ArmazemSupabase(Armazem):
    """O bucket `raw`, por HTTP. Três perguntas, e nenhuma delas é «apague».

    A porta não tem `remover` — e esta implementação também não o inventa. Se a
    memória falhar depois do envio, apagar o byte para fingir atomicidade
    destruiria a única evidência que sobrou.
    """

    def __init__(self, url=None, chave=None, bucket="raw"):
        self.base = (url or os.environ["SUPABASE_URL"]).rstrip("/")
        self.chave = chave or os.environ["SUPABASE_SECRET_KEY"]
        self.bucket = bucket

    def _pedir(self, metodo, caminho, dados=None, tipo=None):
        req = urllib.request.Request(
            "%s/storage/v1/object/%s/%s" % (self.base, self.bucket, caminho),
            data=dados, method=metodo)
        req.add_header("Authorization", "Bearer %s" % self.chave)
        req.add_header("apikey", self.chave)
        if tipo:
            req.add_header("Content-Type", tipo)
        return urllib.request.urlopen(req, timeout=120)

    def existe(self, caminho):
        try:
            self._pedir("GET", caminho).read(1)
            return True
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                return False
            raise

    def enviar(self, caminho, dados, media_type):
        self._pedir("POST", caminho, dados, media_type).read()

    def ler(self, caminho):
        return self._pedir("GET", caminho).read()


def _lit(v):
    """Um valor como literal SQL. `None` vira `null`, e nunca a palavra 'None'.

    ⚠️ ISTO NAO E DECORACAO. As chaves de identidade tem campos que PODEM ser
    nulos — `document_key` na tentativa sem prova, `storage_object_id` numa
    linha nao preservada. Interpolar `None` faria a consulta procurar a
    STRING 'None', encontrar nada, e o escritor concluir que a observacao nao
    existe. Um retry entraria outra vez, e a duplicata teria vindo de uma
    conversao de tipo.
    """
    if v is None:
        return "null"
    return "'" + str(v).replace("'", "''") + "'"


class MemoriaSupabase(MemoriaDoDerivado):
    """O Postgres de produção, falado por `psql`.

    Sem driver instalado: `psql` já existe no runner, e instalar um pacote
    global só para isto continua proibido nesta casa.
    """

    SEP = "\x1f"

    def __init__(self, url=None):
        self.url = url or os.environ["SUPABASE_DB_URL"]
        self.aplicacoes = 0

    def _psql(self, sql):
        r = subprocess.run(
            ["psql", "-X", "-q", "-A", "-t", "-F", self.SEP,
             "-v", "ON_ERROR_STOP=1", "-c", sql, self.url],
            capture_output=True, text=True)
        if r.returncode != 0:
            raise IOError(_sem_segredo(r.stderr.strip())[:400])
        return r.stdout

    def _valor(self, sql):
        linhas = [x for x in self._psql(sql).splitlines() if x.strip()]
        if len(linhas) != 1:
            raise IOError("esperava UM valor e vieram %d" % len(linhas))
        return linhas[0]

    # O `psql` devolve TUDO como texto, e `raw_asset.id` e `bigserial`. Sem
    # esta conversao a porta descartavel devolveria `17` e esta devolveria
    # `"17"` — o mesmo campo com dois tipos e o mesmo nome. Quem consome
    # escolhe um dos dois e parte no outro, e o erro aparece longe daqui.
    #
    #     DUAS PORTAS DA MESMA COISA TEM DE FALAR A MESMA LINGUA,
    #     SENAO NAO SAO DUAS PORTAS: SAO DOIS CONTRATOS.
    #
    # So o `id` entra: converter tudo o que parece numero transformaria um
    # `sha256` de digitos ou um identificador nativo em inteiro, e um
    # identificador que muda de tipo conforme o conteudo nao e identificador.
    INTEIROS = ("id",)

    def _linhas(self, sql, colunas):
        fora = []
        for linha in self._psql(sql).splitlines():
            if not linha.strip():
                continue
            v = linha.split(self.SEP)
            d = {c: (x if x != "" else None) for c, x in zip(colunas, v)}
            for c in self.INTEIROS:
                if d.get(c) is not None:
                    d[c] = int(d[c])
            fora.append(d)
        return fora

    def aplicar(self, sql):
        self.aplicacoes += 1
        r = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", self.url],
                           input=sql, capture_output=True, text=True)
        if r.returncode != 0:
            raise IOError(_sem_segredo(r.stderr.strip())[:400])

    # O TEMPO VOLTA NA MESMA FORMA EM QUE FOI ESCRITO. O Postgres imprime
    # `2026-09-08 00:00:00+00`; nos escrevemos `...T...Z`. Comparar as duas
    # formas daria um conflito FALSO — e conflito falso ensina toda a gente a
    # ignorar o alarme.
    _ISO = "to_char(%s at time zone 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')"
    TEMPOS = ("started_at", "finished_at", "captured_at", "derived_at")

    COLS_RUN = ("run_id", "actor", "actor_version", "source_country",
                "started_at", "rule_version", "capture_method", "status",
                "finished_at")
    # 026: a identidade da observacao entra na projecao. Sem ela, o writer
    # perguntaria «ja ha linha neste caminho?» e receberia a linha SEM saber se
    # ela e a mesma observacao — que e exactamente a pergunta que a chave de
    # idempotencia responde.
    COLS_OBJ = ("run_id", "storage_path", "media_type", "bytes", "sha256",
                "captured_at", "source_url",
                "identity_state", "source_id", "document_key",
                "document_key_basis")
    # ⚠️ `objetos_da_corrida()` LIA SEM O `id`, e por isso a identidade da
    # observacao nao tinha por onde voltar desta porta: a coluna existe na
    # tabela desde a migration 001, e era a PROJECAO que a deixava de fora.
    # `COLS_OBJ` sobrevive como projeccao base; quem lhe acrescenta `id` e
    # `storage_object_id` e `COLS_OBS`, porque quem encontra uma linha pela
    # chave precisa de poder dizer QUAL linha achou.
    # A COPIA tem as colunas DELA, e `id` esta la porque e ele que a chave da
    # tentativa sem prova usa. A OBSERVACAO traz `id` pela mesma razao: quem
    # encontra uma linha pela chave precisa de poder dizer QUAL linha achou.
    COLS_COPIA = ("id", "storage_path", "media_type", "bytes", "sha256")
    COLS_OBS = ("id", "storage_object_id", "attempts") + COLS_OBJ

    COLS_OBJ_DA_CORRIDA = ("id",) + COLS_OBJ
    COLS_RAW = ("id", "run_id", "storage_path", "media_type", "bytes",
                "sha256", "captured_at", "source_url",
                "identity_state", "source_id", "document_key",
                "document_key_basis")
    COLS_DER = ("id", "raw_asset_id", "parent_sha256", "kind", "producer",
                "producer_version", "pipeline_version", "parameters_hash",
                "serie_posicao", "sha256", "bytes", "media_type",
                "storage_path", "derived_at")

    def _select(self, colunas, prefixo=""):
        return ", ".join(self._ISO % (prefixo + c) if c in self.TEMPOS
                         else prefixo + c for c in colunas)

    def corrida(self, run_id):
        l = self._linhas("select %s from public.collection_run where run_id='%s'"
                         % (self._select(self.COLS_RUN), run_id), self.COLS_RUN)
        return l[0] if l else None

    # ── AS TRES PERGUNTAS, CADA UMA COM A SUA CHAVE ─────────────────────
    # `objeto_em(storage_path)` foi retirado: ele perguntava pela COPIA e
    # respondia com a primeira OBSERVACAO do endereco. Com o endereco unico
    # isso acertava por acidente; depois da fase 10 devolveria uma linha ao
    # acaso com cara de determinismo.
    def copia_em(self, storage_path):
        linhas = self._linhas(
            "select %s from public.storage_object where storage_path = '%s'"
            % (self._select(self.COLS_COPIA), storage_path.replace("'", "''")),
            self.COLS_COPIA)
        return linhas[0] if linhas else None

    def observacao_identificada(self, run_id, source_id, document_key, sha256):
        linhas = self._linhas(
            "select %s from public.raw_asset where identity_state = '%s'"
            " and run_id = %s and source_id = %s and document_key = %s"
            " and sha256 = %s"
            % (self._select(self.COLS_OBS), "FORWARD_IDENTIFIED",
               _lit(run_id), _lit(source_id), _lit(document_key),
               _lit(sha256)), self.COLS_OBS)
        return linhas[0] if linhas else None

    def tentativa_sem_prova(self, run_id, source_id, storage_object_id, sha256):
        # `is not distinct from`, e nao `=`: sem copia o id e nulo dos dois
        # lados, e `null = null` nao e verdade. A linha nao preservada ficaria
        # invisivel a propria chave que devia encontra-la.
        linhas = self._linhas(
            "select %s from public.raw_asset where identity_state = '%s'"
            " and run_id = %s and source_id = %s"
            " and storage_object_id is not distinct from %s and sha256 = %s"
            % (self._select(self.COLS_OBS), "FORWARD_IDENTITY_UNPROVEN",
               _lit(run_id), _lit(source_id), _lit(storage_object_id),
               _lit(sha256)), self.COLS_OBS)
        return linhas[0] if linhas else None

    def observacoes_em(self, storage_path):
        """TODAS. Devolve lista para que ninguem lhe chame uma linha."""
        return self._linhas(
            "select %s from public.raw_asset where storage_path = '%s'"
            " order by id"
            % (self._select(self.COLS_OBS), storage_path.replace("'", "''")),
            self.COLS_OBS)

    def objetos_da_corrida(self, run_id):
        return self._linhas(
            "select %s from public.raw_asset where run_id='%s' "
            "order by storage_path"
            % (self._select(self.COLS_OBJ_DA_CORRIDA), run_id),
            self.COLS_OBJ_DA_CORRIDA)

    def raw_por_id(self, raw_asset_id):
        # Todas as colunas do bruto com prefixo `a.`: sem isso o `run_id` fica
        # ambiguo no join, e o Postgres recusa — com razao.
        cols = self.COLS_RAW + ("source_country",)
        l = self._linhas(
            "select %s, r.source_country from public.raw_asset a "
            "join public.collection_run r on r.run_id = a.run_id "
            "where a.id = %d" % (self._select(self.COLS_RAW, "a."),
                                 int(raw_asset_id)), cols)
        return l[0] if l else None

    def derivado_com_identidade(self, identidade):
        # `is not distinct from`: em SQL, NULL = NULL e DESCONHECIDO, e sem isto
        # a linha de `serie_posicao` NULL nunca seria reencontrada.
        def _v(x):
            return "null" if x is None else "'%s'" % str(x).replace("'", "''")
        onde = " and ".join("%s is not distinct from %s" % (c, _v(identidade[c]))
                            for c in identidade)
        l = self._linhas("select %s from public.derived_artifact where %s"
                         % (self._select(self.COLS_DER), onde), self.COLS_DER)
        return l[0] if l else None

    def contar(self, tabela, onde="true"):
        return int(self._valor("select count(*) from public.%s where %s"
                               % (tabela, onde)))


def buscar(url: str) -> dict:
    """UM GET real, e o recibo dele.

    Nada de confiar no `sha256` histórico: o que conta é o que voltou HOJE, e
    é medido dos bytes que chegaram.
    """
    from datetime import datetime, timezone
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; SINTONIA/1.0)")
    quando = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with urllib.request.urlopen(req, timeout=120) as r:
        dados = r.read()
        return {"URL_PEDIDA": url, "URL_EFETIVA": r.geturl(),
                "HTTP_STATUS": r.status,
                "CONTENT_TYPE": r.headers.get("Content-Type"),
                "CONTENT_LENGTH_DECLARADO": r.headers.get("Content-Length"),
                "COLLECTED_AT": quando, "BYTES": dados, "TAMANHO": len(dados)}


def e_pdf(dados: bytes) -> bool:
    """A assinatura real dos bytes, não o que o servidor disse que eram.

    Um desafio de bot devolve `200` com HTML por dentro. `content-type` é
    declaração; `%PDF-` é facto.
    """
    return dados[:5] == b"%PDF-"


if __name__ == "__main__":
    print(json.dumps({"O_QUE_ISTO_E": "adaptadores, nao donos",
                      "PORTAS": ["ArmazemSupabase", "MemoriaSupabase"]},
                     ensure_ascii=False))
