#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS 15 CRITICOS, CLASSIFICADOS POR TIPO ANTES DE SE PROCURAR MAIS FONTE.

POR QUE O TIPO VEM PRIMEIRO
---------------------------
Procurar fonte publica para um dado que a lei proibe publicar e' procurar para
sempre. A missao anterior ja achou um caso desses (as provas GEP). Sem
classificar o tipo, a busca nunca termina e a conclusao nunca aparece.

    SOURCE_GAP                  falta quem produza. Procurar fonte RESOLVE.
    ACCESS_GAP                  o dado EXISTE e tem dono que nao o publica.
                                Resolve-se por contrato, licenca ou parceria.
    DATA_MODEL_GAP              o dado esta em casa e falta LIGAR ou ESCREVER.
                                Nenhuma coleta resolve.
    COLLECTION_CAPABILITY_GAP   a fonte existe e publica; falta-nos a
                                CAPACIDADE de a ler (JS, login, DNS, PDF).
                                Nao e' gap de fonte: e' gap nosso.
    UNKNOWN                     nao sei, e digo que nao sei.

A CONTA QUE INTERESSA
---------------------
CRITICAL_GAPS_BEFORE nao baixa por eu ter achado fonte. Baixa quando o gap
deixa de ser SOURCE_GAP sem resposta. Um gap reclassificado como ACCESS_GAP
continua a doer — mas para de consumir buscas.
"""

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-fechar")
ANTES = Path("C:/Users/London1/AppData/Local/Temp/sintonia-gap")

# chave = "TOOL · RAW_NEED" → (tipo, estado_depois, quem_fecha, porque)
GAPS = {

 "WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)": (
  "SOURCE_GAP", "FECHADO",
  "Bollettini colture estensive Veneto · Bollettini interprovinciali "
  "Emilia-Romagna · ERSA FVG (mais BBCH 42-70) · Bollettini UTM Campania · "
  "Consorzi Fitosanitari (pomodoro) · ARSAC · CAAR Liguria · AMAP Marche",
  "era o buraco central (`CROP_STAGE 0/29`) e agora ha OITO fontes abertas e "
  "validadas que publicam fase por cultura. ⚠️ E fica uma correcao minha: eu "
  "apresentei o boletim nacional da RRN como fonte de fenologia por cultura — "
  "a busca desta missao mediu que ele cobre PRINCIPALMENTE VITE, OLIVO E "
  "ROBINIA. Continua forte, mas para tres culturas, nao para dez. As arvenses "
  "vem das regioes."),

 "WINDOWS · RASTREABILIDADE: que fonte sustenta esta janela": (
  "DATA_MODEL_GAP", "ABERTO — E NAO FECHA COM FONTE",
  "—",
  "`SOURCE_IDS 0/29`. As fontes existem, agora 21 delas abertas e validadas. "
  "O que falta e' ESCREVER qual sustentou qual janela. Coletar mais nao "
  "conserta; a accao e' de modelo de dado."),

 "MARKET · PRODUCAO, AREA e RENDIMENTO por cultura": (
  "SOURCE_GAP", "FECHADO COM DADO NA MAO",
  "ISTAT dataflow 101_1015_DF_DCSP_COLTIVAZIONI_1 (SDMX)",
  "⚠️ E AQUI CORRIGI DUAS COISAS MINHAS. O identificador que eu tinha escrito "
  "(«DCSP_COLTIVAZIONI») NAO EXISTE — o servico responde «Could not find "
  "requested structures». Procurei nos 4.907 dataflows publicados e achei o "
  "verdadeiro. Depois puxei DADO: 13.522.174 bytes de CSV com as colunas "
  "REF_AREA · TYPE_OF_CROP · TIME_PERIOD · OBS_VALUE · UNIT_MEAS. Nao e' "
  "pagina que fala de dado — e' o dado. E ha mais dois: `_2` por provincia e "
  "`_10` intencoes de semeadura."),

 "PORTFOLIO · INTERVALO DE SEGURANCA (PHI) e n.o maximo de aplicacoes": (
  "COLLECTION_CAPABILITY_GAP", "ABERTO — MAS MUDOU DE NATUREZA",
  "Ministero (rotulo PDF) · Fitogest (filtra por tempo di carenza)",
  "`interval 15/219 (7%)` e `maxApp 0/219`. As duas fontes abrem e a segunda "
  "FILTRA por carencia, logo tem o campo. O que falta e' capacidade nossa de "
  "extrair do PDF do rotulo — e a memoria do projeto diz que esses PDF abrem "
  "no urllib. Deixa de ser «procurar fonte» e passa a ser «escrever o "
  "extrator»."),

 "PORTFOLIO · ALTERACAO de autorizacao (o que mudou e quando)": (
  "SOURCE_GAP", "FECHADO",
  "Ministero (descarga diaria, comparavel entre dias) · Bollettini "
  "interprovinciali Emilia-Romagna (derrogas datadas) · convegno de Bolonha",
  "campo ausente no casco. Duas vias abertas e validadas: comparar o "
  "descarregavel diario consigo mesmo, ou ler a derroga publicada com data — "
  "exemplo real medido: Septoria em trigo, uso permitido a partir de "
  "20/03/2026. ⚠️ A derroga e' REGIONAL: vale na Emilia-Romagna, nao em "
  "Italia."),

 "PORTFOLIO · Ligacao produto x janela de cultura": (
  "DATA_MODEL_GAP", "ABERTO — E NAO FECHA COM FONTE",
  "—",
  "`PRODUCT_MATCHES 0/29`. Join entre 219 produtos e 29 janelas, ambos em "
  "casa. Nenhum italiano publica esta ligacao, e nem devia."),

 "VOICES · REGIAO da voz de campo": (
  "SOURCE_GAP", "FECHADO PARA TECNICO, ABERTO PARA PRODUTOR",
  "Bollettini UTM Campania · ARSAC (8 zonas) · CAAR (4 provincias) · ALSIA "
  "(3 comprensori)",
  "`0/17`. Ha agora quatro fontes que escrevem a regiao com granularidade "
  "sub-regional declarada — a UTM da Campania e' unidade de monitorizacao "
  "nomeada. ⚠️ MAS CONTINUA A TROCAR O SUJEITO: e' tecnico institucional, nao "
  "produtor. Se a ferramenta quer o que o produtor do Veneto esta a dizer, "
  "isto nao responde."),

 "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)": (
  "SOURCE_GAP", "FECHADO",
  "CONAF/albo · Emanuele Scalcione (ALSIA, responsavel do SAL) · tecnicos "
  "nomeados no Forum Fitoiatrico",
  "`0/17`. O albo da nome, papel reconhecido e territorio. E a segunda vaga "
  "trouxe um caso exemplar: o boletim semanal da ALSIA e' apresentado por uma "
  "pessoa nomeada com funcao declarada."),

 "VOICES · DATA da observacao de campo": (
  "SOURCE_GAP", "FECHADO PARA TECNICO, ABERTO PARA PRODUTOR",
  "toda a familia de boletins numerados e datados",
  "`0/17`. Exemplos reais medidos nesta missao: «Bollettino 17 del 04 giugno "
  "2026 Reggio Emilia», «n. 8/2026 del 24 giugno 2026», «Boll_09_MAIS_"
  "03072026», avisos da Valle d'Aosta atualizados em 26/06/2026. ⚠️ E as duas "
  "datas nao sao a mesma: publicacao != observacao. O boletim da as duas; a "
  "rede social da so' a primeira."),

 "FUTURE · PRAGA OU DOENCA EMERGENTE (primeira deteccao)": (
  "SOURCE_GAP", "FECHADO",
  "protezionedellepiante.it · Ufficio fitosanitario Valle d'Aosta (rede de "
  "armadilhas) · salutepianteinlombardia.it",
  "campo ausente. A rota nacional abre e valida; e a segunda vaga trouxe a "
  "rede de armadilhas da Valle d'Aosta com servico de previsao e aviso por "
  "quatro canais, incluindo SMS."),

 "FIELD_NET · Relato da rede comercial, com autor e data": (
  "DATA_MODEL_GAP", "ABERTO — E NAO FECHA COM FONTE",
  "—",
  "18 registos, todos `SYNTHETIC_DEMO`. E' dado PROPRIO da ADAMA. Procurar "
  "fonte italiana para isto e' procurar fora o que esta dentro."),

 "RADAR · ENTRADA: janela de cultura com data e regiao": (
  "SOURCE_GAP", "FECHADO NA ORIGEM (WINDOWS)", "= WINDOWS",
  "herda. A entrada melhorou porque a camada de origem melhorou."),
 "RADAR · ENTRADA: ligacao produto x problema": (
  "DATA_MODEL_GAP", "ABERTO NA ORIGEM (PORTFOLIO)", "= PORTFOLIO",
  "herda um join interno. Continua aberto."),
 "RADAR · ENTRADA: voz de campo na mesma cultura/problema": (
  "SOURCE_GAP", "PARCIAL NA ORIGEM (VOICES)", "= VOICES",
  "herda a troca de sujeito: ganha regiao e data de TECNICO, nao de produtor. "
  "⚠️ Continua a ser a entrada mais fraca do Radar."),
 "RADAR · ENTRADA: mercado da mesma cultura": (
  "SOURCE_GAP", "FECHADO NA ORIGEM (MARKET)", "= MARKET",
  "herda. O CSV do ISTAT tem REF_AREA e TYPE_OF_CROP, que e' o que o "
  "cruzamento precisa."),
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cob = json.loads((ANTES / "COBERTURA.json").read_text(encoding="utf-8"))
    criticos = [r for r in cob if r["GAP_SEVERITY"] == "CRITICAL"]
    faltam = {f'{r["TOOL"]} · {r["RAW_NEED"]}' for r in criticos} - set(GAPS)
    if faltam:
        print("!! CRITICOS SEM CLASSIFICACAO:")
        for f in sorted(faltam):
            print("   ", f)
        sys.exit(1)

    linhas = []
    for r in criticos:
        k = f'{r["TOOL"]} · {r["RAW_NEED"]}'
        tipo, estado, quem, porque = GAPS[k]
        linhas.append({
            "TOOL": r["TOOL"], "RAW_NEED": r["RAW_NEED"],
            "GAP_TYPE": tipo,
            "MEDICAO_QUE_PROVA": r["MEDIDO"],
            "ESTADO_DEPOIS": estado,
            "QUEM_FECHA": quem,
            "PORQUE": porque,
            "PROCURAR_MAIS_FONTE_RESOLVE": (
                "SIM" if tipo == "SOURCE_GAP" and "ABERTO" in estado else
                "NAO — ja fechado" if tipo == "SOURCE_GAP" else
                "NAO — " + {"DATA_MODEL_GAP": "e' ligar/escrever em casa",
                            "ACCESS_GAP": "e' contrato, nao coleta",
                            "COLLECTION_CAPABILITY_GAP":
                                "e' capacidade nossa de ler"}[tipo])})

    (TRAB / "GAPS-CRITICOS.json").write_text(
        json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")

    print("OS 15 CRITICOS, POR TIPO")
    print("=" * 96)
    for l in sorted(linhas, key=lambda x: (x["GAP_TYPE"], x["TOOL"])):
        print(f"  {l['GAP_TYPE']:26s} {l['ESTADO_DEPOIS'][:32]:32s} "
              f"{l['TOOL']:11s} {l['RAW_NEED'][:36]}")
    print("=" * 96)
    print("  por tipo:", dict(Counter(l["GAP_TYPE"] for l in linhas)))
    fechados = sum(1 for l in linhas if "FECHADO" in l["ESTADO_DEPOIS"])
    print(f"\n  CRITICAL_GAPS_BEFORE = {len(criticos)}")
    print(f"  fechados ou fechados-na-origem = {fechados}")
    print(f"  CRITICAL_GAPS_AFTER (que ainda pedem fonte) = "
          f"{sum(1 for l in linhas if l['PROCURAR_MAIS_FONTE_RESOLVE'] == 'SIM')}")
    print(f"  que NAO fecham com fonte nenhuma = "
          f"{sum(1 for l in linhas if l['GAP_TYPE'] != 'SOURCE_GAP')}")


if __name__ == "__main__":
    main()
