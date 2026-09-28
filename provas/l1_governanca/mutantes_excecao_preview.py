# -*- coding: utf-8 -*-
"""D140 · OS MUTANTES DA EXCEÇÃO PREVIEW_E2E — a guarda morde?

    python provas/l1_governanca/mutantes_excecao_preview.py [saida.json]

Cada mutante estraga UMA linha da guarda em `leis/fundacao_da_coleta.py` — o
vazamento para producao, o escopo que alarga, a Sala que se escreve, o objeto
nao liberado que passa, a D140 que deixa de contar — e corre
`tests.test_excecao_preview_e2e`. Mutante MORTO = a suite reprovou.

Reversivel e local: escreve so no ficheiro da lei, desfaz no fim de cada
mutante e confere o sha256 byte a byte. Zero rede, zero Git.
Cada corrida usa uma pasta de .pyc propria: um mutante do mesmo tamanho no
mesmo segundo nao pode ser servido pelo .pyc do original.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALVO = os.path.join(RAIZ, "leis", "fundacao_da_coleta.py")
SUITE = "tests.test_excecao_preview_e2e"

# (nome, pergunta da missao, trecho original, trecho mutado)
MUTANTES = [
    ("M01_excecao_destrava_a_inteligencia", "a",
     "    if COLLECTION_FOUNDATION_CLOSED:\n        return True, 'COLLECTION_FOUNDATION_CLOSED=SIM",
     "    if COLLECTION_FOUNDATION_CLOSED or excecao_vigente(*carregar()[:2]):\n        return True, 'COLLECTION_FOUNDATION_CLOSED=SIM"),
    ("M02_entrada_que_fecha_a_fundacao_vale", "a",
     "or e.get('NAO_FECHA_A_FUNDACAO') is not True:", ":"),
    ("M03_branch_de_producao_aceite", "b",
     "if not ramo or ramo_de_producao(ramo, publicacao):", "if not ramo:"),
    ("M04_host_canonico_aceite", "b",
     "if host and host == publicacao.get('CANONICAL_HOST'):", "if False:"),
    ("M05_contrato_alarga_o_escopo", "b",
     "tipos = set(DESTINOS_DO_PREVIEW) & set(", "tipos = set(DESTINOS_DO_PREVIEW) | set("),
    ("M06_para_cliente_aceite", "b",
     "if d.get('PARA_CLIENTE') is not False:", "if d.get('PARA_CLIENTE') is True:"),
    ("M07_build_local_com_host_publico", "b",
     "if d.get('TIPO') == 'BUILD_LOCAL' and host not in HOSTS_LOCAIS:", "if False:"),
    ("M08_artefatos_autorizados_em_producao", "b",
     "if e is None or any(ramo_de_producao(r, publicacao) for r in ramos):", "if e is None:"),
    ("M09_objeto_nao_liberado_passa", "c",
     "if o.get('LIBERACAO') != LIBERADO:", "if False:"),
    ("M10_conferencia_falhada_passa", "c",
     "elif any(c.get(k) != 'PASSOU' for k in CONFERENCIAS_QUE_PASSAM):", "elif False:"),
    ("M11_sem_decisao_do_dono_passa", "c",
     "elif not c8.strip() or c8.startswith('FALHOU'):", "elif False:"),
    ("M12_gates_do_pote_v2_saltados", "c",
     "violacoes = validar(pote)", "violacoes = []"),
    ("M13_pote_vazio_passa", "c",
     "if n == 0:", "if False:"),
    ("M14_escrever_na_sala_aceite", "d",
     "if pedido.get('OPERACAO') != PUBLICAR_NO_PREVIEW:",
     "if pedido.get('OPERACAO') not in (PUBLICAR_NO_PREVIEW, 'ESCREVER_NA_SALA', 'MARCAR_CONSUMIDO_EM', None):"),
    ("M15_sala_real_sem_read_only", "d",
     "if ent.get('TIPO') != ENTRADA_READ_ONLY or ent.get('READ_ONLY') is not True:", "if False:"),
    ("M16_sem_prova_reversa_do_lab", "d",
     "if lab.get('VEREDITO') != 'PASS' or not str(lab.get('ONDE') or '').strip():", "if False:"),
    ("M17_d140_fora_do_diario_vale", "e",
     "if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW or MARCA_NO_DIARIO not in diario:",
     "if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW:"),
    ("M18_outra_autoridade_vale", "e",
     "if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW or MARCA_NO_DIARIO not in diario:",
     "if MARCA_NO_DIARIO not in diario:"),
    ("M19_revogada_vale", "e",
     "if e.get('REVOGADA') is not False or", "if e.get('REVOGADA') is True or"),
    ("M20_sem_excecao_passa_igual", "e",
     "    if e is None:\n        return False, '%s · sem a excecao",
     "    if False:\n        return False, '%s · sem a excecao"),
    ("M22_ambito_exato_ignorado", "e",
     "        if any(ambito.get(k) != v for k, v in AMBITO_EXATO.items()):\n            return None\n",
     ""),
    ("M23_consumido_em_aceite", "d",
     "if any(k in pedido for k in ('CONSUMIDO_EM', 'MARCAR_CONSUMIDO_EM')):", "if False:"),
    ("M21_excecao_removida_da_guarda", "f",
     "    return True, ('EXCECAO %s (%s)", "    return False, ('EXCECAO %s (%s)"),
]


def _sha(caminho):
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _correr_suite():
    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = tempfile.mkdtemp(prefix="mut-l1-")
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        env[k] = "http://127.0.0.1:9"
    r = subprocess.run([sys.executable, "-m", "unittest", SUITE], cwd=RAIZ, env=env,
                       capture_output=True, text=True, timeout=600)
    return r.returncode == 0, r.stderr


def main(argv):
    with open(ALVO, "rb") as f:
        original = f.read()
    sha0 = _sha(ALVO)
    texto = original.decode("utf-8")

    passou, _ = _correr_suite()
    if not passou:
        print("ABORTA: a suite ja reprova sem mutante nenhum; nao se prova nada assim.")
        return 2

    res = []
    for nome, pergunta, antes, depois in MUTANTES:
        n = texto.count(antes)
        if n != 1:
            res.append({"MUTANTE": nome, "PERGUNTA": pergunta, "ESTADO": "NAO_APLICADO",
                        "PORQUE": "o trecho aparece %d vezes" % n})
            continue
        try:
            with open(ALVO, "wb") as f:
                f.write(texto.replace(antes, depois).encode("utf-8"))
            vivo, erro = _correr_suite()
        finally:
            with open(ALVO, "wb") as f:
                f.write(original)
        falhas = [l.split(" (")[0].replace("FAIL: ", "").replace("ERROR: ", "")
                  for l in erro.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res.append({"MUTANTE": nome, "PERGUNTA": pergunta,
                    "ESTADO": "SOBREVIVEU" if vivo else "MORTO", "MORTO_POR": falhas[:5]})
        print("%-40s (%s) %s" % (nome, pergunta, res[-1]["ESTADO"]))

    desfeito = _sha(ALVO) == sha0
    mortos = sum(1 for r in res if r["ESTADO"] == "MORTO")
    saida = {"ALVO": "leis/fundacao_da_coleta.py", "SHA256_DO_ALVO": sha0, "SUITE": SUITE,
             "MUTANTES": len(MUTANTES), "MORTOS": mortos, "DESFEITO_E_CONFERIDO": desfeito,
             "RESULTADOS": res}
    print("MORTOS %d/%d · alvo desfeito e conferido: %s" % (mortos, len(MUTANTES),
                                                           "SIM" if desfeito else "NAO <-- GRAVE"))
    if len(argv) > 1:
        with open(argv[1], "w", encoding="utf-8") as f:
            json.dump(saida, f, ensure_ascii=False, indent=1)
    return 0 if (mortos == len(MUTANTES) and desfeito) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
