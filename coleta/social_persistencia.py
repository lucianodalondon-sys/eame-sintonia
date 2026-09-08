#!/usr/bin/env python3
"""O DONO DA PERSISTENCIA SOCIAL — conteudo, comentario, reobservacao.

E SO ISSO. Este modulo NAO e dono de:

    RAW           o dono forward do G-42 — Supabase Storage + `raw_asset`
    PROGRESSO     `coleta/coleta_checkpoint.py` — `checkpoint_coleta`
    IDENTIDADE    ninguem, ainda — e por isso ele RECUSA em vez de inventar

Este modulo NAO importa nem chama o dono do G-42, de proposito: ele recebe
`raw_durou` como PARAMETRO. Quem preserva os bytes e quem grava a estrutura sao
dois donos, e a costura entre eles e do chamador — nao de um deles por dentro.
O nome do modulo do G-42 nao aparece escrito aqui porque a prova que guarda
aquela peca conta caller real por varredura de texto, e um nome citado num
docstring apareceria como caller que nao existe. `CAN DO != DID DO` vale para os
dois lados: nem prometer estrada que nao existe, nem declarar uso que nao houve.

A recusa e a parte importante. Para gravar `conteudo` o banco exige `canal_id`;
`canal` exige `origem_id`; e `origem` tem uma constraint que exige PESSOA ou
ORGANIZACAO. Reproduzido no Postgres 16 descartavel:

    ERROR: new row for relation "origem" violates check constraint
           "origem_e_pessoa_ou_organizacao"

Ou seja: o banco JA se recusa a deixar um canal existir sem que alguem tenha
decidido de quem ele e. Portanto:

    CHANNEL_ID PROVA O CANAL.
    NAO PROVA SOZINHO PERSON_IDENTITY NEM ORGANIZATION_IDENTITY.

Um executor social que criasse `organizacao` porque o titulo do canal diz
«Syngenta Italy», ou `pessoa` porque o handle diz «riccardocastaldi», estaria
promovendo EVIDENCIA CANDIDATA a IDENTIDADE CANONICA sozinho, no meio de uma
coleta, sem ninguem olhando. Este modulo devolve `CHANNEL_IDENTITY_NOT_RESOLVED`
e para. Quem resolve identidade humana e outra missao, com outro dono.

O QUE ELE FAZ, NA ORDEM QUE IMPORTA
-----------------------------------
    RAW durou  ->  conteudo  ->  comentario  ->  (so entao o checkpoint anda)

`persistir_video()` RECUSA sem prova de RAW durado. Nao e zelo: o checkpoint
usa `conteudo` como memoria do que ja foi colhido, e conteudo sem RAW faria a
proxima execucao pular um video cujo bruto nunca foi guardado.

    SEEN NAO E PERSISTED.
    KNOWN VEM DE CONTEUDO PERSISTIDO — nunca de video visto na API,
    nunca de RAW sozinho, nunca de cache em RAM.
"""
import hashlib
import hmac
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401

import instagram_pessoal as ip   # noqa: E402 — dono do sal do pseudonimo

# ── AS RECUSAS ───────────────────────────────────────────────────────────
CANAL_NAO_RESOLVIDO = 'CHANNEL_IDENTITY_NOT_RESOLVED'
RAW_NAO_DUROU = 'RAW_NOT_PRESERVED'
PAI_NAO_PERSISTIDO = 'PARENT_NOT_PERSISTED'
TEXTO_DIVERGIU = 'COMMENT_TEXT_DIVERGED'
REOBSERVADO = 'REOBSERVED'
CONTEUDO_DIVERGIU = 'CONTENT_DRIFT'

# `canal.plataforma` e MINUSCULO no banco (check da 002) e MAIUSCULO no
# envelope. Medido, nao suposto — a primeira tentativa de gravar 'YOUTUBE'
# levou `canal_plataforma_check`. O mapa vive aqui para nao virar um `.lower()`
# solto em cinco chamadores.
PLATAFORMA_NO_BANCO = {'YOUTUBE': 'youtube', 'INSTAGRAM': 'instagram',
                       'LINKEDIN': 'linkedin', 'TIKTOK': 'tiktok',
                       'FACEBOOK': 'facebook', 'X': 'x', 'WEB': 'web',
                       'PODCAST': 'podcast', 'API': 'api'}


def _lit(v):
    """Literal SQL. `None` vira NULL de verdade, nunca a string 'None'."""
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def autor_hash(author_native_id, *, platform):
    """`(plataforma, id nativo do autor)` -> 64 hex. NUNCA nome, NUNCA @.

    A PLATAFORMA ENTRA, e isso nao e zelo: a casa inteira ja trata identidade
    nativa como PLATFORM-SCOPED — `social_envelope.dedupe()` funde por
    `(PLATFORM, NATIVE_ID)` e `public.canal` tem `UNIQUE (plataforma,
    channel_id)`. Esta funcao era o UNICO lugar que largava a plataforma pelo
    caminho.

        IDENTIDADE NATIVA E PLATFORM-SCOPED.

    Sem ela, um autor `12345` no YouTube e um autor `12345` noutra plataforma
    cairiam no MESMO `autor_hash` — e a contagem de «pessoas distintas» passaria
    a afirmar, calada, que sao a mesma pessoa. Nao sabemos disso. Juntar uma
    pessoa entre plataformas e IDENTITY RESOLUTION, tarefa futura e de outro
    dono; coleta nao infere isso de graca por causa de um numero igual.

    Medido em 2026-09-08 antes de mudar: UM consumidor
    (`persistir_comentarios`, aqui mesmo) e ZERO linhas em `public.comentario`
    — entao a mudanca nao invalida pseudonimo nenhum ja gravado.

    O algoritmo NAO e novo: e o mesmo HMAC-SHA256 com sal persistente fora do
    Git que `instagram_pessoal.pseudonimo()` ja usa, e o sal e literalmente o
    mesmo arquivo — dois sais seriam duas identidades para a mesma pessoa.

    So a largura muda: `pseudonimo()` corta em 12 hex porque o artefato dele e
    para leitura humana; `comentario.autor_hash` e `char(64)`, entao aqui vai o
    digest inteiro. Cortar para 12 e depois preencher seria jogar fora 52
    caracteres de espaco de colisao de graca.

    A ENTRADA e `AUTHOR_CHANNEL_ID`, e so ele. `AUTHOR_DISPLAY_NAME` esta
    proibido: nome visivel muda quando a pessoa quiser, e pseudonimo que muda
    transforma uma pessoa em N pessoas na contagem. Sem channel id, UNKNOWN —
    que e uma resposta, nao um preenchimento.
    """
    if not author_native_id or author_native_id == 'UNKNOWN':
        return None
    # `\x1f` separa os dois campos para que ('YOUTUBE','A1') e ('YOU','TUBEA1')
    # nunca produzam a mesma entrada — concatenar direto criaria colisao entre
    # pares diferentes.
    entrada = '%s\x1f%s' % (str(platform).upper().strip(),
                            str(author_native_id).strip())
    return hmac.new(ip._sal(), entrada.encode('utf-8'), hashlib.sha256).hexdigest()


# ── O CORPO QUE VIRA `hash_conteudo` ─────────────────────────────────────
# A 003 diz «sha256 do corpo, para dedupe real» e «titulo igual NAO colapsa»,
# mas NAO diz QUAL corpo, para video. Medido em 2026-09-08: nenhum modulo do
# repositorio define essa serializacao — `persistir_video()` recebia um
# `texto_canonico` ja pronto e cada chamador decidia sozinho o que era.
#
#     DOIS CHAMADORES COM SERIALIZACOES DIFERENTES
#     PRODUZEM DRIFT QUE NAO EXISTE.
#
# Entao ela ganha UM dono, aqui, e uma VERSAO. A versao e o que torna uma
# mudanca futura visivel: mudar os campos sem mexer nela faria todo o acervo
# parecer ter sofrido drift de uma vez.
CORPO_VERSAO = 'v1:titulo+descricao'


def corpo_canonico(*, titulo=None, descricao=None):
    """Os campos do video que compoem o corpo, em ordem fixa.

    Titulo e descricao, nada mais. Nao entram: contadores (vistas, likes) que
    mudam sozinhos a cada minuto e fariam todo reencontro parecer edicao; nem
    `run_id`, `coletado_em` ou qualquer marca da corrida, que fariam o mesmo
    video ter um corpo diferente por execucao.
    """
    return '\n'.join([CORPO_VERSAO, titulo or '', descricao or ''])


def hash_do_texto(texto):
    """`hash_conteudo` = hash do TEXTO. Sem ID dentro, nunca.

    Meter o ID nativo aqui fecharia a constraint velha sem migration — e faria
    dois «Grazie!» iguais terem hashes diferentes, quebrando a unica pergunta
    que esta coluna existe para responder: este texto mudou?
    """
    return hashlib.sha256((texto or '').encode('utf-8')).hexdigest()


# ═════════════════════════════════════════════════════════════════════════
# 1 · O CANAL — resolver NAO e o mesmo que criar
# ═════════════════════════════════════════════════════════════════════════
def canal_canonico(banco, *, platform, channel_id):
    """Devolve o `canal.id` que JA existe, ou None. Nunca cria.

    Nao ha `insert` nesta funcao de proposito. Criar um canal obriga a decidir
    de quem ele e — e essa decisao nao pertence a um executor de coleta.
    """
    p = PLATAFORMA_NO_BANCO.get(str(platform).upper())
    if not p:
        return None
    linhas = banco.executa(
        "select id from public.canal where plataforma = %s and channel_id = %s"
        % (_lit(p), _lit(channel_id)))
    return int(linhas[0][0]) if linhas else None


def exigir_canal(banco, *, platform, channel_id):
    """→ `(canal_id, None)` ou `(None, recusa)`. A recusa carrega o porque."""
    cid = canal_canonico(banco, platform=platform, channel_id=channel_id)
    if cid:
        return cid, None
    return None, {
        'STATE': CANAL_NAO_RESOLVIDO,
        'PLATFORM': platform, 'CHANNEL_ID': channel_id,
        'PORQUE': ('o canal nao existe no banco, e criar um exige decidir de quem '
                   'ele e — `origem` tem constraint que exige pessoa ou organizacao. '
                   'CHANNEL_ID PROVA O CANAL, NAO PROVA A ORIGEM.'),
        'QUEM_RESOLVE': 'um dono de identidade, fora do executor de coleta',
    }


# ═════════════════════════════════════════════════════════════════════════
# 2 · O CONTEUDO — um conteudo, N observacoes
# ═════════════════════════════════════════════════════════════════════════
def persistir_video(banco, *, canal_id, run_id, content_id, texto_canonico,
                    publicado_em=None, rule_version='v1', raw_durou=False,
                    originalidade='ORIGINAL', tipo='video'):
    """Grava o conteudo e a observacao desta corrida. Idempotente.

    ⚠️ `tipo` PASSOU A SER PARAMETRO, E O DEFAULT MANTEM O QUE JA ERA.
    Este writer e o dono de `public.conteudo`, mas escrevia `'video'` fixo no
    SQL — a coluna `tipo` existia desde a 003 com nove valores, e ele so sabia
    dizer um. Para um boletim tecnico em PDF a escolha era escrever `video`
    (mentira no banco) ou abrir um SEGUNDO writer para a mesma tabela.

        UM CONCEITO, UM DONO. O DONO APRENDE O TIPO — NAO NASCE OUTRO DONO.

    O default `'video'` mantem todos os chamadores existentes byte a byte.

    `raw_durou` NAO tem default `True` de proposito: quem nao provar que o bruto
    sobreviveu nao escreve conteudo. A cadeia e RAW -> CONTEUDO, e inverter a
    ordem cria perda silenciosa — o checkpoint passaria a considerar KNOWN um
    video cujo bruto ninguem guardou.
    """
    if not raw_durou:
        return {'STATE': RAW_NAO_DUROU, 'CONTENT_ID': content_id,
                'PORQUE': ('a API respondeu, mas o RAW nao foi preservado. '
                           'RAW VEM ANTES DE CONTEUDO.')}
    h = hash_do_texto(texto_canonico)
    # `on conflict (canal_id, content_id)` — a identidade da 003/016. RUN_ID,
    # DATASET_ID e CAPTURED_AT ficam FORA dela: se entrassem, a mesma obra
    # viraria N conteudos, um por corrida.
    sql = (
        "with novo as ("
        " insert into public.conteudo"
        " (canal_id, run_id, tipo, content_id, hash_conteudo, originalidade,"
        "  coletado_em, publicado_em, rule_version)"
        " values (%s, %s, %s, %s, %s, %s, now(), %s, %s)"
        " on conflict (canal_id, content_id) do nothing"
        " returning id)"
        " select coalesce((select id from novo),"
        "                 (select id from public.conteudo"
        "                   where canal_id = %s and content_id = %s)),"
        "        (select count(*) from novo),"
        # O hash JA PERSISTIDO volta junto. Sem ele, `DO NOTHING` conta a linha
        # como reencontro saudavel sem nunca ter olhado o que estava la.
        #
        #     ON CONFLICT DO NOTHING SEM COMPARACAO NAO E IDEMPOTENCIA.
        "        coalesce((select hash_conteudo from public.conteudo"
        "                   where canal_id = %s and content_id = %s), '-')"
        % (_lit(canal_id), _lit(run_id), _lit(tipo), _lit(content_id), _lit(h),
           _lit(originalidade), _lit(publicado_em), _lit(rule_version),
           _lit(canal_id), _lit(content_id),
           _lit(canal_id), _lit(content_id)))
    linhas = banco.executa(sql)
    conteudo_id, inseriu = int(linhas[0][0]), linhas[0][1] == '1'
    no_banco = linhas[0][2] if len(linhas[0]) > 2 else '-'
    # A REOBSERVACAO. Uma corrida nova que reencontra o mesmo video NAO cria
    # outro conteudo — cria outra linha de «foi visto de novo».
    #     ONE CONTENT + N OBSERVATIONS.
    #
    # A linha e escrita mesmo quando ha divergencia: esta corrida VIU o video, e
    # isso e um fato de procedencia que nao se apaga. O que ela NAO pode fazer e
    # dizer que estava tudo bem — quem diz isso e o STATE, logo abaixo.
    banco.executa(
        "insert into public.conteudo_visto_em (conteudo_id, run_id, visto_em)"
        " values (%s, %s, now()) on conflict (conteudo_id, run_id) do nothing"
        % (_lit(conteudo_id), _lit(run_id)))

    # ── IDENTIDADE IGUAL + CORPO DIFERENTE NAO E REOBSERVACAO SAUDAVEL ────
    # `content_id` define a identidade — isso continua. Mas o video pode ter
    # sido editado, e um titulo novo entrando calado como «reobservacao OK»
    # apagaria a unica pista de que o mundo mudou.
    #
    # NAO se decide aqui se o texto novo substitui o velho: a linha antiga fica
    # INTACTA. Detectar vem antes de versionar, e a politica de update precisa
    # ser explicita — de uma pessoa, nao de um writer no meio de uma coleta.
    #
    # GAP DECLARADO: o schema de hoje guarda UM `hash_conteudo` por conteudo.
    # Preservar as duas versoes exigiria tabela ou coluna nova, e esta missao
    # nao a cria.
    if not inseriu and no_banco not in ('-', '') and no_banco != h:
        return {'STATE': CONTEUDO_DIVERGIU, 'CONTEUDO_ID': conteudo_id,
                'CONTENT_ID': content_id, 'INSERIU_CONTEUDO': False,
                'REOBSERVACAO': True,
                'HASH_NO_BANCO': no_banco, 'HASH_OBSERVADO': h,
                'CORPO_VERSAO': CORPO_VERSAO,
                'SOBRESCREVEU': False,
                'GAP': ('o schema guarda UM hash_conteudo por conteudo; as duas '
                        'versoes NAO cabem sem coluna ou tabela nova, e criar '
                        'uma nao e decisao deste writer'),
                'POLITICA': ('linha antiga intacta. DETECTAR vem antes de '
                             'VERSIONAR, e escolher qual texto vale e decisao '
                             'de uma pessoa.')}
    return {'STATE': 'OK' if inseriu else REOBSERVADO,
            'CONTEUDO_ID': conteudo_id, 'CONTENT_ID': content_id,
            'INSERIU_CONTEUDO': inseriu, 'REOBSERVACAO': not inseriu}


def conteudo_conhecido(banco, *, canal_id, content_ids):
    """Quais destes JA estao persistidos. E daqui que sai `known`.

    Nao pergunta ao RAW, nao pergunta a API, nao pergunta a memoria do processo.
    KNOWN = PERSISTED, e a unica testemunha disso e a tabela.
    """
    if not content_ids:
        return set()
    lista = ', '.join(_lit(c) for c in content_ids)
    linhas = banco.executa(
        "select content_id from public.conteudo where canal_id = %s"
        " and content_id in (%s)" % (_lit(canal_id), lista))
    return {l[0] for l in linhas}


# ═════════════════════════════════════════════════════════════════════════
# 3 · O COMENTARIO — a ocorrencia tem ID, e a resposta tem pai
# ═════════════════════════════════════════════════════════════════════════
def persistir_comentarios(banco, *, conteudo_id, run_id, comentarios):
    """Grava os comentarios preservando identidade e parentesco.

    `comentarios` sao envelopes do executor. De cada um saem tres coisas que a
    versao anterior do schema nao conseguia guardar juntas: o ID NATIVO (a
    identidade da ocorrencia), o PAI (quem ele responde) e o TEXTO.

        COMMENT_ID NAO E COMMENT_TEXT.
        REPLY NAO E TOP-LEVEL.

    Divergencia de texto no MESMO id nao sobrescreve em silencio: e reportada.
    Sobrescrever apagaria a versao que ja tinhamos sem ninguem saber; e decidir
    qual das duas vale nao e decisao de um writer.
    """
    rel = {'PEDIDOS': len(comentarios), 'INSERIDOS': 0, 'JA_EXISTIAM': 0,
           'TOP_LEVEL': 0, 'REPLIES': 0, 'SEM_ID_NATIVO': [],
           'PAIS_NAO_PERSISTIDOS': [], 'TEXTO_DIVERGIU': []}
    for c in comentarios:
        bruto = c.get('RAW') or {}
        externo = c.get('NATIVE_ID') or bruto.get('COMMENT_ID')
        if not externo or externo == 'None':
            # UNKNOWN NAO PODE VIRAR DUPLICATA AUTOMATICA: sem ID nativo nao ha
            # identidade de ocorrencia, e duas linhas assim colidiriam entre si.
            rel['SEM_ID_NATIVO'].append(bruto.get('TEXT_ORIGINAL'))
            continue
        pai = bruto.get('PARENT_ID')
        texto = c.get('TEXT') or ''
        h = hash_do_texto(texto)
        sql = (
            "with novo as ("
            " insert into public.comentario"
            " (conteudo_id, run_id, externo_id, parent_externo_id, autor_hash,"
            "  texto, hash_conteudo, publicado_em)"
            " values (%s, %s, %s, %s, %s, %s, %s, %s)"
            " on conflict (conteudo_id, externo_id) do nothing"
            " returning id)"
            # `coalesce(..., '-')` e o idioma da casa (`coleta_checkpoint.pode_gastar`):
            # campo final VAZIO some no recorte do psql, e contar colunas depois
            # explodiria com IndexError. Um marcador que nunca e vazio evita isso.
            " select (select count(*) from novo),"
            "        coalesce((select hash_conteudo from public.comentario"
            "                   where conteudo_id = %s and externo_id = %s), '-')"
            % (_lit(conteudo_id), _lit(run_id), _lit(externo), _lit(pai),
               _lit(autor_hash(bruto.get('AUTHOR_CHANNEL_ID'),
                              platform=c.get('PLATFORM') or 'YOUTUBE')), _lit(texto),
               _lit(h), _lit(c.get('PUBLISHED_AT') if c.get('PUBLISHED_AT') != 'UNKNOWN' else None),
               _lit(conteudo_id), _lit(externo)))
        linhas = banco.executa(sql)
        inseriu = linhas[0][0] == '1'
        hash_no_banco = linhas[0][1] if len(linhas[0]) > 1 else '-'
        hash_no_banco = '' if hash_no_banco == '-' else hash_no_banco
        rel['INSERIDOS' if inseriu else 'JA_EXISTIAM'] += 1
        rel['REPLIES' if pai else 'TOP_LEVEL'] += 1
        if not inseriu and hash_no_banco and hash_no_banco != h:
            rel['TEXTO_DIVERGIU'].append(
                {'EXTERNO_ID': externo, 'STATE': TEXTO_DIVERGIU,
                 'HASH_NO_BANCO': hash_no_banco, 'HASH_OBSERVADO': h,
                 'POLITICA': ('NAO sobrescrito. O texto guardado continua o de '
                              'antes, e a divergencia fica registrada para uma '
                              'pessoa decidir. Escrever por cima apagaria a '
                              'versao anterior sem ninguem saber.')})
    # PAI DECLARADO E NAO PERSISTIDO e um estado, nao um motivo para promover a
    # resposta a topo. `parent_externo_id` continua la, escrito, com o ID que a
    # fonte declarou — a relacao observada nao se perde por causa da ordem.
    linhas = banco.executa(
        "select externo_id, parent_externo_id from public.comentario f"
        " where f.conteudo_id = %s and f.parent_externo_id is not null"
        " and not exists (select 1 from public.comentario p"
        "                  where p.conteudo_id = f.conteudo_id"
        "                    and p.externo_id = f.parent_externo_id)"
        % _lit(conteudo_id))
    rel['PAIS_NAO_PERSISTIDOS'] = [
        {'EXTERNO_ID': l[0], 'PARENT_EXTERNO_ID': l[1], 'STATE': PAI_NAO_PERSISTIDO}
        for l in linhas]
    return rel


def thread_do_conteudo(banco, *, conteudo_id):
    """Reconstroi a conversa SO pelo banco. Se isto falhar, a thread morreu.

    Nenhum RAW e aberto aqui — e esse e o teste. Uma camada estruturada que so
    consegue dizer quem responde a quem lendo o bruto nao esta representando
    comentario, esta guardando texto.
    """
    linhas = banco.executa(
        "select externo_id, coalesce(parent_externo_id, ''), texto"
        " from public.comentario where conteudo_id = %s order by id"
        % _lit(conteudo_id))
    arvore, topo = {}, []
    for externo, pai, texto in linhas:
        arvore.setdefault(externo, {'EXTERNO_ID': externo, 'TEXTO': texto,
                                    'PARENT': pai or None, 'RESPOSTAS': []})
    for externo, pai, _t in linhas:
        if pai and pai in arvore:
            arvore[pai]['RESPOSTAS'].append(arvore[externo])
        elif not pai:
            topo.append(arvore[externo])
    return {'TOP_LEVEL': topo,
            'ORFAS': [arvore[e] for e, p, _ in linhas if p and p not in arvore]}


if __name__ == '__main__':
    print(__doc__)
