#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTAÇÃO DAS GUARDAS DO SCRAP-PORTAS — cada guarda tem de morder.

Para cada guarda nova: estraga-se o CÓDIGO (ou a lei) que a sustenta, corre-se o
teste que a declara, e exige-se VERMELHO. Guarda cujo teste continua verde com a
guarda arrancada não é guarda — é decoração.

Restauro: `git checkout --` do ficheiro tocado, sempre, mesmo quando falha.

    py tests/mutacao_do_scrap_portas.py
"""
import io
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
#: Onde ficam as cópias de segurança dos ficheiros mutados.
TMP = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp',
                   'mutacao-scrap-portas')


def corre(modulo):
    r = subprocess.run([PY, "-m", "unittest", modulo], cwd=RAIZ,
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:]


def muta(ficheiro, velho, novo):
    """→ (aplicou?, motivo). O ficheiro tem de ter o velho UMA vez.

    ⚠️ O ficheiro do repositório guarda CRLF, e uma âncora escrita com `\\n`
    não casa nele — foi assim que duas mutações ficaram «NÃO APLICOU» e
    pareceram defeito do teste. Tenta-se a âncora como veio e, depois, com o
    fim-de-linha do ficheiro.
    """
    caminho = os.path.join(RAIZ, ficheiro)
    s = io.open(caminho, encoding='utf-8', newline='').read()
    for velho_a, novo_a in ((velho, novo),
                            (velho.replace('\n', '\r\n'),
                             novo.replace('\n', '\r\n'))):
        if s.count(velho_a) == 1:
            _copia_de_seguranca(ficheiro, s)
            io.open(caminho, 'w', encoding='utf-8', newline='').write(
                s.replace(velho_a, novo_a))
            return True, "ok"
    return False, "ocorrencias=%d" % s.count(velho)


def _copia_de_seguranca(ficheiro, conteudo):
    """Guarda o ficheiro como estava, ANTES de o estragar.

    ⚠️ ESTA FUNÇÃO NASCEU DE UM ESTRAGO MEDIDO, NÃO DE UMA PRECAUÇÃO.
    A primeira versão desta bancada restaurava com `git checkout --`, e isso
    apagou trabalho que ainda não estava commitado: a matriz foi mutada e
    «restaurada» para o HEAD — que era ANTERIOR à decisão D22 — e o commit
    seguinte levou a matriz velha com os testes novos. O teste ficou vermelho
    depois de ter estado verde, e o defeito não estava em nenhum dos dois.

        RESTAURAR DO HEAD NÃO É RESTAURAR: É DESCARTAR O QUE AINDA NÃO FOI
        COMMITADO. A GUARDA TEM DE GUARDAR O FICHEIRO ANTES DE O ESTRAGAR.
    """
    destino = os.path.join(TMP, ficheiro.replace('/', '__'))
    os.makedirs(TMP, exist_ok=True)
    io.open(destino, 'w', encoding='utf-8', newline='').write(conteudo)
    return destino


def restaura(ficheiro):
    """Devolve o ficheiro EXACTAMENTE como estava antes da mutação."""
    copia = os.path.join(TMP, ficheiro.replace('/', '__'))
    caminho = os.path.join(RAIZ, ficheiro)
    if os.path.exists(copia):
        io.open(caminho, 'w', encoding='utf-8', newline='').write(
            io.open(copia, encoding='utf-8', newline='').read())
        return True
    return False


CASOS = [
    # ── M1 · a LEI volta a recusar o Reel: a porta que o corre passa a
    #         discordar da matriz, e o teste das duas portas tem de ver
    ("leis/social_matriz.py",
     "            r('instagram_transcrever.py:faster-whisper', 'LOCAL_EXECUTOR', 'SIM',\n              'PROVED',",
     "            r('instagram_transcrever.py:faster-whisper', 'LOCAL_EXECUTOR', 'NAO',\n              'ROUTE_NOT_ALLOWED',",
     "tests.test_as_duas_portas_do_scrap",
     "M1 · a matriz recusa o que a porta corre"),
    # ── M2 · o portão deixa de consultar a lei (o defeito SOC1, de volta)
    ("coleta/scrap_executor.py",
     "    if veredicto['MATRIZ_DECISAO'] == mz.NAO_PERMITIDA:",
     "    if False and veredicto['MATRIZ_DECISAO'] == mz.NAO_PERMITIDA:",
     "tests.test_as_duas_portas_do_scrap",
     "M2 · o CHECK deixa de consultar a matriz"),
    # ── M3 · as três do Reel deixam de ter nome na lei
    ("coleta/scrap_capacidades.py",
     "    'instagram.reel.capture': ('INSTAGRAM', PROVEN, EITHER, None, _RE, 'FETCH_TRANSCRIPT')",
     "    'instagram.reel.capture': ('INSTAGRAM', PROVEN, EITHER, None, _RE, None)",
     "tests.test_as_duas_portas_do_scrap",
     "M3 · o Reel perde a capacidade grossa"),
    # ── M4 · o dono do contrato deixa de materializar a identidade
    ("regras/contratos_de_fonte.py",
     '    if regra == NAO_SEI:\n        fora["BASE"] = (',
     '    if True:\n        fora["BASE"] = (',
     "tests.test_cadeia_do_audio_offline",
     "M4 · o DOCUMENT_ID volta a NAO SEI"),
    # ── M5 · o prazo de 30 dias deixa de ser carimbado
    ("coleta/social_envelope.py",
     "    fora.update(retencao_da_rota(route, coletado_em=fora['COLLECTED_AT']))",
     "    fora.update({})",
     "tests.test_as_duas_portas_do_scrap",
     "M5 · a retenção da Data API desaparece"),
    # ── M6 · o RAW do Reel volta a não declarar a espécie
    ("ferramentas/reel_transcricao.py",
     "def _especie_do_ficheiro(caminho, media_kind):",
     "def _especie_do_ficheiro(caminho, media_kind):\n    return None, 'MUTACAO'",
     "tests.test_cadeia_do_audio_offline",
     "M6 · o RAW do Reel perde a espécie"),
]


def main():
    print("MUTACAO_DO_SCRAP_PORTAS")
    mordeu = 0
    nao_mordeu = []
    nao_aplicou = []
    for ficheiro, velho, novo, modulo, nome in CASOS:
        ok, motivo = muta(ficheiro, velho, novo)
        if not ok:
            print("  NAO_APLICOU  %s (%s)" % (nome, motivo))
            nao_aplicou.append(nome)
            continue
        try:
            verde, cauda = corre(modulo)
        finally:
            restaura(ficheiro)
        if verde:
            print("  NAO_MORDEU   %s — o teste %s continuou verde" % (nome, modulo))
            nao_mordeu.append(nome)
        else:
            mordeu += 1
            print("  MORDEU       %s — %s" % (nome, cauda[0][:90] if cauda else ""))
    print()
    print("MUTACOES_MORDERAM=%d/%d" % (mordeu, len(CASOS)))
    if nao_mordeu:
        print("NAO_MORDERAM=%s" % "; ".join(nao_mordeu))
    if nao_aplicou:
        print("NAO_APLICADAS=%s" % "; ".join(nao_aplicou))
    return 0 if (not nao_mordeu and not nao_aplicou) else 1


if __name__ == '__main__':
    sys.exit(main())
