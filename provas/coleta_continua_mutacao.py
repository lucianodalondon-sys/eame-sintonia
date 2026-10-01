"""COLETA-CONTINUA · o ataque: cada guarda do agendador por fonte desligada, uma de cada vez, numa COPIA.

    py provas/coleta_continua_mutacao.py [--ref=HEAD] [--lote=M30,M31,...]

O metodo e o de `provas/rodadas_mutacao.py`: a copia sai de `git archive <ref>` (o repositorio nao e tocado);
cada mutante troca UM trecho exacto de `ferramentas/big_collection/coleta_continua.py`; um trecho que nao
exista uma vez so falha alto. MORTO = `tests/test_coleta_continua.py` reprova ou sai com codigo != 0.
Resultado em `provas/COLETA-CONTINUA-MUTACAO.json`.

D124-REBASE (28/09): M01, M02, M04 e M17 tinham como ancora o texto do codigo de antes da cortesia adaptativa
(`teto` fixo, janela sempre ligada). As ancoras passaram a ser as do codigo portado — o MESMO defeito plantado
no mesmo sitio (janela ignorada, +1 no teto do ciclo, orcamento nao partilhado, teto de 24 h ignorado).
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALVO = "ferramentas/big_collection/coleta_continua.py"
TESTE = "tests/test_coleta_continua.py"
MUTANTES = [
    # os cinco pedidos da missao
    ("M01_DOMINIO_BLOQUEADO_PASSA", ALVO, "if janela_h and v and agora_utc < v + timedelta(hours=janela_h):", "if False:"),
    ("M02_TETO_6_NO_CICLO", ALVO, "if g + orcamento.get(dd, 0) + p > nivel:", "if g + orcamento.get(dd, 0) + p > nivel + 1:"),
    ("M03_PORTAO_IT_PULADO", ALVO, 'if not reg["EGRESSO_ANTES"].get("PASSA"):', "if False:"),
    ("M04_DUAS_LINHAS_SEM_ORCAMENTO_PARTILHADO", ALVO, "orcamento=orcamento, max_fontes=max_fontes, janela_h=janela_h)",
     "orcamento={}, max_fontes=max_fontes, janela_h=janela_h)"),
    ("M05_ROBO_DEIXADO_PARADO", ALVO, "                robo.lancar()\n", ""),
    # o resto das guardas
    ("M06_ROBO_PARADO_QUANDO_O_CICLO_PARA", ALVO, "    finally:\n        if parei:", "    finally:\n        if parei and para is None:"),
    ("M07_FLAG_DE_OUTRO_TIRADA", ALVO, 'if not r0["FLAG"]:\n        robo.parar()', "if True:\n        robo.parar()"),
    ("M08_ROBO_QUE_NAO_PARA_IGNORADO", ALVO, 'if r0["VIVO"] and not robo.esperar(False):', "if False:"),
    ("M09_ROBO_TOCADO_SEM_FONTES", ALVO, "if a_seco or not correm:", "if a_seco:"),
    ("M10_PORTAO_DEPOIS_PULADO", ALVO, 'if not reg["EGRESSO_DEPOIS"].get("PASSA"):', "if False:"),
    ("M11_PROVA_TETO_IGNORADA", ALVO, 'if p["ESTADO"] != "PASS":', "if False:"),
    ("M12_PROVA_TETO_NAO_SEI_FECHA", ALVO, 'if p["ESTADO"] != "PASS":', 'if p["ESTADO"] == "FAIL":'),
    ("M13_PROVA_24H_IGNORADA", ALVO, 'if p24["ESTADO"] != "PASS":', "if False:"),
    ("M14_RAM_IGNORADA", ALVO, "if ram < RAM_MINIMA_GB:", "if False:"),
    ("M15_RAM_NAO_SEI_PASSA", ALVO, 'if ram is None:\n        return fim("RAM_NAO_SEI")', "if ram is None:\n        ram = 99.0"),
    ("M16_BACKUP_IGNORADO", ALVO, 'if not reg["BACKUP"].get("PROVA_VALE"):', "if False:"),
    ("M17_TETO_24H_IGNORADO", ALVO, "if g + p > nivel:", "if False:"),
    ("M18_LIVRO_24H_ILEGIVEL_VIRA_VAZIO", ALVO, '        return fim("LIVRO_24H_NAO_SEI", ERRO=str(ex)[:300])', "        reservas = []"),
    ("M19_PARADO_NAO_FICA_PARADO", ALVO, 'if estado.get("PAROU") and not a_seco:', "if False:"),
    ("M20_LINHA_NAO_LIGADA_CORRE", ALVO, 'if not lig["LIGADA"]:', "if False:"),
    ("M21_CODIGO_DA_ONDA_IGNORADO", ALVO, 'if codigos[n] != 0 or e.get("PAROU"):', 'if e.get("PAROU"):'),
    ("M22_RECONCILIACAO_IGNORADA", ALVO, 'if rec.get("ESTADO") != "PASS":', "if False:"),
    ("M23_SO_O_DOMINIO_DO_PLANO", ALVO, 'for d in c["DOMINIOS"]:\n            v = ultima.get(d)',
     'for d in [c["DOMINIO"]]:\n            v = ultima.get(d)'),
    ("M24_FEITAS_REPETEM", ALVO, 'if c["SOURCE_ID"] in feitas:\n            continue', 'if c["SOURCE_ID"] in feitas:\n            pass'),
    ("M25_RODIZIO_PARADO", ALVO, "k = n_ciclo % len(nomes)", "k = 0"),
    ("M26_ONDA_SEM_O_LIVRO_24H", ALVO, 'os.environ["SINTONIA_TETO_24H"] = str(livro_24h)', "pass"),
    ("M27_LIGACAO_PELO_NOME", ALVO, 'if linha["CHAMADA"] not in f.read_text(encoding="utf-8", errors="replace"):',
     'if "reserva" not in f.read_text(encoding="utf-8", errors="replace"):'),
    ("M28_ERRO_NAO_PARA", ALVO, 'para = "ERRO_NO_CICLO: %r" % (ex,)', "para = None"),
    ("M29_INTERRUPTOR_IGNORADO", ALVO, "if (base / DESLIGAR_F).exists():", "if False:"),
    # SERVICO-TRINCO (30/09): pelo menos uma por regra nova do trinco e da prova de backup
    ("M30_TOMADA_NAO_ATOMICA_DO_C38610E0C", ALVO,
     "        vez = _vez_de_tomar(base)\n        if vez is None:\n            return None\n        morto = None\n"
     "        try:\n            if not _trinco_de_dono_morto(t):\n                return None\n"
     '            morto = base / ("%s.morto-%d-%s" % (TRINCO_F, os.getpid(), secrets.token_hex(4)))\n'
     "            os.rename(t, morto)\n            os.mkdir(t)\n            return _escrever_dono(t)\n"
     "        finally:\n            _largar_a_vez(vez)\n            if morto is not None:\n"
     "                shutil.rmtree(morto, ignore_errors=True)\n",
     '        (t / "DONO.json").unlink(missing_ok=True)\n        os.rmdir(t)\n        os.mkdir(t)\n'
     "        return _escrever_dono(t)\n"),
    ("M31_TOMADA_SEM_VEZ", ALVO, "            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)\n", "            pass\n"),
    ("M32_TOMADA_SEM_RELER_COM_A_VEZ", ALVO,
     "            if not _trinco_de_dono_morto(t):\n                return None\n            morto = base",
     "            morto = base"),
    ("M33_STILL_ACTIVE_259_IGNORADO", ALVO, "            return codigo.value == 259\n", "            return True\n"),
    ("M34_ACESSO_NEGADO_VIRA_MORTO", ALVO, "            return ctypes.get_last_error() != 87\n", "            return False\n"),
    ("M35_PID_IMPOSSIVEL_TOMADO", ALVO, "    if type(pid) is not int or pid <= 0:\n        return False\n", ""),
    # ADENDO-PARADA (01/10, ciclo 146): (1) o agendador pergunta ao portao da onda; (2) ciclo vazio nao para.
    # PARADA-SOBRE-SERVICO: M44-M56 portados de 1b19cac4d (coord/feeder-4-linhas); M38-M43 sao do FEEDER e nao
    # estao neste ramo. M57 e a unica diferenca do porte: linha sem candidatas nao pergunta ao portao.
    ("M44_PORTAO_DA_FONTE_IGNORADO", ALVO,
     'admitida = {s for s, v in vered.items() if v.get("COLLECTION_ELIGIBLE") is True}',
     'admitida = {c["SOURCE_ID"] for c in cands}'),
    ("M45_PORTAO_NAO_SEI_ADMITE_TUDO", ALVO, 'return fim("PORTAO_DA_FONTE_NAO_SEI", ERRO=str(ex)[:300])',
     'vered = {c["SOURCE_ID"]: {"COLLECTION_ELIGIBLE": True} for c in cands}'),
    ("M46_RECUSADA_SEM_NOME_EM_ESPERAM", ALVO, 'for c in recusadas if c["SOURCE_ID"] not in set(feitas)]',
     'for c in [] if c["SOURCE_ID"] not in set(feitas)]'),
    ("M47_SEGUNDA_REGRA_SO_O_ESTADO", ALVO, "    return {s: GATE.avaliar(s, **ctx) for s in ids}\n",
     '    return {s: dict(GATE.avaliar(s, **ctx), COLLECTION_ELIGIBLE=GATE.LC.estado_de(s, ctx["livro"])'
     ' == GATE.LC.READY_FOR_COLLECTION) for s in ids}\n'),
    ("M48_SEM_PORTAO_ADMITE_TUDO", ALVO, 'porta = pecas.get("fonte") or portao_da_fonte_real',
     'porta = pecas.get("fonte") or (lambda ids: {s: {"COLLECTION_ELIGIBLE": True} for s in ids})'),
    ("M49_PASSAGEM_ESPERA_PELA_RECUSADA", ALVO,
     'if cands and all(c["SOURCE_ID"] in set(feitas) for c in cands) and not a_seco:',
     'if cands and all(c["SOURCE_ID"] in set(feitas) for c in cands + recusadas) and not a_seco:'),
    ("M50_CICLO_VAZIO_VOLTA_A_PARAR", ALVO, '    if nada:\n        reg["PROVA_TETO_CICLO"] = nada',
     '    if False:\n        reg["PROVA_TETO_CICLO"] = nada'),
    ("M51_NADA_SEM_OLHAR_O_LIVRO_DA_ONDA", ALVO, '        if n or any(x.get("CORREU")', '        if any(x.get("CORREU")'),
    ("M52_NADA_COM_RUN_IDS", ALVO, "    if run_ids or not pastas:\n", "    if not pastas:\n"),
    ("M53_ESTADO_DA_ONDA_EM_FALTA_E_NADA", ALVO,
     '        if not f.exists():\n            return None\n        livro = pasta / "TETO-ONDA.json"',
     '        if not f.exists():\n            continue\n        livro = pasta / "TETO-ONDA.json"'),
    ("M54_CICLO_VAZIO_DISPENSA_A_PROVA_24H", ALVO, "    if nada and not ids_24h:", "    if nada:"),
    ("M55_FONTE_QUE_CORREU_IGNORADA", ALVO, '        if n or any(x.get("CORREU") for x in e.get("FONTES") or []):',
     "        if n:"),
    ("M56_LIVRO_DA_ONDA_ILEGIVEL_E_NADA", ALVO,
     "        except (ValueError, KeyError, TypeError, AttributeError, OSError):\n            return None\n"
     '        if n or any(',
     "        except (ValueError, KeyError, TypeError, AttributeError, OSError):\n            n, e = 0, {}\n"
     '        if n or any('),
    ("M57_LINHA_VAZIA_PERGUNTA_AO_PORTAO", ALVO,
     'vered = porta(sorted({c["SOURCE_ID"] for c in cands})) if cands else {}',
     'vered = porta(sorted({c["SOURCE_ID"] for c in cands}))'),
    ("M36_SAIDA_VAZIA_ACEITE", "scripts/micro_coleta/provar_backup_da_sala.py",
     '    if not texto.strip():\n        return "SAIDA_VAZIA"\n', ""),
    ("M37_SAIDA_RAIZ_ACEITE", "scripts/micro_coleta/provar_backup_da_sala.py", "    if p == Path(p.anchor):", "    if False:"),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    r = subprocess.run([sys.executable, TESTE], cwd=pasta, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=600)
    m = re.search(r"Ran (\d+) test", r.stderr)
    return r.returncode, int(m.group(1)) if m else None, r.stderr[-600:]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    # --lote=M01,M02,... (SERVICO-TRINCO, 30/09): so estes mutantes, para correr em lotes quando a maquina
    # nao aguenta a rodada inteira; o resultado vai para COLETA-CONTINUA-MUTACAO-LOTE-<primeiro>-<ultimo>.json
    lote = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--lote=")), None)
    mutantes = MUTANTES if lote is None else [m for m in MUTANTES if m[0].split("_")[0] in lote or m[0] in lote]
    if lote is not None and len(mutantes) != len(lote):
        raise SystemExit("LOTE_COM_NOMES_DESCONHECIDOS: pedidos %s, encontrados %s" % (lote, [m[0] for m in mutantes]))
    base = tempfile.mkdtemp(prefix="coleta-continua-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, n, cauda = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base:\n" + cauda)
        for nome, alvo, de, para in mutantes:
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, alvo)
            with open(f, encoding="utf-8", newline="") as h:
                s = h.read()
            s2 = s.replace("\r\n", "\n")
            if s2.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes em %s" % (nome, s2.count(de), alvo))
            s2 = s2.replace(de, para)
            with open(f, "w", encoding="utf-8", newline="") as h:
                h.write(s2.replace("\n", "\r\n") if "\r\n" in s else s2)
            cod, n, cauda = correr(pasta)
            morto = cod != 0
            out["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "MORTO": morto, "CODIGO": cod,
                                    "CAUDA": None if morto else cauda})
            print(nome, "MORTO" if morto else "SOBREVIVEU", flush=True)
            shutil.rmtree(pasta, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    nome_f = ("COLETA-CONTINUA-MUTACAO.json" if lote is None else
              "COLETA-CONTINUA-MUTACAO-LOTE-%s-%s.json" % (mutantes[0][0].split("_")[0], mutantes[-1][0].split("_")[0]))
    with open(os.path.join(RAIZ, "provas", nome_f), "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("COLETA_CONTINUA_MUTACAO · mortos=%d de %d" % (out["MORTOS"], out["TOTAL"]))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
