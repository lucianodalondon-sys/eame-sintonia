#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C6 — ter texto nunca provou que o texto é a fala do vídeo.

A C5 mediu que onze dos 28 textos pagos são inglês vindo de vídeo não-inglês. A
C6 foi ver quem consome esse texto — e encontrou o `COUNTRY_OF_FACT` a ser
decidido por ele, sem nada perguntar de onde ele veio.

    TEXT EXISTS != ORIGINAL TEXT PROVEN.

E a lei irmã, que impede o conserto de virar outro defeito:

    QUEM INFERE PODE SUSPEITAR. QUEM INFERE NÃO PODE CARIMBAR.
"""
import ast
import io
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, 'regras'), os.path.join(RAIZ, 'coleta'),
          os.path.join(RAIZ, 'leis'), os.path.join(RAIZ, 'ferramentas'),
          os.path.join(RAIZ, 'provas')):
    sys.path.insert(0, p)
import _gavetas              # noqa: E402,F401
import proveniencia as pv    # noqa: E402

#: O dono do vocabulário da espécie. Um, e só um.
DONO_DA_ESPECIE = 'regras/proveniencia.py'

PILOTO = os.path.join(RAIZ, 'data', 'samples', 'SENSOR-PILOT')
AUDITORIA = os.path.join(PILOTO, 'ESPECIE-DO-TEXTO-AUDITORIA-V1.json')


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════
class T1VocabularioFechadoEValidado(unittest.TestCase):
    """T1 · quatro espécies, e alguma coisa faz a lista valer."""

    def test_sao_quatro_e_a_quarta_e_a_ausencia(self):
        self.assertEqual(len(pv.ESPECIES_DO_TEXTO), 4)
        self.assertIn(pv.NAO_SEI, pv.ESPECIES_DO_TEXTO)
        self.assertIn(pv.NATIVE_CAPTION_ORIGINAL, pv.ESPECIES_DO_TEXTO)
        self.assertIn(pv.NATIVE_CAPTION_TRANSLATED, pv.ESPECIES_DO_TEXTO)
        self.assertIn(pv.ASR_LOCAL, pv.ESPECIES_DO_TEXTO)

    def test_a_decisao_so_devolve_valor_do_vocabulario(self):
        entradas = ({}, None, {'trackKind': 'asr'}, {'kind': 'asr'},
                    {'isTranslated': True}, {'translatedFrom': 'it'},
                    {'text': 'x'}, {'language': 'it'})
        for e in entradas:
            especie, base = pv.especie_declarada(e)
            self.assertIn(especie, pv.ESPECIES_DO_TEXTO, 'especie fora da lista: %r' % especie)
            self.assertIn(base, pv.BASES_DA_ESPECIE, 'base fora da lista: %r' % base)

    def test_a_base_inferida_do_texto_nao_existe(self):
        """`INFERRED_FROM_TEXT` não está no vocabulário, e a ausência é a lei."""
        for b in pv.BASES_DA_ESPECIE:
            self.assertNotIn('INFER', b.upper(),
                             'nasceu uma base que infere: %r' % b)

    def test_todo_registo_novo_declara_especie_do_vocabulario(self):
        """O escritor não pode inventar um quinto valor por descuido."""
        arvore = ast.parse(_fonte('regras/sensor_coleta.py'))
        literais = []
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Dict):
                continue
            for k, v in zip(no.keys, no.values):
                if (isinstance(k, ast.Constant) and k.value == 'TRANSCRIPT_KIND'
                        and isinstance(v, ast.Constant)):
                    literais.append(v.value)
        for lit in literais:
            self.assertIn(lit, pv.ESPECIES_DO_TEXTO,
                          'o sensor escreve uma especie fora do vocabulario: %r' % lit)


# ══════════════════════════════════════════════════════════════════════════
class T2UmDonoSo(unittest.TestCase):
    """§5 · ONE CONCEPT → ONE OWNER. Dois consumidores tiraram-no do primeiro."""

    def test_so_o_dono_declara_o_vocabulario(self):
        donos = []
        for pasta, dirs, fs in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('__pycache__', '.git', 'node_modules', 'system-map')]
            for f in fs:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(pasta, f), RAIZ)
                if rel.startswith('tests/'):
                    continue
                t = _fonte(rel)
                # Declarar é escrever o literal; usar é referenciar o dono.
                if "NATIVE_CAPTION_TRANSLATED = 'NATIVE_CAPTION_TRANSLATED'" in t:
                    donos.append(rel)
        self.assertEqual(donos, [DONO_DA_ESPECIE],
                         'o vocabulario tem mais de um dono: %s' % donos)

    def test_o_sensor_pergunta_em_vez_de_responder(self):
        import sensor_coleta as sc                              # noqa: PLC0415
        self.assertIs(sc.ESPECIES_DE_TEXTO, pv.ESPECIES_DO_TEXTO,
                      'o sensor voltou a ter a propria lista')
        self.assertEqual(sc.NATIVE_CAPTION_ORIGINAL, pv.NATIVE_CAPTION_ORIGINAL)


# ══════════════════════════════════════════════════════════════════════════
class T3e5AEspecieVemDaDeclaracaoNuncaDoTexto(unittest.TestCase):
    """T3 · T5 · RT1 · RT2 · RT7 — nada no conteúdo decide a espécie canônica."""

    def test_provedor_calado_e_NOT_KNOWN(self):
        especie, base = pv.especie_declarada({'text': 'qualquer coisa longa'})
        self.assertEqual(especie, pv.NAO_SEI)
        self.assertEqual(base, pv.NOT_DECLARED)

    def test_silencio_nunca_vira_original(self):
        """RT1 · o defeito mais fácil de todos."""
        especie, _ = pv.especie_declarada({})
        self.assertNotEqual(especie, pv.NATIVE_CAPTION_ORIGINAL)
        self.assertFalse(pv.serve_para_original(especie))

    def test_texto_ingles_com_titulo_italiano_nao_vira_TRANSLATED_canonico(self):
        """RT2 · a observação da C5 é leitura, e leitura não carimba."""
        especie, base = pv.especie_declarada(
            {'text': 'Olive growers, welcome back to issue 18'})
        self.assertEqual(especie, pv.NAO_SEI)
        self.assertNotEqual(especie, pv.NATIVE_CAPTION_TRANSLATED)
        self.assertEqual(base, pv.NOT_DECLARED)

    def test_a_decisao_canonica_nao_le_o_conteudo(self):
        """RT7 · nem regex, nem detector, nem comparação de título."""
        t = _fonte(DONO_DA_ESPECIE)
        i = t.index('def especie_declarada')
        corpo = t[i:t.index('\ndef ', i + 10)]
        for mau in ('.lower()', 're.', 'langdetect', 'detect', 'TITLE',
                    'DESCRIPTION', 'split('):
            self.assertNotIn(mau, corpo,
                             'a especie canonica passou a olhar o conteudo (%r)' % mau)


# ══════════════════════════════════════════════════════════════════════════
class T4OAsrLocalEDistinguivel(unittest.TestCase):
    """T4 · §20 · RT3 — o que esta casa produziu tem nome próprio."""

    def test_asr_local_e_uma_especie_propria(self):
        self.assertNotEqual(pv.ASR_LOCAL, pv.NATIVE_CAPTION_ORIGINAL)
        self.assertNotEqual(pv.ASR_LOCAL, pv.NATIVE_CAPTION_TRANSLATED)

    def test_o_dono_do_asr_nunca_declara_legenda_nativa(self):
        """RT3 · o reconhecedor local não pode sair como legenda da plataforma."""
        t = _fonte('ferramentas/fala_local.py')
        self.assertNotIn('NATIVE_CAPTION', t,
                         'o dono do ASR passou a falar em legenda nativa')

    def test_o_carimbo_do_asr_identifica_o_transcritor(self):
        import fala_local as fl                                 # noqa: PLC0415
        _d, _c, tr = fl.resolver_dispositivo('CPU')
        c = fl.carimbo('small', tr)
        self.assertEqual(c['TRANSCRIBER_ID'], 'ferramentas/fala_local.py')
        self.assertEqual(c['ASR_ENGINE'], 'faster-whisper')


# ══════════════════════════════════════════════════════════════════════════
class T7e8OConsumidorQuePrecisaDoOriginal(unittest.TestCase):
    """T7 · T8 · RT5 — `NOT_KNOWN` e `TRANSLATED` não entram onde precisa original."""

    def test_desconhecido_nao_serve_para_original(self):
        self.assertFalse(pv.serve_para_original(pv.NAO_SEI))

    def test_traduzida_nao_serve_para_original(self):
        self.assertFalse(pv.serve_para_original(pv.NATIVE_CAPTION_TRANSLATED))

    def test_original_e_asr_local_servem(self):
        self.assertTrue(pv.serve_para_original(pv.NATIVE_CAPTION_ORIGINAL))
        self.assertTrue(pv.serve_para_original(pv.ASR_LOCAL))

    def test_valor_invejado_fora_do_vocabulario_tambem_nao_serve(self):
        """A trava fecha por omissão: o que não está na lista, não passa."""
        for mau in ('ORIGINAL', 'NATIVE_CAPTION', '', None, 'YES', True):
            self.assertFalse(pv.serve_para_original(mau),
                             '%r passou pela trava do original' % mau)

    def test_o_lugar_do_fato_pergunta_a_especie(self):
        """O defeito que a C6 encontrou: ele decidia sem perguntar nada."""
        t = _fonte('regras/sensor_medir.py')
        i = t.index('def medir(')
        corpo = t[i:]
        self.assertIn('serve_para_original', corpo,
                      'o lugar do fato voltou a comer texto de especie desconhecida')

    def test_texto_sem_especie_nao_muda_o_lugar_do_fato(self):
        """A prova viva, com o caso real `EAkcA_2FDN8` que a C6 mediu.

        ⚠️ Correção a mim próprio: a primeira versão usava o título
        «Periodico olivo 1 Maggio 2026». Ele reprovou — e reprovou por estar
        CERTO: a palavra italiana «Periodico» sozinha já devolve `ES`, sem
        transcrição nenhuma. Ver a secção do relatório sobre a raiz `rio`.

            UM TESTE QUE USA UM CASO JÁ CONTAMINADO NÃO MEDE A TRAVA.

        Este título não dispara nada sozinho, e por isso isola o que interessa.

        ⚠️ Segunda correção, na C7. O texto inglês desta prova era *«in the prior
        period… superior… various… scenarios»* — palavras que mudavam o país
        porque a raiz truncada `rio` casava dentro delas. A C7 consertou isso, e
        ao consertá-lo tirou o chão desta prova: ela passou a não reproduzir.

            UMA PROVA QUE SE APOIA NUM DEFEITO MORRE QUANDO O DEFEITO MORRE.

        O texto passou a NOMEAR um lugar, que é o que um texto original faria.
        Agora a prova mede só o que lhe compete: se a ESPÉCIE do texto decide se
        ele entra — e não se o casador de lugar é bom.
        """
        import sensor_medir as sm                               # noqa: PLC0415
        titulo = 'CONTRASTO ALLA FLAVESCENZA DORATA DELLA VITE'
        so_fonte, _ = sm.lugar_do_fato(titulo)
        self.assertEqual(so_fonte, 'NOT_KNOWN',
                         'o titulo escolhido deixou de ser neutro — troque-o')

        ingles = ('In La Rioja the trial showed superior results across '
                  'several scenarios during the prior period.')
        com_texto, _ = sm.lugar_do_fato('%s %s' % (titulo, ingles))
        self.assertNotEqual(com_texto, so_fonte,
                            'o caso que motivou a trava deixou de reproduzir — '
                            'confirme antes de apagar esta prova')

        # E com a trava: texto de especie desconhecida nao entra.
        usado = ingles if pv.serve_para_original(pv.NAO_SEI) else ''
        com_trava, _ = sm.lugar_do_fato('%s %s' % (titulo, usado))
        self.assertEqual(com_trava, so_fonte,
                         'a trava nao impediu o texto de decidir o lugar do fato')

        # E com especie que SERVE, o texto volta a entrar — a trava filtra por
        # procedencia, nao bane texto.
        usado2 = ingles if pv.serve_para_original(pv.ASR_LOCAL) else ''
        com_asr, _ = sm.lugar_do_fato('%s %s' % (titulo, usado2))
        self.assertEqual(com_asr, com_texto,
                         'a trava barrou tambem o que tem procedencia provada')


# ══════════════════════════════════════════════════════════════════════════
class T9TraducaoNaoEBanidaGlobalmente(unittest.TestCase):
    """T9 · RT10 · §16 — fit-for-purpose é do consumidor, não da coleta."""

    def test_o_tipo_de_conteudo_continua_a_receber_o_texto(self):
        t = _fonte('regras/sensor_medir.py')
        i = t.index('def medir(')
        corpo = t[i:]
        self.assertIn('classificar_conteudo(v.get(\'TITLE\'), v.get(\'DESCRIPTION\'), tr)',
                      corpo,
                      'a traducao foi banida do tipo de conteudo — isso perde '
                      'capacidade para arrumar um campo')

    def test_nao_existe_rejeicao_global_de_traduzido(self):
        """Nenhum sítio trata `TRANSLATED` como lixo em toda a casa."""
        for pasta, dirs, fs in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('__pycache__', '.git', 'node_modules', 'system-map')]
            for f in fs:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(pasta, f), RAIZ)
                if rel.startswith('tests/'):
                    continue
                t = _fonte(rel)
                for mau in ('TRANSLATED = REJECTED', 'REJECT_TRANSLATED',
                            'DESCARTAR_TRADUZIDO'):
                    self.assertNotIn(mau, t, '%s bane traducao globalmente' % rel)

    def test_especie_nao_e_qualidade(self):
        """§19 · quatro espécies não são quatro qualidades."""
        t = _fonte(DONO_DA_ESPECIE)
        i = t.index('NATIVE_CAPTION_ORIGINAL =')
        corpo = t[max(0, i - 2000):i]
        self.assertIn('qualidade', corpo.lower(),
                      'o dono deixou de dizer que especie nao e qualidade')
        for mau in ('MELHOR', 'PIOR', 'SCORE', 'RANK'):
            self.assertNotIn(mau, t[i:i + 1500],
                             'nasceu hierarquia de qualidade entre especies')


# ══════════════════════════════════════════════════════════════════════════
class T10e11OHistoricoNaoFoiReescrito(unittest.TestCase):
    """T10 · T11 · RT6 · §7 · §24 — o que ficou gravado continua a dizer o que sabíamos."""

    def test_os_artefatos_historicos_nao_ganharam_especie(self):
        import glob                                             # noqa: PLC0415
        for f in glob.glob(os.path.join(PILOTO, 'TRANSCRICOES-*.json')):
            with io.open(f, encoding='utf-8') as fh:
                d = json.load(fh)
            for i in d.get('ITEMS') or []:
                self.assertNotIn('TRANSCRIPT_KIND', i,
                                 'o historico %s foi reescrito com especie' % f)

    def test_o_caso_italiano_continua_intacto(self):
        import glob                                             # noqa: PLC0415
        achou = None
        for f in glob.glob(os.path.join(PILOTO, 'TRANSCRICOES-*.json')):
            with io.open(f, encoding='utf-8') as fh:
                for i in json.load(fh).get('ITEMS') or []:
                    if 'RisRARQSFAg' in str(i.get('SOURCE_URL') or ''):
                        achou = i
        if achou is None:
            self.skipTest('o caso italiano nao esta neste ambiente')
        self.assertIn('Olive growers', (achou.get('TRANSCRIPT') or '')[:120],
                      'o texto ingles foi trocado — ele E a prova do defeito')
        self.assertEqual(achou.get('TRANSCRIPT_LANGUAGE'), 'NÃO SEI')

    def test_o_raw_nao_foi_tocado(self):
        r = subprocess.run(['git', 'status', '--short', '--', 'data/raw'],
                           cwd=RAIZ, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), '', 'o RAW mudou: %s' % r.stdout)


# ══════════════════════════════════════════════════════════════════════════
class T12AuditoriaNaoEIdentidade(unittest.TestCase):
    """§8 · §23 · RT2 — a suspeita vive ao lado do canônico, nunca por cima."""

    def _auditoria(self):
        if not os.path.exists(AUDITORIA):
            self.skipTest('o artefato de auditoria nao existe neste ambiente')
        with io.open(AUDITORIA, encoding='utf-8') as f:
            return json.load(f)

    def test_o_canonico_continua_NOT_KNOWN_em_todos(self):
        d = self._auditoria()
        canon = {x['TRANSCRIPT_KIND_CANONICAL'] for x in d['ITEMS']}
        self.assertEqual(canon, {pv.NAO_SEI},
                         'a auditoria carimbou especie canonica: %s' % canon)

    def test_os_campos_da_suspeita_tem_prefixo_proprio(self):
        d = self._auditoria()
        for x in d['ITEMS']:
            self.assertIn('AUDIT_TRANSLATION_SUSPECT', x)
            self.assertIn('AUDIT_BASIS', x)
            self.assertNotIn('TRANSCRIPT_KIND', x,
                             'a auditoria escreveu no campo canonico')

    def test_a_lei_esta_escrita_no_proprio_artefato(self):
        d = self._auditoria()
        self.assertIn('AUDIT_CLASSIFICATION != TRANSCRIPT_KIND', d['LEI'])

    def test_a_auditoria_declara_o_pai(self):
        """§25 · linhagem pelo contrato da casa, não por sistema novo."""
        d = self._auditoria()
        self.assertEqual(d['ARTIFACT_KIND'], 'DERIVED')
        self.assertTrue(d['PARENT_ARTIFACTS'])
        for p in d['PARENT_ARTIFACTS']:
            self.assertTrue(os.path.exists(os.path.join(RAIZ, p)),
                            'o pai declarado nao existe: %s' % p)

    def test_a_suspeita_tem_tres_estados_e_nao_dois(self):
        """Sem sinal de língua de um dos lados, não se afirma nada."""
        d = self._auditoria()
        vistos = {x['AUDIT_TRANSLATION_SUSPECT'] for x in d['ITEMS']}
        self.assertIn('UNKNOWN', vistos,
                      'a auditoria deixou de admitir que as vezes nao sabe')
        self.assertTrue(vistos <= {'YES', 'NO', 'UNKNOWN'}, vistos)

    def test_nenhum_codigo_le_a_auditoria_para_decidir_especie(self):
        """RT2 · o fio que nunca pode existir."""
        for pasta, dirs, fs in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('__pycache__', '.git', 'node_modules', 'system-map')]
            for f in fs:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(pasta, f), RAIZ)
                if rel.startswith('tests/') or 'auditoria' in rel:
                    continue
                t = _fonte(rel)
                self.assertNotIn('AUDIT_TRANSLATION_SUSPECT', t,
                                 '%s le a suspeita da auditoria' % rel)


# ══════════════════════════════════════════════════════════════════════════
class T13RawDeTesteVaiParaTemp(unittest.TestCase):
    """§30 — lei da casa desde a C2."""

    def test_a_suite_nao_deixou_bruto_de_teste_no_acervo(self):
        """A lei é sobre RAW FALSO de teste, não sobre artefato novo legítimo.

        ⚠️ Correção a mim próprio: a primeira versão reprovava QUALQUER ficheiro
        por rastrear em `data/`, e apanhou o artefato de auditoria desta missão —
        que é entrega, não lixo.

            «AINDA NAO COMMITADO» NAO E O MESMO QUE «LIXO DE TESTE».

        A pergunta certa é sobre bruto: pasta de RAW, cache de áudio, ficheiro
        com cara de temporário. Um derivado novo com nome declarado não é isso.
        """
        r = subprocess.run(['git', 'status', '--short'], cwd=RAIZ,
                           capture_output=True, text=True)
        marcas = ('raw-free/', 'raw-paid/', 'audio-cache/', 'html-bruto/',
                  '/tmp', '.tmp', 'TESTE', 'teste-')
        sujos = [ln for ln in r.stdout.splitlines()
                 if ln.startswith('??') and any(m in ln for m in marcas)]
        self.assertEqual(sujos, [], 'teste deixou bruto no acervo: %s' % sujos)

    def test_o_raw_preservado_continua_sem_alteracao(self):
        r = subprocess.run(['git', 'status', '--short', '--', 'data/raw'],
                           cwd=RAIZ, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), '', 'o RAW mudou: %s' % r.stdout)


# ══════════════════════════════════════════════════════════════════════════
class T14AsMissoesAnterioresNaoRegrediram(unittest.TestCase):
    """T12 · C1 a C5 continuam de pé."""

    def test_c5_o_gate_de_politica_continua_fechado(self):
        import social_matriz as mz                              # noqa: PLC0415
        rotas = mz.MATRIZ['YOUTUBE']['FETCH_TRANSCRIPT']
        estados = {r['ROTA']: r['ESTADO'] for r in rotas}
        self.assertEqual(estados['youtube-data-api-v3:captions.download'],
                         'REQUIRES_OWNER_PERMISSION')
        self.assertEqual(estados['timedtext'], 'ROUTE_NOT_ALLOWED')
        padrao = mz._rota_padrao(rotas)
        self.assertIn('apify', padrao['ROTA'],
                      'a rota de legenda mudou — a C6 nao podia mexer nisso')

    def test_c5_os_dois_atores_continuam_ligados(self):
        t = _fonte('regras/sensor_coleta.py')
        for a in ('pintostudio~youtube-transcript-scraper',
                  'starvibe~youtube-video-transcript'):
            self.assertIn(a, t, 'o ator %s foi retirado na C6' % a)

    def test_c4_o_padrao_do_reconhecedor_nao_mudou(self):
        import fala_local as fl                                 # noqa: PLC0415
        if not os.environ.get('SINTONIA_ASR_DEVICE'):
            self.assertEqual(fl.DISPOSITIVO_PADRAO, fl.CPU)
        self.assertEqual(fl.modelo_de('reel'), 'medium')
        self.assertEqual(fl.modelo_de('youtube'), 'small')

    def test_c3_as_capacidades_oficiais_continuam(self):
        import social_matriz as mz                              # noqa: PLC0415
        for cap in ('SEARCH_KEYWORD', 'INCREMENTAL', 'FETCH_VIDEO_METADATA',
                    'FETCH_COMMENTS'):
            padrao = mz._rota_padrao(mz.MATRIZ['YOUTUBE'][cap])
            self.assertEqual(padrao['PERMITIDA'], 'SIM',
                             '%s deixou de sair pela rota oficial' % cap)


if __name__ == '__main__':
    unittest.main(verbosity=2)
