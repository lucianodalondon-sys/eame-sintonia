#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R3 · O CONTRATO DO PACOTE: o cabeçalho só diz o que o corpo sustenta.

    python3 scripts/v21_contrato_do_pacote.py

DOIS DEFEITOS, UMA CAUSA
------------------------
1. `SOURCES.json` declarava `BY_QA` e `BY_ORIGIN` somando **177** com **185**
   registros no corpo, e a classe `DERIVED_V2_1` nem aparecia na quebra.
2. O `ACCEPTANCE-REPORT` dizia `CONTAGEM_DECLARADA_DIVERGE: []` — verdade, porque
   ele só conferia `COUNT_TOTAL` e `COUNT_CLIENT_SAFE`. Nunca olhou `BY_QA`.

A causa é a mesma: as quebras são contadas no *ingest*, e os passos seguintes
acrescentam registros sem recontar. Oito fontes entraram depois e ninguém somou.

    O RELATÓRIO QUE SÓ MEDE O QUE SABE MEDIR NÃO ESTÁ ERRADO.
    ESTÁ INCOMPLETO — E PARECE COMPLETO.

Aqui toda quebra declarada é RECONTADA do corpo, em todos os arquivos, no fim da
cadeia. E a evidência de rota que existe medida é ligada às fontes que ela mede —
sem inventar evidência para as que não foram medidas.
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
ROTAS = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')

# quebra declarada no cabeçalho -> campo do registro que a alimenta
QUEBRAS = {'BY_QA': 'QA_STATUS', 'BY_ORIGIN': 'ORIGIN_LAYER'}

# Uma rodada nao responde «por onde a requisicao saiu». Um coletor ja concluiu
# «o ISMEA nunca foi bloqueado» porque recebeu HTTP 200 — com a VPN ligada, sem
# saber. Por isso a nota diz o que a medicao alcanca, e nao mais que isso.
NOTA_ROTA = {
    'DUAS': 'rota medida nas duas rodadas: direta e com VPN italiana.',
    'SO_DIRETA': ('rota medida em UMA rodada apenas, a direta. Isto diz o que '
                  'aconteceu, nao por onde a requisicao saiu.'),
    'SO_VPN': ('rota medida em UMA rodada apenas, com VPN italiana. Isto diz o '
               'que aconteceu, nao por onde a requisicao saiu.'),
    'NAO_ABRIU': ('a rota nao abriu nesta medicao. O erro cru da ferramenta esta '
                  'em ROUTE_PROBE_RAW. Ferramenta que recusa nao prova porta '
                  'fechada.'),
}


def host(u):
    m = re.match(r'https?://([^/]+)', str(u or ''))
    return m.group(1).lower().replace('www.', '') if m else None


def rotas_medidas():
    """A rota que foi REALMENTE medida, por host. Nada é inferido."""
    out = {}
    for arq, com_vpn in (('IT-ROTA-SEM_VPN.json', False),
                         ('IT-ROTA-COM_VPN_IT.json', True)):
        p = os.path.join(ROTAS, arq)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for x in (d.get('ITENS') or []):
            h = host(x.get('URL'))
            if h:
                out.setdefault(h, {})['VPN' if com_vpn else 'DIRETO'] = x
    return out


README = os.path.join(ROOT, 'docs', 'design', 'ITALY-V2.1-README-FIRST.md')


def conferir_readme():
    """Cada numero afirmado no README e recontado do pacote."""
    if not os.path.exists(README):
        return ['README-FIRST nao encontrado em docs/design/']
    txt = open(README, encoding='utf-8').read()
    S = json.load(open(os.path.join(ING, 'SOURCES.json'), encoding='utf-8'))['RECORDS']
    cs = [r for r in S if r.get('CLIENT_SAFE')]
    ambos = sum(1 for r in S if r.get('ACCESS_EVIDENCE')
                and r.get('REQUIRES_ITALIAN_ROUTE') is not None)
    com_estado = sum(1 for r in S if r.get('ACCESS_STATE') or r.get('ACCESS_STATUS'))
    afirmacoes = [
        ('**%d das %d fontes**' % (ambos, len(S)),
         'a cobertura do teste de rota'),
        ('As **%d**' % com_estado, 'as fontes com ACCESS_STATE ou ACCESS_STATUS'),
        ('**%d fontes client-safe**' % len(cs), 'o numero de fontes client-safe'),
    ]
    falhas = [f'{o} — o README nao diz "{t}"' for t, o in afirmacoes if t not in txt]
    # a promessa que nao pode voltar
    if 'teste de rota de cada fonte' in txt:
        falhas.append('o README voltou a prometer teste de rota "de cada fonte"')
    return falhas


def main():
    # A ROTA E CONTEUDO: entra ANTES da traducao, senao ACCESS_EVIDENCE vai a
    # tela em portugues. A CONTAGEM E ARITMETICA: entra DEPOIS do fechamento,
    # senao reconta um corpo que ainda vai mudar.
    #
    #     CADA PASSO NO LUGAR ONDE O QUE ELE MEXE JA PAROU DE MUDAR.
    modo = sys.argv[1] if len(sys.argv) > 1 else '--tudo'
    so_rota = modo == '--rota'
    so_contagem = modo == '--contagens'
    rot = rotas_medidas()
    ligadas = 0
    v = {'QUEBRA_QUE_NAO_SOMA_O_CORPO': [], 'CONTAGEM_DECLARADA_DIVERGE': []}

    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq == 'APP-MANIFEST.json':
            continue
        p = os.path.join(ING, arq)
        d = json.load(open(p, encoding='utf-8'))
        if not (isinstance(d, dict) and isinstance(d.get('RECORDS'), list)):
            continue
        recs = d['RECORDS']

        # ── 1 · a evidência de rota que existe, ligada a quem ela mede ───────
        if arq == 'SOURCES.json' and not so_contagem:
            for r in recs:
                h = host(r.get('URL') or (r.get('SOURCE_URLS') or [None])[0])
                m = rot.get(h)
                if not m:
                    continue
                direto, vpn = m.get('DIRETO'), m.get('VPN')
                base = direto or vpn
                # ⚠️ NUNCA SOBRESCREVER EVIDENCIA QUE JA EXISTE.
                # A sonda generica desta rodada mede menos do que a leitura feita
                # a mao: para o ISMEA ela devolveu falha de conexao onde a medicao
                # anterior lera 121.797 bytes de tabela de precos. Trocar uma pela
                # outra faria o pacote afirmar que a fonte esta fechada.
                #
                #     FERRAMENTA QUE RECUSA != PORTA FECHADA.
                #
                # Entao a sonda so PREENCHE o que estava vazio; onde ja havia
                # evidencia, ela entra ao lado como segunda observacao.
                # O FATO TECNICO NAO TEM LINGUA; A LEITURA TEM.
                # Escrever "sem VPN" dentro de ACCESS_EVIDENCE punha prosa
                # portuguesa num campo que vai a tela e obrigava a traduzir
                # dezenas de strings variaveis. O estado e o tamanho sao numero;
                # a mensagem de erro do sistema e CITACAO da ferramenta, e
                # citacao nao se traduz — por isso vai depois de "literal:".
                estado = str(base.get('ESTADO') or '')
                detalhe = str(base.get('DETALHE') or '')
                if estado.upper().startswith(('HTTP', 'OK')):
                    # HTTP 200 · 4000 bytes · 0.7s — numero nao tem lingua.
                    sonda = '%s · %s · %.1fs' % (estado, detalhe,
                                                 base.get('SEGUNDOS') or 0)
                else:
                    # ⚠️ A MENSAGEM CRUA DO SISTEMA NAO VAI A TELA.
                    # As 24 medicoes de falha vieram de uma maquina Windows em
                    # portugues: «Uma tentativa de conexao falhou porque o
                    # componente conectado nao respondeu». Isso e infraestrutura
                    # de coleta (§18), nao evidencia para o cliente — e um cliente
                    # italiano nao tem por que ler o erro do Windows de quem
                    # coletou. O texto cru fica num campo tecnico; o campo de tela
                    # recebe a frase fixa, que se traduz uma vez.
                    #
                    #     O ERRO DA FERRAMENTA E NOSSO, NAO DO LEITOR.
                    sonda = NOTA_ROTA['NAO_ABRIU']
                    r['ROUTE_PROBE_RAW'] = '%s · %s · %.1fs' % (
                        estado, detalhe, base.get('SEGUNDOS') or 0)
                if not r.get('ACCESS_EVIDENCE'):
                    r['ACCESS_EVIDENCE'] = sonda
                    r['ACCESS_EVIDENCE_MEASURED'] = True
                else:
                    r['ROUTE_PROBE_SECOND_READING'] = sonda
                # «por onde a requisição saiu» só se responde comparando as duas
                # rodadas. Uma só rodada não responde, e dizer que responde seria
                # o erro do coletor que concluiu «nunca foi bloqueado» ao receber
                # 200 com a VPN ligada sem saber.
                # Frases FIXAS, e por isso traduziveis uma vez. Texto de rota
                # gerado com variavel dentro vira frase nova a cada build, e
                # frase nova a cada build nunca fica traduzida.
                if direto and vpn:
                    r['REQUIRES_ITALIAN_ROUTE'] = (
                        direto.get('CAUSA') != 'ABERTO' and vpn.get('CAUSA') == 'ABERTO')
                    r['ROUTE_EVIDENCE_NOTE'] = NOTA_ROTA['DUAS']
                elif direto:
                    r['ROUTE_EVIDENCE_NOTE'] = NOTA_ROTA['SO_DIRETA']
                else:
                    r['ROUTE_EVIDENCE_NOTE'] = NOTA_ROTA['SO_VPN']
                ligadas += 1

        # ── 2 · toda quebra declarada é recontada do corpo ───────────────────
        mudou = False
        if so_rota:
            if ligadas and arq == 'SOURCES.json':
                json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            continue
        for campo, chave in QUEBRAS.items():
            if campo not in d:
                continue
            real = dict(Counter(r.get(chave) for r in recs))
            if d[campo] != real:
                v['QUEBRA_QUE_NAO_SOMA_O_CORPO'].append(
                    '%s · %s: declarado soma %d, corpo soma %d'
                    % (arq, campo, sum(d[campo].values()), len(recs)))
                d[campo] = real
                mudou = True
        for campo, esperado in (('COUNT_TOTAL', len(recs)),
                                ('COUNT_CLIENT_SAFE',
                                 sum(1 for r in recs if r.get('CLIENT_SAFE') is True))):
            if campo in d and d[campo] != esperado:
                v['CONTAGEM_DECLARADA_DIVERGE'].append(
                    '%s · %s: %s != %s' % (arq, campo, d[campo], esperado))
                d[campo] = esperado
                mudou = True
        if mudou or (arq == 'SOURCES.json' and ligadas):
            json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ── 3 · o README so pode afirmar numero que o pacote sustenta ───────────
    # O README dizia "sete das dez culturas nao tem mercado" muito depois de a
    # last-mile ter fechado a lacuna, e prometia teste de rota "de cada fonte"
    # tendo-o em 128 de 185. Numero escrito a mao envelhece em silencio.
    #
    #     NUMERO QUE NAO SE RECALCULA E NUMERO QUE VAI MENTIR ALGUM DIA.
    #     A UNICA DUVIDA E QUANDO.
    if not so_rota:
        v['README_AFIRMA_O_QUE_O_PACOTE_NAO_SUSTENTA'] = conferir_readme()

    print('== R3 · CONTRATO DO PACOTE ==')
    print('  rota medida ligada a fontes : %d' % ligadas)
    for k, val in v.items():
        print('  %-32s: %d' % (k, len(val)))
        for ex in val[:6]:
            print('      %s' % ex)
    print('  (as quebras acima foram RECONTADAS do corpo e regravadas)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
