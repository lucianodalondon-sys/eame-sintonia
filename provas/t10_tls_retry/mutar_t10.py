"""T10-TLS-RETRY · prova de mutacao do recuo transitorio e da retentativa na mesma reserva.

    py provas/t10_tls_retry/mutar_t10.py --conferir-alvos     (1 s: cada alvo casa EXACTAMENTE uma vez?)
    py provas/t10_tls_retry/mutar_t10.py                      (mede e escreve MUTACAO-T10.json)

Cada mutante troca um texto que tem de casar exactamente UMA vez; senao sai NAO_APLICADO e a medicao
recusa-se a correr (rc=2) — um mutante que nao entra nao e um mutante morto. Morto = o teste
`tests.test_transporte_tls_retry` sai com rc != 0. Os bytes originais voltam no `finally` e o sha256
e conferido depois de cada mutante (nada de `git checkout`, que devolve o indice e apaga trabalho).
rc=0 so com TODOS mortos; rc=1 com sobrevivente.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COLETOR = "coleta/italy_pilot_collect.mjs"
CORTESIA = "coleta/cortesia_adaptativa.mjs"
SAIDA = os.path.join(RAIZ, "provas", "t10_tls_retry", "MUTACAO-T10.json")
TESTE = "tests.test_transporte_tls_retry"

MUTANTES = [
    ("M01_RECUO_SAI_DA_MATERIA", COLETOR,
     "{ reservaEm, recuoS: recuoTransitorioS(i), proximoRecuoS: i < tentativas",
     "{ reservaEm, recuoS: 0, proximoRecuoS: i < tentativas"),
    ("M02_RECUO_SAI_DO_ROBOTS", COLETOR,
     "{ reservaEm, recuoS: recuoTransitorioS(i), proximoRecuoS: i < 2",
     "{ reservaEm, recuoS: 0, proximoRecuoS: i < 2"),
    ("M03_RECUO_SEM_LIMITE", COLETOR,
     "Math.min(RECUO_TRANSITORIO.MAXIMO_S, RECUO_TRANSITORIO.BASE_S * 2 ** (tentativa - 2))",
     "RECUO_TRANSITORIO.BASE_S * 2 ** (tentativa - 2)"),
    ("M04_RECUO_ENGOLIDO_PELA_PAUSA", COLETOR,
     "const falta = ultimo + minimo + recuoS * 1000 - Date.now();",
     "const falta = ultimo + Math.max(minimo, recuoS * 1000) - Date.now();"),
    ("M05_RECUO_ANTES_DA_1A_TENTATIVA", COLETOR,
     "(tentativa <= 1 ? 0 :",
     "(tentativa < 1 ? 0 :"),
    ("M06_TLS_35_NAO_E_TRANSITORIO", COLETOR,
     "const TRANSITORIOS = [28, 35, 52, 56, 7];",
     "const TRANSITORIOS = [28, 52, 56, 7];"),
    ("M07_A_FALHA_FECHA_A_RESERVA", COLETOR,
     "          throw Object.assign(e, { reservaEm, respostaAdiada: true });",
     "          { registarResposta(host, url, null, []); throw Object.assign(e, { reservaEm, respostaAdiada: true }); }"),
    ("M08_RETENTATIVA_PEDE_RESERVA_NOVA", COLETOR,
     "  const naMesmaReserva = reservaEm !== null;",
     "  const naMesmaReserva = false;"),
    ("M09_SEM_CONFERIR_O_LEASE", COLETOR,
     "TRANSITORIOS.includes(e.code) && cabeNaReserva(reservaEm, pausaS + proximoRecuoS))",
     "TRANSITORIOS.includes(e.code))"),
    ("M10_RETENTATIVA_DO_ROBOTS_PERGUNTA_O_TETO", COLETOR,
     "if (reservaEm === null && tetoAtingido(host)) return",
     "if (tetoAtingido(host)) return"),
    ("M11_RETENTATIVA_DA_MATERIA_PERGUNTA_O_TETO", COLETOR,
     "    for (let i = 1; i <= tentativas && !r; i++) {\n",
     "    for (let i = 1; i <= tentativas && !r; i++) {\n      if (i > 1 && tetoAtingido(lic.host)) return { erro: \"CORTESIA TETO\", status: 0, tentativas: i - 1, recusado: motivoDoTeto(), foiARede, retry_permitido: false };\n"),
    ("M12_RETENTATIVA_ESCONDIDA", COLETOR,
     "  if (naMesmaReserva) CORTESIA.retentativas.set(host, (CORTESIA.retentativas.get(host) || 0) + 1);",
     "  if (naMesmaReserva) ;"),
    ("M13_RETENTATIVA_CONTA_NO_TETO", COLETOR,
     "  if (naMesmaReserva) CORTESIA.retentativas.set(",
     "  if (naMesmaReserva) CORTESIA.porHost.set(host, (CORTESIA.porHost.get(host) || 0) + 1), CORTESIA.retentativas.set("),
    ("M14_DESAFIO_DEIXA_DE_SER_SINAL", CORTESIA,
     'if (desafio) sinais.push("PAGINA_DE_DESAFIO");',
     ";"),
]


def ler(rel):
    with open(os.path.join(RAIZ, rel), "rb") as f:
        return f.read()


def escrever(rel, b):
    with open(os.path.join(RAIZ, rel), "wb") as f:
        f.write(b)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def conferir_alvos():
    mortos = []
    for nome, rel, antes, _ in MUTANTES:
        n = ler(rel).decode("utf-8").count(antes)
        if n != 1:
            mortos.append({"MUTANTE": nome, "CASAMENTOS": n})
    return mortos


def main():
    alvos_mortos = conferir_alvos()
    if "--conferir-alvos" in sys.argv:
        print(json.dumps({"ALVOS_QUE_NAO_CASAM_1_VEZ": alvos_mortos}, ensure_ascii=False, indent=1))
        return 2 if alvos_mortos else 0
    if alvos_mortos:
        print("NAO_APLICADO — a medicao nao corre:", alvos_mortos)
        return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "status", "--porcelain", "--", COLETOR, CORTESIA], cwd=RAIZ,
                          capture_output=True, text=True).stdout.strip()
    if sujo:
        print("os ficheiros atacados tem mudancas por commitar — commitar antes (a prova reescreve-os):", sujo)
        return 2
    originais = {rel: ler(rel) for rel in {COLETOR, CORTESIA}}
    env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
    env.update(PYTHONUTF8="1", NODE_DISABLE_COMPILE_CACHE="1")

    def correr():
        t = time.time()
        p = subprocess.run([sys.executable, "-m", "unittest", TESTE], cwd=RAIZ, env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=1500)
        falhas = [l for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        return p.returncode, round(time.time() - t, 1), falhas

    rc0, s0, f0 = correr()
    controlo = {"RC": rc0, "SEGUNDOS": s0, "FALHAS": f0}
    if rc0 != 0:
        print("o teste ja falha SEM mutante — a medicao nao vale:", f0)
        return 2
    res = []
    for nome, rel, antes, depois in MUTANTES:
        orig = originais[rel]
        try:
            escrever(rel, orig.decode("utf-8").replace(antes, depois, 1).encode("utf-8"))
            rc, s, falhas = correr()
        finally:
            escrever(rel, orig)
        if sha(ler(rel)) != sha(orig):
            raise SystemExit("o ficheiro %s nao voltou ao original depois de %s" % (rel, nome))
        res.append({"MUTANTE": nome, "FICHEIRO": rel, "ESTADO": "MORTO" if rc != 0 else "SOBREVIVEU",
                    "RC": rc, "SEGUNDOS": s, "APANHADO_POR": [f.split(" (")[0] for f in falhas]})
        print(nome, res[-1]["ESTADO"], s, "s", res[-1]["APANHADO_POR"][:3], flush=True)
    mortos = sum(r["ESTADO"] == "MORTO" for r in res)
    out = {"PROVA": "T10-TLS-RETRY mutacao", "HEAD": head, "TESTE": TESTE,
           "SHA256_ORIGINAIS": {rel: sha(b) for rel, b in originais.items()},
           "CONTROLO_SEM_MUTANTE": controlo, "MORTOS": mortos, "TOTAL": len(res),
           "SOBREVIVENTES": [r["MUTANTE"] for r in res if r["ESTADO"] != "MORTO"], "MUTANTES": res}
    with open(SAIDA, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("MORTOS %d/%d" % (mortos, len(res)))
    return 0 if mortos == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
