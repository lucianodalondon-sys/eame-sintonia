#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · VALIDADOR

    UMA LEI SEM DENTES E UM PEDIDO POR FAVOR.

`AGENTS.md` manda manter o mapa sincronizado com o repositorio. Este ficheiro e
o que torna essa frase verificavel: ele roda no CI, em cada mudanca, e REPROVA.

Falha fechado. Erro inesperado tambem e FAIL, pela mesma razao que o portao da
build falha fechado: dar a sensacao de guarda com a garantia de nenhuma e pior
do que nao ter guarda.

O QUE ELE PROVA
---------------
  P1  o mapa commitado e o mesmo que o repositorio de hoje produz  ← anti-drift
  P2  nenhum ID repetido
  P3  nenhuma ligacao apontando para peca que nao existe
  P4  todo ficheiro declarado existe mesmo
  P5  nenhuma ligacao tecnica sem linha de codigo que a prove
  P6  nenhum verde sem a prova propria do tipo
  P7  o NAO SEI sobreviveu (nao foi convertido em verde nem escondido)
  P8  nenhum ficheiro com dois donos
  P9  todo ficheiro de codigo tem dono declarado                    ← anti-drift
  P10 status so pode ser um dos quatro valores conhecidos

P1 e P9 sao os dois que impedem "depois alguem atualiza o mapa": criar um script
novo em `scripts/` sem o declarar reprova; mudar codigo sem regerar reprova.
"""

import glob
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "system-map" / "data"
AQUI = Path(__file__).parent

VALIDOS = {"PROVEN", "PENDING", "BROKEN", "UNKNOWN"}
falhas: list[str] = []
provas: list[str] = []


def prova(id_: str, o_que: str, ok: bool, detalhe: str = ""):
    provas.append(f"  {'PASS' if ok else 'FAIL'}  {id_:22s} {o_que}")
    if not ok:
        falhas.append(f"{id_}: {o_que}" + (f"\n        {detalhe}" if detalhe else ""))
        if detalhe:
            provas.append(f"        {detalhe}")


def mentiras_sobre_existencia(declarado, nos, raiz):
    """As pecas dadas por INEXISTENTES com o ficheiro no DISCO.

    ⚠️ ESTA FUNCAO ESTA SEPARADA DA `main()` DE PROPOSITO.

    O validador REGENERA o estado antes de o validar (e a P1, anti-drift). Isso
    e certo — e torna impossivel testar esta guarda injectando uma mentira no
    ficheiro `state.generated.json`: a regeneracao apaga a injecção antes de a
    guarda a ver.

    Uma guarda que so pode ser exercitada pelo caminho que a apaga e uma guarda
    que ninguem consegue provar que morde. Por isso ela e uma funcao pura de
    (declarado, nos, disco), e o teste chama-a com um estado sintetico.

    Pergunta ao DISCO, e parte dos caminhos DECLARADOS — nao da lista resolvida,
    que numa peca acusada de inexistente esta vazia.
    """
    fora = []
    for c in declarado.get("COMPONENTS", []):
        n = nos.get(c["id"])
        if n is None or n.get("status") != "BROKEN":
            continue
        no_disco = [p for p in c.get("files", [])
                    if (Path(raiz) / p).exists()
                    or glob.glob(str(Path(raiz) / p), recursive=True)]
        if no_disco:
            fora.append("%s diz BROKEN e %s esta no disco"
                        % (c["id"], no_disco[0]))
    return fora


def main() -> int:
    # ── P1 · anti-drift: regerar e comparar com o que esta commitado ─────────
    def arquitetura(nome: str):
        """O conteudo SEM o bloco de proveniencia.

        HEAD e BRANCH mudam a cada commit e a cada ramo. Compara-los faria o
        portao reprovar toda a gente, sempre. O que tem de bater e a
        arquitetura; o carimbo de quem correu e informativo.
        """
        f = DADOS / nome
        if not f.exists():
            return None
        d = json.loads(f.read_text(encoding="utf-8"))
        d.pop("PROVENANCE", None)
        return json.dumps(d, ensure_ascii=False, sort_keys=True)

    SERVIDO = RAIZ / "italia-portale" / "client" / "system-map"

    def sem_proveniencia(f: Path):
        if not f.exists():
            return None
        d = json.loads(f.read_text(encoding="utf-8"))
        d.pop("PROVENANCE", None)
        return json.dumps(d, ensure_ascii=False, sort_keys=True)

    antes = {n: arquitetura(n)
             for n in ("architecture.generated.json", "sources.generated.json",
                       "state.generated.json")}
    # A COPIA SERVIDA entra na mesma comparacao. E ela que o cliente abre: se
    # so o ficheiro de dados fosse conferido, alguem podia regerar, commitar os
    # dados e servir a app antiga — e o URL publico mostrava um mapa que ja nao
    # existe, com o carimbo a dizer que estava em dia.
    def servido(n: str):
        f = SERVIDO / n
        if not f.exists():
            return None
        return sem_proveniencia(f) if n.endswith(".json") else f.read_text(encoding="utf-8")

    # A LISTA DO QUE E SERVIDO VEM DA CADEIA, nao daqui. Enquanto estava escrita
    # neste ficheiro, acrescentar `freshness.js` a app deixava-o FORA da conferencia
    # anti-drift: alguem podia regerar os dados, commitar, e servir uma versao
    # antiga da lei da frescura — o pior sitio possivel para uma copia velha.
    CADEIA = json.loads((AQUI / "CADEIA-DO-MAPA.json").read_text(encoding="utf-8"))
    servido_antes = {n: servido(n) for n in CADEIA["PUBLICADO"]}

    # O INDICE DE FONTES tambem e gerado. Um indice commitado que ja nao bate com
    # o atlas de onde saiu e pior do que nao ter indice: quem o le acredita nele.
    INDICE = RAIZ / "docs" / "fontes" / "INDICE-DE-FONTES.md"
    indice_antes = INDICE.read_text(encoding="utf-8") if INDICE.exists() else None
    # A porta de entrada das reguas tambem e gerada. Uma porta desatualizada e
    # pior que nenhuma: quem a le acredita nela.
    PORTA = RAIZ / "regras" / "LEIA-ANTES-DE-COLETAR.md"
    porta_antes = PORTA.read_text(encoding="utf-8") if PORTA.exists() else None

    # A ordem importa: `scan_sources.py` le a saida de `scan_repo.py`, e o
    # gerador le as duas. Correr fora de ordem daria um mapa montado sobre uma
    # medicao anterior — e o pior tipo de erro, porque passa sem reclamar.
    for script in ("scan_repo.py", "scan_sources.py", "scan_casco.py",
                   "generate_system_map.py"):
        r = subprocess.run([sys.executable, str(AQUI / script)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            prova("P1_REGERA", f"{script} correu sem erro", False, r.stderr.strip()[:400])
            return relatar()

    def onde_difere(a: str, b: str, limite: int = 4) -> list:
        """As primeiras chaves em que dois JSON deixam de ser iguais.

        «REGERAR MUDOU architecture.generated.json» nao chega para consertar nada.
        Fica-se a saber que ha diferenca e nao QUAL — e passei tres tentativas a
        adivinhar, com o CI a reprovar de cada vez. Um portao que diz «esta
        errado» sem dizer onde obriga quem o le a trabalhar as cegas, e o custo
        disso e sempre maior do que o de imprimir o caminho.
        """
        import json as _json

        def caminhos(o, prefixo=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield from caminhos(v, f"{prefixo}.{k}")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    yield from caminhos(v, f"{prefixo}[{i}]")
            else:
                yield prefixo, o

        try:
            da, db = _json.loads(a), _json.loads(b)
        except (ValueError, TypeError):
            return []
        va, vb = dict(caminhos(da)), dict(caminhos(db))
        fora = []
        for k in list(va) + [k for k in vb if k not in va]:
            if va.get(k) != vb.get(k):
                fora.append(f"{k}: commitado={str(va.get(k))[:40]} "
                            f"regerado={str(vb.get(k))[:40]}")
            if len(fora) >= limite:
                break
        return fora

    mudou = []
    detalhe_do_drift = []
    for n, texto in antes.items():
        agora = arquitetura(n)
        if texto != agora:
            mudou.append(n)
            if n.endswith(".json"):
                detalhe_do_drift += onde_difere(texto, agora)
    for n, texto in servido_antes.items():
        atual = servido(n)
        fonte = ((RAIZ / "system-map" / "app" / n).read_text(encoding="utf-8")
                 if not n.endswith(".json") and (RAIZ / "system-map" / "app" / n).exists() else None)
        if texto != atual or (fonte is not None and fonte != atual):
            mudou.append(f"servido/{n}")
    if indice_antes != (INDICE.read_text(encoding="utf-8") if INDICE.exists() else None):
        mudou.append("docs/fontes/INDICE-DE-FONTES.md")
    if porta_antes != (PORTA.read_text(encoding="utf-8") if PORTA.exists() else None):
        mudou.append("regras/LEIA-ANTES-DE-COLETAR.md")
    prova("P1_SEM_DRIFT", "o mapa commitado corresponde ao repositorio de hoje",
          not mudou,
          ("regerar mudou " + ", ".join(mudou) +
           ("\n        primeira diferenca: " + "\n        ".join(detalhe_do_drift)
            if detalhe_do_drift else "") +
           "\n        ALGUEM MEXEU NA ARQUITETURA E NAO ATUALIZOU O MAPA."
           "\n        Conserto: py system-map/scripts/generate_system_map.py && git add system-map/data")
          if mudou else "")

    S = json.loads((DADOS / "state.generated.json").read_text(encoding="utf-8"))
    G = json.loads((DADOS / "architecture.generated.json").read_text(encoding="utf-8"))
    nos = {n["id"]: n for n in S["NODES"]}
    existentes = {f["path"] for f in G["FILES"]}

    # ── P2 · ids unicos ──────────────────────────────────────────────────────
    ids = [n["id"] for n in S["NODES"]]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    prova("P2_IDS_UNICOS", "nenhuma peca com id repetido", not dup, ", ".join(dup))

    terr = {t["id"] for t in S["TERRITORIES"]}
    sem_terr = sorted({n["id"] for n in S["NODES"] if n["territory"] not in terr})
    prova("P2_TERRITORIO", "toda peca vive num territorio que existe",
          not sem_terr, ", ".join(sem_terr))

    # ── P2b · toda zona pertence a uma das tres partes ───────────────────────
    # COLETA -> INTELIGENCIA -> ENTREGA e a leitura mais simples que este mapa
    # tem. Uma zona sem familia seria um bloco sem cor, a flutuar fora da
    # historia — e a proxima pessoa a criar uma zona nao vai lembrar-se desta
    # regra sozinha.
    fams = {f["id"] for f in S["FAMILIES"]}
    orfas = sorted(z["id"] for z in S["TERRITORIES"] if z.get("family") not in fams)
    prova("P2_ZONA_TEM_FAMILIA",
          "toda zona pertence a COLETA, INTELIGENCIA ou ENTREGA",
          not orfas, ", ".join(orfas))

    sem_fam = sorted({n["id"] for n in S["NODES"] if n.get("family") not in fams})
    prova("P2_PECA_TEM_FAMILIA", "toda peca herda a familia da sua zona",
          not sem_fam, ", ".join(sem_fam[:8]))

    # ── P2c · A PRATELEIRA BATE COM O MAPA ───────────────────────────────────
    #
    #     ESTA E A LEI. O VISUAL TEM DE ESTAR 100% DE ACORDO COM O PROJETO.
    #
    # Enquanto os 149 scripts viviam empilhados numa pasta so, o mapa podia dizer
    # "isto e uma regra" e "aquilo e uma ferramenta" sem que nada no repositorio
    # confirmasse. Duas verdades sobre a mesma coisa — e a que se ve primeiro ao
    # abrir a pasta era a errada.
    #
    # Agora cada zona tem a sua gaveta, e este portao recusa qualquer ficheiro que
    # esteja numa gaveta que nao e a da sua peca. Mover um ficheiro sem mover a
    # peca no mapa reprova. Mudar a peca de zona sem mover o ficheiro reprova.
    # Nao ha como as duas verdades voltarem a divergir em silencio.
    gavetas = {z["folder"] for z in S["TERRITORIES"] if z.get("folder")}
    pasta_da_zona = {z["id"]: z.get("folder") for z in S["TERRITORIES"]}
    fora_do_lugar = []
    for n in S["NODES"]:
        certa = pasta_da_zona.get(n["territory"])
        for f in n["files"]:
            g = f.split("/")[0]
            if g in gavetas and g != certa:
                fora_do_lugar.append(f"{f} esta em {g}/ e a peca «{n['name']}» "
                                     f"mora em {certa or 'nenhuma gaveta'}/")
    prova("P2_PASTA_BATE_COM_MAPA",
          "todo ficheiro esta na gaveta da sua peca",
          not fora_do_lugar,
          "\n        ".join(fora_do_lugar[:8]) +
          ("\n        A PRATELEIRA E O MAPA TEM DE CONTAR A MESMA HISTORIA."
           if fora_do_lugar else ""))

    # ── P3 · ligacoes apontam para peca existente ────────────────────────────
    soltas = sorted({f"{e['from']}->{e['to']}" for e in S["EDGES"]
                     if e["from"] not in nos or e["to"] not in nos})
    prova("P3_SEM_PONTA_SOLTA", "nenhuma ligacao aponta para peca inexistente",
          not soltas, ", ".join(soltas[:6]))

    deps = set(S["DEPARTMENTS"])
    b_ruins = sorted({f"{e['from']}->{e['to']}" for e in S["BUSINESS_EDGES"]
                      if e["from"] not in nos
                      or not (e["to"].startswith("DEPT:") and e["to"][5:] in deps)})
    prova("P3_NEGOCIO_VALIDO", "toda ligacao de negocio liga peca real a departamento real",
          not b_ruins, ", ".join(b_ruins))

    # ── P4 · ficheiro declarado existe ───────────────────────────────────────
    fantasmas = sorted({f for n in S["NODES"] for f in n["files"] if f not in existentes})
    prova("P4_FICHEIROS_REAIS", "todo ficheiro citado pelo mapa existe no repositorio",
          not fantasmas, ", ".join(fantasmas[:6]))

    # ── P4b · o mapa nao pode MENTIR sobre inexistencia ──────────────────────
    # ⚠️ POR QUE A P4 SOZINHA NAO CHEGAVA, E DEIXOU PASSAR UMA MENTIRA.
    #
    # A P4 percorre `n["files"]` — a lista RESOLVIDA — e compara-a com
    # `existentes`, que sai de `architecture.generated.json`. Duas cegueiras
    # empilhadas:
    #
    #   1. `existentes` vem de `scan_repo.py`, que lista com `git ls-files`.
    #      E o inventario do GIT, nao do DISCO. Comparar o gerado com o gerado
    #      prova que o gerador e coerente consigo proprio — nao que ele diz a
    #      verdade sobre o repositorio.
    #
    #   2. quando uma peca e acusada de nao existir, `files` fica VAZIA. A P4
    #      itera zero ficheiros e PASSA. A peca falsamente partida e invisivel
    #      justamente para a prova que existia para a apanhar.
    #
    # Em 08/09/2026 isso publicou C-CENSO-OBSERVABILIDADE como BROKEN com
    # «nao existe no repositorio», com o ficheiro no disco — e o
    # SYSTEM_MAP_CHECK deu PASS na mesma.
    #
    #     GENERATED == EXPECTED GENERATOR OUTPUT
    #     NAO E
    #     GENERATED == REAL FILE EXISTENCE.
    #
    # Esta prova pergunta ao DISCO, e parte dos caminhos DECLARADOS.
    declarado = json.loads(
        (DADOS / "architecture.declared.json").read_text(encoding="utf-8"))
    mentiras = mentiras_sobre_existencia(declarado, nos, RAIZ)
    prova("P4_NAO_MENTIR_SOBRE_EXISTENCIA",
          "nenhuma peca e dada por inexistente com o ficheiro no disco",
          not mentiras,
          ("\n        ".join(mentiras[:6]) +
           "\n        EXISTE NO DISCO != RASTREADO PELO GIT != NAO EXISTE."
           "\n        Conserto: `git add` o ficheiro e regerar — ou corrigir o"
           " caminho declarado.") if mentiras else "")

    # ── P5 · aresta tecnica sem prova nao existe ─────────────────────────────
    sem_prova = [f"{e['from']}->{e['to']} ({e['type']})" for e in S["EDGES"]
                 if e.get("kind") == "technical" and not e.get("evidence")]
    prova("P5_ARESTA_PROVADA", "nenhuma ligacao tecnica sem linha de codigo que a prove",
          not sem_prova, ", ".join(sem_prova[:6]))

    mal_formada = [f"{e['from']}->{e['to']}" for e in S["EDGES"]
                   for ev in e.get("evidence", [])
                   if not (ev.get("file") in existentes and isinstance(ev.get("line"), int))]
    prova("P5_PROVA_APONTAVEL", "toda prova aponta para ficheiro e linha que existem",
          not mal_formada, ", ".join(sorted(set(mal_formada))[:6]))

    # ── P5c · a linha citada tem de DIZER alguma coisa ───────────────────────
    # A P5 acima so exige que o numero caiba no ficheiro, e isso deixa passar o
    # envelhecimento silencioso: a prova mais importante da fronteira da coleta
    # (C-ADMISSAO -> C-READY) apontava para `admissao/admissao.py:391` com um
    # `snippet` escrito a mao. A funcao mudou de sitio, a linha 391 ficou EM
    # BRANCO, e nenhum portao reparou — porque a linha existe.
    #
    #     UMA PROVA QUE APONTA PARA UMA LINHA EM BRANCO NAO E UMA PROVA.
    #
    # So se recusa o indecidivel-por-omissao: linha vazia ou feita so de
    # fecho de parenteses, virgulas e aspas. O que ela diz continua a ser
    # julgado por gente.
    _cache_l: dict = {}

    def _linha(f: str, n: int):
        if f not in _cache_l:
            try:
                _cache_l[f] = (RAIZ / f).read_text(
                    encoding="utf-8", errors="replace").splitlines()
            except OSError:
                _cache_l[f] = []
        L = _cache_l[f]
        return L[n - 1] if 0 < n <= len(L) else None

    _trivial = __import__("re").compile(r"^[\s\)\]\}\,\'\";:]*$")
    ocas = [f"{e['from']}->{e['to']} ({ev['file']}:{ev['line']})"
            for e in S["EDGES"] for ev in e.get("evidence", [])
            if isinstance(ev.get("line"), int) and ev.get("file") in existentes
            and (_l := _linha(ev["file"], ev["line"])) is not None
            and _trivial.match(_l)]
    prova("P5_PROVA_TEM_CONTEUDO", "nenhuma prova aponta para linha sem conteudo",
          not ocas, ", ".join(sorted(set(ocas))[:6]))

    # ── P6 · verde exige prova, nunca "o ficheiro existe" ────────────────────
    verde_frouxo = [n["id"] for n in S["NODES"]
                    if n["status"] == "PROVEN"
                    and not (n["inbound"] or n["outbound"])
                    # Peca de FACTO (linhagem, fonte) prova-se por documento
                    # nomeado ou por medicao do git — nao por import. Exigir-lhe
                    # uma aresta seria exigir a prova errada. Mas so escapa quem
                    # DIZ de onde vem a certeza: "eu sei" nao e valor aceite.
                    and not (n.get("proof") == "document" and n["files"])
                    and not (n.get("proof") == "git-measurement")]
    prova("P6_VERDE_TEM_PROVA", "nenhum verde so por o ficheiro existir",
          not verde_frouxo, ", ".join(verde_frouxo))

    # Quem nao tem aresta nenhuma TEM de dizer em que documento se apoia.
    sem_tipo = [n["id"] for n in S["NODES"]
                if not n["inbound"] and not n["outbound"]
                and n["status"] == "PROVEN"
                and n.get("proof") not in ("document", "git-measurement")]
    prova("P6_FACTO_DIZ_A_PROVA",
          "peca sem ligacao so pode ser verde se disser em que documento se apoia",
          not sem_tipo, ", ".join(sem_tipo))

    sem_doc = [n["id"] for n in S["NODES"]
               if n.get("proof") == "document" and not n["files"]]
    prova("P6_DOCUMENTO_EXISTE",
          "peca que se apoia num documento cita um ficheiro que existe",
          not sem_doc, ", ".join(sem_doc[:8]))

    verde_stale = [n["id"] for n in S["NODES"]
                   if n["status"] == "PROVEN" and n.get("changed_since_declared")]
    prova("P6_VERDE_NAO_E_VELHO", "nenhum verde sobre ficheiro que mudou depois de declarado",
          not verde_stale, ", ".join(verde_stale))

    # ── P7 · o NAO SEI sobreviveu ────────────────────────────────────────────
    # Um mapa em que tudo e verde nao esta saudavel: esta a esconder.
    expected_verde = [f"{e['from']}->{e['to']}" for e in S["EDGES"]
                      if e.get("kind") == "expected" and e["status"] != "UNKNOWN"]
    prova("P7_NAO_SEI_VIVE", "ligacao declarada e nao provada continua sendo NAO SEI",
          not expected_verde, ", ".join(expected_verde))

    # ── P8 · um ficheiro, um dono ────────────────────────────────────────────
    conf = [f"{c['file']} ({' e '.join(c['claimed_by'])})" for c in S["OWNERSHIP_CONFLICTS"]]
    prova("P8_UM_DONO", "nenhum ficheiro reivindicado por duas pecas",
          not conf, "; ".join(conf[:6]))

    # ── P8b · o dono decidido por gente e o unico que escreve ───────────────
    # O dono eleito por ordem alfabetica muda sozinho quando alguem renomeia uma
    # peca. Onde ha decisao humana em `CANONICAL_OWNERS`, ela e lei — e esta
    # prova mede se o CODIGO a respeita, e nao se o cartao a repete.
    #
    #     MUDAR O CARTAO NAO E MUDAR A ARQUITETURA.
    viol = [f"{v['file']}: declarado {v['declared_owner']}, escrevem "
            f"{', '.join(v['written_by']) or 'NINGUEM'} [{v['verdict']}]"
            for v in S.get("CANONICAL_OWNER_VIOLATIONS", [])]
    prova("P8_DONO_CANONICO", "so o dono declarado escreve o artefato dele",
          not viol, "; ".join(viol[:4]))

    # ── P9 · anti-drift: codigo novo tem de ser declarado ────────────────────
    orfaos = S["UNCLAIMED_CODE_FILES"]
    prova("P9_CODIGO_DECLARADO", "todo ficheiro de codigo pertence a uma peca do mapa",
          not orfaos,
          (f"{len(orfaos)} ficheiro(s) de codigo que o mapa nao conhece:\n        "
           + "\n        ".join(orfaos[:10]) +
           "\n        CODIGO NOVO SEM PECA NO MAPA E ARQUITETURA INVISIVEL."
           "\n        Conserto: declare-o em system-map/data/architecture.declared.json")
          if orfaos else "")

    # ── P10 · vocabulario de status fechado ──────────────────────────────────
    maus = sorted({n["status"] for n in S["NODES"]} - VALIDOS)
    prova("P10_STATUS_VALIDO", "todo status e um dos quatro valores conhecidos",
          not maus, ", ".join(maus))

    return relatar(S.get("ARTEFACT_MULTIPLE_AUTHORS", []))


def relatar(varios_autores: list | tuple = ()) -> int:
    print("\n".join(provas))

    # ── OBSERVACAO · o artefacto escrito por mais de uma peca ────────────────
    # Nao e prova, e por isso nao reprova: nao ha lei nesta casa que proiba dois
    # autores para o mesmo ficheiro. Mas o mapa tem de eleger UM dono, e elege
    # por ordem alfabetica — o dono muda sozinho quando alguem renomeia uma
    # peca. Isto diz, em voz alta, onde a resposta a pergunta «de quem e isto?»
    # esta a ser dada por um sorteio.
    if varios_autores:
        print("\n" + "-" * 70)
        print(f"OBSERVACAO · {len(varios_autores)} artefacto(s) com MAIS DE UM autor:")
        for v in varios_autores:
            print(f"  · {v['file']}")
            print(f"      escrito por {', '.join(v['written_by'])}"
                  f" · dono eleito por ordem alfabetica: {v['owner_elected']}")
        print("  UM DONO ELEITO POR ORDEM ALFABETICA NAO E UM DONO."
              "\n  Quem decide e gente, e a decisao vai em architecture.declared.json.")

    if falhas:
        print("\n" + "=" * 70)
        print(f"SYSTEM_MAP_CHECK=FAIL · {len(falhas)} prova(s) reprovada(s)")
        print("=" * 70)
        for f in falhas:
            print(f"  · {f}")
        print("\nO mapa e derivado do repo. O repo nao e derivado do mapa.")
        print("Leia AGENTS.md antes de mexer.")
        return 1
    print("\nSYSTEM_MAP_CHECK=PASS · o mapa corresponde ao repositorio")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # falha fechado, sempre
        print(f"SYSTEM_MAP_CHECK=FAIL · erro inesperado no validador: {e}", file=sys.stderr)
        raise SystemExit(1)
