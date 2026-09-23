"""Resolucao PROPOSTA dos conflitos de codigo ponte <- servico (missao 5-PREP-b).

Escreve SO na worktree de ensaio passada em argumento (nunca numa lane).
Para cada ficheiro: tres vias com a base CERTA, depois cada bloco de conflito
recebe a escolha registada em ESCOLHAS (com o porque), depois os remendos
semanticos que o merge limpo nao ve.

Uso:  py ferramentas/unificacao/resolver_conflitos.py <worktree-de-ensaio>
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PONTE = "2018ed6a"
SERVICO = os.environ.get("UNIF_SERVICO", "9a82197c")  # missao 5: +gatilho ocioso (era 779ac8f6 no ensaio)
# A ponte recebeu estes tres por COPIA de candidate-bridge-v1 (63b71421, commit
# 5b6068cf), nao por merge: para o git sao add/add contra 8bbea01c. A base
# verdadeira e 63b71421, que esta na historia do servico. Com ela: 0 conflitos.
BASE_REAL = {
    "curadoria/descobrir.py": "63b71421",
    "curadoria/test_discovery.py": "63b71421",
    "curadoria/test_ponte_candidatas.py": "63b71421",
}
BASE_COMUM = "8bbea01c"

# P = lado da ponte, S = lado do servico, ou funcao(p, s) -> texto
ESCOLHAS = {
    "curadoria/supervisor.py": [
        # 1 docstring do hook_fila_vazia: a da ponte descreve o comportamento
        #   real (so e chamado em volta IDLE); a do servico diz «abaixo do
        #   limiar», que e o que o GATILHO decide, nao o supervisor.
        "P",
        # 2 chamada do hook: mesmo comportamento; a da ponte anota o TIPO da
        #   excecao. O abastecimento do servico (gatilho_discovery) passa pelo
        #   mesmo parametro, entao fica preservado.
        "P",
        # 3 docstring de ler_estado_servico: fica a do servico (e o codigo que
        #   fica) + o paragrafo da ponte sobre o diagnostico.
        lambda p, s: s.rstrip("\n").rstrip('"').rstrip() + (
            "\n\n    SERVICE_DIAGNOSIS guarda o vocabulario da ponte (RUNNING / IDLE /\n"
            "    STOPPED_FINISHED / STOPPED_BROKEN / BLOCKED / UNKNOWN): o rotulo do\n"
            "    ficheiro confrontado com o SO. SOURCE_CURATOR_SERVICE continua a ser\n"
            "    o rollup do servico (RUNNING / STOPPED / BLOCKED), que a telemetria\n"
            "    em producao le.\n    \"\"\"\n"),
        # 4 liveness: estrutura do SERVICO (em producao; telemetria.py le
        #   WORKER_STATE/SUPERVISOR_STATE) + a verificacao da ponte de que o
        #   PID e mesmo python (PID reciclado pelo Windows nao conta como vivo).
        lambda p, s: s.replace(
            "bool(worker_pid and _pid_no_so(worker_pid))",
            "bool(worker_pid and _pid_no_so(worker_pid) and _proc_e_python(worker_pid))").replace(
            "bool(sup_pid and _pid_no_so(sup_pid))",
            "bool(sup_pid and _pid_no_so(sup_pid) and _proc_e_python(sup_pid))"),
        # 5 batimento: servico (hb_stale); a ponte deriva-se dele em 6.
        "S",
        # 6 estado: servico + o diagnostico da ponte calculado ao lado.
        lambda p, s: s + (
            "\n    # --- DIAGNOSTICO DA PONTE: o rotulo do ficheiro contra o SO ---\n"
            "    ficheiro = estado_gravado if s else \"UNKNOWN\"\n"
            "    if ficheiro == \"RUNNING\":\n"
            "        diagnostico = \"RUNNING\" if (worker_alive and sup_vivo) else \"STOPPED_BROKEN\"\n"
            "    elif ficheiro == \"IDLE\":\n"
            "        diagnostico = \"IDLE\" if sup_vivo else \"STOPPED_BROKEN\"\n"
            "    elif ficheiro == \"STOPPED\":\n"
            "        diagnostico = \"STOPPED_FINISHED\"\n"
            "    elif ficheiro == \"BLOCKED\":\n"
            "        diagnostico = \"BLOCKED\"\n"
            "    elif ficheiro == \"STARTING\":\n"
            "        diagnostico = \"RUNNING\" if sup_vivo else \"STOPPED_BROKEN\"\n"
            "    else:\n"
            "        diagnostico = \"UNKNOWN\"\n"),
        # 7 chaves devolvidas: todas as do servico + as da ponte com nome proprio.
        lambda p, s: s + (
            "        \"SERVICE_DIAGNOSIS\":         diagnostico,\n"
            "        \"SERVICE_STATE_IN_FILE\":     ficheiro,\n"
            "        \"SERVICE_STATE_MEASURED_VIA\": \"tasklist PID + nome de imagem python + batimento no run log\",\n"
            "        \"HEARTBEAT_FRESH\":           (not hb_stale) if hb_idade is not None else None,\n"),
    ],
    "curadoria/status_live.py": [
        # 1 ficam as quatro funcoes: _nivel_da_fila e _status_discovery da
        #   ponte (sem os literais 18 e 0 que pareciam medicao), _rendimento e
        #   _ready_sources_24h do servico (observabilidade em producao).
        #   Ninguem fora do painel le CANDIDATES_TOTAL/QUEUE_DEPTH (medido).
        lambda p, s: p + s[s.index("def _rendimento"):s.index("def _status_discovery")],
    ],
    "curadoria/test_supervisor.py": [
        # 1 a classe Isolado da ponte isola FILA, LIVRO, LOCK, ESTADO, PARAR e
        #   DIARIO e troca o lancador por um processo inerte — contem o
        #   isolamento da fila que o servico acrescentou, e mais.
        "P",
        # 2 (so com o servico >= 9a82197c, gatilho ocioso) o processo morto do
        #   test_crash_com_progresso: o ajudante _popen da ponte (pipes iguais
        #   aos do lancador) com o CODIGO do servico — rc 1, porque desde o
        #   gatilho ocioso rc 0 e «saida limpa», nao crash, e o teste deixaria
        #   de medir a morte com progresso.
        lambda p, s: p.replace('self._popen("pass")',
                               'self._popen("import sys; sys.exit(1)")  # crash: rc 0 e saida limpa'),
    ],
}


def remendos(raiz: Path) -> list:
    """Defeitos que o merge LIMPO nao mostra. Devolve o que foi feito."""
    feito = []
    sl = raiz / "curadoria/status_live.py"
    t = sl.read_text(encoding="utf-8")
    # o servico chama _status_discovery() em _disc e a ponte em **_status_discovery():
    # depois do merge o painel mede duas vezes. Fica a variavel.
    if "        **_status_discovery(),\n" in t and "**_disc," in t:
        t = t.replace("        **_status_discovery(),\n", "", 1)
        feito.append("status_live: chamada duplicada de _status_discovery removida")
    sl.write_text(t, encoding="utf-8", newline="\n")
    # os testes da ponte sobre o diagnostico leem a chave nova
    tp = raiz / "curadoria/test_painel_pergunta_ao_so.py"
    if tp.exists():
        u = tp.read_text(encoding="utf-8")
        u2 = u.replace('["SOURCE_CURATOR_SERVICE"]', '["SERVICE_DIAGNOSIS"]')
        if u2 != u:
            tp.write_text(u2, encoding="utf-8", newline="\n")
            feito.append("test_painel_pergunta_ao_so: le SERVICE_DIAGNOSIS")
    feito += _telemetria_com_nome_proprio(raiz)
    feito += _testes_do_servico_no_isolamento_da_ponte(raiz)
    feito += _pasta_descartavel(raiz)
    return feito


def _telemetria_com_nome_proprio(raiz: Path) -> list:
    """O servico criou curadoria/telemetria.py; a casa ja tinha leis/telemetria.py
    (ESTADOS_DE_ETAPA, lido por coleta/ e admissao/). Na mesma corrida de testes
    o primeiro importado tapa o outro: rastro_da_coleta rebenta com
    AttributeError. O do servico passa a telemetria_do_curador."""
    velho = raiz / "curadoria/telemetria.py"
    if not velho.exists():
        return []
    velho.rename(raiz / "curadoria/telemetria_do_curador.py")
    mud = ["curadoria/telemetria.py -> curadoria/telemetria_do_curador.py"]
    for f in sorted((raiz / "curadoria").glob("*.py")):
        t = f.read_text(encoding="utf-8")
        u = re.sub(r"^(\s*)from telemetria import ", r"\1from telemetria_do_curador import ", t, flags=re.M)
        u = re.sub(r"^(\s*)import telemetria as ", r"\1import telemetria_do_curador as ", u, flags=re.M)
        u = re.sub(r"^(\s*)import telemetria\s*$", r"\1import telemetria_do_curador as telemetria", u, flags=re.M)
        if u != t:
            f.write_text(u, encoding="utf-8", newline="\n")
            mud.append("import corrigido: %s" % f.name)
    # (missao 5) o red team da telemetria nomeia o FICHEIRO a mutar por texto:
    # com o nome velho, cada mutante falhava a abrir o alvo — o red team
    # deixava de atacar sem nenhum import partido que o denunciasse.
    rt = raiz / "curadoria/red_team_telemetria.py"
    if rt.exists():
        t = rt.read_text(encoding="utf-8")
        u = re.sub(r'^(\s*)"telemetria\.py",', r'\1"telemetria_do_curador.py",', t, flags=re.M)
        if u != t:
            rt.write_text(u, encoding="utf-8", newline="\n")
            mud.append("red_team_telemetria: alvo das mutacoes -> telemetria_do_curador.py")
    return mud


CLASSES_DO_SERVICO = ("TestCrawlMesmaUrlDuasSementes", "TestOrcamentoEsgotadoParaLimpo",
                      "TestSementeJaVisitadaNaoRevisitada")


def _testes_do_servico_no_isolamento_da_ponte(raiz: Path) -> list:
    """Tres testes do servico usam _ContextoLimpo (guardar e restaurar a fila REAL);
    a ponte trocou-o por Isolada (pasta descartavel + rede proibida) e apagou-o.
    Os tres passam a herdar Isolada e perdem o `with`."""
    f = raiz / "curadoria/test_discovery.py"
    linhas = f.read_text(encoding="utf-8").split("\n")
    out, feito, dentro, ind_with = [], [], False, None
    for l in linhas:
        m = re.match(r"^class (\w+)\(unittest\.TestCase\):", l)
        if m:
            dentro = m.group(1) in CLASSES_DO_SERVICO
            if dentro:
                l = "class %s(Isolada):" % m.group(1)
                feito.append("test_discovery: %s herda Isolada" % m.group(1))
        elif l.startswith("class "):
            dentro = False
        if dentro and l.strip() == "with _ContextoLimpo():":
            ind_with = len(l) - len(l.lstrip())
            continue
        if ind_with is not None:
            ind = len(l) - len(l.lstrip())
            if l.strip() and ind <= ind_with:
                ind_with = None
            elif l.strip():
                l = l[4:]
        out.append(l)
    f.write_text("\n".join(out), encoding="utf-8", newline="\n")
    return feito


def _pasta_descartavel(raiz: Path) -> list:
    """A guarda da ponte (test_zz_guarda_isolamento) exige TemporaryDirectory em
    todo o teste que toca estado; dois testes do servico usam mkdtemp e nunca
    apagam a pasta."""
    feito = []
    for nome in ("test_status_liveness.py", "test_worker_qualify.py"):
        f = raiz / "curadoria" / nome
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        u = re.sub(r"Path\(tempfile\.mkdtemp\(prefix=(\"[^\"]+\")\)\)",
                   r"Path(self.enterContext(tempfile.TemporaryDirectory(prefix=\1)))", t)
        if u != t:
            f.write_text(u, encoding="utf-8", newline="\n")
            feito.append("%s: mkdtemp -> TemporaryDirectory (apagada no fim)" % nome)
    return feito


def mostrar(ref, caminho):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, caminho)], capture_output=True)
    return r.stdout if r.returncode == 0 else b""


BLOCO = re.compile(r"^<<<<<<< PONTE\n(.*?)^\|\|\|\|\|\|\| BASE\n.*?^=======\n(.*?)^>>>>>>> SERVICO\n",
                   re.S | re.M)


def resolver(raiz: Path) -> dict:
    rel = {}
    for f in sorted(set(BASE_REAL) | set(ESCOLHAS) | {"curadoria/worker.py"}):
        tmp = Path(tempfile.mkdtemp(prefix="res-"))
        a, o, b = tmp / "a", tmp / "o", tmp / "b"
        a.write_bytes(mostrar(PONTE, f).replace(b"\r\n", b"\n"))
        o.write_bytes(mostrar(BASE_REAL.get(f, BASE_COMUM), f).replace(b"\r\n", b"\n"))
        b.write_bytes(mostrar(SERVICO, f).replace(b"\r\n", b"\n"))
        r = subprocess.run(["git", "merge-file", "--diff3", "-L", "PONTE", "-L", "BASE", "-L", "SERVICO",
                            str(a), str(o), str(b)])
        texto = a.read_text(encoding="utf-8")
        esc = ESCOLHAS.get(f, [])
        blocos = BLOCO.findall(texto)
        if len(blocos) != len(esc):
            raise SystemExit("%s: %d blocos, %d escolhas — a entrada mudou, rever" % (f, len(blocos), len(esc)))
        it = iter(esc)

        def troca(m):
            e = next(it)
            p, s = m.group(1), m.group(2)
            return p if e == "P" else s if e == "S" else e(p, s)
        texto = BLOCO.sub(troca, texto)
        (raiz / f).write_text(texto, encoding="utf-8", newline="\n")
        rel[f] = {"base": BASE_REAL.get(f, BASE_COMUM), "blocos": len(blocos)}
    rel["REMENDOS"] = remendos(raiz)
    return rel


if __name__ == "__main__":
    import json
    print(json.dumps(resolver(Path(sys.argv[1])), indent=1, ensure_ascii=False))
