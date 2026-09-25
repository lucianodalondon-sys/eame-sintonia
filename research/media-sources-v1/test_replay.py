import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import replay  # noqa: E402

BASE = subprocess.run(["git", "-C", str(AQUI), "show", "df0865e6:candidatas/FONTES-CANDIDATAS.json"],
                      capture_output=True, check=True).stdout


class Replay(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()); self.fila = self.tmp / "FONTES-CANDIDATAS.json"
        self.fila.write_bytes(BASE)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_medir_nao_escreve(self):
        r = replay.replay(self.fila, gravar=False)
        self.assertEqual((r["NOVAS"], r["DEDUP"]), (5, 0))
        self.assertEqual(self.fila.read_bytes(), BASE)

    def test_gravar_duas_vezes_e_idempotente(self):
        r1 = replay.replay(self.fila, gravar=True)
        self.assertEqual((r1["LINHAS_ANTES"], r1["LINHAS_DEPOIS"], r1["NOVAS"]), (1199, 1204, 5))
        r2 = replay.replay(self.fila, gravar=True)
        self.assertEqual((r2["LINHAS_DEPOIS"], r2["NOVAS"], r2["DEDUP"]), (1204, 0, 5))
        self.assertEqual([a["CANDIDATA_ID"] for a in r1["ACHADOS"]], [a["CANDIDATA_ID"] for a in r2["ACHADOS"]])
        self.assertEqual((r2["IDS_DUPLICADOS"], r2["URLS_DUPLICADAS"]), (0, 0))

    def test_url_ja_existente_com_outra_grafia_e_dedup(self):
        d = json.loads(BASE)
        d["CANDIDATAS"].append({"CANDIDATA_ID": "CAND-1200", "TIPO": "OUTRO", "PAIS": "IT", "NOME": "outra lane",
                                "URL": "http://reterurale.it/podcast/", "ESTADO": "CANDIDATA"})
        self.fila.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        r = replay.replay(self.fila, gravar=True)
        rrn = [a for a in r["ACHADOS"] if "reterurale" in a["URL"]][0]
        self.assertEqual((rrn["RESULTADO"], rrn["CANDIDATA_ID"]), ("DEDUP", "CAND-1200"))
        self.assertEqual((r["NOVAS"], r["LINHAS_DEPOIS"]), (4, 1204))
        # o ID que a bancada deu (CAND-1200 ao TEA alle 5) NAO se transporta
        tea = [a for a in r["ACHADOS"] if "tea-alle-5" in a["URL"]][0]
        self.assertNotEqual(tea["CANDIDATA_ID"], "CAND-1200")

    def test_ids_ocupados_por_outra_lane_ficam_intactos(self):
        # o vivo: CAND-1200..1204 sao de outra lane (ARPAE). O replay nao os toca.
        d = json.loads(BASE)
        outras = [{"CANDIDATA_ID": f"CAND-{1200 + i}", "TIPO": "BASE_OFICIAL", "PAIS": "IT",
                   "NOME": f"ARPAE {i}", "URL": f"https://arpae.example/{i}", "ESTADO": "CANDIDATA"} for i in range(5)]
        d["CANDIDATAS"] += outras
        self.fila.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        r = replay.replay(self.fila, gravar=True)
        self.assertEqual(r["LINHAS_ANTIGAS_ALTERADAS"], [])
        self.assertEqual([a["CANDIDATA_ID"] for a in r["ACHADOS"]], [f"CAND-{i}" for i in range(1205, 1210)])
        fila = {c["CANDIDATA_ID"]: c for c in json.loads(self.fila.read_text(encoding="utf-8"))["CANDIDATAS"]}
        for o in outras:
            self.assertEqual(fila[o["CANDIDATA_ID"]], o)

    def test_fila_inexistente_falha_alto(self):
        with self.assertRaises(SystemExit):
            replay.replay(self.tmp / "nao-existe.json", gravar=True)
        self.assertFalse((self.tmp / "nao-existe.json").exists())


if __name__ == "__main__":
    unittest.main()
