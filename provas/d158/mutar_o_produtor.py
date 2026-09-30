#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS MUTANTES DO PRODUTOR DE AFIRMACOES (D158) — cada garantia, atacada uma vez.

    py provas/d158/mutar_o_produtor.py [--saida MUTACAO-PRODUTOR-V1.json]

COMO SE MEDE
------------
A arvore commitada sai por `git archive` para uma copia descartavel. Em cada rodada UMA
troca de texto entra na copia — e so uma —, e a bateria do produtor corre LA DENTRO. O
mutante MORRE se a bateria reprovar. Um mutante que SOBREVIVE nao e um erro do mutante: e
uma garantia que ninguem esta a guardar, e sai na entrega com o nome.

O que se ataca (uma linha por garantia):
    1  o trecho deixa de ser texto[inicio:fim]        — a prova deixa de ser prova
    2  o ASSERTION_ID deixa de olhar o offset          — dois trechos, um nome so
    3  o ASSERTION_ID deixa de olhar o byte do RAW     — outro documento, mesmo nome
    4  a conferencia deixa de comparar o trecho        — o portao abre-se
    5  a conferencia deixa de olhar o RAW_SHA256       — documento alterado passa
    6  a conferencia deixa de olhar o BASIS do tempo   — data sem prova passa
    7  qualquer PAPEL vira tempo do facto              — validade/previsao viram facto
    8  o PERIODO_DA_EDICAO vira ACONTECIMENTO          — a edicao vira o facto
    9  o periodo futuro vira ACONTECIMENTO             — previsao vira observacao
   10  a D147 deixa de exigir «sem concorrente»        — compoe na duvida
   11  a D147 deixa de exigir o papel do cabecalho     — herda de qualquer cabecalho
   12  a D147 deixa de recusar conselho e futuro       — recomendacao herda a data
   13  a D149 deixa de comparar impresso x conta       — duas datas, escolhe uma
   14  `desdobrar` aceita qualquer linha               — cabecalho inventado
   15  a virgula que emenda deixa de cortar            — duas afirmacoes num trecho so
   16  a memoria de leitura passa a responder a todos  — um documento responde por outro

O BLOQUEADOR do Intelligence owner e os dois defeitos que ele mediu (§5-C do contrato):
   17  dois tempos no trecho, escolhe um                — o par tempo+lugar volta a ser falso
   18  dois lugares no trecho, escolhe um              — idem, pelo lado do lugar
   19  a contagem de TEMPOS nao viaja                   — a Intelligence cega
   20  a contagem de LUGARES nao viaja                  — idem
   21  o intervalo passa a contar dois                  — a janela de validade morre
   22  o hifen deixa de ser espaco                      — «Emilia Romagna» nao e contada
   23  a area supranacional deixa de contar             — «Europa» nao concorre
   24  a data escrita volta a ser RELATIVO_D63          — a origem mente
   25  compara TEXTO em vez do DIA                      — «12 novembre 2026» != «2026-11-12»
   26  a loja volta a nao ser mercado                   — a visita vira ALERTA_EVENTO
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BATERIA = "tests/test_o_produtor_de_afirmacoes.py"

#: (nome, ficheiro, o que estava la, o que passa a estar)
MUTANTES = [
    ("TRECHO_DEIXA_DE_SER_O_TEXTO", "leis/afirmacao_do_documento.py",
     '                "TRECHO_LITERAL": span,', '                "TRECHO_LITERAL": span[1:],'),
    ("ID_NAO_OLHA_O_OFFSET", "leis/afirmacao_do_documento.py",
     'str(int(inicio)), str(int(fim)), str(trecho)])',
     'str(trecho)])'),
    ("ID_NAO_OLHA_O_BYTE_DO_RAW", "leis/afirmacao_do_documento.py",
     'str(raw_sha256 or NAO_SEI),', ''),
    ("CONFERENCIA_NAO_COMPARA_O_TRECHO", "leis/afirmacao_do_documento.py",
     '    if trecho != t[a:b]:', '    if False:'),
    ("CONFERENCIA_NAO_OLHA_O_RAW_SHA256", "leis/afirmacao_do_documento.py",
     '    if raw_sha256 is not None and prov.get("RAW_SHA256") not in (NAO_SEI, raw_sha256):',
     '    if False:'),
    ("CONFERENCIA_NAO_OLHA_O_BASIS", "leis/afirmacao_do_documento.py",
     '        elif basis.get("TRECHO") != t[basis.get("INICIO", -1):basis.get("FIM", -1)]:',
     '        elif False:'),
    ("QUALQUER_PAPEL_E_FACTO", "leis/tempo_da_afirmacao.py",
     'PAPEL_QUE_E_FACTO = (ACONTECIMENTO,)', 'PAPEL_QUE_E_FACTO = PAPEIS'),
    ("EDICAO_VIRA_ACONTECIMENTO", "leis/tempo_da_afirmacao.py",
     '        return PERIODO_DA_EDICAO, "periodo no cabecalho do proprio boletim: diz de que dias a EDICAO fala"',
     '        return ACONTECIMENTO, "periodo no cabecalho do proprio boletim"'),
    ("FUTURO_VIRA_ACONTECIMENTO", "leis/tempo_da_afirmacao.py",
     '        return PREVISAO, "o periodo comeca depois da publicacao provada: ainda nao aconteceu"',
     '        return ACONTECIMENTO, "o periodo comeca depois da publicacao provada"'),
    ("D147_SEM_A_CONDICAO_DO_CONCORRENTE", "leis/tempo_da_afirmacao.py",
     '    if len(periodos) != 1:', '    if not periodos:'),
    ("D147_SEM_O_PAPEL_DO_CABECALHO", "leis/tempo_da_afirmacao.py",
     '    if papel != ACONTECIMENTO:', '    if False:'),
    ("D147_SEM_A_RECUSA_DO_CONSELHO", "leis/tempo_da_afirmacao.py",
     '    conselho = fala_de_acontecimento(span)', '    conselho = None'),
    ("D149_NAO_COMPARA_IMPRESSO_COM_A_CONTA", "leis/tempo_da_afirmacao.py",
     '            if p["VALOR"] == c["fact_time"]:', '            if True:'),
    ("DESDOBRAR_ACEITA_TUDO", "leis/tempo_da_afirmacao.py",
     '        if any(p[i] != p[i + 1] for i in range(0, len(p), 2)):\n            return None',
     '        if False:\n            return None'),
    ("A_VIRGULA_QUE_EMENDA_DEIXA_DE_CORTAR", "leis/afirmacao_do_documento.py",
     '                     | {m.start() + 1 for m in _RE_VIRGULA_QUE_EMENDA.finditer(t, ini, fim)}',
     '                     | set()'),
    # ── os mutantes que o CONTRATO DE CONSUMO da Intelligence exige (§4) ─────
    ("FACT_TIME_VIRA_A_PUBLICACAO", "leis/afirmacao_do_documento.py",
     '            fact_time = (tempo["VALOR"] if e_facto',
     '            fact_time = (prov.get("PUBLISHED_AT") if e_facto'),
    ("FACT_LOCATION_VIRA_O_LUGAR_DA_FONTE", "leis/afirmacao_do_documento.py",
     '    return {"VALOR": NAO_SEI if valor == UNRESOLVED else valor,',
     '    return {"VALOR": "SOURCE_LOCATION" if valor == UNRESOLVED else valor,'),
    ("SPAN_SEM_O_NOME_NO_TRECHO", "leis/afirmacao_do_documento.py",
     '        ok, porque = AF.procedencia_da_entidade(e["ENTITY_SOURCE"], nome_no_trecho=no_trecho)',
     '        ok, porque = AF.procedencia_da_entidade(e["ENTITY_SOURCE"], nome_no_trecho=True)'),
    ("O_PRODUTOR_ESCREVE_LIBERADO", "leis/afirmacao_do_documento.py",
     '                "CONTRATO": CONTRATO,\n                # ── identidade e lineage',
     '                "CONTRATO": CONTRATO,\n                "LIBERACAO": "LIBERADO_PARA_CLIENTE",\n                # ── identidade e lineage'),
    ("CLAIM_ID_DEIXA_DE_SER_O_ASSERTION_ID", "leis/afirmacao_do_documento.py",
     '                "CLAIM_ID": oid,', '                "CLAIM_ID": oid + "-x",'),
    ("EVIDENCE_SPAN_NAO_BATE_COM_O_TEXTO", "leis/afirmacao_do_documento.py",
     '"EVIDENCE_SPAN": {"INICIO": a, "FIM": b, "TRECHO": span, "SHA256": sha_do_trecho(span)},',
     '"EVIDENCE_SPAN": {"INICIO": a, "FIM": b, "TRECHO": span[1:], "SHA256": sha_do_trecho(span)},'),
    ("A_CLASSE_SAI_DO_VOCABULARIO_FECHADO", "leis/afirmacao_do_documento.py",
     '        return {"VALOR": marcas[0], "MARCAS": marcas,',
     '        return {"VALOR": "CLASSE_" + marcas[0], "MARCAS": marcas,'),
    ("A_CLASSE_ESCOLHE_UMA_DE_DUAS", "leis/afirmacao_do_documento.py",
     '    if len(marcas) > 1:', '    if False:'),
    # ── as tres condicoes do Intelligence owner (§5-B: C1, C2, C3) ─────────
    ("A_D149_CHAMA_SE_LITERAL", "leis/tempo_da_afirmacao.py",
     'ORIGEM=RELATIVA_ANCORADA_D149,', 'ORIGEM=LITERAL,'),
    ("O_CABECALHO_CHAMA_SE_LITERAL", "leis/tempo_da_afirmacao.py",
     'ORIGEM=CABECALHO_D147, BASIS=p["BASIS"],', 'ORIGEM=LITERAL, BASIS=p["BASIS"],'),
    ("A_CONFERENCIA_ACEITA_LITERAL_COM_BASIS_DE_FORA", "leis/afirmacao_do_documento.py",
     '        elif origem == TA.LITERAL and not (a <= basis["INICIO"] and basis["FIM"] <= b):',
     '        elif False:'),
    ("O_LUGAR_VIAJA_SEM_PRECISAO", "leis/afirmacao_do_documento.py",
     '            "PRECISAO": l_.get("PRECISAO") or "NOT_KNOWN",', '            "PRECISAO": None,'),
    ("O_LUGAR_VIAJA_SEM_A_COBERTURA", "leis/afirmacao_do_documento.py",
     '            "COBERTURA_DO_GAZETTEER": cobertura_do_gazetteer()}',
     '            "COBERTURA_DO_GAZETTEER": None}'),
    ("O_PRODUTOR_ESCREVE_ESPECIE", "leis/afirmacao_do_documento.py",
     '                "CLAIM_ID": oid,',
     '                "ESPECIE": "SINAL",\n                "CLAIM_ID": oid,'),
    # ── os defeitos que o red team D160 mediu (§2) ──────────────────────────
    ("RT3_DATA_DEPOIS_DA_PUBLICACAO_NAO_E_PREVISAO", "leis/tempo_da_afirmacao.py",
     '        if pub is not None and ini > pub:\n            return PREVISAO, "a data e posterior a publicacao provada"',
     '        if False:\n            return PREVISAO, "a data e posterior a publicacao provada"'),
    ("RT3B_DATA_DEPOIS_DA_CAPTURA_NAO_E_PREVISAO", "leis/tempo_da_afirmacao.py",
     '        if captura is not None and ini > captura:', '        if False:'),
    ("A_DATA_SO_SE_LE_EM_ISO", "leis/tempo_da_afirmacao.py",
     '    m = _RE_DIA_MES.search(FL._baixo(s))', '    m = None if True else _RE_DIA_MES.search(FL._baixo(s))'),
    ("O_FUTURO_DO_VERBO_DEIXA_DE_CONTAR", "leis/tempo_da_afirmacao.py",
     '    return bool(_RE_FUTURO_DO_VERBO.search(frase) or _RE_ANUNCIO.search(frase))',
     '    return False'),
    # ── RT3 §2.A · os dois defeitos da regra do futuro, um mutante cada ──────
    ("RT3_O_ACENTO_DEIXA_DE_SER_OBRIGATORIO", "leis/tempo_da_afirmacao.py",
     '(?:rà\\b|(?<!ti)ranno\\b)', '(?:r[àa]\\b|(?<!ti)ranno\\b)'),
    ("RT3_A_JANELA_VOLTA_A_CORTAR_PALAVRA", "leis/tempo_da_afirmacao.py",
     '    frase = frase_do_valor(span, valor)',
     '    _i = span.lower().find(str(valor or "").lower())\n'
     '    frase = span[max(0, _i - FT.JANELA_ANTES):_i + FT.JANELA_DEPOIS] if _i >= 0 else span'),
    ("RT12_O_FUTURO_OLHA_O_TRECHO_INTEIRO", "leis/tempo_da_afirmacao.py",
     '    frase = frase_do_valor(span, valor)', '    frase = span'),
    ("RT4_ALERTA_EVENTO_SEM_ACONTECIMENTO", "leis/afirmacao_do_documento.py",
     '    if tempo.get("PAPEL") != TA.ACONTECIMENTO:', '    if False:'),
    # ── RT3 §2.D · a ancora do campo SAIU da classe (respondia a outra pergunta) e a MARCA
    # ESCRITA entrou no lugar dela. O mutante segue a garantia, nao a linha antiga.
    ("RT3_A_CLASSE_NAO_EXIGE_MARCA_ESCRITA", "leis/afirmacao_do_documento.py",
     '    if not marcas:\n        faltas.append("nenhuma marca de classe esta escrita no trecho (contrato §5-C)")',
     '    if False:\n        faltas.append("nenhuma marca de classe esta escrita no trecho (contrato §5-C)")'),
    ("RT3_A_MARCA_DE_EVENTO_NAO_E_LIDA_DO_VIVO", "leis/afirmacao_do_documento.py",
     '    if FT._RE_EVENTO.search(span):\n        marcas.append("ALERTA_EVENTO")',
     '    if False:\n        marcas.append("ALERTA_EVENTO")'),
    # ⚠️ Este mutante atacava a linha inteira do ano. A PROD-3 partiu a condicao em duas
    # metades (a PRECISAO/ANO e a pergunta ao VALOR) e o alvo antigo desapareceu — ficou
    # NAO_APLICADO no pre-teste dos alvos. Agora ataca SO a primeira metade, e o
    # PROD3_A_CLASSE_NAO_PERGUNTA_AO_VALOR ataca a segunda: duas garantias, dois ataques.
    ("A_CLASSE_NAO_EXIGE_O_ANO", "leis/afirmacao_do_documento.py",
     '    if (str(tempo.get("PRECISAO") or "").endswith("SEM_ANO") or tempo.get("ANO") == NAO_SEI',
     '    if (False'),
    # A garantia e «uma janela de USO PERMITIDO nao e a data em que a coisa aconteceu».
    # Ela tem TRES formas escritas, e cada uma leva o seu mutante: uma so, a atacar a
    # primeira, sobrevivia por a segunda cobrir o mesmo texto de prova (medido).
    ("A_VALIDADE_SEM_A_FORMA_IMPIEGO_CONSENTITO", "leis/tempo_da_afirmacao.py",
     r'(?:impiego|utilizzo|impieghi|uso)\s+(?:consentit|ammess|autorizzat)|',
     r'(?:zzzimpiego)\s+(?:consentit)|'),
    ("A_VALIDADE_SEM_A_FORMA_AUTORIZZATO_DAL", "leis/tempo_da_afirmacao.py",
     r'(?:consentit[oi]|ammess[oi]|autorizzat[oi])\s+(?:a\s+partire\s+)?dal|',
     r'(?:zzzconsentito)\s+dal|'),
    ("A_VALIDADE_SEM_A_FORMA_VALE_DAL", "leis/tempo_da_afirmacao.py",
     'vale\\s+dal|decorre\\s+dal|con\\s+decorrenza|',
     'zzznuncacasa|'),
    # ── RT3 §2.C · as tres formas novas da VALIDADE, uma alternativa por mutante ──
    ("RT3_A_VALIDADE_SEM_RENDE_ATTIVA", "leis/tempo_da_afirmacao.py",
     'rende\\s+attiv|fase\\s+di\\s+attenzione|', 'zzzrende\\s+attiv|zzzfase|'),
    ("RT3_A_VALIDADE_SEM_DI_OGNI_ANNO", "leis/tempo_da_afirmacao.py",
     'di\\s+ogni\\s+anno)", re.I)', 'zzzdi\\s+ogni\\s+anno)", re.I)'),
    ("RT3_O_PRAZO_ENTRO_IL_PROSSIMO_DEIXA_DE_SER_FUTURO", "leis/tempo_da_afirmacao.py",
     'entro\\s+il\\s+prossim|entro\\s+la\\s+prossim)', 'zzzentro\\s+il\\s+prossim)'),
    # ── RT3 §2.D · os tres atos que nao escrevem «decreto» ───────────────────
    ("RT3_A_MARCA_DE_ATO_SEM_DEROGA", "leis/tempo_da_afirmacao.py",
     'r"deroga|stabilito\\s+dal|"', 'r"zzzderoga|stabilito\\s+dal|"'),
    ("RT3_A_MARCA_DE_ATO_SEM_STABILITO_DAL", "leis/tempo_da_afirmacao.py",
     'r"deroga|stabilito\\s+dal|"', 'r"deroga|zzzstabilito\\s+dal|"'),
    ("RT3_A_MARCA_DE_ATO_SEM_SOSTITUITO", "leis/tempo_da_afirmacao.py",
     r'(?:e|è)\s+stat[oa]\s+sostituit)', r'zzzsostituit)'),
    # ── CONTRATO §5-D · a classe OBSERVACAO_MEDIDA, e os cinco ataques da DT ──
    # DT_FO_1 · retirar a marca (o bloco, o verbo e o valor: tres portas, tres mutantes)
    ("DT_FO_1a_A_CLASSE_SEM_A_MARCA_ESCRITA", "leis/afirmacao_do_documento.py",
     "    if marca and porque_o_lugar_nao_serve is None:\n        marcas.append(OBSERVACAO_MEDIDA)",
     "    if porque_o_lugar_nao_serve is None:\n        marcas.append(OBSERVACAO_MEDIDA)"),
    ("DT_FO_1b_O_VALOR_ACEITA_PERCENTAGEM_E_EURO", "leis/afirmacao_do_documento.py",
     r'_UNIDADES_DE_MEDICAO = r"mm|millimetri|cm|°\s*C|hPa|km/h|m/s"',
     r'_UNIDADES_DE_MEDICAO = r"mm|millimetri|cm|°\s*C|hPa|km/h|m/s|%|euro|€"'),
    ("DT_FO_1c_O_VERBO_ACEITA_QUALQUER_PALAVRA", "leis/afirmacao_do_documento.py",
     r'r"(?<![a-zà-ÿ])(?:registrat|rilevat|misurat)[aoie](?![a-zà-ÿ])", re.I)',
     r'r"(?<![a-zà-ÿ])(?:registrat|rilevat|misurat|osservat|cadut)[aoie](?![a-zà-ÿ])", re.I)'),
    # DT_FO_2 · o futuro a contar como medicao feita, e a troca por outra classe
    ("DT_FO_2a_O_FUTURO_CONTA_COMO_MEDICAO_FEITA", "leis/afirmacao_do_documento.py",
     "        if _RE_AUXILIAR_DE_FUTURO.search(antes):", "        if False:"),
    ("DT_FO_2b_A_CLASSE_NOVA_NAO_EXIGE_TEMPO_NEM_ANO", "leis/afirmacao_do_documento.py",
     '    EXIGEM_TEMPO = ("ALERTA_EVENTO", OBSERVACAO_MEDIDA)',
     '    EXIGEM_TEMPO = ("ALERTA_EVENTO",)'),
    # DT_FO_3 · o offset da marca a deixar de ser absoluto no documento
    ("DT_FO_3_O_OFFSET_DA_MARCA_FICA_RELATIVO", "leis/afirmacao_do_documento.py",
     '        verbo = {"INICIO": inicio + m.start(), "FIM": inicio + m.end(), "TRECHO": m.group(0)}',
     '        verbo = {"INICIO": m.start(), "FIM": m.end(), "TRECHO": m.group(0)}'),
    # DT_FO_4 · o lugar da fonte ou do cabecalho a sustentar a classe
    ("DT_FO_4a_O_LUGAR_DO_CABECALHO_SUSTENTA_A_CLASSE", "leis/afirmacao_do_documento.py",
     '    if lugar.get("LOCATION_SOURCE") != BC.TEXT:', '    if False:'),
    ("DT_FO_4b_O_LUGAR_SEM_POSICAO_SUSTENTA_A_CLASSE", "leis/afirmacao_do_documento.py",
     '    if not onde:\n        return "o lugar nao traz posicao (§5-D exige ONDE)"',
     '    if False:\n        return "o lugar nao traz posicao (§5-D exige ONDE)"'),
    # DT_FO_6 · o commit que o Intelligence owner pediu, e a ressalva que o torna honesto
    ("DT_FO_6a_O_COMMIT_NAO_VIAJA_NO_ARTEFATO", "leis/afirmacao_do_documento.py",
     '            "GIT": _commit_do_codigo(),', ''),
    ("DT_FO_6b_O_SHA_VIAJA_SEM_DIZER_SE_A_ARVORE_ESTAVA_LIMPA", "leis/afirmacao_do_documento.py",
     '        "ARVORE_LIMPA": (sujos == "") if (sha and sujos is not None) else NAO_SEI,',
     '        "ARVORE_LIMPA": True,'),
    # ── RT3 §7 · a precisao nao pode contradizer a origem ────────────────────
    ("RT3_LITERAL_VOLTA_A_VIAJAR_COM_CALCULADA", "leis/tempo_da_afirmacao.py",
     '        if origem == LITERAL:\n            precisao = precisao.replace("+CALCULADA", "")',
     '        if False:\n            precisao = precisao.replace("+CALCULADA", "")'),
    ("RT3_A_PRECISAO_APAGA_CALCULADA_SEMPRE", "leis/tempo_da_afirmacao.py",
     '        if origem == LITERAL:\n            precisao = precisao.replace("+CALCULADA", "")',
     '        if True:\n            precisao = precisao.replace("+CALCULADA", "")'),
    # ── RT3 §5.2 · o MOTIVO tem de viajar num campo, nos DOIS sitios ─────────
    # ⚠️ O alvo deste inclui a linha SEGUINTE de proposito: a versao curta (30 espacos) e
    # SUBSTRING da linha do FACT_TIME_ROLE (35 espacos) e casava 2 vezes — o pre-teste
    # apanhou-o. Dois alvos parecidos precisam de ancora, nao de sorte.
    ("RT3_O_MOTIVO_NAO_VIAJA_NO_FACT_TIME", "leis/afirmacao_do_documento.py",
     '                              "MOTIVO": tempo.get("MOTIVO"),\n'
     '                              "PORQUE_NAO": None if e_facto else tempo["PORQUE"]},',
     '                              "PORQUE_NAO": None if e_facto else tempo["PORQUE"]},'),
    ("RT3_O_MOTIVO_NAO_VIAJA_NO_PAPEL", "leis/afirmacao_do_documento.py",
     '                                   "MOTIVO": tempo.get("MOTIVO"),', ''),
    # ── RT3 §2.D · o mes sozinho tem de acender o «sem ano» no primeiro_dia ──
    ("RT3_PRIMEIRO_DIA_NAO_DIZ_SE_O_ANO_FALTA", "leis/tempo_da_afirmacao.py",
     "    return None, falta_o_ano(s)", "    return None, False"),
    ("A_IDENTIDADE_NAO_SEI_PASSA", "leis/afirmacao_do_documento.py",
     '        if e_ignorancia(af.get(c)):\n            v.append("%s = %r: NAO SEI na identidade RECUSA',
     '        if af.get(c) in (None, ""):\n            v.append("%s = %r: NAO SEI na identidade RECUSA'),
    ("O_BLOCO_DE_MENU_VOLTA_A_SER_CORPO", "leis/afirmacao_do_documento.py",
     '            and not e_bloco_de_linhas_curtas(s))', '            and True)'),
    ("O_LUGAR_ATRAVESSA_LINHA_E_PASSA", "leis/afirmacao_do_documento.py",
     '    if onde and onde["ATRAVESSA_LINHA"]:', '    if False:'),
    ("O_LUGAR_PERDE_O_OFFSET", "leis/afirmacao_do_documento.py",
     '            "ONDE": onde,', '            "ONDE": None,'),
    ("MEMORIA_RESPONDE_A_TODOS", "leis/boletim_do_campo.py",
     '        def _envolta(*args):\n            if args in guardadas:',
     '        def _envolta(*args):\n            if guardadas:\n                return next(iter(guardadas.values()))\n            if args in guardadas:'),
    # ── BLK-1 · o bloqueador do Intelligence owner, e cada peca dele atacada ──
    ("BLK1_DOIS_TEMPOS_ESCOLHEM_UM", "leis/tempo_da_afirmacao.py",
     '        if papel in PAPEL_QUE_E_FACTO and len(escritos) > 1:',
     '        if False:'),
    ("BLK1_DOIS_LUGARES_ESCOLHEM_UM", "leis/afirmacao_do_documento.py",
     '    if valor != UNRESOLVED and len(escritos) > 1:', '    if False:'),
    # A contagem tem de VIAJAR: o dono recusa tambem quando o campo falta. Dois mutantes,
    # um por campo — um so deixava o outro sem guarda.
    ("BLK1_A_CONTAGEM_DE_TEMPOS_NAO_VIAJA", "leis/afirmacao_do_documento.py",
     '                "TEMPOS_NO_TRECHO": tempo.get("TEMPOS_NO_TRECHO", 0),', ''),
    ("BLK1_A_CONTAGEM_DE_LUGARES_NAO_VIAJA", "leis/afirmacao_do_documento.py",
     '                "LUGARES_NO_TRECHO": lugar["LUGARES_NO_TRECHO"],', ''),
    # O INTERVALO: se ele deixar de se juntar, «dal X fino al Y» conta 2 e a janela de
    # validade do D160 §2.2 morre. A guarda e nos dois sentidos.
    ("BLK1_O_INTERVALO_PASSA_A_CONTAR_DOIS", "leis/tempo_da_afirmacao.py",
     '            if _RE_LIGA_UM_PERIODO.match(entre):', '            if False:'),
    # O HIFEN: sem a tolerancia, «Emilia Romagna» nao e contada e o bloqueador volta a 2
    # lugares. Foi a diferenca entre a guarda disparar e nao disparar — medido.
    # ⚠️ O apostrofo desta classe de caracteres tem de chegar aqui INTEIRO. A 1.a versao
    # escreveu-o num literal RAW (r'...\''), o backslash ficou no texto, o alvo apareceu 0
    # vezes e o mutante saiu NAO_APLICADO — que nao e um mutante morto, e um ataque que
    # nunca aconteceu. Por isso este entra em string NORMAL, com o backslash dobrado.
    ("BLK1_HIFEN_DEIXA_DE_SER_ESPACO", "leis/afirmacao_do_documento.py",
     "% r\"[-\\s']+\".join(partes))", '% r" ".join(partes))'),
    ("BLK1_A_AREA_SUPRANACIONAL_DEIXA_DE_CONTAR", "leis/afirmacao_do_documento.py",
     '    nomes = sorted({n for n, _p in TA.FL.GAZETTEER} | set(_AREAS_SUPRANACIONAIS),',
     '    nomes = sorted({n for n, _p in TA.FL.GAZETTEER},'),
    # ── PROD-1 · a data escrita e LITERAL ────────────────────────────────────
    ("PROD1_A_DATA_ESCRITA_VOLTA_A_SER_RELATIVA", "leis/tempo_da_afirmacao.py",
     '        if calculada and _escreve_este_dia(escritos, c["fact_time"]):', '        if False:'),
    ("PROD1_COMPARA_TEXTO_EM_VEZ_DO_DIA", "leis/tempo_da_afirmacao.py",
     '        se_dia, _ = primeiro_dia(x["TRECHO"])\n        if se_dia == dia:',
     '        if str(x["TRECHO"]) == str(valor):'),
    # ── PROD-2 · a loja e mercado em toda a casa ─────────────────────────────
    ("PROD2_A_LOJA_VOLTA_A_NAO_SER_MERCADO", "leis/afirmacao_do_documento.py",
     ' or FT._RE_LOJA.search(span)', ''),
    # ── PROD-3 · o mes sozinho nao tem ano, e a contagem nao pode ser incoerente ──
    ("PROD3_A_CLASSE_NAO_PERGUNTA_AO_VALOR", "leis/afirmacao_do_documento.py",
     '            or TA.falta_o_ano(tempo.get("VALOR"))):', '            or False):'),
    # (O PROD3_A_PRECISAO_NAO_DIZ_QUE_FALTA_O_ANO saiu daqui: a linha que ele atacava era uma
    #  SEGUNDA guarda sobre a mesma pergunta do ano, e foi apagada. Tres guardas a cobrirem-se
    #  umas as outras deram tres mutantes sobreviventes — a saida foi juntar a guarda num sitio,
    #  o `primeiro_dia`, e nao inventar um teste para cada camada.)
    # `falta_o_ano` tem duas metades, e cada uma leva o seu mutante: se so o mes contasse, o
    # «12 marzo» passava; se qualquer texto contasse, «in Toscana» dizia que lhe falta o ano.
    ("PROD3_FALTA_O_ANO_IGNORA_O_MES_ESCRITO", "leis/tempo_da_afirmacao.py",
     '    return bool(_RE_MES_ESCRITO.search(FL._baixo(s)) or re.search(r"\\d", s))',
     '    return bool(re.search(r"\\d", s))'),
    ("PROD3_FALTA_O_ANO_DIZ_SIM_A_QUALQUER_TEXTO", "leis/tempo_da_afirmacao.py",
     '    if escreve_o_ano(s):\n        return False', '    if False:\n        return False'),
    ("PROD3_A_CONTAGEM_IGNORA_O_LUGAR_EMITIDO", "leis/afirmacao_do_documento.py",
     '    if valor != UNRESOLVED and not any(x["PLACE"] == valor for x in escritos):',
     '    if False:'),
    ("PROD3_A_CONTAGEM_IGNORA_O_TEMPO_EMITIDO", "leis/tempo_da_afirmacao.py",
     "        if origem == LITERAL and not escritos:", "        if False:"),
    # E os dois limites, um mutante cada:
    #  · se contasse em QUALQUER origem, a relativa e o cabecalho declaravam uma data escrita
    #    no trecho onde nao ha nenhuma;
    #  · se somasse mesmo havendo expressoes contadas, «il 18 febbraio» ia a 2 e a guarda dos
    #    concorrentes matava um FACT_TIME certo (foi o que aconteceu, e um teste apanhou-o).
    ("PROD3_O_TEMPO_EMITIDO_CONTA_EM_QUALQUER_ORIGEM", "leis/tempo_da_afirmacao.py",
     "        if origem == LITERAL and not escritos:", "        if not escritos:"),
    ("PROD3_O_TEMPO_EMITIDO_SOMA_SE_MESMO_COM_EXPRESSOES", "leis/tempo_da_afirmacao.py",
     "        if origem == LITERAL and not escritos:",
     "        if origem == LITERAL and not _escreve_este_dia(escritos, c[\"fact_time\"]):"),
    # ── PROD-4 · o ato citado pelo numero ────────────────────────────────────
    # Uma alternativa por mutante: a lei da validade (D160 §2.2) mostrou que um mutante unico
    # sobrevive quando outra alternativa apanha o mesmo texto de prova.
    ("PROD4_A_MARCA_DE_ATO_SEM_RECANTE", "leis/tempo_da_afirmacao.py",
     r'regolamento\s+\(?(?:ue|ce)\)?|recante|', r'regolamento\s+\(?(?:ue|ce)\)?|zzzrecante|'),
    ("PROD4_A_MARCA_DE_ATO_SEM_N_DEL", "leis/tempo_da_afirmacao.py",
     r'r"n\.?\s*\d+\s+del(?![a-zà-ÿ])|lotta\s+obbligatoria|"',
     r'r"zzznumero\s+del|lotta\s+obbligatoria|"'),
    ("PROD4_A_MARCA_DE_ATO_SEM_LOTTA_OBBLIGATORIA", "leis/tempo_da_afirmacao.py",
     r'|lotta\s+obbligatoria|"', r'|zzzlotta\s+obbligatoria|"'),
]


def copia_da_arvore(destino: Path) -> None:
    """A arvore COMMITADA, por `git archive` — nunca a pasta de trabalho."""
    tar = destino.parent / "arvore.tar"
    with open(tar, "wb") as f:
        subprocess.run(["git", "archive", "HEAD"], cwd=str(RAIZ), stdout=f, check=True)
    destino.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tar", "-xf", str(tar), "-C", str(destino)], check=True)
    tar.unlink()


def correr_a_bateria(raiz: Path):
    r = subprocess.run([sys.executable, BATERIA], cwd=str(raiz), capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
                                PYTHONPATH=os.environ.get("PYTHONPATH", "")))
    return r.returncode, ((r.stderr or "") + (r.stdout or ""))


# ════════════════════════════════════════════════════════════════════════════
# OS MUTANTES QUE AINDA NAO TEM CODIGO PARA ATACAR (DT-FATO-OBSERVADO)
# ════════════════════════════════════════════════════════════════════════════
# A DT-FATO-OBSERVADO (coordenador + red team, 30/09) criou a classe FATO_OBSERVADO e listou
# cinco ataques que tem de morrer, mais um controle bom fora da R9. Mas quem versiona o
# vocabulario e o DONO DO CONTRATO, e o produtor classifica DEPOIS — logo o codigo que estes
# mutantes atacam ainda nao existe.
#
# Escrever um mutante contra codigo que nao existe da NAO_APLICADO, e NAO_APLICADO nao e um
# mutante morto: e um ataque que nunca aconteceu. Ja aconteceu duas vezes nesta bancada, e a
# segunda so foi vista porque o pre-teste dos alvos passou a existir.
#
#     UMA LISTA DE MUTANTES POR FAZER E DIVIDA DECLARADA.
#     A MESMA LISTA ESQUECIDA E UMA GARANTIA QUE NINGUEM VAI GUARDAR.
#
# Entao ficam AQUI: declarados, contados e impressos em cada corrida, fora do laco que mede.
# `tests/test_o_produtor_de_afirmacoes.py::OsMutantesDaDTEstaoDeclaradosENaoEsquecidos`
# reprova se alguem mexer nesta lista sem passar por lá.
# ✅ 30/09, DEPOIS: o dono do contrato versionou o §5-D e a classe existe. Os seis que estavam
# aqui SAIRAM DA DIVIDA e entraram na lista que corre (procurar `DT_FO_`). A lista fica, vazia,
# de proposito: ela e o sitio onde uma divida destas se declara, e apaga-la esconderia que o
# mecanismo existe.
#: (nome, o que o ataque faz, porque ainda nao corre) — vazia quando nao ha divida
MUTANTES_PENDENTES = []


def conferir_os_alvos() -> list:
    """OS ALVOS, ANTES DE A MEDICAO COMECAR. Devolve a lista dos que nao casam 1 vez.

    ⚠️ ESTE PASSO NASCEU DE DOIS ATAQUES QUE NUNCA ACONTECERAM.
    O `BLK1_HIFEN_DEIXA_DE_SER_ESPACO` trazia o apostrofo num literal RAW do Python, o
    backslash ficou no texto e o alvo apareceu 0 vezes. O `A_CLASSE_NAO_EXIGE_O_ANO` perdeu o
    alvo quando a PROD-3 partiu a condicao do ano em duas metades. Os dois sairam
    NAO_APLICADO — que o laco ja conta como SOBREVIVENTE, e faz bem.

        UM MUTANTE QUE NAO ENTRA NAO E UM MUTANTE MORTO:
        E UMA GARANTIA QUE NINGUEM ATACOU, A CONTAR-SE COMO GARANTIA GUARDADA.

    O laco descobria isto DEPOIS de copiar a arvore e correr a bateria, mutante a mutante.
    Aqui descobre-se em um segundo, antes de gastar a medicao — e sobretudo antes de alguem
    ler «MORTOS 53/54» e pensar que o 54.o e um buraco no codigo em vez de um erro de alvo.
    """
    fora = []
    for nome, rel, de, _para in MUTANTES:
        caminho = RAIZ / rel
        n = caminho.read_text(encoding="utf-8").count(de) if caminho.exists() else -1
        if n != 1:
            fora.append({"NOME": nome, "FICHEIRO": rel,
                         "VEZES": n, "PORQUE": "o ficheiro nao existe" if n < 0 else
                                               "o texto a trocar aparece %d vezes (tem de ser 1)" % n})
    return fora


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent / "MUTACAO-PRODUTOR-V1.json"))
    ap.add_argument("--conferir-alvos", action="store_true",
                    help="so confere que cada alvo casa 1 vez, e sai; nao mede nada")
    a = ap.parse_args(argv)

    maus = conferir_os_alvos()
    if a.conferir_alvos:
        for m in maus:
            print("ALVO_MAU %-45s %s" % (m["NOME"], m["PORQUE"]))
        print("ALVOS %d · MAUS %d · PENDENTES %d (DT-FATO-OBSERVADO, sem codigo para atacar)"
              % (len(MUTANTES), len(maus), len(MUTANTES_PENDENTES)))
        for nome, ataque, _porque in MUTANTES_PENDENTES:
            print("   PENDENTE %-44s %s" % (nome, ataque))
        return 1 if maus else 0
    if maus:
        print("ALVOS_MAUS=%d · a medicao NAO corre: %s"
              % (len(maus), ", ".join(m["NOME"] for m in maus)), file=sys.stderr)
        print("Corrija os alvos (py provas/d158/mutar_o_produtor.py --conferir-alvos) e repita. "
              "Medir com um alvo morto conta um ataque que nunca aconteceu.", file=sys.stderr)
        return 2

    base = Path(tempfile.mkdtemp(prefix="d158-mut-"))
    limpo = base / "limpo"
    copia_da_arvore(limpo)
    codigo, saida = correr_a_bateria(limpo)
    r = {"ARVORE": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(RAIZ), capture_output=True,
                                  text=True).stdout.strip(),
         "BATERIA": BATERIA,
         "SEM_MUTACAO": {"CODIGO": codigo, "VERDE": codigo == 0, "CAUDA": saida.strip()[-400:]},
         "MUTANTES": []}
    if codigo != 0:
        r["AVISO"] = ("a bateria ja reprova na copia LIMPA: nenhum mutante prova nada enquanto isto "
                      "for verdade")
        Path(a.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(r["SEM_MUTACAO"], ensure_ascii=False))
        return 1

    mortos = 0
    for nome, rel, de, para in MUTANTES:
        alvo = base / nome
        if alvo.exists():
            shutil.rmtree(alvo)
        shutil.copytree(limpo, alvo)
        p = alvo / Path(rel)
        fonte = p.read_text(encoding="utf-8")
        if fonte.count(de) != 1:
            r["MUTANTES"].append({"NOME": nome, "FICHEIRO": rel, "ESTADO": "NAO_APLICADO",
                                  "PORQUE": "o texto a trocar aparece %d vezes (tem de aparecer 1)"
                                            % fonte.count(de)})
            continue
        p.write_text(fonte.replace(de, para), encoding="utf-8", newline="\n")
        c, s = correr_a_bateria(alvo)
        morto = c != 0
        mortos += morto
        r["MUTANTES"].append({"NOME": nome, "FICHEIRO": rel, "ESTADO": "MORTO" if morto else "SOBREVIVEU",
                              "CODIGO": c,
                              "QUEM_O_MATOU": [l.strip() for l in s.splitlines()
                                               if l.startswith(("FAIL:", "ERROR:"))][:6]})
        shutil.rmtree(alvo, ignore_errors=True)
    r["TOTAL"] = len(MUTANTES)
    r["MORTOS"] = mortos
    r["SOBREVIVENTES"] = [m["NOME"] for m in r["MUTANTES"] if m["ESTADO"] != "MORTO"]
    r["ALVOS_CONFERIDOS"] = True
    # A divida fica DENTRO da prova, e nao so no codigo: quem ler o JSON amanha ve que ha
    # seis ataques por fazer e porque. Um numero de mortos sem a lista do que falta atacar
    # conta a metade boa da historia.
    r["MUTANTES_PENDENTES"] = [{"NOME": n, "ATAQUE": at, "PORQUE_NAO_CORRE": pq}
                               for n, at, pq in MUTANTES_PENDENTES]
    r["PORQUE_HA_PENDENTES"] = (
        "DT-FATO-OBSERVADO: o dono do contrato versiona o vocabulario (classe, marcas aceites, "
        "tempo exigido) e o produtor classifica DEPOIS. Sem o codigo da classe, estes seis "
        "sairiam NAO_APLICADO — que nao e um mutante morto, e um ataque que nunca aconteceu.")
    Path(a.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.rmtree(base, ignore_errors=True)
    print("MORTOS %d/%d · SOBREVIVENTES: %s" % (mortos, len(MUTANTES), r["SOBREVIVENTES"] or "nenhum"))
    # ⚠️ ESTE ARNES DEVOLVIA 0 COM SOBREVIVENTES VIVOS.
    # Um medidor que sai com sucesso quando a medicao corre — e nao quando ela PASSA — nao
    # serve de portao: quem o chamasse num gancho ou num workflow lia verde por ter corrido.
    # Agora o codigo de saida responde a pergunta que interessa.
    return 1 if r["SOBREVIVENTES"] else 0


if __name__ == "__main__":
    sys.exit(main())
