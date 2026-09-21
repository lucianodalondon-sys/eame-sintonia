# -*- coding: utf-8 -*-
"""AS GUARDAS DA ROTA DO HTML — e as do tempo e do lugar que ela nao preenche.

    UMA FERRAMENTA QUE RECEBE O QUE NAO SABE ABRIR NAO FALHOU:
    FOI CHAMADA PARA O TRABALHO ERRADO.

Este ficheiro guarda o que a `DUAS-PORTAS-V1` ligou, e guarda-o do lado de
quem ataca:

    a ESCOLHA do executor por especie declarada
    o texto VAZIO que nao pode passar por extracao feita
    os bytes que NAO sao HTML e nao podem ser abertos aqui
    a proveniencia que tem de viajar inteira, ou a unidade nao sai
    o `FACT_TIME` que NAO cai para `PUBLISHED_AT`
    o `FACT_LOCATION` que NAO cai para `SOURCE_LOCATION`
    o contrato de saida que RECUSA emitir sem `SIM`

⚠️ OS VALORES ESPERADOS ESTAO ESCRITOS A MAO. Nenhum teste aqui itera a
estrutura que verifica: um teste que lesse `CAPACIDADE["ACEITA_MEDIA_TYPES"]`
para depois confirmar que `executor_para` devolve esse executor passaria
depois de a ficha inteira ser apagada.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import artefato as art  # noqa: E402
import ingresso as ing  # noqa: E402

import executor_texto_de_html as html  # noqa: E402

#: HTML minimo com texto de gente la dentro.
COM_TEXTO = (b"<html><head><title>T</title><style>p{color:red}</style></head>"
             b"<body><script>var x=1;</script><p>Le quotazioni dell&#39;uva "
             b"restano contenute.</p></body></html>")
#: HTML que abre bem e nao tem uma letra de conteudo. NAO precisa de OCR.
SEM_TEXTO = (b"<html><head><style>body{margin:0}</style></head><body>"
             b"<script>montaTudo();</script>  \n\t  </body></html>")
#: Um PDF declarado como HTML. A rota e de outro dono.
BYTES_DE_PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n"


class AEscolhaDoExecutorEPorEspecieDeclarada(unittest.TestCase):
    """`executor_para` e o dono da pergunta «quem abre isto?»."""

    def test_html_vai_ao_executor_de_html(self):
        m = ing.executor_para("text/html")
        self.assertIsNotNone(m, "nenhum executor declara text/html: a rota "
                                "esta desligada outra vez")
        self.assertEqual(m.EXECUTOR_ID, "texto-de-html")

    def test_html_com_charset_tambem(self):
        m = ing.executor_para("text/html; charset=utf-8")
        self.assertEqual(getattr(m, "EXECUTOR_ID", None), "texto-de-html")

    def test_xhtml_tambem(self):
        m = ing.executor_para("application/xhtml+xml")
        self.assertEqual(getattr(m, "EXECUTOR_ID", None), "texto-de-html")

    def test_o_pdf_continua_do_dono_do_pdf(self):
        """A rota do HTML nao rouba a do PDF. Dois donos da mesma especie
        seriam dois, e o segundo ganharia por acidente de declaracao."""
        m = ing.executor_para("application/pdf")
        self.assertEqual(getattr(m, "EXECUTOR_ID", None), "texto-de-pdf")

    def test_a_midia_continua_do_dono_da_midia(self):
        m = ing.executor_para("video/mp4")
        self.assertEqual(getattr(m, "EXECUTOR_ID", None), "transcricao-de-midia")

    #: O que CADA executor declara saber abrir, escrito a mao. Nao se le das
    #: fichas: um teste que lesse as fichas para depois confirmar as fichas
    #: passaria depois de todas elas serem trocadas.
    DONOS_DECLARADOS = {
        "executor_texto_de_pdf": ("application/pdf",),
        "executor_transcricao_midia": (),
        "executor_texto_de_html": ("text/html", "application/xhtml+xml"),
    }

    def test_cada_executor_declara_exactamente_as_especies_que_sabe_abrir(self):
        import importlib                                 # noqa: PLC0415
        for modulo, esperado in self.DONOS_DECLARADOS.items():
            with self.subTest(modulo=modulo):
                cap = importlib.import_module(modulo).CAPACIDADE
                self.assertEqual(
                    tuple(cap.get("ACEITA_MEDIA_TYPES") or ()), esperado,
                    "a ficha de %s mudou. Se foi de proposito, actualize esta "
                    "tabela E escreva porque." % modulo)

    def test_nenhuma_especie_exacta_tem_dois_donos(self):
        """⚠️ ESTE TESTE NASCEU DE UM SOBREVIVENTE DO RED TEAM.

        O ataque `M12` pos `application/pdf` na ficha do executor de HTML e
        NADA reclamou: `executor_para` percorre `_DONOS_DA_DERIVACAO` por
        ordem, o de PDF esta primeiro, e ele ganhava. O mutante sobrevivia
        porque a ORDEM o tapava.

            UM MUTANTE QUE SOBREVIVE PODE SER CODIGO REDUNDANTE —
            OU UMA TRAVA QUE NUNCA EXISTIU, ESCONDIDA POR UM ACIDENTE.

        E `coleta/ingresso.py` ja tinha escrito, por extenso, que este caso e
        proibido: «a ordem NAO e prioridade: as especies nao se sobrepoem, e
        no dia em que se sobrepuserem isso e uma decisao a ESCREVER, nao a
        herdar de quem foi importado primeiro». A lei estava escrita e nao
        tinha quem a fizesse morder. Passa a ter.
        """
        import importlib                                 # noqa: PLC0415
        visto = {}
        for modulo in ing._DONOS_DA_DERIVACAO:
            cap = importlib.import_module(modulo).CAPACIDADE
            for especie in (cap.get("ACEITA_MEDIA_TYPES") or ()):
                chave = str(especie).strip().lower()
                self.assertNotIn(
                    chave, visto,
                    "«%s» e reclamada por %s e por %s. Dois donos da mesma "
                    "especie: quem ganha e quem foi importado primeiro, e "
                    "isso nao e uma decisao — e um acidente."
                    % (chave, visto.get(chave), modulo))
                visto[chave] = modulo

    def test_o_csv_continua_sem_dono(self):
        """`IT-T4-001` e `text/csv` e esta medido como MISSING_ROUTE de OUTRO
        dono. Declarar a familia `text` aqui roubava-lhe a rota."""
        self.assertIsNone(ing.executor_para("text/csv"))
        self.assertIsNone(ing.executor_para("text/plain"))


class OVazioNaoPassaPorExtracaoFeita(unittest.TestCase):

    def test_html_com_texto_da_TEXT_LAYER_PRESENT(self):
        texto, estado, erro, medidas = html.extrair(COM_TEXTO)
        self.assertEqual(estado, "TEXT_LAYER_PRESENT")
        self.assertEqual(erro, "")
        self.assertIn("quotazioni", texto)
        self.assertGreater(medidas["NON_WHITESPACE_CHARACTERS"], 0)

    def test_o_script_e_o_style_nao_entram_no_texto(self):
        texto, _e, _err, _m = html.extrair(COM_TEXTO)
        self.assertNotIn("var x", texto)
        self.assertNotIn("color:red", texto)

    def test_html_sem_letra_nenhuma_NAO_produz_derivado(self):
        """PRODUZIR FICHEIRO VAZIO NAO E SUCESSO."""
        texto, estado, _erro, medidas = html.extrair(SEM_TEXTO)
        self.assertEqual(estado, "SEM_TEXTO_NO_DOCUMENTO")
        self.assertEqual(medidas["NON_WHITESPACE_CHARACTERS"], 0)

    def test_o_estado_do_vazio_nao_e_o_do_PDF(self):
        """`TEXT_LAYER_ABSENT` esta anotado com «→ NEEDS_OCR` em
        `leis/artefato.py`. Um HTML sem letra nao tem imagem para reconhecer,
        e herdar o nome mandava alguem comprar OCR para nada."""
        _t, estado, _e, _m = html.extrair(SEM_TEXTO)
        self.assertNotEqual(estado, art.TEXT_LAYER_ABSENT)


class OsBytesQueNaoSaoHtmlNaoEntramAqui(unittest.TestCase):

    def test_um_pdf_declarado_html_e_recusado_com_nome(self):
        texto, estado, erro, _m = html.extrair(BYTES_DE_PDF, "text/html")
        self.assertEqual(estado, "BYTES_NAO_SAO_HTML")
        self.assertEqual(texto, "")
        self.assertIn("executor_texto_de_pdf", erro)

    def test_a_recusa_aponta_para_o_dono_certo(self):
        _t, _e, erro, _m = html.extrair(BYTES_DE_PDF, "text/html")
        self.assertIn("%PDF-", erro)


class AProvenienciaViajaOuAUnidadeNaoSai(unittest.TestCase):
    """O dono do vocabulario monta e CONFERE a unidade antes de haver bytes."""

    def unidade(self, **troca):
        import proveniencia as pv                        # noqa: PLC0415
        base = dict(texto="qualquer coisa", kind=html.TEXT_KIND,
                    kind_basis=html.TEXT_BASIS, relation=html.TEXT_RELATION,
                    language=None, raw_observation_id=7,
                    derivation_method=html.METODO,
                    unit_id="TU-texto-de-html-1", tool=html.FERRAMENTA)
        base.update(troca)
        return pv.unidade_de_texto(**base), pv

    def test_a_unidade_que_o_executor_monta_passa_no_dono(self):
        u, pv = self.unidade()
        self.assertEqual(pv.conferir_unidade_de_texto(u), [])

    def test_a_especie_declarada_e_PAGE_TEXT_ORIGINAL(self):
        self.assertEqual(html.TEXT_KIND, "PAGE_TEXT")
        self.assertEqual(html.TEXT_RELATION, "ORIGINAL")
        self.assertEqual(html.TEXT_BASIS, "DECLARED_BY_ROUTE")
        self.assertEqual(html.METODO, "EXTRACTED_FROM_DOCUMENT")

    def test_sem_ferramenta_declarada_a_unidade_e_RECUSADA(self):
        """`EXTRACTED_FROM_DOCUMENT` e metodo de MAQUINA: um texto de maquina
        sem maquina declarada nao se confere nem se repete."""
        u, pv = self.unidade(tool=None)
        problemas = pv.conferir_unidade_de_texto(u)
        self.assertTrue(problemas, "uma unidade sem ferramenta passou")
        self.assertTrue(any("ferramenta" in str(p) for p in problemas),
                        "o motivo nao fala da ferramenta: %r" % problemas)

    def test_a_lingua_nao_se_deduz_do_texto(self):
        """LINGUA ITALIANA NAO PROVA ITALIA, E TEXTO ITALIANO NAO PROVA `it`."""
        u, _pv = self.unidade()
        self.assertEqual(u["LANGUAGE"], "UNKNOWN")

    def test_o_kind_da_linha_e_o_que_a_migration_022_reservou(self):
        self.assertEqual(html.KIND, "TEXT_EXTRACTION")


class OTempoEOLugarNaoSePreenchem(unittest.TestCase):
    """SEM FALLBACK: `FACT_TIME != PUBLISHED_AT`, `FACT_LOCATION != SOURCE_LOCATION`."""

    def documento(self, **extra):
        item = {"artifact_type": "DERIVED", "source_id": "IT-T10-018",
                "parent_sha256": "b" * 64, "id": "obs:teste",
                "url": "https://exemplo.invalid/n",
                "texto": ("Le quotazioni e il prezzo dell'uva da tavola "
                          "scendono ancora.")}
        item.update(extra)
        return item

    def admitido(self, **extra):
        item = self.documento(**extra)
        d = adm.decidir(item, "T10", corrida="T-FACTOS")
        self.assertEqual(d.resultado, "SIM",
                         "o gabarito deste teste deixou de passar a porta: %s"
                         % d.motivo)
        return adm.pronto_para_inteligencia(item, d)

    def test_sem_fact_time_o_contrato_sai_NAO_SEI(self):
        pronto = self.admitido()
        self.assertEqual(pronto["FACT_TIME"], "NAO SEI")

    def test_published_at_NAO_vira_fact_time(self):
        """A data em que a fonte PUBLICOU nao e a data em que o fato
        aconteceu. Uma queda aqui enche a estatistica e apaga a pergunta."""
        pronto = self.admitido(published_at="2026-03-04T00:00:00Z")
        self.assertEqual(pronto["PUBLISHED_AT"], "2026-03-04T00:00:00Z")
        self.assertEqual(pronto["FACT_TIME"], "NAO SEI")

    def test_captured_at_NAO_vira_fact_time(self):
        """COLLECTED_AT != FACT_TIME. O instante em que ESTA maquina recebeu
        os bytes nao diz nada sobre quando o fato aconteceu."""
        pronto = self.admitido(captured_at="2026-09-21T19:27:00.000Z")
        self.assertEqual(pronto["CAPTURED_AT"], "2026-09-21T19:27:00.000Z")
        self.assertEqual(pronto["FACT_TIME"], "NAO SEI")

    def test_source_location_NAO_vira_fact_location(self):
        """Onde esta quem publica nao e onde o fato aconteceu."""
        pronto = self.admitido(source_location="IT-Veneto")
        self.assertEqual(pronto["SOURCE_LOCATION"], "IT-Veneto")
        self.assertEqual(pronto["FACT_LOCATION"], "NAO SEI")

    def test_o_fact_time_declarado_viaja_tal_como_veio(self):
        """A guarda e contra PREENCHER, nao contra TRANSPORTAR."""
        pronto = self.admitido(fact_time="2026-02-01T00:00:00Z")
        self.assertEqual(pronto["FACT_TIME"], "2026-02-01T00:00:00Z")


class OContratoDeSaidaRecusaSemSim(unittest.TestCase):
    """ADMISSION SIM != READY AUTOMATICO — e o contrario tambem: sem SIM, o
    dono do contrato nem emite."""

    def item_sem_prova(self):
        return {"artifact_type": "DERIVED", "source_id": "IT-T10-018",
                "parent_sha256": "c" * 64, "id": "obs:sem",
                "url": "https://exemplo.invalid/x",
                "texto": "A sede historica comemora cinquenta anos."}

    def test_um_NAO_SEI_nao_produz_unidade(self):
        item = self.item_sem_prova()
        d = adm.decidir(item, "T10", corrida="T-FACTOS")
        self.assertIn(d.resultado, ("NAO_SEI", "NAO"))
        with self.assertRaises(ValueError):
            adm.pronto_para_inteligencia(item, d)

    def test_um_NAO_tambem_nao(self):
        item = dict(self.item_sem_prova(),
                    texto=("La peronospora e l'oidio colpiscono i vigneti con "
                           "forte infestazione dei parassiti."))
        d = adm.decidir(item, "T10", corrida="T-FACTOS")
        self.assertEqual(d.resultado, "NAO")
        with self.assertRaises(ValueError):
            adm.pronto_para_inteligencia(item, d)


class AFichaDaCapacidadeDizAVerdade(unittest.TestCase):
    """Uma ficha que promete o que o codigo nao faz e pior do que ficha
    nenhuma: ela e LIDA pela porta."""

    def test_nao_declara_familia_nenhuma(self):
        """Declarar a familia `text` apanharia `text/csv` e `text/plain`, que
        esta ferramenta nao sabe abrir."""
        self.assertEqual(tuple(html.CAPACIDADE["ACEITA_FAMILIAS"]), ())

    def test_declara_que_nao_vai_a_rede(self):
        self.assertEqual(html.CAPACIDADE["NETWORK_REQUIRED"], "NO")
        self.assertEqual(html.CAPACIDADE["OCR"], "NO")

    def test_aponta_para_o_dono_da_extracao_em_vez_de_o_repetir(self):
        self.assertEqual(html.CAPACIDADE["TEXT_OWNER"],
                         "coleta/texto_fonte.py::limpar")

    def test_nao_declara_ferramenta_externa(self):
        """Python puro: este executor nao pode ficar indisponivel por falta
        de instalacao, ao contrario do de PDF."""
        self.assertIsNone(html.CAPACIDADE["FERRAMENTA_EXTERNA"])


if __name__ == "__main__":
    unittest.main()
