#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE DE MÍDIA — quem abre o quê, e o que ela nunca se torna.

    py -m unittest tests.test_c4h_executor_de_midia

A C4G deixou o diagnóstico fechado: a porta da derivação conhecia UM executor,
importado pelo nome, e o próprio ficheiro tinha previsto o custo — «no dia em
que entrasse um executor de áudio os dois divergiam em silêncio».

Estas provas guardam o que a C4H fez com isso, e sobretudo o que ela NÃO fez.
"""
import ast
import inspect
import io
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                            # noqa: E402,F401
import artefato as art                                     # noqa: E402
import derivacao_forward as df                             # noqa: E402
import executor_texto_de_pdf as ep                         # noqa: E402
import executor_transcricao_midia as em                    # noqa: E402
import ingresso as ing                                     # noqa: E402


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding="utf-8") as fh:
        return fh.read()


def _codigo_de(rel, nome):
    """O CODIGO de uma funcao — sem comentario e sem docstring. → str.

    ⚠️ APANHEI-ME A MIM PROPRIO, PELA TERCEIRA VEZ NESTA CASA.
    Seis destas provas procuravam palavras como `classific`, `FACT_TIME` ou
    `sql` no TEXTO do executor — e reprovaram por causa da PROSA que explica
    justamente por que ele nao faz essas coisas.

        PROCURAR A PALAVRA NO FICHEIRO MEDE O QUE ESTA ESCRITO.
        A PERGUNTA ERA SOBRE O QUE EXECUTA.

    `ast.unparse` deita fora comentarios por construcao; a docstring sai a mao.
    """
    for no in ast.walk(ast.parse(_fonte(rel))):
        if not isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if no.name != nome:
            continue
        corpo = list(no.body)
        if (corpo and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)):
            corpo = corpo[1:]
        return "\n".join(ast.unparse(x) for x in corpo)
    raise AssertionError("a funcao %r nao existe em %s" % (nome, rel))


# ══════════════════════════════════════════════════════════════════════════
class T1aT5QuemAbreOQue(unittest.TestCase):
    """A escolha é pela ESPÉCIE declarada, nunca pelo nome do ficheiro."""

    def test_T1_video_mp4_escolhe_o_executor_de_midia(self):
        nome, _cap = ing.executor_para("video/mp4")
        self.assertEqual(nome, "executor_transcricao_midia")

    def test_T2_audio_escolhe_o_executor_de_midia(self):
        for mt in ("audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg"):
            with self.subTest(media_type=mt):
                self.assertEqual(ing.executor_para(mt)[0],
                                 "executor_transcricao_midia")

    def test_T3_pdf_continua_a_escolher_o_executor_de_pdf(self):
        self.assertEqual(ing.executor_para("application/pdf")[0],
                         "executor_texto_de_pdf")

    def test_T4_o_declarado_vence_a_extensao(self):
        """A correcção da C4G, guardada aqui de novo pelo lado da escolha."""
        item = {"SOURCE_ID": "PROVA/C4H", "SOURCE_NATIVE_ID": "x",
                "STORAGE_LOCATION": "README.md", "NAME": "README.md",
                "CONTENT_TYPE": "audio/wav"}
        f = ing.ficha(item, corrida={"RUN_ID": "C4H", "STARTED_AT": art.agora()})
        self.assertEqual(f.CONTENT_TYPE, "audio/wav")
        self.assertEqual(ing.executor_para(f.CONTENT_TYPE)[0],
                         "executor_transcricao_midia")

    def test_T5_ficheiro_chamado_pdf_com_especie_de_video_nao_vai_ao_pdf(self):
        """⚠️ O ataque que mata a tentação de escolher pelo nome.

        `package.json` renomeado, `notas.pdf` que é um MP4 — o nome é do
        utilizador, a espécie é de quem observou os bytes.
        """
        item = {"SOURCE_ID": "PROVA/C4H", "SOURCE_NATIVE_ID": "x",
                "STORAGE_LOCATION": "README.md", "NAME": "relatorio.pdf",
                "CONTENT_TYPE": "video/mp4"}
        f = ing.ficha(item, corrida={"RUN_ID": "C4H", "STARTED_AT": art.agora()})
        self.assertEqual(f.CONTENT_TYPE, "video/mp4")
        nome, _ = ing.executor_para(f.CONTENT_TYPE)
        self.assertEqual(nome, "executor_transcricao_midia")
        self.assertNotEqual(nome, "executor_texto_de_pdf")

    def test_nenhum_executor_recebe_o_que_declarou_nao_aceitar(self):
        for cap in ing._capacidades_de_derivacao():
            aceita = tuple(str(a).lower()
                           for a in (cap.get("ACEITA_MEDIA_TYPES") or ()))
            for mt in aceita:
                with self.subTest(executor=cap["EXECUTOR_ID"], media_type=mt):
                    self.assertEqual(ing.executor_para(mt)[1]["EXECUTOR_ID"],
                                     cap["EXECUTOR_ID"])

    def test_a_porta_conhece_mais_do_que_um(self):
        ids = {c["EXECUTOR_ID"] for c in ing._capacidades_de_derivacao()}
        self.assertIn("texto-de-pdf", ids)
        self.assertIn("transcricao-midia", ids)


# ══════════════════════════════════════════════════════════════════════════
class T6aT8OContratoDoTexto(unittest.TestCase):
    """E7 — a espécie do texto, a relação, e a língua."""

    def test_T6_o_produto_e_TRANSCRIPT_e_a_especie_do_derivado_e_TRANSCRIPTION(self):
        import proveniencia as pv                             # noqa: PLC0415
        self.assertEqual(em.ESPECIE, "TRANSCRIPTION")
        self.assertIn(em.ESPECIE, em.CAPACIDADE["PRODUCES"])
        # A especie do TEXTO vem do dono; a do DERIVADO vem da 022. Sao duas
        # listas fechadas diferentes, e as duas sao respeitadas.
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertIn("pv.TRANSCRIPT", corpo)
        self.assertIn(pv.TRANSCRIPT, pv.TEXT_KINDS)

    def test_T7_caption_nunca_e_rebatizada_transcript(self):
        """O executor não produz, não lê e não converte CAPTION."""
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertNotIn("CAPTION", corpo)
        # E quem produz CAPTION continua a ser outro ficheiro, com outro valor.
        self.assertIn("'TEXT_KIND': 'CAPTION'", _fonte("coleta/comunicacao_coleta.py"))

    def test_T8_a_lingua_vem_da_evidencia_e_nao_do_pais(self):
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertIn("language=r.get('LANGUAGE')", corpo)
        # E a confianca/fonte da deteccao continuam visiveis nas medidas.
        self.assertIn("LANGUAGE_SOURCE",
                      _codigo_de("coleta/executor_transcricao_midia.py", "_medidas"))
        for proibido in ("COUNTRY_SCOPE", "SOURCE_LOCATION", "FACT_LOCATION"):
            self.assertNotIn(proibido, corpo,
                             "a lingua nao nasce de %s" % proibido)

    def test_a_traducao_nao_substitui_o_original(self):
        import proveniencia as pv                             # noqa: PLC0415
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertIn("pv.ORIGINAL", corpo)
        self.assertIn(pv.ORIGINAL, pv.TEXT_RELATIONS)
        self.assertNotIn("TRANSLAT", corpo, "o executor nao traduz")


# ══════════════════════════════════════════════════════════════════════════
class T9aT11OQueOExecutorNuncaFaz(unittest.TestCase):

    def test_T9_source_id_desconhecido_continua_desconhecido(self):
        """O executor não vê `SOURCE_ID`, e por isso não pode inventá-lo."""
        fonte = _fonte("coleta/executor_transcricao_midia.py")
        self.assertNotIn("SOURCE_ID", fonte)
        self.assertNotIn("source_id", fonte)

    def test_T10_o_executor_nao_inventa_raw_asset_id(self):
        """Ele RECEBE o pai como contexto da unidade — nunca o deduz."""
        par = inspect.signature(em.derivar_um).parameters
        self.assertIn("raw_asset_id", par)
        fonte = _fonte("coleta/executor_transcricao_midia.py")
        i = fonte.index("def derivar_um")
        self.assertNotIn("raw_asset_id =", fonte[i:])

    def test_T11_o_executor_nao_escreve_no_banco(self):
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        for proibido in ("psycopg", "insert into", "cursor", "commit(",
                         "execute("):
            self.assertNotIn(proibido, corpo.lower(),
                             "escrita directa no banco: %r" % proibido)
        self.assertIn("preservar_derivado", corpo)

    def test_o_executor_nao_duplica_o_reconhecedor(self):
        """RT3 — `fala_local` continua a ser o único dono de FALA -> TEXTO."""
        fonte = _fonte("coleta/executor_transcricao_midia.py")
        for proibido in ("WhisperModel(", "BatchedInferencePipeline(",
                         "faster_whisper", "compute_type=", "device="):
            self.assertNotIn(proibido, fonte,
                             "o executor esta a abrir o motor: %r" % proibido)
        self.assertIn("import fala_local", fonte)

    def test_o_executor_nao_julga_relevancia_nem_tempo_do_facto(self):
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        for proibido in ("FACT_TIME", "ADMISSION", "RELEVANC", "classific"):
            self.assertNotIn(proibido, corpo)


# ══════════════════════════════════════════════════════════════════════════
class T12eT13ErroNaoERecusa(unittest.TestCase):
    """RT18 · `ERROR != REJECTED` — o sistema falhou / o item não servia."""

    def test_T12_falha_de_ASR_e_ERROR_e_nunca_REJECTED(self):
        for motivo in (em.ASR_FALHOU, em.ASR_INDISPONIVEL, em.AUDIO_NAO_OBTIDO):
            with self.subTest(motivo=motivo):
                self.assertEqual(df.DESTINO_DO_MOTIVO[motivo], "ERROR")

    def test_T13_audio_sem_texto_nao_vira_ausencia_de_fala(self):
        """O motivo chama-se `SEM_TEXTO_RECONHECIDO`, e não `SEM_FALA`.

        `fala_local` é explícito: «AUSÊNCIA DE TEXTO != AUSÊNCIA DE FALA». O
        reconhecedor diz o que produziu, e não o que havia no áudio.
        """
        self.assertEqual(em.SEM_TEXTO_RECONHECIDO, "SEM_TEXTO_RECONHECIDO")
        self.assertEqual(df.DESTINO_DO_MOTIVO[em.SEM_TEXTO_RECONHECIDO],
                         "REJECTED")
        # ⚠️ MEDIDO NO MODULO, E NAO NO TEXTO. A primeira versao procurava a
        # palavra `SEM_FALA` no ficheiro — e reprovava por causa do COMENTARIO
        # que explica por que o motivo NAO se chama assim.
        self.assertFalse(hasattr(em, "SEM_FALA"),
                         "nasceu um motivo que afirma sobre o audio")
        self.assertNotIn("SEM_FALA", set(em.DESTINO_DOS_MOTIVOS))
        # E nenhuma das mensagens que o executor devolve afirma ausencia de
        # fala: as que existem dizem o contrario, por extenso.
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertIn("NAO_SIGNIFICA", corpo)

    def test_todo_motivo_declarado_tem_destino(self):
        """Um motivo sem destino cai no `UNKNOWN` e ninguém percebe porquê."""
        for motivo in em.DESTINO_DOS_MOTIVOS:
            self.assertIn(motivo, df.DESTINO_DO_MOTIVO)


# ══════════════════════════════════════════════════════════════════════════
class T14aT16IdentidadeEReprocessamento(unittest.TestCase):

    def test_T15_o_que_muda_o_TEXTO_entra_na_identidade_do_derivado(self):
        """Modelo e ferro mudam o texto — logo mudam a chave, e não a apagam.

        A 022 escreveu a razão: «o modelo `base` e o `small` sobre o mesmo
        audio dao textos diferentes... Sem a versao na identidade, a segunda
        passagem apagaria a primeira em silencio.»
        """
        fonte = _fonte("coleta/executor_transcricao_midia.py")
        i = fonte.index('"parameters"')
        bloco = fonte[i:i + 700]
        for campo in ("ASR_MODEL", "ASR_DEVICE_USED", "ASR_COMPUTE_SELECTED",
                      "ASR_ENGINE_VERSION"):
            self.assertIn(campo, bloco, "%s fora da identidade" % campo)

    def test_T16_o_sha_nao_e_usado_como_identidade_da_observacao(self):
        """O executor recebe `raw_asset_id`; ele nunca calcula um sha para o pai."""
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        for proibido in ("sha256", "parent_sha256", "hashlib"):
            self.assertNotIn(proibido, corpo,
                             "o executor calcula sha, e isso e do dono da escrita")

    def test_T14_o_dono_da_escrita_e_que_decide_reuso(self):
        """O executor não tem opinião sobre REUSED — ele entrega a receita."""
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertNotIn("REUSED", corpo)
        self.assertIn("REUSED", _fonte("guarda/preservar_derivado.py"))


# ══════════════════════════════════════════════════════════════════════════
class OAudioIntermedioEMaterialDeTrabalho(unittest.TestCase):
    """RT10 — e a autoridade é de 2022, não uma escolha desta missão."""

    def test_a_lista_fechada_de_especies_nao_tem_audio(self):
        sql = _fonte("supabase/migrations/022_o_derivado_ganha_casa.sql")
        i = sql.index("kind            text not null check (kind in (")
        bloco = sql[i:i + 400]
        self.assertIn("'TRANSCRIPTION'", bloco)
        for inventado in ("AUDIO_EXTRACTION", "'AUDIO'", "AUDIO_DERIVED"):
            self.assertNotIn(inventado, bloco)

    def test_o_wav_nasce_e_morre_numa_pasta_temporaria(self):
        fonte = _fonte("coleta/executor_transcricao_midia.py")
        self.assertIn("tempfile.mkdtemp", fonte)
        self.assertIn("shutil.rmtree", fonte)
        # E o WAV nunca vira derivado: o unico `media_type` que este executor
        # entrega ao dono da escrita e o do TEXTO.
        self.assertIn('"media_type": "text/plain"', fonte)
        self.assertNotIn('"media_type": "audio', fonte)
        self.assertNotIn('"media_type": "video', fonte)


# ══════════════════════════════════════════════════════════════════════════
class OReconhecedorCorreDeVerdade(unittest.TestCase):
    """Uma peça de áudio real, feita aqui, sem rede e sem acervo."""

    @classmethod
    def setUpClass(cls):
        cls.wav = None
        pasta = tempfile.mkdtemp(prefix="c4h-")
        alvo = os.path.join(pasta, "tom.wav")
        try:
            r = subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                 "sine=frequency=440:duration=2", "-ac", "1", "-ar", "16000",
                 alvo], capture_output=True, timeout=120)
            if r.returncode == 0 and os.path.getsize(alvo) > 1000:
                cls.wav = alvo
        except (OSError, subprocess.SubprocessError):
            pass

    def test_um_tom_sem_fala_sai_SEM_TEXTO_RECONHECIDO_e_nao_ERROR(self):
        """⚠️ E a diferença é toda: a ferramenta correu, e não havia texto.

        Se isto saísse `ERROR`, a Collection culparia a si própria por um áudio
        que simplesmente não tem palavras. Se saísse «sem fala», afirmaria
        sobre o áudio o que só quem ouviu poderia dizer.
        """
        if not self.wav:
            self.skipTest("ffmpeg nao produziu o tom nesta maquina")
        import fala_local as fl                              # noqa: PLC0415
        ha, _porque = fl.disponivel()
        if not ha:
            self.skipTest("o reconhecedor nao esta instalado nesta maquina")
        r = em.derivar_um(1, self.wav, armazem=None, memoria=None,
                          media_type="audio/wav")
        self.assertEqual(r["ESTADO"], "SEM_DERIVADO")
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], em.SEM_TEXTO_RECONHECIDO)
        self.assertEqual(df.DESTINO_DO_MOTIVO[r["MOTIVO_DO_EXECUTOR"]],
                         "REJECTED")
        self.assertIn("MEDIDAS", r)
        self.assertIn("nao tem fala", (r.get("NAO_SIGNIFICA") or "").lower()
                      .replace("ã", "a").replace("ú", "u"))


# ══════════════════════════════════════════════════════════════════════════
class OQueEstaMissaoNaoTocou(unittest.TestCase):
    """RT20 — a aba paralela do YouTube não foi incorporada nem sobreposta."""

    FICHEIROS_DA_MISSAO = (
        "coleta/executor_transcricao_midia.py",
        "coleta/ingresso.py",
        "coleta/derivacao_forward.py",
        "tests/test_c4h_executor_de_midia.py",
    )

    def test_nenhum_ficheiro_de_youtube_entrou_nesta_missao(self):
        for rel in self.FICHEIROS_DA_MISSAO:
            with self.subTest(ficheiro=rel):
                self.assertNotIn("youtube", os.path.basename(rel).lower())

    def test_o_executor_de_midia_nao_conhece_youtube(self):
        fonte = _fonte("coleta/executor_transcricao_midia.py").lower()
        for palavra in ("youtube", "yt-dlp", "yt_dlp", "instagram"):
            self.assertNotIn(palavra, fonte,
                             "a ponte de midia nao conhece plataforma: %r" % palavra)

    def test_o_dono_do_ASR_nao_foi_alterado_por_esta_missao(self):
        """`fala_local` é infraestrutura partilhada com a aba do YouTube."""
        fonte = _fonte("ferramentas/fala_local.py")
        self.assertNotIn("executor_transcricao_midia", fonte,
                         "o owner do ASR passou a conhecer a ponte — a "
                         "dependencia tem de ser numa direccao so")


# ══════════════════════════════════════════════════════════════════════════
class SinteseC4HArbitragem(unittest.TestCase):
    """O que a arbitragem C4H-ARB mandou corrigir, e o que ela mandou portar."""

    def test_o_vocabulario_vem_do_DONO_e_nao_de_literais(self):
        """⚠️ ERA A ÚNICA VIOLAÇÃO DE CONTRATO DESTA IMPLEMENTAÇÃO.

        `regras/proveniencia.py` existe, tem `TEXT_KINDS`, `TEXT_RELATIONS` e
        `METODOS_DE_DERIVACAO` — e tem CONSTRUTOR e VALIDADOR. Escrever
        `"TRANSCRIPT"` à mão era um segundo dono do mesmo vocabulário.

            UM VALOR CERTO ESCRITO NO SÍTIO ERRADO É UM VALOR QUE VAI DERIVAR.
        """
        import proveniencia as pv                             # noqa: PLC0415
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertIn("pv.unidade_de_texto", corpo)
        self.assertIn("pv.TRANSCRIPT", corpo)
        self.assertIn("pv.ORIGINAL", corpo)
        self.assertIn("pv.PRODUCED_BY_LOCAL_ASR", corpo)
        self.assertIn("pv.ASR_DA_CASA", corpo)
        # ⚠️ A ASSERCAO E POSITIVA DE PROPOSITO.
        # A primeira versao proibia a string `'TRANSCRIPT'` e apanhou
        # `r.get('TRANSCRIPT')` — que e a CHAVE DE SAIDA do reconhecedor, nao
        # o vocabulario. Proibir uma string apanha strings parecidas.
        #
        #     PERGUNTAR «QUE SIMBOLO E USADO» E PRECISO.
        #     PROIBIR UM TEXTO E UM PALPITE COM CARA DE REGRA.
        self.assertNotIn("TEXT_KIND': 'TRANSCRIPT'", corpo)
        self.assertNotIn("TEXT_RELATION': 'ORIGINAL'", corpo)

    def test_o_dono_confere_a_unidade_antes_de_ela_sair(self):
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertIn("pv.conferir_unidade_de_texto", corpo)
        self.assertIn("UNIDADE_RECUSADA", corpo)

    def test_a_unidade_que_este_executor_monta_passa_no_dono(self):
        """A prova que o validador do dono faz, feita aqui também."""
        import proveniencia as pv                             # noqa: PLC0415
        u = pv.unidade_de_texto(
            texto="uma frase", kind=pv.TRANSCRIPT,
            kind_basis=pv.PRODUCED_BY_LOCAL_ASR, relation=pv.ORIGINAL,
            language="it", raw_observation_id=1,
            derivation_method=pv.ASR_DA_CASA,
            unit_id="TU-%s-%s" % (em.EXECUTOR_ID, em.EXECUTOR_VERSION),
            tool="faster-whisper", model="small")
        self.assertEqual(pv.conferir_unidade_de_texto(u), [])
        self.assertEqual(u["LINEAGE"]["DERIVATION_METHOD"], "LOCAL_ASR")

    def test_o_metodo_de_derivacao_esta_na_lista_fechada(self):
        """O mesmo tipo de contrato que `kind` tem na 022 — e o que derrubou B."""
        import proveniencia as pv                             # noqa: PLC0415
        self.assertIn(pv.ASR_DA_CASA, pv.METODOS_DE_DERIVACAO)

    def test_o_kind_continua_na_lista_fechada_da_022(self):
        sql = _fonte("supabase/migrations/022_o_derivado_ganha_casa.sql")
        i = sql.index("kind            text not null check (kind in (")
        self.assertIn("'%s'" % em.ESPECIE, sql[i:i + 400])
        self.assertNotIn("AUDIO_TRANSCRIPTION", sql[i:i + 400])

    def test_ficheiro_sem_faixa_de_som_e_facto_do_ORIGINAL(self):
        """Ideia portada da implementação concorrente, e ela estava certa.

        Um MP4 só de imagem existe. Mandá-lo ao reconhecedor devolve
        `REQUESTED_EMPTY` — verdade, e verdade CARA: paga-se o carregamento do
        modelo para saber o que o contentor dizia de graça.
        """
        self.assertEqual(df.DESTINO_DO_MOTIVO[em.SEM_FAIXA_DE_SOM], "REJECTED")
        corpo = _codigo_de("coleta/executor_transcricao_midia.py", "derivar_um")
        self.assertIn("tem_faixa_de_som", corpo)

    def test_a_pergunta_dos_fluxos_vai_ao_DONO_da_midia(self):
        """Porta-se a ideia, não o código: um segundo `ffprobe` seria 2 donos."""
        corpo = _codigo_de("coleta/executor_transcricao_midia.py",
                           "tem_faixa_de_som")
        self.assertIn("fl.fluxos", corpo)
        # `ffprobe` aparece nas MENSAGENS, e isso e diagnostico para quem le.
        # O que nao pode existir e um segundo sitio a CHAMAR a ferramenta.
        self.assertNotIn("subprocess", corpo)
        self.assertNotIn("Popen", corpo)
        self.assertNotIn("shutil.which", corpo)

    def test_nao_medir_nao_autoriza_concluir_que_nao_ha_som(self):
        import fala_local as fl                               # noqa: PLC0415

        class _Mudo:
            @staticmethod
            def fluxos(_c):
                return fl.NAO_SEI, fl.NAO_SEI, "ffprobe recusou"
        ok, porque = em.tem_faixa_de_som("x", _Mudo)
        self.assertTrue(ok, "ausencia de medicao virou ausencia de som")
        self.assertIn("ausencia de medicao", porque)

    def test_familias_NAO_foram_portadas(self):
        """§4B — famílias abririam media types que esta casa nunca provou.

        `audio/*` aceitaria `audio/x-inventado`. A lista explícita aceita
        apenas o que se pode provar, e é essa que fica.
        """
        self.assertNotIn("ACEITA_FAMILIAS", em.CAPACIDADE)
        self.assertFalse(hasattr(em, "FAMILIAS"))
        self.assertTrue(em.CAPACIDADE["ACEITA_MEDIA_TYPES"])
        self.assertFalse(em.aceita("audio/x-inventado"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
