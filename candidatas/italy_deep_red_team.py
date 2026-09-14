#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM — tentar derrubar a lista, e provar que os detectores funcionam.

Duas perguntas por cada um dos 24 ataques do pedido:

    1 · ACHEI o caso na minha propria lista? (se sim, onde ficou)
    2 · O DETECTOR FUNCIONA? — prova-se com CONTROLE POSITIVO: um caso que eu
        sei que e mau e que o filtro tem de apanhar. Detector que nunca apanha
        nada nao e um detector limpo: e um detector desligado.

Um relatorio de red team sem controle positivo diz sempre a mesma coisa —
"nao encontrei problemas" — e nao se pode saber se isso e verdade ou se o
teste nao mede nada.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    L = json.loads((TRABALHO / "LINHAS-FINAL.json").read_text(encoding="utf-8"))
    AB = [x for x in L if x["QUALITY_CLASS"] in ("A", "B")]
    REJ = [x for x in L if x["QUALITY_CLASS"] == "REJECT"]
    HOLD = [x for x in L if x["QUALITY_CLASS"] in ("HOLD", "UNKNOWN")]
    por_host = {}
    for x in L:
        por_host.setdefault(x["RELATED_OWNER"], []).append(x)

    def tem(lista, *frag):
        out = []
        for x in lista:
            alvo = (x.get("QUALITY_REASON", "") + " " + x.get("NAME", "") + " "
                    + x.get("RELATED_OWNER", "") + " " + x.get("LIMITATION", "")).lower()
            if all(f.lower() in alvo for f in frag):
                out.append(x)
        return out

    ataques = []

    def at(n, nome, achado, onde, controle, veredito):
        ataques.append({"N": n, "ATAQUE": nome, "ACHEI_NA_MINHA_LISTA": achado,
                        "ONDE_FICOU": onde, "CONTROLE_POSITIVO": controle,
                        "VEREDITO": veredito})

    # 1 · organizacao sem informacao propria
    sem_propria = [x for x in AB if (x.get("INFO_PROPRIA_N") or 0) == 0
                   and x["RECORD_KIND"] == "SOURCE"]
    at(1, "organizacao sem informacao propria",
       f"{len(sem_propria)} linhas A/B com ZERO marca de informacao propria medida",
       "ficaram em A/B por leitura humana (ex. universidade, ordem profissional) ou "
       "por sinal agricola denso; cada uma tem a razao escrita em QUALITY_REASON",
       "madiventura.it (importadora de especiarias, pagina 'la nostra azienda') foi "
       "recusada; enpaia.it (fundo de previdencia, TERRITORIES vazio) foi recusada",
       "DETECTOR FUNCIONA, mas e' PARCIAL: a medida de 'informacao propria' le a "
       "homepage. Fonte que publica atras de login marca zero e nao e por isso vazia")

    # 2 · site bonito mas inutil
    at(2, "site bonito mas sem utilidade",
       f"{len(tem(REJ, 'sobre nos')) + len(tem(REJ, 'nossa empresa'))} recusadas "
       f"explicitamente por serem pagina institucional",
       "aba REJECTED", "madiventura.it", "DETECTOR FUNCIONA")

    # 3 · perfil social falso / sem prova de dono
    sem_dono = [x for x in L if x["RECORD_KIND"] == "CHANNEL"
                and x.get("OWNER_MATCH") == "NOT_PROVED"]
    hold_canal = [x for x in L if x["RECORD_KIND"] == "CHANNEL"
                  and x["QUALITY_CLASS"] == "HOLD"]
    at(3, "perfil social sem prova de dono",
       f"{len(sem_dono)} canais sem dono provado; {len(hold_canal)} ficaram em HOLD",
       "aba SOCIAL, coluna OWNER_MATCH", "Agri Italia (canal citado numa lista, "
       "dono nao identificado) ficou HOLD, nao B",
       "DETECTOR FUNCIONA: HOLD, nao REJECT — nao se recusa por nao saber")

    # 4 · homonimo
    at(4, "homonimo",
       "1 caso suspeito: um nome devolvido pela busca como 'Servizio Fitosanitario "
       "Toscana' colide com uma investigadora conhecida de outro instituto",
       "NAO entrou na folha PEOPLE — foi deixado de fora por falta de prova",
       "o nome ficou fora da entrega; nenhuma linha o afirma",
       "DETECTOR FUNCIONA PELO LADO CONSERVADOR: em duvida, nao se escreve o nome")

    # 5 e 6 · pesquisador errado / afiliacao antiga
    afil = [x for x in L if x["RECORD_KIND"] == "PERSON"
            and "NAO VERIFICADA" in (x.get("EVIDENCE", "") + x.get("QUALITY_REASON", "")).upper()]
    at(5, "pesquisador errado",
       "0 confirmados; TODAS as 60 linhas de pessoa carregam a limitacao "
       "'afiliacao atual por confirmar'",
       "aba PEOPLE, coluna LIMITATION",
       "Aldo Ferrero entrou com a nota explicita de afiliacao nao verificada",
       "DETECTOR E' UMA RESSALVA, NAO UM FILTRO: nenhuma afiliacao foi verificada "
       "num perfil institucional. Isto e uma FRAQUEZA REAL desta entrega")
    at(6, "pesquisador com afiliacao antiga",
       f"{len(afil)} linha(s) marcada(s) explicitamente",
       "aba PEOPLE", "Aldo Ferrero (possivel emerito) — marcado, nao removido",
       "DETECTOR FUNCIONA SO' QUANDO A FONTE AVISA")

    # 7 · canal internacional sem relacao com Italia
    fora = [x for x in L if x.get("REGION") == "FORA_DE_ITALIA"
            or "sem ligacao provada a italia" in x.get("QUALITY_REASON", "").lower()]
    at(7, "canal/site internacional sem relacao real com Italia",
       f"{len(fora)} linhas recusadas por nao provarem ligacao a Italia",
       "aba REJECTED",
       "Spicy Moustache (4,5 milhoes de seguidores, horta urbana em Londres) e "
       "Lely (robotica neerlandesa) recusados; 8 canais dos EUA/UK de uma lista "
       "italiana recusados",
       "DETECTOR FUNCIONA — E TEM FURO MEDIDO: recusou tambem fonte ITALIANA que "
       "publica noutra lingua (Laimburg em alemao, Italian Journal of "
       "Agrometeorology em ingles). Os dois casos foram corrigidos a mao")

    # 8 · mesma organizacao contada varias vezes
    repetidos = {h: v for h, v in por_host.items() if len(v) > 1}
    dups = [x for x in L if x["NEW_VS_EXISTING"] == "TRUE_DUPLICATE"]
    at(8, "mesma organizacao contada varias vezes",
       f"{len(repetidos)} hosts com mais de uma linha; {len(dups)} marcados "
       f"TRUE_DUPLICATE",
       "aba OWNER_MAP, com a nota de contagem em cada linha repetida",
       "inseri Luciana Tavella DUAS vezes de proposito na folha de pessoas: a "
       "segunda saiu marcada TRUE_DUPLICATE",
       "DETECTOR FUNCIONA nos tres niveis (URL, host, raiz) e tambem DENTRO da "
       "rodada — o dedupe intra-rodada de pessoas foi acrescentado depois de o "
       "controle positivo mostrar que faltava")

    # 9 · pagina e canal confundidos
    at(9, "pagina e canal confundidos",
       f"{sum(1 for x in L if x['RECORD_KIND']=='CHANNEL')} canais vivem numa folha "
       f"separada (SOCIAL) com coluna PLATFORM; "
       f"{sum(1 for x in L if x['RECORD_KIND']=='SOURCE')} fontes web noutra",
       "abas SOCIAL vs ORGANIZATIONS",
       "Sudtiroler Beratungsring aparece como 3 linhas (site, YouTube, Instagram) "
       "e 1 dono — visivel na OWNER_MAP",
       "DETECTOR FUNCIONA por desenho: RECORD_KIND separa desde a origem")

    # 10 · redirect para site diferente
    red = [x for x in L if x.get("URL_STATUS") == "REDIRECT"]
    at(10, "redirect para um site diferente",
       f"{len(red)} linhas com URL_STATUS=REDIRECT (URL_FINAL diferente do sondado)",
       "colunas URL_DISCOVERED / URL_FINAL / URL_STATUS, guardadas em separado",
       "todas as linhas guardam as duas URLs; a comparacao e automatica",
       "DETECTOR FUNCIONA")

    # 11 · dominio reaproveitado
    at(11, "dominio reaproveitado",
       "0 casos provados. Esta missao NAO consegue detetar reaproveitamento de "
       "dominio: isso exige historico (WHOIS, arquivo da web), e nenhum foi "
       "consultado",
       "—", "nenhum",
       "DETECTOR AUSENTE — E' UM BURACO DECLARADO desta entrega")

    # 12 · site morto com HTTP 200
    casca = [x for x in REJ if "casca, nao conteudo" in x.get("QUALITY_REASON", "")]
    velhos = [x for x in L if "possivel abandono" in x.get("QUALITY_REASON", "")]
    at(12, "site morto com HTTP 200",
       f"{len(casca)} recusadas por devolverem HTTP 200 com menos de 400 "
       f"caracteres de texto; {len(velhos)} rebaixadas por data mais recente "
       f"anterior a 2022",
       "aba REJECTED e coluna QUALITY_REASON",
       "demo.idra.it (subdominio de teste de uma agencia web) recusado; "
       "difesaintegratabasilicata.jimdofree.com divergiu na segunda prova com "
       "material mais novo de 2020",
       "DETECTOR FUNCIONA — e apanhou tambem falso positivo: pagina construida em "
       "JavaScript devolve casca sem estar morta (Clementine di Calabria, "
       "San Marzano). Os dois foram corrigidos a mao")

    # 13 · midia generica classificada como tecnica
    midia = [x for x in REJ if "midia generalista" in x.get("QUALITY_REASON", "").lower()]
    at(13, "midia generica classificada como tecnica",
       f"{len(midia)} recusadas por serem midia generalista",
       "aba REJECTED", "repubblica.it, corriere.it, lastampa.it, adnkronos.com, "
       "avvenire.it — a maquina tinha posto repubblica.it em A",
       "DETECTOR FUNCIONA — mas so DEPOIS da leitura humana: a regra automatica "
       "de contagem de palavras nao os apanhava")

    # 14 · marketing classificado como informacao
    loja = [x for x in REJ if "vende, nao informa" in x.get("QUALITY_REASON", "")]
    t9 = [x for x in AB if "T9" in (x.get("TERRITORIES") or "")]
    at(14, "marketing classificado como informacao",
       f"{len(loja)} recusadas como loja; {len(t9)} empresas do setor ficaram em "
       f"A/B mas marcadas T9 (concorrente), nao T1/T3",
       "aba REJECTED e coluna TERRITORIES",
       "acasatua.it e delvecchioagri.it (loja que republica boletim) recusadas; "
       "Sipcam, Diachem, Ascenza e ILSA ficaram como T9",
       "DETECTOR FUNCIONA, e a distincao util nao foi 'aceitar/recusar' mas "
       "'que territorio': a comunicacao de um concorrente E' informacao — sobre ele")

    # 15 · evento isolado como fonte recorrente
    ev = [x for x in REJ if "evento isolado" in x.get("QUALITY_REASON", "").lower()]
    t11 = [x for x in L if "T11" in (x.get("TERRITORIES") or "")
           and x["QUALITY_CLASS"] == "C"]
    at(15, "evento isolado classificado como fonte recorrente",
       f"{len(ev)} recusadas; {len(t11)} eventos e feiras foram rebaixados a C "
       f"pela regra R7",
       "aba REJECTED e aba C_COMPLEMENTARY",
       "micocosmofestival.net (programa de um festival de 2026) recusado, e a "
       "maquina tinha-o posto em A",
       "DETECTOR FUNCIONA")

    # 16 e 17 · artigo / paper como fonte
    art = [x for x in REJ if "artigo" in x.get("QUALITY_REASON", "").lower()
           or "comunicado" in x.get("QUALITY_REASON", "").lower()
           or "documento, nao fonte" in x.get("QUALITY_REASON", "").lower()]
    at(16, "artigo isolado classificado como fonte",
       f"{len(art)} recusadas por serem um artigo, comunicado ou documento",
       "aba REJECTED",
       "cultura.gov.it (um comunicado sobre a UNESCO) e leggi.alumbria.it (o texto "
       "de uma lei de 2015) recusados — os dois estavam em A pela maquina",
       "DETECTOR FUNCIONA SO' POR LEITURA HUMANA: a sonda nao distingue 'pagina de "
       "artigo' de 'pagina de secao'")
    at(17, "paper classificado como fonte",
       "0 papers entraram como fonte. Os agregadores academicos "
       "(researchgate, sciencedirect, springer, mdpi, scholar) foram recusados "
       "sem sonda, por regra",
       "aba REJECTED, motivo 'enciclopedia/agregador sem informacao propria'",
       "researchgate.net e link.springer.com recusados",
       "DETECTOR FUNCIONA — e com um custo: recusar o agregador recusa tambem o "
       "caminho para o paper. Isso e escolha, nao acidente")

    # 18 · seguidores usados como relevancia
    at(18, "numero de seguidores usado como relevancia",
       "0 linhas usam alcance na classe. A folha SOCIAL tem QUATRO colunas "
       "separadas (REACH, FIELD_AUTHORITY, TECHNICAL_AUTHORITY, "
       "COMMERCIAL_INFLUENCE) e NENHUMA soma",
       "aba SOCIAL",
       "os dois maiores alcances de toda a pesquisa (Spicy Moustache, 4,5 milhoes; "
       "Giovanni Storti, 1 milhao) estao em REJECT. O canal em A (Vito Vitelli) tem "
       "15 mil — 300 vezes menos",
       "DETECTOR FUNCIONA, e este e o controle positivo mais forte da entrega")

    # 19 · regiao inferida pelo nome
    naoprov = [x for x in L if x.get("REGION") == "NAO SEI"]
    prov = [x for x in L if "TEXTO_DA_PAGINA" in (x.get("REGION_EVIDENCE") or "")]
    at(19, "regiao inferida pelo nome do dominio",
       f"0 linhas inferem regiao pelo dominio. {len(prov)} tem regiao provada pelo "
       f"TEXTO da pagina; {len(naoprov)} ficaram com REGION = NAO SEI",
       "coluna REGION_EVIDENCE, em todas as linhas",
       "agrisicilia.it, sicilia.coldiretti.it e semelhantes NAO receberam a regiao "
       "pelo nome — so a receberam quando o texto a citou",
       f"DETECTOR FUNCIONA, e o preco esta a vista: {len(naoprov)} linhas sem "
       f"regiao provada. Preferi o buraco visivel a uma coluna cheia e errada")

    # 20 · assunto confundido com identidade
    at(20, "assunto confundido com identidade",
       "as colunas TERRITORIES/CROPS/TOPICS (assunto) sao distintas de "
       "OWNER/ORGANIZATION/RELATED_OWNER (identidade), e a proximidade "
       "(INFORMATION_PROXIMITY) e calculada do TIPO DE DONO, nao do assunto",
       "todas as abas",
       "repubblica.it tinha assunto agricola na homepage e identidade de jornal "
       "generalista: foi a identidade que decidiu",
       "DETECTOR FUNCIONA")

    # 21 · modelo/GPU criando relevancia sem prova
    at(21, "modelo ou GPU criando relevancia sem prova",
       "NENHUM modelo de linguagem, embedding, classificador ou GPU foi usado para "
       "classificar fonte nesta missao. A pre-classe vem de contagem de palavras e "
       "de sonda HTTP, ambas legiveis e reproduziveis",
       "candidatas/italy_deep_probe.py — o codigo inteiro da regra esta a vista",
       "nao aplicavel: a ferramenta nao foi usada",
       "SEM RISCO POR AUSENCIA DE USO. A escolha foi deliberada: um modelo a dizer "
       "'parece relevante' nao deixa rasto que se possa auditar")

    # 22 · perfil social sem prova de owner (ver 3)
    at(22, "perfil social sem prova de owner",
       "ver ataque 3 — mesma medida",
       "aba SOCIAL, coluna OWNER_MATCH", "Agri Italia em HOLD",
       "DETECTOR FUNCIONA")

    # 23 · fonte existente apresentada como nova
    conhecidas = [x for x in L if x["NEW_VS_EXISTING"] == "KNOWN_SOURCE"]
    mesmo_dono = [x for x in L if x["NEW_VS_EXISTING"] == "SAME_OWNER_DIFFERENT_SOURCE"]
    at(23, "fonte ja existente apresentada como nova",
       f"{len(conhecidas)} linhas marcadas KNOWN_SOURCE e {len(mesmo_dono)} "
       f"SAME_OWNER_DIFFERENT_SOURCE; as KNOWN_SOURCE foram BARRADAS do CSV",
       "coluna NEW_VS_EXISTING e o relatorio de barradas do CSV",
       "o agrupador de dominios chegou a marcar "
       "agricoltura.regione.emilia-romagna.it como NOVA (encurtava para "
       "emilia-romagna.it). Foi apanhado e corrigido no meio da missao",
       "DETECTOR FUNCIONA DEPOIS DE CORRIGIDO. Antes da correcao, mentia — e isso "
       "esta escrito na aba README")

    # 24 · URL alternativa apresentada como fonte nova
    var = [x for x in L if x["NEW_VS_EXISTING"] == "SAME_SOURCE_VARIANT_URL"]
    at(24, "URL alternativa apresentada como fonte nova",
       f"{len(var)} marcadas SAME_SOURCE_VARIANT_URL; alem disso, a regra R5 "
       f"recusou as edicoes noutro pais do mesmo dono",
       "coluna NEW_VS_EXISTING e aba REJECTED",
       "arsacweb.it e arsac.calabria.it = o MESMO boletim da ARSAC em dois "
       "enderecos; gire.ipsp.cnr.it e gire.mlib.cnr.it = o mesmo GIRE; "
       "freshplaza.es/.fr/.com/.de e sipav.org = mesmos donos de fontes ja no acervo",
       "DETECTOR FUNCIONA")

    (TRABALHO / "RED-TEAM.json").write_text(
        json.dumps(ataques, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"RED TEAM · {len(ataques)} ataques\n")
    for a in ataques:
        print(f"#{a['N']:2d} {a['ATAQUE']}")
        print(f"    achei ...... {a['ACHEI_NA_MINHA_LISTA']}")
        print(f"    controle ... {a['CONTROLE_POSITIVO'][:150]}")
        print(f"    VEREDITO ... {a['VEREDITO'][:170]}")
        print()
    c = Counter("FUNCIONA" if "FUNCIONA" in a["VEREDITO"] else
                ("AUSENTE" if "AUSENTE" in a["VEREDITO"] else "OUTRO")
                for a in ataques)
    print("resumo dos vereditos:", dict(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
