#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ROTA GRATUITA AINDA E GRATUITA? — e quem responde NAO SEI quando nao pode medir.

    python3 provas/a_rota_gratuita_ainda_e_gratuita.py

A PERGUNTA
----------
Tres coletores desta casa declaram, no cabecalho, que o OpenAlex e «rota REST
gratuita, sem chave». Em 2026-09-14 a prova de fogo da Collection pediu obras
dezassete vezes e recebeu, com HTTP 200:

    {"error":"Rate limit exceeded",
     "message":"Insufficient budget. This request costs $0.001
                but you only have $0 remaining."}

Nao e reputacao de IP, nao e bloqueio de rede, nao e a fonte em baixo. E
modelo de negocio novo da plataforma.

    UMA ROTA QUE ERA GRATUITA NAO E UMA ROTA QUE E GRATUITA.
    E UM CABECALHO NAO SE ACTUALIZA SOZINHO.

E A PERGUNTA QUE ESTA PROVA RECUSA RESPONDER SEM MEDIR
-------------------------------------------------------
⚠️ Nesta sessao a politica de egresso responde `403 CONNECT` a
`api.openalex.org` — e a todos os outros hospedeiros externos. Isso significa
que esta maquina NAO CONSEGUE saber se a rota esta aberta hoje.

Havia duas maneiras faceis de responder na mesma, e as duas seriam mentira:

    dizer GRATUITA   repetindo o cabecalho antigo, que ninguem re-mediu
    dizer PAGA       adoptando a medicao de OUTRA sessao como se fosse minha

    UMA MEDICAO DE OUTRA MAQUINA CITADA SEM DATA E SEM DONO
    DEIXA DE SER MEDICAO E PASSA A SER BOATO.

Entao a resposta e `NAO SEI`, com o motivo, com a ultima medicao conhecida
datada e atribuida, e com o comando exacto que a fecha.

E O QUE NAO SE FAZ COM UM NAO SEI
----------------------------------
⚠️ NAO SE TROCA O OPENALEX POR ORCID OU CROSSREF EM SILENCIO. Sao fontes
diferentes e respondem a perguntas diferentes; substituir uma pela outra para
o numero continuar a sair e trocar o dado sem ninguem decidir.

    SOURCE A != SOURCE B.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "capacidade-openalex.generated.json")

ABERTA, PAGA, NAO_SEI = "ABERTA", "PAGA_OU_SEM_ORCAMENTO", "NAO SEI"

#: A ultima medicao conhecida, com data e dono. NAO e o veredicto desta prova:
#: e o que alguem mediu noutro sitio, citado como tal.
ULTIMA_MEDICAO_CONHECIDA = {
    "QUANDO": "2026-09-14",
    "QUEM": "prova de fogo da Collection (claude/gifted-shannon-8u9l78)",
    "O_QUE_MEDIU": ("17 pedidos a api.openalex.org/works devolveram HTTP 200 "
                    "com corpo `Insufficient budget ... you only have $0 "
                    "remaining`"),
    "ESTADO": PAGA,
    "ONDE_NAO_SE_APLICA": ("esta e uma medicao DE OUTRA SESSAO. Ela nao prova "
                           "o estado de hoje, e nao e o veredicto deste "
                           "ficheiro."),
}

#: O que cada alternativa substitui, e o que NAO substitui. Escrito antes de
#: alguem precisar dela com pressa.
ALTERNATIVAS = {
    "ORCID": {
        "WHAT_CAPABILITY_IT_REPLACES": (
            "a IDENTIDADE declarada pela propria pessoa: pagina oficial, "
            "afiliacao, e a lista de obras que ela mesma registou."),
        "WHAT_CAPABILITY_IT_DOES_NOT_REPLACE": (
            "o INDICE. O OpenAlex indexa a obra publicada com data, tipo, "
            "veiculo e DOI, e devolve a autoria obra a obra — inclusive de quem "
            "nunca preencheu um perfil. O ORCID so sabe o que a pessoa "
            "declarou: quem nao registou, nao existe la. Trocar um pelo outro "
            "encolhe o corpus e o encolhimento nao aparece em lado nenhum."),
    },
    "CROSSREF": {
        "WHAT_CAPABILITY_IT_REPLACES": (
            "o registo bibliografico do DOI: titulo, veiculo, data de "
            "publicacao e a lista de autores como o editor a depositou."),
        "WHAT_CAPABILITY_IT_DOES_NOT_REPLACE": (
            "a DESAMBIGUACAO de autor e o topico. O Crossref nao tem id "
            "canonico de pessoa nem classificacao de assunto, e foi exactamente "
            "a desambiguacao que esta casa ja viu falhar uma vez (o "
            "`Nikolaos Papadopoulos` com 58 organizacoes). Sem ela, «as obras "
            "desta pessoa» volta a ser um palpite."),
    },
}

FALHAS, PASSOU = [], []


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def medir():
    """Pergunta ao OpenAlex. Devolve (estado, porque, corpo)."""
    r = subprocess.run(
        ["curl", "-sS", "-m", "25", "-w", "\\n%{http_code}",
         "https://api.openalex.org/works?per-page=1"],
        capture_output=True, text=True)
    if r.returncode != 0:
        return NAO_SEI, ("nao se chegou ao host: %s. Isto e o AMBIENTE desta "
                         "sessao, e nao uma resposta da plataforma."
                         % (r.stderr or "").strip()[:160]), ""
    saida = r.stdout.rsplit("\n", 1)
    corpo, codigo = (saida[0], saida[1]) if len(saida) == 2 else (r.stdout, "?")
    baixo = corpo.lower()
    if "insufficient budget" in baixo or "remaining" in baixo:
        return PAGA, ("a plataforma respondeu, e a resposta e de ORCAMENTO: "
                      "HTTP %s com `Insufficient budget`" % codigo), corpo[:400]
    if codigo == "200" and '"results"' in corpo:
        return ABERTA, "HTTP 200 com resultados, sem chave", corpo[:200]
    return NAO_SEI, ("HTTP %s com corpo que nao se reconhece" % codigo), corpo[:400]


print("A ROTA GRATUITA AINDA E GRATUITA?")
print()

estado, porque, corpo = medir()
print("  OPENALEX_CAPABILITY = %s" % estado)
print("    %s" % porque)
print()

T("a capacidade nao e declarada GRATUITA sem medicao desta sessao",
  estado != ABERTA or corpo,
  "declarou ABERTA sem corpo que o sustente")

# ⚠️ A TRAVA QUE IMPEDE O CABECALHO DE MENTIR: nenhum dono de rota pode
# continuar a chamar-lhe «gratuita» enquanto o estado nao for ABERTA medido.
rede = io.open(os.path.join(RAIZ, "superficie", "rede.py"),
               encoding="utf-8").read()
linha_do_host = [l for l in rede.splitlines()
                 if "api.openalex.org'," in l.replace('"', "'")]
contexto = "\n".join(rede.splitlines()[
    max(0, rede.splitlines().index(linha_do_host[0])) if linha_do_host else 0:][:4])
T("o portao de rede deixou de afirmar que a rota e gratuita",
  "rota gratuita, sem chave" not in contexto,
  "`superficie/rede.py` ainda declara a rota como gratuita a partir de um "
  "portao que so mede REDE")

T("as alternativas dizem o que NAO substituem",
  all(a.get("WHAT_CAPABILITY_IT_DOES_NOT_REPLACE") for a in ALTERNATIVAS.values()),
  "uma alternativa sem limites declarados vira substituicao silenciosa")

registo = {
    "O_QUE_ISTO_E": ("O estado REAL da rota OpenAlex, medido nesta sessao — "
                     "ou `NAO SEI` quando o ambiente nao deixa medir."),
    "COMO_REFAZER": "python3 provas/a_rota_gratuita_ainda_e_gratuita.py",
    "MEDIDO_EM": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                capture_output=True, text=True).stdout.strip(),
    "OPENALEX_CAPABILITY": estado,
    "PORQUE": porque,
    "CORPO_DA_RESPOSTA": corpo,
    "ULTIMA_MEDICAO_CONHECIDA": ULTIMA_MEDICAO_CONHECIDA,
    "A_LEI": "HOST_ALCANCAVEL != ROTA_GRATUITA != QUOTA_DISPONIVEL",
    "ALTERNATIVAS": ALTERNATIVAS,
    "O_QUE_NAO_SE_FEZ": (
        "nao se pagou, nao se pos Apify, e nao se trocou OpenAlex por ORCID ou "
        "Crossref. SOURCE A != SOURCE B, e a substituicao silenciosa e a "
        "maneira de trocar o dado sem ninguem decidir."),
    "COMO_FECHAR_ESTE_NAO_SEI": (
        "correr esta prova num ambiente com egresso para api.openalex.org. "
        "Enquanto o `403 CONNECT` da politica desta sessao existir, a resposta "
        "honesta e NAO SEI."),
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(registo, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("OPENALEX_CAPABILITY = %s · %d passaram · %d falharam"
      % (estado, len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
