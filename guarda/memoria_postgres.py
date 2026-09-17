#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MEMÓRIA EM POSTGRES, FALADA POR `psql` — o adaptador canónico, um só.

POR QUE ISTO MORA EM `guarda/` E NÃO EM `provas/`
-------------------------------------------------
Até 2026-09-17 o único adaptador Postgres completo desta casa — o que sabe
responder às perguntas do RAW, do DERIVED e do DOCUMENTO estruturado — vivia em
`provas/preservar_coleta_no_postgres.py`. Era prova, e por isso o runtime não
o podia importar. E não importava: a porta de linha de comando do orquestrador
corria sem memória nenhuma, e o replay canário pelo workflow real (run
35215565657, know-how §132) mediu o preço — um banco criado, migrado e
aprovado pelo portão, e nunca escrito.

    PROVA NÃO É RUNTIME.
    DEPENDÊNCIA DECLARADA != DEPENDÊNCIA LIGADA.

A implementação genérica veio para cá, na gaveta do dono, ao lado das portas
que implementa (`preservar_coleta.Memoria`, `preservar_derivado.MemoriaDoDerivado`,
`preservar_documento.MemoriaDoDocumento`). A prova passou a importar daqui e
a acrescentar só a trava dela; a porta LIVE (`portas_live.MemoriaSupabase`)
passou a ser uma subclasse que só sabe de onde vem a URL. Um dialeto, uma
implementação, três chamadores.

    ISTO NÃO É UM DONO. É UMA PORTA.

Não decide nada, não tem regra de negócio, não sabe o que é uma derivação.
Traduz chamadas para `psql`, e mais nada. Toda a lei continua nos donos.

O QUE ESTE ADAPTADOR NÃO FAZ
----------------------------
Não valida se o banco é descartável. Isso é decisão de quem COMPÕE o runtime
(`orquestrador/persistencia.py`) e de cada prova — e vive em
`guarda/banco_descartavel.py`. Um adaptador que recusasse produção não poderia
servir a porta LIVE; um adaptador que ligasse a produção por conta própria
seria o defeito que esta casa mais teme. Ele não decide: liga onde lhe
mandarem, e quem manda tem de provar antes.

O DIALETO, E AS LIÇÕES QUE ELE CARREGA
--------------------------------------
    -X -q -A -t -F <sep>   a saída que uma máquina lê: sem `~/.psqlrc`, sem
                            ruído, sem alinhamento, sem cabeçalho nem rodapé
    -f - + stdin UTF-8      TEXTO ACENTUADO NÃO VIAJA EM ARGV NO WINDOWS
                            (§130: 0x92, a aspa curva de um boletim da
                            Campania, rebentou o STRUCTURED)
    DSN em ÚLTIMO           o psql do Windows não permuta opções (BG-04)
    `id` volta inteiro      `bigserial` no banco e `"17"` no Python seriam o
                            mesmo campo com dois tipos
    tempo volta normalizado o Postgres imprime `2026-09-08 00:00:00+00`; nós
                            escrevemos `...T...Z`; comparar as duas formas
                            daria METADATA_CONFLICT falso
    erro sem segredo        um erro do psql pode trazer a URL — e a URL pode
                            trazer a senha

Não usa driver instalado: fala pelo `psql`, que o runner já tem. Instalar um
pacote global só para uma porta continua proibido nesta casa.
"""
import re
import subprocess

from guarda.cliente_postgres import resolver_psql
from guarda.preservar_derivado import MemoriaDoDerivado

_SEGREDO = re.compile(r"postgres(ql)?://[^\s\"']*")


def sem_segredo(texto: str) -> str:
    """Nunca se ecoa uma URL de banco: ela pode trazer a senha dentro."""
    return _SEGREDO.sub("<URL_OMITIDA>", texto or "")


def lit(v) -> str:
    """Um valor como literal SQL. `None` vira `null`, e nunca a palavra 'None'.

    ⚠️ ISTO NÃO É DECORAÇÃO. As chaves de identidade têm campos que PODEM ser
    nulos — `document_key` na tentativa sem prova, `storage_object_id` numa
    linha não preservada. Interpolar `None` faria a consulta procurar a
    STRING 'None', encontrar nada, e o escritor concluir que a observação não
    existe. Um retry entraria outra vez, e a duplicata teria vindo de uma
    conversão de tipo.
    """
    if v is None:
        return "null"
    return "'" + str(v).replace("'", "''") + "'"


class MemoriaPostgres(MemoriaDoDerivado):
    """A porta do banco falada por `psql`. Lê de volta com `SELECT`, como deve.

    Implementa as três portas de leitura desta casa — `Memoria` (RAW),
    `MemoriaDoDerivado` (DERIVED) e, por contrato de forma,
    `MemoriaDoDocumento` (STRUCTURED) — porque o adaptador é do BANCO, e o
    banco é um só para as três etapas da mesma corrida.
    """

    #: O separador de campos. Uma unidade de separação do ASCII, que nunca
    #: aparece num caminho, numa URL nem num hash.
    SEP = "\x1f"

    def __init__(self, url):
        if not isinstance(url, str) or not url.strip():
            raise ValueError("MemoriaPostgres exige uma URL; recebeu vazio.")
        self.url = url.strip()
        self.aplicacoes = 0

    # ── FALAR COM O psql ─────────────────────────────────────────────────
    def _psql(self, sql):
        """Uma saída que uma máquina consegue ler, e sem surpresas.

        ⚠️ A VERSÃO ANTERIOR MONTAVA ISTO POR ÍNDICE (`cmd[3:3] = [...]`) e
        inseria os sinalizadores entre o `-v` e o `ON_ERROR_STOP=1`. O psql
        leu `-v -t`, a saída voltou com cabeçalho e rodapé, e
        `int('count\\n0\\n(1 row)')` rebentou no CI. Não se conserta isso a
        apanhar `(1 row)` com as mãos: conserta-se pedindo a saída certa.

        ⚠️ A CABEÇA DA LISTA NÃO É `"psql"`. O replay canário 3 (run GitHub
        35232024024, know-how §135) caiu AQUI com `FileNotFoundError`: o
        Python do job não tinha `psql` no PATH, e o nome nu confiava nele.
        Quem diz qual executável usar é `guarda/cliente_postgres.py` — a
        declaração `SINTONIA_PSQL_EXE`, ou o PATH quando nada está declarado,
        e falha fechada quando nenhum serve. Nunca um caminho inventado.
        """
        cmd = [resolver_psql(), "-X", "-q", "-A", "-t", "-F", self.SEP,
               "-v", "ON_ERROR_STOP=1", "-f", "-", self.url]
        r = subprocess.run(cmd, input=sql, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise IOError(sem_segredo(r.stderr.strip())[:400])
        return r.stdout

    def _valor(self, sql):
        """Um escalar, e a garantia de que veio sozinho."""
        linhas = [x for x in self._psql(sql).splitlines() if x.strip()]
        if len(linhas) != 1:
            raise IOError(
                "esperava UM valor e vieram %d linhas: %r. O psql voltou a "
                "mandar cabecalho ou rodape." % (len(linhas), linhas[:4]))
        return linhas[0]

    def aplicar(self, sql):
        # `encoding="utf-8"`: `text=True` sozinho codifica o stdin na codepage
        # da máquina (cp1252 no Windows) e o texto do documento chegava
        # mutilado ao banco UTF-8. Mesma lei do `_psql` acima.
        self.aplicacoes += 1
        r = subprocess.run([resolver_psql(), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "-f", "-", self.url],
                           input=sql, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise IOError(sem_segredo(r.stderr.strip())[:400])

    # O `psql` devolve tudo como texto, e `raw_asset.id` é `bigserial`. Só o
    # `id` entra: converter tudo o que parece número transformaria um `sha256`
    # de dígitos ou um identificador nativo em inteiro.
    INTEIROS = ("id",)

    def _linhas(self, sql, colunas):
        fora = []
        for linha in self._psql(sql).splitlines():
            if not linha.strip():
                continue
            valores = linha.split(self.SEP)
            d = {c: (v if v != "" else None) for c, v in zip(colunas, valores)}
            for c in self.INTEIROS:
                if d.get(c) is not None:
                    d[c] = int(d[c])
            fora.append(d)
        return fora

    # ── O TEMPO VOLTA NA FORMA EM QUE FOI ESCRITO ────────────────────────
    # ⚠️ Cortava em segundos e produzia o conflito falso que existe para
    # evitar: `2026-09-07T15:37:40.362Z` escrito, `15:37:40Z` lido, DEZ
    # observações boas em METADATA_CONFLICT. Os zeros à direita saem, então um
    # instante sem milissegundos continua a voltar exatamente como voltava.
    _ISO = ("regexp_replace(to_char(%s at time zone 'UTC', "
            "'YYYY-MM-DD\"T\"HH24:MI:SS.US'), '\\.?0+$', '') || 'Z'")

    COLS_RUN = ("run_id", "actor", "actor_version", "source_country",
                "started_at", "rule_version", "capture_method", "status",
                "finished_at")
    # 026: a identidade da observação entra na projeção.
    COLS_OBJ = ("run_id", "storage_path", "media_type", "bytes", "sha256",
                "captured_at", "source_url",
                "identity_state", "source_id", "document_key",
                "document_key_basis")
    # A CÓPIA tem as colunas DELA; a OBSERVAÇÃO traz `id` porque é dele que
    # sai o `RAW_OBSERVATION_ID`.
    COLS_COPIA = ("id", "storage_path", "media_type", "bytes", "sha256")
    COLS_OBS = ("id", "storage_object_id", "attempts") + COLS_OBJ
    COLS_OBJ_DA_CORRIDA = ("id",) + COLS_OBJ
    TEMPOS = ("started_at", "finished_at", "captured_at", "derived_at")

    def _select(self, colunas, prefixo=""):
        return ", ".join(self._ISO % (prefixo + c) if c in self.TEMPOS
                         else prefixo + c for c in colunas)

    # ── A PORTA DO RAW (`Memoria`) ───────────────────────────────────────
    def corrida(self, run_id):
        linhas = self._linhas(
            "select %s from public.collection_run where run_id = %s"
            % (self._select(self.COLS_RUN), lit(run_id)), self.COLS_RUN)
        return linhas[0] if linhas else None

    def copia_em(self, storage_path):
        linhas = self._linhas(
            "select %s from public.storage_object where storage_path = %s"
            % (self._select(self.COLS_COPIA), lit(storage_path)),
            self.COLS_COPIA)
        return linhas[0] if linhas else None

    def observacao_identificada(self, run_id, source_id, document_key, sha256):
        linhas = self._linhas(
            "select %s from public.raw_asset where identity_state = '%s'"
            " and run_id = %s and source_id = %s and document_key = %s"
            " and sha256 = %s"
            % (self._select(self.COLS_OBS), "FORWARD_IDENTIFIED",
               lit(run_id), lit(source_id), lit(document_key), lit(sha256)),
            self.COLS_OBS)
        return linhas[0] if linhas else None

    def tentativa_sem_prova(self, run_id, source_id, storage_object_id, sha256):
        # `is not distinct from`, e não `=`: sem cópia o id é nulo dos dois
        # lados, e `null = null` não é verdade.
        linhas = self._linhas(
            "select %s from public.raw_asset where identity_state = '%s'"
            " and run_id = %s and source_id = %s"
            " and storage_object_id is not distinct from %s and sha256 = %s"
            % (self._select(self.COLS_OBS), "FORWARD_IDENTITY_UNPROVEN",
               lit(run_id), lit(source_id), lit(storage_object_id),
               lit(sha256)), self.COLS_OBS)
        return linhas[0] if linhas else None

    def observacoes_em(self, storage_path):
        """TODAS. Devolve lista para que ninguém lhe chame uma linha."""
        return self._linhas(
            "select %s from public.raw_asset where storage_path = %s"
            " order by id"
            % (self._select(self.COLS_OBS), lit(storage_path)), self.COLS_OBS)

    def objetos_da_corrida(self, run_id):
        return self._linhas(
            "select %s from public.raw_asset where run_id = %s "
            "order by storage_path"
            % (self._select(self.COLS_OBJ_DA_CORRIDA), lit(run_id)),
            self.COLS_OBJ_DA_CORRIDA)

    def contar(self, tabela, onde="true"):
        return int(self._valor("select count(*) from public.%s where %s"
                               % (tabela, onde)))

    # ── A PORTA DO DERIVADO (`MemoriaDoDerivado`) ────────────────────────
    COLS_RAW = ("id", "run_id", "storage_path", "media_type", "bytes",
                "sha256", "captured_at", "source_url")
    COLS_DER = ("id", "raw_asset_id", "parent_sha256", "kind", "producer",
                "producer_version", "pipeline_version", "parameters_hash",
                "serie_posicao", "sha256", "bytes", "media_type",
                "storage_path", "derived_at")

    def raw_por_id(self, raw_asset_id):
        # JOIN só de leitura com a corrida, pelo `source_country`. Todas as
        # colunas do bruto levam `a.`: `run_id` existe nas duas tabelas.
        cols = self.COLS_RAW + ("source_country",)
        linhas = self._linhas(
            "select %s, r.source_country from public.raw_asset a "
            "join public.collection_run r on r.run_id = a.run_id "
            "where a.id = %d" % (self._select(self.COLS_RAW, "a."),
                                 int(raw_asset_id)), cols)
        return linhas[0] if linhas else None

    def derivado_com_identidade(self, identidade):
        # `is not distinct from`: a linha de `serie_posicao` NULL tem de ser
        # reencontrada, senão o reencontro vira colisão.
        onde = " and ".join("%s is not distinct from %s" % (c, lit(identidade[c]))
                            for c in identidade)
        linhas = self._linhas(
            "select %s from public.derived_artifact where %s"
            % (self._select(self.COLS_DER), onde), self.COLS_DER)
        return linhas[0] if linhas else None

    # ── A PORTA DO DOCUMENTO ESTRUTURADO (migration 030) ────────────────
    COLS_DOC = ("derived_artifact_id", "run_id", "source_id", "hash_texto",
                "document_id", "source_url", "titulo")

    def documento_do_derivado(self, derived_artifact_id):
        """A linha que já estrutura este derivado, ou `None`. O `texto` NÃO
        vem: quem pergunta «já existe?» precisa do `hash_texto`, não do corpo."""
        linhas = self._linhas(
            "select %s from public.documento_estruturado"
            " where derived_artifact_id = %d"
            % (self._select(self.COLS_DOC), int(derived_artifact_id)),
            self.COLS_DOC)
        return linhas[0] if linhas else None
