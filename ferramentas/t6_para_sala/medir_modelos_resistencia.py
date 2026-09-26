#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MODELO/DSS, CONDICAO->RISCO e RESISTENCIA nos trabalhos guardados — SO MEDIR (sem rede,
sem campo novo no contrato). Pedido da coordenacao 12:00 (ALINHAMENTO DO DONO, secoes 5 e 9).

    py ferramentas/t6_para_sala/medir_modelos_resistencia.py --rodadas=<pasta> --para=<json>

Le o titulo + resumo que a FONTE publicou (o registo do OpenAlex). Cada classe exige o termo
ESCRITO, por palavra inteira, e o termo fica gravado. Nada disto e o facto de risco: e o texto
dizer que o trabalho trata disso (secao 9: «reconheceu condicoes que a literatura associa ao
risco» != «a doenca aconteceu»).

    DSS_OU_MODELO_DE_RISCO   o trabalho nomeia um modelo/DSS/previsao do organismo
    MODELO_GENERICO          so «model/modelling» solto (pode ser modelo molecular): a parte
    CONDICAO_RISCO           uma VARIAVEL (temperatura, humidade, molhamento, chuva, graus-dia,
                             fase fenologica) E uma RESPOSTA do organismo (infeccao, risco,
                             incidencia, voo, geracao...) E uma RELACAO (favorece, limiar,
                             depende, associado...) no mesmo texto
    RESISTENCIA_A_PRODUTO    resistencia/sensibilidade a fungicida/insecticida/molecula/FRAC
    RESISTENCIA_DA_PLANTA    resistencia da cultivar/genotipo (outra pergunta: nao se soma)
"""
import json
import re
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import pesquisadores_t6 as T6  # noqa: E402

DSS = ('decision support system', 'decision support systems', 'dss', 'forecasting model', 'forecasting models',
       'forecast model', 'warning system', 'early warning', 'risk model', 'risk models', 'epidemiological model',
       'infection model', 'mechanistic model', 'phenological model', 'phenology model', 'simulation model',
       'predictive model', 'prediction model', 'population dynamics model', 'degree-day model', 'vite.net',
       'weather-driven model', 'process-based model', 'disease model')
MODELO = ('model', 'models', 'modelling', 'modeling', 'forecast', 'forecasting', 'prediction', 'predict',
          'predicted', 'simulation')
VARIAVEL = ('temperature', 'temperatures', 'humidity', 'relative humidity', 'leaf wetness', 'wetness',
            'wetness duration', 'rainfall', 'rain', 'precipitation', 'degree-days', 'degree days', 'degree-day',
            'gdd', 'growing degree', 'phenological stage', 'phenology', 'bbch', 'photoperiod', 'vapour pressure',
            'microclimate', 'weather')
RESPOSTA = ('infection', 'infections', 'risk', 'incidence', 'severity', 'outbreak', 'outbreaks', 'epidemic',
            'epidemics', 'sporulation', 'germination', 'flight', 'flights', 'generation', 'generations',
            'emergence', 'oviposition', 'population growth', 'development rate', 'larval development',
            'disease development', 'primary infection', 'secondary infection')
RELACAO = ('favour', 'favours', 'favoured', 'favor', 'favors', 'favored', 'favourable', 'favorable', 'threshold',
           'thresholds', 'optimal', 'optimum', 'depend', 'depends', 'dependent', 'associated', 'correlated',
           'correlation', 'affected', 'influenced', 'driven', 'required', 'requires', 'conducive', 'triggered')
PRODUTO = ('fungicide', 'fungicides', 'insecticide', 'insecticides', 'acaricide', 'herbicide', 'active ingredient',
           'active substance', 'frac', 'irac', 'qoi', 'sdhi', 'dmi', 'caa', 'strobilurin', 'strobilurins')
RESIST = ('resistance', 'resistant', 'reduced sensitivity', 'sensitivity', 'insensitive', 'insensitivity',
          'cross-resistance', 'tolerance')
PLANTA = ('resistant cultivar', 'resistant cultivars', 'resistant varieties', 'resistant variety',
          'resistant genotypes', 'resistant genotype', 'host resistance', 'resistance genes', 'resistance gene',
          'resistance loci', 'resistance locus', 'rpv', 'ren3', 'piwi', 'disease-resistant', 'resistant grapevine')


def _achou(termos, t):
    return [x for x in termos if T6.CP._tem(x, t)]


def classes(u, resumo):
    t = T6.CP._texto(u['TITULO'] + ' . ' + resumo)
    dss, var, resp, rel = _achou(DSS, t), _achou(VARIAVEL, t), _achou(RESPOSTA, t), _achou(RELACAO, t)
    res = _achou(RESIST, t)
    prod = _achou(PRODUTO, t) + [m['VALOR'] for m in (u['MOLECULA'] if u['MOLECULA'] != T6.NAO_SEI else [])]
    planta = _achou(PLANTA, t)
    out = {}
    if dss:
        out['DSS_OU_MODELO_DE_RISCO'] = dss[:3]
    elif _achou(MODELO, t):
        out['MODELO_GENERICO'] = _achou(MODELO, t)[:3]
    # v2 (lidos a mao 10+10): variavel, resposta e relacao NA MESMA FRASE — frases de
    # contexto («weather favourable to infections» no fundo de um artigo de peptidos) caiam aqui
    for frase in re.split(r'(?<=[.;:!?])\s+', t):
        v, r_, l_ = _achou(var, frase), _achou(resp, frase), _achou(rel, frase)
        if v and r_ and l_:
            out['CONDICAO_RISCO'] = {'VARIAVEL': v[:3], 'RESPOSTA': r_[:3], 'RELACAO': l_[:3],
                                     'FRASE': frase[:160]}
            break
    # v2: «resistencia A um produto», nao «resistencia» + «fungicida» soltos no mesmo texto
    # (1 em 10 certos na v1: o resto era resistencia da planta ou resistencia induzida)
    if res and prod:
        alvo = '|'.join(re.escape(p) for p in sorted(set(prod), key=len, reverse=True))
        rx = re.compile(r'(?:(?:%s)[\w-]*\s+(?:resistan\w+|insensitiv\w+|sensitivity))'
                        r'|(?:(?:resistan\w+|insensitiv\w+|sensitivity)\s+(?:to|towards|against)\s+'
                        r'(?:[\w-]+\s+){0,3}?(?:%s))' % (alvo, alvo))
        m = rx.search(t)
        if m and not re.search(r'(induced|systemic acquired|plant|host)\s+resistance', m.group(0)):
            out['RESISTENCIA_A_PRODUTO'] = {'TRECHO': m.group(0)[:100]}
    if planta:
        out['RESISTENCIA_DA_PLANTA'] = planta[:3]
    return out


def main(argv):
    opt = dict(a[2:].split('=', 1) for a in argv if a.startswith('--') and '=' in a)
    us, _, _ = T6.ler_pasta(opt['rodadas'])
    resumos = {}
    for f in sorted(os.listdir(opt['rodadas'])):
        if f.startswith('openalex-') and f.endswith('.json'):
            d = T6._ler(os.path.join(opt['rodadas'], f))
            if T6.resposta_valida(d)[0]:
                for w in d['results']:
                    resumos[T6._doi(w.get('doi')) or w.get('id')] = T6.CP._resumo_do_indice(w.get('abstract_inverted_index'))
    por, linhas = {}, []
    for u in us:
        k = u['DOI'] if u['DOI'] != T6.NAO_SEI else u['OPENALEX_WORK_ID']
        c = classes(u, resumos.get(k, ''))
        for n in c:
            por[n] = por.get(n, 0) + 1
        if c:
            linhas.append({'DOI': k, 'TITULO': u['TITULO'][:140], 'PARES': u['NA_CONSULTA_E_NO_TEXTO'], 'CLASSES': c})
    sem_resumo = sum(1 for u in us if not u.get('TEM_RESUMO_NO_INDICE'))
    r = {'TRABALHOS': len(us), 'SEM_RESUMO_NO_INDICE': sem_resumo, 'POR_CLASSE': dict(sorted(por.items())),
         'DSS_OU_CONDICAO_RISCO': sum(1 for l in linhas if 'DSS_OU_MODELO_DE_RISCO' in l['CLASSES']
                                      or 'CONDICAO_RISCO' in l['CLASSES']),
         'AMOSTRA_LER_A_MAO': {n: [l for l in linhas if n in l['CLASSES']][:10] for n in
                               ('DSS_OU_MODELO_DE_RISCO', 'CONDICAO_RISCO', 'RESISTENCIA_A_PRODUTO')},
         'TODOS': linhas}
    with open(opt['para'], 'w', encoding='utf-8', newline='\n') as h:
        json.dump(r, h, ensure_ascii=False, indent=1)
    print(json.dumps({k: r[k] for k in ('TRABALHOS', 'SEM_RESUMO_NO_INDICE', 'POR_CLASSE', 'DSS_OU_CONDICAO_RISCO')},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
