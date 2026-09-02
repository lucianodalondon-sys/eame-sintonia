#!/usr/bin/env python3
"""
O MONITOR DIÁRIO — o que o concorrente publicou hoje, e o que disso é notícia.

    py scripts/instagram_diario.py fila       # GRÁTIS: quem vence hoje, e por quê
    py scripts/instagram_diario.py rodar      # a passada do dia
    py scripts/instagram_diario.py noticia    # GRÁTIS: o que MUDOU desde ontem

O QUE MUDA QUANDO A COLETA É DIÁRIA
-------------------------------------
O muro do Instagram deixa ver os **12 posts mais recentes** de cada conta, e nada além.
Lido uma vez, isso é uma amostra pobre de uma conta com 1.974 posts. Lido TODO DIA, é
cobertura completa do que é novo — para sempre.

    O MURO DE 12 SÓ MACHUCA QUEM QUER HISTÓRIA. QUEM QUER O AGORA, ELE BASTA.

E o número não é meu: `coletar-perfil-instagram.py` do portal-sintonia (Brasil) já fixa
`POSTS_POR_PERFIL = 12`, com o comentário *"recentes bastam: queremos a conversa de
agora"*. A régua da casa e o teto da rota são o mesmo número, por acidente feliz.

AS RÉGUAS QUE ESTE ARQUIVO HERDA DO BRASIL, E NÃO REINVENTA
-------------------------------------------------------------
| régua | de onde vem | o que faz aqui |
|---|---|---|
| 12 posts por perfil | `coletar-perfil-instagram.py` | o teto da leitura diária |
| `MADURO = 7` dias | idem | post com mais de 7 dias não é relido por comentário |
| cadência por tipo | `REGUAS-DA-COLETA.md` | de quantos em quantos dias cada conta volta |
| a SECA | idem | conta sem novidade em 3 visitas triplica a cadência, teto 45 dias |
| `autor_hash` | `coletar-instagram.py` | o autor do comentário nunca entra em claro |
| `hash_conteudo` | idem | dedupe pelo TEXTO, não pelo id |
| `publicado_em` EXATA | idem | a data é do comentário, nunca a do post |
| PASSA · NÃO SEI · BARRA | `REGUAS-DA-COLETA.md` | três vereditos, nunca dois |

A LEI MAIS CARA QUE VEM DE LÁ
-------------------------------
`camada-da-fonte.sql` registra o defeito: o Brasil lia `tipo='post'` como *"a camada
técnica falando"* — e aí **a Syngenta escrevendo sobre nematoide virava "resposta técnica
publicada"**, e a ferramenta respondia *"esse assunto já está coberto"* quando o que
estava coberto era o concorrente vendendo.

Aqui é pior: nesta missão **todo documento é de concorrente**. Por isso cada item nasce
com `CAMADA = CONCORRENTE_FALANDO`, e nunca com nada que se pareça com cobertura técnica.

    POST DE CONCORRENTE NÃO É RESPOSTA TÉCNICA. É O CONCORRENTE VENDENDO.

A ACUMULAÇÃO DE COMENTÁRIO — POR QUE LER TODO DIA COBRE MAIS
--------------------------------------------------------------
A rota deslogada entrega uma FATIA dos comentários: medido em 7 posts, 18 de 31 (58%);
num post de 1 comentário, 100%; num de 782, 15. A fatia é dos mais recentes.

Lendo o mesmo post por 7 dias e juntando pelo `hash_conteudo`, o que uma leitura só perde
a próxima pega — porque o comentário de hoje é o mais recente de hoje. Não vira 100%, e
este arquivo NUNCA diz que virou: `COMMENTS_DECLARED` fica ao lado de
`COMMENTS_COLLECTED`, sempre.

AUTORIZAÇÃO — DECLARADA, DATADA, E NÃO INVENTADA POR MIM
----------------------------------------------------------
O `robots.txt` do Instagram fecha para todos (`User-agent: *` / `Disallow: /`) e o
cabeçalho dele proíbe coleta automatizada sem permissão escrita. O `PROTOCOLO-coleta.md`
desta casa classificaria isso como NÃO AUTORIZADO.

Em 02/09/2026 o Luciano autorizou expressamente seguir por esta rota, ciente disso. A
decisão é dele, está registrada em `docs/decisoes/`, e cada artefato carrega
`ROUTE_AUTHORIZATION` dizendo em que regime foi colhido — para que ninguém, depois,
confunda o que veio da API oficial com o que veio daqui.

O QUE CONTINUA TRANCADO, E NÃO É QUESTÃO DE TERMOS DE USO
-----------------------------------------------------------
O TEXTO do comentário é dado pessoal de pessoa física na UE. `instagram_pessoal.py`
continua sendo o dono disso: pseudônimo no lugar do handle, bruto fora do Git, retenção
`UNDECLARED_PENDING_LEGAL_REVIEW`. Termos de uso são contrato com a Meta; GDPR é gente.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cdp                       # noqa: E402
import instagram_janela as ij    # noqa: E402
import instagram_pessoal as ip   # noqa: E402

SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'INSTAGRAM-DIARIO')
ESTADO = os.path.join(SAIDA, 'ESTADO.json')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

# ── as réguas herdadas, com o dono de cada uma ──────────────────────────────────
POSTS_POR_PERFIL = 12      # portal-sintonia/coletar-perfil-instagram.py
MADURO_DIAS = 7            # idem — comentário chega nas primeiras horas
CADENCIA = {               # portal-sintonia/REGUAS-DA-COLETA.md
    'imprensa': 3, 'creator': 7, 'produtor': 7, 'portal': 7,
    'concorrente': 1,      # ⭐ ACRÉSCIMO LOCAL: nesta missão o concorrente é o alvo,
                           #    e "dado do dia a dia" é o pedido. 1 dia.
    'tecnico': 14, 'associacao': 14, 'pesquisador': 30, 'instituicao': 30,
}
CADENCIA_OUTROS = 21
SECA_MINIMO_VISITAS = 3    # menos que isso não é medição
SECA_MULTIPLICA = 3
SECA_TETO_DIAS = 45

# Quanto o número de seguidores precisa mexer para ser notícia. Abaixo disso é ruído da
# própria tela: a página arredonda ("18,7 mil") e o arredondamento oscila sozinho.
RUIDO_SEGUIDORES = 0.01    # 1%


def agora():
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def hoje():
    import datetime
    return datetime.date.today().isoformat()


def _dias_desde(iso):
    import datetime
    if not iso or iso == NAO_SEI:
        return None
    try:
        d = datetime.date.fromisoformat(str(iso)[:10])
    except ValueError:
        return None
    return (datetime.date.today() - d).days


def _hash(texto, n=32):
    """Dedupe pelo CONTEÚDO. Herdado do Brasil: id de plataforma muda, texto não."""
    return hashlib.sha256(('sintonia-eame|' + (texto or '')).encode('utf-8')).hexdigest()[:n]


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/INSTAGRAM-DIARIO/' + nome


def _estado():
    if not os.path.exists(ESTADO):
        return {'CONTAS': {}, 'OBJETOS': {}, 'COMENTARIOS': {}}
    with open(ESTADO, encoding='utf-8') as f:
        return json.load(f)


def _gravar_estado(e):
    e['ATUALIZADO_EM'] = agora()
    _gravar('ESTADO.json', e)


# ══════════════════════════════════════════════════════════════ FASE 1 · A FILA
def cadencia_de(conta, est):
    """De quantos em quantos dias esta conta volta. NUNCA nula — a lei do Brasil.

    Cadência vazia numa fonte já coletada fazia a linha SUMIR sem erro e sem aviso, porque
    comparar com nulo não dá falso: dá nulo, e o banco descarta.
    """
    base = CADENCIA.get((conta.get('TIPO_DE_FONTE') or 'concorrente').lower(),
                        CADENCIA_OUTROS)
    h = est['CONTAS'].get(conta['ACCOUNT_HANDLE']) or {}
    visitas = h.get('VISITAS', 0)
    secas = h.get('VISITAS_SEM_NOVIDADE', 0)
    if visitas >= SECA_MINIMO_VISITAS and secas >= SECA_MINIMO_VISITAS:
        return min(base * SECA_MULTIPLICA, SECA_TETO_DIAS), 'SECA (%d visitas sem novidade)' % secas
    return base, 'cadência do tipo'


def fila(mostrar=True):
    """Quem vence hoje. Custo zero, e é o que impede visitar quem não precisa."""
    est = _estado()
    fora = []
    for c in ij.contas():
        c.setdefault('TIPO_DE_FONTE', 'concorrente')
        dias, motivo = cadencia_de(c, est)
        h = est['CONTAS'].get(c['ACCOUNT_HANDLE']) or {}
        desde = _dias_desde(h.get('ULTIMA_VISITA'))
        vence = desde is None or desde >= dias
        fora.append({'ACCOUNT_HANDLE': c['ACCOUNT_HANDLE'], 'COMPANY': c['COMPANY'],
                     'COUNTRY_SCOPE': c['COUNTRY'], 'CADENCIA_DIAS': dias,
                     'CADENCIA_MOTIVO': motivo,
                     'ULTIMA_VISITA': h.get('ULTIMA_VISITA', 'nunca'),
                     'DIAS_DESDE': desde if desde is not None else NAO_SEI,
                     'VENCE_HOJE': 'SIM' if vence else 'nao',
                     'VISITAS': h.get('VISITAS', 0),
                     'CONTA': c})
    if mostrar:
        print('%-16s %-9s %-8s %-12s %s' % ('conta', 'cadência', 'vence?', 'última', 'motivo'))
        print('-' * 74)
        for f in fora:
            print('%-16s %6d d  %-8s %-12s %s'
                  % (f['ACCOUNT_HANDLE'], f['CADENCIA_DIAS'], f['VENCE_HOJE'],
                     str(f['ULTIMA_VISITA'])[:10], f['CADENCIA_MOTIVO']))
        print()
        print('vencem hoje: %d de %d · custo: 0,00 USD'
              % (sum(1 for f in fora if f['VENCE_HOJE'] == 'SIM'), len(fora)))
    return fora


# ══════════════════════════════════════════════════════════════ FASE 2 · A PASSADA
def rodar(so_conta=None, forcar=False):
    """A passada do dia: perfil, os 12 recentes, e comentário dos posts ainda maduros.

    `forcar=True` ignora a cadência — o operador pode querer reler antes da hora, e isso
    é decisão dele. Mas fica GRAVADO no artefato: uma passada forçada não é uma passada
    da cadência, e comparar as duas como se fossem iguais seria mudar o método no meio.
    """
    est = _estado()
    todas = fila(mostrar=False)
    devidas = [f for f in todas
               if (forcar or f['VENCE_HOJE'] == 'SIM')
               and (not so_conta or f['ACCOUNT_HANDLE'] == so_conta)]
    if not devidas:
        print('nenhuma conta vence hoje. Isto NÃO é "nada aconteceu" — é a cadência '
              'dizendo que ainda não é hora. Para reler assim mesmo: `rodar --forcar`. '
              'Custo: 0,00 USD.')
        return 0
    if forcar:
        print('⚠️  PASSADA FORÇADA: a cadência não pedia esta leitura. Fica marcada como '
              'tal no artefato.')

    rede = ij.saida_de_rede()
    print('saída de rede: %s / %s' % (rede.get('NETWORK_EXIT_COUNTRY'),
                                      rede.get('NETWORK_EXIT_ORG')))
    cdp.subir(ij.PORTA, perfil=ij.PERFIL)
    novos_posts, novos_coment, contas_lidas = [], [], []

    for f in devidas:
        c = f['CONTA']
        handle = c['ACCOUNT_HANDLE']
        print('\n── %s (%s · %s)' % (handle, c['COMPANY'], c['COUNTRY']))
        antes = est['CONTAS'].get(handle) or {}

        # ── perfil
        try:
            aba, html = cdp.abrir(c['ACCOUNT_URL'], porta=ij.PORTA, espera=6)
            try:
                p = aba.js(ij.JS_PERFIL) or {}
            finally:
                aba.fechar()
        except cdp.Erro as e:
            print('   porta não abriu: %s' % str(e)[:80])
            # Visita que não aconteceu NÃO conta como visita sem novidade — senão a SECA
            # puniria a conta por um defeito da minha ponta.
            est['CONTAS'].setdefault(handle, {})['ULTIMO_ERRO'] = str(e)[:160]
            est['CONTAS'][handle]['ULTIMO_ERRO_EM'] = agora()
            continue

        seg, _como = ij._numero(p.get('SEGUIDORES_TEXTO'))
        codigos = (p.get('CODIGOS_NA_GRADE') or [])[:POSTS_POR_PERFIL]
        vistos_antes = set(antes.get('CODIGOS_VISTOS') or [])
        codigos_novos = [k for k in codigos if k not in vistos_antes]
        destaques_antes = set(antes.get('DESTAQUES') or [])
        destaques = sorted(set(p.get('DESTAQUES') or []))
        destaques_novos = sorted(destaques_antes.symmetric_difference(destaques))
        print('   grade: %d itens · %d NOVOS · destaques: %d%s'
              % (len(codigos), len(codigos_novos), len(destaques),
                 (' (%d mudou)' % len(destaques_novos)) if destaques_novos else ''))

        # ── objetos: os novos por inteiro; os maduros só para comentário
        for cod in codigos:
            tipo, _, sc = cod.partition(':')
            ja = est['OBJETOS'].get(sc) or {}
            e_novo = cod in codigos_novos
            idade = _dias_desde(ja.get('PUBLISHED_AT'))
            # A regra do Brasil: post com mais de 7 dias não é relido por comentário.
            # Reler a foto da semana passada, que ninguém mais comenta, e deixar a de
            # hoje sem ler, é o desperdício que o MADURO existe para impedir.
            maduro = idade is None or idade <= MADURO_DIAS
            if not e_novo and not maduro:
                continue

            if e_novo:
                obj = ij._objeto(handle, {'ACCOUNT_URL': c['ACCOUNT_URL'],
                                          'COMPANY': c['COMPANY'],
                                          'COUNTRY_SCOPE': c['COUNTRY']}, tipo, sc)
                obj['CAMADA'] = 'CONCORRENTE_FALANDO'
                obj['CAMADA_NAO_E'] = ('RESPOSTA_TECNICA_PUBLICADA. Post de concorrente é '
                                       'o concorrente vendendo — ver camada-da-fonte.sql '
                                       'do portal-sintonia.')
                obj['ROUTE_AUTHORIZATION'] = ('BROWSER_UNLOGGED — autorizado por decisão '
                                              'declarada de 2026-09-02, contra o '
                                              'robots.txt do Instagram')
                obj['FIRST_SEEN'] = hoje()
                est['OBJETOS'][sc] = {
                    'PUBLISHED_AT': obj.get('PUBLISHED_AT'),
                    'ACCOUNT_HANDLE': handle, 'FIRST_SEEN': hoje(),
                    'COMMENT_HASHES': [],
                    'COMMENTS_DECLARED': _declarado(obj)}
                novos_posts.append(obj)
                print('      + %s %s (%s)' % (tipo, sc, obj.get('PUBLISHED_AT', '?')[:10]))
                time.sleep(ij.PAUSA)

            # ── comentários: só enquanto o post é maduro, e sempre acumulando
            n_novos = _comentarios(handle, c, tipo, sc, est, novos_coment)
            if n_novos:
                print('        %d comentário(s) novo(s)' % n_novos)
            time.sleep(ij.PAUSA / 2)

        houve_novidade = bool(codigos_novos)
        est['CONTAS'][handle] = {
            'ULTIMA_VISITA': hoje(),
            'VISITAS': antes.get('VISITAS', 0) + 1,
            'VISITAS_SEM_NOVIDADE': 0 if houve_novidade
                                    else antes.get('VISITAS_SEM_NOVIDADE', 0) + 1,
            'CODIGOS_VISTOS': sorted(set(list(vistos_antes) + codigos)),
            'FOLLOWERS': seg,
            'FOLLOWERS_ANTES': antes.get('FOLLOWERS'),
            'BIO': (p.get('TEXTO_VISIVEL') or '')[:600],
            'BIO_ANTES': antes.get('BIO'),
            'GRID_ITEMS': len(codigos),
            'DESTAQUES': destaques,
            'DESTAQUES_ANTES': sorted(destaques_antes),
        }
        contas_lidas.append(handle)

    _gravar_estado(est)
    nome_arq = ('PASSADA-%s%s.json'
                % (hoje(), '-FORCADA-' + agora()[11:16].replace(':', '')
                   if forcar else ''))
    caminho = _gravar(nome_arq, {
        'SOURCE_ID': 'INSTAGRAM-DIARIO/' + nome_arq.replace('.json', ''),
        'PASSADA_FORCADA': 'YES' if forcar else 'NO',
        'PASSADA_FORCADA_SIGNIFICA': (
            'a cadência não pedia esta leitura; o operador pediu. Duas passadas '
            'no mesmo dia NÃO são comparáveis com uma sequência de passadas '
            'diárias — comparar as duas seria mudar o método no meio.'),
        'source': 'passada diária pela rota pública, em Chrome com janela, deslogado',
        'SOURCE_LOCATION': 'Instagram',
        'FACT_LOCATION': 'NOT_KNOWN — sai do conteúdo, nunca da conta',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'CAMADA': 'CONCORRENTE_FALANDO',
        'ROUTE_AUTHORIZATION': ('BROWSER_UNLOGGED — decisão declarada de 2026-09-02. '
                                'O robots.txt do Instagram fecha para todos; a decisão '
                                'de seguir assim mesmo é do Luciano e está datada.'),
        'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        **rede,
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'ACCOUNTS_DUE': len(devidas), 'ACCOUNTS_READ': len(contas_lidas),
        'NEW_POSTS': len(novos_posts), 'NEW_COMMENTS': len(novos_coment),
        'REGRAS_HERDADAS': {
            'POSTS_POR_PERFIL': POSTS_POR_PERFIL,
            'MADURO_DIAS': MADURO_DIAS,
            'DE_ONDE': 'portal-sintonia (Brasil): coletar-perfil-instagram.py e '
                       'REGUAS-DA-COLETA.md',
        },
        'ITEMS': novos_posts,
        'COMMENTS': novos_coment})
    print('\ngravado: %s' % caminho)
    print('  contas=%d · posts novos=%d · comentários novos=%d · custo=0,00 USD'
          % (len(contas_lidas), len(novos_posts), len(novos_coment)))
    return 0


def _declarado(obj):
    v = [x for x in (obj.get('COMMENT_COUNT_BY_ROUTE') or {}).values()
         if isinstance(x, int)]
    return max(v) if v else 0


def _comentarios(handle, conta, tipo, shortcode, est, saco):
    """Colhe os comentários visíveis e guarda só os INÉDITOS. → quantos entraram.

    O autor NUNCA entra em claro: `instagram_pessoal.pseudonimo()` é o dono disso, e é a
    mesma prática do `autor_hash` do Brasil.
    """
    url = 'https://www.instagram.com/%s/%s/' % ('reel' if tipo == 'reel' else 'p',
                                                shortcode)
    try:
        aba, _h = cdp.abrir(url, porta=ij.PORTA, espera=8)
        try:
            r = aba.js(ij.JS_COMENTARIOS) or {}
        finally:
            aba.fechar()
    except cdp.Erro:
        return 0
    reg = est['OBJETOS'].setdefault(shortcode, {'COMMENT_HASHES': []})
    ja = set(reg.get('COMMENT_HASHES') or [])
    n = 0
    for c in (r.get('COMENTARIOS') or []):
        hc = _hash((c.get('TEXTO') or '') + '|' + shortcode)
        if hc in ja:
            continue
        ja.add(hc)
        n += 1
        saco.append({
            'PLATAFORMA': 'instagram', 'TIPO': 'comentario',
            'HASH_CONTEUDO': hc,
            'MIDIA_ID': shortcode,
            'ACCOUNT_HANDLE': handle, 'COMPANY': conta.get('COMPANY'),
            'COUNTRY_SCOPE': conta.get('COUNTRY'),
            'TEXTO': c.get('TEXTO'),
            'AUTOR_PSEUDONIMO': ip.pseudonimo(c.get('AUTOR')),
            'AUTOR_HANDLE': 'REDACTED_BY_POLICY',
            'CURTIDAS': c.get('CURTIDAS'),
            # A fonte deu tempo RELATIVO ("19 h"). Converter em data inventaria precisão.
            'PUBLICADO_EM': (str(c.get('TEMPO_ABSOLUTO'))[:10]
                             if c.get('TEMPO_ABSOLUTO') else NAO_SEI),
            'PUBLICADO_RELATIVO': c.get('TEMPO_RELATIVO'),
            'PRIMEIRA_VEZ_VISTO': hoje(),
            'PROCESSADO': False,
            'CAMADA': 'AUDIENCIA',
            'EVIDENCE_CLASS': 'FIELD_VOICE_OBSERVED',
            'NAO_E': ('FIELD_PROBLEM_CONFIRMED, e nem VOZ DO AGRICULTOR: um comentário é '
                      'de quem comentou, e nada garante que seja produtor. O nome certo '
                      'é VOZ DO CAMPO — CAMADAS-DA-VOZ-DO-CAMPO.md do portal-sintonia.'),
            'PERSONAL_DATA': 'YES', 'LEGAL_REVIEW': 'PENDING',
            'RETENTION_STATE': ip.RETENCAO,
        })
    reg['COMMENT_HASHES'] = sorted(ja)
    reg['COMMENTS_COLLECTED'] = len(ja)
    reg['COMMENTS_DECLARED'] = max(reg.get('COMMENTS_DECLARED', 0), r.get('N', 0))
    reg['ULTIMA_LEITURA_DE_COMENTARIO'] = hoje()
    return n


# ══════════════════════════════════════════════════════════════ FASE 3 · A NOTÍCIA
def noticia():
    """O que MUDOU. Custo zero, e é o produto — não o despejo de dados.

    Um relatório que lista tudo o que existe não é notícia; é inventário. Notícia é a
    DIFERENÇA entre hoje e ontem, e cada linha aqui carrega o número que a sustenta.
    """
    est = _estado()
    os.makedirs(SAIDA, exist_ok=True)
    passada = None
    for n in sorted(os.listdir(SAIDA), reverse=True):
        if n.startswith('PASSADA-'):
            with open(os.path.join(SAIDA, n), encoding='utf-8') as f:
                passada = json.load(f)
            break
    if not passada:
        print('nenhuma passada ainda. Rode `py scripts/instagram_diario.py rodar`.')
        return 1

    # ── A PRIMEIRA PASSADA NÃO É NOTÍCIA, É O RETRATO INICIAL ───────────────────
    # Na primeira visita a uma conta, TUDO é inédito: os 12 da grade e todos os
    # comentários que a tela mostra. Chamar isso de "60 posts novos hoje" faria o
    # relatório dizer que os concorrentes publicaram 60 posts hoje — quando o que
    # aconteceu foi eu ter olhado pela primeira vez.
    #
    #     PRIMEIRA LEITURA NÃO É MUDANÇA. É A LINHA DE BASE.
    #
    # É a mesma família da armadilha da Biblioteca de Anúncios que já pegou esta casa:
    # ler mais fundo entre duas medições virou "587 anúncios novos em uma hora".
    contas_de_primeira = {h for h, v in (est.get('CONTAS') or {}).items()
                          if (v or {}).get('VISITAS', 0) <= 1}

    def _rotulo(handle, tipo_novo):
        return 'LINHA_DE_BASE' if handle in contas_de_primeira else tipo_novo

    linhas = []
    for p in passada.get('ITEMS') or []:
        linhas.append({
            'TIPO_DE_NOTICIA': _rotulo(p.get('ACCOUNT_HANDLE'), 'POST_NOVO'),
            'ACCOUNT_HANDLE': p.get('ACCOUNT_HANDLE'), 'COMPANY': p.get('COMPANY'),
            'COUNTRY_SCOPE': p.get('COUNTRY_SCOPE'),
            'QUANDO': p.get('PUBLISHED_AT', NAO_SEI),
            'O_QUE': (p.get('CAPTION') or '')[:240],
            'MEDIA': p.get('MEDIA_TYPE'), 'VIDEO': p.get('IS_VIDEO'),
            'CURTIDAS': p.get('LIKE_COUNT_EMBED'),
            'VISUALIZACOES': p.get('VIDEO_VIEW_COUNT'),
            'URL': p.get('SOURCE_URL'),
            'POR_QUE_E_NOTICIA': ('não estava na grade na visita anterior'
                                 if p.get('ACCOUNT_HANDLE') not in contas_de_primeira
                                 else 'PRIMEIRA VISITA a esta conta — isto é o '
                                      'retrato inicial, NÃO uma publicação de hoje'),
        })
    for c in passada.get('COMMENTS') or []:
        linhas.append({
            'TIPO_DE_NOTICIA': _rotulo(c.get('ACCOUNT_HANDLE'), 'COMENTARIO_NOVO'),
            'ACCOUNT_HANDLE': c.get('ACCOUNT_HANDLE'), 'COMPANY': c.get('COMPANY'),
            'COUNTRY_SCOPE': c.get('COUNTRY_SCOPE'),
            'QUANDO': c.get('PUBLICADO_RELATIVO', NAO_SEI),
            'O_QUE': (c.get('TEXTO') or '')[:240],
            'AUTOR': c.get('AUTOR_PSEUDONIMO'),
            'URL': 'https://www.instagram.com/p/%s/' % c.get('MIDIA_ID'),
            'POR_QUE_E_NOTICIA': ('texto inédito neste post'
                                 if c.get('ACCOUNT_HANDLE') not in contas_de_primeira
                                 else 'PRIMEIRA VISITA — linha de base, não novidade'),
            'PERSONAL_DATA': 'YES',
        })
    # mudança de perfil: seguidores e bio
    for handle, h in (est.get('CONTAS') or {}).items():
        a, b = h.get('FOLLOWERS_ANTES'), h.get('FOLLOWERS')
        if isinstance(a, int) and isinstance(b, int) and a > 0:
            var = (b - a) / float(a)
            if abs(var) >= RUIDO_SEGUIDORES:
                linhas.append({
                    'TIPO_DE_NOTICIA': 'SEGUIDORES_MEXERAM',
                    'ACCOUNT_HANDLE': handle, 'QUANDO': hoje(),
                    'O_QUE': '%d → %d (%+.1f%%)' % (a, b, var * 100),
                    'POR_QUE_E_NOTICIA': ('variou mais que o ruído de arredondamento da '
                                          'própria tela (%.0f%%)' % (RUIDO_SEGUIDORES * 100)),
                })
        if h.get('BIO_ANTES') and h.get('BIO') and h['BIO_ANTES'] != h['BIO']:
            linhas.append({
                'TIPO_DE_NOTICIA': 'BIO_MUDOU', 'ACCOUNT_HANDLE': handle,
                'QUANDO': hoje(), 'O_QUE': h['BIO'][:240],
                'POR_QUE_E_NOTICIA': 'a conta reescreveu a própria apresentação'})

    caminho = _gravar('NOTICIA-%s.json' % hoje(), {
        'SOURCE_ID': 'INSTAGRAM-DIARIO/NOTICIA-%s' % hoje(),
        'source': 'diferença entre a passada de hoje e o estado anterior — nada é coletado aqui',
        'CAPTURED_AT': agora(), 'MISSION': MISSION,
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_NAO_E': ('inventário. Um relatório que lista tudo o que existe não é '
                             'notícia. Aqui só entra o que MUDOU, com o número que sustenta.'),
        'SILENCIO_SIGNIFICA': ('zero linhas é "nada mudou nas contas visitadas hoje" — '
                               'NUNCA "o concorrente parou". Conta que não venceu a '
                               'cadência não foi visitada, e isso está na fila.'),
        'BASELINE_ACCOUNTS': sorted(contas_de_primeira),
        'BASELINE_SIGNIFICA': ('conta visitada pela PRIMEIRA vez: tudo o que ela '
                               'trouxe é retrato inicial, nunca "publicou hoje". '
                               'A notícia de verdade começa na segunda passada.'),
        'ITEM_COUNT': len(linhas), 'ITEMS': linhas})

    from collections import Counter
    print('NOTÍCIA DE %s' % hoje())
    print('-' * 60)
    for t, n in Counter(l['TIPO_DE_NOTICIA'] for l in linhas).most_common():
        print('  %-22s %d' % (t, n))
    print()
    for l in linhas[:12]:
        print('  [%s] @%s' % (l['TIPO_DE_NOTICIA'], l.get('ACCOUNT_HANDLE')))
        print('      %s' % str(l.get('O_QUE'))[:150].replace('\n', ' '))
    if not linhas:
        print('  nada mudou nas contas visitadas hoje.')
        print('  (isto NÃO é "o concorrente parou" — é silêncio nas contas que venceram.)')
    print()
    print('gravado: %s · custo=0,00 USD' % caminho)
    return 0


FASES = {'fila': lambda: fila() and 0, 'rodar': rodar, 'noticia': noticia}

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'fila'
    if cmd == 'fila':
        fila()
        raise SystemExit(0)
    if cmd == 'rodar':
        alvo = next((a for a in sys.argv[2:] if not a.startswith('--')), None)
        raise SystemExit(rodar(alvo, forcar='--forcar' in sys.argv))
    if cmd == 'noticia':
        raise SystemExit(noticia())
    print('uso: instagram_diario.py {fila|rodar [conta] [--forcar]|noticia}')
    raise SystemExit(2)
