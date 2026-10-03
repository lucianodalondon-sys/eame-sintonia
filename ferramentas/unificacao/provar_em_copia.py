"""Passo 4 da missao 5: as provas da ponte e do supervisor numa COPIA descartavel.

    py ferramentas/unificacao/provar_em_copia.py <ref> <saida.json>

- `git worktree add --detach` em %TEMP%; a fila fica VAZIA (a suite e as provas
  do curator lancam worker real, que le a fila do disco e bateria a rede);
- nenhum PID vivo e tocado: a copia nao tem SUPERVISOR-STATE, SUPERVISOR.lock
  nem PARAR.flag (estao no .gitignore), e o supervisor so e exercitado por
  `uma_volta_sup` com o lancador trocado por um processo inerte;
- corre:
    1. curadoria/provar_ponte_curador.py         (a ponte nos dois sentidos)
    2. curadoria/red_team_ponte_curador.py       (SURVIVORS tem de ser 0)
    3. supervisor.py --estado e ponte_automatica.py --saude (so leitura)
    4. uma volta do supervisor observada: fila vazia -> IDLE, hook chamado,
       nenhum worker lancado; e o worker ocioso (rc 0) nao conta como crash.
    5. (2.a passagem) os modulos de prova do gatilho ocioso, do worker pendurado
       e das sementes da discovery; e os dois ENSAIOS reais (supervisor e worker
       verdadeiros) numa segunda copia SEM .git (git archive | tar), que e a
       unica onde eles aceitam correr.
- remove a worktree no fim.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VOLTA = r'''
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, "curadoria")
import supervisor as S
lancados = []
def inerte(pausa=1.0):
    lancados.append(1)
    return subprocess.Popen([sys.executable, "-c", "pass"])
S._lancar_worker = inerte
estado = {"CRASHES_SEM_PROGRESSO": [], "RESTARTS": 0, "WORKER_PID": None,
          "SUPERVISOR_STATE": "RUNNING"}
chamadas = []
accao, estado, proc = S.uma_volta_sup(estado, None, pausa_worker=0.1,
                                      hook_fila_vazia=lambda: chamadas.append(1))
# o worker ocioso sai com rc 0: nao e crash
p = subprocess.Popen([sys.executable, "-c", "pass"]); p.wait()
est2 = {"CRASHES_SEM_PROGRESSO": [], "RESTARTS": 0, "WORKER_PID": p.pid,
        "SUPERVISOR_STATE": "RUNNING"}
accao2, est2, _ = S.uma_volta_sup(est2, p, pausa_worker=0.1, hook_fila_vazia=lambda: None)
print(json.dumps({"ACCAO_FILA_VAZIA": accao, "HOOK_CHAMADO": len(chamadas),
                  "WORKERS_LANCADOS": len(lancados),
                  "ACCAO_DEPOIS_DE_SAIDA_LIMPA": accao2,
                  "CRASHES_DEPOIS_DE_SAIDA_LIMPA": len(est2.get("CRASHES_SEM_PROGRESSO", []))}))
'''


def git(cwd, *a, ok=(0,)):
    p = subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode not in ok:
        raise SystemExit("git %s: %s%s" % (a, p.stdout[-800:], p.stderr[-800:]))
    return p


def correr(wt, args, timeout=3000):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=str(Path.home() / ".sintonia-libs"))
    p = subprocess.run([sys.executable, *args], cwd=str(wt), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=timeout)
    out = (p.stdout + "\n" + p.stderr).replace("Could not find platform independent libraries <prefix>\n", "")
    return {"RC": p.returncode, "FIM": out.strip().splitlines()[-25:]}


def main(ref, saida):
    raiz = Path(git(Path(__file__).parent, "rev-parse", "--show-toplevel").stdout.strip())
    sha = git(raiz, "rev-parse", ref).stdout.strip()
    wt = Path(tempfile.gettempdir()) / ("provar-copia-%s" % sha[:8])
    if wt.exists():
        git(raiz, "worktree", "remove", "--force", str(wt), ok=(0, 128))
        shutil.rmtree(wt, ignore_errors=True)
    git(raiz, "worktree", "add", "-q", "--detach", str(wt), sha)
    doc = {"REF": ref, "SHA": sha}
    try:
        (wt / "curadoria/LIFECYCLE-QUEUE-V1.json").write_text(
            json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")
        doc["PONTE_PROOF"] = correr(wt, ["curadoria/provar_ponte_curador.py"])
        doc["RED_TEAM_PONTE"] = correr(wt, ["curadoria/red_team_ponte_curador.py"])
        doc["SUPERVISOR_ESTADO"] = correr(wt, ["curadoria/supervisor.py", "--estado"], 120)
        doc["PONTE_SAUDE"] = correr(wt, ["curadoria/ponte_automatica.py", "--saude"], 120)
        doc["SUPERVISOR_VOLTA"] = correr(wt, ["-c", VOLTA], 300)
        doc["MODULOS_DE_PROVA"] = correr(wt, ["-m", "unittest", "-v", "curadoria.test_gatilho_ocioso",
                                              "curadoria.test_worker_pendurado",
                                              "curadoria.test_discovery_sementes",
                                              # 3.a passagem
                                              "curadoria.test_fila_windows",
                                              "curadoria.test_travao_sementes",
                                              "curadoria.test_decisao_semantica",
                                              "curadoria.test_pais_das_candidatas",
                                              "curadoria.test_contrato_unico",
                                              "curadoria.test_ponte_promocao",
                                              "curadoria.test_ponte_candidatas",
                                              "curadoria.test_livros_reais_intactos",
                                              "tests.test_admissao_multilingue",
                                              "tests.test_retirada_por_decisao",
                                              "tests.test_aplicar_desbloqueio",
                                              "tests.test_ld2_aditamento"], 3000)
        # os testes da politica NAO SEI e da quarentena (Q1), por padrao de nome: a
        # regra da Q1 conta como chamador todo o ficheiro que escreve o nome dela.
        doc["MODULOS_NAO_SEI"] = correr(wt, ["-m", "unittest", "discover", "-v", "-s", "tests",
                                             "-p", "test_*na*sei*.py"], 1800)
        for f in ("provas/recollection_http_local.mjs", "provas/recollection_indice_local.mjs",
                  "provas/recollection_timeout_local.mjs"):
            if (wt / f).exists():
                p = subprocess.run(["node", f], cwd=str(wt), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=900)
                doc.setdefault("PROVAS_NODE_R1_R2", {})[f] = {
                    "RC": p.returncode, "FIM": (p.stdout + p.stderr).strip().splitlines()[-6:]}
        snaps = sorted((Path.home() / "sintonia-gabarito").glob("B1-SNAPSHOT-*"))
        if snaps and (wt / "medidas/prova_b2_ponte_em_copia.py").exists():
            doc["PONTE_B2_PROMOCAO_DESPROMOCAO"] = correr(
                wt, ["medidas/prova_b2_ponte_em_copia.py", str(snaps[-1])], 1800)
        doc["COPIA_SUJA_DEPOIS"] = git(wt, "status", "--short").stdout.splitlines()[:40]
        arq = Path(tempfile.gettempdir()) / ("ensaio-tar-%s" % sha[:8])
        shutil.rmtree(arq, ignore_errors=True)
        arq.mkdir(parents=True)
        tar = subprocess.run("git archive %s | tar -x -C \"%s\"" % (sha, arq.as_posix()), shell=True,
                             cwd=str(raiz), capture_output=True, text=True)
        doc["COPIA_TAR"] = {"RC": tar.returncode, "TEM_GIT": (arq / ".git").exists()}
        try:
            (arq / "curadoria/LIFECYCLE-QUEUE-V1.json").write_text(
                json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")
            doc["ENSAIO_WORKER_PENDURADO"] = correr(
                arq, ["curadoria/ensaiar_worker_pendurado.py", "--sou-uma-copia"], 1800)
            doc["ENSAIO_GATILHO_OCIOSO"] = correr(
                arq, ["curadoria/ensaiar_gatilho_ocioso.py", "--sou-uma-copia"], 1800)
            if (arq / "curadoria/ensaiar_fila_windows.py").exists():
                (arq / "curadoria/LIFECYCLE-QUEUE-V1.json").write_text(
                    json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")
                doc["ENSAIO_FILA_WINDOWS"] = correr(
                    arq, ["curadoria/ensaiar_fila_windows.py", "--sou-uma-copia"], 1800)
        finally:
            shutil.rmtree(arq, ignore_errors=True)
        doc["COPIA_TAR_REMOVIDA"] = not arq.exists()
    finally:
        git(raiz, "worktree", "remove", "--force", str(wt), ok=(0, 128))
        git(raiz, "worktree", "prune")
    doc["WORKTREE_REMOVIDA"] = not wt.exists()
    for f, r in doc.get("PROVAS_NODE_R1_R2", {}).items():
        print("== NODE", f, "rc=%s" % r["RC"], " | ".join(r["FIM"][-2:]))
    Path(saida).write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    for k in ("PONTE_PROOF", "RED_TEAM_PONTE", "SUPERVISOR_ESTADO", "PONTE_SAUDE", "SUPERVISOR_VOLTA",
              "MODULOS_DE_PROVA", "MODULOS_NAO_SEI", "PONTE_B2_PROMOCAO_DESPROMOCAO", "ENSAIO_WORKER_PENDURADO",
              "ENSAIO_GATILHO_OCIOSO", "ENSAIO_FILA_WINDOWS"):
        if k not in doc:
            print("==", k, "NAO CORREU")
            continue
        print("==", k, "rc=%s" % doc[k]["RC"])
        print("\n".join(doc[k]["FIM"][-8:]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
