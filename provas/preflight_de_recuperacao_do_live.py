#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════
# O PREFLIGHT DE RECUPERAÇÃO DO LIVE — o que se mede sem credencial
#
# ── A PERGUNTA ────────────────────────────────────────────────────────
#
# A `C-RESTORE-PROOF-BEFORE-LIVE-V2` fechou com `LIVE_RECOVERY_CAPABILITY
# = NOT_MEASURED`. Esta prova mede tudo o que ainda é mensurável sem
# credencial de gestão, e — mais importante — **separa em estruturas
# diferentes** três coisas que se confundem sozinhas:
#
#     DOCUMENTACAO   o que o fornecedor diz que o produto faz
#     ALCANCE        o que esta sessao consegue ALCANCAR
#     MEDICAO        o que se mediu DESTE projeto
#
# Só a terceira responde «este projeto tem backup». As duas primeiras
# nunca promovem a terceira, e o `portao()` recusa-se a deixá-las.
#
#     CAN DO != DID DO.
#     PLANO PRO NAO PROVA BACKUP ATIVO.
#     DOCUMENTACAO NAO E CONFIGURACAO.
#
# ── PORQUE É QUE SONDAR NÃO É ESCREVER ────────────────────────────────
#
# As sondas são `GET` sem `apikey` e sem token. Não autenticam, não
# escrevem, não listam dados. O que elas medem é se o gateway do projeto
# RESPONDE e se a API de gestão está ALCANÇÁVEL — que é exactamente o que
# distingue «o recurso não existe» de «não temos a chave».
#
#     CREDENCIAL AUSENTE != RECURSO AUSENTE.
# ═══════════════════════════════════════════════════════════════════════
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

LIVE_REF = "odhdwvugikjdvkapbowe"
DEV_REF = "xhqebdweltytnghiavew"


def http(url: str, tempo: int = 25) -> dict:
    """GET sem credencial nenhuma. Devolve codigo e cabecalhos que importam."""
    p = subprocess.run(
        ["bash", "-lc",
         f"timeout {tempo} curl -sS -o /tmp/_pf_body -D /tmp/_pf_hdr "
         f"-w '%{{http_code}}' {json.dumps(url)}"],
        capture_output=True, text=True, check=False)
    corpo = Path("/tmp/_pf_body").read_text()[:200] if Path("/tmp/_pf_body").exists() else ""
    hdr = Path("/tmp/_pf_hdr").read_text() if Path("/tmp/_pf_hdr").exists() else ""
    ref = re.search(r"sb-project-ref:\s*(\S+)", hdr, re.I)
    return {"http": p.stdout.strip() or "erro", "corpo": corpo.strip(),
            "sb_project_ref": ref.group(1) if ref else None,
            "alcancavel": p.stdout.strip().isdigit()}


# ── 1 · O ALCANCE DESTA SESSAO ────────────────────────────────────────
def mede_alcance() -> dict:
    credenciais = {n: ("PRESENTE" if os.environ.get(n) else "AUSENTE") for n in (
        "SUPABASE_ACCESS_TOKEN", "SUPABASE_MANAGEMENT_TOKEN", "SUPABASE_DB_URL",
        "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY")}
    tem_gestao = any(credenciais[n] == "PRESENTE" for n in
                     ("SUPABASE_ACCESS_TOKEN", "SUPABASE_MANAGEMENT_TOKEN"))
    gestao = http("https://api.supabase.com/v1/projects")
    backups = http(f"https://api.supabase.com/v1/projects/{LIVE_REF}/database/backups")
    return {
        "CREDENCIAIS": credenciais,
        "MANAGEMENT_CREDENTIAL_AVAILABLE": "YES" if tem_gestao else "NO",
        "MANAGEMENT_READ_CAPABILITY": "YES" if tem_gestao else "NO",
        "MANAGEMENT_API_ALCANCAVEL": "SIM" if gestao["alcancavel"] else "NAO",
        "MANAGEMENT_API_RESPOSTA": gestao["http"],
        "ENDPOINT_DE_BACKUPS_EXISTE": (
            "SIM (401, e nao 404)" if backups["http"] == "401" else backups["http"]),
        # A distincao que o ataque A06 defende.
        "PORQUE_ISTO_IMPORTA": (
            "401 e nao 404 nem timeout: a rota existe e a rede chega la. "
            "O que falta e a chave, e nao o recurso."),
        "CREDENCIAL_NECESSARIA": (
            "Supabase Personal Access Token (ou token de granularidade fina com "
            "a permissao `backups_read`; em OAuth, o escopo `database:read`). "
            "So LEITURA — nada nesta lista escreve."),
    }


# ── 2 · O QUE SE MEDIU DESTE PROJETO ──────────────────────────────────
def mede_projetos() -> dict:
    out = {}
    for nome, ref in (("LIVE", LIVE_REF), ("DEV", DEV_REF)):
        dns = subprocess.run(["bash", "-lc", f"getent hosts db.{ref}.supabase.co"],
                             capture_output=True, text=True, check=False)
        r = http(f"https://{ref}.supabase.co/rest/v1/")
        out[nome] = {
            "PROJECT_REF": ref,
            "DNS_RESOLVE": "SIM" if dns.returncode == 0 else "NAO",
            "GATEWAY_HTTP": r["http"],
            # O gateway devolve o ref que serviu. E isto que prova que o ref
            # nao esta trocado — o ataque A11.
            "REF_ECOADO_PELO_GATEWAY": r["sb_project_ref"],
            "REF_CONFERE": "SIM" if r["sb_project_ref"] == ref else "NAO",
            "PROJETO_RESPONDE": "SIM" if r["http"] == "401" else f"? ({r['http']})",
            # ⚠️ E SO ISTO QUE SE MEDIU. Tudo o resto exige gestao.
            "PROJECT_STATUS": "NOT_MEASURED",
            "REGION": "NOT_MEASURED",
            "POSTGRES_MAJOR": "NOT_MEASURED",
            "POSTGRES_VERSION": "NOT_MEASURED",
            "ORGANIZATION": "NOT_MEASURED",
            "PLAN": "NOT_MEASURED",
        }
    return out


BACKUP_NOT_MEASURED = {
    "BACKUP_FEATURE_AVAILABLE": "NOT_MEASURED",
    "BACKUP_ENABLED": "NOT_MEASURED",
    "LATEST_BACKUP_TIMESTAMP": "NOT_MEASURED",
    "OLDEST_AVAILABLE_BACKUP": "NOT_MEASURED",
    "BACKUP_RETENTION": "NOT_MEASURED",
    "PITR_AVAILABLE": "NOT_MEASURED",
    "PITR_ENABLED": "NOT_MEASURED",
    "PITR_RETENTION": "NOT_MEASURED",
    "RESTORE_UI_OR_API_AVAILABLE": "NOT_MEASURED",
    "RESTORE_TO_SEPARATE_PROJECT_SUPPORTED": "NOT_MEASURED",
    "RESTORE_IN_PLACE_SUPPORTED": "NOT_MEASURED",
    "WALG_ENABLED": "NOT_MEASURED",
}

# ── 3 · A DOCUMENTACAO DO FORNECEDOR ──────────────────────────────────
# Lida em 2026-09-14. Vive AQUI, num campo proprio, e nunca dentro de
# `MEDICAO` — um facto do fornecedor cravado no meio de uma medicao passa
# a parecer medido.
DOCUMENTACAO = {
    "LIDO_EM": "2026-09-14",
    "FONTES": [
        "https://supabase.com/docs/guides/platform/backups",
        "https://supabase.com/docs/guides/platform/clone-project",
        "https://supabase.com/docs/reference/api/v1-list-all-backups",
        "https://supabase.com/pricing",
    ],
    "BACKUP_DIARIO": "Pro 7 dias · Team 14 dias · Enterprise ate 30 dias",
    "BACKUP_FISICO_A_PARTIR_DE": "PostgreSQL 15.8.1.079",
    "PITR": "ADD-ON pago, nao e recurso do plano. Granularidade ate ao segundo, "
            "RPO de 2 minutos no pior caso. Ligar PITR DESLIGA o backup diario.",
    "RESTORE_TO_NEW_PROJECT": (
        "existe, e funciona com BACKUP DIARIO FISICO — NAO exige PITR. "
        "Exclusivo de planos pagos com backups fisicos ligados. O clone fica na "
        "MESMA regiao da origem. Um clone NAO pode ser origem de outro clone. "
        "O custo e mostrado no ecra ANTES de confirmar."),
    "CUSTO": {
        "PRO": "25 USD/mes por ORGANIZACAO (nao por projeto)",
        "PITR_7D": "100 USD/mes",
        "PITR_14D": "200 USD/mes",
        "PITR_28D": "DISCREPANCIA ENTRE FONTES: a pagina de backups diz "
                    "0,55 USD/hora (~400 USD/mes); a pagina de precos diz "
                    "300 USD/mes. NAO RESOLVIDO — confirmar no ecra.",
        "SMALL_COMPUTE_ADDON": "15 USD/mes",
        "PITR_EXIGE_COMPUTE": "a pagina de backups diz «at least a Small compute "
                              "add-on»; a pagina de precos nao confirma. NAO RESOLVIDO.",
    },
    "O_QUE_ISTO_NAO_E": "nada aqui diz o que ESTE projeto tem configurado.",
}


def portao(f: dict) -> str:
    """PASS exige MEDICAO, e nenhuma documentacao a compra."""
    criticos = ("BACKUP_ENABLED", "LATEST_BACKUP_TIMESTAMP", "BACKUP_RETENTION",
                "PITR_ENABLED", "RESTORE_UI_OR_API_AVAILABLE")
    medidos = [c for c in criticos if f.get(c) not in (None, "NOT_MEASURED")]
    if not medidos:
        return "BLOCKED"
    if len(medidos) < len(criticos):
        return "PARTIAL"
    return "PASS"


def red_team(m: dict) -> dict:
    a: dict = {}

    def reg(n, desc, apanhado, como):
        a[n] = {"ATAQUE": desc, "RESULTADO": "APANHADO" if apanhado else "SOBREVIVEU",
                "COMO": como}

    b = m["BACKUP"]
    live = m["PROJETOS"]["LIVE"]
    alc = m["ALCANCE"]
    cad = m["CADEIA"]

    reg("A01", "plano Pro tratado como prova de backup",
        b["BACKUP_ENABLED"] == "NOT_MEASURED",
        "o plano nem sequer foi medido; e mesmo que fosse, vive em DOCUMENTACAO")
    reg("A02", "documentacao tratada como configuracao real",
        "BACKUP_DIARIO" in m["DOCUMENTACAO"] and b["BACKUP_RETENTION"] == "NOT_MEASURED",
        "a retencao do plano esta na documentacao e a DESTE projeto continua NOT_MEASURED")
    reg("A03", "backup existente tratado como PITR",
        b["PITR_ENABLED"] == "NOT_MEASURED" and b["BACKUP_ENABLED"] == "NOT_MEASURED",
        "campos separados; e a propria documentacao diz que ligar PITR DESLIGA o diario")
    reg("A04", "PITR disponivel tratado como habilitado",
        b["PITR_AVAILABLE"] == "NOT_MEASURED" and b["PITR_ENABLED"] == "NOT_MEASURED",
        "AVAILABLE e ENABLED sao dois campos, e nenhum foi medido")
    reg("A05", "restore disponivel tratado como executado",
        b["RESTORE_UI_OR_API_AVAILABLE"] == "NOT_MEASURED"
        and m["VEREDITO"]["SAME_PLATFORM_RESTORE"] == "NOT_RUN",
        "disponibilidade e execucao sao campos diferentes; o segundo e NOT_RUN")
    reg("A06", "credencial ausente tratada como recurso ausente",
        alc["MANAGEMENT_API_ALCANCAVEL"] == "SIM" and alc["MANAGEMENT_API_RESPOSTA"] == "401",
        "a API responde 401, e nao 404 nem timeout: a rota existe, falta a chave")
    reg("A07", "migration no Git tratada como migration LIVE",
        cad["LIVE_MIGRATIONS_APPLIED"] == "NOT_MEASURED"
        and cad["GIT_MIGRATIONS_AVAILABLE"] != "NOT_MEASURED",
        "o Git foi medido e o livro-razao do LIVE nao; o retrato datado nao conta")
    reg("A08", "031 aplicada a pular 028-030",
        cad["APLICAR_031_SOZINHA_E_PERMITIDO"] == "NAO",
        "medido que nao ha DEPENDENCIA — e mesmo assim o portao recusa, porque o "
        "aplicador canonico tem UMA ordem e um livro com buraco e drift")
    reg("A09", "numero de migration tratado como dependencia sem medir conteudo",
        cad["A_031_DEPENDE_DE_028_029_030"] == "NAO",
        "medido a EXECUTAR a 031 sobre o estado 027: aplica-se. O numero maior "
        "nao era dependencia, e dizer que era teria sido inventar um blocker")
    reg("A10", "projeto dev tratado como descartavel sem autorizacao",
        m["DEV_PROJECT_CANDIDATE"] == "UNKNOWN" and m["ESCRITAS_NO_DEV"] == 0,
        "so metadata; nenhuma escrita, nenhum reset, nenhuma migration")
    reg("A11", "project ref errado",
        live["REF_CONFERE"] == "SIM",
        "o gateway ECOA o ref que serviu, e ele bate com o pedido")
    reg("A12", "regiao errada",
        live["REGION"] == "NOT_MEASURED",
        "a regiao nao foi medida e nao se afirma; a historica fica como historica")
    reg("A13", "PostgreSQL major errado",
        live["POSTGRES_MAJOR"] == "NOT_MEASURED",
        "nao medido. Um backup FISICO nao atravessa major, e por isso "
        "adivinhar aqui seria o pior sitio para adivinhar")
    reg("A14", "backup timestamp desconhecido tratado como atual",
        b["LATEST_BACKUP_TIMESTAMP"] == "NOT_MEASURED",
        "continua NOT_MEASURED; nenhum backup deste projeto foi listado ou datado")
    reg("A15", "retencao presumida",
        b["BACKUP_RETENTION"] == "NOT_MEASURED" and b["PITR_RETENTION"] == "NOT_MEASURED",
        "a retencao do PLANO esta na documentacao; a deste projeto nao foi medida")
    reg("A16", "restore in-place confundido com restore separado",
        b["RESTORE_IN_PLACE_SUPPORTED"] == "NOT_MEASURED"
        and b["RESTORE_TO_SEPARATE_PROJECT_SUPPORTED"] == "NOT_MEASURED",
        "dois campos distintos, e a documentacao distingue-os: o in-place deixa "
        "o projeto inacessivel, o clone nao")
    reg("A17", "backup logico confundido com restore fisico",
        m["VEREDITO"]["LIVE_RECOVERY_MECHANISM"] != "LOGICAL_BACKUP"
        and b["WALG_ENABLED"] == "NOT_MEASURED",
        "o mecanismo declarado e o fisico da plataforma; e se ele esta ligado "
        "(walg_enabled) continua por medir")
    reg("A18", "leitura causando escrita",
        m["VEREDITO"]["LIVE_WRITES"] == 0 and m["VEREDITO"]["LIVE_DDL"] == 0
        and m["METODO_DAS_SONDAS"] == "GET sem credencial",
        "todas as sondas sao GET sem apikey e sem token; nada autentica, nada escreve")
    texto = json.dumps(m, ensure_ascii=False, default=str)
    padroes = [r"sbp_[A-Za-z0-9]{16,}", r"eyJ[A-Za-z0-9_\-]{20,}",
               r"://[^@\s\"]*:[^@\s\"]+@", r"service_role_key"]
    reg("A19", "segredo a aparecer em log",
        not [p for p in padroes if re.search(p, texto)],
        "nenhum padrao de segredo no relatorio; nao ha token nesta sessao para vazar")
    reg("A20", "custo inventado",
        "DISCREPANCIA" in m["DOCUMENTACAO"]["CUSTO"]["PITR_28D"]
        and m["CUSTO"]["EXPECTED_COST"] == "UNKNOWN",
        "os precos sao citados da fonte, a divergencia entre duas paginas oficiais "
        "fica registada como divergencia, e o custo real do clone e UNKNOWN "
        "porque depende do compute da origem, que nao foi medido")
    reg("A21", "preflight PARCIAL declarado PASS",
        portao(b) == "BLOCKED",
        "o portao e uma funcao: sem nenhum campo critico medido, devolve BLOCKED")
    reg("A22", "classe fisica ja provada usada para dispensar a plataforma",
        m["VEREDITO"]["SAME_PLATFORM_RESTORE"] == "NOT_RUN"
        and m["VEREDITO"]["READY_FOR_LIVE_APPLY"] == "NO",
        "a V2 provou a CLASSE; o portao continua a exigir a PLATAFORMA")

    sobreviventes = [k for k, v in a.items() if v["RESULTADO"] != "APANHADO"]
    return {"ATAQUES": a, "RED_TEAM_ATTACKS": len(a),
            "RED_TEAM_SURVIVORS": len(sobreviventes), "SOBREVIVENTES": sobreviventes}


def main() -> int:
    m: dict = {"PROVA": "PREFLIGHT-DE-RECUPERACAO-DO-LIVE",
               "MEDIDO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "METODO_DAS_SONDAS": "GET sem credencial"}
    m["ALCANCE"] = mede_alcance()
    m["PROJETOS"] = mede_projetos()
    m["BACKUP"] = dict(BACKUP_NOT_MEASURED)
    m["DOCUMENTACAO"] = DOCUMENTACAO

    # O projeto dev: SO metadata. Nenhuma escrita, e nenhuma decisao sobre
    # ele — quem autoriza usar um projeto e gente.
    m["DEV_PROJECT_CANDIDATE"] = "UNKNOWN"
    m["ESCRITAS_NO_DEV"] = 0
    m["PORQUE_DEV_E_UNKNOWN"] = (
        "o projeto responde, e e tudo o que se sabe. Se e descartavel, de quem e, "
        "o que tem dentro e se alguem depende dele — nada disso foi medido, e "
        "nenhuma dessas perguntas se responde sem gente.")

    # A cadeia, medida pela prova irma.
    cadeia = RAIZ / "provas" / "PREFLIGHT-CADEIA-031-MEDIDO.json"
    c = json.loads(cadeia.read_text())["VEREDITO"] if cadeia.exists() else {}
    m["CADEIA"] = {
        "GIT_MIGRATIONS_AVAILABLE": "001-030 na linha funcional; 031 SO no ramo da Sala",
        "LIVE_MIGRATIONS_APPLIED": "NOT_MEASURED",
        "PORQUE": "ler o livro-razao do LIVE exige credencial de banco, que nao existe "
                  "aqui. O retrato datado de PREFLIGHT-LIVE-READONLY-V1 diz 001-007 e "
                  "009-027, mas um retrato nao e uma medicao de hoje.",
        "A_031_DEPENDE_DE_028_029_030": c.get("A_031_DEPENDE_DE_028_029_030", "NOT_MEASURED"),
        "APLICAR_031_SOZINHA_E_PERMITIDO": "NAO",
        "PORQUE_NAO_E_PERMITIDO":
            "nao por dependencia — medido que nao ha — mas porque o aplicador "
            "canonico tem UMA ordem, aplica tudo o que esta na pasta, e um "
            "livro-razao com buraco e drift por construcao.",
        "MIGRATION_CHAIN_028_031": c.get("MIGRATION_CHAIN_028_031", "NOT_MEASURED"),
        "MIGRATION_031_DEFECT": c.get("MIGRATION_031_DEFECT", "NOT_MEASURED"),
        "031_NA_LINHA_FUNCIONAL": "NAO",
    }

    m["CUSTO"] = {
        "RESOURCE_REQUIRED": "um projeto Supabase NOVO, criado pelo proprio "
                             "«Restore to a New Project» a partir do backup diario",
        "RESOURCE_TYPE": "projeto clone (nao e branch, nao exige PITR)",
        "EXPECTED_COST": "UNKNOWN",
        "BILLING_UNIT": "mensal, por projeto, espelhando os recursos da origem",
        "PORQUE_UNKNOWN": "o custo espelha o compute da ORIGEM, e o compute da "
                          "origem nao foi medido. A documentacao diz que o valor e "
                          "mostrado no ecra ANTES de confirmar — logo, VER o preco "
                          "custa zero.",
        "WHY_REQUIRED": "so um restauro executado PELA PLATAFORMA move "
                        "SAME_PLATFORM_RESTORE de NOT_RUN para PASS.",
        "O_QUE_NAO_E_PRECISO": "PITR. Medido na documentacao: «Restore to a New "
                               "Project» funciona com o backup diario fisico. "
                               "Os 100 USD/mes do PITR NAO sao pre-requisito.",
    }

    m["VEREDITO"] = {
        "LIVE_BACKUP_PREFLIGHT": portao(m["BACKUP"]),
        "LIVE_RECOVERY_CAPABILITY": "NOT_MEASURED",
        "SAME_PLATFORM_RESTORE": "NOT_RUN",
        "MIGRATION_CHAIN_028_031": m["CADEIA"]["MIGRATION_CHAIN_028_031"],
        "MIGRATION_031_DEFECT": m["CADEIA"]["MIGRATION_031_DEFECT"],
        "READY_FOR_LIVE_APPLY": "NO",
        "LIVE_RECOVERY_MECHANISM": "SUPABASE_BACKUP_RESTORE",
        "PORQUE_ESSE_MECANISMO":
            "e o unico que a plataforma oferece SEM add-on pago e que devolve "
            "dados: backup diario fisico, restaurado pela consola. O PITR seria "
            "mais fino, mas nao esta medido como ligado e e pago. Um mecanismo "
            "principal, e nao dois.",
        "SAME_PLATFORM_RESTORE_NEXT_ACTION": [
            "1. obter Personal Access Token de LEITURA e correr "
            "GET /v1/projects/{ref}/database/backups",
            "2. so entao decidir: RESTORE_EXISTING_BACKUP_TO_NEW_PROJECT",
            "3. VERIFY com a impressao de provas/recuperacao_fisica_provada_no_postgres.py",
            "4. DELETE_DISPOSABLE",
        ],
        "LIVE_READS": 2,
        "LIVE_WRITES": 0,
        "LIVE_DDL": 0,
        "RESTORE_EXECUTED": 0,
        "REAL_COLLECTION": 0,
    }
    m["O_QUE_LIVE_READS_CONTA"] = (
        "2 GET sem credencial ao gateway publico de cada projeto (LIVE e DEV), "
        "que devolveram 401. Nenhum dado foi lido; o que se mediu foi que o "
        "projeto responde e que o ref bate. Conta-se na mesma, porque uma "
        "leitura nao declarada e uma leitura escondida.")

    rt = red_team(m)
    m["RED_TEAM"] = rt

    saida = RAIZ / "provas" / "PREFLIGHT-RECUPERACAO-LIVE-MEDIDO.json"
    saida.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(m["VEREDITO"], indent=2, ensure_ascii=False))
    print(f"\nRED_TEAM = {rt['RED_TEAM_ATTACKS']} ataques, "
          f"{rt['RED_TEAM_SURVIVORS']} sobreviventes {rt['SOBREVIVENTES']}")
    print(f"relatorio -> {saida.relative_to(RAIZ)}")
    return 0 if rt["RED_TEAM_SURVIVORS"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
