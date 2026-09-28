#!/usr/bin/env python3
"""REROUTE-T1T2 · a LEITURA do que a regua T5 C1 tira dos 158 T5 de ANTES de 28/09 (os 22 de 28/09 tem
os rotulos do LAB). Le REPLAY-T5-C1.json, junta a leitura abaixo e escreve LEITURA-SAI-T5-C1.json.

QUEM LEU: o agente desta missao (modelo), item a item, pelo titulo e as primeiras linhas do texto do export.
HUMAN_REVIEW = NOT_DONE (D110). Criterio (o mesmo do LAB, CRITERIO-ROTULO-V1.md, resumido):
  UTIL        ciencia ou tecnica com assunto agro (cultura, praga, doenca, producao agricola)
  DISCUTIVEL  agro ou agro-alimentar, mas evento/curso/institucional, ou fronteira (floresta, zootecnia...)
  NAO         sem assunto agro (administracao universitaria, repositorio, outro dominio)

    py provas/reroute_t1t2/leitura_sai_t5_c1.py  -> provas/reroute_t1t2/LEITURA-SAI-T5-C1.json
"""
import collections
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# item -> (rotulo, porque, por que regra de C1 sai)
LEITURA = {
    "derived:23": ("DISCUTIVEL", "livro de testemunhos de ex-alunos de Agraria (Pisa); nao e estudo nem assunto de campo"),
    "derived:24": ("NAO", "linhas-guia de internacionalizacao de cursos"),
    "derived:25": ("NAO", "interface do repositorio AIR (docentes)"),
    "derived:26": ("NAO", "politica de acesso aberto da Universidade de Bolonha"),
    "derived:27": ("NAO", "guia do arquivo institucional de Padua"),
    "derived:28": ("NAO", "manual do 'desktop prodotti' (UniTo)"),
    "derived:29": ("NAO", "call for papers sobre learning outcomes (educacao)"),
    "derived:30": ("NAO", "selecao de tutores para estudantes com deficiencia"),
    "derived:31": ("NAO", "plano operativo do departamento de biotecnologias (Verona), administrativo"),
    "derived:56": ("DISCUTIVEL", "workshop IBBR-CNR (biociencias e biorrecursos): evento, pagina quase toda menu"),
    "derived:57": ("DISCUTIVEL", "summer school LCA de sistemas zootecnicos: agro (pecuaria), mas curso; o LAB citou-o"),
    "derived:58": ("UTIL", "projeto INNOFLORENERG (floricultura sustentavel, Sant'Anna): agro, sem cultura da lista"),
    "derived:59": ("NAO", "pagina de departamento de Padua, so menu"),
    "derived:60": ("NAO", "delegados de departamento"),
    "derived:61": ("NAO", "cibermafias (policia postal)"),
    "derived:62": ("DISCUTIVEL", "dia internacional do desperdicio alimentar (Agro-Alimentari, Bolonha): evento"),
    "derived:126": ("NAO", "FAQ do repositorio FLORE"),
    "derived:128": ("UTIL", "INNOFLORENERG (outra copia do mesmo projeto)"),
    "derived:129": ("NAO", "pagina de departamento de Padua, so menu (outra copia)"),
    "derived:130": ("NAO", "cibermafias (outra copia)"),
    "derived:142": ("NAO", "aulas e exames, Agraria Napoles (administrativo)"),
    "derived:143": ("NAO", "avisos de exames, Catania (administrativo)"),
    "derived:794": ("NAO", "kit contra ansiedade de exames"),
    "derived:795": ("NAO", "welcome day"),
    "derived:796": ("NAO", "avisos de aulas"),
    "derived:918": ("NAO", "eventos das sociedades cientificas (Istat)"),
    "derived:963": ("NAO", "CREA 'Infrastrutture di ricerca': pagina de menu"),
    "derived:964": ("DISCUTIVEL", "CREA curso de analise sensorial do mel (apicultura): agro, mas curso"),
    "derived:966": ("NAO", "ENEA: radiacao UV em Lampedusa"),
    "derived:967": ("NAO", "ENEA: premio inovadores responsaveis"),
    "derived:968": ("NAO", "ENEA: noite dos investigadores"),
    "derived:1018": ("DISCUTIVEL", "CREA e INRAE reforcam o eixo cientifico agroalimentar: institucional"),
    "derived:1019": ("UTIL", "CREA: colecao cientifica internacional sobre viticultura sustentavel"),
    "derived:1022": ("NAO", "ENEA: meetings internacionais"),
    "derived:1024": ("NAO", "ENEA: workshop DAPHNE de modelos atmosfericos"),
    "derived:1129": ("NAO", "ENEA: previsao de correntes marinhas para a America's Cup"),
    "derived:1242": ("NAO", "Fitto com estudantes (educacao civica)"),
    "derived:1244": ("UTIL", "INNOFLORENERG em ingles (floricultura)"),
    "derived:1245": ("NAO", "novos socios dos Lincei"),
    "derived:1246": ("NAO", "Internet Festival 2026"),
    "https://doi.org/10.1002/jsfa.11814": ("UTIL", "fungicidas naturais contra mildio da videira"),
    "https://doi.org/10.1002/ps.6860": ("UTIL", "Plasmopara viticola, estrategias sustentaveis"),
    "https://doi.org/10.1002/ps.8140": ("UTIL", "biocontrolo de Botrytis na vinha"),
    "https://doi.org/10.1017/s0007485319000075": ("UTIL", "Trichoderma e silica na defesa da videira contra insetos"),
    "https://doi.org/10.1055/s-0045-1814921": ("UTIL", "vesiculas extracelulares planta-fungo"),
    "https://doi.org/10.1055/s-0045-1814968": ("UTIL", "Salvia contra patogenos de plantas"),
    "https://doi.org/10.1093/jxb/erac286": ("DISCUTIVEL", "fenotipagem de plantas (producao de culturas em geral)"),
    "https://doi.org/10.1094/phyto-04-26-0103-r": ("UTIL", "videira e fitoplasma da flavescencia dourada"),
    "https://doi.org/10.30574/gscarr.2020.4.2.0059": ("UTIL", "zeolitos na protecao do tomateiro"),
    "https://doi.org/10.30574/ijsra.2023.9.2.0637": ("UTIL", "zeolito na protecao da videira"),
    "https://doi.org/10.35948/geo/geoinfo/32130_3540": ("UTIL", "resistencia de Diabrotica ao milho Bt (EUA)"),
    "https://doi.org/10.5194/egusphere-egu22-10511": ("UTIL", "drones para pragas e doencas em macieira e vinha"),
    "https://doi.org/10.5281/zenodo.4319469": ("UTIL", "zeolitos no tomateiro (outra copia do mesmo artigo)"),
}


def main() -> int:
    rep = json.loads((AQUI / "REPLAY-T5-C1.json").read_text(encoding="utf-8"))
    antes = [l for l in rep["ITENS"] if not l["DE_28_09"]]
    fora, falta = [], []
    for l in antes:
        sai = {k: l[k] != "SIM" for k in ("CORPO_ESTRITO", "CORPO_SENAO_INTEIRO", "TEXTO_INTEIRO")}
        if not any(sai.values()):
            continue
        if l["ITEM"] not in LEITURA:
            falta.append(l["ITEM"])
            continue
        rot, porque = LEITURA[l["ITEM"]]
        fora.append({"ITEM": l["ITEM"], "SOURCE_ID": l["SOURCE_ID"], "ROTULO": rot, "PORQUE": porque,
                     "SAI_EM": [k for k, v in sai.items() if v],
                     "MOTIVO_TEXTO_INTEIRO": l["TEXTO_INTEIRO_MOTIVO"],
                     "MOTIVO_CORPO_ESTRITO": l["CORPO_ESTRITO_MOTIVO"],
                     "PALAVRAS_T5_ANTES": l["ANTES_PALAVRAS"], "PALAVRAS_T5_INICIO": l["PALAVRAS_T5_INICIO"]})
    if falta:
        raise SystemExit("itens que saem sem leitura: %s" % falta)
    conta = {}
    for leitura in ("CORPO_ESTRITO", "CORPO_SENAO_INTEIRO", "TEXTO_INTEIRO"):
        c = collections.Counter(x["ROTULO"] for x in fora if leitura in x["SAI_EM"])
        conta[leitura] = dict(sorted(c.items()))
    util_texto = [x for x in fora if x["ROTULO"] == "UTIL" and "TEXTO_INTEIRO" in x["SAI_EM"]]
    out = {"LEITURA": "LEITURA-SAI-T5-C1", "QUEM_LEU": "agente da missao REROUTE-T1T2 (modelo)",
           "HUMAN_REVIEW": "NOT_DONE (D110)", "LINHAS_QUE_SAEM": len(fora),
           "ROTULOS_DO_QUE_SAI_POR_LEITURA": conta,
           "UTIL_PERDIDO_TEXTO_INTEIRO": [{"ITEM": x["ITEM"], "PORQUE": x["PORQUE"],
                                           "MOTIVO": x["MOTIVO_TEXTO_INTEIRO"],
                                           "PALAVRAS_T5": [x["PALAVRAS_T5_ANTES"], x["PALAVRAS_T5_INICIO"]]}
                                          for x in util_texto],
           "ITENS": fora}
    (AQUI / "LEITURA-SAI-T5-C1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                  encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("LINHAS_QUE_SAEM", "ROTULOS_DO_QUE_SAI_POR_LEITURA",
                                          "UTIL_PERDIDO_TEXTO_INTEIRO")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
