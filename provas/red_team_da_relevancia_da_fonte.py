#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DO PORTAO DE RELEVANCIA DE FONTE — 27 ataques, e todos tem de morrer.

    py provas/red_team_da_relevancia_da_fonte.py

    UM PORTAO QUE SO APROVA NAO E UM PORTAO.
    E UM PORTAO QUE NUNCA FOI ATACADO NAO SE SABE SE E PORTAO.

Cada ataque aqui e uma maneira concreta de fazer o sistema dizer «relevante»
sem que ninguem tenha provado nada — ou de fazer dizer «nao serve» a uma fonte
que so nao se conseguiu abrir. Nenhum deles e teorico: todos saem de um defeito
que esta casa ja cometeu, ou que o desenho convidava a cometer.

    ATAQUE_MORTO   o sistema recusou o ataque    -> bom
    ATAQUE_VIVO    o ataque conseguiu            -> o portao nao serve

Este ficheiro devolve 1 se sobreviver um so.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import relevancia_da_fonte as rel        # noqa: E402
import receitas                          # noqa: E402
import orquestrador as orq               # noqa: E402
import prova_barata                      # noqa: E402
import censo_de_relevancia_das_fontes as censo  # noqa: E402
from pedido import Pedido                # noqa: E402

ATAQUES = []
GRATIS = 'gratuito'
PAGO = 'pago quando passa pela rota Apify'


def ataque(codigo, nome):
    def deco(f):
        ATAQUES.append((codigo, nome, f))
        return f
    return deco


def _decisao(sid, prop, resultado, **kw):
    kw.setdefault('motivo', 'red team')
    kw.setdefault('metodo', 'RED_TEAM')
    if resultado in rel.RESULTADOS_QUE_AFIRMAM:
        kw.setdefault('evidencia', {'file': 'x', 'line': 1})
    return rel.Decisao(source_id=sid, proposito=prop, resultado=resultado,
                       **kw).para_livro()


# ══════════════════════════════════════════════════════════════════════════
# OS ATAQUES QUE FAZEM UMA OUTRA COISA PASSAR POR RELEVANCIA
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-01', 'marcar todas as GREEN como relevantes por convencao')
def rt01():
    c = censo.medir()
    verdes = [l for l in c['FONTES'] if l['VERDICT_DO_ATLAS'] == 'GREEN']
    promovidas = [l for l in verdes if l['VEREDITO_DO_PORTAO'] == rel.AUTORIZA]
    return (not promovidas and c['PORTADAS_DO_ATLAS'] == 0,
            '%d fontes GREEN no cadastro, %d promovidas pela cor'
            % (len(verdes), len(promovidas)))


@ataque('RT-02', 'usar HTTP 200 como relevancia')
def rt02():
    # Nao ha por onde: o estado so le o livro, e o livro so aceita as cinco
    # palavras. «200» nao e uma delas.
    try:
        rel.Decisao(source_id='IT-T3-002', proposito='T3', resultado='200',
                    motivo='respondeu', metodo='HTTP')
        return False, 'aceitou «200» como resultado'
    except rel.DecisaoInvalida:
        pass
    v = rel.portao('IT-T3-002', 'T3', [], custo=GRATIS)
    return (v['ESTADO_DA_RELEVANCIA'] == rel.NAO_AVALIADA,
            'responder nao move o portao')


@ataque('RT-03', 'usar ACCESSIBLE como relevancia')
def rt03():
    acessivel = {'source_id': 'IT-T3-002', 'access_method': 'HTTP direto'}
    bloqueada = {'source_id': 'IT-T9-008', 'access_method': 'NÃO SEI'}
    assert receitas._sabe_o_caminho(acessivel)
    assert not receitas._sabe_o_caminho(bloqueada)
    a = rel.portao('IT-T3-002', 'T3', [], custo=GRATIS)['ESTADO_DA_RELEVANCIA']
    b = rel.portao('IT-T9-008', 'T9', [], custo=GRATIS)['ESTADO_DA_RELEVANCIA']
    return (a == b == rel.NAO_AVALIADA,
            'acesso conhecido e acesso desconhecido dao o mesmo estado: %s / %s'
            % (a, b))


@ataque('RT-04', 'usar custo zero como relevancia')
def rt04():
    v = rel.portao('IT-T3-002', 'T3', [], custo=GRATIS)
    return v['VEREDITO'] != rel.AUTORIZA, 'gratis nao autoriza'


@ataque('RT-05', 'usar SOURCE_HEALTH como relevancia')
def rt05():
    import inspect
    p = set(inspect.signature(rel.estado).parameters)
    proibidos = {'health', 'saude', 'source_health', 'ficha', 'fonte'}
    return (not (p & proibidos) and p == {'source_id', 'proposito', 'livro'},
            'estado() le: %s' % sorted(p))


@ataque('RT-06', 'usar um unico post relevante para promover a fonte')
def rt06():
    # uma decisao de ITEM (lingua da admissao) posta no livro da fonte
    livro = [{'item': 'post-1', 'universo': 'T9', 'resultado': rel.SIM}]
    v = rel.portao('IT-T9-002', 'T9', livro, custo=PAGO)
    return (v['ESTADO_DA_RELEVANCIA'] == rel.NAO_AVALIADA
            and v['BLOQUEIA_A_CORRIDA'],
            'um item nao promove a fonte')


@ataque('RT-07', 'usar um post irrelevante para eliminar a fonte')
def rt07():
    livro = [{'item': 'post-1', 'universo': 'T3', 'resultado': rel.NAO}]
    v = rel.portao('IT-T3-002', 'T3', livro, custo=GRATIS)
    return v['VEREDITO'] != rel.BARRA, 'um item nao condena a fonte'


@ataque('RT-08', 'copiar a decisao de T3 para T9')
def rt08():
    livro = [_decisao('IT-T3-002', 'T3', rel.SIM)]
    v = rel.portao('IT-T3-002', 'T9', livro, custo=PAGO)
    return (v['ESTADO_DA_RELEVANCIA'] == rel.NAO_AVALIADA
            and v['BLOQUEIA_A_CORRIDA'],
            'T3 nao fala por T9')


# ══════════════════════════════════════════════════════════════════════════
# OS ATAQUES QUE TRANSFORMAM UMA CONFISSAO NUM VEREDITO
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-09', 'UNKNOWN vira NO')
def rt09():
    v = rel.portao('IT-T3-002', 'T3', [_decisao('IT-T3-002', 'T3', rel.NAO_SEI)],
                   custo=GRATIS)
    return v['VEREDITO'] == rel.EXIGE_AVALIACAO, v['VEREDITO']


@ataque('RT-10', 'timeout vira NO')
def rt10():
    d = _decisao('IT-T3-002', 'T3', rel.ERRO, motivo='timeout ao abrir o portal')
    v = rel.portao('IT-T3-002', 'T3', [d], custo=GRATIS)
    return v['VEREDITO'] != rel.BARRA, v['VEREDITO']


@ataque('RT-11', '403 vira NO')
def rt11():
    d = _decisao('IT-T3-002', 'T3', rel.ERRO, motivo='HTTP 403 no host')
    v = rel.portao('IT-T3-002', 'T3', [d], custo=GRATIS)
    return (v['VEREDITO'] != rel.BARRA and v['PODE_OBSERVAR_BARATO'],
            '403 continua a ser erro, nao rejeicao')


@ataque('RT-12', 'lista vazia vira NO sem baseline')
def rt12():
    o = prova_barata.observar('IT-T5-001', 'T5')
    return (o['DECISAO'] == 'NAO_TOMADA'
            and o['O_QUE_DEU'] not in rel.RESULTADOS,
            'acervo vazio produziu «%s»' % o['O_QUE_DEU'])


@ataque('RT-13', 'keyword miss vira NO')
def rt13():
    """A COL-LAW-036 em codigo: nao casar palavra nao prova nada.

    ⚠️ A PRIMEIRA VERSAO DESTE ATAQUE PROCURAVA A PALAVRA «keyword» NO
    FICHEIRO DA LEI — e sobreviveu, porque a lei escreve «NO KEYWORD MATCH !=
    NOT_RELEVANT» no proprio texto. O ataque estava a apanhar a defesa.

        PROCURAR UMA PALAVRA NUM FICHEIRO NAO E MEDIR O QUE ELE FAZ.

    Mede-se o comportamento: uma fonte cujo nome, temas e cultura nao tem uma
    unica palavra em comum com o proposito continua NAO_AVALIADA — e o portao
    nao recebe texto nenhum por onde a pudesse comparar.
    """
    import inspect
    # 1 · a lei nao tem maquinaria lexical: nao importa `re`.
    mod = sys.modules[rel.__name__]
    sem_regex = not hasattr(mod, 're')
    # 2 · o portao nao recebe texto nenhum. Sem texto nao ha como casar palavra.
    entradas = set(inspect.signature(rel.portao).parameters)
    sem_texto = not (entradas & {'texto', 'nome', 'topics', 'crops',
                                 'query', 'termos', 'ficha'})
    # 3 · comportamento: zero palavras em comum, e o estado nao e NAO.
    v = rel.portao('IT-T1-001', 'T3', [], custo=GRATIS)
    return (sem_regex and sem_texto
            and v['ESTADO_DA_RELEVANCIA'] == rel.NAO_AVALIADA
            and v['VEREDITO'] != rel.BARRA,
            'sem regex, sem texto a entrada, e a ausencia de palavra da '
            'NAO_AVALIADA em vez de NAO')


# ══════════════════════════════════════════════════════════════════════════
# OS ATAQUES CONTRA A IDENTIDADE DA FONTE
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-14', 'fabricar SOURCE_ID pela URL')
def rt14():
    mortos = 0
    urls = ('https://arpa.veneto.it', 'www.istat.it', 'x/y', '//a.it')
    for u in urls:
        try:
            rel.conferir_source_id(u)
        except rel.SourceIdInvalido:
            mortos += 1
    return mortos == len(urls), '%d de %d URLs recusadas' % (mortos, len(urls))


@ataque('RT-24', 'candidate virar registered sem evidencia')
def rt24():
    fonte = open(os.path.join(RAIZ, 'candidatas', 'fonte_nova.py'),
                 encoding='utf-8').read()
    fila_nao_preenche = '"SOURCE_ID": None' in fonte
    try:
        prova_barata.observar('CAND-0001', 'T3')
        sondou_candidata = True
    except prova_barata.ProvaRecusada:
        sondou_candidata = False
    return (fila_nao_preenche and not sondou_candidata,
            'a fila nao atribui SOURCE_ID e a prova recusa quem nao esta no cadastro')


# ══════════════════════════════════════════════════════════════════════════
# OS ATAQUES QUE CONTORNAM A PORTA
# ══════════════════════════════════════════════════════════════════════════
def _sem_livro(f):
    """Corre `f` com o livro vazio, sem tocar no ficheiro real."""
    antes = receitas.rel.ler_livro
    receitas.rel.ler_livro = lambda *a, **k: []
    try:
        return f()
    finally:
        receitas.rel.ler_livro = antes


@ataque('RT-15', 'permitir coleta paga com relevancia ausente')
def rt15():
    recibo = _sem_livro(lambda: orq.correr(Pedido(alvo='T9')))
    return (recibo['STATUS'] == 'BARRADO_NA_RELEVANCIA'
            and recibo['COST_USD'] == 0,
            'STATUS=%s' % recibo['STATUS'])


@ataque('RT-16', 'bypass por workflow (acionamento AGENDADO)')
def rt16():
    recibo = _sem_livro(
        lambda: orq.correr(Pedido(alvo='T2', acionamento='AGENDADO')))
    return recibo['STATUS'] == 'BARRADO_NA_RELEVANCIA', recibo['STATUS']


@ataque('RT-17', 'bypass por CLI (o binario, nao a funcao)')
def rt17():
    import subprocess
    r = subprocess.run([sys.executable, 'orquestrador/orquestrador.py',
                        'colete concorrentes'], cwd=RAIZ,
                       capture_output=True, text=True, timeout=300)
    return (r.returncode == 3 and 'BARRADO NO PORTAO' in r.stdout,
            'exit=%s' % r.returncode)


@ataque('RT-18', 'bypass direto ao executor pelo plano')
def rt18():
    """O plano continua a dizer QUEM correria — e a dizer que esta barrado.

    O ataque real e outro: chamar `coleta/comunicacao_coleta.py` a mao. Esse
    caminho existe e NAO passa por portao nenhum — e esta declarado como
    buraco no relatorio em vez de ser escondido aqui. O que este ataque mede e
    que o caminho CANONICO nao se contorna lendo `plano.executores`.
    """
    plano = _sem_livro(lambda: receitas.resolver(Pedido(alvo='T9')))
    return (bool(plano.executores) and plano.bloqueia_a_corrida,
            'o plano nomeia o executor e marca-o barrado')


@ataque('RT-19', 'mudar o gate depois de ver o resultado')
def rt19():
    v = rel.portao('IT-T3-002', 'T3', [], custo=GRATIS)
    d = _decisao('IT-T3-002', 'T3', rel.SIM)
    return (v['VERSAO_DO_PORTAO'] == rel.VERSAO_DO_PORTAO
            and d['VERSAO'] == rel.VERSAO_DA_AVALIACAO
            and rel.VERSAO_DO_PORTAO and rel.VERSAO_DA_AVALIACAO,
            'portao v%s · decisao v%s, e as duas sao carimbadas'
            % (rel.VERSAO_DO_PORTAO, rel.VERSAO_DA_AVALIACAO))


@ataque('RT-20', 'apagar a decisao negativa antiga')
def rt20():
    portas = [n for n in dir(rel)
              if any(p in n.lower() for p in ('apagar', 'remover', 'delete',
                                              'limpar', 'truncar'))]
    with tempfile.TemporaryDirectory() as d:
        rel.registar([_decisao('IT-T3-002', 'T3', rel.NAO)], raiz=d)
        rel.registar([_decisao('IT-T3-002', 'T3', rel.SIM)], raiz=d)
        livro = rel.ler_livro(d)
    return (not portas and len(livro) == 2 and livro[0]['RESULTADO'] == rel.NAO,
            'sem porta de apagar; o NAO de ontem continua no livro')


# ══════════════════════════════════════════════════════════════════════════
# OS ATAQUES CONTRA A SEPARACAO DOS EIXOS
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-21', 'score medio compensando falha grave')
def rt21():
    v = rel.portao('IT-T3-002', 'T3', [], custo=GRATIS)
    numericos = [k for k, x in v.items()
                 if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return (numericos == ['HISTORICO'] and 'SOURCE_SCORE' in rel.NAO_CRIAR,
            'numeros no veredito: %s' % numericos)


@ataque('RT-22', 'misturar reliability e relevance')
def rt22():
    fonte = open(os.path.join(RAIZ, 'leis', 'relevancia_da_fonte.py'),
                 encoding='utf-8').read()
    declara = 'SOURCE_RELEVANCE  != SOURCE_RELIABILITY' in fonte
    import inspect
    p = set(inspect.signature(rel.estado).parameters)
    return declara and 'reliability' not in p, 'a lei nomeia e nao le reliability'


@ataque('RT-23', 'misturar relevance e collection priority')
def rt23():
    import politica_da_coleta as pol
    v = rel.portao('IT-T3-002', 'T3', [_decisao('IT-T3-002', 'T3', rel.SIM)],
                   custo=GRATIS)
    sem_tier = 'PRIORITY_TIER' not in v and 'ACAO' not in v
    # e a politica nao sabe nada de relevancia
    d = pol.decidir(source_id='IT-T3-002', satisfaction=pol.NAO_TENHO)
    sem_relevancia = 'RELEVANCIA' not in d and 'RESULTADO' not in d
    return sem_tier and sem_relevancia, 'o veredito nao traz tier; a politica nao traz relevancia'


@ataque('RT-25', 'erro tecnico promover ou degradar a relevancia')
def rt25():
    antes = rel.portao('IT-T3-002', 'T3', [], custo=GRATIS)['ESTADO_DA_RELEVANCIA']
    try:
        prova_barata.sondar('IT-T3-002', 'T3', custo_da_rota=GRATIS)
        rebentou = False
    except prova_barata.ProvaRecusada:
        rebentou = True
    depois = rel.portao('IT-T3-002', 'T3', [], custo=GRATIS)['ESTADO_DA_RELEVANCIA']
    return (rebentou and antes == depois == rel.NAO_AVALIADA,
            'a sonda falhou e o estado nao se mexeu')


# ══════════════════════════════════════════════════════════════════════════
# DOIS ATAQUES QUE A MISSAO NAO PEDIU, E QUE O DESENHO CONVIDAVA
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-26', 'custo «NAO SEI» passar por gratuito')
def rt26():
    v = rel.portao('IT-T9-002', 'T9', [], custo='NAO SEI')
    return (rel.GASTO_DINHEIRO in v['FORMAS_DE_GASTO_ABERTAS']
            and v['BLOQUEIA_A_CORRIDA'],
            'custo desconhecido conta como gasto')


@ataque('RT-27', 'um SIM numa fonte abrir a porta as outras sete do territorio')
def rt27():
    livro = [_decisao('IT-T9-002', 'T9', rel.SIM)]
    antes = receitas.rel.ler_livro
    receitas.rel.ler_livro = lambda *a, **k: livro
    try:
        plano = receitas.resolver(Pedido(alvo='T9'))
    finally:
        receitas.rel.ler_livro = antes
    return (plano.relevancia['SOURCE_ID'] is None
            and plano.bloqueia_a_corrida,
            'o plano nao nomeia fonte, logo o SIM de uma nao autoriza o lote')


def main() -> int:
    print('RED TEAM · PORTAO DE RELEVANCIA DE FONTE')
    print('=' * 74)
    vivos, mortos, linhas = [], [], []
    for codigo, nome, f in ATAQUES:
        try:
            morreu, nota = f()
        except Exception as e:                                  # noqa: BLE001
            # ⚠️ UM ATAQUE QUE REBENTA NAO E UM ATAQUE QUE MORREU.
            # Contar excepcao como defesa seria a mesma confusao que esta
            # missao existe para matar: ERRO nao e REJEICAO.
            morreu, nota = False, 'o ataque rebentou: %s: %s' % (type(e).__name__, e)
        (mortos if morreu else vivos).append(codigo)
        linhas.append({'CODIGO': codigo, 'ATAQUE': nome,
                       'ESTADO': 'ATAQUE_MORTO' if morreu else 'ATAQUE_VIVO',
                       'NOTA': nota})
        print('  %-7s %-8s %-56s' % (codigo,
                                     'MORTO' if morreu else 'VIVO  <<<',
                                     nome[:56]))
        print('          %s' % nota)
    print('=' * 74)
    print('ATAQUES=%d · MORTOS=%d · VIVOS=%d' % (len(ATAQUES), len(mortos), len(vivos)))
    if vivos:
        print('SOBREVIVERAM: %s' % ', '.join(vivos))
        return 1
    print('TODOS OS ATAQUES MORRERAM.')
    if '--escrever' in sys.argv:
        saida = os.path.join(RAIZ, 'data', 'derivados',
                             'RED-TEAM-RELEVANCIA-DE-FONTE-V1.json')
        os.makedirs(os.path.dirname(saida), exist_ok=True)
        with open(saida, 'w', encoding='utf-8') as f:
            f.write(json.dumps(
                {'SCHEMA': 'sintonia.red-team-relevancia-de-fonte/1',
                 'CONTRATO': rel.CONTRATO,
                 'VERSAO_DO_PORTAO': rel.VERSAO_DO_PORTAO,
                 'TOTAL': len(ATAQUES), 'MORTOS': len(mortos),
                 'VIVOS': len(vivos), 'ATAQUES': linhas},
                ensure_ascii=False, indent=2) + '\n')
        print('escrito: data/derivados/RED-TEAM-RELEVANCIA-DE-FONTE-V1.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
