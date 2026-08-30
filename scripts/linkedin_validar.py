#!/usr/bin/env python3
"""
VALIDAR os 8 perfis já pagos antes de gastar de novo. Só GET.

A recuperação provou que os itens existem e são perfis completos. Falta a
pergunta que o RAW deixou em aberto: **são as pessoas certas?**

O Actor recebe uma consulta de busca e devolve UM perfil. Ele sempre devolve
algum. O primeiro item recuperado tem nome curto que não bate com nenhum alvo
longo da lista — sinal de que pelo menos um retorno é outra pessoa.

    SEARCH_HIT ≠ PERSON

E A ORDEM NÃO SERVE DE CHAVE
-----------------------------
Seria cômodo casar o run n-ésimo com o alvo n-ésimo. Não faço isso: a listagem
vem em ordem cronológica inversa, execuções podem ter falhado no meio, e uma
correspondência posicional erraria em silêncio. Cada perfil é comparado **por
nome** contra todos os oito alvos, e quem não casa com ninguém fica órfão e
declarado.

QUATRO ESTADOS, NÃO DOIS
-------------------------
    IDENTITY_CONFIRMED             nome e sobrenome do alvo estão no perfil
    IDENTITY_PLAUSIBLE_NOT_PROVED  sobrenome bate, nome não — pode ser homônimo
    IDENTITY_MISMATCH              o perfil é claramente de outra pessoa
    IDENTITY_NOT_ENOUGH_EVIDENCE   o item não traz nome utilizável

`PLAUSIBLE` existe porque sobrenome sozinho não prova pessoa, e tratá-lo como
prova seria atribuir a um pesquisador conteúdo que não é dele.

E A LOCALIZAÇÃO NÃO VIAJA
--------------------------
`basic_info.location` vira `PROFILE_DECLARED_LOCATION`, nunca `FACT_LOCATION`.
Onde a pessoa mora não é onde o fenômeno agrícola aconteceu.

    SOURCE_LOCATION ≠ FACT_LOCATION
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap            # noqa: E402
import apify_recuperar as rec      # noqa: E402
import linkedin_schema as sch      # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-LINKEDIN-IDENTITY.json')

ALVOS = [
    ('Pasquale De Vita', 'RESEARCHER', 'CREA Cerealicoltura e Colture Industriali'),
    ('Nicola Pecchioni', 'RESEARCHER', 'CREA Cerealicoltura e Colture Industriali'),
    ('Sabrina Locatelli', 'RESEARCHER', 'CREA — Bergamo'),
    ('Francesca Nocente', 'RESEARCHER', 'CREA'),
    ('Daniela Pacifico', 'RESEARCHER', 'CREA'),
    ('Stefano Biagetti', 'TECHNICAL_FIELD_VOICE', 'Consorzio Agrario di Ancona'),
    ('Giovanni Drei', 'TECHNICAL_FIELD_VOICE', 'Bayer Crop Science Italia'),
    ('Federico Cavina', 'TECHNICAL_FIELD_VOICE', 'Terremerse Soc. Coop.'),
]

CONFIRMED = 'IDENTITY_CONFIRMED'
PLAUSIBLE = 'IDENTITY_PLAUSIBLE_NOT_PROVED'
MISMATCH = 'IDENTITY_MISMATCH'
SEM_EVID = 'IDENTITY_NOT_ENOUGH_EVIDENCE'


def casar(perfil):
    """Compara o perfil contra TODOS os alvos. Devolve (alvo, estado, motivo)."""
    if perfil.get('SCHEMA') != sch.SCHEMA_V1:
        return None, SEM_EVID, 'schema não reconhecido'
    cheio = sch._normal(perfil.get('FULLNAME') or
                        '%s %s' % (perfil.get('FIRST_NAME') or '',
                                   perfil.get('LAST_NAME') or ''))
    if not cheio.strip():
        return None, SEM_EVID, 'o item não traz nome utilizável'

    melhor, estado, motivo = None, MISMATCH, 'nenhum alvo bate com o nome devolvido'
    for nome, _, _inst in ALVOS:
        partes = sch._normal(nome).split()
        presentes = [p for p in partes if p in cheio]
        if len(presentes) == len(partes):
            return nome, CONFIRMED, 'nome e sobrenome do alvo estão no perfil'
        # sobrenome é a última palavra; sozinho não prova pessoa
        if partes and partes[-1] in cheio and melhor is None:
            melhor, estado, motivo = nome, PLAUSIBLE, (
                'o sobrenome "%s" bate, o nome não — pode ser homônimo' % partes[-1])
    return melhor, estado, motivo


def main():
    censo = ap.censo()
    out = {
        'SOURCE_ID': 'DERIVED/IT-LINKEDIN-IDENTITY',
        'source': 'validação de identidade sobre RAW JÁ PAGO — nenhum Actor iniciado',
        'SOURCE_LOCATION': 'LinkedIn', 'FACT_LOCATION': 'n/a — metadado de coleta',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'NEW_ACTOR_RUNS': 0,
        'LAWS': ['SEARCH_HIT ≠ PERSON', 'SOURCE_LOCATION ≠ FACT_LOCATION'],
        'MATCHING_METHOD': ('cada perfil é comparado POR NOME contra os oito alvos. '
                            'A ordem da listagem NÃO é usada como chave: ela vem em '
                            'ordem cronológica inversa e uma correspondência posicional '
                            'erraria em silêncio.'),
        'POOL': censo, 'TOKEN_VALUE_LOGGED': 'NO',
    }
    ks = ap.pool()
    if not ks:
        out['STATE'] = 'APIFY_ENV_MISSING'
        _grava(out); print('APIFY_ENV_MISSING'); return

    pos, regs = 0, []
    while pos < len(ks):
        try:
            regs = rec.recuperar(ks[pos])
            break
        except Exception as e:
            if ap.classificar(excecao=e) in ap.ROTACIONAM:
                pos += 1; continue
            out['ERROR'] = ap.redigir(str(e))[:200]
            break

    achados, orfaos = {}, []
    for r in regs:
        if not r.get('RAW_PATH'):
            continue
        import gzip
        with gzip.open(os.path.join(ROOT, r['RAW_PATH']), 'rt', encoding='utf-8') as f:
            itens = json.load(f)
        for it in itens:
            p = sch.extrair_perfil(it)
            alvo, estado, motivo = casar(p)
            reg = {
                'ACTOR_RUN_ID': r['ACTOR_RUN_ID'], 'DATASET_ID': r['DATASET_ID'],
                'RAW_PATH': r['RAW_PATH'], 'RAW_SHA256': r['RAW_SHA256'],
                'COST': r.get('COST'),
                'IDENTITY_STATE': estado, 'IDENTITY_REASON': motivo,
                'PROFILE_URL': p.get('PROFILE_URL'),
                'PUBLIC_IDENTIFIER': p.get('PUBLIC_IDENTIFIER'),
                'RETURNED_FULLNAME': p.get('FULLNAME'),
                'HEADLINE': p.get('HEADLINE'),
                'CURRENT_COMPANY': p.get('CURRENT_COMPANY'),
                'PROFILE_DECLARED_LOCATION': p.get('LOCATION'),
                'PROFILE_COUNTRY_CODE': p.get('COUNTRY_CODE'),
                'FACT_LOCATION': 'NÃO DERIVADO — a localização do perfil não é a do fato',
                'FOLLOWER_COUNT': p.get('FOLLOWER_COUNT'),
            }
            if alvo and estado in (CONFIRMED, PLAUSIBLE):
                anterior = achados.get(alvo)
                if not anterior or (anterior['IDENTITY_STATE'] == PLAUSIBLE
                                    and estado == CONFIRMED):
                    achados[alvo] = reg
            else:
                orfaos.append(reg)

    tabela = []
    for nome, classe, inst in ALVOS:
        r = achados.get(nome)
        tabela.append({
            'TARGET': nome, 'VOICE_CLASS': classe, 'KNOWN_INSTITUTION': inst,
            'IDENTITY_STATE': r['IDENTITY_STATE'] if r else SEM_EVID,
            'IDENTITY_REASON': r['IDENTITY_REASON'] if r else
                               'nenhum perfil recuperado casou com este alvo',
            'PROFILE_URL': r.get('PROFILE_URL') if r else None,
            'RETURNED_FULLNAME': r.get('RETURNED_FULLNAME') if r else None,
            'HEADLINE': r.get('HEADLINE') if r else None,
            'PROFILE_DECLARED_LOCATION': r.get('PROFILE_DECLARED_LOCATION') if r else None,
            'FACT_LOCATION': 'NÃO DERIVADO',
            'RAW_PATH': r.get('RAW_PATH') if r else None,
            'ACTOR_RUN_ID': r.get('ACTOR_RUN_ID') if r else None,
        })

    cont = {}
    for t in tabela:
        cont[t['IDENTITY_STATE']] = cont.get(t['IDENTITY_STATE'], 0) + 1
    out.update({
        'STATE': 'VALIDATED', 'RUNS_READ': len(regs),
        'TARGETS': tabela, 'COUNTS': cont,
        'ORPHAN_PROFILES': orfaos,
        'ORPHAN_NOTE': ('perfis devolvidos pelo Actor que não casam com nenhum alvo. '
                        'Cada um é uma execução paga que retornou OUTRA PESSOA — a prova '
                        'concreta de SEARCH_HIT ≠ PERSON.'),
        'CONFIRMED_TARGETS': [t['TARGET'] for t in tabela
                              if t['IDENTITY_STATE'] == CONFIRMED],
    })
    _grava(out)
    print('=== IDENTIDADE DOS 8 ALVOS (sobre RAW ja pago, 0 runs novos) ===')
    for t in tabela:
        print('  %-20s %-32s %s' % (t['TARGET'], t['IDENTITY_STATE'],
                                    (t['RETURNED_FULLNAME'] or '-')))
    print('CONTAGEM:', json.dumps(cont, ensure_ascii=False))
    print('ORFAOS (perfil devolvido que nao e nenhum alvo):', len(orfaos))
    for o in orfaos[:8]:
        print('   devolveu: %-24s | %s' % ((o['RETURNED_FULLNAME'] or '-')[:24],
                                           (o['HEADLINE'] or '-')[:60]))


def _grava(out):
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        fh.write(ap.redigir(json.dumps(out, ensure_ascii=False, indent=2)))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
