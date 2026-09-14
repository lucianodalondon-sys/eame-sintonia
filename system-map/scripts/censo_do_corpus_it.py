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

E a busca por esse número antigo encontrou outra coisa — mais importante, e
que tem de ser escrita com as palavras certas:

    ANTIGO «MILHÕES DE CARACTERES»  =  NÃO REPRODUZIDO COMO TEXTO
    ACHADO NOVO, COMPROVADO         =  49 ocorrências de PDF italiano
                                    =  43 conteúdos diferentes
                                    =  62,7 MB de evidência bruta

E OCORRÊNCIA NÃO É CONTEÚDO. Quando isto foi escrito, dizia «43 deles sem
derivação de texto» — e ficou velho duas vezes. Primeiro porque a derivação
passou a existir; depois porque o censo só sabia procurar o texto pelo NOME do
ficheiro, e não via os 43 textos que já existiam com o pai declarado.

    49 - 43 = 6  NÃO É PERDA. São seis conteúdos que foram BUSCADOS DUAS
                 VEZES — duas idas reais à fonte que trouxeram os mesmos
                 bytes, cada uma com o seu recibo.

Isto aqui já disse «seis documentos guardados em dois sítios ao mesmo tempo»,
como se fosse fotocópia. Era palpite lido no nome da pasta. Quem foi medir a
prova de captura de cada caminho foi `censo_de_identidade_it.py`, e o veredito
é 6 de 6 `INDEPENDENT_CAPTURES_SAME_CONTENT`. **Caminho diferente não prova
captura diferente, e SHA igual não prova a mesma captura.**

Ver `ocorrencia_e_conteudo()` e `derivados_por_impressao_digital()`.

Um erro que quase se cometeu aqui: dizer «encontrei os milhões, estão nos
PDF». Não está provado. Megabyte não é caractere — um PDF de 6 MB tanto pode
ser cinquenta páginas escritas como uma única fotografia digitalizada. São
dois factos separados e escrevem-se separados.

Ver `o_bruto_por_ler()`, mais abaixo.

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
import hashlib
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


def _prosa_no_mesmo_registo(no, alvo: str):
    """Encontra a LINHA que fala deste PDF e vê se ela guarda prosa.

    A primeira versão desta função perguntava outra coisa: «esta planilha cita
    o PDF, e esta planilha tem prosa em algum sítio?». Isso dava 31 de 49, e
    era falso. Uma planilha com trinta boletins pode citar um PDF numa linha e
    ter prosa noutra linha completamente diferente — a prosa é de outro
    documento.

        MENCIONAR NÃO É USAR. Quinta vez que esta armadilha aparece na casa.

    A pergunta certa é mais apertada: existe uma LINHA que nomeia este PDF e
    que, dentro dela mesma, guarda o texto? Se sim, o PDF foi lido. Se não, o
    PDF está guardado e continua fechado.
    """
    achou = False
    if isinstance(no, dict):
        cita = any(isinstance(v, str) and alvo in v for v in no.values())
        if cita:
            saco = {'registos': 0, 'registos_com_texto': 0,
                    'objetos_em_lista': 0, 'caracteres': 0, 'campos': {}}
            varrer(no, saco)
            if saco['caracteres'] >= 200:
                return True  # 200 letras: uma linha de prosa, não um rótulo
        for v in no.values():
            achou = achou or _prosa_no_mesmo_registo(v, alvo)
            if achou:
                return True
    elif isinstance(no, list):
        for x in no:
            if _prosa_no_mesmo_registo(x, alvo):
                return True
    return achou


def derivados_por_impressao_digital():
    """Que CONTEÚDOS já têm texto derivado — ligados pela impressão digital.

    Esta é a ligação mais forte que existe neste repositório, e por isso é a
    primeira a ser perguntada: o registo de artefatos guarda `PARENT_SHA256`,
    que é exatamente o hash do PDF de onde o texto saiu.

        NOME DE FICHEIRO É INDÍCIO. IMPRESSÃO DIGITAL É PROVA.

    Enquanto esta função não existia, o censo só sabia procurar o texto pelo
    NOME (um irmão `.txt` ao lado, ou o nome citado numa planilha) — e por isso
    dizia «43 PDF sem texto derivado» ao mesmo tempo que existiam 43 textos
    derivados, cada um com o pai declarado. Os dois números estavam no mesmo
    mapa, a dizer o contrário um do outro.

    Devolve {sha256_do_pai: [caminhos do texto derivado]}.
    """
    reg = os.path.join(RAIZ, 'data', 'derivados', 'REGISTO-DE-ARTEFATOS.json')
    if not os.path.exists(reg):
        return {}
    try:
        with io.open(reg, encoding='utf-8') as fh:
            d = json.load(fh)
    except (ValueError, OSError):
        return {}
    fichas = d if isinstance(d, list) else next(
        (v for v in d.values() if isinstance(v, list)), [])
    por_pai = {}
    for f in fichas:
        pai = f.get('PARENT_SHA256')
        onde = f.get('STORAGE_LOCATION')
        if pai and onde:
            por_pai.setdefault(pai, []).append(onde)
    return por_pai


def _tem_texto_derivado(nome_pdf: str, indice_de_prosa: dict):
    """Existe, em algum sítio, o texto que saiu deste PDF?

    Devolve (sim_ou_nao, onde). Ver `_prosa_no_mesmo_registo` para a regra —
    ela é apertada de propósito.
    """
    base = os.path.basename(nome_pdf)
    onde = []
    for ficheiro, (bruto, arvore) in indice_de_prosa.items():
        if base not in bruto or arvore is None:
            continue
        if _prosa_no_mesmo_registo(arvore, base):
            onde.append(ficheiro)
    return bool(onde), onde


def o_bruto_por_ler(indice_de_prosa):
    """Os PDF italianos guardados, e quais deles viraram texto.

    ATENÇÃO À LINGUAGEM, porque aqui já se errou uma vez.

    A frase «milhões de caracteres» aparece escrita uma vez neste repositório,
    em `regional-bulletin-sources.json`: «mais de 2,2 milhões de caracteres
    somados», a falar de treze PDF de boletim regional.

    Encontrar 49 PDF e 62,7 MB **não prova** que existem milhões de caracteres.
    Megabyte não é caractere: um PDF de 6 MB pode ser cinquenta páginas de
    texto ou uma única fotografia digitalizada. São dois factos separados, e
    juntá-los foi exatamente o erro que se tentava consertar:

        ANTIGO «MILHÕES DE CARACTERES»  =  NÃO REPRODUZIDO COMO TEXTO
        ACHADO NOVO, COMPROVADO         =  49 PDF italianos
                                        =  62,7 MB de evidência bruta
                                        =  sem derivação de texto localizada

    O achado novo é mais importante que o número antigo. Mas é OUTRO facto, e
    escreve-se como outro facto.

        TER O DOCUMENTO NÃO É TER O TEXTO.
        É a diferença entre ter o livro na estante e ter o livro lido.

    Contam-se aqui ficheiros, megabytes, e quantos têm texto derivado. NÃO se
    contam caracteres: para isso era preciso abrir os PDF, e abrir PDF é
    derivação, não medição. Se um dia alguém os abrir, esse número entra por
    uma porta própria, com recibo.
    """
    por_impressao = derivados_por_impressao_digital()
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
            tem, onde = _tem_texto_derivado(rel, indice_de_prosa)
            # A PROVA VEM PRIMEIRO: se o registo de artefatos diz que este
            # conteudo tem filho, isso decide — o nome do ficheiro nao tem voto.
            sha = _sha256(os.path.join(dirp, f))
            if sha in por_impressao:
                tem = True
                onde = sorted(set(onde) | set(por_impressao[sha]))
            # Um ficheiro de texto ao lado do PDF também conta como derivação.
            derivado = 0
            irmao = os.path.splitext(os.path.join(dirp, f))[0]
            for ext in ('.txt', '.md', '.text'):
                if os.path.exists(irmao + ext):
                    tem = True
                    onde.append(os.path.relpath(irmao + ext, RAIZ)
                                .replace('\\', '/'))
                    try:
                        derivado += len(io.open(irmao + ext,
                                                encoding='utf-8').read())
                    except Exception:
                        pass
            achados.append({
                'FICHEIRO': rel,
                'BYTES': os.path.getsize(os.path.join(dirp, f)),
                'SHA256': sha,
                'TEM_TEXTO_DERIVADO': tem,
                'CARACTERES_JA_DERIVADOS': derivado,
                'ONDE_ESTA_O_TEXTO': onde,
            })
    achados.sort(key=lambda x: -x['BYTES'])
    return achados


def _sha256(caminho):
    """A impressao digital do ficheiro. E ela — nao o caminho — que diz o que
    a coisa E."""
    h = hashlib.sha256()
    with io.open(caminho, 'rb') as fh:
        for pedaco in iter(lambda: fh.read(1 << 20), b''):
            h.update(pedaco)
    return h.hexdigest()


def ocorrencia_e_conteudo(brutos):
    """OCORRENCIA nao e CONTEUDO — e a conta que os confunde inventa perda.

        49 caminhos  -  43 conteudos  =  6 PERDIDOS       <- ERRADO
        49 ocorrencias · 43 conteudos · 6 repeticoes      <- CERTO

    Uma OCORRENCIA e uma aparicao documentada, com procedencia propria: onde
    ela esta, de que corrida veio, por que caminho. Um CONTEUDO sao os bytes,
    e quem os identifica e o hash.

    Duas ocorrencias podem apontar para o MESMO conteudo sem que nada se tenha
    perdido. Neste acervo isso acontece sempre pelo mesmo motivo: o documento
    esta na loja do coletor E na amostra versionada. Mesma coisa no mundo, duas
    procedencias — e apagar uma perderia a prova de como ela chegou ali.

        MESMO CONTEUDO NAO E A MESMA COLETA.

    E a lei que isto exerce e a COL-LAW-501. Ela existe porque a subtracao
    ingenua ja estava a um passo de ser escrita num relatorio.
    """
    por_hash = {}
    for b in brutos:
        por_hash.setdefault(b['SHA256'], []).append(b['FICHEIRO'])
    repetidos = {h: cs for h, cs in por_hash.items() if len(cs) > 1}
    return {
        'O_QUE_E': ('OCORRENCIA e CONTEUDO sao especies diferentes. A '
                    'contagem NUNCA subtrai uma da outra: a diferenca entre '
                    'elas e repeticao, nao perda. COL-LAW-501.'),
        'OCORRENCIAS': len(brutos),
        'CONTEUDOS_UNICOS': len(por_hash),
        'OCORRENCIAS_DE_CONTEUDO_REPETIDO': len(brutos) - len(por_hash),
        'CONTEUDOS_COM_MAIS_DE_UM_CAMINHO': len(repetidos),
        'PERDA': 0,
        'PORQUE_NAO_E_PERDA': ('cada copia repetida continua no disco, com o seu '
                               'caminho e a sua procedencia. Nada sumiu. E a '
                               'repeticao nao e fotocopia: censo_de_identidade_it.py '
                               'classificou os 6 grupos pela prova de captura e deu '
                               '6/6 INDEPENDENT_CAPTURES_SAME_CONTENT — duas idas '
                               'reais a fonte que trouxeram os mesmos bytes.'),
        'ONDE_SE_REPETE': [
            {'SHA256': h, 'CAMINHOS': sorted(cs)}
            for h, cs in sorted(repetidos.items(), key=lambda x: -len(x[1]))
        ],
    }


def indice_de_quem_cita_pdf():
    """Para cada planilha do repositório: que nomes cita, e quanta prosa tem.

    É a lista telefónica que permite perguntar «este PDF virou texto em algum
    sítio?». Sem ela, a resposta só poderia ser um palpite.
    """
    indice = {}
    for pasta in ('data', 'build', 'docs'):
        base = os.path.join(RAIZ, pasta)
        if not os.path.isdir(base):
            continue
        for dirp, _, fs in os.walk(base):
            for f in fs:
                if not f.endswith(('.json', '.ndjson', '.md')):
                    continue
                caminho = os.path.join(dirp, f)
                rel = os.path.relpath(caminho, RAIZ).replace('\\', '/')
                try:
                    bruto = io.open(caminho, encoding='utf-8').read()
                except Exception:
                    continue
                if '.pdf' not in bruto.lower():
                    continue  # não cita PDF nenhum: não interessa aqui
                arvore = None
                if f.endswith('.json'):
                    try:
                        arvore = json.loads(bruto)
                    except Exception:
                        arvore = None
                indice[rel] = (bruto, arvore)
    return indice


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

    brutos = o_bruto_por_ler(indice_de_quem_cita_pdf())
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
        # O NOME ANTIGO ERA «BRUTO_POR_LER», E DEIXOU DE SER VERDADE.
        # Ele nasceu quando os PDF estavam mesmo por ler. Hoje todos tem
        # derivacao localizavel — e o bloco continuava a dizer
        # «TEXT_DERIVATION_EXISTS=NAO» ao lado de «PDF_SEM_TEXTO_DERIVADO: 0».
        #
        #     UM NOME QUE FICOU FALSO E PIOR QUE UM CAMPO EM FALTA.
        #     O campo em falta faz perguntar; o nome falso faz confiar.
        #
        # Nao se criou campo paralelo para preservar o nome antigo: o nome
        # mudou no dono, e os consumidores foram atras.
        'ACERVO_EM_PDF': {
            'O_QUE_E': (
                'O acervo italiano em PDF, e o estado da derivacao dele. '
                'OCORRENCIA e o caminho no disco; CONTEUDO sao os bytes, '
                'identificados por SHA-256. Uma MESMA derivacao serve todas as '
                'ocorrencias do mesmo conteudo — por isso ha mais ocorrencias '
                'do que derivados, e isso NAO e falta. '
                'RAW_EXISTS=SIM, TEXT_DERIVATION_EXISTS=SIM.'),
            'OCORRENCIAS': len(brutos),
            'CONTEUDOS_UNICOS': len({b['SHA256'] for b in brutos}),
            'MEGABYTES': round(sum(b['BYTES'] for b in brutos) / 1e6, 1),
            'OCORRENCIAS_COM_DERIVACAO': sum(1 for b in brutos
                                             if b['TEM_TEXTO_DERIVADO']),
            'OCORRENCIAS_SEM_DERIVACAO': sum(1 for b in brutos
                                             if not b['TEM_TEXTO_DERIVADO']),
            'DERIVADOS_UNICOS': len({b['SHA256'] for b in brutos
                                     if b['TEM_TEXTO_DERIVADO']}),
            'COMO_SE_LIGA': ('pelo PARENT_SHA256 do registo de artefatos. Nome '
                             'de ficheiro e indicio; impressao digital e prova.'),
            'CARACTERES': ('NAO MEDIDO e NAO CANONICO — abrir PDF e derivar, '
                           'nao medir. E nem sobre o texto ja derivado ha regra '
                           'de contagem escrita: a mesma pasta da contas '
                           'diferentes conforme a quebra de linha. Entra por '
                           'porta propria, com contrato.'),
            'LISTA': brutos,
        },
        # OCORRENCIA x CONTEUDO — a distincao que impede a conta errada.
        # Nasce dos MESMOS `brutos` acima: nada e recontado por outra via,
        # porque duas medicoes da mesma coisa divergem no primeiro dia.
        'OCORRENCIA_E_CONTEUDO': ocorrencia_e_conteudo(brutos),
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
    _com = sum(1 for b in brutos if b['TEM_TEXTO_DERIVADO'])
    print('    com texto derivado .. %d / %d' % (_com, len(brutos)))
    print('    SEM texto derivado .. %d / %d' % (len(brutos) - _com, len(brutos)))
    print('    letras ja derivadas . %d (nos .txt ao lado dos PDF)'
          % sum(b['CARACTERES_JA_DERIVADOS'] for b in brutos))
    print('    caracteres nos PDF .. NAO MEDIDO — abrir PDF e derivar.')
    print('                          62,7 MB NAO e prova de milhoes de letras:')
    print('                          um PDF de 6 MB pode ser 50 paginas de texto')
    print('                          ou uma unica fotografia digitalizada.')
    print()
    print('  gravado: %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))


if __name__ == '__main__':
    main()
