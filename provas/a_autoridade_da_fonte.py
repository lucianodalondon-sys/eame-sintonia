#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUEM TEM AUTORIDADE PARA DIZER DE QUEM E ESTA FONTE?

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_autoridade_da_fonte.py

    (o banco e opcional: sem ele, os casos que exigem banco sao PULADOS,
     e pulado nao conta como provado)

A PERGUNTA, E POR QUE ELA VEM ANTES DO CODIGO
----------------------------------------------
A M2 corre de ponta a ponta, mas a identidade do canal e montada A MAO dentro
da prova: alguem escreve, no banco descartavel, que a fonte `IT-T2-002`
pertence a organizacao `ARPAV`. Para isso deixar de ser fixture, e preciso um
dono de identidade. E antes de escrever esse dono ha uma pergunta que nao se
pode saltar:

    QUEM TEM AUTORIDADE PARA AFIRMAR QUE `IT-T2-002` PERTENCE A `ARPAV`?

Este ficheiro NAO resolve identidade. Ele NAO escreve em `organizacao`,
`pessoa`, `origem` nem `canal`. Ele so MEDE a cadeia de autoridade nos
artefatos canonicos da casa, e diz se ela chega — ou onde exatamente ela
falta.

    SOURCE CATALOG DECLARATION  !=  DB IDENTITY AUTHORITY.
    CANDIDATE RECORD            !=  CANONICAL FACT.

O QUE ELE MEDE, E EM QUE ORDEM
-------------------------------
    AU1  qual e o registo canonico das fontes — e quem o diz
    AU2  ha um contrato canonico que declare OWNER? para que fontes?
    AU3  `IT-T2-002` tem ficha no registo canonico?
    AU4  `IT-T2-002` tem contrato canonico com OWNER?
    AU5  onde a relacao existe, entao — e o que esse sitio diz de si proprio
    AU6  MUTACAO: admitir o candidato como autoridade vira o veredito
    AU7  mesmo depois de promovida, o que ainda faltaria
    AU8  no banco, ninguem escreveu identidade a correr isto
    AU9  um SEGUNDO sitio declara dono, e os dois discordam
    AU10 e nenhuma gaveta de runtime escreve identidade

⚠️ ESTE FICHEIRO NAO E O DONO DA IDENTIDADE, E NAO DEVE VIRAR UM.
Ele vive em `provas/` de propósito: nada de runtime pode depender dele. Se um
dia a autoridade existir, quem escrever o dono leva este censo consigo — e ate
la nao ha dono nenhum a fingir que ha.
"""
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

# ── OS ARTEFATOS, E O QUE CADA UM E ─────────────────────────────────────
ATLAS = os.path.join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
CONTRATOS = os.path.join(RAIZ, "docs", "operacao", "CONTRATOS-DAS-FONTES-EAME.md")
RECONCILIADO = os.path.join(RAIZ, "system-map", "data", "sources.generated.json")
CANDIDATO = os.path.join(RAIZ, "candidatas", "ITALY-SOURCE-MASTER-V1.json")
SCHEMA_IDENTIDADE = os.path.join(RAIZ, "supabase", "migrations",
                                 "002_identidade_pessoa_org_canal.sql")

# A fonte que a rota da M2 atravessa. Nao e um exemplo escolhido: e a unica
# unidade real que a cadeia forward ja percorreu de ponta a ponta.
A_FONTE_DA_M2 = "IT-T2-002"

# As tabelas cuja escrita esta em causa. Se alguma ganhar linha ao correr esta
# medicao, ela deixou de ser medicao.
TABELAS_DE_IDENTIDADE = ("organizacao", "pessoa", "origem", "canal")

fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def _texto(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


# ═════════════════════════════════════════════════════════════════════════
# A MEDICAO — so leitura, e so de artefatos canonicos
# ═════════════════════════════════════════════════════════════════════════
def contratos_com_owner():
    """As fontes que TEM contrato canonico com dono declarado.

    O contrato e um documento de operacao, e declara o par em prosa:

        SOURCE_ID   IT-T4-001
        OWNER       Ministero della Salute (Italia)

    E prosa, e mesmo assim e a coisa mais forte que a casa tem: e um
    documento canonico a nomear quem publica aquela fonte.
    """
    texto = _texto(CONTRATOS)
    pares, atual = {}, None
    for linha in texto.splitlines():
        m = re.match(r"^SOURCE_ID\s+(\S+)", linha)
        if m:
            atual = m.group(1).strip()
            continue
        m = re.match(r"^OWNER\s+(.+)$", linha)
        if m and atual:
            pares[atual] = m.group(1).strip()
            atual = None
    return pares


def fontes_com_ficha_no_atlas():
    """Os SOURCE_ID que tem ficha no registo canonico."""
    texto = _texto(ATLAS)
    return set(re.findall(r"\b(?:EU|FR|ES|IT)-T\d{1,2}-\d{3}\b", texto))


def o_que_o_reconciliado_diz(source_id):
    """O que o scanner da casa ja mediu sobre esta fonte.

    ⚠️ ESTE ARTEFATO E DERIVADO, e derivar nao confere autoridade: propaga-a.
    Ele copia o `owner` do candidato E carimba de onde veio (`onde`) e com que
    veredito. E por isso que ele serve de MEDIDA e nao de PROVA.
    """
    d = json.loads(_texto(RECONCILIADO))
    ficha = next((x for x in d.get("MASTER_ITALIANO", [])
                  if x.get("source_id") == source_id), None)
    return d.get("RECONCILIACAO", {}), ficha


def o_que_o_candidato_diz(source_id):
    d = json.loads(_texto(CANDIDATO))
    fonte = next((s for s in d.get("sources", [])
                  if s.get("SOURCE_ID") == source_id), None)
    dono = None
    if fonte and fonte.get("OWNER_ID"):
        dono = next((o for o in d.get("owners", [])
                     if o.get("OWNER_ID") == fonte["OWNER_ID"]), None)
    return d, fonte, dono


def tipos_que_o_schema_aceita():
    """O vocabulario de `organizacao.tipo`, lido do schema."""
    texto = _texto(SCHEMA_IDENTIDADE)
    m = re.search(r"tipo\s+text check \(tipo in\s*\((.*?)\)\)", texto, re.S)
    return set(re.findall(r"'([a-z_]+)'", m.group(1))) if m else set()


def owner_kinds_do_candidato():
    d = json.loads(_texto(CANDIDATO))
    return {o.get("OWNER_KIND") for o in d.get("owners", []) if o.get("OWNER_KIND")}


# ═════════════════════════════════════════════════════════════════════════
def o_que_o_contrato_de_acesso_diz(source_id):
    """O SEGUNDO sitio que declara um dono para a mesma fonte.

    `regras/italy_contracts.mjs` e um contrato de ACESSO — diz como abrir a
    fonte (URL, mime, assinatura, template de rota). Mas ele traz `OWNER_ID`
    junto, e para 13 fontes.
    """
    caminho = os.path.join(RAIZ, "regras", "italy_contracts.mjs")
    if not os.path.exists(caminho):
        return None
    texto = _texto(caminho)
    i = texto.find('"%s"' % source_id)
    if i < 0:
        return None
    m = re.search(r'OWNER_ID:\s*"([^"]+)"', texto[i:i + 500])
    return m.group(1) if m else None


def escritores_de_identidade_em_runtime():
    """Quem ESCREVE identidade fora de ensaio, prova e fixture.

        TEST FIXTURE RESOLVES PRECONDITION != FORWARD IDENTITY OWNER EXISTS.
    """
    gavetas = ("coleta/", "guarda/", "admissao/", "leis/", "medidas/",
               "regras/", "orquestrador/", "ferramentas/", "fontes/",
               "pedido/", "pacote/")
    achados = []
    saida = subprocess.run(["git", "-C", RAIZ, "ls-files"],
                           capture_output=True, text=True).stdout.split("\n")
    for f in saida:
        if not f.startswith(gavetas) or not f.endswith((".py", ".sql", ".mjs")):
            continue
        corpo = "\n".join(re.sub(r"#.*$", "", l) for l in _texto(
            os.path.join(RAIZ, f)).split("\n"))
        for tabela in ("organizacao", "pessoa", "origem", "canal"):
            if re.search(r"insert\s+into\s+public\.%s\b" % tabela, corpo, re.I):
                achados.append("%s -> %s" % (f, tabela))
    return achados


def main():
    print("A CADEIA DE AUTORIDADE, MEDIDA NOS ARTEFATOS CANONICOS")
    print("=" * 70)

    # ── AU1 · qual e o registo canonico, e quem o diz ────────────────────
    recon, ficha_reconciliada = o_que_o_reconciliado_diz(A_FONTE_DA_M2)
    leitura = recon.get("leitura") or ""
    caso("AU1_a_casa_declara_qual_e_o_registo_canonico",
         "atlas e o registo canonico" in leitura.lower().replace("é", "e"),
         "sources.generated.json diz: «%s»" % leitura[-64:].strip())

    # ── AU2 · ha contrato canonico com OWNER? ────────────────────────────
    contratos = contratos_com_owner()
    caso("AU2_existe_contrato_canonico_que_declara_OWNER",
         len(contratos) > 0,
         "%d fonte(s) com OWNER em CONTRATOS-DAS-FONTES-EAME.md: %s"
         % (len(contratos), ", ".join(sorted(contratos))))

    # ── AU3 · a fonte da M2 tem ficha no registo canonico? ───────────────
    no_atlas = fontes_com_ficha_no_atlas()
    caso("AU3_a_fonte_da_M2_NAO_tem_ficha_no_registo_canonico",
         A_FONTE_DA_M2 not in no_atlas,
         "%s no atlas: %s · o atlas tem %d fontes com ficha"
         % (A_FONTE_DA_M2, A_FONTE_DA_M2 in no_atlas, len(no_atlas)))

    # ── AU4 · e contrato canonico com OWNER? ─────────────────────────────
    caso("AU4_a_fonte_da_M2_NAO_tem_contrato_canonico_com_OWNER",
         A_FONTE_DA_M2 not in contratos,
         "as %d fontes contratadas nao a incluem" % len(contratos))

    # ── AU5 · onde a relacao existe, e o que esse sitio diz de si ────────
    catalogo, fonte_cand, dono_cand = o_que_o_candidato_diz(A_FONTE_DA_M2)
    tocados = catalogo.get("canonical_artifacts_touched") or {}
    caso("AU5a_a_relacao_existe_APENAS_no_catalogo_candidato",
         bool(fonte_cand and dono_cand),
         "%s -> %s -> %s, em %s"
         % (A_FONTE_DA_M2, (fonte_cand or {}).get("OWNER_ID"),
            ((dono_cand or {}).get("OWNER_CANONICAL_NAME") or "")[:26],
            os.path.relpath(CANDIDATO, RAIZ)))
    caso("AU5b_e_o_proprio_catalogo_declara_que_nao_e_canonico",
         tocados.get("modified") == []
         and "aditivo" in (tocados.get("reason") or ""),
         "ele diz: «este catalogo e aditivo e nao altera o placar»")
    caso("AU5c_e_o_scanner_marca_a_fonte_como_nunca_promovida",
         A_FONTE_DA_M2 in (recon.get("so_no_master_italiano") or []),
         "esta em `so_no_master_italiano` (%d fontes) · verdict=%s status=%s"
         % (len(recon.get("so_no_master_italiano") or []),
            (ficha_reconciliada or {}).get("verdict"),
            (ficha_reconciliada or {}).get("status")))
    caso("AU5d_o_derivado_carimba_de_onde_a_relacao_veio",
         (ficha_reconciliada or {}).get("onde")
         == os.path.relpath(CANDIDATO, RAIZ).replace("\\", "/"),
         "onde=%s — derivar propaga a autoridade, nao a cria"
         % (ficha_reconciliada or {}).get("onde"))

    # ── AU6 · A MUTACAO ──────────────────────────────────────────────────
    #
    #     UM PORTAO QUE NUNCA REPROVA E INDISTINGUIVEL DE UM DESLIGADO.
    #
    # Se o catalogo candidato contasse como autoridade, a cadeia fechava. E
    # esse e exatamente o atalho que esta missao NAO pode tomar — promover um
    # candidato para a prova ficar verde e escrever a resposta no exame.
    def resolve(admitir_candidato):
        """Ha autoridade para ligar esta fonte a uma entidade?"""
        if A_FONTE_DA_M2 in contratos:
            return "RESOLVED", "contrato canonico"
        if A_FONTE_DA_M2 in no_atlas:
            return "RESOLVED", "ficha no registo canonico"
        if admitir_candidato and fonte_cand and dono_cand:
            return "RESOLVED", "catalogo candidato"
        return "UNRESOLVED", "nenhuma autoridade canonica alcanca esta fonte"

    com, porque_com = resolve(True)
    sem, porque_sem = resolve(False)
    caso("AU6a_com_a_autoridade_canonica_a_fonte_fica_UNRESOLVED",
         sem == "UNRESOLVED", porque_sem)
    caso("AU6b_MUTACAO_admitir_o_candidato_viraria_o_veredito",
         com == "RESOLVED" and com != sem,
         "seria RESOLVED por «%s» — e e por isso que nao se admite" % porque_com)

    # ── AU9 · E O CATALOGO CANDIDATO NAO ESTA SOZINHO ────────────────────
    #
    # Ha um SEGUNDO sitio a declarar um dono para a mesma fonte, e os dois
    # NAO dizem o mesmo. Isto nao enfraquece o veredito — endurece-o: mesmo
    # que alguem decidisse admitir um catalogo nao promovido, teria de
    # escolher QUAL dos dois, e nada no repositorio diz qual vence.
    #
    #     AMBIGUOUS != FIRST MATCH.
    dono_acesso = o_que_o_contrato_de_acesso_diz(A_FONTE_DA_M2)
    dono_catalogo = (fonte_cand or {}).get("OWNER_ID")
    caso("AU9a_um_segundo_sitio_declara_dono_para_a_mesma_fonte",
         bool(dono_acesso),
         "regras/italy_contracts.mjs diz OWNER_ID=%s" % dono_acesso)
    caso("AU9b_e_os_dois_NAO_concordam",
         bool(dono_acesso) and bool(dono_catalogo)
         and dono_acesso != dono_catalogo,
         "catalogo diz %s · contrato de acesso diz %s — escolher um seria "
         "inventar identidade" % (dono_catalogo, dono_acesso))

    # ── AU10 · E NINGUEM, EM RUNTIME, PODE ESCREVER IDENTIDADE ───────────
    #
    # Mesmo que a autoridade existisse, nao ha quem a materialize: os unicos
    # escritores de `organizacao`, `pessoa`, `origem` e `canal` sao ensaios
    # SQL, provas e fixtures de teste.
    escritores = escritores_de_identidade_em_runtime()
    caso("AU10_nenhuma_gaveta_de_runtime_escreve_identidade",
         escritores == [],
         "zero escritores em coleta/, guarda/, admissao/, leis/, medidas/, "
         "regras/, orquestrador/, ferramentas/, fontes/, pedido/, pacote/"
         if not escritores else "apareceram: %s" % escritores)

    # ── AU7 · o que faltaria AINDA DEPOIS de promover ────────────────────
    #
    # Isto e o achado que poupa a proxima missao: promover a fonte NAO chega.
    # O schema exige `organizacao.tipo` de um vocabulario de nove; o catalogo
    # fala outro, de doze. Ninguem declarou a traducao — e a prova da M2
    # escolheu `orgao_publico` para `OFFICIAL_REGIONAL_AGENCY` por conta
    # propria.
    #
    #     UMA TRADUCAO QUE NINGUEM DECLAROU E UMA DECISAO QUE NINGUEM ASSINOU.
    tipos = tipos_que_o_schema_aceita()
    kinds = owner_kinds_do_candidato()
    sem_traducao = sorted(k for k in kinds if k.lower() not in tipos)
    caso("AU7a_os_dois_vocabularios_de_especie_nao_se_encontram",
         bool(tipos) and bool(kinds) and len(sem_traducao) == len(kinds),
         "schema aceita %d tipos; o catalogo fala %d OWNER_KIND, e NENHUM "
         "coincide" % (len(tipos), len(kinds)))
    caso("AU7b_e_a_traducao_usada_na_prova_da_M2_nao_esta_declarada",
         "OFFICIAL_REGIONAL_AGENCY" in sem_traducao,
         "OFFICIAL_REGIONAL_AGENCY -> 'orgao_publico' foi escolha de quem "
         "escreveu a prova, e nao de um contrato")

    # ── AU8 · nada foi escrito ao medir ──────────────────────────────────
    url = os.environ.get("BANCO_DESCARTAVEL_URL") or ""
    if url:
        import importlib.util as u
        spec = u.spec_from_file_location(
            "pgprova", os.path.join(RAIZ, "provas",
                                    "preservar_coleta_no_postgres.py"))
        pg = u.module_from_spec(spec)
        spec.loader.exec_module(pg)
        if not pg._e_descartavel(url):
            raise SystemExit("RECUSADO: '%s' nao e um banco descartavel local."
                             % url)
        for n in ("001", "002"):
            pasta = os.path.join(RAIZ, "supabase", "migrations")
            alvo = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")][0]
            subprocess.run(["psql", url, "-q", "-f", os.path.join(pasta, alvo)],
                           capture_output=True, text=True)
        contagens = {}
        for t in TABELAS_DE_IDENTIDADE:
            r = subprocess.run(["psql", url, "-tA", "-c",
                                "select count(*) from public.%s" % t],
                               capture_output=True, text=True)
            contagens[t] = r.stdout.strip() if r.returncode == 0 else "?"
        caso("AU8_medir_a_autoridade_nao_escreve_identidade_nenhuma",
             all(v == "0" for v in contagens.values()),
             "linhas depois de medir: %s"
             % ", ".join("%s=%s" % kv for kv in sorted(contagens.items())))
    else:
        print("  (AU8 PULADO — sem BANCO_DESCARTAVEL_URL. Pulado nao e provado.)")

    # ── O RELATORIO ──────────────────────────────────────────────────────
    print()
    mal = [n for n, ok, _d in fora if not ok]
    for nome, ok, detalhe in fora:
        print("  %s  %-56s %s" % ("PASS" if ok else "FAIL", nome, detalhe))
    print("=" * 70)
    veredito = "UNRESOLVED" if sem == "UNRESOLVED" else "RESOLVED"
    print("AUTORIDADE_DA_FONTE=%s" % ("PASS" if not mal else "FAIL"))
    print("SOURCE_AUTHORITY[%s] = %s" % (A_FONTE_DA_M2, veredito))
    print()
    print("  MISSING_AUTHORITY, com nome:")
    print("    1 · %s nao tem ficha em docs/fontes/ATLAS-DE-FONTES-EAME.md," %
          A_FONTE_DA_M2)
    print("        que e o registo canonico — e quem o diz e o scanner da casa.")
    print("    2 · nao tem contrato em docs/operacao/CONTRATOS-DAS-FONTES-EAME.md,")
    print("        que declara OWNER para %d fontes e nao para esta."
          % len(contratos))
    print("    3 · nao ha traducao declarada de OWNER_KIND para organizacao.tipo,")
    print("        e sem ela nem uma fonte promovida se materializa sozinha.")
    print()
    print("  O QUE ISTO NAO CONCLUI: que a relacao esteja errada. ARPAV publica")
    print("  mesmo aquele boletim. O que falta nao e verdade — e AUTORIDADE.")
    print("  UNKNOWN HONESTO > IDENTIDADE INVENTADA.")
    return 0 if not mal else 1


if __name__ == "__main__":
    raise SystemExit(main())
