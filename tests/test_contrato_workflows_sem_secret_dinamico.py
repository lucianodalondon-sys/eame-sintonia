#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CONTRATO — NENHUM WORKFLOW ESCOLHE O SECRET PELO NOME.

    py -m unittest tests.test_contrato_workflows_sem_secret_dinamico

`${{ secrets[<expressao>] }}` (indice dinamico) faz o GitHub entregar ao runner TODOS os secrets do
repositorio (nao sabe, antes de correr, qual vai ser lido) e deixa um input/pedido escolher QUAL secret
sai — um nome errado mandaria, por exemplo, a chave do Supabase como `key=` para a API do Google.
`toJSON(secrets)` entrega-os todos de uma vez. Nenhum dos dois cabe aqui: cada secret escreve-se FIXO,
`secrets.NOME`. O contrato le o TEXTO inteiro de cada workflow (comentarios incluidos: um exemplo
comentado copia-se).
"""
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, ".github", "workflows")

PROIBIDOS = (
    ("secrets[...] (secret escolhido pelo nome)", re.compile(r"\bsecrets\s*\[", re.I)),
    ("toJSON(secrets) (todos os secrets)", re.compile(r"\btojson\s*\(\s*secrets\s*\)", re.I)),
)


def workflows():
    return sorted(os.path.join(PASTA, f) for f in os.listdir(PASTA)
                  if f.endswith((".yml", ".yaml")))


def violacoes(texto):
    out = []
    for i, linha in enumerate(texto.splitlines(), 1):
        for nome, rx in PROIBIDOS:
            if rx.search(linha):
                out.append((i, nome, linha.strip()))
    return out


class ContratoSemSecretDinamico(unittest.TestCase):
    def test_ha_workflows_para_medir(self):
        self.assertIn(os.path.join(PASTA, "linha-busca-google.yml"), workflows())

    def test_nenhum_workflow_usa_secrets_por_indice_nem_tojson(self):
        achados = {}
        for p in workflows():
            with open(p, encoding="utf-8") as f:
                v = violacoes(f.read())
            if v:
                achados[os.path.basename(p)] = v
        self.assertEqual({}, achados)

    def test_o_detetor_apanha_as_formas_perigosas(self):
        # o proprio contrato tem de morder: as formas que ele proibe sao reconhecidas
        for mau in ("KEY: ${{ secrets[steps.pedido.outputs.segredo_da_chave] }}",
                    "KEY: ${{ secrets [ inputs.nome ] }}",
                    "KEY: ${{ secrets['YOUTUBE_DATA_API_KEY'] }}",
                    "TUDO: ${{ toJSON(secrets) }}"):
            self.assertTrue(violacoes(mau), mau)
        self.assertFalse(violacoes("KEY: ${{ secrets.YOUTUBE_DATA_API_KEY }}"))

    def test_a_linha_busca_le_so_a_chave_do_youtube_fixa(self):
        with open(os.path.join(PASTA, "linha-busca-google.yml"), encoding="utf-8") as f:
            t = f.read()
        self.assertEqual({"YOUTUBE_DATA_API_KEY"}, set(re.findall(r"secrets\.([A-Za-z0-9_]+)", t)))
        # o CX (ID publico do mecanismo) vem do pedido, nao de um secret
        self.assertIn("SINTONIA_GOOGLE_CSE_CX: ${{ steps.pedido.outputs.cx }}", t)
        self.assertNotIn("workflow_dispatch:", t)


if __name__ == "__main__":
    unittest.main()
