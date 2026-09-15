#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ATLAS CONHECE ESTA FONTE? — uma pergunta, e só esta.

    py leis/fonte_do_atlas.py             # a população, dita em voz alta
    py leis/fonte_do_atlas.py IT-T3-013   # conhece? sim/não

Não responde se a fonte serve para o assunto (isso é
`leis/relevancia_da_fonte.py`), se ela responde hoje, quanto custa lá chegar,
nem se pode participar de uma corrida DESTE país. Responde uma coisa:

    ESTE `SOURCE_ID` FOI ALGUMA VEZ EMITIDO NO ATLAS?

POR QUE ISTO EXISTE, E FOI MEDIDO
----------------------------------
Medido no `1222d97d`, antes desta lei:

```
scrap_colheita.unidade(..., fonte='IT-T99-999')  ->  SOURCE_ID = 'IT-T99-999'
guarda/preservar_coleta._identifica('IT-T99-999') ->  True
ficheiros do fluxo que leem o atlas para validar  ->  NENHUM
```

O adapter **carimbava** a fonte que descia com o pedido e ninguém perguntava se
ela existia. `_identifica()` recusa as confissões — `None`, vazio, `NAO SEI` —
e **aceita tudo o resto**, o que está certo para o que ela mede: ela distingue
«veio um valor» de «veio uma desculpa». Não distingue — nem deve — um valor
verdadeiro de um inventado.

    UM `SOURCE_ID` QUE NINGUÉM EMITIU NÃO É UMA IDENTIDADE FRACA.
    É UMA IDENTIDADE QUE NÃO EXISTE.

E o custo aparece exactamente na corrida que se quer certificar: uma letra
trocada — `IT-T3-O13` com a letra O, `IT-T3-014` com o número errado — produz
uma corrida verde, com recibo, carimbada com uma fonte que o Atlas nunca
conheceu. A certificação diria «a identidade atravessou intacta», e ela teria
atravessado intacta: intacta e falsa.

A LEI QUE ISTO APLICA JÁ EXISTIA
---------------------------------
O Atlas é o dono do `SOURCE_ID` e diz, na sua convenção, que o ID *«uma vez
atribuído, não é reciclado»*. Um número que nunca foi atribuído está fora dessa
frase — e é por isso que se pergunta à população inteira, e não só às fichas.

⚠️ **A POPULAÇÃO NÃO É SÓ O ATLAS.** Medido em 15/09/2026: 170 IDs em fichas do
Atlas e **272** em uso na árvore. `candidatas/ITALY-SOURCE-MASTER-V1.json` cunhou
53 identidades italianas que estão presas a contratos e a pastas de evidência.
Perguntar só ao Atlas recusaria fontes verdadeiras — e recusar o verdadeiro é
tão defeito como aceitar o falso.

    A PERGUNTA É À POPULAÇÃO EM USO, NUNCA A UM DOS EMISSORES SOZINHO.

⚠️ E NÃO CAI PARA UMA CÓPIA
----------------------------
Se o Atlas não estiver ao alcance, isto **levanta**. Cair para uma lista de
reserva seria pôr uma segunda população a responder no dia em que a primeira
mudasse — calada, e convincente.

    FALHAR ALTO É MELHOR DO QUE RESPONDER PELA LISTA ERRADA.
"""
from __future__ import annotations

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)

#: A AUTORIDADE. A mesma que `leis/territorios.py` já nomeia. Não há segunda.
ATLAS = os.path.join("docs", "fontes", "ATLAS-DE-FONTES-EAME.md")

#: O outro emissor real, medido. Cunhou 53 identidades italianas que vivem
#: presas a contratos e a pastas de evidência.
MASTER_IT = os.path.join("candidatas", "ITALY-SOURCE-MASTER-V1.json")

#: `<PAÍS>-<TERRITÓRIO>-<sequencial>`, a convenção que o próprio Atlas declara.
FORMA = re.compile(r"^(EU|FR|ES|IT|PT|DE|PL)-T\d{1,2}-\d{3}$")
_ID = r"(?:EU|FR|ES|IT|PT|DE|PL)-T\d{1,2}-\d{3}"

#: Onde o registo de fontes começa. Acima disto o Atlas só ENSINA o formato —
#: `SOURCE_ID: # ex.: FR-T3-001` é um modelo, não uma identidade emitida. Contar
#: o preâmbulo já inventou uma fonte que não existe.
INICIO_DO_REGISTO = "## REGISTRO DE FONTES"

_cache = None


class AtlasIlegivel(Exception):
    """O Atlas não está ao alcance. NÃO se cai para uma cópia — ver o cabeçalho."""


def _texto(raiz=None) -> str:
    caminho = os.path.join(raiz or RAIZ, ATLAS)
    if not os.path.isfile(caminho):
        raise AtlasIlegivel(
            "a autoridade do SOURCE_ID nao esta ao alcance: %s. Sem ela nao ha "
            "resposta, e uma lista de reserva seria a segunda populacao." % ATLAS)
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return f.read()


def _do_atlas(texto: str) -> set:
    """As quatro formas com que o Atlas declara identidade.

    Ler só a ficha perde 27 numa faixa só (`ES-T7-001..027`) e perde as que o
    Atlas declara em tabela de estado. Um universo medido a menos recusa fonte
    verdadeira, que é o defeito que esta função existe para não ter.
    """
    i = texto.find(INICIO_DO_REGISTO)
    corpo = texto[i:] if i >= 0 else texto
    fora = set()
    for m in re.finditer(r"^SOURCE_ID:\s*(.+)$", corpo, re.M):
        decl = m.group(1).strip()
        faixa = re.match(r"(" + _ID + r")\.\.(\d{3})", decl)
        if faixa:                                   # forma FAIXA · 001..027
            pref, ini = faixa.group(1)[:-3], int(faixa.group(1)[-3:])
            fora |= {"%s%03d" % (pref, n) for n in range(ini, int(faixa.group(2)) + 1)}
            continue
        fora |= set(re.findall(_ID, decl))          # formas FICHA e MULTI
    for m in re.finditer(r"^\|\s*`?(" + _ID + r")`?\s*\|", corpo, re.M):
        fora.add(m.group(1))                        # forma TABELA DE ESTADO
    return fora


def _do_master(raiz=None) -> set:
    caminho = os.path.join(raiz or RAIZ, MASTER_IT)
    if not os.path.isfile(caminho):
        return set()
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return set(re.findall(_ID, f.read()))


def populacao(raiz=None, recarregar: bool = False) -> set:
    """Todo `SOURCE_ID` alguma vez emitido e ainda visível nesta árvore."""
    global _cache
    if _cache is not None and not recarregar and raiz is None:
        return _cache
    fora = _do_atlas(_texto(raiz)) | _do_master(raiz)
    if raiz is None:
        _cache = fora
    return fora


def conhece(source_id, raiz=None) -> bool:
    """O Atlas — ou o outro emissor — alguma vez emitiu este `SOURCE_ID`?

    ⚠️ `conhece` não é `autoriza`. Uma fonte espanhola conhecida devolve `True`
    aqui, e continua a não dever entrar numa corrida italiana — essa é outra
    pergunta, com outro dono, e ainda sem porta nesta árvore.

        CONHECER UMA FONTE E AUTORIZAR UMA FONTE SÃO PERGUNTAS DIFERENTES.
    """
    s = str(source_id or "").strip()
    if not s or not FORMA.match(s):
        return False
    return s in populacao(raiz)


def porque_nao(source_id, raiz=None) -> str:
    """A frase que o recusador escreve. Vazia quando a fonte é conhecida."""
    s = str(source_id or "").strip()
    if not s:
        return ""
    if not FORMA.match(s):
        return ("«%s» nao tem a forma de um SOURCE_ID do atlas "
                "(<PAIS>-T<n>-<NNN>, ex.: IT-T3-013)." % s[:40])
    if s in populacao(raiz):
        return ""
    return ("«%s» tem a forma certa e o atlas NUNCA o emitiu. Medido contra a "
            "populacao inteira (%s + %s): %d identidades. Uma letra trocada "
            "produz exactamente isto, e o recibo sairia identico ao de uma "
            "fonte verdadeira." % (s, ATLAS, MASTER_IT, len(populacao(raiz))))


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = list(argv if argv is not None else sys.argv[1:])
    pop = populacao()
    if not args:
        import collections
        c = collections.Counter(s.split("-")[0] for s in pop)
        print("POPULACAO = %d  ·  %s" % (len(pop), dict(sorted(c.items()))))
        return 0
    for s in args:
        ok = conhece(s)
        print("%-14s %s%s" % (s, "CONHECIDA" if ok else "DESCONHECIDA",
                              "" if ok else "  · " + porque_nao(s)[:96]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
