#!/usr/bin/env python3
"""SEC-020 · O REPOSITORIO DIZ UMA COISA. A BASE VIVA DIZ OUTRA.

Medido em 2026-09-09: as migrations criam 66 tabelas e nunca declaram RLS em
doze delas; a base viva tem 67 tabelas e RLS activa em todas. A base estava
mais segura do que o repositorio dizia — o que foi sorte, e nao desenho.

    A LIVE DATABASE THAT IS SAFER THAN THE REPO IS STILL DRIFT.
    REPO STATE != LIVE STATE.  MIGRATION STATE != LIVE SECURITY STATE.

Este programa transforma essa lei em codigo. Le o censo de metadados da base
viva, compara-o com o estado ESPERADO que o repositorio declara, e responde
duas perguntas separadas — porque juntar as duas foi exactamente o defeito:

    SECURITY_STATUS   a porta esta fechada?
    DRIFT_STATUS      a base e a que dissemos que era?

Uma base segura mas diferente do esperado da SAFE + DRIFT. Verde silencioso,
nunca: uma deriva que hoje protege pode amanha expor, e ninguem daria por ela.

    SAFE DRIFT != NO DRIFT.

O ficheiro esperado nao e uma fotografia da base: e uma declaracao revista.

    LIVE SNAPSHOT != DESIRED SECURITY POLICY.

Uso:
    python3 security/drift_db.py CENSO.txt              # compara e classifica
    python3 security/drift_db.py CENSO.txt --escrever   # regrava o esperado
"""
import json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESPERADO = RAIZ / "security" / "live-db-expected.json"
MIGRATIONS = RAIZ / "supabase" / "migrations"

CLASSES_REGRESSAO = {"LIVE_LESS_RESTRICTIVE", "PRIVILEGE_MISMATCH_ABERTURA", "RLS_DESLIGADA"}


# ── ler o censo ────────────────────────────────────────────────────────────
def kv(partes):
    return dict(p.split("=", 1) for p in partes if "=" in p)


def ler_censo(caminho):
    obs = {"contexto": {}, "roles": [], "schema": {}, "tabelas": {}, "vistas": {}}
    for linha in pathlib.Path(caminho).read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or "|" not in linha:
            continue
        campos = linha.split("|")
        tipo = campos[0]
        if tipo == "CTX":
            obs["contexto"] = kv(campos[1:])
        elif tipo == "ROLE":
            obs["roles"].append(campos[1])
        elif tipo == "SCHEMA":
            obs["schema"] = kv(campos[2:])
        elif tipo == "T":
            obs["tabelas"][campos[1]] = kv(campos[2:])
        elif tipo == "V":
            obs["vistas"][campos[1]] = kv(campos[2:])
    return obs


# ── o que o repositorio DECLARA ────────────────────────────────────────────
def declarado_pelas_migrations():
    criadas, com_rls = set(), set()
    for f in sorted(MIGRATIONS.glob("*.sql")):
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r"create table\s+(?:if not exists\s+)?([\w.\"]+)", txt, re.I):
            criadas.add(m.group(1).strip('"').lower().replace("public.", ""))
        for m in re.finditer(r"alter table\s+(?:if exists\s+)?([\w.\"]+)\s+enable row level security",
                             txt, re.I):
            com_rls.add(m.group(1).strip('"').lower().replace("public.", ""))
    return criadas, com_rls


def v(d, k):
    return d.get(k) == "true"


def comparar(obs):
    esperado = json.loads(ESPERADO.read_text(encoding="utf-8")) if ESPERADO.exists() else {}
    esp_tab = esperado.get("tabelas", {})
    criadas, com_rls = declarado_pelas_migrations()
    achados = []

    def add(classe, alvo, detalhe):
        achados.append({"classe": classe, "alvo": alvo, "detalhe": detalhe})

    # 1 · a porta esta fechada? Esta e a pergunta de SEGURANCA.
    for nome, t in obs["tabelas"].items():
        if any(v(t, k) for k in ("anon_s", "anon_i", "anon_u", "anon_d")):
            esp = esp_tab.get(nome, {})
            if not any(esp.get(k) for k in ("anon_s", "anon_i", "anon_u", "anon_d")):
                add("LIVE_LESS_RESTRICTIVE", nome,
                    "anon ganhou privilegio efectivo onde o esperado nao previa nenhum")
        if not v(t, "rls") and esp_tab.get(nome, {}).get("rls") is True:
            add("RLS_DESLIGADA", nome, "RLS estava activa no esperado e nao esta na base viva")
    # O Postgres grava esta opcao como `on`, nao como `true`. Comparar com
    # "true" daria sempre desigual e transformaria as 16 vistas correctas em
    # 16 achados — e um portao que acusa o que esta certo e um portao desligado.
    for nome, w in obs["vistas"].items():
        invoker_ligado = w.get("invoker") in ("on", "true")
        if v(w, "anon_s") and not invoker_ligado:
            add("VISTA_SEM_SECURITY_INVOKER_LEGIVEL_POR_ANON", nome,
                "uma vista sem security_invoker corre com os direitos de quem a criou: "
                "e um caminho a volta da RLS das tabelas que ela le")
        elif not invoker_ligado:
            # Fechada hoje, porque anon nao a alcanca. Mas o dia em que alguem
            # der SELECT a anon, esta vista passa a ler com os direitos do dono.
            #     A PORTA LATERAL NAO PRECISA DE ESTAR ABERTA PARA EXISTIR.
            add("VISTA_SEM_SECURITY_INVOKER_LATENTE", nome,
                "sem security_invoker; hoje inalcancavel por anon, mas seria "
                "uma porta lateral no dia em que o for")

    # 2 · a base e a que dissemos que era? Esta e a pergunta de DERIVA.
    vivas = set(obs["tabelas"])
    for nome in sorted(vivas - criadas):
        add("TABLE_ONLY_IN_LIVE", nome, "existe na base viva e nenhuma migration a cria")
    for nome in sorted(criadas - vivas):
        add("TABLE_ONLY_IN_REPO", nome, "uma migration cria-a e ela nao existe na base viva")
    for nome in sorted(vivas & criadas):
        t = obs["tabelas"][nome]
        if v(t, "rls") and nome not in com_rls:
            add("LIVE_MORE_RESTRICTIVE", nome,
                "RLS activa na base viva e nao declarada em nenhuma migration")
        if not v(t, "rls") and nome in com_rls:
            add("RLS_MISMATCH", nome, "a migration declara RLS e a base viva nao a tem")
        esp = esp_tab.get(nome)
        if esp is not None:
            for k in ("anon_s", "anon_i", "anon_u", "anon_d", "auth_s", "auth_i", "auth_u", "auth_d"):
                if v(t, k) != bool(esp.get(k)):
                    classe = "PRIVILEGE_MISMATCH_ABERTURA" if v(t, k) else "PRIVILEGE_MISMATCH_FECHO"
                    add(classe, f"{nome}.{k}", "privilegio efectivo diferente do esperado")
        if esp is not None and int(t.get("policies", "0")) != int(esp.get("policies", 0)):
            add("POLICY_MISMATCH", nome, "numero de politicas diferente do esperado")
        elif esp is None:
            add("TABELA_SEM_ESPERADO", nome, "viva e nao declarada em live-db-expected.json")

    return achados, criadas, com_rls


def instantaneo(obs):
    """O que fica registado. Nomes e estado de seguranca — nunca conteudo,
    nunca credencial, nunca DSN."""
    return {
        "COMENTARIO": "Estado ESPERADO da base viva. Nao e uma fotografia automatica: "
                      "e uma declaracao revista. LIVE SNAPSHOT != DESIRED SECURITY POLICY.",
        "MEDIDO_EM": "2026-09-09",
        "METODO": "catalogo em leitura, via .github/workflows/rls-censo-metadados.yml",
        "schema_public": {k: obs["schema"].get(k) == "true" for k in obs["schema"]},
        "tabelas": {n: {"rls": v(t, "rls"), "force": v(t, "force"),
                        "policies": int(t.get("policies", "0")),
                        **{k: v(t, k) for k in ("anon_s", "anon_i", "anon_u", "anon_d",
                                                "auth_s", "auth_i", "auth_u", "auth_d")}}
                    for n, t in sorted(obs["tabelas"].items())},
        "vistas": {n: {"security_invoker": w.get("invoker"), "anon_s": v(w, "anon_s")}
                   for n, w in sorted(obs["vistas"].items())},
    }


def main():
    censo = sys.argv[1]
    obs = ler_censo(censo)
    if "--escrever" in sys.argv:
        ESPERADO.write_text(json.dumps(instantaneo(obs), ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        print(f"escrito {ESPERADO.name}: {len(obs['tabelas'])} tabelas, {len(obs['vistas'])} vistas")
        return 0

    achados, criadas, _ = comparar(obs)
    regressoes = [a for a in achados if a["classe"] in CLASSES_REGRESSAO]
    derivas = [a for a in achados if a["classe"] not in CLASSES_REGRESSAO]

    print("── CONTEXTO ──")
    for k, val in obs["contexto"].items():
        print(f"  {k} = {val}")
    print(f"  roles = {', '.join(obs['roles'])}")
    print(f"  schema public = {obs['schema']}")
    print(f"\n── CONTAGENS ──")
    print(f"  tabelas nas migrations   {len(criadas)}")
    print(f"  tabelas na base viva     {len(obs['tabelas'])}")
    print(f"  vistas na base viva      {len(obs['vistas'])}")
    print(f"  com RLS activa           {sum(1 for t in obs['tabelas'].values() if v(t, 'rls'))}")
    print(f"  com politica             {sum(1 for t in obs['tabelas'].values() if int(t.get('policies','0')))}")
    print(f"  anon com SELECT          {sum(1 for t in obs['tabelas'].values() if v(t, 'anon_s'))}")
    print(f"  anon com escrita         {sum(1 for t in obs['tabelas'].values() if any(v(t,k) for k in ('anon_i','anon_u','anon_d')))}")

    print("\n── VEREDITO ──")
    # As duas perguntas, separadas de proposito. Juntar foi o defeito.
    print(f"  SECURITY_STATUS = {'REGRESSION' if regressoes else 'SAFE'}")
    print(f"  DRIFT_STATUS    = {'DRIFT' if derivas else 'ALINHADO'}")

    if regressoes:
        # Porta aberta: o detalhe fica retido. Este log e publico e a contencao
        # ainda nao existe.  PROVA DE PORTA ABERTA -> PRIMEIRO FECHA-SE.
        print(f"\n  REGRESSAO DE SEGURANCA: {len(regressoes)} · DETALHE_RETIDO = YES")
        print("  Classes: " + ", ".join(sorted({a['classe'] for a in regressoes})))
        print("  Nomes de tabela nao sao impressos: quem tem a chave le pela sua conexao.")
    if derivas:
        # Deriva sem exposicao: publicavel. Dizer que uma tabela tem RLS a mais
        # do que a migration declara nao ensina nada a um estranho.
        print(f"\n  DERIVA (sem exposicao, publicavel): {len(derivas)}")
        for a in derivas:
            print(f"    {a['classe']:42} {a['alvo']}")
            print(f"      {a['detalhe']}")
    return 1 if regressoes else 0


if __name__ == "__main__":
    sys.exit(main())
