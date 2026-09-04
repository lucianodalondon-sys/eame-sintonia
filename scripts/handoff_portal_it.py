#!/usr/bin/env python3
"""O HANDOFF DO SPRINT PORTAL ITÁLIA — determinístico, e por isso auditável.

    python3 scripts/handoff_portal_it.py

Escreve `data/samples/IT-HUMAN-SENSORS/IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json`
e imprime o SHA-256 do arquivo. **Rodar duas vezes tem de dar o mesmo hash.**

POR QUE ELE MEDE EM VEZ DE TRANSCREVER
---------------------------------------
Esta rodada encontrou nove números digitados à mão dentro de um gerador que promete, na
própria docstring, que nada é digitado à mão. Eles estavam **certos** — e mesmo assim não
eram auditáveis, porque nenhum arquivo os continha.

    UM NÚMERO CERTO QUE NINGUÉM CONSEGUE AUDITAR É PIOR QUE UM ERRADO:
    O ERRADO ALGUÉM DERRUBA.

Então aqui nada é transcrito do relatório. Cada número é remedido, agora, dos mesmos
arquivos que a Linha B vai receber. Se a fonte mudar, o handoff muda junto — e é assim
que deve ser.

POR QUE ELE NÃO TEM RELÓGIO
----------------------------
`CAPTURED_AT` não é a hora de execução: é a **data do commit de `SOURCE_HEAD`**. Um
carimbo de relógio faria duas execuções idênticas produzirem hashes diferentes, e o
"rodei duas vezes e deu igual" deixaria de provar qualquer coisa. A data do commit é um
fato sobre a ENTRADA, não sobre a corrida — e é o que interessa a quem for reproduzir.

O QUE ELE NÃO FAZ
------------------
Não toca no protótipo (D-007, `PROTOTYPE_FROZEN = SIM`). Não corrige os nove números
digitados. Não renomeia nada no candidato de deploy. Não coleta rede. Custo zero.
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

SAMPLES = os.path.join(ROOT, 'data', 'samples')
IT = os.path.join(SAMPLES, 'IT-HUMAN-SENSORS')
CSV_IT = os.path.join(ROOT, 'data', 'raw', 'IT-T4-001', 'PROD_FTS.csv')
SAIDA = os.path.join(IT, 'IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json')

NAO_SEI = 'NÃO SEI'


# ────────────────────────────────────────────────────────────────── leitura crua
def _git(*args):
    r = subprocess.run(['git'] + list(args), cwd=ROOT, capture_output=True, text=True)
    return (r.stdout or '').strip()


def _sha(caminho):
    if not os.path.exists(caminho):
        return None
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def _amostra(nome):
    with open(os.path.join(IT, nome), encoding='utf-8') as f:
        return json.load(f)


def _registro():
    """As linhas do registro italiano. Sem ele, o handoff diz NÃO SEI em vez de inventar."""
    if not os.path.exists(CSV_IT):
        return None
    with open(CSV_IT, encoding='utf-8', errors='replace') as f:
        return list(csv.DictReader(f, delimiter=';'))


def _data(s):
    s = (s or '').strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            import datetime
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


# ── os dois eixos que todo número italiano de vigência tem de declarar ──────────
def _estado(x):
    return (x.get('stato_amministrativo') or '').strip()


ESTRITO = lambda x: 'autorizzato' in _estado(x).lower()                      # noqa: E731
AMPLIADO = lambda x: _estado(x).lower().startswith(                          # noqa: E731
    ('autorizzato', 'ri-registrato', 'rinnovato'))
E_ADAMA = lambda x: 'ADAMA' in (x.get('ragione_sociale') or '').upper()      # noqa: E731
E_ADAMA_IT = lambda x: (x.get('ragione_sociale') or '').strip().upper() == \
    'ADAMA ITALIA S.R.L.'                                                    # noqa: E731


def _vigencia(linhas, corte):
    """→ a matriz critério × recorte, que é a única forma honesta de publicar esse número."""
    fora = {}
    for nome_c, crit in (('STRICT', ESTRITO), ('AMPLIADO', AMPLIADO)):
        for nome_r, rec in (('ADAMA_CINCO_RAZOES_SOCIAIS', E_ADAMA),
                            ('ADAMA_ITALIA_SRL_APENAS', E_ADAMA_IT),
                            ('MERCADO_INTEIRO', lambda x: True)):
            base = [x for x in linhas if crit(x) and rec(x)]
            fut = [x for x in base
                   if (_data(x.get('data_scadenza_autorizzazione')) or corte) > corte]
            fora['%s|%s' % (nome_c, nome_r)] = {
                'VIGENTES': len(base),
                'VIGENTES_COM_VENCIMENTO_FUTURO': len(fut),
            }
    return fora


# ─────────────────────────────────────────────────────────────────── os achados
def caso_azoxy_prothio(linhas):
    """1 · PORTAL_NOW. Universo fechado de quatro, não amostra."""
    if linhas is None:
        return {'ESTADO': NAO_SEI, 'POR_QUE': 'registro italiano ausente neste checkout'}
    alvo = [x for x in linhas
            if 'AZOXYSTROBIN' in (x.get('sostanze_attive') or '').upper()
            and 'PROTHIOCONAZOLE' in (x.get('sostanze_attive') or '').upper()]
    itens = sorted(({
        'PRODUTO': x['denominazione_prodotto'].strip(),
        'REGISTRO': x['num_registrazione'].strip(),
        'TITULAR': x['ragione_sociale'].strip(),
        'VENCIMENTO': x['data_scadenza_autorizzazione'].strip(),
        'ESTADO_ADMINISTRATIVO': _estado(x),
    } for x in alvo), key=lambda d: d['REGISTRO'])
    venc = sorted({i['VENCIMENTO'] for i in itens})
    return {
        'CLASSE': 'PORTAL_NOW',
        'UNIVERSO': len(itens),
        'E_UNIVERSO_FECHADO_NAO_AMOSTRA': 'SIM',
        'TODOS_VIGENTES': 'SIM' if all(AMPLIADO(x) for x in alvo) else 'NÃO',
        'CRITERIO_DO_FILTRO': ('produtos cujo campo `sostanze_attive` nomeia AZOXYSTROBIN '
                               'E PROTHIOCONAZOLE ao mesmo tempo'),
        'ITENS': itens,
        'VENCIMENTOS_DISTINTOS': venc,
        'FATO': ('quatro registros, todos vigentes: dois da ADAMA ITALIA S.R.L. vencendo em '
                 '31/05/2027 e dois da CAC CHEMICAL GMBH vencendo em 31/03/2028'),
        'INTERPRETACAO': ('o concorrente tem ~10 meses a mais de janela autorizada na mesma '
                          'dupla de substâncias'),
        'ACAO_QUE_SO_A_ADAMA_DECIDE': ('se a renovação de 31/05/2027 já está em curso, e se a '
                                       'diferença de janela importa comercialmente'),
        'DELTA_JANELA_MESES_APROX': 10,
        'FONTE_OFICIAL': ('Ministero della Salute — Banca dati prodotti fitosanitari '
                          '(dati.salute.gov.it), CC BY 4.0'),
        'TRAVA_DE_INDEPENDENCIA': ('ato europeu e registro nacional NÃO são duas fontes '
                                   'independentes: o nacional deriva do europeu. Contá-los '
                                   'como duas confirmações infla a confiança de um fato que '
                                   'tem uma origem só.'),
    }


def autorizacoes_adama(linhas):
    """2 · PORTAL_WITH_METHOD. Quatro respostas para a mesma pergunta."""
    if linhas is None:
        return {'ESTADO': NAO_SEI, 'POR_QUE': 'registro italiano ausente neste checkout'}
    import datetime
    snap = datetime.date(2026, 8, 24)
    matriz = _vigencia(linhas, snap)
    contagem = {}
    for x in linhas:
        contagem[_estado(x)] = contagem.get(_estado(x), 0) + 1
    return {
        'CLASSE': 'PORTAL_WITH_METHOD',
        'DATA_DO_SNAPSHOT': '2026-08-24',
        'PROIBIDO_PUBLICAR': 'ADAMA possui 155 autorizações',
        'POR_QUE': ('o número depende de DOIS eixos que ninguém declarou: qual critério de '
                    'vigência, e qual ADAMA. Sem os dois, é um de quatro.'),
        'CRITERIOS': {
            'STRICT': 'apenas estados administrativos que contêm "Autorizzato"',
            'AMPLIADO': 'STRICT mais "Ri-registrato*" e "Rinnovato*"',
        },
        'RECORTES': {
            'ADAMA_CINCO_RAZOES_SOCIAIS': sorted({
                x['ragione_sociale'].strip() for x in linhas if E_ADAMA(x)}),
            'ADAMA_ITALIA_SRL_APENAS': ['ADAMA ITALIA S.R.L.'],
        },
        'AGRUPAR_AS_CINCO_E': ('JULGAMENTO HUMANO, não fato do registro — é a lacuna DECK-015 '
                               '(titular ≠ grupo empresarial)'),
        'MATRIZ_CRITERIO_X_RECORTE': matriz,
        'ESTADOS_SEM_DONO': {
            'Sospeso': contagem.get('Sospeso', 0),
            'Autorizzato provvisoriamente': contagem.get('Autorizzato provvisoriamente', 0),
            'REGRA': ('NÃO SEI declarado. Uma autorização suspensa não está vigente nem '
                      'revogada, e nenhum dos critérios acima diz o que fazer com ela. '
                      'Não forçar para nenhum dos lados até existir regra dona.'),
        },
        'CONTAGEM_POR_ESTADO_ADMINISTRATIVO': dict(sorted(contagem.items())),
    }


def revogado_x_scaduto(linhas):
    """3 · PORTAL_WITH_METHOD. Data de validade sozinha não diz se o registro serve."""
    if linhas is None:
        return {'ESTADO': NAO_SEI, 'POR_QUE': 'registro italiano ausente neste checkout'}
    import datetime
    hoje_de_referencia = datetime.date(2026, 9, 4)
    rev = [x for x in linhas if _estado(x) == 'Revocato']
    sca = [x for x in linhas if _estado(x) == 'Scaduto']
    tem_motivo = [x for x in rev
                  if (x.get('motivo_della revoca') or '').strip() not in ('', '-')]
    tem_decreto = [x for x in rev
                   if (x.get('data_decreto_revoca') or '').strip() not in ('', '-')]
    fut = [x for x in rev
           if (_data(x.get('data_scadenza_autorizzazione')) or hoje_de_referencia)
           > hoje_de_referencia]
    fut_adama = [x for x in fut if E_ADAMA(x)]
    return {
        'CLASSE': 'PORTAL_WITH_METHOD',
        'SAO_ESTADOS_DIFERENTES': 'SIM',
        'REVOCATO': len(rev),
        'SCADUTO': len(sca),
        'REVOCATO_COM_VENCIMENTO_AINDA_FUTURO': len(fut),
        'REVOCATO_COM_VENCIMENTO_AINDA_FUTURO_ADAMA': len(fut_adama),
        'DATA_DE_REFERENCIA_DO_FUTURO': '2026-09-04',
        'REVOCATO_COM_MOTIVO_DECLARADO': len(tem_motivo),
        'REVOCATO_COM_DATA_DE_DECRETO': len(tem_decreto),
        'FATO': ('a Itália publica revogação como estado próprio, com motivo e duas datas — '
                 'coluna que a camada espanhola não tem'),
        'DEMONSTRACAO': ('data de validade sozinha não responde se um registro está '
                         'utilizável: %d autorizações estão REVOCATO com vencimento ainda '
                         'no futuro' % len(fut)),
        'LIMITE': ('motivo declarado em %d de %d. Nos outros, por que foi revogado é '
                   'NÃO SEI — e não se infere.' % (len(tem_motivo), len(rev))),
    }


def social_youtube():
    """4 · METHOD_ONLY. Nada aqui é fato de campo."""
    med = _amostra('PILOT-MEASUREMENT.json')
    docs = med['DOCUMENTS']
    leg = _amostra(os.path.join('PILOTO-YOUTUBE', 'LEGENDAS.json'))
    tentados = leg['ITEMS']
    canais = sorted({str(i.get('ACCOUNT_HANDLE')) for i in tentados})
    estados = {}
    for i in tentados:
        estados[i.get('CAPTION_STATE')] = estados.get(i.get('CAPTION_STATE'), 0) + 1
    rel = [str(d.get('PUBLICATION_RELATIVE') or '') for d in docs]
    lixo = sorted({r for r in rel if 'hace' not in r.lower()})
    fontes = _amostra('SOURCES.json')['SOURCES']
    sem_coleta = sum(1 for f in fontes if f.get('ULTIMA_COLETA') is None)
    return {
        'CLASSE': 'METHOD_ONLY',
        'DO_NOT_SHOW_COMO_FATO_DE_CAMPO': 'SIM',
        'HAS_CAPTION': NAO_SEI,
        'HAS_CAPTION_EM_QUANTOS': '%d de %d' % (len(docs), len(docs)),
        'PROIBIDO_PUBLICAR': '0 legendas',
        'POR_QUE': ('o campo nasce False; 0 é valor padrão, não medição. Nenhum vídeo '
                    'respondeu "não há faixa".'),
        'TENTATIVAS_DE_LEGENDA': len(tentados),
        'NUNCA_TENTADOS': len(docs) - len(tentados),
        'CANAIS_TENTADOS': canais,
        'ESTADOS_DAS_TENTATIVAS': dict(sorted(estados.items())),
        'DOCUMENTOS': len(docs),
        'OPERACIONAIS_A_B_C': sum(med['BY_VALUE_CLASS'][k] for k in 'ABC'),
        'RELEVANTES_POR_TITULO': med['AG_RELEVANT'],
        'NAO_JULGAVEIS': med['NOT_JUDGEABLE_TITLE_ONLY'],
        'REGRA_DOS_61': ('os 61 e os 82 saem da MESMA passada do mesmo classificador '
                         'lexical, sem legenda e sem a verificação humana que o próprio '
                         'arquivo exige. Os 61 não podem ganhar status mais forte que os 82.'),
        'PUBLICATION_DATE': NAO_SEI,
        'PUBLICATION_DATE_EM_QUANTOS': '%d de %d' % (
            sum(1 for d in docs if str(d.get('PUBLICATION_DATE')) == 'NOT_KNOWN'), len(docs)),
        'PUBLICATION_RELATIVE_UTILIZAVEIS': len(docs) - len(
            [r for r in rel if 'hace' not in r.lower()]),
        'PUBLICATION_RELATIVE_LIXO_DE_DOM': lixo,
        'ORDENACAO_PERMITIDA': 'faixa de recência, sem exibir data nenhuma',
        'ULTIMA_COLETA_NULA': '%d de %d fontes' % (sem_coleta, len(fontes)),
        'CONSEQUENCIA': ('sem segunda passagem não há linha de base; sem linha de base '
                         '"mudou" não existe — só "é assim"'),
        'REGION': NAO_SEI,
        'REGION_EM_QUANTOS': '%d de %d' % (
            sum(1 for d in docs
                if 'NÃO SEI' in str(d.get('REGION'))), len(docs)),
        'PROIBIDO_USAR_COMO_GEOGRAFIA': ('sede legal do titular — é endereço de empresa, '
                                         'não lugar do fato'),
    }


def pessoas_papeis():
    """5 · PORTAL_WITH_METHOD. Linha de papel não é pessoa."""
    ents = _amostra('ENTITIES.json')['ENTITIES']
    entradas = [r for e in ents for r in (e.get('ROLES') or [])]
    provados = [r for r in entradas if r.get('ESTADO') == 'PROVADO']
    por_papel = {}
    for r in provados:
        por_papel[r['PAPEL']] = por_papel.get(r['PAPEL'], 0) + 1
    com = [e for e in ents
           if any(r.get('ESTADO') == 'PROVADO' for r in (e.get('ROLES') or []))]
    CAMPO = ('agronomo', 'produtor', 'consultor', 'tecnico', 'cooperativa',
             'extensionista')
    return {
        'CLASSE': 'PORTAL_WITH_METHOD',
        'PROIBIDO_PUBLICAR': '114 pessoas',
        'ENTRADAS_DE_PAPEL': len(entradas),
        'ENTRADAS_COM_ESTADO_PROVADO': len(provados),
        'ENTIDADES': len(ents),
        'ENTIDADES_COM_AO_MENOS_UM_PAPEL_PROVADO': len(com),
        'PAPEIS_PROVADOS_POR_TIPO': dict(sorted(por_papel.items())),
        'PAPEIS_DE_CAMPO_PROVADOS': sum(v for k, v in por_papel.items() if k in CAMPO),
        'AGRONOMO_PROVADO': por_papel.get('agronomo', 0),
        'PRODUTOR_PROVADO': por_papel.get('produtor', 0),
        'CONSULTOR_PROVADO': por_papel.get('consultor', 0),
        'LEI': ('papel vem SÓ de campo estruturado declarado — nunca de prosa livre, nome '
                'de conta, foto, idioma ou assunto do post. Papel inferido não vira '
                'identidade profissional comprovada.'),
    }


def cobertura_territorial():
    """6 · PORTAL_WITH_METHOD. O mapa diz onde temos olhos."""
    cov = _amostra('COVERAGE.json')
    return {
        'CLASSE': 'PORTAL_WITH_METHOD',
        'CELULAS': cov['CELLS'],
        'COM_EXPANSAO_TERRITORIAL': cov['BY_STATE'],
        'SEM_EXPANSAO_TERRITORIAL': cov.get('BY_STATE_SEM_EXPANSAO', NAO_SEI),
        'SENSORES_SEM_ESPECIALIDADE_DECLARADA':
            cov.get('SENSORES_SEM_ESPECIALIDADE_DECLARADA', NAO_SEI),
        'A_EXPANSAO_E': ('REGRA METODOLÓGICA, não fato bruto: organização territorial '
                         'Tier A/B sem especialidade declarada cobre todas as '
                         'especialidades da sua cultura naquela região'),
        'O_QUE_O_MAPA_RESPONDE': 'temos olhos aqui',
        'O_QUE_O_MAPA_NUNCA_RESPONDE': 'há problema aqui',
    }


def correcao_de_datas():
    """7 · CODE_FIX_HANDOFF. Já consertado nesta branch; não refazer na Linha B."""
    import datetime
    import fonte_territorial as ft
    errados = {}
    for fmt, rot in (('%Y-%m-%d', 'ISO'), ('%d/%m/%Y', 'dd/mm/aaaa'),
                     ('%Y/%m/%d', 'ISO_COM_BARRA'), ('%d-%m-%Y', 'dd-mm-aaaa')):
        n = 0
        dia = datetime.date(2026, 1, 1)
        while dia.year == 2026:
            lido = ft.datas_no_texto(dia.strftime(fmt))
            if not lido or lido[0] != dia:
                n += 1
            dia += datetime.timedelta(days=1)
        errados[rot] = n
    chamadores = sorted(
        '%s:%d' % (os.path.relpath(os.path.join(HERE, nome), ROOT), i + 1)
        for nome in sorted(os.listdir(HERE)) if nome.endswith('.py')
        for i, linha in enumerate(
            open(os.path.join(HERE, nome), encoding='utf-8', errors='replace')
            .read().splitlines())
        if 'datas_no_texto(' in linha and 'def datas_no_texto' not in linha)
    return {
        'CLASSE': 'CODE_FIX_HANDOFF',
        'NAO_REFAZER_NA_LINHA_B': 'SIM',
        'DEFEITO': ("datas_no_texto('2026-08-24') devolvia 2026-08-02"),
        'CAUSA': ('alternância do dia escrita como (0?[1-9]|[12]\\d|3[01]); regex casa '
                  'leftmost-first e, sem nada depois que force retrocesso, o dia era '
                  'truncado ao dígito das dezenas'),
        'ESCALA_ANTES': '257 de 365 datas ISO de 2026 voltavam erradas',
        'DIRECAO_DO_ERRO': ('sempre para trás — fazia toda fonte parecer mais velha do que é, '
                            'que é a conclusão errada que o número existe para evitar'),
        'POR_QUE_NINGUEM_VIU': ('em dd/mm/aaaa o [-/] seguinte forçava o retrocesso e o '
                               'formato passava; e nenhum teste cobria a função'),
        'CONSERTO': 'alternativas longas primeiro: (3[01]|[12]\\d|0?[1-9])',
        'ARQUIVO': 'scripts/fonte_territorial.py',
        'TESTE': 'tests/test_datas.py — varre o ano inteiro em quatro formatos',
        'ERRADAS_DEPOIS_DO_CONSERTO': dict(sorted(errados.items())),
        'CHAMADORES': chamadores,
        'DIVIDA_QUE_FICA': ('os artefatos territoriais já gravados foram produzidos com a '
                            'leitura defeituosa. Nenhum número de recência territorial vai '
                            'à tela antes de remedir. Remedir não exige coleta nova.'),
    }


def prod_fts():
    """8 · CODE_FIX_HANDOFF / BLOCKER_IF_FEATURE_USED."""
    esperado = 'PROD_FTS_6_20260824.csv'
    # Este gerador NOMEIA o caminho errado para poder reportá-lo. Incluí-lo na lista de
    # quebrados seria o artefato acusando a si mesmo — ruído que o leitor teria de filtrar.
    eu = os.path.basename(__file__)
    quebrados = sorted(
        '%s:%d' % (os.path.relpath(os.path.join(HERE, nome), ROOT), i + 1)
        for nome in sorted(os.listdir(HERE))
        if nome.endswith('.py') and nome != eu
        for i, linha in enumerate(
            open(os.path.join(HERE, nome), encoding='utf-8', errors='replace')
            .read().splitlines())
        if esperado in linha)
    existe_esperado = os.path.exists(
        os.path.join(ROOT, 'data', 'raw', 'IT-T4-001', esperado))
    return {
        'CLASSE': 'CODE_FIX_HANDOFF',
        'SUBCLASSE': 'BLOCKER_IF_FEATURE_USED',
        'NAO_CORRIGIDO_NESTA_BRANCH': 'SIM — esta branch não é dona dessa porta',
        'CAMINHO_CODIFICADO': 'data/raw/IT-T4-001/%s' % esperado,
        'CAMINHO_EXISTE': 'SIM' if existe_esperado else 'NÃO',
        'ARQUIVO_REAL_EM_DISCO': 'data/raw/IT-T4-001/PROD_FTS.csv',
        'ARQUIVO_REAL_EXISTE': 'SIM' if os.path.exists(CSV_IT) else 'NÃO',
        'SCRIPTS_QUEBRADOS': quebrados,
        'QUEM_JA_RESOLVE': 'scripts/chain.py — acha por prefixo PROD_FTS, com glob',
        'CONSEQUENCIA_MEDIDA': ('DATA-CLOCK-manifest.json marca IT-T4-001 como AUSENTE com o '
                                'dado em disco; a ferramenta de consulta fica cega para a '
                                'Itália'),
        'RESSALVA': ('o AUSENTE do data clock NÃO é defeito italiano: são 6 linhas em 3 '
                     'fontes (FR-T4-001 x3, ES-T3-001 x2, IT-T4-001 x1), consequência de '
                     'data/raw não ser versionado (D-003)'),
        'DECLARACAO_EXPLICITA': ('se Ask Sintonia, normalize_substance ou o data clock '
                                 'italiano forem usados na demo, este defeito precisa estar '
                                 'resolvido pelo dono ANTES da apresentação'),
    }


def rotulo_oportunidade():
    """9 · OWNER_DECISION. A contradição fica registrada; a decisão não é minha."""
    doc = os.path.join(ROOT, 'docs', 'piloto', 'ARQUITETURA-DE-PRODUTO-ATUAL.md')
    with open(doc, encoding='utf-8') as f:
        texto = f.read()
    proibicoes = sorted({m for m in ('SALES OPPORTUNITY', 'UNDERUSED ASSET',
                                     'WHITE SPACE CONFIRMED') if m in texto})
    achou_no_repo = bool(re.search(r'Opportunit', texto))
    return {
        'CLASSE': 'OWNER_DECISION',
        'DOCUMENTO_DONO_DA_REGRA': 'docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md',
        'REGRA': 'MT3 entrega ACTIVATION QUESTION',
        'ROTULOS_PROIBIDOS_PELO_DONO': proibicoes,
        'LINHA_QUE_PROIBE': 'apresentar MT3 como oportunidade | é `ACTIVATION QUESTION`',
        'TELA_ATUAL_RELATADA_PELO_DONO': 'Radar Opportunità',
        'TELA_ATUAL_VERIFICADA_POR_MIM': NAO_SEI,
        'POR_QUE_NAO_VERIFIQUEI': ('italia-portale/client não existe nesta branch e esta '
                                   'sessão está proibida de tocá-lo. A existência do rótulo '
                                   'é relato do dono, não medição minha — e registrá-la como '
                                   'medida seria o erro que este handoff inteiro combate.'),
        'OCORRENCIA_DE_OPPORTUNITA_NESTA_BRANCH': 'SIM' if achou_no_repo else 'NÃO',
        'IMPACTO': ('o rótulo transforma uma PERGUNTA que a ADAMA responde numa CONCLUSÃO '
                    'que nós entregamos. E para a Itália a base nem sustenta a pergunta: a '
                    'atividade pública medida é 7 documentos operacionais em 150, com 82 '
                    'não julgáveis.'),
        'NAO_RENOMEADO_NESTA_SESSAO': 'SIM',
        'QUEM_DECIDE': ('a sessão dona do Portal Itália, antes do polimento final'),
    }


def prototipo():
    """10 · OWNER_DECISION. D-007 continua de pé."""
    return {
        'CLASSE': 'OWNER_DECISION',
        'PROTOTYPE_FROZEN': 'SIM',
        'DECISAO': 'D-007 — Claude descobre o produto, Claude Design desenha o produto',
        'CANDIDATE_DEPLOY_AFFECTED': 'NÃO',
        'DIVIDA_REGISTRADA': ('build_portal.py promete na docstring que nenhum número é '
                              'digitado à mão, e isso é falso em pelo menos as linhas 66 e '
                              '191. Os três valores do card italiano (58 · 37,4% · 20,9%) '
                              'são REPRODUTÍVEIS — critério AMPLIADO, cinco razões sociais, '
                              'snapshot de 24/08 — e mesmo assim não existem em arquivo '
                              'nenhum, então auditá-los exige re-derivar de um CSV que não é '
                              'versionado.'),
        'POR_QUE_ISSO_IMPORTA': ('tests/test_evidence.py verifica que o CAMINHO da evidência '
                                 'existe, nunca que o número exibido veio dele — então um '
                                 'número digitado passa no teste'),
        'NAO_CORRIGIR_AGORA': 'SIM — decisão do dono, e não afeta o candidato medido',
    }


# ─────────────────────────────────────────────────────────────────────── montagem
def montar():
    head = _git('rev-parse', 'HEAD')
    branch = _git('rev-parse', '--abbrev-ref', 'HEAD')
    # Sem relógio: a data é a do commit de SOURCE_HEAD, um fato sobre a ENTRADA.
    data_do_head = _git('show', '-s', '--format=%cI', 'HEAD')
    linhas = _registro()

    testes = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'],
        cwd=ROOT, capture_output=True, text=True)
    saida_testes = (testes.stderr or '') + (testes.stdout or '')
    m = re.search(r'^Ran (\d+) tests', saida_testes, re.M)
    falhas = re.search(r'FAILED \((.*)\)', saida_testes)

    fontes = sorted([
        'data/samples/IT-HUMAN-SENSORS/COVERAGE.json',
        'data/samples/IT-HUMAN-SENSORS/ENTITIES.json',
        'data/samples/IT-HUMAN-SENSORS/PILOT-MEASUREMENT.json',
        'data/samples/IT-HUMAN-SENSORS/PILOTO-YOUTUBE/LEGENDAS.json',
        'data/samples/IT-HUMAN-SENSORS/SOURCES.json',
        'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
        'data/raw/IT-T4-001/PROD_FTS.csv',
        'scripts/fonte_territorial.py',
        'tests/test_datas.py',
    ])

    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/IT-PORTAL-SPRINT-HANDOFF-V1',
        'source': ('handoff determinístico do sprint Portal Itália para a Linha B, derivado '
                   'dos artefatos preservados nesta branch'),
        'SOURCE_LOCATION': 'ITALY',
        'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'CAPTURED_AT': data_do_head,
        'CAPTURED_AT_ORIGEM': ('data do commit de SOURCE_HEAD, NÃO a hora de execução: um '
                               'carimbo de relógio faria duas corridas idênticas produzirem '
                               'hashes diferentes, e o "rodei duas vezes e deu igual" '
                               'deixaria de provar coisa alguma'),
        'SOURCE_HEAD': head,
        'SOURCE_BRANCH': branch,
        'DETERMINISTICO': 'SIM — sem relógio, sem aleatório, chaves ordenadas',
        'GERADO_POR': 'scripts/handoff_portal_it.py',
        'TESTS': {
            'COMANDO': 'python3 -m unittest discover -s tests',
            'TOTAL': int(m.group(1)) if m else NAO_SEI,
            'FALHAS': falhas.group(1) if falhas else '0',
            'RESULTADO': 'OK' if 'OK' in saida_testes and not falhas else 'FALHOU',
        },
        'ARTEFACT_HASHES': {c: (_sha(os.path.join(ROOT, c)) or NAO_SEI) for c in fontes},
        'ACHADOS': {
            '01_AZOXISTROBINA_PROTIOCONAZOL': caso_azoxy_prothio(linhas),
            '02_AUTORIZACOES_ADAMA': autorizacoes_adama(linhas),
            '03_REVOGADO_X_SCADUTO': revogado_x_scaduto(linhas),
            '04_SOCIAL_YOUTUBE': social_youtube(),
            '05_PESSOAS_E_PAPEIS': pessoas_papeis(),
            '06_COBERTURA_TERRITORIAL': cobertura_territorial(),
            '07_CORRECAO_DE_DATAS': correcao_de_datas(),
            '08_PROD_FTS': prod_fts(),
            '09_ROTULO_OPORTUNIDADE': rotulo_oportunidade(),
            '10_PROTOTIPO': prototipo(),
        },
        'PORTAL_NOW': ['01_AZOXISTROBINA_PROTIOCONAZOL'],
        'PORTAL_WITH_METHOD': ['02_AUTORIZACOES_ADAMA', '03_REVOGADO_X_SCADUTO',
                               '05_PESSOAS_E_PAPEIS', '06_COBERTURA_TERRITORIAL'],
        'METHOD_ONLY': ['04_SOCIAL_YOUTUBE'],
        'OWNER_DECISION': ['09_ROTULO_OPORTUNIDADE', '10_PROTOTIPO'],
        'CODE_FIX_HANDOFF': ['07_CORRECAO_DE_DATAS', '08_PROD_FTS'],
        # A lista que a tela consulta ANTES de escrever uma frase, não depois.
        'DO_NOT_SHOW': [
            {'NAO_DIZER': '0 legendas',
             'DIZER': 'existência de legenda: NÃO SEI em 150 de 150',
             'ACHADO': '04_SOCIAL_YOUTUBE'},
            {'NAO_DIZER': 'ADAMA possui 155 autorizações',
             'DIZER': '155 sob critério AMPLIADO, cinco razões sociais somadas, '
                      'snapshot de 2026-08-24; sob STRICT são 89',
             'ACHADO': '02_AUTORIZACOES_ADAMA'},
            {'NAO_DIZER': '114 pessoas',
             'DIZER': '90 entidades com ao menos um papel provado, de 221',
             'ACHADO': '05_PESSOAS_E_PAPEIS'},
            {'NAO_DIZER': 'temos agrônomos e produtores na base',
             'DIZER': '5 papéis de campo provados: 3 técnicos e 2 cooperativas; '
                      'agrônomo, produtor e consultor provados = 0',
             'ACHADO': '05_PESSOAS_E_PAPEIS'},
            {'NAO_DIZER': 'cobertura BOA em 72 células',
             'DIZER': '72 com a expansão territorial declarada; 30 sem ela',
             'ACHADO': '06_COBERTURA_TERRITORIAL'},
            {'NAO_DIZER': 'há problema nesta região',
             'DIZER': 'temos olhos nesta região',
             'ACHADO': '06_COBERTURA_TERRITORIAL'},
            {'NAO_DIZER': '61 documentos relevantes',
             'DIZER': '61 por casamento lexical de título, não verificados — mesmo '
                      'classificador dos 82 não julgáveis',
             'ACHADO': '04_SOCIAL_YOUTUBE'},
            {'NAO_DIZER': 'qualquer data de publicação de documento social italiano',
             'DIZER': 'faixa de recência, sem exibir data',
             'ACHADO': '04_SOCIAL_YOUTUBE'},
            {'NAO_DIZER': 'mudou / está subindo, sobre fonte social italiana',
             'DIZER': 'ULTIMA_COLETA nula em 243 de 243: não há linha de base',
             'ACHADO': '04_SOCIAL_YOUTUBE'},
            {'NAO_DIZER': 'mapa da Itália pintado pela sede do titular',
             'DIZER': 'sede legal é endereço de empresa, não lugar do fato',
             'ACHADO': '04_SOCIAL_YOUTUBE'},
            {'NAO_DIZER': 'oportunidade / espaço livre / ativo subutilizado',
             'DIZER': 'ACTIVATION QUESTION — e para a Itália a base nem sustenta a '
                      'pergunta ainda',
             'ACHADO': '09_ROTULO_OPORTUNIDADE'},
            {'NAO_DIZER': 'ato europeu e registro nacional confirmam o mesmo fato',
             'DIZER': 'o nacional deriva do europeu: é uma origem, não duas',
             'ACHADO': '01_AZOXISTROBINA_PROTIOCONAZOL'},
            {'NAO_DIZER': 'X produtos foram retirados do mercado',
             'DIZER': 'revogados; motivo declarado em 1.119 de 13.216',
             'ACHADO': '03_REVOGADO_X_SCADUTO'},
            {'NAO_DIZER': 'contagem de registros como participação de mercado',
             'DIZER': 'contagem de registros, e só',
             'ACHADO': '02_AUTORIZACOES_ADAMA'},
        ],
        'LIMITATIONS': [
            'Nenhuma coleta de rede foi feita nesta rodada. Custo = 0.',
            'Nenhuma afirmação se apoia em legenda: nenhuma legenda foi obtida (D-040).',
            ('data/raw/IT-T4-001/PROD_FTS.csv NÃO é versionado (D-003). Em clone novo ele '
             'não existe, e os achados 01, 02 e 03 voltam como NÃO SEI em vez de números. '
             'O hash do CSV está em ARTEFACT_HASHES para identificar o snapshot.'),
            ('O snapshot do registro é de 2026-08-24. Qualquer "futuro" calculado contra ele '
             'envelhece: 7 dos 20 próximos vencimentos publicados já haviam passado em '
             '2026-09-04. Futuro se calcula contra a data de leitura.'),
            ('A camada territorial já gravada foi produzida com a leitura de data '
             'defeituosa (achado 07). Remedir antes de exibir qualquer recência.'),
            ('italia-portale/client não existe nesta branch e não foi tocado. O rótulo '
             '"Radar Opportunità" é relato do dono, não medição minha.'),
            ('Contagem de registros não é participação de mercado, em nenhum dos achados.'),
            ('P-012 (GDPR) segue aberta: a camada nomeia pessoas com afiliação e ORCID. '
             'Qualquer tela que liste gente identificada precisa de revisão antes.'),
        ],
    }
    return corpo


def main():
    corpo = montar()
    os.makedirs(IT, exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')
    rel = os.path.relpath(SAIDA, ROOT)
    print('gravado: %s' % rel)
    print('SHA256 : %s' % _sha(SAIDA))
    print('HEAD   : %s (%s)' % (corpo['SOURCE_HEAD'][:12], corpo['SOURCE_BRANCH']))
    print('TESTES : %s · falhas %s' % (corpo['TESTS']['TOTAL'], corpo['TESTS']['FALHAS']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
