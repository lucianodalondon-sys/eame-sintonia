#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A AUTORIDADE DA FONTE — medida, e nao presumida.

    SOURCE CATALOG DECLARATION  !=  DB IDENTITY AUTHORITY.
    CANDIDATE RECORD            !=  CANONICAL FACT.

A M2 atravessa `DERIVED -> STRUCTURED -> ADMISSION` com uma unidade real, e a
identidade do canal dela ainda e montada A MAO dentro da prova. Para deixar de
ser fixture, e preciso um dono de identidade — e antes dele, a pergunta que
nao se salta: QUEM TEM AUTORIDADE PARA DIZER DE QUEM E ESTA FONTE?

Medido: ninguem. A relacao `IT-T2-002 -> IT-OWN-003 -> ARPAV` existe apenas em
`candidatas/`, e o proprio ficheiro declara-se aditivo.

⚠️ ESTES TESTES NAO CONGELAM O ESTADO DE HOJE.
Ja custou duas vezes nesta branch: um teste que fixa o numero de hoje proibe o
de amanha, e reprova o conserto em vez do defeito. Aqui a exigencia e sobre a
RELACAO — se um dia a fonte for promovida por um artefato canonico, estes
testes passam na mesma. O que eles recusam e uma so coisa: que o CANDIDATO
passe a valer como autoridade sem promocao.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "provas"))
import _gavetas  # noqa: E402,F401
import a_autoridade_da_fonte as au  # noqa: E402

FONTE = au.A_FONTE_DA_M2


class OsArtefatosDeAutoridade(unittest.TestCase):
    """Quais existem, e o que cada um pode afirmar."""

    def test_o_registo_canonico_e_declarado_pela_propria_casa(self):
        """Nao e opiniao minha: o scanner escreve-o no artefato gerado."""
        recon, _ficha = au.o_que_o_reconciliado_diz(FONTE)
        self.assertIn("atlas e o registo canonico",
                      (recon.get("leitura") or "").lower().replace("é", "e"))

    def test_existe_contrato_canonico_que_declara_dono_de_fonte(self):
        """A forma mais forte que a casa tem: um documento canonico a nomear
        quem publica. Existe — para algumas fontes."""
        self.assertTrue(au.contratos_com_owner())

    def test_o_catalogo_italiano_declara_se_a_si_proprio_como_aditivo(self):
        catalogo, _f, _d = au.o_que_o_candidato_diz(FONTE)
        tocados = catalogo.get("canonical_artifacts_touched") or {}
        self.assertEqual([], tocados.get("modified"))
        self.assertIn("aditivo", tocados.get("reason") or "")


class AFonteDaM2(unittest.TestCase):
    """O caso concreto — e ele decide a missao."""

    def test_a_relacao_existe_no_candidato(self):
        """A relacao NAO esta errada. ARPAV publica mesmo aquele boletim.
        O que falta nao e verdade — e autoridade."""
        _c, fonte, dono = au.o_que_o_candidato_diz(FONTE)
        self.assertEqual("IT-OWN-003", fonte["OWNER_ID"])
        self.assertIn("ARPAV", dono["OWNER_CANONICAL_NAME"])

    def test_mas_a_autoridade_canonica_nao_a_alcanca(self):
        """⚠️ E ESTE TESTE VIRA SOZINHO NO DIA EM QUE ELA ALCANCAR.

        Ele nao exige que a fonte fique para sempre por resolver. Exige que,
        SE ela resolver, resolva por um artefato canonico — e nao por o
        candidato ter sido admitido as escondidas."""
        contratos = au.contratos_com_owner()
        no_atlas = au.fontes_com_ficha_no_atlas()
        if FONTE in contratos or FONTE in no_atlas:
            self.assertTrue(True, "promovida por artefato canonico: legitimo")
        else:
            recon, ficha = au.o_que_o_reconciliado_diz(FONTE)
            self.assertIn(FONTE, recon.get("so_no_master_italiano") or [],
                          "a fonte deixou de ser so-do-candidato sem ganhar "
                          "ficha nem contrato: alguem mudou a cadeia sem "
                          "passar pela promocao")
            self.assertEqual("candidatas/ITALY-SOURCE-MASTER-V1.json",
                             (ficha or {}).get("onde"))

    def test_MUTACAO_admitir_o_candidato_viraria_o_veredito(self):
        """UM PORTAO QUE NUNCA REPROVA E INDISTINGUIVEL DE UM DESLIGADO.

        Se o catalogo contasse, a cadeia fechava — e era esse o atalho. O teste
        existe para que o atalho seja visivel, e nao para o tapar."""
        contratos = au.contratos_com_owner()
        no_atlas = au.fontes_com_ficha_no_atlas()
        _c, fonte, dono = au.o_que_o_candidato_diz(FONTE)
        canonico = FONTE in contratos or FONTE in no_atlas
        if not canonico:
            self.assertTrue(fonte and dono,
                            "a mutacao deixou de ser possivel de montar")


class OQueFaltariaAindaDepoisDePromover(unittest.TestCase):
    """O achado que poupa a proxima missao: promover a fonte nao chega."""

    def test_os_dois_vocabularios_de_especie_nao_se_encontram(self):
        """`organizacao.tipo` fala nove nomes; o catalogo fala doze outros, e
        nenhum coincide. Sem traducao declarada, nem uma fonte promovida se
        materializa sozinha."""
        tipos = au.tipos_que_o_schema_aceita()
        kinds = au.owner_kinds_do_candidato()
        self.assertTrue(tipos and kinds)
        self.assertEqual(set(), {k.lower() for k in kinds} & tipos)

    def test_a_traducao_usada_na_prova_da_M2_nao_esta_declarada(self):
        """⚠️ UMA TRADUCAO QUE NINGUEM DECLAROU E UMA DECISAO QUE NINGUEM
        ASSINOU. A prova escreve `orgao_publico` para
        `OFFICIAL_REGIONAL_AGENCY`; nenhum contrato o manda."""
        self.assertIn("OFFICIAL_REGIONAL_AGENCY", au.owner_kinds_do_candidato())
        self.assertNotIn("official_regional_agency", au.tipos_que_o_schema_aceita())


class NinguemVirouDonoDeIdentidade(unittest.TestCase):
    """CASO C: a missao NAO podia criar o dono, e nao criou."""

    ESCRITORES_LEGITIMOS = ("tests/", "provas/")

    def test_nenhum_modulo_de_runtime_escreve_identidade(self):
        """Se um dono runtime tivesse nascido, ele apareceria aqui — e a
        missao teria de o justificar. Ele nao nasceu."""
        import subprocess
        alvo = r"into public\.(organizacao|pessoa|origem|canal)\b"
        r = subprocess.run(["grep", "-rlE", alvo, "--include=*.py",
                            "--include=*.mjs", "."],
                           cwd=RAIZ, capture_output=True, text=True)
        escritores = [x[2:] for x in r.stdout.split() if x.startswith("./")]
        intrusos = [e for e in escritores
                    if not e.startswith(self.ESCRITORES_LEGITIMOS)]
        self.assertEqual([], intrusos,
                         "nasceu um escritor de identidade fora de provas/ e "
                         "tests/: %s" % intrusos)

    def test_o_writer_de_conteudo_continua_a_recusar_e_a_dizer_quem_resolve(self):
        """CONTENT PERSISTENCE != IDENTITY RESOLUTION. `exigir_canal` recusa, e
        a recusa nomeia quem teria de resolver — que continua a nao existir."""
        import social_persistencia as sp
        fonte = open(os.path.join(RAIZ, "coleta", "social_persistencia.py"),
                     encoding="utf-8").read()
        self.assertIn("QUEM_RESOLVE", fonte)
        self.assertIn("CHANNEL_ID PROVA O CANAL, NAO PROVA A ORIGEM", fonte)
        self.assertTrue(hasattr(sp, "exigir_canal"))


if __name__ == "__main__":
    unittest.main()
