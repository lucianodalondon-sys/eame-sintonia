#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PORTAO DA BIG COLLECTION — o READY existe mesmo, ou so a etapa correu?

    BANCO_DESCARTAVEL_URL=postgresql://postgres:descartavel@localhost:5432/descartavel \\
    SINTONIA_SALA_BACKEND=POSTGRES \\
    SINTONIA_SALA_DSN=$BANCO_DESCARTAVEL_URL \\
        python3 provas/o_portao_da_big_collection.py

A PERGUNTA QUE ESTA PROVA EXISTE PARA FECHAR
---------------------------------------------
A prova da ponte de midia mediu, e a medicao foi honesta:

    ADMISSION_EXECUTED = YES · ADMISSION_DECISION = NAO_SEI
    READY_HANDLING = NOT_RUN · WAITING_ROOM_HANDLING = NOT_RUN

A etapa `READY` correu. **Nenhum READY existiu.** Sao coisas diferentes, e a
unica maneira de nao as confundir e ir ver a LINHA.

    ETAPA REGISTADA != UNIDADE PRODUZIDA.
    MODULO EXISTE != LINHA EXISTE.
    CAN DO != DID DO.

O QUE ELA FAZ
-------------
    A · a cadeia canonica ate a 032, num PostgreSQL 16 descartavel
    B · o contrato READY tem 19 campos, e a tabela tem colunas para os 19
    C · um canario ADMISSIVEL de verdade — texto italiano real, universo T3 —
        atravessa a porta com SIM
    D · o READY e construido pelo dono unico e POUSA na Sala
    E · a linha e lida DE OUTRO PROCESSO, pelo dono canonico da Sala

⚠️ A REGUA NAO SE MEXE PARA O CANARIO PASSAR
---------------------------------------------
O canario nao foi escolhido por ser facil: e um boletim italiano REAL que a
`provas/a_porta_le_italiano.py` ja media como positivo antes desta missao. Se
ele deixar de entrar, esta prova reprova — e isso e uma noticia sobre a regua,
nao um convite para a afrouxar.

E o canario NAO e midia, de proposito. A mesma prova mede, ao lado, que o
fixture de midia continua a NAO ser admissivel — porque essa e a verdade, e
enfraquecer a porta para o video entrar seria comprar o verde com a lei.

    O OBJETIVO E PROVAR A ESTRADA, NAO CONVENCER A ADMISSAO.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

import admissao                                   # noqa: E402
import coleta_checkpoint as cc                    # noqa: E402
import sala_de_espera as espera                   # noqa: E402

RUN = "RUN-GATE-BIG-COLLECTION-01"

#: O canario ADMISSIVEL. Nao e midia, e o motivo esta na docstring.
#: `LOJA` e o mesmo caminho que `provas/a_porta_le_italiano.py` usa, e os tres
#: documentos sao os que ela ja media como positivos em T3.
LOJA = os.path.join(RAIZ, "data", "collection-store", "italy")
CANDIDATOS = (
    ("IT-T3-010", "IT-T3-010/APOL_2026_N9_BR-COLLINA/v1_59da05274359/"
                  "Bollettino_Mosca_dellOlivo_n_9_del_07_09_2026.pdf"),
    ("IT-T3-002", "IT-T3-002/CAMPANIA_SA_02-09-2026/v1_0c2723e66201/SA-02-09.pdf"),
    ("IT-T3-008", "IT-T3-008/ARIF_SETTIMANALE_2026_N36/v1_e612807928b5/"
                  "Notiziario_Agrometeorologico_N36_02-09-2026.pdf"),
)
UNIVERSO = "T3"

SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "portao-big-collection.generated.json")

#: A 008 fica de fora: e a VERIFICACAO POS-APLICACAO, e corre-la no meio da
#: cadeia e pedir-lhe contas de tabelas que ainda nao nasceram.
_SO_VERIFICA = ("008",)

FALHAS, PASSOU = [], []
medido = {}


def caso(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def _mede(nome, valor, porque=""):
    medido[nome] = {"VALOR": str(valor), "PORQUE": porque}
    print("  %-36s = %-26s %s" % (nome, valor, porque[:40]))
    return valor


def _cadeia():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    fora = []
    for f in sorted(os.listdir(pasta)):
        if f.endswith(".sql") and f.split("_", 1)[0] not in _SO_VERIFICA:
            fora.append(f.split("_", 1)[0])
    return fora


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    cadeia = _cadeia()
    for n in cadeia:
        f = [x for x in sorted(os.listdir(pasta)) if x.startswith(n + "_")][0]
        r = subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, f), url],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s\n%s" % (f, r.stderr[:700]))
            raise SystemExit(1)
    return cadeia


def texto_do_pdf(caminho):
    """O texto do documento REAL, pelo extractor da casa."""
    saida = caminho + ".portao.txt"
    try:
        subprocess.run(["pdftotext", caminho, saida], capture_output=True,
                       check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    with io.open(saida, encoding="utf-8", errors="replace") as f:
        t = f.read()
    os.unlink(saida)
    return t


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL") or ""
    if not _pg._e_descartavel(url):
        raise SystemExit("RECUSADO: '%s' nao e um banco descartavel local. "
                         "Esta prova nunca corre contra producao." % url)

    # ⚠️ A SALA TEM DE SER A CANONICA, E EXIGE-SE ANTES DE MEDIR.
    # Sem `SINTONIA_SALA_BACKEND=POSTGRES` o dono cai para ficheiro — e um
    # READY escrito num disco efemero do runner passaria por READY persistido.
    # `exigir_canonica()` e do proprio dono: nao se reimplementa a pergunta.
    try:
        espera.exigir_canonica()
    except Exception as e:                                     # noqa: BLE001
        raise SystemExit("A SALA NAO E CANONICA: %s\n"
                         "Defina SINTONIA_SALA_BACKEND=POSTGRES e "
                         "SINTONIA_SALA_DSN. NAO se mede READY em ficheiro."
                         % e)

    # ── A · A CADEIA ATE A 032 ────────────────────────────────────────────
    print("A · A CADEIA CANONICA")
    cadeia = aplicar_migrations(url)
    _mede("MIGRATIONS_APLICADAS", len(cadeia), "ultima: %s" % cadeia[-1])
    _mede("MIGRATION_032_APPLIED", "032" in cadeia, "aplicada nesta corrida")
    caso("A1_a_cadeia_vai_ate_a_032", "032" in cadeia,
         "a 032 nao esta na cadeia desta arvore")

    sql = cc.Banco(url)
    colunas = {l[0] for l in sql.executa(
        "select column_name from information_schema.columns"
        " where table_schema='public' and table_name='sala_de_espera'")}
    _mede("COLUNAS_NA_SALA", len(colunas), "")
    OS_SETE = {"estagio", "fact_time_basis", "fact_location_basis",
               "published_at", "observed_at",
               "source_declared_evidence_class", "fato"}
    faltam = sorted(OS_SETE - colunas)
    caso("A2_as_sete_colunas_da_032_existem_na_tabela", not faltam,
         "faltam: %s" % faltam)

    # ── B · O CONTRATO TEM 19 CAMPOS ──────────────────────────────────────
    print("\nB · O CONTRATO READY")
    _mede("READY_CONTRACT_FIELDS", len(espera.CAMPOS_READY),
          "lido do dono, nao contado a mao")
    caso("B1_o_contrato_READY_tem_19_campos",
         len(espera.CAMPOS_READY) == 19,
         "tem %d: %s" % (len(espera.CAMPOS_READY), espera.CAMPOS_READY))
    # ⚠️ E OS 19 DO CONTRATO TEM DE TER ONDE MORAR NA TABELA.
    # Um contrato de 19 com uma tabela de 12 nao e um contrato: e uma promessa
    # que o `insert` desmente.
    #
    # ⚠️ MAS DOIS NAO MORAM NUMA COLUNA COM O MESMO NOME, E ISSO ESTA CERTO.
    # A primeira versao deste caso fazia `c.lower() in colunas` para os 19 e
    # reprovava — e reprovava sobre uma tabela que esta correcta:
    #
    #     ESTADO   e uma CONSTANTE do contrato (`PRONTO_PARA_INTELIGENCIA`).
    #              Guardar uma coluna cujo valor e sempre o mesmo seria guardar
    #              a palavra, e nao o facto. O dono repoe-a na leitura.
    #     CORRIDA  mora em `run_id`, que e a coluna que TODA a casa usa para a
    #              mesma coisa. Uma segunda coluna `corrida` seria um segundo
    #              nome para a mesma identidade, livre para divergir.
    #
    #     UM CAMPO DE CONTRATO NAO E UMA COLUNA. A EQUIVALENCIA DECLARA-SE.
    #
    # Declarada aqui, e verificada: se um destes dois passar a ter coluna
    # propria, ou mudar de casa, este caso reprova e obriga a reescrever a
    # equivalencia — que e como uma correspondencia deixa de apodrecer.
    MORA_NOUTRO_SITIO = {
        "ESTADO": ("constante do contrato, reposta na leitura pelo dono", None),
        "CORRIDA": ("a identidade da corrida, e a casa inteira chama-lhe assim",
                    "run_id"),
    }
    sem_coluna, mal_declarados = [], []
    for c in espera.CAMPOS_READY:
        if c.lower() in colunas:
            continue
        if c in MORA_NOUTRO_SITIO:
            _porque, alias = MORA_NOUTRO_SITIO[c]
            if alias is not None and alias not in colunas:
                mal_declarados.append("%s -> %s (coluna ausente)" % (c, alias))
            continue
        sem_coluna.append(c)
    caso("B2_cada_campo_do_contrato_tem_onde_morar", not sem_coluna,
         "sem coluna e sem equivalencia declarada: %s" % sem_coluna)
    caso("B2b_as_equivalencias_declaradas_existem_de_facto", not mal_declarados,
         " · ".join(mal_declarados))
    _mede("CAMPOS_COM_COLUNA_PROPRIA",
          sum(1 for c in espera.CAMPOS_READY if c.lower() in colunas),
          "os outros %d tem equivalencia declarada" % len(MORA_NOUTRO_SITIO))

    # ── C · O CANARIO ADMISSIVEL ──────────────────────────────────────────
    print("\nC · O CANARIO ADMISSIVEL (e a regua nao se mexe)")
    escolhido, texto, decisao = None, None, None
    tentados = []
    for fonte, rel in CANDIDATOS:
        caminho = os.path.join(LOJA, rel)
        if not os.path.isfile(caminho):
            tentados.append("%s: ficheiro ausente" % fonte)
            continue
        t = texto_do_pdf(caminho)
        if not t:
            tentados.append("%s: pdftotext nao leu" % fonte)
            continue
        item = {"id": "%s::portao" % fonte, "texto": t, "source_id": fonte,
                "artifact_type": "DERIVED", "parent_sha256": "a" * 64}
        d = admissao.decidir(item, UNIVERSO, corrida=RUN)
        tentados.append("%s: %s" % (fonte, d.resultado))
        if d.resultado == admissao.SIM:
            escolhido, texto, decisao = fonte, t, d
            break

    _mede("CANARIOS_TENTADOS", " · ".join(tentados), "")
    _mede("ADMISSION_DECISION_CANARIO",
          getattr(decisao, "resultado", "NENHUM"), escolhido or "")
    caso("C1_um_canario_italiano_real_entra_com_SIM",
         decisao is not None and decisao.resultado == admissao.SIM,
         "nenhum dos %d candidatos deu SIM: %s" % (len(CANDIDATOS), tentados))
    if decisao is None:
        _falhar()

    # ⚠️ E O CONTROLO NEGATIVO, NA MESMA CORRIDA.
    # Uma porta que so diz SIM nao e uma porta. O fixture de midia da C4H
    # continua a NAO ser admissivel, e isso e a VERDADE — nao um defeito a
    # corrigir com uma regra nova.
    d_nao = admissao.decidir(
        {"id": "controlo::mercado", "artifact_type": "DERIVED",
         "parent_sha256": "b" * 64, "source_id": "IT-PROVA",
         "texto": ("I prezzi del grano duro sulla piazza di Foggia risultano "
                   "stabili; il mercato registra volumi in lieve aumento.")},
        UNIVERSO, corrida=RUN)
    _mede("CONTROLO_NEGATIVO", d_nao.resultado, "texto de mercado em T3")
    caso("C2_a_porta_continua_a_recusar_o_que_nao_serve",
         d_nao.resultado != admissao.SIM,
         "o texto de mercado entrou em T3: a regua afrouxou")

    # ── D · O READY REAL, E A POUSAGEM ────────────────────────────────────
    print("\nD · O READY, E A SALA")
    # A observacao e REAL: escreve-se um `raw_asset` para o canario e usa-se o
    # `id` que o banco devolveu. Nunca se inventa `RAW_OBSERVATION_ID`.
    raw_id = _observacao_do_canario(sql, url, escolhido, texto)
    _mede("RAW_OBSERVATION_ID", raw_id, "raw_asset.id lido do banco")

    item_pronto = {"id": "%s::portao" % escolhido, "texto": texto,
                   "source_id": escolhido, "artifact_type": "DERIVED",
                   "parent_sha256": "a" * 64,
                   "raw_asset_id": raw_id,
                   "captured_at": "2026-09-14T20:00:00Z",
                   "published_at": "2026-09-07T00:00:00Z",
                   "observed_at": "2026-09-14T20:00:00Z"}
    d2 = admissao.decidir(item_pronto, UNIVERSO, corrida=RUN)
    caso("D0_o_item_com_observacao_continua_a_entrar",
         d2.resultado == admissao.SIM, "deu %s" % d2.resultado)

    pronto = admissao.pronto_para_inteligencia(item_pronto, d2)
    _mede("READY_FIELD_COUNT", len(pronto), "contado no objeto produzido")
    caso("D1_o_READY_sai_com_19_campos", len(pronto) == 19,
         "saiu com %d: %s" % (len(pronto), sorted(pronto)))
    caso("D2_o_READY_leva_a_observacao_e_nao_NAO_SEI",
         pronto["RAW_OBSERVATION_ID"] == raw_id,
         "RAW_OBSERVATION_ID=%r" % pronto["RAW_OBSERVATION_ID"])
    caso("D3_o_READY_declara_quem_o_admitiu",
         bool(pronto.get("ADMITIDO_POR")) and "v" in str(pronto["ADMITIDO_POR"]),
         "ADMITIDO_POR=%r" % pronto.get("ADMITIDO_POR"))

    recibo = espera.pousar(RUN, [pronto])
    _mede("SALA_BACKEND", recibo["BACKEND"], "canonico=%s" % recibo["CANONICO"])
    _mede("SALA_ESTADO", recibo["ESTADO"], recibo["PORQUE"])
    caso("D4_a_sala_que_recebeu_e_a_CANONICA", recibo["CANONICO"] is True,
         "backend=%s" % recibo["BACKEND"])
    caso("D5_a_unidade_POUSOU", recibo["ESTADO"] == espera.POUSOU,
         "estado=%s" % recibo["ESTADO"])

    # ⚠️ E AGORA A LINHA, NA TABELA. `pousar` devolveu um recibo; um recibo e
    # uma afirmacao de quem escreveu.
    n = int(sql.executa(
        "select count(*) from public.sala_de_espera where run_id = %s"
        % _lit(RUN))[0][0])
    _mede("WAITING_ROWS", n, "contadas na tabela, nao no recibo")
    caso("D6_ha_UMA_linha_na_sala_para_esta_corrida", n == 1,
         "%d linhas" % n)

    # ── E · A DURABILIDADE, NOUTRO PROCESSO ───────────────────────────────
    print("\nE · O PROCESSO ESCRITOR MORRE, E A LINHA FICA")
    # ⚠️ UMA EXCECAO AQUI NAO PODE MATAR A PROVA EM SILENCIO.
    # Foi o que aconteceu na primeira corrida: a seccao imprimiu o titulo e o
    # processo morreu com codigo 1, sem uma linha a dizer porque. O relatorio
    # gravado ficou sem a seccao inteira.
    #
    #     UMA PROVA QUE REBENTA NAO MEDIU NADA, E TEM DE O DIZER.
    try:
        lido = _ler_noutro_processo(url)
    except Exception as e:                                     # noqa: BLE001
        lido = {"ENCONTRADO": False,
                "ERRO": "a propria leitura rebentou: %r" % (e,)}
    _mede("READY_EXISTS_AFTER_PROCESS_EXIT", lido.get("ENCONTRADO"),
          "lido pelo dono canonico, noutro interpretador")
    _mede("LEITURA_CAMPOS", lido.get("CAMPOS"), "")
    caso("E1_outro_processo_ve_o_READY", lido.get("ENCONTRADO") is True,
         lido.get("ERRO") or "nao encontrou a corrida")
    caso("E2_o_READY_lido_tem_19_campos", lido.get("CAMPOS") == 19,
         "leu %s campos" % lido.get("CAMPOS"))
    caso("E3_a_linhagem_fecha_do_outro_lado",
         str(lido.get("RAW_OBSERVATION_ID")) == str(raw_id)
         and lido.get("CORRIDA") == RUN
         and lido.get("SOURCE_ID") == escolhido,
         "obs=%s corrida=%s fonte=%s" % (lido.get("RAW_OBSERVATION_ID"),
                                         lido.get("CORRIDA"),
                                         lido.get("SOURCE_ID")))
    caso("E4_o_leitor_usou_o_dono_canonico_e_nao_SQL_por_fora",
         lido.get("VIA") == "sala_de_espera.ler",
         "via=%s" % lido.get("VIA"))

    _gravar()
    return 1 if FALHAS else 0


def _lit(v):
    return "'" + str(v).replace("'", "''") + "'"


def _observacao_do_canario(sql, url, fonte, texto):
    """Um `raw_asset` REAL para o canario, pelo dono do bruto.

    ⚠️ NAO SE INVENTA `RAW_OBSERVATION_ID`. O id sai do banco depois de a
    linha existir — `bigserial`, e nao um numero escolhido aqui.
    """
    from guarda.preservar_coleta import ArmazemDeMentira, preservar, sha256
    banco = _pg.MemoriaPostgres(url)
    corrida = {"RUN_ID": RUN, "PLATFORM": "web", "ACTOR": "portao-big-collection",
               "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT",
               "MISSION": "C-GATE-BIG-COLLECTION-01",
               "STARTED_AT": "2026-09-14T20:00:00Z",
               "RULE_VERSION": "v1", "CAPTURE_METHOD": "LOCAL_REPROCESS"}
    bytes_ = texto.encode("utf-8")
    artefato = {"COUNTRY": "IT", "SOURCE_SLUG": fonte, "SOURCE_ID": fonte,
                "DOCUMENT_ID": "GATE:DOC:1", "ARTIFACT_KIND": "DOCUMENT",
                "NAME": "%s.txt" % fonte, "SOURCE_NATIVE_ID": "GATE-1",
                "SHA256": sha256(bytes_), "BYTES": len(bytes_),
                "MEDIA_TYPE": "text/plain",
                "CAPTURED_AT": "2026-09-14T20:00:00Z",
                "SOURCE_URL": "https://exemplo.it/%s" % fonte}
    preservar(corrida, [artefato], ArmazemDeMentira(), lambda o: bytes_,
              memoria=banco, terminou_em="2026-09-14T20:01:00Z")
    return int(banco._valor(
        "select id from public.raw_asset where run_id = %s" % _lit(RUN)))


def _ler_noutro_processo(url):
    """Abre um interpretador NOVO e pergunta ao dono canonico da Sala.

    ⚠️ NAO SE CONSULTA A TABELA POR FORA. `sala_de_espera.ler()` e o dono da
    pergunta «o que esta pousado nesta corrida?». Fazer `select` aqui mediria
    o Postgres, e nao a Sala — e no dia em que o dono mudasse de forma de
    guardar, esta prova continuaria verde sobre uma casa vazia.

        PERGUNTAR A TABELA NAO E PERGUNTAR AO DONO.
    """
    # ⚠️ ESTE CODIGO NAO PASSA POR `%`, E A RAZAO E UM DEFEITO MEDIDO.
    # A primeira versao interpolava a raiz com `... % (RAIZ, RAIZ, RAIZ, RUN)`
    # — e o proprio texto do programa tinha um `%r` la dentro, numa mensagem de
    # erro. A formatacao de fora comeu-o, e o processo leitor rebentou ANTES de
    # correr, com a seccao E a morrer sem imprimir uma linha.
    #
    #     UM TEMPLATE QUE FORMATA CODIGO COMPETE COM O CODIGO PELOS MESMOS
    #     SIMBOLOS, E QUEM PERDE E SEMPRE O DEPURADOR.
    #
    # Os dois valores entram por `json.dumps`, que e o que ja se usa para os
    # atravessar de volta.
    codigo = """
import json, os, sys
RAIZ = json.loads(os.environ["PORTAO_RAIZ"])
RUN  = json.loads(os.environ["PORTAO_RUN"])
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, os.path.join(RAIZ, 'admissao'))
import _gavetas
import sala_de_espera as espera
try:
    u = espera.ler(RUN)
except Exception as e:
    print(json.dumps({'ENCONTRADO': False, 'ERRO': repr(e)}))
    raise SystemExit(0)
if not u:
    print(json.dumps({'ENCONTRADO': False, 'VIA': 'sala_de_espera.ler',
                      'ERRO': 'ler() devolveu vazio'}))
    raise SystemExit(0)
itens = u.get('ITENS') if isinstance(u, dict) else u
if not isinstance(itens, list) or not itens:
    print(json.dumps({'ENCONTRADO': False, 'VIA': 'sala_de_espera.ler',
                      'ERRO': 'ler() nao trouxe ITENS',
                      'CHAVES': sorted(u) if isinstance(u, dict) else str(type(u))}))
    raise SystemExit(0)
p = itens[0]
print(json.dumps({'ENCONTRADO': True, 'VIA': 'sala_de_espera.ler',
                  'CAMPOS': len(p),
                  'RAW_OBSERVATION_ID': p.get('RAW_OBSERVATION_ID'),
                  'CORRIDA': p.get('CORRIDA'),
                  'SOURCE_ID': p.get('SOURCE_ID'),
                  'ESTADO': p.get('ESTADO')}, default=str))
"""
    amb = dict(os.environ)
    amb["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    amb["SINTONIA_SALA_DSN"] = url
    amb["PORTAO_RAIZ"] = json.dumps(RAIZ)
    amb["PORTAO_RUN"] = json.dumps(RUN)
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True,
                       text=True, env=amb)
    linha = (r.stdout or "").strip().splitlines()
    if not linha:
        return {"ENCONTRADO": False,
                "ERRO": "o processo leitor nao escreveu nada: %s"
                        % ((r.stderr or "").strip()[-400:] or "sem stderr")}
    try:
        return json.loads(linha[-1])
    except Exception:                                          # noqa: BLE001
        return {"ENCONTRADO": False,
                "ERRO": "saida ilegivel: %s" % linha[-1][:200]}


def _gravar():
    estado = {
        "SCHEMA": "portao-big-collection/v1",
        "O_QUE_ISTO_E": ("Se existe um READY DE VERDADE na Sala, lido de outro "
                         "processo pelo dono canonico — e nao so uma etapa "
                         "READY registada."),
        "COMO_REFAZER": "python3 provas/o_portao_da_big_collection.py",
        "A_LEI": ("ETAPA REGISTADA != UNIDADE PRODUZIDA · "
                  "MODULO EXISTE != LINHA EXISTE · CAN DO != DID DO"),
        "MEDIDO": medido, "PASSOU": PASSOU, "FALHAS": FALHAS,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    io.open(SAIDA, "w", encoding="utf-8").write(
        json.dumps(estado, ensure_ascii=False, indent=1, default=str) + "\n")
    print("\n  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
    print("\nPORTAO_BIG_COLLECTION = %s · %d passaram · %d falharam"
          % ("PROVADO" if not FALHAS else "FALHOU", len(PASSOU), len(FALHAS)))


def _falhar():
    _gravar()
    raise SystemExit(1)


if __name__ == "__main__":
    raise SystemExit(main())
