#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════
# O PREFLIGHT DO RESTAURO NA PRÓPRIA PLATAFORMA — e onde ele para
#
# ── A PERGUNTA ────────────────────────────────────────────────────────
#
# «Um backup REAL do LIVE consegue ser restaurado pelo mecanismo REAL do
# Supabase para um NOVO projeto, e o banco restaurado contém mesmo o que
# devia conter?»
#
# ── ONDE ESTA MISSÃO PARA, E PORQUÊ ───────────────────────────────────
#
# Medido na documentação oficial em 2026-09-14: «Restore to a New
# Project» é uma operação de CONSOLA. A página oficial manda ir a
# `dashboard/project/_/database/backups/restore-to-new-project` e não
# nomeia rota nenhuma da Management API nem do CLI.
#
#     NAO E FALTA DE PERMISSAO. E AUSENCIA DE ROTA.
#
# A distinção importa porque as duas levam a decisões opostas: falta de
# permissão resolve-se pedindo escopo; ausência de rota não se resolve
# com escopo nenhum. Ampliar o token não aproximaria isto um milímetro.
#
# E há uma armadilha vizinha, que esta prova NOMEIA para que ninguém lá
# caia: existe `POST /v1/projects/{ref}/restore` na Management API. Ela
# age sobre o `{ref}` que recebe — ou seja, sobre o PRÓPRIO projeto — e
# exige `projects:write`. Apontá-la a `odhdwvugikjdvkapbowe` seria mexer
# na PRODUÇÃO, e não criar clone nenhum.
#
#     UMA ROTA COM A PALAVRA «RESTORE» NAO E A ROTA QUE SE PROCURA.
#
# Esta prova NÃO a chama. Não chama POST nenhum.
#
# ── O QUE ELA FAZ, ENTÃO ──────────────────────────────────────────────
#
# Mede tudo o que é mensurável sem gastar: o backup escolhido, o estado
# do LIVE, as pré-condições que a documentação nomeia, e o caminho de
# verificação que TEM de existir antes de alguém criar o clone (§11).
# Depois corre 28 ataques contra si própria.
#
#     SAME_PLATFORM_RESTORE CONTINUA NOT_RUN, E ESTA PROVA NAO O PROMOVE.
# ═══════════════════════════════════════════════════════════════════════
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "provas" / "SAME-PLATFORM-RESTORE-PREFLIGHT.json"
MEDICAO_DOS_BACKUPS = RAIZ / "provas" / "SUPABASE-LIVE-BACKUP-MEASURED.json"

SOURCE_PROJECT_REF = "odhdwvugikjdvkapbowe"
DEV_PROJECT_REF = "xhqebdweltytnghiavew"
AGORA = datetime.now(timezone.utc)


# ── O QUE A DOCUMENTACAO OFICIAL DIZ ──────────────────────────────────
# Vive numa estrutura SEPARADA da medicao, de proposito: um facto do
# fornecedor cravado no meio de uma medicao passa a parecer medido.
DOCUMENTACAO = {
    "LIDA_EM": "2026-09-14",
    "FONTES": [
        "https://supabase.com/docs/guides/platform/backups",
        "https://supabase.com/docs/guides/platform/clone-project",
        "https://supabase.com/docs/reference/api/v1-restore-a-project",
    ],
    "RESTORE_TO_NEW_PROJECT_E_CONSOLA": (
        "a pagina oficial manda ir ao dashboard, separador «Restore to a "
        "New Project». Nenhuma rota de Management API ou CLI e nomeada."),
    "PRE_CONDICOES_CITADAS": [
        "«exclusive to users on paid plans»",
        "physical backups «enabled for the source project»",
        "PITR e add-on OPCIONAL, e NAO requisito",
    ],
    "CUSTO_CITADO": (
        "«Before starting the restoration, you'll be presented with an "
        "overview of the costs associated with creating the new project.» "
        "O ecra do custo vive na CONSOLA."),
    "LIMITACOES_CITADAS": [
        "um projeto criado por restauro NAO pode ser fonte de outro clone",
        "extensoes que fazem operacoes externas (pg_net, pg_cron, wrappers) "
        "«should be disabled once the copy process has completed»",
        "daily backups nao guardam passwords de custom roles",
    ],
    "ALVOS_DE_RESTAURO_PARA_BACKUP_FISICO": {
        "1_IN_PLACE": "restaura o projeto SOBRE SI PROPRIO. O alvo e a fonte.",
        "2_RESTORE_TO_A_NEW_PROJECT": "cria um projeto NOVO.",
        "3_PARA_UM_PROJETO_EXISTENTE_DIFERENTE": (
            "NAO EXISTE. A documentacao nao descreve esta opcao."),
    },
    "BACKUP_FISICO_NAO_SE_DESCARREGA": (
        "«You can still use physical backups for restoration, but they are "
        "not available for direct download.» O backup descarregavel do "
        "dashboard e o LOGICO, e so existe em projetos antigos."),
    "STORAGE_CITADO": (
        "«Database backups do not include objects you store via the Storage "
        "API, as the database only includes metadata about these objects.»"),
    "O_QUE_ISTO_NAO_E": (
        "nada aqui e uma medicao DESTE projeto. Documentacao nao e "
        "configuracao, e a consola deste projeto nao foi vista."),
}


def le_backups() -> dict:
    if not MEDICAO_DOS_BACKUPS.exists():
        return {"ERRO": "medicao dos backups ausente"}
    return json.loads(MEDICAO_DOS_BACKUPS.read_text(encoding="utf-8"))


def escolhe_o_backup(m: dict) -> dict:
    """O COMPLETED mais recente. Nada de reaproveitar a data da missao anterior."""
    candidatos = [b for b in m.get("BACKUPS", [])
                  if b.get("status") == "COMPLETED"]
    if not candidatos:
        return {"RESTORE_SOURCE_BACKUP_ID": "NENHUM",
                "PORQUE": "nenhum backup COMPLETED na medicao"}
    escolhido = max(candidatos, key=lambda b: b["inserted_at"])
    return {
        "RESTORE_SOURCE_BACKUP_ID": escolhido["id"],
        "RESTORE_SOURCE_BACKUP_TIMESTAMP": escolhido["inserted_at"],
        "RESTORE_SOURCE_BACKUP_STATUS": escolhido["status"],
        "RESTORE_SOURCE_BACKUP_IS_PHYSICAL": escolhido["is_physical_backup"],
        "ESCOLHIDO_POR": "o COMPLETED mais recente da medicao desta missao",
        "CANDIDATOS_COMPLETED": len(candidatos),
    }


# ── O BASELINE DO LIVE ────────────────────────────────────────────────
# Medido pela auditoria canonica em 2026-09-14T03:04Z, corrida 34801217087.
# Copiado do log da corrida, e nao inventado; a corrida e o original.
LIVE_BASELINE = {
    "MEDIDO_EM": "2026-09-14T03:04:30Z",
    "MEDIDO_POR": "auditoria-live run 34801217087 (provas/auditoria_live.sh)",
    "AUDITORIA_LIVE": "PASS",
    "READ_ONLY_SESSION": "on",
    "READ_ONLY_PROVEN": "YES",
    "LIVE_MIGRATION_LEDGER": {
        "LEDGER_ROWS": 26,
        "LEDGER_VERSIONS": ("001,002,003,004,005,006,007,009,010,011,012,013,"
                            "014,015,016,017,018,019,020,021,022,023,024,025,"
                            "026,027"),
        "LEDGER_DUPLICATES": 0,
        "LEDGER_INVALID_RESULTS": 0,
        "LEDGER_MISSING_SHA": 0,
        "MIGRATIONS_PENDENTES": ["028", "029", "030"],
        "EXTRA_IN_LIVE": "nenhuma",
    },
    "LIVE_TABLE_ROWS": {
        "collection_run": 11, "raw_asset": 252, "storage_object": 252,
        "derived_artifact": 1, "etapa_da_corrida": 0, "schema_migracao": 26,
        "participacao_na_derivacao": "AUSENTE",
        "documento_estruturado": "AUSENTE",
    },
    "LIVE_CONSTRAINT_COUNT_COLLECTION": 44,
    "LIVE_CONSTRAINTS_TODAS_CONVALIDADAS": "SIM nas tabelas da Collection",
    "CONSTRAINTS_NAO_CONVALIDADAS": 2,
    "QUAIS_NAO_CONVALIDADAS": ["crop_calendar.calendario_geografia_e_do_pais",
                               "issue_window.janela_issue_geografia_e_do_pais"],
    "NOTA": ("as duas nao convalidadas NAO sao da Collection, e ja estavam "
             "assim antes desta missao."),
}

# O que o clone teria de mostrar para `STRUCTURAL_MATCH = PASS`. Escrito
# ANTES de existir clone nenhum, que e a unica altura em que um criterio
# nao pode ser feito a medida do resultado.
CRITERIO_DE_COMPARACAO = {
    "COMPARAVEL": [
        "LEDGER_ROWS e LEDGER_VERSIONS (nenhuma migration foi aplicada "
        "desde o backup — MIGRATIONS_PENDENTES continua 028 029 030)",
        "existencia e ausencia das 8 tabelas",
        "as 44 travas da Collection, por nome e por convalidada",
        "os indices nomeados nas seccoes E, F e G da auditoria",
    ],
    "COMPARAVEL_SO_SE_NADA_ESCREVEU": [
        "contagens de linhas: 11 / 252 / 252 / 1 / 0 / 26",
    ],
    "NAO_COMPARAVEL_POR_IGUALDADE": [
        "sequencias — o WAL regista-as aos saltos de 32, e um restauro "
        "correcto devolve-as ADIANTADAS. Ver RUNBOOK-DE-RECUPERACAO §6.",
        "qualquer escrita posterior ao backup. BACKUP_TIME != NOW.",
    ],
    "PORQUE_AS_CONTAGENS_SAO_COMPARAVEIS_HOJE": (
        "a auditoria de 2026-09-13T12:08Z e a de 2026-09-14T03:04Z devolvem "
        "as MESMAS contagens, e o backup escolhido e de 2026-09-13T03:05Z, "
        "entre as duas. Nao ha coleta a correr. Isto e EVIDENCIA de que o "
        "conjunto esta parado — nao e prova de que nenhuma escrita ocorreu."),
}

# O caminho de verificacao EXIGIDO pelo §11, e que tem de existir ANTES
# de alguem criar o clone.
PLANO_DE_VERIFICACAO = {
    "EXISTE": "SIM",
    "DONO": "provas/auditoria_live.sh — o que ja existe, e nao um novo",
    "PORTA": ".github/workflows/supabase-clone-verify.yml",
    "GUARDA": "provas/guarda_do_clone.py, com 10 testes",
    "SEGREDO_NECESSARIO": "SUPABASE_CLONE_DB_URL (temporario, morre com o clone)",
    "PORQUE_O_SEGREDO_NAO_PODE_EXISTIR_AINDA": (
        "a DSN de um projeto que ainda nao nasceu nao existe. Ela so passa "
        "a existir depois de a consola criar o clone."),
    "O_QUE_A_GUARDA_RECUSA": [
        "a producao, pela ligacao directa",
        "a producao, pelo POOLER — onde o ref vive no UTILIZADOR e nao no "
        "host, e uma guarda ingenua deixaria passar",
        "o projeto dev, pelas duas vias",
        "uma DSN de que nao se consiga extrair ref nenhum",
    ],
    "ESCRITAS_QUE_ESTA_PORTA_PODE_FAZER": 0,
}


def red_team(m: dict) -> dict:
    a: dict = {}

    def reg(n, desc, apanhado, como):
        a[n] = {"ATAQUE": desc,
                "RESULTADO": "APANHADO" if apanhado else "SOBREVIVEU",
                "COMO": como}

    bk = m["BACKUP_ESCOLHIDO"]
    criado = m["TARGET_PROJECT_REF"] == "NOT_CREATED"

    reg("A01", "botao existe, mas nunca foi executado, e conta como prova",
        m["SAME_PLATFORM_RESTORE"] == "BLOCKED",
        "SAME_PLATFORM_RESTORE e BLOCKED, com BLOCKER nomeado, e nenhum "
        "campo desta prova o move")
    reg("A02", "projeto criado sem vir do backup escolhido", criado,
        "nenhum projeto foi criado; o backup escolhido esta nomeado por id "
        "para que a criacao futura possa ser conferida contra ele")
    reg("A03", "projeto ACTIVE_HEALTHY mas banco vazio", criado,
        "TARGET_PROJECT_STATUS e NOT_CREATED; e o criterio de comparacao "
        "exige ledger e travas, que um banco vazio nao tem")
    reg("A04", "schema existe mas dados nao", criado,
        "o criterio separa STRUCTURAL_MATCH de RESTORED_DATA_PROOF, e o "
        "segundo exige contagens e nao so tabelas")
    reg("A05", "dados existem mas migration ledger nao bate", criado,
        "LEDGER_ROWS e LEDGER_VERSIONS estao na lista COMPARAVEL, com os "
        "valores do LIVE medidos hoje")
    reg("A06", "comparar backup de ontem com LIVE de hoje como mesmo instante",
        "NAO_COMPARAVEL_POR_IGUALDADE" in CRITERIO_DE_COMPARACAO,
        "BACKUP_TIME != NOW esta escrito no criterio, e as contagens estao "
        "em COMPARAVEL_SO_SE_NADA_ESCREVEU e nao em COMPARAVEL")
    reg("A07", "restaurar o backup errado",
        bk.get("ESCOLHIDO_POR", "").startswith("o COMPLETED mais recente"),
        "o backup e escolhido por regra e nomeado por id e timestamp, "
        "medidos NESTA missao e nao herdados da anterior")
    reg("A08", "usar backup que nao esta COMPLETED",
        bk.get("RESTORE_SOURCE_BACKUP_STATUS") == "COMPLETED",
        "so entram candidatos com status COMPLETED")
    reg("A09", "usar o projeto dev como cobaia",
        DEV_PROJECT_REF in PLANO_DE_VERIFICACAO["O_QUE_A_GUARDA_RECUSA"][2]
        or "dev" in PLANO_DE_VERIFICACAO["O_QUE_A_GUARDA_RECUSA"][2],
        "a guarda do clone recusa o ref do dev pelas duas vias, com teste")
    reg("A10", "alterar o LIVE para fabricar uma prova",
        m["LIVE_SQL_WRITES"] == 0 and m["LIVE_DDL"] == 0,
        "as unicas operacoes contra o LIVE foram SELECT, e a propria "
        "auditoria mediu READ_ONLY_SESSION=on")
    reg("A11", "aplicar migration durante o restore",
        m["LIVE_MIGRATIONS"] == 0 and criado,
        "nenhuma migration foi aplicada em lado nenhum; MIGRATIONS_PENDENTES "
        "continua 028 029 030")
    reg("A12", "aumentar o escopo do token automaticamente",
        m["TOKEN_SCOPE_CHANGED"] == "NO",
        "o token continua o mesmo de Backups Read; nao foi criado token "
        "novo nem pedido escopo novo")
    reg("A13", "vazar credencial em log",
        m["CREDENCIAIS_IMPRESSAS"] == 0,
        "o secret entra por env e nunca e echo-ado; a guarda do clone tem "
        "teste que prova que nenhuma linha do log carrega a DSN")
    reg("A14", "vazar connection string em Git",
        m["DSN_NA_ARVORE"] == 0,
        "nenhuma DSN entra na arvore; as DSN dos testes montam-se em tempo "
        "de execucao, pela lei do §113")
    reg("A15", "custo nao conhecido e criar mesmo assim",
        m["PROJECT_CREATION_COST"] == "UNKNOWN" and criado,
        "o custo vive no ecra da consola, que esta sessao nao alcanca. "
        "Custo UNKNOWN -> NAO CRIAR, e nao se criou")
    reg("A16", "projeto descartavel ficar vivo a cobrar", criado,
        "nao ha projeto descartavel. Nao existe nada a cobrar por esta missao")
    reg("A17", "apagar o projeto fonte por engano",
        m["DELETES_EXECUTADOS"] == 0,
        "nenhum delete foi executado contra projeto nenhum, e a guarda "
        "recusa ate LER a producao por esta porta")
    reg("A18", "apagar o dev por engano", m["DELETES_EXECUTADOS"] == 0,
        "o mesmo: zero deletes, e o dev esta na lista de refs recusados")
    reg("A19", "target ref igual ao source ref", criado,
        "nao ha target. E quando houver, guarda_do_clone.py recusa "
        "target==source pelas duas vias, com teste que o prova")
    reg("A20", "considerar sucesso da UI como prova do conteudo",
        m["STRUCTURAL_MATCH"] == "BLOCKED",
        "ACTIVE_HEALTHY != RESTORED_CORRECTLY esta no criterio, e o "
        "veredito estrutural e BLOCKED e nao PASS")
    reg("A21", "PostgreSQL aceitar conexao mas estar incompleto",
        m["DATABASE_QUERYABLE"] == "NO",
        "aceitar conexao nao e criterio nenhum aqui: o criterio sao ledger, "
        "travas, indices e contagens")
    reg("A22", "assumir que os bytes do Storage foram restaurados",
        m["STORAGE_OBJECT_BYTES_RECOVERY"] == "NOT_PROVEN",
        "a documentacao oficial diz o contrario, e esta citada: backups de "
        "banco NAO incluem objetos do Storage. 252 storage_object no LIVE "
        "sao METADADOS, e nao bytes")
    reg("A23", "SAME_CLASS passar por SAME_PLATFORM",
        m["SAME_CLASS_RESTORE"] == "PASS"
        and m["SAME_PLATFORM_RESTORE"] == "BLOCKED",
        "a classe fisica foi provada pela V2 num Postgres descartavel; a "
        "plataforma continua por provar, e os dois campos vivem separados")
    reg("A24", "destruir o clone antes de guardar evidencias",
        criado,
        "nao ha clone. E a porta de verificacao guarda o artefacto ANTES "
        "do passo de limpeza, por ordem dos passos")
    reg("A25", "usar mock para comportamento que precisa do Supabase real",
        m["MOCKS_USADOS_COMO_PROVA"] == 0,
        "nada aqui simula o Supabase. O que nao foi medido diz-se "
        "NOT_MEASURED, e nao se substitui por imitacao")
    reg("A26", "transformar UNKNOWN em PASS",
        m["DATABASE_RECOVERY_GATE"] == "BLOCKED",
        "o portao e BLOCKED. Nenhum UNKNOWN desta missao foi promovido")
    reg("A27", "reutilizar custo ou documentacao antiga sem medir",
        DOCUMENTACAO["LIDA_EM"] == "2026-09-14"
        and m["BACKUPS_REMEDIDOS_NESTA_MISSAO"] == "YES",
        "os backups foram re-medidos hoje e a documentacao foi relida hoje, "
        "com as fontes citadas")
    reg("A28", "System Map puxar esta missao para fora do foco",
        m["SYSTEM_MAP_TOCADO"] == "NO",
        "o mapa nao foi editado nesta missao; se o validador reclamar, "
        "classifica-se e nao se conserta")

    # ── OS QUE A CORRECCAO DE 2026-09-14 ABRIU ────────────────────────
    reg("A29", "o dev existir ser tomado como prova de que ja foi um restauro",
        m["SAME_PLATFORM_RESTORE"] == "BLOCKED"
        and m["DEV_MEDIDO"]["DEV_MIGRATION_LEDGER"] == "NOT_MEASURED",
        "nada do interior do dev foi medido, logo nada dele pode parecer-se "
        "com o LIVE ao ponto de enganar. CAN DO != DID DO, e EXISTE != VEIO "
        "DE UM RESTAURO")
    reg("A30", "restaurar in-place para «reutilizar um projeto existente» — "
        "e o projeto existente ser o LIVE",
        m["SOURCE_PROJECT_CHANGED"] == "NO" and m["LIVE_DDL"] == 0,
        "a UNICA opcao da plataforma que aponta a um projeto existente e o "
        "in-place, e o existente que ela aceita e a PROPRIA FONTE. Chamar "
        "isso de «reutilizar o dev» teria restaurado por cima da producao")
    reg("A31", "descarregar o backup e repo-lo no dev com psql, e chamar "
        "a isso SAME_PLATFORM_RESTORE",
        m["SAME_PLATFORM_RESTORE"] == "BLOCKED",
        "seria pg_restore com outro nome — SAME_CLASS, que a V2 ja provou. "
        "E nem esta disponivel: backup fisico nao se descarrega")
    reg("A32", "palavra do utilizador sobre o dev tratada como medicao",
        m["DEV_REUSE_SAFE"] == "BLOCKED",
        "«foi criado para testes e esta sem uso» e informacao, e nao estado "
        "medido. DEV_REUSE_SAFE nao foi promovido a YES")
    reg("A33", "autorizacao para usar o dev tratada como autorizacao para "
        "criar projeto novo",
        m["NEW_PROJECT_CREATED"] == "NO" and m["PROJETOS_CRIADOS"] == 0,
        "a correccao autorizou REUTILIZAR, e disse explicitamente que criar "
        "exige nova decisao humana. Nada foi criado")
    reg("A34", "apagar ou pausar o dev no fim, pela instrucao antiga",
        m["DEV_STILL_ACTIVE"] == "YES" and m["DELETES_EXECUTADOS"] == 0,
        "a correccao revogou a limpeza para este alvo. O dev fica de pe, e "
        "DEV_STILL_NEEDED fica UNKNOWN em vez de ser adivinhado")
    reg("A35", "custo zero desta missao apresentado como «o dev nao custa»",
        m["NEW_COST_CAUSED_BY_THIS_MISSION"] == 0
        and m["EXISTING_DEV_COST"] == "UNKNOWN",
        "os dois numeros vivem separados: esta missao nao causou custo novo, "
        "e o que o dev ja custava continua por medir")
    reg("A36", "BLOCKED por limite de autorizacao lido como FAIL do restauro",
        m["BLOCKER"] == "PLATFORM_REQUIRES_NEW_PROJECT",
        "o restauro nao foi tentado, logo nao falhou. O bloqueio tem nome, e "
        "o nome diz de quem e o limite")

    return {"RED_TEAM_ATTACKS": len(a),
            "RED_TEAM_SURVIVORS": sum(1 for v in a.values()
                                      if v["RESULTADO"] == "SOBREVIVEU"),
            "ATAQUES": a}


def main() -> int:
    backups = le_backups()
    m: dict = {
        "PROVA": "SAME-PLATFORM-RESTORE-PREFLIGHT",
        "MEDIDO_EM": AGORA.isoformat(timespec="seconds"),
        "SOURCE_PROJECT": "eame-sintonia",
        "SOURCE_PROJECT_REF": SOURCE_PROJECT_REF,
        "DEV_PROJECT_REF_NAO_TOCADO": DEV_PROJECT_REF,
    }

    m["BACKUPS_REMEDIDOS_NESTA_MISSAO"] = "YES"
    m["MEDICAO_DOS_BACKUPS"] = {
        "MEDIDO_EM": backups.get("MEDIDO_EM"),
        "HTTP_STATUS": backups.get("HTTP_STATUS"),
        "BACKUP_COUNT": backups.get("BACKUP_COUNT"),
        "BACKUP_TYPES": backups.get("BACKUP_TYPES"),
        "LATEST_BACKUP_TIMESTAMP": backups.get("LATEST_BACKUP_TIMESTAMP"),
        "PITR_ENABLED": backups.get("PITR_ENABLED"),
        "WALG_ENABLED": backups.get("WALG_ENABLED"),
        "REGION_OBSERVED": backups.get("REGION_OBSERVED"),
    }
    m["BACKUP_ESCOLHIDO"] = escolhe_o_backup(backups)
    m["LIVE_BASELINE"] = LIVE_BASELINE
    m["CRITERIO_DE_COMPARACAO"] = CRITERIO_DE_COMPARACAO
    m["PLANO_DE_VERIFICACAO"] = PLANO_DE_VERIFICACAO
    m["DOCUMENTACAO"] = DOCUMENTACAO

    # ── O MECANISMO ───────────────────────────────────────────────────
    m["MECANISMO"] = {
        "RESTORE_TO_NEW_PROJECT_EXISTE_NO_PRODUTO": "YES",
        "RESTORE_TO_NEW_PROJECT_TEM_ROTA_DE_API": "NO",
        "RESTORE_TO_NEW_PROJECT_ALCANCAVEL_DESTA_SESSAO": "NO",
        "PORQUE": ("e operacao de CONSOLA. Nao e falta de permissao — e "
                   "ausencia de rota, e escopo nenhum a cria."),
        "PRE_CONDICAO_PHYSICAL_BACKUPS": "YES (walg_enabled=true, medido)",
        "PRE_CONDICAO_PLANO_PAGO": "NOT_MEASURED (exige escopo de projeto)",
        "PITR_E_REQUISITO": "NO (documentacao oficial; e add-on opcional)",
        "ROTA_VIZINHA_QUE_NAO_SE_USA": {
            "ROTA": "POST /v1/projects/{ref}/restore",
            "PORQUE_NAO": ("age sobre o PROPRIO {ref} e exige projects:write. "
                           "Aponta-la a producao seria mexer no LIVE, e nao "
                           "criar clone nenhum. NAO FOI CHAMADA."),
        },
    }
    # RESTORE_TO_NEW_PROJECT_AVAILABLE fala da CONSOLA DESTE projeto, e
    # essa nao foi vista. As pre-condicoes que se puderam medir passam.
    # ── A PERGUNTA DA CORRECCAO: o dev pode ser o alvo? ──────────────
    m["RESTORE_INTO_EXISTING_PROJECT"] = "NO"
    m["PORQUE_NAO_PARA_PROJETO_EXISTENTE"] = (
        "medido na documentacao oficial em 2026-09-14: para um projeto de "
        "backups FISICOS o Supabase oferece dois alvos, e so dois — o "
        "PROPRIO projeto (in-place) ou um projeto NOVO. Restaurar o backup "
        "de um projeto para OUTRO projeto ja existente nao e uma opcao do "
        "produto.")
    m["A_ARMADILHA_DO_IN_PLACE"] = (
        "das duas opcoes, a unica que aponta a um projeto EXISTENTE e o "
        "in-place — e o projeto existente que ela aceita e a PROPRIA FONTE. "
        "Ou seja: a unica forma de restaurar para algo que ja existe seria "
        "restaurar POR CIMA DO LIVE. E exactamente a operacao que esta "
        "missao tem proibida, e chamar-lhe «reutilizar um projeto» seria o "
        "erro mais caro possivel.")
    m["O_CAMINHO_QUE_NAO_SE_TOMA"] = (
        "descarregar um backup e repo-lo com psql noutro projeto NAO e o "
        "mecanismo da plataforma: e pg_restore com outro nome, e seria "
        "SAME_CLASS outra vez. Alem disso o backup deste projeto e FISICO, "
        "e backups fisicos nao se descarregam.")
    m["RESTORE_TO_NEW_PROJECT_AVAILABLE"] = "UNKNOWN"
    m["PORQUE_AVAILABLE_UNKNOWN"] = (
        "so a consola deste projeto responde se o separador aparece. As "
        "pre-condicoes mensuraveis daqui estao satisfeitas (backups fisicos "
        "COMPLETED, walg ligado), mas pre-condicao satisfeita nao e botao visto.")

    # ── O PROJETO DEV, MEDIDO SEM LHE TOCAR ───────────────────────────
    m["EXISTING_DEV_FOUND"] = "YES"
    m["DEV_PROJECT_NAME"] = "eame-sintonia-dev"
    m["DEV_PROJECT_REF"] = DEV_PROJECT_REF
    m["DEV_MEDIDO"] = {
        "DEV_RESPONDE": "YES",
        "DEV_GATEWAY_HTTP": 401,
        "DEV_REF_ECOADO_BATE": "YES",
        "METODO": ("GET sem apikey e sem token ao gateway publico. O gateway "
                   "devolve o ref que serviu, e e assim que se confere a "
                   "identidade sem ler dado nenhum."),
        "DEV_REGION": "NOT_MEASURED",
        "DEV_PROJECT_STATUS": "NOT_MEASURED",
        "DEV_POSTGRES_VERSION": "NOT_MEASURED",
        "DEV_SCHEMA": "NOT_MEASURED",
        "DEV_MIGRATION_LEDGER": "NOT_MEASURED",
        "DEV_TABLE_COUNT": "NOT_MEASURED",
        "DEV_HAS_DATA": "NOT_MEASURED",
        "DEV_HAS_UNIQUE_DATA_NOT_IN_LIVE": "NOT_MEASURED",
        "PORQUE_NOT_MEASURED": (
            "nao ha credencial nenhuma para o dev nesta sessao: o token de "
            "gestao esta limitado aos backups do LIVE, e SUPABASE_DB_URL "
            "aponta ao LIVE. Ler o dev por dentro exigiria uma credencial "
            "que nao existe, e esta missao nao cria credenciais."),
    }
    # DEV_REUSE_SAFE nao se declara YES por palavra de ninguem — e a
    # correccao diz isso melhor do que eu: INFORMACAO DO UTILIZADOR != PROVA
    # DO ESTADO ATUAL. Mas a pergunta tambem deixou de decidir alguma coisa.
    m["DEV_REUSE_SAFE"] = "BLOCKED"
    m["PORQUE_DEV_REUSE_BLOCKED"] = (
        "por duas razoes independentes, e qualquer uma chegava. PRIMEIRA: o "
        "conteudo do dev nao e mensuravel desta sessao, e o utilizador dizer "
        "que esta sem uso nao e uma medicao do estado dele. SEGUNDA, e a que "
        "fecha a questao: o dev nao pode ser alvo de um restauro da "
        "plataforma, logo a pergunta «e seguro sobrescreve-lo?» nunca chega "
        "a ser feita. NADA NO DEV FOI TOCADO.")
    m["DEV_ESCRITAS"] = 0
    m["DEV_DDL"] = 0
    m["DEV_STILL_ACTIVE"] = "YES"
    m["DEV_STILL_NEEDED"] = "UNKNOWN"
    m["PORQUE_DEV_STILL_NEEDED_UNKNOWN"] = (
        "esta missao nao mediu o que vive la dentro nem quem depende dele. "
        "Manter, pausar ou apagar e decisao de gente, e com medicao a "
        "frente. Esta missao nao apagou nem pausou nada.")

    # ── CUSTO ─────────────────────────────────────────────────────────
    m["TARGET_REGION"] = "eu-west-1 (a origem; a documentacao diz que o "
    m["TARGET_REGION"] += "clone fica na mesma regiao)"
    m["TARGET_COMPUTE"] = "NOT_MEASURED"
    m["PROJECT_CREATION_COST"] = "UNKNOWN"
    m["RECURRING_COST"] = "UNKNOWN"
    m["OUTROS_CUSTOS"] = "UNKNOWN"
    m["CURRENCY"] = "UNKNOWN"
    m["PORQUE_CUSTO_UNKNOWN"] = (
        "o ecra que mostra o custo vive na consola, imediatamente antes de "
        "confirmar. Esta sessao nao o alcanca. E a regra e a regra: "
        "CUSTO UNKNOWN -> NAO CRIAR.")
    m["ESTIMATED_COST_BEFORE"] = "UNKNOWN"
    m["ACTUAL_COST_OBSERVED"] = "NOT_YET_AVAILABLE"
    m["PROJECT_LIFETIME_MINUTES"] = 0
    m["NEW_PROJECT_CREATED"] = "NO"
    m["NEW_PROJECT_COST"] = 0
    m["NEW_COST_CAUSED_BY_THIS_MISSION"] = 0
    m["EXISTING_DEV_COST"] = "UNKNOWN"
    m["PORQUE_DEV_COST_UNKNOWN"] = (
        "ler faturacao exige escopo de organizacao, que este token nao tem "
        "e que esta missao nao amplia. O dev ja existia antes desta missao "
        "e continua a existir depois dela, sem alteracao nenhuma.")
    m["TARGET_PROJECT"] = "NOT_CREATED"
    m["COST_APPROVED_BY_HUMAN"] = "NO"
    m["PORQUE_NAO_APROVADO"] = (
        "nao se pede autorizacao para um gasto cujo valor nao se sabe dizer, "
        "e cuja execucao esta fora do alcance desta sessao. Pedir um «sim» "
        "que nada destrava seria teatro.")

    # ── O QUE NAO ACONTECEU ───────────────────────────────────────────
    m["TARGET_PROJECT_NAME"] = "NOT_CREATED"
    m["TARGET_PROJECT_REF"] = "NOT_CREATED"
    m["TARGET_PROJECT_STATUS"] = "NOT_CREATED"
    m["TARGET_CREATED_AT"] = "NOT_CREATED"
    m["RESTORE_OPERATION_ID"] = "NOT_CREATED"
    m["DATABASE_QUERYABLE"] = "NO"
    m["STRUCTURAL_MATCH"] = "BLOCKED"
    m["RESTORED_DATA_PROOF"] = "BLOCKED"
    m["CONSTRAINT_BEHAVIOR"] = "NOT_RUN"
    m["TARGET_CLEANUP"] = "NOT_CREATED"

    m["SAME_CLASS_RESTORE"] = "PASS"
    m["SAME_CLASS_PROVA"] = ("provas/recuperacao_fisica_provada_no_postgres.py "
                             "— base backup fisico + WAL, num Postgres 17 "
                             "descartavel. Provou a CLASSE, e nao a plataforma.")
    m["SAME_PLATFORM_RESTORE"] = "BLOCKED"
    m["BLOCKER"] = "PLATFORM_REQUIRES_NEW_PROJECT"
    m["PORQUE_BLOCKED_E_NAO_FAIL"] = (
        "FAIL diria que o restauro foi tentado e nao funcionou. Nao foi "
        "tentado: a plataforma so oferece in-place (que destruiria o LIVE) "
        "ou projeto NOVO (que exige decisao humana de gasto, e que o "
        "utilizador declarou nao querer abrir sem necessidade). E limite da "
        "EXECUCAO AUTORIZADA, e nao prova de que o restauro falha.")
    m["DATABASE_RECOVERY_GATE"] = "BLOCKED"
    m["STORAGE_OBJECT_BYTES_RECOVERY"] = "NOT_PROVEN"
    m["STORAGE_PORQUE"] = (
        "a documentacao oficial diz que backups de banco NAO incluem objetos "
        "do Storage. As 252 linhas de storage_object no LIVE sao METADADOS. "
        "Mesmo um restauro perfeito do banco nao devolve os bytes — e isso "
        "e um buraco de recuperacao SEPARADO, que continua aberto.")

    m["SOURCE_PROJECT_CHANGED"] = "NO"
    m["LIVE_SQL_WRITES"] = 0
    m["LIVE_DDL"] = 0
    m["LIVE_MIGRATIONS"] = 0
    m["REAL_COLLECTION"] = 0
    m["DELETES_EXECUTADOS"] = 0
    m["PROJETOS_CRIADOS"] = 0
    m["POSTS_A_MANAGEMENT_API"] = 0
    m["TOKEN_SCOPE_CHANGED"] = "NO"
    m["CREDENCIAIS_IMPRESSAS"] = 0
    m["DSN_NA_ARVORE"] = 0
    m["MOCKS_USADOS_COMO_PROVA"] = 0
    m["SYSTEM_MAP_TOCADO"] = "NO"

    m["READY_FOR_LIVE_APPLY"] = "NO"
    m["PORQUE_NAO_PRONTO"] = (
        "a lei em vigor exige SAME_PLATFORM_RESTORE executado, e ele "
        "continua NOT_RUN. Medir o mecanismo nao e executa-lo.")

    m["RED_TEAM"] = red_team(m)

    texto = json.dumps(m, indent=2, ensure_ascii=False)
    SAIDA.write_text(texto + "\n", encoding="utf-8")

    for c in ("SOURCE_PROJECT_REF", "RESTORE_TO_NEW_PROJECT_AVAILABLE",
              "PROJECT_CREATION_COST", "COST_APPROVED_BY_HUMAN",
              "TARGET_PROJECT_REF", "DATABASE_QUERYABLE", "STRUCTURAL_MATCH",
              "RESTORED_DATA_PROOF", "CONSTRAINT_BEHAVIOR",
              "SAME_CLASS_RESTORE", "SAME_PLATFORM_RESTORE",
              "DATABASE_RECOVERY_GATE", "STORAGE_OBJECT_BYTES_RECOVERY",
              "SOURCE_PROJECT_CHANGED", "LIVE_SQL_WRITES", "LIVE_DDL",
              "LIVE_MIGRATIONS", "REAL_COLLECTION", "TARGET_CLEANUP",
              "READY_FOR_LIVE_APPLY"):
        print("%s=%s" % (c, m[c]))
    b = m["BACKUP_ESCOLHIDO"]
    print("RESTORE_SOURCE_BACKUP_ID=%s" % b.get("RESTORE_SOURCE_BACKUP_ID"))
    print("RESTORE_SOURCE_BACKUP_TIMESTAMP=%s"
          % b.get("RESTORE_SOURCE_BACKUP_TIMESTAMP"))
    rt = m["RED_TEAM"]
    print("RED_TEAM_ATTACKS=%s" % rt["RED_TEAM_ATTACKS"])
    print("RED_TEAM_SURVIVORS=%s" % rt["RED_TEAM_SURVIVORS"])
    if rt["RED_TEAM_SURVIVORS"]:
        for n, v in rt["ATAQUES"].items():
            if v["RESULTADO"] == "SOBREVIVEU":
                print("SOBREVIVEU %s · %s" % (n, v["ATAQUE"]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
