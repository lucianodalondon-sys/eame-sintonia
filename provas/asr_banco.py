#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O BANCO DE PROVA DO RECONHECEDOR — a mesma pergunta, ferro a ferro.

    py provas/asr_banco.py                       # o padrao do dono, como esta
    py provas/asr_banco.py --device GPU          # a placa, se houver
    py provas/asr_banco.py --modelos small,medium --device AUTO
    py provas/asr_banco.py --json                # para artefato

O QUE ISTO RESPONDE, E O QUE NAO
----------------------------------
Responde: **qual configuracao DESTA maquina entrega o melhor equilibrio para o
SINTONIA?** Nao responde «qual e o melhor reconhecedor do planeta» — essa
pergunta nao tem fim, e nao e a desta casa.

    MAIS RAPIDO NAO E MELHOR. MAIOR NAO E MELHOR.
    O QUE CONTA E O NOME DA CULTURA, DA MARCA E DA DOENCA.

O CORPUS E O QUE JA ESTA PRESERVADO. NADA NOVO E BAIXADO
----------------------------------------------------------
Oito Reels ja capturados vivem em `data/raw/REEL-MIDIA/`, com o `.wav` ao lado.
Descarregar midia nova para montar banco de prova seria adquirir conteudo por
uma rota que esta missao nao autorizou — e a pergunta «esta maquina transcreve?»
nao precisa de um byte novo para ser respondida.

    CAN TRANSCRIBE != CAN ACQUIRE MEDIA. Sao duas missoes.

A VERDADE DE REFERENCIA NAO E MINHA
-------------------------------------
Os termos esperados saem de `QUALIDADE-DA-FALA-V1.json`, que os declara UM A UM
com a origem de cada um — legenda do proprio post, ou identidade da conta.
Inventar aqui uma segunda lista faria duas verdades sobre a mesma pergunta, e a
partir daí nenhuma valeria.

ESTE FICHEIRO NAO CARREGA MODELO NENHUM
-----------------------------------------
Ele chama `ferramentas/fala_local.py`, que e o dono unico do reconhecedor desta
casa. Um banco de prova que instanciasse `WhisperModel` seria um segundo dono —
e medir com um motor que nao e o de producao mede a coisa errada.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
import fala_local as fl                                        # noqa: E402

MIDIA = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA')
VERDADE = os.path.join(RAIZ, 'data', 'samples', 'REEL-TRANSCRICOES',
                       'QUALIDADE-DA-FALA-V1.json')
NAO_MEDIDO = 'NOT_MEASURED'
NAO_SE_APLICA = 'NOT_APPLICABLE'

#: As linguas que a missao quer cobrir. A que nao tiver amostra PROVADA sai
#: `NOT_MEASURED` — inventar audio ou verdade de referencia para encher a tabela
#: seria produzir a evidencia que se quer medir.
LINGUAS_ALVO = ('it', 'es', 'fr', 'en', 'pt')


def _sem_acento(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t)
                   if unicodedata.category(c) != 'Mn')


def _tem_termo(texto, termo):
    """O termo aparece no texto? Comparacao tolerante a acento e caixa.

    NAO e tolerante a palavra partida ao meio: `small` escreveu «mai scoltori»
    onde se disse «maiscoltori», e um `in` cru diria que acertou — porque
    «maiscoltori» contem «mais»... e «mai scoltori» tambem contem «mai».

        UMA COMPARACAO FROUXA TRANSFORMA UM ERRO MEDIDO NUM ACERTO PUBLICADO.

    A fronteira de palavra e o que separa as duas.
    """
    if not texto or not termo:
        return False
    a, b = _sem_acento(texto).lower(), _sem_acento(termo).lower()
    return re.search(r'(?<!\w)%s(?!\w)' % re.escape(b), a) is not None


def verdade():
    """→ {reel: {'IDIOMA':…, 'TERMOS':[{TERMO, ORIGEM, TIPO}]}}. Do dono, nao daqui."""
    with open(VERDADE, encoding='utf-8') as f:
        d = json.load(f)
    fora = {}
    for linha in d.get('LINHAS') or []:
        termos = linha.get('TERMOS') or []
        if not termos:
            continue
        fora[linha['REEL']] = {
            'IDIOMA': linha.get('IDIOMA'),
            'CONTA': linha.get('CONTA'),
            # MARCA e o termo cuja origem é a IDENTIDADE DA CONTA; os outros sao
            # vocabulario do conteudo. A distincao nao e minha: a origem de cada
            # termo ja vinha declarada no artefato.
            'TERMOS': [{'TERMO': t['TERMO'],
                        'TIPO': 'BRAND' if str(t.get('ORIGEM', '')).startswith('ACCOUNT')
                                else 'TERM'}
                       for t in termos],
        }
    return fora


def _sem_o_dono(caminho):
    """O caminho sem o nome de quem usa a maquina — a mesma lei da C4.

    Um banco de prova pode dizer QUE pasta leu; nunca DE QUEM ela e. E este
    relatorio vai para documento versionado, onde um `C:\\Users\\<nome>` ficaria
    para sempre.
    """
    t = str(caminho or '')
    perfil = os.environ.get('USERPROFILE') or os.path.expanduser('~')
    if perfil and perfil in t:
        t = t.replace(perfil, '<perfil>')
    return re.sub(r'(?i)([A-Z]:\\Users\\)[^\\/]+', r'\1<perfil>', t)


def amostras(midia=None):
    """Os `.wav` ja preservados. → lista. NADA NOVO E BAIXADO, em caminho nenhum.

    DUAS PROCEDENCIAS, E ELAS NAO VALEM O MESMO
    ---------------------------------------------
    A primeira e o corpus canonico: `.wav` com **verdade de referencia
    declarada** em `QUALIDADE-DA-FALA-V1.json`. So com ele se pode falar de
    acerto de termo, de marca e de lingua.

    A segunda existe porque a maquina que tem a PLACA pode nao ter o CORPUS —
    e foi exactamente o caso medido a 2026-09-14: `data/raw/REEL-MIDIA` estava
    vazia nesta maquina, e havia audio real ja preservado noutra pasta da
    operacao. Sem esta porta, a unica alternativa seria baixar midia nova, que
    e adquirir conteudo por uma rota que nenhuma missao de hardware autoriza.

        MEDIR O FERRO PRECISA DE AUDIO. NAO PRECISA DE VERDADE DECLARADA.
        MEDIR A QUALIDADE PRECISA DAS DUAS, E POR ISSO SO A PRIMEIRA A MEDE.

    Quem entra pela segunda porta sai com `QUALITY = NOT_MEASURED` colado, e
    `TERMOS` vazio. Ler acerto dali seria inventar a verdade que falta.
    """
    raiz = midia or MIDIA
    v = verdade()
    fora = []
    for reel, meta in sorted(v.items()):
        wav = os.path.join(raiz, '%s.wav' % reel)
        if os.path.exists(wav):
            fora.append({'REEL': reel, 'WAV': wav, 'QUALITY': 'MEASURED', **meta})
    if fora or not midia or not os.path.isdir(raiz):
        return fora
    for nome in sorted(os.listdir(raiz)):
        if not nome.lower().endswith('.wav'):
            continue
        fora.append({'REEL': os.path.splitext(nome)[0],
                     'WAV': os.path.join(raiz, nome),
                     # `None` aqui NAO e descuido: e o que faz o reconhecedor
                     # detectar a lingua em vez de a receber. Declarar uma
                     # lingua que ninguem provou seria inventar metade do dado.
                     'IDIOMA': None, 'CONTA': NAO_SE_APLICA, 'TERMOS': [],
                     'QUALITY': NAO_MEDIDO})
    return fora


def _pico_de_ram():
    """RAM do processo, em MiB. → valor ou NOT_MEASURED. Nunca levanta."""
    try:
        import resource                                        # noqa: PLC0415
        kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux devolve KiB; macOS devolve bytes. A heuristica e grosseira de
        # proposito: um numero com ordem de grandeza certa vale mais do que um
        # numero preciso da unidade errada.
        return round(kb / 1024, 1) if kb > 10 ** 6 / 1024 else round(kb / 1024, 1)
    except Exception:                                          # noqa: BLE001
        pass
    try:
        if os.path.isdir(fl.LIBS) and fl.LIBS not in sys.path:
            sys.path.insert(0, fl.LIBS)
        import psutil                                          # noqa: PLC0415
        return round(psutil.Process().memory_info().rss / 2 ** 20, 1)
    except Exception:                                          # noqa: BLE001
        return NAO_MEDIDO


def _vram_usada():
    """VRAM ocupada agora, em MiB. → valor, NOT_APPLICABLE ou NOT_MEASURED."""
    import shutil                                              # noqa: PLC0415
    import subprocess                                          # noqa: PLC0415
    exe = shutil.which('nvidia-smi')
    if exe is None:
        return NAO_SE_APLICA
    try:
        r = subprocess.run([exe, '--query-gpu=memory.used,utilization.gpu',
                            '--format=csv,noheader,nounits'],
                           capture_output=True, text=True, timeout=20)
    except Exception:                                          # noqa: BLE001
        return NAO_MEDIDO
    if r.returncode != 0 or not r.stdout.strip():
        return NAO_MEDIDO
    n = re.findall(r'\d+', r.stdout)
    return {'VRAM_USED_MB': int(n[0]) if n else NAO_MEDIDO,
            'GPU_UTILIZATION_PCT': int(n[1]) if len(n) > 1 else NAO_MEDIDO}


def uma(amostra, *, modelo, dispositivo):
    """Uma amostra, uma configuracao. → a linha da tabela.

    O IDIOMA E DECLARADO, E ISSO E DE PROPOSITO
    --------------------------------------------
    O corpus sabe a lingua de cada peca. Deixar o detector escolher mediria o
    detector, e a pergunta desta missao e sobre o RECONHECEDOR. A estabilidade
    de lingua mede-se a parte, comparando o que ele DETECTOU com o que se sabia.
    """
    t0 = time.time()
    r = fl.transcrever(amostra['WAV'], idioma=amostra['IDIOMA'],
                       modelo_nome=modelo, dispositivo=dispositivo)
    parede = round(time.time() - t0, 2)
    texto = r.get('TRANSCRIPT') or ''

    achados, tipos = [], {'TERM': [0, 0], 'BRAND': [0, 0]}
    for t in amostra['TERMOS']:
        ok = _tem_termo(texto, t['TERMO'])
        achados.append({'TERMO': t['TERMO'], 'TIPO': t['TIPO'],
                        'ENCONTRADO': 'YES' if ok else 'NO'})
        tipos[t['TIPO']][1] += 1
        tipos[t['TIPO']][0] += 1 if ok else 0

    # ── ESTABILIDADE DE LINGUA ────────────────────────────────────────────
    # Tres estados, e nao dois. `DECLARED_ONLY` quer dizer que o motor nao
    # devolveu deteccao para comparar — o que nao e nem estavel nem instavel.
    det = r.get('LANGUAGE_DETECTED')
    if amostra.get('IDIOMA') in (None, '', fl.NAO_SEI):
        # ⚠️ SEM LINGUA DECLARADA NAO HA ESTABILIDADE PARA MEDIR.
        # Comparar o detectado com `None` dava `DRIFT` em toda a linha — uma
        # deriva publicada onde nunca houve ponto de partida para derivar.
        estabilidade = 'NOT_DECLARED'
    elif det in (None, fl.NAO_SEI):
        estabilidade = 'DECLARED_ONLY'
    elif str(det).lower() == str(amostra['IDIOMA']).lower():
        estabilidade = 'STABLE'
    else:
        estabilidade = 'DRIFT'

    linha = {
        'REEL': amostra['REEL'],
        # De que porta veio esta amostra. Sem verdade declarada nao ha acerto
        # para ler, e o campo di-lo antes de alguem tentar.
        'QUALITY': amostra.get('QUALITY', NAO_MEDIDO),
        'LANGUAGE_REQUESTED': amostra['IDIOMA'],
        'LANGUAGE_DETECTED': det,
        'LANGUAGE_BASIS': r.get('LANGUAGE_SOURCE'),
        'LANGUAGE_STABILITY': estabilidade,
        'ASR_MODEL': r.get('ASR_MODEL'),
        'DEVICE_REQUESTED': r.get('ASR_DEVICE_REQUESTED'),
        # ── TRES CAMPOS ONDE ANTES IA UM ────────────────────────────────
        # O banco publicava `DEVICE_USED` sozinho, e ele enchia-se na ESCOLHA.
        # Uma linha com `DEVICE_USED=GPU` e `TRANSCRIPT_STATE=ASR_FALHOU` lia-se
        # como «a placa correu e o resultado foi mau» — quando a verdade era
        # «a placa foi escolhida e a inferencia nunca acabou».
        'DEVICE_SELECTED': r.get('ASR_DEVICE_SELECTED'),
        'DEVICE_EXECUTION': r.get('ASR_DEVICE_EXECUTION'),
        'DEVICE_USED': r.get('ASR_DEVICE_USED'),
        'WHY_FALLBACK': r.get('ASR_WHY_FALLBACK'),
        'COMPUTE_TYPE': r.get('ASR_DEVICE'),
        'AUDIO_DURATION_S': r.get('AUDIO_SECONDS'),
        'WALL_TIME_S': parede,
        'REALTIME_FACTOR': r.get('REALTIME_FACTOR'),
        'PEAK_RAM_MB': _pico_de_ram(),
        'TRANSCRIPT_STATE': r.get('TRANSCRIPT_STATE'),
        'TRANSCRIPT_CHARS': r.get('TRANSCRIPT_CHARS'),
        # O TEXTO FICA. Um banco que publica so o numero do acerto obriga a
        # acreditar no numero; com o texto ao lado, quem le confere.
        'TRANSCRIPT': texto,
        'TERMS': achados,
        'TERM_ACCURACY': '%d/%d' % tuple(tipos['TERM']) if tipos['TERM'][1] else NAO_SE_APLICA,
        'BRAND_ACCURACY': '%d/%d' % tuple(tipos['BRAND']) if tipos['BRAND'][1] else NAO_SE_APLICA,
        'FAILURE': r.get('ERROR'),
    }
    v = _vram_usada()
    if isinstance(v, dict):
        linha.update(v)
    else:
        linha['VRAM_USED_MB'] = v
    return linha


def correr(modelos, dispositivo, midia=None):
    ams = amostras(midia)
    linhas = []
    for m in modelos:
        for a in ams:
            linhas.append(uma(a, modelo=m, dispositivo=dispositivo))
    return linhas


def ferro_a_ferro(modelos, midia=None):
    """O MESMO audio, nos dois ferros, na mesma corrida. → lista de pares.

    POR QUE ISTO NAO E «CORRER O BANCO DUAS VEZES»
    -----------------------------------------------
    Duas corridas separadas medem duas maquinas em dois momentos, e a diferenca
    de texto entre elas fica sem dono: foi o ferro, foi o modelo a recarregar,
    foi outra coisa a mexer na maquina. Aqui a unica variavel que muda e o
    dispositivo, peca a peca, no mesmo processo.

    E A PERGUNTA QUE ELE RESPONDE E ESTREITA, DE PROPOSITO
    -------------------------------------------------------
        «O TEXTO MUDA QUANDO SAI DO PROCESSADOR PARA A PLACA?»

    Nao responde se o texto esta CERTO — isso precisa de verdade de referencia
    declarada, e so o corpus canonico a tem.

        DOIS FERROS QUE CONCORDAM PODEM ESTAR ERRADOS OS DOIS,
        E CONCORDAR NAO E ACERTAR.

    A semelhanca e de caracteres (`difflib`), nao de sentido. Ela apanha a
    troca de uma palavra e nao sabe se a palavra trocada era a importante —
    por isso o texto dos dois lados sai inteiro no artefato, para se ler.
    """
    import difflib                                             # noqa: PLC0415
    pares = []
    for m in modelos:
        for a in amostras(midia):
            linhas = {d: uma(a, modelo=m, dispositivo=d) for d in (fl.CPU, fl.GPU)}
            t_cpu = linhas[fl.CPU].get('TRANSCRIPT') or ''
            t_gpu = linhas[fl.GPU].get('TRANSCRIPT') or ''
            s_cpu, s_gpu = (linhas[fl.CPU].get('WALL_TIME_S'),
                            linhas[fl.GPU].get('WALL_TIME_S'))
            pares.append({
                'REEL': a['REEL'],
                'ASR_MODEL': m,
                'QUALITY': a.get('QUALITY', NAO_MEDIDO),
                'AUDIO_DURATION_S': linhas[fl.CPU].get('AUDIO_DURATION_S'),
                'CPU_DEVICE_USED': linhas[fl.CPU].get('DEVICE_USED'),
                'GPU_DEVICE_USED': linhas[fl.GPU].get('DEVICE_USED'),
                'CPU_COMPUTE': linhas[fl.CPU].get('COMPUTE_TYPE'),
                'GPU_COMPUTE': linhas[fl.GPU].get('COMPUTE_TYPE'),
                'CPU_SECONDS': s_cpu,
                'GPU_SECONDS': s_gpu,
                'CPU_REALTIME_FACTOR': linhas[fl.CPU].get('REALTIME_FACTOR'),
                'GPU_REALTIME_FACTOR': linhas[fl.GPU].get('REALTIME_FACTOR'),
                'SPEEDUP': (round(s_cpu / s_gpu, 2)
                            if isinstance(s_cpu, (int, float))
                            and isinstance(s_gpu, (int, float)) and s_gpu else NAO_MEDIDO),
                'CPU_STATE': linhas[fl.CPU].get('TRANSCRIPT_STATE'),
                'GPU_STATE': linhas[fl.GPU].get('TRANSCRIPT_STATE'),
                'CPU_LANGUAGE_DETECTED': linhas[fl.CPU].get('LANGUAGE_DETECTED'),
                'GPU_LANGUAGE_DETECTED': linhas[fl.GPU].get('LANGUAGE_DETECTED'),
                'SAME_LANGUAGE': ('YES' if linhas[fl.CPU].get('LANGUAGE_DETECTED')
                                  == linhas[fl.GPU].get('LANGUAGE_DETECTED') else 'NO'),
                # ⚠️ DOIS VAZIOS NAO SAO UM ACORDO.
                # Medido a 2026-09-14: de 8 pecas, 4 saiam `TEXT_IDENTICAL=YES`
                # — e duas delas eram `REQUESTED_EMPTY` dos dois lados. Zero
                # caracteres iguais a zero caracteres e uma verdade aritmetica
                # que, somada na manchete, dizia «os dois ferros concordam em
                # metade» quando o que havia era «em duas nao houve texto».
                #
                #     COMPARAR PRECISA DE DUAS COISAS PARA COMPARAR.
                #
                # Por isso `COMPARABLE`, e por isso o total conta so as pecas
                # em que os dois lados escreveram alguma coisa.
                'COMPARABLE': 'YES' if (t_cpu and t_gpu) else 'NO',
                'BOTH_EMPTY': 'YES' if not (t_cpu or t_gpu) else 'NO',
                'TEXT_IDENTICAL': 'YES' if t_cpu == t_gpu else 'NO',
                'TEXT_SIMILARITY': (round(
                    difflib.SequenceMatcher(None, t_cpu, t_gpu).ratio(), 4)
                    if (t_cpu and t_gpu) else NAO_SE_APLICA),
                'CPU_TRANSCRIPT': t_cpu,
                'GPU_TRANSCRIPT': t_gpu,
                'QUALITY_VERDICT': NAO_MEDIDO,
                'QUALITY_WHY': ('semelhanca nao e acerto: sem verdade de referencia '
                                'declarada, esta linha nao diz se o texto esta certo'),
            })
    return pares


def cobertura(linhas):
    """Que linguas ficaram medidas, e quais NAO. A ausencia tem de aparecer."""
    vistas = {str(l['LANGUAGE_REQUESTED']).lower() for l in linhas}
    return {lg.upper(): ('MEASURED' if lg in vistas else NAO_MEDIDO)
            for lg in LINGUAS_ALVO}


def _tabela(linhas):
    print('\n  %-14s %-7s %-4s %-9s %-7s %-7s %-6s %-6s %s'
          % ('REEL', 'MODELO', 'DEV', 'ESTADO', 'RTF', 'TERMOS', 'MARCA', 'LING', 'AUDIO_S'))
    print('  ' + '-' * 86)
    for l in linhas:
        print('  %-14s %-7s %-4s %-9s %-7s %-7s %-6s %-6s %s'
              % (l['REEL'], l['ASR_MODEL'], l['DEVICE_EXECUTION'],
                 l['TRANSCRIPT_STATE'], l['REALTIME_FACTOR'],
                 l['TERM_ACCURACY'], l['BRAND_ACCURACY'],
                 l['LANGUAGE_STABILITY'][:6], l['AUDIO_DURATION_S']))


def _ferro_a_ferro_main(modelos, midia, ams, json_=False):
    pares = ferro_a_ferro(modelos, midia)
    audio = sum(p['AUDIO_DURATION_S'] for p in pares
                if isinstance(p.get('AUDIO_DURATION_S'), (int, float)))
    cpu_s = sum(p['CPU_SECONDS'] for p in pares
                if isinstance(p.get('CPU_SECONDS'), (int, float)))
    gpu_s = sum(p['GPU_SECONDS'] for p in pares
                if isinstance(p.get('GPU_SECONDS'), (int, float)))
    comparaveis = [p for p in pares if p['COMPARABLE'] == 'YES']
    iguais = sum(1 for p in comparaveis if p['TEXT_IDENTICAL'] == 'YES')
    vazios = sum(1 for p in pares if p['BOTH_EMPTY'] == 'YES')
    fora = {
        'BANCO': 'ASR-FERRO-A-FERRO-V1',
        'O_QUE_ISTO_RESPONDE': 'se o TEXTO muda entre o processador e a placa',
        'O_QUE_ISTO_NAO_RESPONDE': ('se o texto esta CERTO — isso exige verdade de '
                                    'referencia declarada, e as amostras sem ela '
                                    'saem QUALITY=NOT_MEASURED'),
        'CORPUS': _sem_o_dono(midia or MIDIA),
        'CORPUS_NOTE': 'audio JA preservado. Nada novo foi baixado.',
        'RUNNER_NAME': os.environ.get('RUNNER_NAME') or NAO_SE_APLICA,
        'MODELOS': modelos,
        'AMOSTRAS': len(ams),
        'AUDIO_SECONDS_TOTAL': round(audio, 1),
        'CPU_SECONDS_TOTAL': round(cpu_s, 2),
        'GPU_SECONDS_TOTAL': round(gpu_s, 2),
        'CPU_REALTIME_FACTOR_TOTAL': round(audio / cpu_s, 2) if cpu_s else NAO_MEDIDO,
        'GPU_REALTIME_FACTOR_TOTAL': round(audio / gpu_s, 2) if gpu_s else NAO_MEDIDO,
        'SPEEDUP_TOTAL': round(cpu_s / gpu_s, 2) if gpu_s else NAO_MEDIDO,
        # A manchete conta so onde havia o que comparar, e diz o denominador
        # ao lado — nunca «metade», nunca «quase sempre».
        'TEXT_IDENTICAL': '%d/%d' % (iguais, len(comparaveis)),
        'COMPARABLE_PAIRS': len(comparaveis),
        'BOTH_EMPTY_PAIRS': vazios,
        'PARES': pares,
    }
    if json_:
        print(json.dumps(fora, ensure_ascii=False, indent=1))
        return 0
    print('\nFERRO A FERRO — o mesmo audio, nos dois, na mesma corrida')
    print('=' * 92)
    print('  corpus      %s' % fora['CORPUS'])
    print('  modelos     %s' % ', '.join(modelos))
    print('\n  %-16s %-8s %-9s %-9s %-7s %-7s %-6s %s'
          % ('PECA', 'AUDIO_S', 'CPU_S', 'GPU_S', 'GANHO', 'IGUAL', 'SEMEL', 'LINGUA'))
    print('  ' + '-' * 88)
    for p in pares:
        print('  %-16s %-8s %-9s %-9s %-7s %-7s %-6s %s/%s'
              % (p['REEL'][:16], p['AUDIO_DURATION_S'], p['CPU_SECONDS'],
                 p['GPU_SECONDS'], p['SPEEDUP'], p['TEXT_IDENTICAL'],
                 p['TEXT_SIMILARITY'], p['CPU_LANGUAGE_DETECTED'],
                 p['GPU_LANGUAGE_DETECTED']))
    print('  ' + '-' * 88)
    print('  %-16s %-8s %-9s %-9s %-7s %s'
          % ('TOTAL', fora['AUDIO_SECONDS_TOTAL'], fora['CPU_SECONDS_TOTAL'],
             fora['GPU_SECONDS_TOTAL'], fora['SPEEDUP_TOTAL'], fora['TEXT_IDENTICAL']))
    print('\n  RTF  cpu %s x tempo real  ·  gpu %s x tempo real'
          % (fora['CPU_REALTIME_FACTOR_TOTAL'], fora['GPU_REALTIME_FACTOR_TOTAL']))
    print('  texto igual nos dois ferros: %s das pecas COM texto dos dois lados'
          % fora['TEXT_IDENTICAL'])
    print('  pecas sem texto nenhum dos dois lados: %d — nao entram na conta, '
          'porque dois vazios nao sao um acordo' % fora['BOTH_EMPTY_PAIRS'])
    print('\n  QUALITY_VERDICT = NOT_MEASURED — %s\n' % fora['O_QUE_ISTO_NAO_RESPONDE'])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modelos', default=fl.MODELO_PADRAO)
    ap.add_argument('--device', default=None,
                    help='AUTO · CPU · GPU. Ausente = o padrao do dono.')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--midia', default=None,
                    help='pasta de .wav JA PRESERVADOS, quando o corpus canonico '
                         'nao esta nesta maquina. Nao baixa nada.')
    ap.add_argument('--ferro-a-ferro', action='store_true',
                    help='o mesmo audio no processador e na placa, lado a lado')
    a = ap.parse_args()
    modelos = [m.strip() for m in a.modelos.split(',') if m.strip()]

    ha, porque = fl.disponivel()
    if not ha:
        print('ASR_INDISPONIVEL · %s' % porque)
        return 1

    ams = amostras(a.midia)
    if not ams:
        print('SEM_CORPUS · nenhum .wav preservado com verdade de referencia '
              'declarada. Isto NAO autoriza baixar midia nova.')
        return 1

    if a.ferro_a_ferro:
        return _ferro_a_ferro_main(modelos, a.midia, ams, json_=a.json)

    linhas = correr(modelos, a.device, a.midia)
    cob = cobertura(linhas)
    fora = {
        'BANCO': 'ASR-LOCAL-V1',
        'RUNNER_NAME': os.environ.get('RUNNER_NAME') or NAO_SE_APLICA,
        'CORPUS': '%s — ja preservado, nada novo foi baixado'
                  % _sem_o_dono(a.midia or 'data/raw/REEL-MIDIA'),
        'GROUND_TRUTH': 'data/samples/REEL-TRANSCRICOES/QUALIDADE-DA-FALA-V1.json',
        'MODELOS': modelos,
        'DEVICE_ARG': a.device or fl.DISPOSITIVO_PADRAO,
        'AMOSTRAS': len(ams),
        'LANGUAGE_COVERAGE': cob,
        'LINHAS': linhas,
    }
    if a.json:
        print(json.dumps(fora, ensure_ascii=False, indent=1))
        return 0

    print('\nBANCO DE PROVA DO RECONHECEDOR — %d amostras ja preservadas' % len(ams))
    print('=' * 90)
    print('  corpus        %s' % fora['CORPUS'])
    print('  verdade       %s' % fora['GROUND_TRUTH'])
    print('  modelos       %s' % ', '.join(modelos))
    print('  dispositivo   %s (pedido)' % fora['DEVICE_ARG'])
    _tabela(linhas)
    print('\n  COBERTURA DE LINGUA')
    for lg, est in cob.items():
        print('    %-4s %s' % (lg, est))
    quedas = {l['WHY_FALLBACK'] for l in linhas if l.get('WHY_FALLBACK')}
    print('\n  QUEDAS DECLARADAS: %s' % (', '.join(sorted(quedas)) if quedas
                                         else 'nenhuma'))
    print('')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
