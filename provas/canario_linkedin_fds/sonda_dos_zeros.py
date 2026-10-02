"""CANARIO-LINKEDIN-FDS · o ZERO abriu a pagina, ou a pagina veio vazia/barrada?

    py provas/canario_linkedin_fds/sonda_dos_zeros.py SAIDA.json

O envelope de uma corrida `video-linkedin` com 0 cartoes diz ZERO_RESULTS e nao guarda
o que a pagina serviu. Esta sonda NAO e o canario e nao decide nada: faz 1 pedido a
cada pagina, pela MESMA descoberta do adaptador (`posts_com_video`, sem bytes de midia,
sem login), e escreve o que a pagina serviu — tamanho, quantas publicacoes
(`urn:li:activity`), quantos cartoes com video, e se ha marcas de ecra de login.
Portao de egresso IT antes de cada pedido; 20 s entre paginas.
"""
import json
import os
import re
import subprocess
import sys
import time

WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(WT)
sys.path.insert(0, os.path.join(WT, "coleta"))
import adaptador_linkedin as LI  # noqa: E402


PAGINAS = {"IT-T7-253": "https://www.linkedin.com/company/cia-agricoltori-italiani/",
           "IT-T5-190": "https://www.linkedin.com/company/ispra_2/",
           "IT-T7-254": "https://www.linkedin.com/company/consorzio-tutela-grana-padano/"}
LOGIN = re.compile(r"authwall|uas/login|/login\?|join-form|sign-in-modal|checkpoint/challenge", re.I)


def egresso_it():
    r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return "\"EGRESS_GATE\": \"PASS\"" in r.stdout


def main(saida):
    linhas = []
    for sid, url in PAGINAS.items():
        if not egresso_it():
            linhas.append({"SOURCE_ID": sid, "PAGINA": url, "PARADO": "EGRESSO_NAO_IT"})
            break
        guardado = {}

        def transporte(u):
            corpo = LI._buscar_texto(u, None)
            guardado["CORPO"] = corpo
            return corpo
        try:
            cartoes, ctx = LI.posts_com_video(pagina_url=url, run_id="SONDA-ZERO", transporte=transporte)
            corpo = guardado.get("CORPO") or ""
            texto = corpo if isinstance(corpo, str) else str(corpo)
            linhas.append({"SOURCE_ID": sid, "PAGINA": url, "PEDIDOS": ctx["PEDIDOS_TOTAIS"],
                           "BYTES_DA_PAGINA": len(texto.encode("utf-8")),
                           "ACTIVITY_IDS_DISTINTOS": len(set(re.findall(r"urn:li:activity:(\d{15,25})", texto))),
                           "CARTOES_COM_VIDEO": len(cartoes),
                           "TAGS_VIDEO": len(re.findall(r"<video\b", texto, re.I)),
                           "MARCAS_DE_LOGIN": sorted(set(m.lower() for m in LOGIN.findall(texto))),
                           "TITULO": (re.search(r"<title>(.*?)</title>", texto, re.S | re.I) or [None, None])[1]})
        except Exception as e:  # noqa: BLE001 — a sonda escreve o erro, nao o esconde
            linhas.append({"SOURCE_ID": sid, "PAGINA": url, "ERRO": "%s: %s" % (type(e).__name__, str(e)[:300])})
        print(json.dumps(linhas[-1], ensure_ascii=False), flush=True)
        time.sleep(20)
    json.dump({"DATASET": "CANARIO-LINKEDIN-FDS-SONDA-DOS-ZEROS", "LINHAS": linhas},
              open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
