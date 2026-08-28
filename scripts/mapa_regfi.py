#!/usr/bin/env python3
"""
Cliente do Registro Oficial de Productos Fitosanitarios (ES) — rotas públicas.

A MISSÃO 06 registrou `servicio.mapa.gob.es/regfiweb` como "responde 200 mas a
grade é JavaScript e as rotas de detalhe dão 404", e por isso titular e fabricante
do ES-01717 ficaram em fonte SECUNDÁRIA. Isso estava errado: a rota existia e a
página a declara em texto aberto.

COMO AS ROTAS FORAM DESCOBERTAS — sem nada além do que o navegador de qualquer
visitante faz:
  · a própria página `/regfiweb/` traz `<input type="hidden">` com os caminhos de
    cada área (`pathProductos`, `pathTitulares`, …);
  · a página `/regfiweb/Productos/Index` traz os caminhos AJAX
    (`getProductoByIdAjax`, `getProductoByFiltroAjax`, `exportGenericoJson`, …);
  · `/regfiweb/js/site.min.js` mostra os nomes de parâmetro que o frontend envia.
Nenhuma autenticação foi contornada e nenhuma vulnerabilidade foi usada.

CONTRATO
  GET  Productos/ProductosGrid?NumRegistro=&Titular=&Fabricante=&IdEstado=
       → HTML da grade; o rodapé traz "de un total de N" (N = total do filtro,
         a página mostra 5); cada linha traz `data-id` = idProducto.
  GET  Productos/GetProductoById?idProducto=N
       → JSON da ficha: titular, fabricante, fabrica, formulado, estado, tramite,
         estadoTramite e as datas.
  GET  Productos/ExportFichaProductoPdfGet?idProducto=N
       → ficha oficial em PDF (a mesma que o site oferece ao usuário).
  POST Exportaciones/ExportJsonProductos   (form: dataDto[<filtro>]=<valor>)
       → {"Contenido": "<json em string>", "Fecha": "<timestamp do servidor>"}
         com TODO o conjunto filtrado numa requisição — é a rota educada: um
         pedido em vez de centenas de páginas de grade.

USO
    python3 scripts/mapa_regfi.py producto ES-01717
    python3 scripts/mapa_regfi.py export  > ropf.json      # registro inteiro
    python3 scripts/mapa_regfi.py total   Titular=ADAMA
"""
import json
import re
import sys
import urllib.parse
import urllib.request

BASE = 'https://servicio.mapa.gob.es/regfiweb'
UA = 'Mozilla/5.0 (X11; Linux x86_64) SintoniaEAME/1.0 (pesquisa; contato via repositorio)'
HEAD = {'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Referer': BASE + '/'}
TOTAL = re.compile(r'de un total de (\d+)')
ROW = re.compile(r'btnBuscarProductoId"\s+data-nombre="([^"]*)"\s+data-id="(\d+)"')


def _get(path, params=None):
    url = f'{BASE}/{path}'
    if params:
        url += '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD), timeout=90) as r:
        return r.read()


def grid(**filters):
    """Devolve (total_do_filtro, [(nome, idProducto)] da primeira página)."""
    html = _get('Productos/ProductosGrid', filters).decode('utf-8', 'replace')
    m = TOTAL.search(html)
    return (int(m.group(1)) if m else 0), ROW.findall(html)


def producto(num_registro):
    """Ficha JSON de um registro, resolvendo o idProducto pela grade."""
    total, rows = grid(NumRegistro=num_registro)
    if not rows:
        return None
    return json.loads(_get('Productos/GetProductoById',
                           {'idProducto': rows[0][1]}).decode('utf-8'))


def ficha_pdf(id_producto, dest):
    with open(dest, 'wb') as f:
        f.write(_get('Productos/ExportFichaProductoPdfGet', {'idProducto': id_producto}))
    return dest


def export(**filters):
    """Conjunto filtrado inteiro numa requisição. Devolve (lista, timestamp do servidor)."""
    body = urllib.parse.urlencode({f'dataDto[{k}]': v for k, v in (filters or {'numRegistro': ''}).items()})
    req = urllib.request.Request(f'{BASE}/Exportaciones/ExportJsonProductos',
                                 data=body.encode(), headers=HEAD)
    with urllib.request.urlopen(req, timeout=300) as r:
        outer = json.loads(r.read().decode('utf-8'))
    if isinstance(outer, str):
        outer = json.loads(outer)
    return json.loads(outer['Contenido']), outer.get('Fecha')


# ---------------------------------------------------------------------------
# A REGRA DO FILTRO `IdEstado` — descoberta e verificada na MISSÃO 08
#
# A grade e o export discordavam: 1.998/1.086 contra 1.993/1.091, com o mesmo total
# de 3.084. A MISSÃO 07 registrou isso como divergência não resolvida. Ela tem regra:
#
#     IdEstado=1 ("VIGENTE")  seleciona  Estado == 'Vigente'
#                             OU        (Estado == 'Cancelado' E fechaLimiteVenta >= hoje)
#
# Ou seja: o FILTRO responde "ainda pode ser vendido?" e o CAMPO `Estado` responde
# "a autorização está em vigor?". São perguntas diferentes, e a diferença são os
# produtos cancelados dentro do prazo legal de escoamento.
#
# Verificado por igualdade de conjunto, não por contagem: os 5 registros que o
# export idEstado=1 devolve com Estado='Cancelado' são EXATAMENTE os 5 cancelados
# com fechaLimiteVenta futura. Nem um a mais, nem um a menos.
#
# Consequência operacional: 1.998 é um número com data de validade. Quando o prazo
# de escoamento do último desses produtos vencer, ele cai sozinho.
# ---------------------------------------------------------------------------

def selling_off(rows, today):
    """Registros que o filtro VIGENTE inclui e o campo Estado chama de Cancelado."""
    import datetime
    out = []
    for r in rows:
        if r.get('Estado') != 'Cancelado':
            continue
        raw = r.get('StrFechaLimiteVenta') or ''
        try:
            lim = datetime.datetime.strptime(raw, '%d-%m-%Y').date()
        except ValueError:
            continue
        if lim >= today:
            out.append(r)
    return out


def explain_divergence(rows, today):
    """Devolve a conta fechada dos dois recortes, para que nenhum seja publicado sozinho."""
    vig = [r for r in rows if r.get('Estado') == 'Vigente']
    canc = [r for r in rows if r.get('Estado') == 'Cancelado']
    esc = selling_off(rows, today)
    return {
        'TOTAL': len(rows),
        'BY_FIELD_Estado': {'Vigente': len(vig), 'Cancelado': len(canc)},
        'BY_FILTER_IdEstado': {'1_VIGENTE': len(vig) + len(esc),
                               '2_CANCELADO': len(canc) - len(esc)},
        'SELLING_OFF_PERIOD': sorted(r['NumRegistro'] for r in esc),
        'RULE': "IdEstado=1 == Estado=='Vigente' OR (Estado=='Cancelado' AND "
                "fechaLimiteVenta >= hoje)",
        'MEANING': {'FILTER_ANSWERS': 'ainda pode ser vendido?',
                    'FIELD_ANSWERS': 'a autorizacao esta em vigor?'},
        'WARNING': 'os dois numeros sao corretos e respondem a perguntas diferentes. '
                   'Publicar um deles sem dizer qual pergunta ele responde e erro.',
    }


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'producto'
    if cmd == 'producto':
        print(json.dumps(producto(sys.argv[2]), ensure_ascii=False, indent=1))
    elif cmd == 'export':
        rows, when = export(**dict(a.split('=', 1) for a in sys.argv[2:]))
        print(json.dumps({'Fecha': when, 'n': len(rows), 'rows': rows}, ensure_ascii=False))
    elif cmd == 'total':
        print(grid(**dict(a.split('=', 1) for a in sys.argv[2:]))[0])
    elif cmd == 'divergencia':
        import datetime
        rows, when = export()
        print(json.dumps(explain_divergence(rows, datetime.date.today()),
                         ensure_ascii=False, indent=1))
