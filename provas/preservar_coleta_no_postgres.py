#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MESMA GARANTIA, CONTRA POSTGRES DE VERDADE — e num que morre no fim.

POR QUE ISTO EXISTE
-------------------
`tests/test_preservar_coleta_no_banco.py` prova a reconciliação contra um banco
real, mas SQLite. As travas que interessam são as mesmas — `storage_path`
único, `sha256` não único, `run_id` obrigatório com chave estrangeira — só que
SQLite não é Postgres, e dizer «provado no banco» sem dizer **qual** seria
esconder metade da frase.

Este ficheiro corre os mesmos cenários contra **Postgres 16**, com a
`migration 001` ORIGINAL aplicada — enum `run_status` incluído, que o SQLite
teve de traduzir para um `CHECK`. Ele corre no workflow `banco-descartavel.yml`,
num contentor que nasce e morre dentro do próprio job.

    DB_TESTED (SQLITE)                    é o que a bateria local prova
    POSTGRES16_FOUNDATION_SCHEMA_TESTED   é o que este ficheiro acrescenta

E o nome é longo de propósito. Aqui aplica-se **só a migration 001**: as
002–021 não entram, e chamar a isto «o esquema atual provado» seria dizer mais
do que se mediu. Alargar o escopo não é o assunto — não superestimar a prova é.

A TRAVA CONTRA O ACIDENTE
-------------------------
Este é o único ficheiro desta missão que fala com um banco a sério. Por isso
ele **recusa-se a arrancar** se a ligação não for descartável. E a trava não
procura pedaços de texto: ela **decompõe a URL** e exige que o `hostname` seja
exatamente local E que o banco esteja na lista curta dos descartaveis. Um
dedo enganado a
apontar para produção não passa daqui.

Não usa driver instalado: fala pelo `psql`, que o runner já tem. Instalar um
pacote global só para um teste passar continua proibido.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.preservar_coleta import (  # noqa: E402
    METADATA_CONFLICT, NEW_RUN_SAME_STORAGE_PATH, PRESERVED_AND_REGISTERED, RUN_ID_CONFLICT,
    UPLOAD_PENDING_METADATA, ArmazemDeMentira, Memoria,
    caminho_do_objeto, preservar, sha256)

MIGRACAO = os.path.join(RAIZ, "supabase", "migrations",
                        "001_fundacao_geografia_e_proveniencia.sql")
# 025 acrescenta uma trava A `raw_asset`, e esta prova escreve linhas dessa
# tabela. Prova-la sobre a 001 sozinha seria prova-la contra um esquema que
# esta casa ja nao tem.
# E a 026 acrescenta a IDENTIDADE da observacao, que o writer passou a
# escrever: sem ela, o SQL deste dono nomeia colunas que nao existem.
MIGRACAO_025 = os.path.join(RAIZ, "supabase", "migrations",
                            "025_o_objeto_ganha_casa.sql")
MIGRACAO_026 = os.path.join(RAIZ, "supabase", "migrations",
                            "026_a_observacao_ganha_identidade.sql")

HOSTS_LOCAIS = ("localhost", "127.0.0.1", "::1", "[::1]")
# Os UNICOS nomes de banco que esta casa aceita para uma prova. Sao os que os
# workflows criam e deitam fora; qualquer outro — sobretudo um chamado como a
# producao — nao passa. Acrescentar um nome aqui e uma decisao consciente, e e
# esse o ponto: a lista e curta para que crescer doa.
# `social` entrou em 2026-09-08 para a prova do contrato de persistencia
# social. Banco proprio de proposito: herdar linhas de outra prova faria um
# caso passar por causa do estado alheio.
# `objeto` entrou em 2026-09-10 para a prova da migration 025, que separa a
# copia da observacao. Banco proprio de proposito: herdar linhas de outra prova
# faria um caso passar por causa do estado alheio.
BANCOS_PERMITIDOS = ("descartavel", "derivado", "social", "objeto")


def _e_descartavel(url: str) -> bool:
    """O endereço tem de ser local **e** o banco tem de chamar-se descartável.

    ⚠️ A VERSÃO ANTERIOR PROCURAVA PEDAÇOS DE TEXTO — `localhost`, `@db:`,
    `@postgres:` — em qualquer sítio da URL. Isso não é uma trava: um servidor
    chamado `db.exemplo.com` contém `db.`, e um host
    `localhost.atacante.example` contém `localhost`. Comparar pedaços de texto
    onde se devia comparar **estrutura** é como conferir um passaporte pelas
    letras que aparecem nele.

    Aqui a URL é **decomposta**, e as duas partes são exigidas separadamente:

        hostname   tem de ser EXATAMENTE um dos locais
        database   tem de estar na lista curta: `descartavel`, `derivado`

    E é lista de PERMISSÃO, não de bloqueio: bloqueio falha por omissão — basta
    esquecer um nome. Permissão falha fechado, que é o lado certo para falhar.
    """
    from urllib.parse import urlparse
    try:
        u = urlparse(url or "")
    except ValueError:
        return False
    if u.scheme not in ("postgres", "postgresql"):
        return False
    if (u.hostname or "").lower() not in HOSTS_LOCAIS:
        return False
    return (u.path or "").lstrip("/") in BANCOS_PERMITIDOS


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


class MemoriaPostgres(Memoria):
    """A porta do banco falada por `psql`. Lê de volta com `SELECT`, como deve."""

    def __init__(self, url):
        if not _e_descartavel(url):
            raise SystemExit(
                "RECUSADO: '%s' nao parece um banco descartavel local. "
                "Esta prova nunca corre contra producao." % url)
        self.url = url
        self.aplicacoes = 0

    # O SEPARADOR DE CAMPOS. Uma unidade de separação do ASCII, que nunca
    # aparece num caminho, numa URL nem num hash.
    SEP = "\x1f"

    def _psql(self, sql):
        """Uma saída que uma máquina consegue ler, e sem surpresas.

        ⚠️ A VERSÃO ANTERIOR MONTAVA ISTO POR ÍNDICE:

            cmd = ["psql", url, "-v", "ON_ERROR_STOP=1", "-c", sql]
            cmd[3:3] = ["-t", "-A", "-F", sep]

        O `[3:3]` inseria os sinalizadores **entre** o `-v` e o
        `ON_ERROR_STOP=1`. O `psql` leu `-v -t`, ou seja «define uma variável
        chamada `-t`», e o resto virou lixo posicional. A saída voltou alinhada,
        com cabeçalho e rodapé, e `int('count\\n0\\n(1 row)')` rebentou no CI.

        Não se conserta isso a apanhar `count`/`(1 row)` com as mãos: isso seria
        aprender a ler a saída errada. Conserta-se **pedindo a saída certa**:

            -X   não ler o `~/.psqlrc` de quem quer que corra isto
            -q   sem ruído
            -A   sem alinhamento
            -t   só as linhas, sem cabeçalho nem rodapé
            -F   o separador de campos
        """
        cmd = ["psql", "-X", "-q", "-A", "-t", "-F", self.SEP,
               "-v", "ON_ERROR_STOP=1", "-c", sql, self.url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise IOError(r.stderr.strip()[:400])
        return r.stdout

    def _valor(self, sql):
        """Um escalar, e a garantia de que veio sozinho.

        Se o `psql` alguma vez voltar a mandar cabeçalho ou rodapé, isto
        rebenta com uma mensagem que diz o que veio — em vez de tentar
        adivinhar qual das linhas era o número.
        """
        linhas = [x for x in self._psql(sql).splitlines() if x.strip()]
        if len(linhas) != 1:
            raise IOError(
                "esperava UM valor e vieram %d linhas: %r. O psql voltou a "
                "mandar cabecalho ou rodape." % (len(linhas), linhas[:4]))
        return linhas[0]

    def aplicar(self, sql):
        self.aplicacoes += 1
        r = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            self.url],
                           input=sql, capture_output=True, text=True)
        if r.returncode != 0:
            raise IOError(r.stderr.strip()[:400])

    # O `psql` devolve tudo como texto, e `raw_asset.id` e `bigserial`. Mesma
    # razao do dialeto acima: a porta descartavel devolve `17` e esta devolveria
    # `"17"`, e o mesmo campo com dois tipos e dois contratos com um nome so.
    INTEIROS = ("id",)

    def _linhas(self, sql, colunas):
        fora = []
        for linha in self._psql(sql).splitlines():
            if not linha.strip():
                continue
            valores = linha.split("\x1f")
            d = {c: (v if v != "" else None) for c, v in zip(colunas, valores)}
            for c in self.INTEIROS:
                if d.get(c) is not None:
                    d[c] = int(d[c])
            fora.append(d)
        return fora

    # O TEMPO TEM DE VOLTAR NA MESMA FORMA EM QUE FOI ESCRITO.
    # O Postgres guarda `timestamptz` e devolve `2026-09-08 00:00:00+00`; nos
    # escrevemos `2026-09-08T00:00:00Z`. Comparar as duas formas daria um
    # METADATA_CONFLICT falso — e conflito falso e pior do que conflito
    # nenhum, porque ensina toda a gente a ignorar o alarme.
    #
    # A normalizacao mora AQUI, no adaptador, porque e um assunto de dialeto.
    # O dono da escrita nao tem de saber como cada banco imprime uma data.
    _ISO = "to_char(%s at time zone 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')"

    COLS_RUN = ("run_id", "actor", "actor_version", "source_country",
                "started_at", "rule_version", "capture_method", "status",
                "finished_at")
    # 026: a identidade da observacao entra na projecao. Sem ela o writer
    # pergunta «ja ha linha neste caminho?» e recebe a linha SEM saber se ela e
    # a mesma observacao — que e a pergunta que a chave de idempotencia
    # responde. E a conferencia POS-ESCRITA leria `null` onde escreveu estado.
    COLS_OBJ = ("run_id", "storage_path", "media_type", "bytes", "sha256",
                "captured_at", "source_url",
                "identity_state", "source_id", "document_key",
                "document_key_basis")
    # A leitura da corrida traz o `id`, porque e dela que sai o
    # `RAW_OBSERVATION_ID`. E `COLS_OBS` tambem: uma chave que encontra uma
    # linha tem de poder dizer QUAL linha encontrou.
    # A COPIA tem as colunas DELA, e `id` esta la porque e ele que a chave da
    # tentativa sem prova usa. A OBSERVACAO traz `id` pela mesma razao: quem
    # encontra uma linha pela chave precisa de poder dizer QUAL linha achou.
    COLS_COPIA = ("id", "storage_path", "media_type", "bytes", "sha256")
    COLS_OBS = ("id", "storage_object_id", "attempts") + COLS_OBJ

    COLS_OBJ_DA_CORRIDA = ("id",) + COLS_OBJ
    TEMPOS = ("started_at", "finished_at", "captured_at", "derived_at")

    def _select(self, colunas):
        return ", ".join(self._ISO % c if c in self.TEMPOS else c
                         for c in colunas)

    def corrida(self, run_id):
        linhas = self._linhas(
            "select %s from public.collection_run where run_id = '%s'"
            % (self._select(self.COLS_RUN), run_id), self.COLS_RUN)
        return linhas[0] if linhas else None

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
            "select %s from public.raw_asset where run_id = '%s' "
            "order by storage_path"
            % (self._select(self.COLS_OBJ_DA_CORRIDA), run_id),
            self.COLS_OBJ_DA_CORRIDA)

    def contar(self, tabela):
        return int(self._valor("select count(*) from public.%s" % tabela))

    # ── as leituras que o dono do DERIVADO precisa ───────────────────────
    # Vivem aqui porque este e o adaptador do Postgres — a porta e uma so, e o
    # dialeto tambem. `MemoriaDoDerivado` declara-as; isto implementa-as.
    COLS_RAW = ("id", "run_id", "storage_path", "media_type", "bytes",
                "sha256", "captured_at", "source_url")
    COLS_DER = ("id", "raw_asset_id", "parent_sha256", "kind", "producer",
                "producer_version", "pipeline_version", "parameters_hash",
                "serie_posicao", "sha256", "bytes", "media_type",
                "storage_path", "derived_at")

    def raw_por_id(self, raw_asset_id):
        # JOIN SO DE LEITURA com a corrida, pelo `source_country`. Sem coluna
        # nova: a informacao ja existe, uma tabela ao lado.
        # TODAS as colunas do bruto levam o prefixo `a.`. Sem isso o `run_id`
        # fica ambiguo — ele existe nas duas tabelas do join, e o Postgres
        # recusa, com razao: nao lhe cabe adivinhar de qual se fala.
        cols = self.COLS_RAW + ("source_country",)
        sel = ", ".join(self._ISO % ("a." + c) if c in self.TEMPOS else "a." + c
                        for c in self.COLS_RAW)
        linhas = self._linhas(
            "select %s, r.source_country from public.raw_asset a "
            "join public.collection_run r on r.run_id = a.run_id "
            "where a.id = %d" % (sel, int(raw_asset_id)), cols)
        return linhas[0] if linhas else None

    def derivado_com_identidade(self, identidade):
        # `is not distinct from` em vez de `=`: em SQL, NULL = NULL e
        # DESCONHECIDO, e sem isto a linha de `serie_posicao` NULL nunca seria
        # reencontrada — o writer acharia sempre que e a primeira vez, e o
        # reencontro viraria colisao.
        def _v(x):
            return "null" if x is None else "'%s'" % str(x).replace("'", "''")
        onde = " and ".join("%s is not distinct from %s" % (c, _v(identidade[c]))
                            for c in identidade)
        linhas = self._linhas(
            "select %s from public.derived_artifact where %s"
            % (self._select(self.COLS_DER), onde), self.COLS_DER)
        return linhas[0] if linhas else None


# ─────────────────────────────────────────────────────────────────────────
# OS CENÁRIOS — os mesmos do banco local, contra o motor de verdade
# ─────────────────────────────────────────────────────────────────────────
A, B = b"o conteudo A", b"o conteudo B"
FIM = "2026-09-08T00:05:00Z"


def _corrida(run_id="IT-PG-0001", **extra):
    d = {"RUN_ID": run_id, "PLATFORM": "local", "ACTOR": "teste",
         "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT", "MISSION": "prova",
         "STARTED_AT": "2026-09-08T00:00:00Z", "RULE_VERSION": "1",
         "CAPTURE_METHOD": "HTTP_GET"}
    d.update(extra)
    return d


def _pousar_outro_conteudo(banco, caminho, sha, doc, bytes_=1,
                           run_id="IT-PG-A"):
    """Outro escritor poe OUTRO conteudo no mesmo endereco.

    Troca a COPIA e a OBSERVACAO juntas, porque desde a 026 elas nao podem
    discordar: a chave estrangeira composta recusa `raw_asset.sha256 = H1` a
    apontar para um objeto de `H2`. Apagar e reescrever e o unico caminho que
    respeita a trava — e o cenario continua a ser o mesmo.
    """
    banco.aplicar(
        "delete from public.raw_asset where storage_path = '%s';\n"
        "delete from public.storage_object where storage_path = '%s';\n"
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256) values ('%s','application/pdf',1,'%s');\n"
        "insert into public.raw_asset (run_id, storage_path, media_type, bytes, "
        "sha256, captured_at, storage_object_id, identity_state, source_id, "
        "document_key, document_key_basis) select '%s','%s',"
        "'application/pdf',%d,'%s','2026-09-08T00:00:00Z', o.id,"
        "'FORWARD_IDENTIFIED','IT-T2-002','%s','SOURCE_DOCUMENT_ID' "
        "from public.storage_object o where o.storage_path = '%s';"
        % (caminho, caminho, caminho, sha, run_id, caminho, bytes_, sha,
           doc, caminho))


def _art(nome, dados, nativo):
    return {"COUNTRY": "IT", "SOURCE_SLUG": "fonte-de-teste",
            # 026: SOURCE_ID canonico e DOCUMENT_ID provado pelo contrato.
            "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": "ARPAV:Z07:%s" % nativo,
            "ARTIFACT_KIND": "DOCUMENT", "NAME": nome,
            "SOURCE_NATIVE_ID": nativo, "SHA256": sha256(dados),
            "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
            "CAPTURED_AT": "2026-09-08T00:00:00Z",
            "SOURCE_URL": "https://exemplo.it/%s" % nativo}


def _bytes_de(obj):
    return {sha256(A): A, sha256(B): B}[obj["SHA256"]]


def _correr(banco, artefatos, run=None, armazem=None):
    return preservar(run or _corrida(), artefatos, armazem or ArmazemDeMentira(),
                     _bytes_de, memoria=banco, terminou_em=FIM)


def cenarios(banco):
    """Os casos A–L, cada um na sua corrida e com o seu próprio arranjo.

    A versão anterior encadeava tudo na mesma corrida e usava `and`/`or`
    soltos — um caso podia dar PASS por causa do estado deixado pelo anterior.
    Aqui cada caso monta o que precisa e **declara o que observou**, para que um
    PASS nunca seja um acaso herdado.

    Devolve `(nome, passou, detalhe)`.
    """
    fora = []

    def caso(nome, condicao, detalhe=""):
        fora.append((nome, bool(condicao), detalhe))

    # ── A · B · C — o caminho feliz, contado no próprio Postgres ─────────
    run_a = _corrida("IT-PG-A")
    arm_a = ArmazemDeMentira()
    r = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                run=run_a, armazem=arm_a)
    caso("A_dois_objetos_planeados", r["PLANO"]["OBJETOS_PLANEADOS"] == 2,
         "planeados=%s" % r["PLANO"]["OBJETOS_PLANEADOS"])
    caso("B_o_SELECT_confirma_duas_linhas",
         r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"] == 2,
         "observadas=%s contar=%d" % (
             r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"],
             banco.contar("raw_asset")))
    pos = r["CONFERENCIA_POS_ESCRITA"] or {}
    caso("B2_os_campos_batem_apos_a_escrita",
         pos.get("POST_WRITE_METADATA_MATCH") == 2 and not pos.get("DIVERGENTES"),
         "match=%s divergentes=%s" % (pos.get("POST_WRITE_METADATA_MATCH"),
                                      len(pos.get("DIVERGENTES") or [])))
    linha_a = banco.corrida("IT-PG-A") or {}
    caso("C_a_corrida_termina_concluida_no_postgres",
         r["RUN_STATE"] == "COMPLETE" and linha_a.get("status") == "concluida"
         and r["PENDENCIA"] == PRESERVED_AND_REGISTERED,
         "run_state=%s status=%s" % (r["RUN_STATE"], linha_a.get("status")))
    caso("C2_finished_at_gravado_e_diferente_do_started_at",
         bool(linha_a.get("finished_at"))
         and linha_a.get("finished_at") != linha_a.get("started_at"),
         "started=%s finished=%s" % (linha_a.get("started_at"),
                                     linha_a.get("finished_at")))

    # ── D · E — retry idêntico ───────────────────────────────────────────
    r2 = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                 run=run_a, armazem=arm_a)
    caso("D_retry_nao_duplica",
         banco.contar("raw_asset") == 2 and banco.contar("collection_run") == 1,
         "raw=%d run=%d" % (banco.contar("raw_asset"),
                            banco.contar("collection_run")))
    caso("E_reencontro_identico_e_REUSED",
         r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"] == 2
         and not r2["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"],
         "reused=%s" % r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"])

    # ── F — mesmo caminho, outro sha256 ──────────────────────────────────
    # ⚠️ DESDE A 026 AS DUAS ESPECIES NAO PODEM DISCORDAR. A versao anterior
    # deste caso mexia so no `sha256` da observacao — e isso agora e recusado
    # pela chave estrangeira COMPOSTA, que e exactamente a trava que se queria.
    # O cenario real («outro escritor pos outro conteudo neste endereco») troca
    # as DUAS: a copia e a observacao. Trocar so uma nunca foi o cenario; era
    # um atalho que o esquema antigo deixava passar.
    antes_de_f = banco.objetos_da_corrida("IT-PG-A")[0]
    caminho = antes_de_f["storage_path"]
    _pousar_outro_conteudo(banco, caminho, "f" * 64, "DOC:OUTRO")
    r3 = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                 run=run_a, armazem=arm_a)
    caso("F_sha_divergente_e_METADATA_CONFLICT",
         r3["PENDENCIA"] == METADATA_CONFLICT and r3["RUN_STATE"] == "PARTIAL",
         "pendencia=%s" % r3["PENDENCIA"])
    # E devolve-se a linha ORIGINAL — a dela, nao a de outro caminho. Repor
    # com a identidade errada colidiria com o indice parcial da fase 9, que e
    # exactamente o que ele existe para fazer.
    _pousar_outro_conteudo(banco, caminho, antes_de_f["sha256"],
                           antes_de_f["document_key"],
                           int(antes_de_f["bytes"]))

    # ── G — mesmo caminho reclamado por OUTRA corrida ────────────────────
    r4 = _correr(banco, [_art("a.pdf", A, "11")],
                 run=_corrida("IT-PG-G"), armazem=arm_a)
    # 026: divergir SO na corrida ganhou nome proprio. E na preparacao da fase
    # 10 deixou de ser CONFLITO: a observacao e legitima, a escrita e TENTADA,
    # e quem a recusa e a trava fisica no banco — nao uma decisao em Python.
    #
    #     O ESCRITOR DEIXOU DE CARREGAR A TRAVA DO ESQUEMA DENTRO DE SI.
    #
    # A `PENDENCIA` continua a dizer o nome certo, porque foi mesmo ela que
    # mordeu; o que mudou e QUEM decidiu.
    notas_g = r4["JA_EXISTIA_NO_BANCO"]["OBSERVACOES_NOVAS_EM_ENDERECO_OCUPADO"]
    caso("G_outra_corrida_no_mesmo_caminho_e_NEW_RUN_SAME_STORAGE_PATH",
         r4["PENDENCIA"] == NEW_RUN_SAME_STORAGE_PATH
         and r4["RUN_STATE"] == "PARTIAL"
         and not r4["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"]
         and notas_g and notas_g[0]["TIPO"] == NEW_RUN_SAME_STORAGE_PATH
         and not r4["MEMORIA"]["APLICADA"],
         "pendencia=%s notas=%d" % (r4["PENDENCIA"], len(notas_g)))

    # ── J — mesmo run_id, identidade congelada diferente ─────────────────
    r5 = _correr(banco, [_art("j.pdf", B, "jj")],
                 run=_corrida("IT-PG-A", ACTOR_VERSION="2"),
                 armazem=ArmazemDeMentira())
    caso("J_run_id_com_outra_identidade_e_RUN_ID_CONFLICT",
         r5["PENDENCIA"] == RUN_ID_CONFLICT and r5["RUN_STATE"] == "PARTIAL",
         "pendencia=%s" % r5["PENDENCIA"])

    # ── H — o SQL corre inteiro e grava a MENOS, sem erro nenhum ─────────
    # Encenado: a mao que aplica deixa cair um `insert`. E o que o
    # `on conflict do nothing` faz de verdade — corre, devolve sucesso, e o
    # banco fica com menos linhas do que se pediu. Se a reconciliacao viesse do
    # numero ESPERADO, isto passava como sucesso.
    original = banco.aplicar
    estado = {"engolir": True}

    def engolir_um_insert(sql):
        if estado["engolir"] and "insert into public.raw_asset" in sql:
            estado["engolir"] = False
            ficam, caiu = [], False
            for linha in sql.splitlines():
                if linha.startswith("insert into public.raw_asset") and not caiu:
                    caiu = True
                    continue
                ficam.append(linha)
            sql = "\n".join(ficam) + "\n"
        original(sql)

    banco.aplicar = engolir_um_insert
    arm_h = ArmazemDeMentira()
    r6 = _correr(banco, [_art("h1.pdf", A, "h1"), _art("h2.pdf", B, "h2")],
                 run=_corrida("IT-PG-H"), armazem=arm_h)
    banco.aplicar = original
    caso("H_grava_a_menos_e_a_reconciliacao_reprova",
         r6["MEMORIA"]["APLICADA"] and r6["MEMORIA"]["LINHAS_ESPERADAS"] == 2
         and r6["MEMORIA"]["LINHAS_OBSERVADAS"] == 1
         and r6["RUN_STATE"] == "PARTIAL"
         and "reconciliacao_observada" in r6["COMPLETION_BASIS"]["FALTOU"],
         "esperadas=%s observadas=%s estado=%s" % (
             r6["MEMORIA"]["LINHAS_ESPERADAS"],
             r6["MEMORIA"]["LINHAS_OBSERVADAS"], r6["RUN_STATE"]))
    caso("H2_a_corrida_fica_rodando_no_banco",
         (banco.corrida("IT-PG-H") or {}).get("status") == "rodando",
         "status=%s" % (banco.corrida("IT-PG-H") or {}).get("status"))
    caso("K_o_byte_fica_preservado_apos_falha_de_memoria",
         len(arm_h.objetos) == 2, "objetos=%d" % len(arm_h.objetos))

    # ── L — recuperação: correr outra vez faz SÓ o que falta ─────────────
    envios_antes = arm_h.envios
    r7 = _correr(banco, [_art("h1.pdf", A, "h1"), _art("h2.pdf", B, "h2")],
                 run=_corrida("IT-PG-H"), armazem=arm_h)
    caso("L_recuperacao_sem_duplicar_byte_nem_linha",
         arm_h.envios == envios_antes and r7["RUN_STATE"] == "COMPLETE"
         and (banco.corrida("IT-PG-H") or {}).get("status") == "concluida",
         "envios=%d->%d estado=%s" % (envios_antes, arm_h.envios,
                                      r7["RUN_STATE"]))

    # ── I — as linhas entram, mas o fecho da corrida falha ───────────────
    def recusar_o_fecho(sql):
        if "update public.collection_run" in sql:
            raise IOError("o banco recusou o fecho")
        original(sql)

    banco.aplicar = recusar_o_fecho
    r8 = _correr(banco, [_art("i1.pdf", A, "i1")],
                 run=_corrida("IT-PG-I"), armazem=ArmazemDeMentira())
    banco.aplicar = original
    caso("I_metadata_entra_mas_fecho_falha_nao_da_COMPLETE",
         r8["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"] == 1
         and r8["RUN_STATE"] == "PARTIAL"
         and "banco_diz_concluida" in r8["COMPLETION_BASIS"]["FALTOU"]
         and not r8["AS_DUAS_CASAS_CONCORDAM"],
         "observadas=%s estado=%s pendencia=%s" % (
             r8["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"],
             r8["RUN_STATE"], r8["PENDENCIA"]))

    # ── CORRIDA CONCORRENTE — contagem certa, conteúdo errado ────────────
    # A janela entre a leitura previa e o nosso insert. Se a reconciliacao
    # fosse so contagem, isto passava — e a corrida fechava sobre um conteudo
    # que nao e o nosso.
    art_r = _art("race.pdf", A, "rr")
    caminho_r = caminho_do_objeto(art_r)

    def intruso_entra_no_meio(sql):
        if "insert into public.raw_asset" in sql:
            banco.aplicar = original
            original("insert into public.collection_run "
                     "(run_id, platform, started_at, rule_version) values "
                     "('IT-PG-INTRUSA','x','2026-01-01T00:00:00Z','1') "
                     "on conflict (run_id) do nothing;")
            # 025: o intruso escreve as DUAS especies. No esquema novo nao
            # ha como escrever so uma — e a encenacao fica mais realista, nao
            # menos: quem chega primeiro ao endereco fica com a copia.
            original("insert into public.storage_object (storage_path, "
                     "media_type, bytes, sha256) values "
                     "('%s','application/pdf',999,'%s') "
                     "on conflict (storage_path) do nothing;"
                     % (caminho_r, "e" * 64))
            # 026: o intruso tambem declara identidade — nao ha caminho para
            # escrever sem ela, e e por isso que a encenacao continua a valer.
            original("insert into public.raw_asset (run_id, storage_path, "
                     "media_type, bytes, sha256, captured_at, "
                     "storage_object_id, identity_state, source_id, "
                     "document_key, document_key_basis) "
                     "select 'IT-PG-INTRUSA','%s',"
                     "'application/pdf',999,'%s','2026-01-01T00:00:00Z', o.id,"
                     "'FORWARD_IDENTIFIED','IT-INTRUSA','DOC:INTRUSA',"
                     "'SOURCE_DOCUMENT_ID' "
                     "from public.storage_object o where o.storage_path = '%s';"
                     % (caminho_r, "e" * 64, caminho_r))
        original(sql)

    banco.aplicar = intruso_entra_no_meio
    r9 = _correr(banco, [art_r], run=_corrida("IT-PG-RACE"),
                 armazem=ArmazemDeMentira())
    banco.aplicar = original
    quantas = len(banco.objetos_da_corrida("IT-PG-INTRUSA"))
    caso("RACE_contagem_certa_conteudo_errado_e_apanhado",
         quantas == 1 and r9["RUN_STATE"] == "PARTIAL"
         and r9["PENDENCIA"] == METADATA_CONFLICT
         and "campos_batem_apos_escrita" in r9["COMPLETION_BASIS"]["FALTOU"],
         "linhas_do_intruso=%d estado=%s pendencia=%s" % (
             quantas, r9["RUN_STATE"], r9["PENDENCIA"]))

    # ── FINISHED_AT — sem hora declarada, o relógio é o do banco ─────────
    r10 = preservar(_corrida("IT-PG-TEMPO"), [_art("t.pdf", B, "tt")],
                    ArmazemDeMentira(), _bytes_de, memoria=banco,
                    terminou_em=None)
    linha_t = banco.corrida("IT-PG-TEMPO") or {}
    caso("TEMPO_finished_at_nunca_herda_started_at",
         r10["RUN_STATE"] == "COMPLETE" and bool(linha_t.get("finished_at"))
         and linha_t.get("finished_at") != linha_t.get("started_at"),
         "started=%s finished=%s" % (linha_t.get("started_at"),
                                     linha_t.get("finished_at")))

    # ── AS TRAVAS DO ESQUEMA REAL ────────────────────────────────────────
    try:
        # A COPIA E CRIADA E LIGADA DE PROPOSITO: sem ela, a 025 tambem
        # recusaria, e este caso passaria pelo motivo errado — provando a trava
        # nova em vez da que tem no nome. Aqui so falta a corrida.
        banco.aplicar(
            "insert into public.storage_object (storage_path, media_type, "
            "bytes, sha256) values ('x/y','application/pdf',1,'%s') "
            "on conflict (storage_path) do nothing;" % ("a" * 64))
        banco.aplicar(
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, storage_object_id) "
            "select 'NAO-EXISTE','x/y','application/pdf',1,'%s',"
            "'2026-09-08T00:00:00Z', o.id from public.storage_object o "
            "where o.storage_path = 'x/y';" % ("a" * 64))
        caso("run_id_obrigatorio_com_chave_estrangeira", False,
             "o banco ACEITOU byte sem corrida")
    except Exception as erro:                          # noqa: BLE001
        # Qualquer recusa serve, e o motor decide o tipo: o Postgres chega aqui
        # como IOError (o adaptador embrulha o stderr do psql), o SQLite como
        # IntegrityError. Apanhar so um tipo faria o ENSAIO LOCAL rebentar em
        # vez de reprovar — e um ensaio que rebenta nao ensina nada.
        caso("run_id_obrigatorio_com_chave_estrangeira", True,
             type(erro).__name__)

    linhas = banco.objetos_da_corrida("IT-PG-A")
    caso("storage_path_unico_e_sha256_nao",
         len({x["storage_path"] for x in linhas}) == len(linhas)
         and len(linhas) >= 2, "linhas=%d" % len(linhas))

    return fora


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not url:
        print("BANCO_DESCARTAVEL_URL nao definido · NOT_RUN — esta prova so corre no "
              "workflow banco-descartavel.yml, contra um Postgres que morre "
              "no fim do job.")
        # ⚠️ NOT_RUN NAO E PASS, E O CODIGO DE SAIDA TEM DE O DIZER.
        #
        # Isto devolvia 0. Sem a variavel de ambiente a prova nao aplicava
        # migration nenhuma, nao falava com banco nenhum, e saia com o codigo
        # do sucesso — de modo que um workflow a que alguem tirasse o bloco
        # `env:` ficava verde para sempre sem nunca ter tocado no Postgres.
        #
        #     UM TESTE QUE PASSA PORQUE NAO CONSEGUIU MEDIR
        #     E PIOR DO QUE TESTE NENHUM.
        #
        # Nao vira FAIL: nao ha defeito nenhum provado. Vira NOT_RUN, que e uma
        # terceira coisa, com o codigo de saida 2 — o mesmo que
        # `provas/a_autoridade_da_fonte.py` ja usa. Uma casa, um vocabulario.
        return 2
    banco = MemoriaPostgres(url)
    for caminho in (MIGRACAO, MIGRACAO_025, MIGRACAO_026):
        with open(caminho, encoding="utf-8") as f:
            banco.aplicar(f.read())
    print("migrations 001 e 025 ORIGINAIS aplicadas num Postgres 16 descartavel.")
    print("ESCOPO DA PROVA: POSTGRES16_FOUNDATION_SCHEMA_TESTED — 001 + 025.")
    print("Isto NAO e o esquema LIVE inteiro: as migrations 002-024 nao foram")
    print("aplicadas aqui, e alargar isso nao e o assunto desta correcao.")

    resultados = cenarios(banco)
    for nome, passou, detalhe in resultados:
        print("  %-4s %-46s %s" % ("PASS" if passou else "FAIL", nome, detalhe))
    reprovados = [n for n, p, _ in resultados if not p]
    # O NOME DA PROVA E O ESCOPO DELA. `POSTGRES_DESCARTAVEL` dizia onde correu
    # e calava o que cobriu — e o que cobriu e so a migration 001.
    print("\nPOSTGRES16_FOUNDATION_SCHEMA_TESTED=%s · %d caso(s)%s" % (
        "PASS" if not reprovados else "FAIL", len(resultados),
        "" if not reprovados else " · reprovados: " + ", ".join(reprovados)))
    return 1 if reprovados else 0


if __name__ == "__main__":
    sys.exit(main())
