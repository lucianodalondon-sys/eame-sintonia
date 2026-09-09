#!/usr/bin/env python3
"""Classifica o censo de metadados das 12 candidatas a P0.

    PROVA DE PORTA FECHADA  -> publicavel inteira.
    PROVA DE PORTA ABERTA   -> veredito e contagem; os nomes ficam retidos.

O repositorio e publico. Este ficheiro decide o que o log conta ao mundo.
"""
import sys, pathlib

ESTADOS = ("NOT_PRESENT_LIVE", "RLS_PROTECTED", "NO_EFFECTIVE_ANON_PRIVILEGE",
           "ANON_READ_POSSIBLE_BY_METADATA", "ANON_WRITE_POSSIBLE_BY_METADATA",
           "EXPOSURE_METADATA_AMBIGUOUS")


def kv(rest):
    out = {}
    for part in rest:
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


def classificar(t):
    if t["presente"] != "true":
        return "NOT_PRESENT_LIVE", False, False
    anon_read = t["anon_s"] == "true"
    anon_write = any(t[k] == "true" for k in ("anon_i", "anon_u", "anon_d"))
    if not anon_read and not anon_write:
        return "NO_EFFECTIVE_ANON_PRIVILEGE", False, False
    # Privilegio existe. RLS ligada com policies pode ainda assim negar cada
    # linha — mas RLS ENABLED != RLS POLICY PROVED, e sem policy a RLS nega tudo.
    if t["rls"] == "true":
        estado = "RLS_PROTECTED" if t["policies"] == "0" else "EXPOSURE_METADATA_AMBIGUOUS"
        return estado, anon_read, anon_write
    return ("ANON_WRITE_POSSIBLE_BY_METADATA" if anon_write
            else "ANON_READ_POSSIBLE_BY_METADATA"), anon_read, anon_write


def main(path):
    linhas = [l.strip() for l in pathlib.Path(path).read_text().splitlines() if l.strip()]
    tabelas, contexto = [], []
    for l in linhas:
        campos = l.split("|")
        if campos[0] == "T":
            d = kv(campos[2:]); d["nome"] = campos[1]; tabelas.append(d)
        else:
            contexto.append(l)

    print("── CONTEXTO (estrutural, ja deducivel das migrations) ──")
    for l in contexto:
        print("  " + l)

    print("\n── ESTADO ESTRUTURAL POR TABELA ──")
    for t in tabelas:
        print(f"  {t['nome']:26} presente={t['presente']:5} rls={t['rls']:5} "
              f"force={t['force']:5} policies={t['policies']:>3} colunas={t['colunas']:>3}")

    res = [(t, *classificar(t)) for t in tabelas]
    expostas = [r for r in res if r[2] or r[3]]
    ambiguas = [r for r in res if r[1] == "EXPOSURE_METADATA_AMBIGUOUS"]

    print("\n── VEREDITO ──")
    print(f"  CANDIDATAS            {len(tabelas)}")
    print(f"  NOT_PRESENT_LIVE      {sum(1 for r in res if r[1] == 'NOT_PRESENT_LIVE')}")
    print(f"  SEM PRIVILEGIO ANON   {sum(1 for r in res if r[1] == 'NO_EFFECTIVE_ANON_PRIVILEGE')}")
    print(f"  ANON_READ  (efectivo) {sum(1 for r in res if r[2])}")
    print(f"  ANON_WRITE (efectivo) {sum(1 for r in res if r[3])}")
    print(f"  AMBIGUAS              {len(ambiguas)}")

    if not expostas:
        print("\n  P0_CANDIDATE = DISPROVED_BY_LIVE_METADATA")
        print("  A porta esta fechada, e provar isso nao ensina nada a ninguem.")
        print("\n── MATRIZ COMPLETA (publicavel: tudo negado) ──")
        for t, estado, _, _ in res:
            print(f"  {t['nome']:26} {estado:32} "
                  f"anon[s{t['anon_s'][0]} i{t['anon_i'][0]} u{t['anon_u'][0]} d{t['anon_d'][0]}] "
                  f"auth[s{t['auth_s'][0]} i{t['auth_i'][0]} u{t['auth_u'][0]} d{t['auth_d'][0]}]")
        return 0

    print("\n  P0_CANDIDATE = EXPOSURE_DETECTED_BY_LIVE_METADATA")
    print("  DETALHE_RETIDO = YES")
    print("  Nomes de tabela, matriz e caminho de exposicao NAO sao impressos:")
    print("  este log e publico e a contencao ainda nao existe.")
    print("  Quem tem a chave do projeto le o detalhe pela sua propria conexao.")
    print("\n     PROVA DE PORTA ABERTA -> PRIMEIRO FECHA-SE, DEPOIS PUBLICA-SE.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
