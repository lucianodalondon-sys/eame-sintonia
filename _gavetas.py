#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POE AS GAVETAS DO PROCESSO NO CAMINHO DE IMPORTACAO.

Os scripts do SINTONIA importam-se uns aos outros pelo nome curto — `import
proveniencia`, `import apify_pool`. Enquanto viviam todos numa pasta so, isso
resolvia sozinho: o Python poe a pasta do ficheiro que esta a correr no caminho
de procura, e os vizinhos estavam todos la.

Agora cada peca vive na gaveta do que ela E, e os vizinhos ficaram noutras
gavetas. Este ficheiro devolve o que a pasta unica dava de graca: importar isto
poe as onze gavetas no caminho, e os nomes curtos voltam a resolver.

    IMPORTA-SE EM DUAS LINHAS, E AS DUAS ESTAO A VISTA NO TOPO DO FICHEIRO.

Nao ha variavel de ambiente, nao ha ficheiro de configuracao escondido, nao ha
`sitecustomize`. Quem le o script ve o que ele faz sem sair dali.
"""
import os
import sys

_RAIZ = os.path.dirname(os.path.abspath(__file__))

GAVETAS = ("admissao", "candidatas", "coleta", "ferramentas", "fontes", "guarda", "leis", "motor", "pacote", "pedido", "portoes", "provas", "regras", "superficie")

# A gaveta, e as prateleiras dentro dela. Uma peca que so serve um pais mora em
# `<gaveta>/<pais>/` — a gaveta continua a dizer a ETAPA, e o pais entra depois.
# Sem esta segunda volta, `guarda/es/adama_es_import_rules` deixava de ser
# encontrado, e o teste dele acordava com «No module named».
for _g in GAVETAS:
    _p = os.path.join(_RAIZ, _g)
    if not os.path.isdir(_p):
        continue
    if _p not in sys.path:
        sys.path.insert(0, _p)
    for _sub in sorted(os.listdir(_p)):
        _q = os.path.join(_p, _sub)
        if os.path.isdir(_q) and not _sub.startswith(('_', '.')) and _q not in sys.path:
            sys.path.insert(0, _q)
