#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROTA APOSENTADA NA C10.4C — ESTE FICHEIRO NÃO TRANSCREVE NADA.

Ele implementava «obter a fala de um Reel do Instagram» pelo caminho que a C8
proibiu:

    baixar o MP4 INTEIRO  →  `ffmpeg -vn`  →  ASR

        TRANSCRIPTION NEED != VIDEO DOWNLOAD.

A C10.4B mediu que ele continuava ALCANÇÁVEL — não por `import` nenhum, mas por
`workflow_dispatch` (fases `transcrever` e `transcrever-alvos`), pelo seu próprio
`__main__`, e pelas instruções operacionais que mandavam correr estes comandos.
A C10.4B travou-o pela política. Travar não é aposentar:

    BLOCKED != RETIRED.  DISABLED != RETIRED.

A C10.4C fechou as portas. Nenhuma função aqui adquire, converte ou transcreve:
todas levantam `RotaAposentada`, e o `__main__` recusa alto, com código 2.

    UM SCRIPT QUE SAI 0 SEM FAZER NADA DIZ QUE CORREU.

O DONO ÚNICO DE TRANSCRIÇÃO DE REEL É:

    coleta/adaptador_instagram.py  →  ferramentas/reel_transcricao.py
    pedido audio-only · ASR local (`ferramentas/fala_local.py`) · portão de
    política antes da rede

Não transformar isto num delegador. Um wrapper que delega continua a ser um nome
pelo qual a capacidade atende, e a casa já tem o nome certo.

    ONE CONCEPT → ONE OWNER.

O FICHEIRO FICA PORQUE A MEDIÇÃO FICA
---------------------------------------
O que ele cronometrou em 2026-09-02 — num reel real de 110 s da @basf_agroes,
16 núcleos, modo em lote — continua a valer e está citado em
`ferramentas/youtube_transcrever.py`, `coleta/youtube_relevancia.py` e nos
documentos da casa:

    modelo    velocidade      qualidade do texto
    tiny      18,7x           "Pirar Pascal", "agro-imfluencia" — inutilizável
    base       9,4x           "Pilar Pasqual", "ingeniero-agricula" — média
    small      3,2x           "Pilar Pascual", "ingeniero agrícola" — boa

E as duas coisas que custaram medição para descobrir: os núcleos não vêm de
graça (declarar `cpu_threads` deu ~4x nesta máquina), e `beam_size=5` custa o
dobro e entrega o mesmo texto. Essas decisões vivem hoje no dono do
reconhecedor, `ferramentas/fala_local.py`, que é quem as aplica.

Apagar o ficheiro apagaria a proveniência dessas três linhas de número. Aposentar
a rota não pede isso — pede que ela deixe de ser uma porta, e deixou.

O QUE A FILA DELE ESCOLHIA
----------------------------
`alvos` decidia que objetos da janela entravam na transcrição: vídeo sim, áudio
de catálogo não, `VIDEO_URL_TEMPORARY` presente — critérios do caminho de vídeo
inteiro, e por isso parte da rota aposentada, não capacidade à parte. Ficam
escritos em `docs/sintonia-scrap/C10-4C-APOSENTAR-A-ROTA-LEGADA.md`. Se o dono
canônico vier a precisar de fila, constrói a dele, com o nome dele.

A DESCOBERTA CONTINUA VIVA, E NÃO É ISTO
------------------------------------------
`coleta/instagram_janela.py` — perfis, objetos, metadados — não foi tocado.
Descoberta não é transcrição, e essa é diferença de conceito, não de pasta.
"""
import sys

# ══════════════════════════════════════════════════════════════════════════
#: O que qualquer chamador desta rota tem de ver, em vez do que ela fazia.
APOSENTADO = (
    'ROTA_APOSENTADA: `instagram_transcrever` baixava o video inteiro para '
    'transcrever. Aposentada na C10.4C. O dono unico de transcricao de Reel e '
    '`coleta/adaptador_instagram.py` -> `ferramentas/reel_transcricao.py`, que '
    'pede so audio e atravessa o portao de politica antes da rede.')


class RotaAposentada(RuntimeError):
    """Levantada por tudo o que esta rota fazia e deixou de fazer."""


#: O ACTO QUE ESTE FICHEIRO EXECUTAVA, NA LÍNGUA DA MATRIZ.
#: Fica declarado para que uma leitura futura saiba de que capacidade se está a
#: falar — e para que se veja que é a MESMA que o dono canônico pergunta.
#: A pergunta de política saiu daqui com a aposentadoria: quem não adquire não
#: precisa de autorização para adquirir. Ela vive no dono canônico.
CAPACIDADE_NA_MATRIZ = 'FETCH_TRANSCRIPT'
PLATAFORMA = 'INSTAGRAM'


# ───────────────────────────────────────────── o que ela fazia, e deixou de fazer
def alvos():
    """APOSENTADA. Escolhia que objetos entravam na fila do caminho de vídeo."""
    raise RotaAposentada(APOSENTADO)


def fase_alvos():
    """APOSENTADA. Era o relatório de custo dessa fila."""
    raise RotaAposentada(APOSENTADO)


def _baixar(url, destino):
    """APOSENTADA. Baixava o MP4 inteiro da CDN da Meta; hoje não baixa nada."""
    raise RotaAposentada(APOSENTADO)


def _url_nova(shortcode):
    """APOSENTADA. Relia o embed para arranjar um MP4 vivo; hoje não o faz."""
    raise RotaAposentada(APOSENTADO)


def _audio(shortcode, url):
    """APOSENTADA. Corria `ffmpeg -vn` sobre o vídeo já baixado."""
    raise RotaAposentada(APOSENTADO)


def fase_rodar(modelo=None, teto=None):
    """APOSENTADA. Era o laço operacional inteiro desta rota."""
    raise RotaAposentada(APOSENTADO)


if __name__ == '__main__':
    # ── SEM ENTRYPOINT OPERACIONAL — APOSENTADO NA C10.4C ───────────────────
    # Não há `alvos`, não há `rodar`, e não há argumento nenhum que faça este
    # ficheiro adquirir seja o que for.
    #
    # E ele RECUSA ALTO, com código 2. Um script aposentado que sai 0 em
    # silêncio é pior do que uma porta aberta: quem o chamasse veria sucesso.
    print(APOSENTADO, file=sys.stderr)
    raise SystemExit(2)
