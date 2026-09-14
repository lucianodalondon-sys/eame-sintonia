#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════
# A GUARDA DO CLONE — o alvo tem de ser um clone, e prova-se
#
# O maior risco da porta de verificação do clone não é ler de menos: é ser
# apontada ao LIVE. Uma auditoria contra a produção, chamada «prova do
# restauro», seria uma mentira verde.
#
#     TARGET != SOURCE, MEDIDO E NAO PROMETIDO.
#
# Esta guarda extrai o `project ref` de uma DSN **sem nunca a imprimir**, e
# recusa se ele for o da produção ou o do dev. Se não conseguir extrair o
# ref, também recusa: não saber QUAL é o projeto não é permissão para
# correr contra ele.
#
#     REF DESCONHECIDO != REF SEGURO.
#
# Vive em ficheiro próprio, e não dentro do YAML, por um motivo só: uma
# guarda que não se pode testar é uma guarda em que ninguém pode confiar.
# ═══════════════════════════════════════════════════════════════════════
from __future__ import annotations

import os
import re
import sys
import urllib.parse as U

SOURCE_PROJECT_REF = "odhdwvugikjdvkapbowe"
DEV_PROJECT_REF = "xhqebdweltytnghiavew"

# O `ref` do Supabase é uma cadeia de 20 letras minúsculas.
REF = r"[a-z]{20}"


def ref_da_dsn(dsn: str) -> tuple[str, str]:
    """Devolve (ref, como_foi_encontrado). Nunca devolve a DSN."""
    try:
        p = U.urlparse(dsn)
    except Exception:
        return "", "DSN ilegivel"
    host, user = (p.hostname or ""), (p.username or "")
    # 1 · ligação directa: db.<ref>.supabase.co
    m = re.match(r"db\.(%s)\.supabase\." % REF, host)
    if m:
        return m.group(1), "host da ligacao directa"
    # 2 · pooler: o host não traz ref nenhum; ele vive no utilizador,
    #     `postgres.<ref>`.
    if "." in user:
        cauda = user.split(".", 1)[1]
        if re.fullmatch(REF, cauda):
            return cauda, "utilizador do pooler"
    return "", "nao localizavel"


def decide(dsn: str) -> tuple[bool, list]:
    """(pode_correr, linhas_para_o_log). As linhas nunca contêm a DSN."""
    ref, via = ref_da_dsn(dsn)
    log = ["REF_EXTRAIDO=%s (via %s)" % ("SIM" if ref else "NAO", via)]
    if not ref:
        log += ["ABORTADO=nao consegui extrair o project ref da DSN.",
                "Sem saber QUAL projeto e, nao se corre nada contra ele."]
        return False, log
    log += ["TARGET_E_A_PRODUCAO=%s" % ("SIM" if ref == SOURCE_PROJECT_REF else "NAO"),
            "TARGET_E_O_DEV=%s" % ("SIM" if ref == DEV_PROJECT_REF else "NAO")]
    # A PRODUCAO E INEGOCIAVEL. Nenhuma autorizacao de missao a abre: esta
    # porta le um ALVO DE PROVA, e a producao nunca e um alvo de prova.
    if ref == SOURCE_PROJECT_REF:
        log += ["ABORTADO=o alvo e a PRODUCAO.",
                "Apontar a auditoria de um alvo de prova ao LIVE seria medir",
                "a coisa errada e chamar-lhe prova."]
        return False, log
    # O DEV passa, e passa NOMEADO. O utilizador autorizou-o como bancada
    # em 2026-09-14; a guarda deixa de o recusar, mas nao deixa de o dizer —
    # quem le o log tem de saber contra QUE CLASSE de projeto isto correu.
    if ref == DEV_PROJECT_REF:
        log += ["ALVO=o projeto dev, autorizado como bancada",
                "ATENCAO=o dev NAO pode ser alvo de um restauro da plataforma",
                "(medido: o Supabase so restaura in-place ou para projeto NOVO).",
                "Uma auditoria verde aqui prova o estado DELE, e nao um restauro."]
        return True, log
    log += ["GUARDA=PASS · o alvo nao e a producao"]
    return True, log


def main() -> int:
    dsn = os.environ.get("SUPABASE_CLONE_DB_URL", "")
    if not dsn:
        print("SUPABASE_CLONE_DB_URL=AUSENTE")
        return 1
    pode, log = decide(dsn)
    for linha in log:
        print(linha)
    return 0 if pode else 1


if __name__ == "__main__":
    sys.exit(main())
