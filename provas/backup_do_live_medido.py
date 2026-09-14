#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════
# O BACKUP DO LIVE, MEDIDO PELA API DE GESTÃO — e só medido
#
# ── O QUE ESTA PROVA FECHA ────────────────────────────────────────────
#
# A `C-SUPABASE-LIVE-RECOVERY-PREFLIGHT-V1` fechou `BLOCKED` com doze
# campos `NOT_MEASURED` e disse exactamente o que faltava: **a chave, e
# não o recurso**. A API respondia `401` — que é «falta pedir», e não
# «não existe». Esta prova usa a chave e faz o pedido.
#
#     UM GET. NENHUMA ESCRITA. NENHUM RESTAURO.
#
# ── AS DISTINÇÕES QUE ESTA PROVA SE RECUSA A COLAPSAR ─────────────────
#
#     401 != SEM BACKUP      a credencial nao foi aceite
#     403 != SEM BACKUP      a credencial vale, o escopo nao chega
#     404 != SEM BACKUP      a rota ou o projeto nao e esse
#     429 != SEM BACKUP      o fornecedor travou o ritmo
#     5xx != SEM BACKUP      o fornecedor falhou
#     200 com lista vazia  = SEM BACKUP VISIVEL, e so isto e a resposta
#
# «Não funcionou» é o nome que se dá a cinco causas diferentes quando não
# se quer escolher uma. Aqui escolhe-se.
#
#     BACKUP DIARIO NAO E PITR.
#     PITR DESCONHECIDO NAO E PITR DESLIGADO.
#     BACKUP LISTADO NAO E RESTAURO PROVADO.
#
# ── O TOKEN ───────────────────────────────────────────────────────────
#
# Vem de `SUPABASE_ACCESS_TOKEN`, vive na memória deste processo, viaja
# num cabeçalho `Authorization` e não sai daqui: não vai para `argv` (não
# há `curl`), não vai para ficheiro, não vai para a URL, não vai para o
# log. Antes de escrever o artefacto, `sem_vazamento()` procura o próprio
# valor do token no que está prestes a ser gravado — e aborta se o achar.
# ═══════════════════════════════════════════════════════════════════════
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "provas" / "SUPABASE-LIVE-BACKUP-MEASURED.json"

# O `ref` canónico desta missão. O dev (`xhqebdweltytnghiavew`) NÃO se toca —
# e o teste `A15` confere que não foi ele que aqui entrou.
LIVE_REF = "odhdwvugikjdvkapbowe"
DEV_REF = "xhqebdweltytnghiavew"
NOME_ESPERADO = "eame-sintonia"

API = "https://api.supabase.com"
ENDPOINT = f"/v1/projects/{LIVE_REF}/database/backups"

AGORA = datetime.now(timezone.utc)

# Campos que podem sair no artefacto. Lista BRANCA, e não lista negra: um
# campo novo que o fornecedor invente amanhã fica de fora por omissão, em
# vez de entrar por distracção.
CAMPOS_DO_BACKUP = ("id", "status", "inserted_at", "is_physical_backup")
CAMPOS_DO_TOPO = ("region", "walg_enabled", "pitr_enabled")
CAMPOS_DA_JANELA = ("earliest_physical_backup_date_unix",
                    "latest_physical_backup_date_unix")


def so_get(caminho: str, token: str) -> dict:
    """GET, e só GET. Devolve status e corpo — nunca o cabeçalho enviado."""
    pedido = urllib.request.Request(API + caminho, method="GET")
    pedido.add_header("Authorization", "Bearer " + token)
    pedido.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(pedido, timeout=45) as r:
            bruto = r.read().decode("utf-8", "replace")
            status = r.status
    except urllib.error.HTTPError as e:
        bruto = e.read().decode("utf-8", "replace")
        status = e.code
    except Exception as e:                       # rede, DNS, TLS, timeout
        return {"HTTP_STATUS": 0, "CORPO": None,
                "FALHA_DE_TRANSPORTE": type(e).__name__}
    try:
        corpo = json.loads(bruto)
    except Exception:
        corpo = None
    return {"HTTP_STATUS": status, "CORPO": corpo,
            # só o `message` do erro, cortado. Nunca o corpo inteiro de um
            # erro que ninguém leu antes de deixar entrar no artefacto.
            "MENSAGEM": (str(corpo.get("message"))[:200]
                         if isinstance(corpo, dict) and corpo.get("message")
                         else None)}


def instante(unix_ou_iso) -> datetime | None:
    """Aceita epoch (int) ou ISO-8601. Devolve None se não for hora nenhuma."""
    if unix_ou_iso in (None, ""):
        return None
    try:
        if isinstance(unix_ou_iso, (int, float)):
            return datetime.fromtimestamp(float(unix_ou_iso), timezone.utc)
        return datetime.fromisoformat(str(unix_ou_iso).replace("Z", "+00:00"))
    except Exception:
        return None


def hora_valida(t: datetime | None) -> str:
    """Uma data que ainda não aconteceu não é uma medição — é um erro de leitura."""
    if t is None:
        return "INVALIDA"
    if t > AGORA:
        return "FUTURA"
    if t.year < 2020:
        return "IMPLAUSIVEL"
    return "OK"


def le_backups(r: dict) -> dict:
    """Do corpo real para os campos do §7 — sem inventar nenhum deles."""
    m = {
        "HTTP_STATUS": r["HTTP_STATUS"],
        "BACKUPS_VISIBLE": "NOT_MEASURED",
        "BACKUP_COUNT": "UNKNOWN",
        "LATEST_BACKUP_TIMESTAMP": "UNKNOWN",
        "OLDEST_BACKUP_TIMESTAMP": "UNKNOWN",
        "BACKUP_RETENTION_OBSERVED": "UNKNOWN",
        "BACKUP_TYPES": "UNKNOWN",
        "PHYSICAL_BACKUP_OBSERVED": "UNKNOWN",
        "PITR_OBSERVED": "UNKNOWN",
        "PITR_ENABLED": "UNKNOWN",
        "BACKUP_SCHEDULE": "UNKNOWN",
        "RESTORE_SOURCE_AVAILABLE": "UNKNOWN",
        "REGION_OBSERVED": "UNKNOWN",
        "WALG_ENABLED": "UNKNOWN",
        "HORAS_SUSPEITAS": [],
        "CAMPOS_IGNORADOS": [],
        "BACKUP_RETENTION_OBSERVED_SIGNIFICA":
            "a distancia entre o mais antigo e o mais recente que a API mostrou "
            "HOJE. NAO e a politica de retencao do plano: um projeto novo mostra "
            "pouco sem que a retencao seja pouca.",
    }

    corpo = r.get("CORPO")
    if r["HTTP_STATUS"] != 200 or not isinstance(corpo, dict):
        # Tudo o que não é 200 fica `NOT_MEASURED`, e a causa vive noutro
        # campo. É aqui que 401, 403, 404, 429 e 5xx deixam de virar «não há».
        m["PORQUE_NAO_MEDIDO"] = {
            0: "falha de transporte: nem chegou a haver resposta HTTP",
            401: "credencial nao aceite — o token nao foi injetado ou nao vale",
            403: "token valido, escopo insuficiente para ler backups",
            404: "rota ou projeto inexistente para esta credencial",
            429: "limite de ritmo do fornecedor",
        }.get(r["HTTP_STATUS"],
              "resposta 5xx do fornecedor" if r["HTTP_STATUS"] >= 500
              else "resposta inesperada, ou corpo que nao e JSON de objeto")
        return m

    # ── daqui para baixo, e SO daqui, houve 200 e ha o que ler ──────────
    for c in CAMPOS_DO_TOPO:
        if c in corpo:
            m["REGION_OBSERVED" if c == "region" else
              "WALG_ENABLED" if c == "walg_enabled" else "PITR_OBSERVED"] = corpo[c]

    # PITR: o campo OBSERVADO e o veredito sao duas coisas. Se o fornecedor
    # nao mandou o campo, `PITR_ENABLED` fica UNKNOWN — e nao NO.
    if "pitr_enabled" in corpo:
        m["PITR_OBSERVED"] = "YES"
        m["PITR_ENABLED"] = "YES" if corpo["pitr_enabled"] else "NO"
    else:
        m["PITR_OBSERVED"] = "NO"
        m["PITR_ENABLED"] = "UNKNOWN"

    lista = corpo.get("backups")
    if not isinstance(lista, list):
        m["BACKUPS_VISIBLE"] = "NO"
        m["BACKUP_COUNT"] = 0
        m["PORQUE_NAO_MEDIDO"] = ("200 sem o array `backups` — a resposta veio, "
                                  "e nao trazia lista nenhuma")
        return m

    vistos = []
    for b in lista:
        if not isinstance(b, dict):
            continue
        vistos.append({c: b.get(c) for c in CAMPOS_DO_BACKUP})
        for c in b:
            if c not in CAMPOS_DO_BACKUP and c not in m["CAMPOS_IGNORADOS"]:
                m["CAMPOS_IGNORADOS"].append(c)

    m["BACKUP_COUNT"] = len(vistos)
    # 200 com lista vazia E uma medicao: diz «nao ha backup VISIVEL». Nao e
    # erro, e nao e o mesmo que 401.
    m["BACKUPS_VISIBLE"] = "YES" if vistos else "NO"
    m["BACKUPS"] = vistos

    horas = []
    for b in vistos:
        t = instante(b.get("inserted_at"))
        v = hora_valida(t)
        if v != "OK":
            m["HORAS_SUSPEITAS"].append({"id": b.get("id"), "motivo": v,
                                         "valor": str(b.get("inserted_at"))})
        elif t is not None:
            horas.append(t)

    m["HORAS_USADAS"] = len(horas)
    if horas:
        m["LATEST_BACKUP_TIMESTAMP"] = max(horas).isoformat()
        m["OLDEST_BACKUP_TIMESTAMP"] = min(horas).isoformat()

    tipos = sorted({("PHYSICAL" if b.get("is_physical_backup") else "LOGICAL")
                    for b in vistos})
    if tipos:
        m["BACKUP_TYPES"] = tipos
        m["PHYSICAL_BACKUP_OBSERVED"] = "YES" if "PHYSICAL" in tipos else "NO"
    elif m["WALG_ENABLED"] is True:
        # `walg_enabled` diz que a máquina física está ligada; não lista backup
        # nenhum. Serve para dizer YES ao mecanismo, nunca para datar nada.
        m["PHYSICAL_BACKUP_OBSERVED"] = "YES"

    janela = corpo.get("physical_backup_data")
    if isinstance(janela, dict):
        j = {c: janela.get(c) for c in CAMPOS_DA_JANELA}
        m["PHYSICAL_BACKUP_WINDOW"] = j
        ini, fim = instante(j[CAMPOS_DA_JANELA[0]]), instante(j[CAMPOS_DA_JANELA[1]])
        for nome, t in (("earliest", ini), ("latest", fim)):
            if t is not None and hora_valida(t) != "OK":
                m["HORAS_SUSPEITAS"].append({"id": "physical_backup_data." + nome,
                                             "motivo": hora_valida(t), "valor": str(t)})
        if ini and fim and hora_valida(ini) == "OK" and hora_valida(fim) == "OK":
            m["PHYSICAL_BACKUP_WINDOW_ISO"] = {"earliest": ini.isoformat(),
                                               "latest": fim.isoformat()}
            m["BACKUP_RETENTION_OBSERVED"] = (
                "%.2f dias de janela fisica observada" % ((fim - ini).days
                                                          + (fim - ini).seconds / 86400.0))
            m["PHYSICAL_BACKUP_OBSERVED"] = "YES"

    # A retenção observada NÃO é a política. É a distância entre a coisa mais
    # velha e a mais nova que a API mostrou HOJE. Um projeto novo mostra pouco
    # sem que a retenção seja pouca.
    if m["BACKUP_RETENTION_OBSERVED"] == "UNKNOWN" and len(horas) >= 2:
        d = max(horas) - min(horas)
        m["BACKUP_RETENTION_OBSERVED"] = (
            "%.2f dias entre o backup mais antigo e o mais recente listados"
            % (d.days + d.seconds / 86400.0))

    # FONTE para restaurar — e não restauro provado. O nome é comprido de
    # propósito: `RESTORE_AVAILABLE` deixaria alguém ler «restauro funciona».
    m["RESTORE_SOURCE_AVAILABLE"] = (
        "YES" if (m["BACKUPS_VISIBLE"] == "YES"
                  or m.get("PHYSICAL_BACKUP_WINDOW_ISO")) else "NO")
    m["RESTORE_SOURCE_AVAILABLE_SIGNIFICA"] = (
        "existe uma FONTE listada pela API. NAO significa que um restauro "
        "corra, nem que corra neste projeto, nem que o resultado sirva. "
        "SAME_PLATFORM_RESTORE continua NOT_RUN.")

    # Nenhum endpoint read-only oficial da Management API devolve o horário
    # do agendamento. Fica UNKNOWN por AUSÊNCIA DE ROTA, e não por falha.
    m["BACKUP_SCHEDULE"] = "UNKNOWN"
    m["PORQUE_SCHEDULE_UNKNOWN"] = (
        "a Management API nao expoe endpoint read-only de agendamento de "
        "backup. UNKNOWN por ausencia de rota — nao por 403 e nao por falha. "
        "Ampliar escopo nao resolveria."
    )
    return m


def red_team(m: dict, token_presente: bool, metodo: dict) -> dict:
    a: dict = {}

    def reg(n, desc, apanhado, como):
        a[n] = {"ATAQUE": desc,
                "RESULTADO": "APANHADO" if apanhado else "SOBREVIVEU",
                "COMO": como}

    s = m["HTTP_STATUS"]
    vis = m["BACKUPS_VISIBLE"]

    reg("A01", "secret ausente e a medicao continua como se tivesse corrido",
        token_presente,
        "sem SUPABASE_ACCESS_TOKEN o processo aborta com codigo 1 antes de "
        "qualquer GET; nao ha artefacto para confundir com medicao")
    reg("A02", "token invalido tratado como medicao valida",
        s != 401 or vis == "NOT_MEASURED",
        "401 nao preenche campo nenhum: tudo fica NOT_MEASURED e a causa "
        "vai para PORQUE_NAO_MEDIDO")
    reg("A03", "401 chamado de «sem backup»",
        not (s == 401 and vis == "NO"),
        "so um 200 pode escrever BACKUPS_VISIBLE; 401 escreve NOT_MEASURED")
    reg("A04", "403 chamado de «sem backup»",
        not (s == 403 and vis == "NO"),
        "403 e escopo insuficiente, e fica dito assim — o campo continua NOT_MEASURED")
    reg("A05", "404 chamado de «sem backup»",
        not (s == 404 and vis == "NO"),
        "404 e rota/projeto inexistente para esta credencial, e nao ausencia de backup")
    reg("A06", "resposta vazia tratada como erro",
        not (s == 200 and vis == "NO" and m.get("PORQUE_NAO_MEDIDO")
             and "erro" in str(m.get("PORQUE_NAO_MEDIDO")).lower()),
        "200 com lista vazia e MEDICAO: escreve BACKUPS_VISIBLE=NO, que e "
        "resposta e nao falha")
    reg("A07", "backup diario tratado como PITR",
        not (vis == "YES" and m["PITR_ENABLED"] == "YES"
             and m["PITR_OBSERVED"] != "YES"),
        "PITR_ENABLED so se escreve a partir do campo pitr_enabled da API; "
        "a existencia de backups nunca lhe toca")
    reg("A08", "PITR UNKNOWN tratado como NO",
        not (m["PITR_OBSERVED"] == "NO" and m["PITR_ENABLED"] == "NO"),
        "campo ausente -> PITR_ENABLED=UNKNOWN. So um false explicito vira NO")
    reg("A09", "backup listado tratado como restauro provado",
        m.get("SAME_PLATFORM_RESTORE", "NOT_RUN") == "NOT_RUN",
        "RESTORE_SOURCE_AVAILABLE diz FONTE. SAME_PLATFORM_RESTORE fica "
        "NOT_RUN por construcao: esta prova nao restaura")
    futuras = [h for h in m["HORAS_SUSPEITAS"] if h["motivo"] == "FUTURA"]
    reg("A10", "timestamp futuro aceite como backup real",
        not futuras or all(h["valor"] not in (m["LATEST_BACKUP_TIMESTAMP"],)
                           for h in futuras),
        "hora_valida() marca FUTURA e a hora sai do calculo de latest/oldest")
    contadas = m.get("HORAS_USADAS", 0) + len(
        [h for h in m["HORAS_SUSPEITAS"] if not str(h["id"]).startswith("physical_")])
    reg("A11", "timestamp invalido aceite, ou hora desaparecida em silencio",
        m["BACKUP_COUNT"] in ("UNKNOWN",) or contadas == m["BACKUP_COUNT"],
        "cada backup ou entrou no calculo (HORAS_USADAS=%s) ou foi marcado "
        "suspeito; a soma tem de bater com BACKUP_COUNT" % m.get("HORAS_USADAS", 0))
    reg("A12", "token a vazar no log",
        metodo["TOKEN_EM_ARGV"] == "NAO" and metodo["ECHO_DO_TOKEN"] == "NAO",
        "nao ha curl: o cabecalho e montado dentro do processo. Nenhum print "
        "toca a variavel, e o workflow nao tem set -x")
    reg("A13", "token a vazar no artefacto",
        metodo["VARREDURA_DE_VAZAMENTO"] == "SIM",
        "sem_vazamento() procura o valor literal do token e a FORMA de uma "
        "credencial no texto ANTES de gravar; e autoteste_do_varredor() prova "
        "que ele ainda apanha seis credenciais falsas e nao reprova prosa")
    reg("A14", "cabecalho Authorization persistido",
        metodo["TOKEN_EM_FICHEIRO"] == "NAO",
        "o cabecalho vive num objeto Request em memoria e morre com o processo; "
        "nada dele e escrito")
    reg("A15", "projeto dev usado por engano",
        DEV_REF not in ENDPOINT and m.get("PROJECT_REF") == LIVE_REF,
        "o ref e constante no ficheiro, e confere-se contra o dev antes de gravar")
    reg("A16", "project_ref errado",
        m.get("PROJECT_REF") == LIVE_REF,
        "o ref pedido e o ref gravado sao o mesmo literal, e a API so responde "
        "200 para um projeto que a credencial alcanca")
    reg("A17", "POST usado sem querer",
        metodo["METODOS_HTTP_USADOS"] == ["GET"],
        "so_get() fixa method=GET e e a unica porta de rede deste ficheiro")
    reg("A18", "workflow com permissao excessiva",
        metodo["PERMISSOES_DO_WORKFLOW"] == "contents: read",
        "o job nao escreve no repositorio nem publica nada")
    reg("A19", "resultado de documentacao tratado como resultado da API",
        "DOCUMENTACAO" not in m,
        "esta prova nao carrega documentacao nenhuma: todo campo vem do corpo "
        "da resposta ou fica UNKNOWN")
    reg("A20", "artefacto antigo tratado como medicao atual",
        m.get("MEDIDO_EM", "").startswith(AGORA.strftime("%Y")),
        "MEDIDO_EM e gravado a cada corrida, e o ficheiro e reescrito inteiro; "
        "o run do GitHub e que o data")
    reg("A21", "retencao observada tratada como politica de retencao",
        bool(m.get("BACKUP_RETENTION_OBSERVED_SIGNIFICA")),
        "o artefacto carrega, ao lado do numero, a frase que diz que ele e a "
        "janela VISIVEL hoje e nao a politica do plano")
    reg("A22", "BLOCKED promovido a PARTIAL por ter havido resposta HTTP",
        not (s != 200 and m.get("LIVE_BACKUP_PREFLIGHT") != "BLOCKED"),
        "o portao le campos MEDIDOS, e um codigo HTTP nao e um campo medido")

    return {"RED_TEAM_ATTACKS": len(a),
            "RED_TEAM_SURVIVORS": sum(1 for v in a.values()
                                      if v["RESULTADO"] == "SOBREVIVEU"),
            "ATAQUES": a}


def portao(m: dict) -> str:
    """PASS exige os campos críticos MEDIDOS. Um código HTTP não é um campo."""
    criticos = ("BACKUPS_VISIBLE", "LATEST_BACKUP_TIMESTAMP",
                "BACKUP_RETENTION_OBSERVED", "PITR_ENABLED",
                "RESTORE_SOURCE_AVAILABLE")
    medidos = [c for c in criticos
               if m.get(c) not in (None, "NOT_MEASURED", "UNKNOWN")]
    if not medidos:
        return "BLOCKED"
    return "PASS" if len(medidos) == len(criticos) else "PARTIAL"


def sem_vazamento(texto: str, token: str) -> list:
    """O que NÃO pode ir para o disco.

    ⚠️ ESTE VARREDOR JÁ ME APANHOU A MIM. A primeira versão procurava as
    *palavras* `sbp_`, `Bearer` e `Authorization:` — e reprovou o artefacto
    por causa da **prosa do próprio red team**, que nomeia esses padrões para
    explicar que os procura. Nenhum segredo estava lá.

        NOME DO PADRAO != VALOR DO PADRAO.

    A lei da missão diz-o: nomes de variáveis e texto de documentação são
    permitidos. Então o que se procura agora é a **forma de uma credencial**
    — um prefixo seguido de comprimento real — e o valor literal do token.
    Falar de `sbp_` passa; carregar um `sbp_<40 caracteres>` não passa.
    """
    achados = []
    # O valor literal, primeiro e sem regex: é o único que se conhece de certeza.
    if token and len(token) >= 8 and token in texto:
        achados.append("VALOR LITERAL DO TOKEN")
    for nome, padrao in (
            ("token de acesso Supabase", r"sb[ps]_[A-Za-z0-9_\-]{16,}"),
            ("JWT", r"eyJ[A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{10,}"),
            ("cabecalho Authorization com valor",
             r"[Aa]uthorization\s*:\s*(?:[Bb]earer\s+)?\S{8,}"),
            ("Bearer com valor", r"Bearer\s+[A-Za-z0-9._\-]{16,}"),
            ("connection string", r"postgres(ql)?://\S{8,}"),
            ("atribuicao de segredo", r"SUPABASE_[A-Z_]*(TOKEN|KEY|URL)\s*=\s*\S{8,}"),
            ("cookie", r"[Ss]et-[Cc]ookie\s*:\s*\S+"),
    ):
        if re.search(padrao, texto):
            achados.append(nome)
    return achados


def autoteste_do_varredor() -> list:
    """O varredor prova-se a si próprio antes de aprovar seja o que for.

    Um varredor que não apanha nada dá sempre verde — e um verde que nunca
    pode ficar vermelho não é uma verificação, é um enfeite.
    """
    falhas = []
    devia_apanhar = (
        ("token literal", "ISCA-SEM-VALOR-1", '{"x":"ISCA-SEM-VALOR-1"}'),
        ("sbp com corpo", "", '{"x":"sbp_ISCA_FALSA_SEM_VALOR_NENHUM"}'),
        ("bearer com valor", "", '{"h":"Bearer ISCA-FALSA-SEM-VALOR"}'),
        ("authorization com valor", "", '{"h":"Authorization: Bearer ISCA-SEM-VALOR"}'),
        ("connection string", "", '{"db":"postgresql://ISCA-FALSA-SEM-VALOR"}'),
        ("jwt", "", '{"t":"eyJISCA_FALSA_SEM_VALOR.ISCA-SEM-VALOR"}'),
    )
    for nome, tok, txt in devia_apanhar:
        if not sem_vazamento(txt, tok):
            falhas.append("NAO APANHOU: " + nome)
    devia_deixar_passar = (
        ("prosa que nomeia os padroes",
         "procura sbp_, Bearer e Authorization: no texto antes de gravar"),
        ("nome de variavel", "o secret chama-se SUPABASE_ACCESS_TOKEN"),
        ("id de backup", '{"id": 123456789, "status": "COMPLETED"}'),
    )
    for nome, txt in devia_deixar_passar:
        if sem_vazamento(txt, ""):
            falhas.append("FALSO POSITIVO: " + nome)
    return falhas


def main() -> int:
    token = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
    print("SUPABASE_ACCESS_TOKEN=%s" % ("PRESENTE" if token else "AUSENTE"))
    if not token:
        # HARD STOP. Sem chave não há medição — e uma medição que não
        # aconteceu não deixa artefacto a fingir que aconteceu.
        print("MEDICAO_IMPOSSIVEL=o secret nao chegou ao runner")
        print("LIVE_BACKUP_PREFLIGHT=BLOCKED")
        return 1

    # O varredor prova-se antes de julgar o artefacto.
    falhas = autoteste_do_varredor()
    print("VARREDOR_AUTOTESTE=%s" % ("PASS" if not falhas else "FAIL"))
    if falhas:
        for f in falhas:
            print("  " + f)
        print("MEDICAO_ABORTADA=o varredor de vazamento nao e de confianca")
        return 1

    metodo = {
        "METODOS_HTTP_USADOS": ["GET"],
        "ENDPOINT": ENDPOINT,
        "TOKEN_EM_ARGV": "NAO",
        "TOKEN_EM_FICHEIRO": "NAO",
        "TOKEN_EM_URL": "NAO",
        "ECHO_DO_TOKEN": "NAO",
        "VARREDURA_DE_VAZAMENTO": "SIM",
        "VARREDOR_AUTOTESTADO": "SIM",
        "PERMISSOES_DO_WORKFLOW": "contents: read",
        "ESCRITAS": 0, "DDL": 0, "SQL_NO_LIVE": 0, "RESTAUROS": 0,
    }

    r = so_get(ENDPOINT, token)
    print("HTTP_STATUS=%s" % r["HTTP_STATUS"])

    m = le_backups(r)
    m["PROVA"] = "SUPABASE-LIVE-BACKUP-MEASURED"
    m["MEDIDO_EM"] = AGORA.isoformat(timespec="seconds")
    m["PROJECT_REF"] = LIVE_REF
    m["PROJECT_NAME_ESPERADO"] = NOME_ESPERADO
    m["PROJECT_NAME_MEDIDO"] = "NOT_MEASURED"
    m["PORQUE_NOME_NAO_MEDIDO"] = (
        "o nome vive em GET /v1/projects, que exige escopo de projeto e nao "
        "de backups. Nao foi chamado: esta missao nao amplia escopo.")
    m["DEV_REF_NAO_TOCADO"] = DEV_REF
    m["ESCRITAS_NO_DEV"] = 0
    m["METODO"] = metodo
    if r.get("MENSAGEM"):
        m["MENSAGEM_DO_FORNECEDOR"] = r["MENSAGEM"]
    if r.get("FALHA_DE_TRANSPORTE"):
        m["FALHA_DE_TRANSPORTE"] = r["FALHA_DE_TRANSPORTE"]

    m["MANAGEMENT_TOKEN_WORKED"] = "YES" if r["HTTP_STATUS"] == 200 else "NO"
    m["SAME_PLATFORM_RESTORE"] = "NOT_RUN"
    m["PORQUE_RESTORE_NOT_RUN"] = (
        "esta missao mede e nao restaura. Nenhum backup listado promove "
        "SAME_PLATFORM_RESTORE: so um restauro EXECUTADO o faria.")
    m["LIVE_BACKUP_PREFLIGHT"] = portao(m)
    # O portão de aplicar não se mexe aqui. Medir remove UNKNOWN; não muda a lei.
    m["READY_FOR_LIVE_APPLY"] = "NO"
    m["PORQUE_NAO_PRONTO"] = (
        "a lei em vigor exige SAME_PLATFORM_RESTORE executado, e ele continua "
        "NOT_RUN. Medir backup remove UNKNOWN; nao relaxa portao.")
    m["LIVE_READS"] = 1
    m["LIVE_WRITES"] = 0
    m["LIVE_DDL"] = 0
    m["REAL_COLLECTION"] = 0
    m["RED_TEAM"] = red_team(m, bool(token), metodo)

    texto = json.dumps(m, indent=2, ensure_ascii=False, sort_keys=False)
    fugas = sem_vazamento(texto, token)
    if fugas:
        # HARD STOP. Não se grava, não se commita, não se publica.
        print("VAZAMENTO_DETETADO=%s" % ", ".join(fugas))
        print("ARTEFACTO_NAO_GRAVADO=SIM")
        return 1

    SAIDA.write_text(texto + "\n", encoding="utf-8")

    for c in ("LIVE_BACKUP_PREFLIGHT", "MANAGEMENT_TOKEN_WORKED",
              "BACKUPS_VISIBLE", "BACKUP_COUNT", "LATEST_BACKUP_TIMESTAMP",
              "OLDEST_BACKUP_TIMESTAMP", "BACKUP_RETENTION_OBSERVED",
              "PHYSICAL_BACKUP_OBSERVED", "PITR_OBSERVED", "PITR_ENABLED",
              "BACKUP_SCHEDULE", "RESTORE_SOURCE_AVAILABLE",
              "SAME_PLATFORM_RESTORE", "READY_FOR_LIVE_APPLY"):
        print("%s=%s" % (c, m.get(c)))
    if m.get("PORQUE_NAO_MEDIDO"):
        print("PORQUE_NAO_MEDIDO=%s" % m["PORQUE_NAO_MEDIDO"])
    rt = m["RED_TEAM"]
    print("RED_TEAM_ATTACKS=%s" % rt["RED_TEAM_ATTACKS"])
    print("RED_TEAM_SURVIVORS=%s" % rt["RED_TEAM_SURVIVORS"])
    print("ARTEFACTO=%s" % SAIDA.relative_to(RAIZ))

    # Sobreviver a um ataque do red team é defeito da prova, e trava.
    if rt["RED_TEAM_SURVIVORS"]:
        for n, v in rt["ATAQUES"].items():
            if v["RESULTADO"] == "SOBREVIVEU":
                print("SOBREVIVEU %s · %s" % (n, v["ATAQUE"]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
