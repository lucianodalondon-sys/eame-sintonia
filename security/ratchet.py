#!/usr/bin/env python3
"""SECURITY RATCHET — esta mudanca piorou a seguranca?

Nao pergunta se o sistema esta perfeito. Pergunta se ele piorou. A divida
herdada fica VISIVEL e nao bloqueia; uma exposicao NOVA bloqueia.

    OLD SECURITY DEBT != PERMISSION TO ADD NEW DEBT.
    KNOWN DEBT != NEW REGRESSION.

Cada achado tem uma CHAVE estavel — classe, ficheiro, marcador. O ficheiro
`security/ratchet-baseline.json` congela as chaves ja conhecidas. Sai 0 quando
nenhuma chave nova apareceu, e 1 nomeando exactamente a que apareceu.

A chave nao inclui contagens de propósito. Um pacote canonico reconstruido traz
mais linhas do mesmo campo todas as semanas; se a contagem entrasse na chave, o
portao gritava a cada rebuild e alguem o desligava.

    GUARDA QUE GRITA DEMAIS VIRA GUARDA DESLIGADA.

Uso:
    python3 security/ratchet.py             # portao
    python3 security/ratchet.py --freeze    # recongela a divida conhecida
    python3 security/ratchet.py --json      # relatorio legivel por maquina
"""
import json, os, re, subprocess, sys, pathlib

try:
    import yaml
except ImportError:                                     # pragma: no cover
    # Sem analisador de YAML nao ha como provar que os workflows correm. Isso e
    # uma falha do portao, nao um passo a saltar em silencio.
    #     SILENTLY SKIPPED STEP = 0.
    raise SystemExit("RATCHET INDISPONIVEL: falta PyYAML, e sem ele os workflows "
                     "nao podem ser verificados. `pip install pyyaml`.")

# Substituivel para que as provas possam montar um repositorio minimo e mutar-lo.
#     UM PORTAO QUE NAO PODE SER ATACADO NAO FOI PROVADO.
RAIZ = pathlib.Path(os.environ.get("SINTONIA_RATCHET_RAIZ") or
                    pathlib.Path(__file__).resolve().parent.parent)
BASELINE = RAIZ / "security" / "ratchet-baseline.json"
sys.path.insert(0, str(RAIZ / "security"))
from superficie_publica import superficie  # noqa: E402  (o dono da fronteira publicada)

# ── O QUE E DADO PESSOAL, POR NOME DE CAMPO ────────────────────────────────
# Deterministico e explicavel de proposito: nada de classificador opaco. Se um
# campo novo aparecer na superficie publicada, queremos poder dizer PORQUE.
CAMPOS_PESSOAIS = [
    "ORCID", "PERSON", "PERSON_ID", "PERSON_NAME", "AUTHOR", "AUTHOR_NAME",
    "EMAIL", "E_MAIL", "PERSONAL_EMAIL", "PHONE", "TELEFONE", "MOBILE",
    "CONTACT", "CONTACT_INFO", "ADDRESS", "MORADA", "POSTAL_CODE",
    "BIRTH_DATE", "DATE_OF_BIRTH", "DOB", "NATIONAL_ID", "CPF", "NIF", "VAT_ID",
    "IP_ADDRESS", "USER_AGENT", "GEOLOCATION", "SALARY", "GENDER", "ETHNICITY",
    "HEALTH", "RELIGION", "POLITICAL", "HANDLE", "USERNAME", "PROFILE_URL",
]
# ── O QUE E MOTOR/REGRA PROPRIETARIA ───────────────────────────────────────
MARCADORES_MOTOR = [
    "DERIVATION_FORMULA", "IS_DERIVED_BY_SINTONIA", "SCORING_WEIGHT", "WEIGHTS",
    "THRESHOLD", "SCORE_FORMULA", "RULE_EXPRESSION", "REGRA_EXPRESSAO",
    "MODEL_INSTRUCTIONS", "SYSTEM_PROMPT", "PROMPT_TEMPLATE", "LLM_PROMPT",
    "RANKING_COEFFICIENT", "COEFICIENTE", "ALGORITHM_STEPS", "PIPELINE_STEPS",
]
# ── CAMINHOS QUE NUNCA DEVEM SER SERVIDOS ──────────────────────────────────
CAMINHOS_SENSIVEIS = [
    (re.compile(r"(^|/)\.env"), "ficheiro de ambiente"),
    (re.compile(r"(^|/)supabase/"), "esquema de base de dados"),
    (re.compile(r"(^|/)(data|build|research|handoff|docs|prototype)/"), "acervo ou investigacao"),
    (re.compile(r"(^|/)(scripts|tests|provas|guarda|coleta|portoes|admissao|motor|pacote)/"), "motor ou ferramenta"),
    (re.compile(r"(^|/)\.git"), "metadados de Git"),
    (re.compile(r"\.sql$"), "SQL"),
    (re.compile(r"(^|/)package(-lock)?\.json$"), "metadados de pacote"),
    (re.compile(r"(^|/)security/"), "documentacao interna de seguranca"),
]
VENDOR = re.compile(r"(^|/)vendor/")


def achado(classe, caminho, marcador, detalhe):
    return {"classe": classe, "caminho": caminho, "marcador": marcador,
            "detalhe": detalhe, "chave": f"{classe}|{caminho}|{marcador}"}


# ══ 1. WORKFLOWS ══════════════════════════════════════════════════════════
# Eventos que um estranho consegue disparar a partir de um fork. Se um destes
# chegar a um runner self-hosted, um PR de fora executa codigo na maquina do dono.
EVENTOS_NAO_CONFIAVEIS = ("pull_request_target", "issue_comment", "pull_request")


def checar_workflows():
    out, wfs = [], sorted((RAIZ / ".github" / "workflows").glob("*.yml"))
    for w in wfs:
        nome, txt = w.name, w.read_text(encoding="utf-8")
        # Um workflow que nao analisa nao corre — e um portao que nao corre nao
        # e um portao. Esta linha entrou depois de um `:` dentro do nome de um
        # passo ter feito o proprio SECURITY CHECK nao arrancar: a corrida deu
        # `failure` com ZERO jobs, que e a forma mais silenciosa de falhar.
        #
        #     UM PORTAO COM ERRO DE SINTAXE NAO FALHA: DESAPARECE.
        try:
            yaml.safe_load(txt)
        except yaml.YAMLError as e:
            marca = getattr(e, "problem_mark", None)
            out.append(achado("WORKFLOW_YAML_INVALIDO", f".github/workflows/{nome}",
                              f"linha {marca.line + 1}" if marca else "erro de analise",
                              "o GitHub nao consegue ler este workflow: ele nao corre"))
        sem_comentarios = "\n".join(l for l in txt.splitlines() if not l.lstrip().startswith("#"))
        if re.search(r"^\s*pull_request_target\s*:", sem_comentarios, re.M):
            out.append(achado("NEW_PULL_REQUEST_TARGET", f".github/workflows/{nome}",
                              "pull_request_target",
                              "um fork passa a poder correr com os segredos do repositorio"))
        if re.search(r"permissions\s*:\s*write-all", sem_comentarios):
            out.append(achado("NEW_WRITE_ALL_PERMISSION", f".github/workflows/{nome}",
                              "write-all", "escopo maximo onde devia haver escopo nomeado"))
        if not re.search(r"^\s*permissions\s*:", sem_comentarios, re.M):
            out.append(achado("WORKFLOW_SEM_PERMISSIONS", f".github/workflows/{nome}",
                              "sem permissions",
                              "sem bloco permissions herda o escopo por omissao do repositorio"))
        if "self-hosted" in sem_comentarios:
            eventos = re.findall(r"^\s{2}(\w+)\s*:", sem_comentarios[sem_comentarios.find("\non:"):], re.M) \
                if "\non:" in sem_comentarios else []
            for ev in EVENTOS_NAO_CONFIAVEIS:
                if ev in eventos:
                    out.append(achado("SELF_HOSTED_EM_EVENTO_NAO_CONFIAVEL",
                                      f".github/workflows/{nome}", ev,
                                      "um PR de fora alcancaria o runner self-hosted"))
    return out, len(wfs)


# ══ 2. SUPERFICIE PUBLICADA ═══════════════════════════════════════════════
LIMITE_LEITURA = 40_000_000


def checar_superficie():
    s = superficie(RAIZ)
    out = []
    for rel in s["ficheiros"]:
        for rx, porque in CAMINHOS_SENSIVEIS:
            if rx.search(rel):
                out.append(achado("NEW_SENSITIVE_PATH_PUBLISHED", rel, porque,
                                  "este caminho nao devia ser servido"))
        if rel.endswith(".map") and not VENDOR.search(rel):
            out.append(achado("NEW_OWN_SOURCE_MAP_PUBLISHED", rel, "ficheiro .map",
                              "source map proprio na superficie publica"))
        p = RAIZ / rel
        if not p.exists() or p.stat().st_size > LIMITE_LEITURA:
            continue
        if not re.search(r"\.(js|json|html|css|txt|mjs)$", rel):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if not VENDOR.search(rel) and "sourceMappingURL" in txt:
            out.append(achado("NEW_OWN_SOURCE_MAP_PUBLISHED", rel, "sourceMappingURL",
                              "codigo proprio publicado aponta para um source map"))
        for campo in CAMPOS_PESSOAIS:
            if re.search(rf'["\']{campo}["\']\s*:', txt):
                out.append(achado("NEW_PERSONAL_DATA_FIELD_IN_PUBLIC_OUTPUT", rel, campo,
                                  "campo de dado pessoal na superficie servida ao publico"))
        for marca in MARCADORES_MOTOR:
            if re.search(rf'["\']{marca}["\']\s*:', txt):
                out.append(achado("NEW_PUBLIC_ENGINE_EXPOSURE", rel, marca,
                                  "regra ou formula proprietaria na superficie servida"))
    return out, s


# ══ 3. MIGRATIONS ═════════════════════════════════════════════════════════
def checar_migrations():
    d = RAIZ / "supabase" / "migrations"
    if not d.exists():
        return [], 0
    criadas, com_rls = {}, set()
    for f in sorted(d.glob("*.sql")):
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r"create table\s+(?:if not exists\s+)?([\w.\"]+)", txt, re.I):
            criadas.setdefault(m.group(1).strip('"').lower(), f.name)
        for m in re.finditer(r"alter table\s+(?:if exists\s+)?([\w.\"]+)\s+enable row level security",
                             txt, re.I):
            com_rls.add(m.group(1).strip('"').lower())
    out = [achado("NEW_TABLE_WITHOUT_RLS", f"supabase/migrations/{criadas[t]}", t,
                  "tabela criada sem declaracao de RLS na migration")
           for t in sorted(set(criadas) - com_rls)]
    return out, len(criadas)


# ══ 4. DELEGACOES ═════════════════════════════════════════════════════════
# Nao ha segundo validador nem segundo redactor: chamam-se os donos que existem.
def delegar(rotulo, argv):
    r = subprocess.run(argv, cwd=RAIZ, capture_output=True, text=True)
    return {"nome": rotulo, "ok": r.returncode == 0, "codigo": r.returncode,
            "saida": (r.stdout + r.stderr).strip().splitlines()[-12:]}


def main():
    achados, n_wf = checar_workflows()
    sup_ach, sup = checar_superficie()
    mig_ach, n_tab = checar_migrations()
    achados += sup_ach + mig_ach

    # As delegacoes so correm na arvore real: nas provas nao existem donos a chamar.
    delegacoes = [] if os.environ.get("SINTONIA_RATCHET_RAIZ") else [
        delegar("baseline-schema", [sys.executable, "security/validate-baseline.py"]),
        delegar("git-secrets (guarda/social_guarda.py)", [sys.executable, "guarda/social_guarda.py"]),
    ]

    if "--freeze" in sys.argv:
        BASELINE.write_text(json.dumps({
            "COMENTARIO": "Divida conhecida no momento do congelamento. Estar aqui nao "
                          "significa aceite para sempre: significa que nao bloqueia HOJE. "
                          "Regressao nova nao esta aqui, e por isso bloqueia.",
            "CONGELADO_EM": "2026-09-09",
            "chaves": sorted({a["chave"] for a in achados}),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"congelado: {len({a['chave'] for a in achados})} chaves de divida conhecida")
        return 0

    conhecidas = set(json.loads(BASELINE.read_text(encoding="utf-8"))["chaves"]) if BASELINE.exists() else set()
    novos = [a for a in achados if a["chave"] not in conhecidas]
    herdados = len(achados) - len(novos)

    if "--json" in sys.argv:
        print(json.dumps({"workflows": n_wf, "tabelas_migrations": n_tab,
                          "ficheiros_publicados": len(sup["ficheiros"]),
                          "achados_totais": len(achados), "herdados": herdados,
                          "novos": novos, "delegacoes": delegacoes},
                         ensure_ascii=False, indent=2))
        return 1 if (novos or any(not d["ok"] for d in delegacoes)) else 0

    print(f"workflows {n_wf} · tabelas nas migrations {n_tab} · ficheiros publicados {len(sup['ficheiros'])}")
    print(f"divida herdada (visivel, nao bloqueia): {herdados}")
    for d in delegacoes:
        print(f"  [{'ok' if d['ok'] else 'FALHA'}] {d['nome']}")
        if not d["ok"]:
            for l in d["saida"]:
                print("        " + l)

    if novos:
        print(f"\nREGRESSAO NOVA: {len(novos)}")
        for a in novos:
            # O erro tem de dizer o que fazer, nao so que falhou. E nunca o valor.
            print(f"\n  {a['classe']}")
            print(f"    ficheiro : {a['caminho']}")
            print(f"    marcador : {a['marcador']}")
            print(f"    porque   : {a['detalhe']}")
        print("\n  Se isto for intencional e revisto, `python3 security/ratchet.py --freeze`")
        print("  move a chave para a divida conhecida — e deixa o registo de quem a moveu.")
    falhou = bool(novos) or any(not d["ok"] for d in delegacoes)
    print("\nRATCHET = " + ("FALHA" if falhou else "PASSA"))
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
