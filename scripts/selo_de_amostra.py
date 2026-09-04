#!/usr/bin/env python3
"""O SELO DE QUEM ESCREVEU E QUANDO — uma linha que a amostra não pode não ter.

`tests/test_evidence.py` cobra duas coisas de toda amostra em `data/samples/`:
de onde ela veio (`SOURCE_ID`) e quando foi capturada (`CAPTURED_AT`, em AAAA-MM-DD).
A cobrança é certa: amostra sem data não é evidência, é arquivo.

Em 2026-09-04 a suíte pegou 13 amostras da camada italiana escritas sem `CAPTURED_AT`
e uma sem `SOURCE_ID` — porque cada função de escrita montava o dicionário à mão e
algumas esqueceram o campo. Esquecer é o modo normal de falhar quando o selo é
opcional em doze lugares diferentes.

    UM SÓ LUGAR CARIMBA. QUEM ESCREVE, CHAMA.

`selar` NÃO sobrescreve o que já existe: se a função de escrita já pôs a data real da
medição, ela vence. O selo só cobre o silêncio.
"""
import time

FORMATO = '%Y-%m-%dT%H:%M:%SZ'


def agora():
    return time.strftime(FORMATO, time.gmtime())


def selar(corpo, source_id=None):
    """→ o mesmo corpo, garantidamente com SOURCE_ID e CAPTURED_AT.

    Não é cópia: carimba no lugar e devolve, para caber dentro de `json.dump(...)`.
    """
    if not isinstance(corpo, dict):
        return corpo
    if source_id and not corpo.get('SOURCE_ID'):
        corpo['SOURCE_ID'] = source_id
    if not corpo.get('CAPTURED_AT'):
        corpo['CAPTURED_AT'] = agora()
    return corpo
