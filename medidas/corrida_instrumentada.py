#!/usr/bin/env python3
"""A FRONTEIRA — o primeiro caminho real a deixar pegada.

    TELEMETRIA OBSERVA O FLUXO. NAO MUDA O RESULTADO DO FLUXO.

DUAS SESSOES FIZERAM O9 EM PARALELO, E ESCOLHERAM O MESMO EXECUTOR
------------------------------------------------------------------
E chegaram a mesma semantica sem se falarem: os mesmos baldes, as copias
repetidas como REUSED, o `NEEDS_OCR` como `rejected` e nao `error`, o grao a
mudar no meio. Divergiram num ponto so: ONDE a traducao vive.

    A OUTRA SESSAO   dentro do executor, em `emitir_rastro`, com o `rastro`
                     injetado — `None` por omissao, e entao nada muda.
    ESTA             fora, numa fronteira que corre o executor e o observa.

Duas traducoes do mesmo recibo seriam DOIS DONOS DA MESMA PERGUNTA — o pecado
de O8C, um andar acima. Entao esta fronteira DEIXOU de traduzir: ela passa o
banco pela costura que a outra sessao abriu, e quem traduz e quem sabe.

    A INFORMACAO NASCE ONDE E CONHECIDA.

O que fica aqui e o que uma fronteira deve mesmo possuir, e o executor nao:
o ciclo da corrida, o caminho da MORTE do executor (uma falha que nao deixa
linha e uma falha que ninguem consegue procurar depois), e o facto de este ser
o ponto de entrada instrumentado — que amanha serve o segundo executor sem
copiar boilerplate para dentro dele.

    EXECUTOR != TELEMETRY OWNER, e nenhum dos dois e os dois.

E A INVARIANCIA CONTINUA PROVAVEL: com `rastro=None` o executor percorre
exatamente o mesmo caminho de antes, e o teste compara as duas corridas.

POR QUE ESTE CAMINHO, E NAO OUTRO
----------------------------------
Medido em `system-map/data/executores.generated.json`, e nao escolhido por
gosto: e o unico candidato que junta INPUT REAL PRESERVADO (49 PDF italianos
em `data/collection-store/`), DUAS etapas reais nomeadas (RAW e DERIVED), zero
rede, zero API paga e zero producao. O BK de M1 recomendou RC-1 para a M2 —
e O9 nao e M2: a melhor rota para construir a proxima aresta nao e a melhor
para provar telemetria.

O QUE O RUNNER PODE E O QUE NAO PODE
-------------------------------------
    O ORQUESTRADOR NAO PODE INVENTAR O QUE SO O EXECUTOR SABE.

Todos os numeros abaixo NASCEM no recibo do executor. O runner nao conta PDF,
nao abre ficheiro, nao adivinha. Ele traduz — e onde o executor nao mede, aqui
fica NULL, nunca zero.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas                    # noqa: E402,F401
import diagnostico as dg           # noqa: E402
import falhas                      # noqa: E402
import rastro_da_coleta as rastro  # noqa: E402
from rastro_da_coleta import _lit  # noqa: E402
import telemetria as tel           # noqa: E402

# A fonte e a rota deste caminho, medidas: os PDF vem do armazem italiano, e a
# classe da rota e a do documento oficial por HTTP — foi por ela que entraram.
# ⚠️ NÃO HÁ IDENTIDADE PROVADA PARA ESTA CORRIDA, E POR ISSO ELA É NULA.
# Este ficheiro dizia `IT-CORPUS-PDF` e o executor dizia `IT-PDF-ITALIANOS`:
# dois nomes para a mesma coleta, e nenhum dos dois existe no catálogo. A
# mesma corrida tinha uma identidade quando corria bem e outra quando o
# executor morria antes de emitir.
#
#     A LOCALIZAÇÃO DA FALHA NÃO PODE MUDAR A IDENTIDADE DA FONTE.
#
# Medido: os 49 PDF atravessam OITO `source_id` reais em 23 ficheiros, e 26
# não têm nenhum derivável. A `route_class` não está registada por item — nem
# no `collection-store`, nem no `collection-ledger`. RC-1 era presunção.
#
#     UM ID DE RASTREIO INVENTADO É PIOR DO QUE UNKNOWN.
#
# `etapa_da_corrida` aceita NULL nos dois campos. É esta a representação, e
# ela já existia.
SOURCE_ID = None
ROUTE_CLASS_ID = None
POLICY_VERSION = 'o9:replay-legado-de-pdf'

# ── OS GRAOS, E POR QUE ELES MUDAM DUAS VEZES ────────────────────────────
#     UM CAMINHO EM DISCO NAO E UM CONTEUDO. UM CONTEUDO NAO E UM TEXTO.
# Seis dos 49 PDF sao a MESMA coisa guardada em dois sitios. Contar 49
# «documentos» seria contar seis duas vezes. E os 43 conteudos viram 43 textos,
# que sao outra especie ainda. Com o grao a mudar em cada etapa, nenhuma razao
# entre entrada e saida e rendimento — e o contrato recusa-se a calcula-la.
GRAO_FICHEIRO = 'RAW_FILE'
GRAO_CONTEUDO = 'RAW_CONTENT'
GRAO_TEXTO = 'TEXT_ARTIFACT'


def _ms(t0):
    return int((time.time() - t0) * 1000)


def _estado_canonico(recibo):
    """De que especie foi a falha, na lingua de `falhas.py`.

    A ferramenta em falta e `EXECUTOR_UNAVAILABLE` — camada EXECUTOR, defeito
    nosso, e NAO uma afirmacao sobre a fonte. Os PDF continuam bons.

        ROTA CAIDA NAO E FONTE CAIDA.
    """
    if recibo.get('FERRAMENTA') == 'AUSENTE':
        return 'EXECUTOR_UNAVAILABLE'
    return 'UNKNOWN_ERROR'


def correr(banco, *, run_id, correr_executor=None, seco=False):
    """Corre o caminho real com a telemetria ligada. Devolve o recibo.

    `correr_executor` e injetavel para a prova de falha poder partir UMA etapa
    sem tocar em fonte nenhuma e sem editar o executor de verdade.
    """
    if correr_executor is None:
        sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
        import executor_texto_de_pdf as ex
        correr_executor = ex.correr

    t0 = time.time()
    try:
        # O BANCO VAI PARA DENTRO. Quem conta e quem sabe contar; esta
        # fronteira nao recontou nada, e por isso nao pode discordar.
        return correr_executor(seco=seco, run_id=run_id, rastro=banco,
                               source_id=SOURCE_ID,
                               route_class_id=ROUTE_CLASS_ID)
    except Exception as erro:
        # ⚠️ O EXECUTOR MORREU ANTES DE EMITIR.
        # Este e o unico caso em que a fronteira escreve: se ela nao
        # escrevesse, a corrida acabaria sem UMA linha, e uma falha sem linha e
        # uma falha que ninguem consegue procurar depois. O executor nao pode
        # cobrir este caso — ele ja nao esta vivo para o contar.
        # ⚠️ A TENTATIVA E MEDIDA, E NAO ZERO FIXO.
        # Com `tentativa=0` fixo, uma segunda passagem pela mesma corrida
        # colidia na chave (run_id, etapa, tentativa) e a linha da MORTE
        # perdia-se — o erro do banco subia com o mesmo tipo do erro do
        # executor, e ninguem via a diferenca. Uma falha que nao deixa linha e
        # exatamente o que esta fronteira existe para impedir.
        try:
            ja = banco.executa(
                "select coalesce(max(tentativa), -1) from"
                " public.etapa_da_corrida where run_id = %s and etapa = 'DERIVED'"
                % _lit(run_id))
            tentativa = int(ja[0][0]) + 1
        except Exception:
            tentativa = 0
        rastro.registrar(
            banco, run_id=run_id, etapa='DERIVED', edge_from='RAW',
            tentativa=tentativa,
            estado='FAIL', source_id=SOURCE_ID, route_class_id=ROUTE_CLASS_ID,
            policy_version=POLICY_VERSION, duracao_ms=_ms(t0),
            actor='coleta/executor_texto_de_pdf.py',
            canonical_state='UNKNOWN_ERROR',
            diagnostic_code=dg.DERIVATION_FAILED,
            error_class=type(erro).__name__, error_message=str(erro),
            last_good_artifact='RAW')
        raise


def main():
    print(__doc__.strip().split('\n')[0])
    print('fonte=%s rota=%s politica=%s'
          % (SOURCE_ID or 'UNKNOWN', ROUTE_CLASS_ID or 'UNKNOWN',
             POLICY_VERSION))
    print('modo: LEGACY_REPLAY · etapas observadas: RAW, DERIVED')
    print('termina em DERIVED: STRUCTURED e ADMISSION nao correm neste caminho')
    print('destinos do contrato: %s' % ', '.join(tel.DESTINOS_DO_ITEM))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
