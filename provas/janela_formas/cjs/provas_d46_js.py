"""D46 condicao (1), sem chave: le os 2 JS do tema de agrometeopuglia para ver se algum poe drupalSettings.api.
Portao PASS IT; robots guardado em d46/ (lido pelo leitor da casa ha minutos); 5 s de pausa; conta D38 = 2 ja + 2."""
import hashlib, subprocess, sys, time, urllib.robotparser
from pathlib import Path
sys.path.insert(0, "C:/Users/London1/orca/workspaces/eame-sintonia/janela-formas-v1/curadoria")
import canario as CAN, gate_de_rota as GATE
r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py", "--portao-de-egresso", "IT"], capture_output=True, text=True)
assert '"EGRESS_GATE": "PASS"' in r.stdout
rp = urllib.robotparser.RobotFileParser(); rp.parse(Path("C:/cur/cjs/d46/robots-www.agrometeopuglia.it.txt").read_text(encoding="utf-8").splitlines())
for nome in ("custom.js", "extend_home.js"):
    u = "https://www.agrometeopuglia.it/themes/drupal8_zymphonies_theme/js/%s?tlijto" % nome
    assert GATE.permitido(u, rp), u
    time.sleep(5)
    st, b, e = CAN.buscar(u)
    Path("C:/cur/cjs/d46/" + nome).write_bytes(b)
    print(st, len(b), hashlib.sha256(b).hexdigest(), u)
