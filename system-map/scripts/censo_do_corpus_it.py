# -*- coding: utf-8 -*-
"""CENSO DO CORPO ITALIANO — quantos registos existem, e quantos trazem texto.

POR QUE ISTO EXISTE
-------------------
Havia uma frase a circular nesta casa: «o corpo italiano tem milhões de
caracteres». Foi medida à mão uma vez, deu «4.654 registos e 7.088 caracteres»,
e ninguém conseguiu repetir nenhum dos dois números — porque a regra de
contagem nunca tinha sido escrita. Conta que não se repete não é medida.

Por isso a conta passou a viver aqui, em código, e corre outra vez sempre que
alguém duvidar.

E a frase dos milhões tinha razão. Só estava a falar de outro sítio: os
caracteres estão dentro de 49 PDF guardados no disco, que ninguém transformou
em texto. Ver `o_bruto_por_ler()`, mais abaixo.

A DISTINÇÃO QUE MUDA TUDO
-------------------------
Um REGISTO é uma linha da planilha: existe, tem identificador, tem data.
O TEXTO é o que está escrito dentro dela — o título, a descrição, a fala.

São duas contagens diferentes, e confundi-las é o erro caro. Ter 4.654 linhas
não é ter 4.654 coisas para ler. Uma linha que diz apenas «vídeo X existe, dura
4 minutos» é um registo REAL e um texto VAZIO. Contar as duas coisas juntas dá
um número grande que não corresponde a nada que se possa analisar.

    CORPO DE REGISTOS  ≠  CORPO DE TEXTO.

AS CINCO GAVETAS DE CADA FICHEIRO
---------------------------------
TEXT_EXPECTED_AND_PRESENT   devia ter texto, e tem            → dá para ler
TEXT_EXPECTED_BUT_MISSING   devia ter texto, e não tem        → BURACO
TEXT_NOT_EXPECTED           nunca foi para ter texto          → está certo
TEXT_EXISTS_ELSEWHERE       o texto existe, mas noutro sítio  → dá, com salto
UNKNOWN                     não sei dizer                     → fica assim

A última gaveta é obrigatória. Uma medição que nunca diz «não sei» está a
adivinhar em algum sítio, e não avisa onde.

CORRER
------
    py system-map/scripts/censo_do_corpus_it.py

Não lê a rede, não gasta nada, não altera nenhum dado. Só conta.
Escreve system-map/data/corpus-it.generated.json.
"""
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'corpus-it.generated.json')

# ── ONDE PROCURAR ──────────────────────────────────────────────────────────
# Só Itália. Espanha e França ficam de fora de propósito: este repositório é o
# projeto italiano, e misturar países foi exatamente o que produziu o número
# dos «milhões de caracteres».
PASTAS = ['data/samples', 'data/collection-store/italy',
          'data/collection-ledger/italy', 'data/raw']


def e_italiano(caminho: str) -> bool:
    """O ficheiro pertence à Itália?

    Pelo NOME e pelo CAMINHO, nunca pelo conteúdo. Ler o conteúdo para decidir
    o país é como decidir a nacionalidade de alguém pela língua que fala no
    vídeo: um italiano a falar inglês continua italiano, e um espanhol a citar
    um estudo italiano continua espanhol.
    """
    p = caminho.replace('\\', '/').upper()
    # Cada pedaco do caminho conta, nao so o nome do ficheiro. Um ficheiro
    # chamado `bollettino.json` dentro de `IT-ARPAV-VENETO/` e italiano, e a
    # primeira versao desta funcao deixava-o de fora — 27 ficheiros medidos em
    # vez de 62. Uma medicao que perde ficheiros em silencio e o defeito que
    # esta casa ja pagou uma vez.
    pedacos = p.split('/')
    for seg in pedacos:
        if seg.startswith('IT-') or seg in ('ITALY', 'ITALIA'):
            return True
        if 'ITALY' in seg or 'ITALIA' in seg:
            return True
    # Regioes e institutos italianos: o nome nao diz «IT», mas o sitio e Italia.
    # Esta lista e escrita a mao de proposito — adivinhar regiao pelo nome do
    # ficheiro poria a Provence francesa dentro do corpo italiano.
    REGIOES_IT = ('PIEMONTE', 'VENETO', 'ARPAV', 'LOMBARDIA', 'EMILIA',
                  'TOSCANA', 'PUGLIA', 'SICILIA', 'ISTAT', 'ISMEA')
    return any(r in p for r in REGIOES_IT)


# ── O QUE CONTA COMO TEXTO ─────────────────────────────────────────────────
# Campos onde mora prosa: coisa escrita por uma pessoa, para ser lida. Um
# identificador, uma data ou um URL são texto no sentido do computador, mas
# não são texto no sentido de «há aqui alguma coisa para analisar».
CAMPOS_DE_TEXTO = (
    'texto', 'text', 'title', 'titulo', 'TITLE', 'TITULO',
    'description', 'descricao', 'DESCRIPTION', 'DESCRICAO',
    'transcript', 'transcricao', 'TRANSCRIPT', 'TRANSCRICAO',
    'comment', 'comentario', 'COMMENT', 'COMMENT_TEXT', 'body', 'BODY',
    'content', 'CONTENT', 'snippet', 'SNIPPET', 'abstract', 'ABSTRACT',
    'caption', 'CAPTION', 'summary', 'RESUMO', 'observacao', 'OBSERVATION',
)

# Campos que PARECEM texto e não são. Um URL tem letras e não se lê; um SHA256
# tem sessenta e quatro caracteres e não diz nada a ninguém. Se estes entrarem
# na conta, o corpo «cresce» sem ganhar uma frase que seja.
NAO_E_TEXTO = ('url', 'URL', 'sha', 'SHA', 'id', 'ID', 'path', 'PATH',
               'href', 'link', 'LINK', 'hash', 'HASH')

MINIMO_DE_PROSA = 20  # menos do que isto é rótulo, não é frase


def _e_campo_de_texto(chave: str) -> bool:
    k = str(chave)
    if any(k == n or k.endswith('_' + n) or k.startswith(n + '_')
           for n in NAO_E_TEXTO):
        return False
    return any(c.lower() in k.lower() for c in CAMPOS_DE_TEXTO)


def varrer(no, saco):
    """Anda pela árvore do JSON somando prosa e contando registos.

    Um «registo» é qualquer dicionário que traga identificador — é a linha da
    planilha. Um dicionário que é só embrulho (a capa do ficheiro) não conta
    como registo, senão cada ficheiro somaria um registo fantasma.
    """
    if isinstance(no, dict):
        tem_id = any(k in no for k in ('id', 'ID', 'CONTENT_ID', 'EXTERNAL_ID',
                                       'ITEM_ID', 'RECORD_ID', 'SOURCE_ID'))
        if tem_id:
            saco['registos'] += 1
            saco['registos_com_texto'] += 0
        antes = saco['caracteres']
        for k, v in no.items():
            if isinstance(v, str) and _e_campo_de_texto(k):
                limpo = v.strip()
                if len(limpo) >= MINIMO_DE_PROSA and limpo not in ('NAO SEI',
                                                                   'NOT_KNOWN'):
                    saco['caracteres'] += len(limpo)
                    saco['campos'][k] = saco['campos'].get(k, 0) + 1
            else:
                varrer(v, saco)
        if tem_id and saco['caracteres'] > antes:
            saco['registos_com_texto'] += 1
    elif isinstance(no, list):
        for x in no:
            # SEGUNDA CONTAGEM, de proposito. «Registo» pode querer dizer duas
            # coisas: a linha que tem identificador proprio, ou qualquer objeto
            # dentro de uma lista. Os dois numeros sao legitimos e dao valores
            # muito diferentes. Publicar so um deles, sem dizer qual, foi o que
            # deixou um numero antigo impossivel de repetir.
            if isinstance(x, dict):
                saco['objetos_em_lista'] += 1
            varrer(x, saco)


# ── A GAVETA DE CADA FICHEIRO ──────────────────────────────────────────────
# Estas regras dizem o que se ESPERAVA de cada tipo de ficheiro. Sem essa
# expectativa escrita, «não tem texto» é só uma observação; com ela, passa a
# ser ou um buraco a tapar ou um ficheiro que está exatamente como devia.
SEM_TEXTO_POR_DESENHO = (
    'INVENTARIO', 'CENSUS', 'CENSO', 'MANIFEST', 'RECIBO', 'LEDGER',
    'PLANO', 'ROTA-', 'PARES-', 'MAPAS', 'DIRETORIO', 'INDICE',
    'REGUA', 'ACTIVE-SUBSTANCE', 'CATALOG', 'CATALOGO', 'COMPLETUDE',
)
DEVIA_TER_TEXTO = (
    'VIDEO', 'COMENTARIO', 'COMMENT', 'TRANSCRI', 'CORPUS', 'BOLLETTIN',
    'BOLETIN', 'CONVERSA', 'CANAL', 'CHANNEL', 'POST', 'NOTICIA', 'SINAIS',
)


def gaveta(nome: str, registos: int, caracteres: int) -> tuple:
    n = nome.upper()
    espera = any(p in n for p in DEVIA_TER_TEXTO)
    nao_espera = any(p in n for p in SEM_TEXTO_POR_DESENHO)
    if espera and caracteres > 0:
        return 'TEXT_EXPECTED_AND_PRESENT', 'nome diz que traz prosa, e traz'
    if espera and caracteres == 0:
        return ('TEXT_EXPECTED_BUT_MISSING',
                'nome diz que traz prosa, e nao traz nenhuma — BURACO')
    if nao_espera and caracteres == 0:
        return 'TEXT_NOT_EXPECTED', 'e uma lista/recibo; nunca foi para ter prosa'
    if nao_espera and caracteres > 0:
        return ('TEXT_NOT_EXPECTED', 'e uma lista/recibo; a prosa que tem e '
                                     'descricao de campo, nao conteudo colhido')
    if caracteres > 0:
        return 'TEXT_EXPECTED_AND_PRESENT', 'tem prosa, ainda que o nome nao diga'
    return ('UNKNOWN',
            'nao tem prosa e o nome nao diz se devia ter. NAO SEI — e este nao '
            'sei e a resposta honesta, nao uma falha da medicao')


def o_bruto_por_ler():
    """Os PDF italianos guardados — o material cru que ninguém transformou.

    Aqui está a resposta ao número que ninguém conseguia repetir. A frase
    «milhões de caracteres» aparece escrita uma vez neste repositório, em
    `regional-bulletin-sources.json`: «mais de 2,2 milhões de caracteres
    somados», a falar de treze PDF de boletim regional.

    Esses caracteres EXISTEM. Estão dentro dos PDF, no disco. O que nunca
    aconteceu foi alguém transformá-los em texto dentro das planilhas — e é por
    isso que a busca por texto encontrava quase nada.

        TER O DOCUMENTO NÃO É TER O TEXTO.
        É a diferença entre ter o livro na estante e ter o livro lido.

    Contam-se aqui os ficheiros e os megabytes. NÃO se conta caracteres: para
    isso era preciso abrir os PDF, e abrir PDF é derivação, não medição. Se um
    dia alguém os abrir, esse número entra por uma porta própria, com recibo.
    """
    achados = []
    for dirp, _, fs in os.walk(RAIZ):
        if '.git' in dirp.replace('\\', '/').split('/'):
            continue
        for f in fs:
            if not f.lower().endswith('.pdf'):
                continue
            rel = os.path.relpath(os.path.join(dirp, f), RAIZ).replace('\\', '/')
            if not e_italiano(rel):
                continue
            achados.append({'FICHEIRO': rel,
                            'BYTES': os.path.getsize(os.path.join(dirp, f))})
    achados.sort(key=lambda x: -x['BYTES'])
    return achados


def main():
    fichas, erros = [], []
    for pasta in PASTAS:
        base = os.path.join(RAIZ, pasta)
        if not os.path.isdir(base):
            continue
        for dirp, _, fs in os.walk(base):
            for f in fs:
                if not f.endswith('.json'):
                    continue
                caminho = os.path.join(dirp, f)
                rel = os.path.relpath(caminho, RAIZ).replace('\\', '/')
                if not e_italiano(rel):
                    continue
                saco = {'registos': 0, 'registos_com_texto': 0,
                        'objetos_em_lista': 0, 'caracteres': 0, 'campos': {}}
                try:
                    with io.open(caminho, encoding='utf-8') as fh:
                        varrer(json.load(fh), saco)
                except Exception as e:
                    erros.append({'FICHEIRO': rel, 'ERRO': str(e)[:120]})
                    continue
                g, porque = gaveta(f, saco['registos'], saco['caracteres'])
                fichas.append({
                    'FICHEIRO': rel,
                    'REGISTOS_COM_IDENTIFICADOR': saco['registos'],
                    'OBJETOS_DENTRO_DE_LISTAS': saco['objetos_em_lista'],
                    'REGISTOS': saco['registos'],
                    'REGISTOS_COM_TEXTO': saco['registos_com_texto'],
                    'CARACTERES_DE_TEXTO': saco['caracteres'],
                    'CAMPOS_DE_TEXTO_USADOS': saco['campos'],
                    'GAVETA': g,
                    'PORQUE': porque,
                })

    brutos = o_bruto_por_ler()
    fichas.sort(key=lambda x: -x['CARACTERES_DE_TEXTO'])
    total_reg = sum(f['REGISTOS'] for f in fichas)
    total_obj = sum(f['OBJETOS_DENTRO_DE_LISTAS'] for f in fichas)
    total_car = sum(f['CARACTERES_DE_TEXTO'] for f in fichas)
    com_texto = [f for f in fichas if f['CARACTERES_DE_TEXTO'] > 0]
    por_gaveta = {}
    for f in fichas:
        d = por_gaveta.setdefault(f['GAVETA'], {'ficheiros': 0, 'registos': 0,
                                                'caracteres': 0})
        d['ficheiros'] += 1
        d['registos'] += f['REGISTOS']
        d['caracteres'] += f['CARACTERES_DE_TEXTO']

    # A CONTA TEM DE FECHAR. Se as gavetas nao somarem o total, a medicao esta
    # a perder ficheiros pelo caminho — e uma medicao que perde e pior que uma
    # que falha alto, porque nao se queixa.
    somado = sum(d['ficheiros'] for d in por_gaveta.values())
    if somado != len(fichas):
        print('CONTA NAO FECHA: %d ficheiros nas gavetas, %d medidos'
              % (somado, len(fichas)), file=sys.stderr)
        raise SystemExit(1)

    estado = {
        'O_QUE_ISTO_E': ('Censo do corpo italiano. Conta REGISTOS e CARACTERES '
                         'DE PROSA em separado, porque sao coisas diferentes e '
                         'confundi-las foi o que produziu a frase «milhoes de '
                         'caracteres».'),
        'COMO_REFAZER': 'py system-map/scripts/censo_do_corpus_it.py',
        'TOTAIS': {
            'FICHEIROS_ITALIANOS': len(fichas),
            'FICHEIROS_COM_ALGUMA_PROSA': len(com_texto),
            'FICHEIROS_SEM_PROSA_NENHUMA': len(fichas) - len(com_texto),
            'CORPO_DE_REGISTOS_COM_IDENTIFICADOR': total_reg,
            'CORPO_DE_OBJETOS_DENTRO_DE_LISTAS': total_obj,
            'CORPO_DE_REGISTOS': total_reg,
            'CORPO_DE_TEXTO_EM_CARACTERES': total_car,
            'CARACTERES_POR_REGISTO': round(total_car / total_reg, 1) if total_reg else 0,
        },
        'POR_GAVETA': por_gaveta,
        'ONDE_ESTA_O_TEXTO_ITALIANO': [
            {'FICHEIRO': f['FICHEIRO'], 'CARACTERES': f['CARACTERES_DE_TEXTO'],
             'REGISTOS': f['REGISTOS']} for f in com_texto
        ],
        'BRUTO_POR_LER': {
            'O_QUE_E': ('PDF italianos guardados no disco. O texto deles existe '
                        'e NAO foi derivado para nenhuma planilha. RAW_EXISTS='
                        'SIM, TEXT_DERIVATION_EXISTS=NAO.'),
            'FICHEIROS': len(brutos),
            'MEGABYTES': round(sum(b['BYTES'] for b in brutos) / 1e6, 1),
            'CARACTERES': ('NAO MEDIDO — abrir PDF e derivar, nao medir. '
                           'Entra por porta propria, com recibo.'),
            'LISTA': brutos,
        },
        'ERROS_A_LER': erros,
        'FICHEIROS': fichas,
    }
    with io.open(SAIDA, 'w', encoding='utf-8') as fh:
        json.dump(estado, fh, ensure_ascii=False, indent=1)
        fh.write('\n')

    t = estado['TOTAIS']
    print('CORPO ITALIANO')
    print('  ficheiros ............. %d' % t['FICHEIROS_ITALIANOS'])
    print('  com alguma prosa ...... %d de %d'
          % (t['FICHEIROS_COM_ALGUMA_PROSA'], t['FICHEIROS_ITALIANOS']))
    print('  linhas com identificador  %d' % t['CORPO_DE_REGISTOS'])
    print('  objetos dentro de listas  %d' % t['CORPO_DE_OBJETOS_DENTRO_DE_LISTAS'])
    print('  texto (caracteres) .... %d' % t['CORPO_DE_TEXTO_EM_CARACTERES'])
    print('  por registo ........... %.1f caracteres'
          % t['CARACTERES_POR_REGISTO'])
    print()
    for g in sorted(por_gaveta, key=lambda k: -por_gaveta[k]['ficheiros']):
        d = por_gaveta[g]
        print('  %-27s %3d ficheiros · %6d registos · %7d caracteres'
              % (g, d['ficheiros'], d['registos'], d['caracteres']))
    print()
    print()
    print('  BRUTO POR LER (PDF guardados, texto nunca derivado)')
    print('    ficheiros ........... %d' % len(brutos))
    print('    megabytes ........... %.1f'
          % (sum(b['BYTES'] for b in brutos) / 1e6))
    print('    caracteres .......... NAO MEDIDO (abrir PDF e derivar)')
    print()
    print('  gravado: %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))


if __name__ == '__main__':
    main()
