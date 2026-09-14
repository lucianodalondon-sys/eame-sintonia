#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRESERVAR A EVIDENCIA — «CAN DO != DID DO».

A missao anterior DESCREVEU exemplos reais. Descrever nao e' preservar: quem
herdar a lista nao pode reabrir a minha frase, so' pode reabrir um ficheiro.
O §9 e' explicito — se o exemplo foi so' descrito, preservar agora.

O QUE ESTE FICHEIRO GUARDA, POR FONTE
-------------------------------------
    pagina.html      o corpo servido, byte a byte
    exemplo.json     titulo, rota, tipo, data observada, rota de saida
    sha256           do corpo, para se poder provar que nao mudou

E O AVISO DO §119.2, QUE E' O MAIS FACIL DE IGNORAR
---------------------------------------------------
Seis dos 140 exemplos guardados na missao paralela passaram em todas as
verificacoes mecanicas — existiam, estavam na propria pagina, a URL batia — e
eram:

    «Codice Etico» · «Termini e condizioni» · «Company Info»

Verdadeiros, presentes, e prova de coisa nenhuma. Por isso aqui ha uma tabela
de RECUSA de rodape: um exemplo que casa com ela nao vale, por mais real que
seja.

⚠️ E A ROTA DE SAIDA, QUE EU ERREI NA MISSAO PASSADA
---------------------------------------------------
A migration 020 escreve a lei: «UM 200 NAO DIZ NADA SOBRE A ROTA SE VOCE NAO
SABE POR ONDE SAIU». Eu declarei «saida direta, sem proxy» na missao anterior
depois de olhar so' a variavel HTTPS_PROXY — que estava vazia. Medido agora
pelo IP publico: a saida desta maquina e' `149.22.91.179`, Palermo, Sicilia,
ITALIA. Havia VPN italiana ligada e eu nao sabia — o mesmo erro que a migration
020 documenta ter acontecido em 02/09/2026 com a ISMEA.

Consequencia: tudo o que eu validei abre POR ROTA ITALIANA. Nao esta provado
que abra de outra saida, e o coletor de producao pode nao sair por Italia.
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-promover")
EVID = RAIZ / "data" / "samples" / "IT-SOURCE-EVIDENCE-2026-09-14"

from italy_fechar_sonda import baixar, CAB                      # noqa: E402

# ── RECUSA DE RODAPE: o aviso do §119.2, virado em codigo ──────────────────
LIXO = re.compile(
    r"codice etico|termini e condizioni|company info|privacy policy|"
    r"informativa privacy|note legali|cookie|accessibilit|mappa del sito|"
    r"amministrazione trasparente|dichiarazione di accessibilit|"
    r"^home$|^contatti$|^chi siamo$|^login$|^cerca$|credits|"
    r"posta elettronica certificata|^pec$|^urp$|whistleblowing", re.I)

# ── O QUE FAZ UM EXEMPLO VALER: fala do assunto E tem data ────────────────
ASSUNTO = re.compile(
    r"bollettin|notiziario|avvis|fenolog|bbch|fitosanitar|agrometeo|"
    r"difesa integrata|produzione integrata|monitoraggio|coltur|"
    r"prezz|quotazion|mercat|superfici|produzion|giacenz|"
    r"sostanza attiva|etichetta|autorizzaz|registro|deroga|"
    r"emergenz|sorveglianz|dataflow|coltivazioni|maturazion|vendemmia|"
    r"mais|soia|pomodoro|frumento|grano|vite|olivo", re.I)

DATA = re.compile(
    r"(?:\b(?:3[01]|[12]\d|0?[1-9])[/\-\.](?:1[0-2]|0?[1-9])[/\-\.]20[12]\d\b)"
    r"|(?:\b20[12]\d[/\-](?:1[0-2]|0?[1-9])[/\-](?:3[01]|[12]\d|0?[1-9])\b)"
    r"|(?:\b(?:3[01]|[12]\d|0?[1-9])\s+(?:gennaio|febbraio|marzo|aprile|maggio|"
    r"giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+20[12]\d\b)"
    r"|(?:\bn[.°º]?\s*\d{1,3}\s+del\s+\d{1,2})", re.I)


# ── O TOPICO QUE PROVA, SEPARADO DO QUE SO' PARECE ────────────────────────
# «avviso» casa com qualquer aviso — inclusive «Avviso del 08/06/2026 —
# Concorso per 374 funzionari», que e' um concurso publico e apareceu como
# prova de que o MASAF publica existencias de vinho. E' o §119.2 outra vez,
# e por isso o topico ESPECIFICO e o GENERICO nao valem o mesmo.
TOPICO_FORTE = re.compile(
    r"bollettin|notiziario|fenolog|bbch|fitosanitar|agrometeo|"
    r"difesa integrata|produzione integrata|disciplinare|deroga|"
    r"giacenz|cantina italia|prezzi dei mezzi|costi di produzione|"
    r"coltivazioni|dataflow|maturazion|vendemmia|"
    r"peronospora|oidio|flavescenz|diabrotica|piralide|popillia|"
    r"mais|soia|pomodoro|frumento|grano (tenero|duro)|vite|olivo", re.I)

# o que desqualifica um titulo mesmo estando datado e no sitio certo
FORA_DO_ASSUNTO = re.compile(
    r"concorso|bando di concorso|funzionari|assunzion|selezione pubblica|"
    r"graduatoria|gara d'appalto|avviso di gara|nomina|"
    r"formazione per|corso di formazione|convegno di presentazione", re.I)


def graduar(tipo, titulo):
    """Tres graus, e so' o primeiro fecha o gate de REGISTRADA.

        FORTE        tem DATA e topico ESPECIFICO -> prova que a fonte publica
                     aquilo, com quando
        FRACA        tem uma das duas coisas, nao as duas
        INSUFICIENTE nao prova nada, ou esta fora do assunto

    O grau nao e' opiniao: sai de duas perguntas mecanicas e da tabela de
    exclusao. E a tabela existe porque «Concorso per 374 funzionari» passou
    por prova de existencias de vinho.
    """
    if FORA_DO_ASSUNTO.search(titulo or ""):
        return ("INSUFICIENTE",
                "o titulo esta datado e no sitio certo, e fala de OUTRA coisa "
                "(concurso, nomeacao, formacao). Verdadeiro e irrelevante — "
                "exatamente o erro que o §119.2 mandou nao repetir.")
    tem_data = bool(DATA.search(titulo or ""))
    tem_topico = bool(TOPICO_FORTE.search(titulo or ""))
    if tem_data and tem_topico:
        anos, nota = idade_do_exemplo(titulo)
        if anos is not None and anos >= 2:
            return ("FORTE_MAS_ANTIGA", nota)
        if tipo == "FRASE_NO_CORPO":
            return ("FRACA", "tem data e topico, mas o «titulo» e' um fragmento "
                             "do corpo, nao um item publicado. Fragmento nao e' "
                             "edicao.")
        return ("FORTE", f"tem data E topico especifico, e {nota}")
    if tem_data:
        return ("FRACA", "tem data mas o topico e' generico. Prova que a casa "
                         "publica algo datado, nao que publique ISTO.")
    if tem_topico:
        return ("FRACA", "fala do assunto certo e NAO tem data. Prova a "
                         "materia, nao a recorrencia.")
    return ("INSUFICIENTE", "sem data e sem topico especifico.")


# ── E A IDADE DO EXEMPLO, QUE E' A TERCEIRA PERGUNTA ──────────────────────
# Um exemplo datado prova que a fonte PUBLICOU. Nao prova que ela publica
# AINDA. Medido em 14/09/2026, nas cinco evidencias de grau FORTE:
#
#   Valle d'Aosta   «Avviso del 19 giugno 2026»                    3 meses
#   RRN fenologia   «Bollettino fenologico - 10 settembre 2026»     4 DIAS
#   Veneto viticoli «Bollettino del 30 agosto 2024»                 2 anos
#   ARSAC           «...valido fino al 29 novembre 2022»            4 ANOS
#
# As duas ultimas doem porque na missao anterior eu declarei a ARSAC como
# «HIGH — semanal» e a recorrencia como OBSERVADA. Eu tinha visto seis titulos
# de 2026 — nos RESULTADOS DE BUSCA, nao na rota. A rota, aberta, serve 2022.
# Resultado de busca nao e' a pagina.
ANO_HOJE = 2026


def idade_do_exemplo(titulo):
    """Anos entre o ano mais recente citado no titulo e hoje."""
    # ⚠ ESTA LINHA ESTEVE QUEBRADA DE UM MODO INVISIVEL. Escrita por
    # heredoc do shell, o  virou um caractere de BACKSPACE (0x08) dentro
    # da regex, que compila, corre e NUNCA casa. Os dois exemplos velhos
    # (2024 e 2022) passavam como recentes. E a ferramenta de leitura nao
    # mostra o defeito: backspace nao se ve. Regex que nao casa nada nao
    # acusa erro; devolve lista vazia, e lista vazia parece «sem ano».
    anos = [int(a) for a in re.findall(r"(20[12]\d)", titulo or "")]
    if not anos:
        return (None, "sem ano legivel no titulo")
    a = max(anos)
    d = ANO_HOJE - a
    if d <= 1:
        return (d, f"exemplo de {a}: recente")
    return (d, f"⚠️ exemplo de {a}, ha {d} anos. Prova que a fonte PUBLICOU; "
               "nao prova que publica AINDA.")


def _bruto(url, timeout=30):
    """Bytes crus, com gzip desfeito. O HTML e' preciso: o texto limpo nao serve.

    ⚠️ DUAS COISAS QUEBRARAM AQUI NA PRIMEIRA VERSAO.
    1) A medicao do IP publico morreu com «utf-8 codec can't decode byte 0x8b»
       — 0x8b e' gzip. Eu pedia gzip no cabecalho e nao o desfazia.
    2) Eu passava ao extrator o TEXTO LIMPO da cache da sonda, que nao tem
       etiquetas. Sem `<a>` e sem `<h2>`, o extrator caia sempre no ultimo
       recurso (frase no corpo) e devolvia fragmentos de menu — «orare al
       Servizio Fitosanitario Laboratorio». Verdadeiros, presentes, e prova de
       coisa nenhuma: o erro do §119.2, repetido por mim.
    """
    import gzip
    import ssl
    import urllib.request
    from italy_fechar_sonda import CTX
    req = urllib.request.Request(url, headers=CAB)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        b = r.read()
        if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
            try:
                b = gzip.decompress(b)
            except OSError:
                pass
        return b, r.status, r.geturl()


def rota_de_saida():
    """De onde a medicao sai. Sem isto o estado de acesso e' uma opiniao."""
    try:
        b, _, _ = _bruto("https://ipinfo.io/json", timeout=20)
        d = json.loads(b.decode("utf-8", "replace"))
        pais = d.get("country", "??")
        return ({"IT": "IT_VPN", "BR": "BR_DIRETO"}.get(pais, "OUTRA"),
                f"{d.get('ip')} · {d.get('city')}, {d.get('region')} ({pais}) · "
                f"{d.get('org', '')}")
    except Exception as e:                                       # noqa: BLE001
        return ("NAO_SEI", f"nao consegui medir o IP publico: {e}")


def candidatos_a_exemplo(html, texto):
    """Titulos plausiveis: o que tem assunto e data, e nao e' rodape."""
    achados = []
    # 1 · titulos de link (o padrao dos boletins: «Bollettino n.17 del 4/6/2026»)
    for m in re.finditer(r"<a[^>]*>(.{6,160}?)</a>", html, re.S | re.I):
        t = re.sub(r"<[^>]+>", " ", m.group(1))
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 8 or LIXO.search(t):
            continue
        if ASSUNTO.search(t) and DATA.search(t):
            achados.append(("LINK_DATADO", t))
    # 2 · titulos de cabecalho
    for m in re.finditer(r"<h[1-4][^>]*>(.{6,160}?)</h[1-4]>", html, re.S | re.I):
        t = re.sub(r"<[^>]+>", " ", m.group(1))
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 8 or LIXO.search(t):
            continue
        if ASSUNTO.search(t):
            achados.append(("CABECALHO_DATADO" if DATA.search(t)
                            else "CABECALHO", t))
    # 3 · frase do corpo com assunto e data, como ultimo recurso
    if not achados:
        for m in DATA.finditer(texto):
            j = max(0, m.start() - 110)
            frag = texto[j:m.end() + 40].strip()
            if ASSUNTO.search(frag) and not LIXO.search(frag):
                achados.append(("FRASE_NO_CORPO", frag))
                break
    # preferir link datado > cabecalho datado > cabecalho > frase
    ordem = {"LINK_DATADO": 0, "CABECALHO_DATADO": 1, "CABECALHO": 2,
             "FRASE_NO_CORPO": 3}
    achados.sort(key=lambda x: ordem[x[0]])
    return achados


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ded = json.loads((TRAB / "DEDUPE.json").read_text(encoding="utf-8"))
    rota, rota_prova = rota_de_saida()
    print(f"ROTA DE SAIDA MEDIDA: {rota}")
    print(f"  {rota_prova}")
    if rota == "IT_VPN":
        print("  ⚠️ SAIDA ITALIANA. Tudo o que abrir aqui abre POR ITALIA — e")
        print("     nao esta provado que abra de outra rota. A missao anterior")
        print("     declarou «saida direta» por olhar so' HTTPS_PROXY.")
    print()

    EVID.mkdir(parents=True, exist_ok=True)
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    linhas = []
    for d in ded["DEDUPE"]:
        url = d["URL_CANONICAL"]
        slug = re.sub(r"[^a-z0-9]+", "-",
                      d["INPUT_SOURCE"].lower())[:58].strip("-")
        pasta = EVID / slug
        estado, http, final, texto, nb = baixar(url)

        # ── O HTML CRU, buscado de novo. A cache da sonda guarda texto LIMPO,
        # e sem etiquetas o extrator nunca ve um titulo de link.
        html = ""
        try:
            b, _h, _f = _bruto(url)
            html = b.decode("utf-8", "replace")
        except Exception as e:                                   # noqa: BLE001
            html = ""
        cands = candidatos_a_exemplo(html or texto, texto)

        if estado != "OK" or not texto:
            linhas.append({**d, "EVIDENCE_PATH": "", "EXAMPLE_TITLE": "",
                           "EXAMPLE_TYPE": "", "OBSERVED_AT": agora,
                           "EXAMPLE_URL": final, "SHA256": "",
                           "ROTA_DE_SAIDA": rota,
                           "EVIDENCE_GRADE": "INSUFICIENTE",
                           "EVIDENCE_GRADE_PORQUE": "a rota nao entregou corpo",
                           "EVIDENCIA_ESTADO": "NAO_PRESERVADA",
                           "EVIDENCIA_PORQUE":
                               f"a rota nao entregou corpo ({estado}, HTTP {http})."})
            continue

        pasta.mkdir(parents=True, exist_ok=True)
        corpo = texto.encode("utf-8")
        sha = hashlib.sha256(corpo).hexdigest()
        (pasta / "pagina.txt").write_bytes(corpo)

        if cands:
            tipo, titulo = cands[0]
            grau, porque_grau = graduar(tipo, titulo)
            est = "PRESERVADA"
            porque = (f"{len(cands)} candidatos achados; escolhido o mais forte "
                      f"({tipo}). Rodape recusado pela tabela do §119.2. "
                      f"GRAU={grau}: {porque_grau}")
        else:
            tipo, titulo, grau = "", "", "INSUFICIENTE"
            porque_grau = "nenhum candidato sobreviveu a recusa de rodape"
            est = "PRESERVADA_SEM_EXEMPLO"
            porque = ("a pagina foi guardada, mas NENHUM titulo com assunto e "
                      "data sobreviveu a recusa de rodape. ⚠️ Sem exemplo, o "
                      "gate de REGISTRADA nao fecha — e e' isso que o §119.2 "
                      "manda nao disfarcar.")

        ex = {"SOURCE": d["INPUT_SOURCE"], "OWNER": d["OWNER"],
              "URL_CANONICAL": url, "EXAMPLE_URL": final,
              "EXAMPLE_TITLE": titulo, "EXAMPLE_TYPE": tipo,
              "EVIDENCE_GRADE": grau, "EVIDENCE_GRADE_PORQUE": porque_grau,
              "OBSERVED_AT": agora,
              "PUBLICATION_DATE": "NAO SEI — a data no titulo e' do boletim, "
                                  "nao necessariamente da publicacao",
              "WHAT_IT_PRODUCES": d.get("RAW_NEEDS_SUPPORTED", "")[:400],
              "HTTP": http, "BYTES_TEXTO": len(corpo), "SHA256": sha,
              "ROTA_DE_SAIDA": rota, "ROTA_PROVA": rota_prova,
              "OUTROS_CANDIDATOS": [t for _, t in cands[1:5]],
              "AVISO": "este ficheiro e' PROVA DE QUE A FONTE ENTREGA, nao "
                       "corpus. Nenhuma coleta foi executada."}
        (pasta / "exemplo.json").write_text(
            json.dumps(ex, ensure_ascii=False, indent=1), encoding="utf-8")

        linhas.append({**d, "EVIDENCE_PATH":
                       str((pasta).relative_to(RAIZ)).replace("\\", "/"),
                       "EXAMPLE_TITLE": titulo, "EXAMPLE_TYPE": tipo,
                       "EVIDENCE_GRADE": grau,
                       "EVIDENCE_GRADE_PORQUE": porque_grau,
                       "OBSERVED_AT": agora, "EXAMPLE_URL": final,
                       "SHA256": sha[:16], "ROTA_DE_SAIDA": rota,
                       "EVIDENCIA_ESTADO": est, "EVIDENCIA_PORQUE": porque})

    (TRAB / "EVIDENCIA.json").write_text(
        json.dumps({"ROTA_DE_SAIDA": rota, "ROTA_PROVA": rota_prova,
                    "LINHAS": linhas}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    from collections import Counter
    print("PRESERVACAO DE EVIDENCIA")
    print("=" * 100)
    for l in sorted(linhas, key=lambda x: x["EVIDENCIA_ESTADO"]):
        print(f"  {l['EVIDENCIA_ESTADO']:24s} {l['EXAMPLE_TYPE']:18s} "
              f"{l['INPUT_SOURCE'][:34]:34s} {l['EXAMPLE_TITLE'][:44]}")
    print("=" * 100)
    print("  ", dict(Counter(l["EVIDENCIA_ESTADO"] for l in linhas)))
    print("  tipos:", dict(Counter(l["EXAMPLE_TYPE"] for l in linhas if
                                   l["EXAMPLE_TYPE"])))
    print("  GRAU :", dict(Counter(l["EVIDENCE_GRADE"] for l in linhas)))
    print()
    print("  So' o grau FORTE fecha o gate de REGISTRADA:")
    for l in linhas:
        if l["EVIDENCE_GRADE"] == "FORTE":
            print(f"    · {l['INPUT_SOURCE'][:38]:38s} «{l['EXAMPLE_TITLE'][:52]}»")
    print(f"\n  pastas de evidencia: {EVID.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
