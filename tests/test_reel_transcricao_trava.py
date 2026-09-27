#!/usr/bin/env python3
"""
O CADEADO DO LOTE DE TRANSCRICOES — abre nos dois sistemas, e continua a ser cadeado.

    py tests/test_reel_transcricao_trava.py

O DEFEITO QUE ESTAS PROVAS FECHAM (medido em 2026-09-17, know-how §139)
--------------------------------------------------------------------------
`ferramentas/reel_transcricao.py` tinha `import fcntl` no topo. `fcntl` so existe em
POSIX: em Windows o modulo INTEIRO nao abria, os dez modulos de tests/ que o importam
morriam no `import`, e a contagem de testes da casa ficava NOT_MEASURABLE — por causa
de uma linha que so corre ao gravar um lote.

A cura segue o precedente medido de `admissao/admissao.py::_prender/_soltar` — e o
que se prova aqui e que a cura NAO afrouxou nada:

    O QUE SE PROVA                                   COMO
    · o modulo abre sem `fcntl`                      processo novo com `fcntl` bloqueado
                                                     em sys.modules (simula Windows em
                                                     POSIX; em Windows e o proprio sistema)
    · nenhum `import fcntl` ao nivel do modulo       AST, nao grep
    · a espera e nossa, sem teto                     LK_NBLCK e nunca LK_LOCK; LOCK_EX e
                                                     nunca LOCK_NB (a mesma guarda do livro
                                                     de decisoes)
    · EXCLUSAO ENTRE PROCESSOS                       este processo prende; um processo NOVO
                                                     sonda sem bloquear e ve OCUPADO; solta;
                                                     a sonda ve LIVRE
    · a contencao ESPERA e nao vira erro             este processo prende 1,2 s; um processo
                                                     NOVO chama gravar_lote() e ATRAVESSA
                                                     depois de esperar — nao rebenta, nao
                                                     desiste, nao escreve por cima
    · o cadeado solta depois de uma FALHA            um processo NOVO morre com o corpo do
                                                     lote a rebentar; a sonda ve LIVRE

Tudo corre numa casa de mentira (`tempfile`): o `SAIDA` da gaveta e redireccionado no
filho, e nada toca em `data/`.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import reel_transcricao as rt  # noqa: E402

NOME_DO_LOTE = 'TRANSCRICOES-REEL.json'


def _codigo_sem_prosa(rel):
    """O ficheiro sem comentarios nem docstrings, para a guarda olhar so para codigo."""
    import ast
    with io.open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        fonte = f.read()
    arvore = ast.parse(fonte)
    for no in ast.walk(arvore):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (no.body and isinstance(no.body[0], ast.Expr)
                    and isinstance(getattr(no.body[0], 'value', None), ast.Constant)
                    and isinstance(no.body[0].value.value, str)):
                no.body = no.body[1:] or [ast.Pass()]
    return ast.unparse(arvore)


# ── O FILHO: um processo novo que faz UMA coisa com o cadeado e conta o que viu ────
FILHO = r'''
import os, sys, json, time
ROOT, MODO, SAIDA, MARCAS = sys.argv[1:5]
sys.path.insert(0, ROOT)
import _gavetas
import reel_transcricao as rt
rt.SAIDA = SAIDA
os.makedirs(SAIDA, exist_ok=True)
CADEADO = os.path.join(SAIDA, %(lote)r + '.lock')

def marca(nome, **e):
    d = dict(e); d['MARCA'] = nome; d['T'] = time.time()
    with open(MARCAS, 'a', encoding='utf-8') as f:
        f.write(json.dumps(d) + '\n')

def sondar():
    """Tenta prender SEM esperar. -> 'LIVRE' ou 'OCUPADO'. E a sonda da prova, nao o contrato."""
    fd = os.open(CADEADO, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        try:
            import fcntl
        except ImportError:
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError:
                return 'OCUPADO'
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            return 'LIVRE'
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return 'OCUPADO'
        fcntl.flock(fd, fcntl.LOCK_UN)
        return 'LIVRE'
    finally:
        os.close(fd)

if MODO == 'SONDAR':
    marca('SONDA', VISTO=sondar())
elif MODO == 'GRAVAR':
    registo = {'REEL': {'POST_ID': 'TRAVA-TESTE'}, 'RUN_ID': 'RUN-FILHO', 'TRANSCRIPT_STATE': 'OK'}
    marca('PRONTO')
    t0 = time.monotonic()
    caminho, corpo = rt.gravar_lote([registo], nome=%(lote)r)
    marca('GRAVOU', ESPEROU=time.monotonic() - t0, ITENS=corpo['ITEM_COUNT'])
elif MODO == 'FALHAR':
    def rebenta(registos, caminho):
        marca('DENTRO_DO_CADEADO', VISTO_DE_DENTRO=sondar())
        raise RuntimeError('o corpo do lote rebentou de proposito')
    rt._gravar_lote_travado = rebenta
    try:
        rt.gravar_lote([{'REEL': {'POST_ID': 'X'}}], nome=%(lote)r)
    except RuntimeError as e:
        marca('REBENTOU', ERRO=str(e))
        sys.exit(97)
    marca('NAO_REBENTOU')
    sys.exit(1)
''' % {'lote': NOME_DO_LOTE}


class UmaCasaDeMentira(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='reel-trava-')
        self.saida = os.path.join(self.tmp, 'saida')
        os.makedirs(self.saida)
        self.filho = os.path.join(self.tmp, 'filho.py')
        with io.open(self.filho, 'w', encoding='utf-8') as f:
            f.write(FILHO)
        self.cadeado = os.path.join(self.saida, NOME_DO_LOTE + '.lock')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _lancar(self, modo):
        marcas = os.path.join(self.tmp, 'marcas-%s-%d.jsonl' % (modo, time.time_ns()))
        p = subprocess.Popen([sys.executable, self.filho, ROOT, modo, self.saida, marcas],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        return p, marcas

    def _correr(self, modo, timeout=120):
        p, marcas = self._lancar(modo)
        out, err = p.communicate(timeout=timeout)
        return p.returncode, self._marcas(marcas), err

    @staticmethod
    def _marcas(caminho):
        if not os.path.exists(caminho):
            return []
        with io.open(caminho, encoding='utf-8') as f:
            return [json.loads(l) for l in f if l.strip()]

    def _esperar_marca(self, marcas, nome, teto=60):
        fim = time.monotonic() + teto
        while time.monotonic() < fim:
            for m in self._marcas(marcas):
                if m['MARCA'] == nome:
                    return m
            time.sleep(0.02)
        self.fail('o filho nunca escreveu a marca %s' % nome)

    def _prender_daqui(self):
        fd = os.open(self.cadeado, os.O_CREAT | os.O_RDWR, 0o644)
        rt._prender(fd)                                        # noqa: SLF001
        return fd

    def _soltar_daqui(self, fd):
        rt._soltar(fd)                                         # noqa: SLF001
        os.close(fd)


class OModuloAbreNosDoisSistemas(unittest.TestCase):

    def test_importa_num_processo_onde_fcntl_nao_existe(self):
        """Simula o Windows em qualquer sistema: `fcntl` bloqueado ANTES do import."""
        guiao = ('import sys; sys.modules["fcntl"] = None\n'
                 'sys.path.insert(0, %r)\n'
                 'import _gavetas\n'
                 'import reel_transcricao as rt\n'
                 'print("ABRIU", callable(rt._prender), callable(rt._soltar))\n' % ROOT)
        r = subprocess.run([sys.executable, '-c', guiao], capture_output=True, text=True,
                           timeout=120, cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        self.assertEqual(0, r.returncode, r.stderr[-1200:])
        self.assertIn('ABRIU True True', r.stdout)

    def test_nenhum_import_fcntl_ao_nivel_do_modulo(self):
        import ast
        with io.open(os.path.join(ROOT, 'ferramentas', 'reel_transcricao.py'),
                     encoding='utf-8') as f:
            arvore = ast.parse(f.read())
        no_topo = [n for n in arvore.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        nomes = {a.name for n in no_topo if isinstance(n, ast.Import) for a in n.names}
        nomes |= {n.module for n in no_topo if isinstance(n, ast.ImportFrom)}
        self.assertNotIn('fcntl', nomes, 'voltou o `import fcntl` ao nivel do modulo')
        self.assertNotIn('msvcrt', nomes, 'um `import msvcrt` no topo partiria o POSIX')

    def test_a_espera_e_nossa_e_sem_teto_como_no_livro_de_decisoes(self):
        codigo = _codigo_sem_prosa('ferramentas/reel_transcricao.py')
        self.assertIn('LK_NBLCK', codigo, 'a espera do Windows deixou de ser nossa')
        self.assertNotIn('LK_LOCK', codigo, 'voltou o `LK_LOCK`, que traz teto proprio escondido')
        self.assertIn('LOCK_EX', codigo, 'o POSIX deixou de travar exclusivo')
        self.assertNotIn('LOCK_NB', codigo, 'o POSIX ganhou um cadeado que desiste')
        self.assertNotIn('_TETO', codigo, 'voltou um teto de espera escrito a mao')
        # E o cadeado continua em volta do ciclo inteiro, com os.replace no fim.
        self.assertIn('_prender(cadeado)', codigo)
        self.assertIn('_soltar(cadeado)', codigo)
        self.assertIn('os.replace(', codigo)


class OCadeadoEVisivelEntreProcessos(UmaCasaDeMentira):

    def test_um_processo_novo_ve_OCUPADO_enquanto_este_prende_e_LIVRE_depois(self):
        fd = self._prender_daqui()
        try:
            codigo, marcas, err = self._correr('SONDAR')
            self.assertEqual(0, codigo, err[-800:])
            self.assertEqual('OCUPADO', marcas[-1]['VISTO'],
                             'outro processo conseguiu prender o cadeado que este ja tinha')
        finally:
            self._soltar_daqui(fd)
        codigo, marcas, err = self._correr('SONDAR')
        self.assertEqual(0, codigo, err[-800:])
        self.assertEqual('LIVRE', marcas[-1]['VISTO'], 'o cadeado ficou preso depois de solto')

    def test_a_contencao_entre_processos_ESPERA_e_atravessa(self):
        """QUEM ESPERA PELO CADEADO, ESPERA. Contencao legitima nao e falha — e o filho e
        um processo de verdade, nao um fio deste."""
        fd = self._prender_daqui()
        p, marcas = self._lancar('GRAVAR')
        try:
            self._esperar_marca(marcas, 'PRONTO')
            # Segura bem para la do que uma tentativa unica aguentaria.
            time.sleep(1.2)
            self.assertIsNone(p.poll(), 'o filho terminou enquanto o cadeado estava preso — '
                                        'ou nao esperou, ou rebentou')
            self.assertEqual([], [m for m in self._marcas(marcas) if m['MARCA'] == 'GRAVOU'],
                             'o filho gravou por cima do cadeado preso')
        finally:
            self._soltar_daqui(fd)
        # ⚠️ O teto e da PROVA, nao do cadeado: existe so para a falha ter voz.
        out, err = p.communicate(timeout=120)
        self.assertEqual(0, p.returncode, err[-1200:])
        gravou = self._esperar_marca(marcas, 'GRAVOU', teto=5)
        self.assertGreaterEqual(gravou['ESPEROU'], 1.0,
                                'o filho nao esperou pelo cadeado — ou ele nao estava preso, '
                                'e entao esta prova nao mede nada')
        self.assertEqual(1, gravou['ITENS'])
        with io.open(os.path.join(self.saida, NOME_DO_LOTE), encoding='utf-8') as f:
            self.assertEqual(1, json.load(f)['ITEM_COUNT'])

    def test_o_cadeado_solta_depois_de_o_corpo_do_lote_rebentar(self):
        codigo, marcas, err = self._correr('FALHAR')
        self.assertEqual(97, codigo, 'o filho nao rebentou como devia: %s' % err[-800:])
        dentro = [m for m in marcas if m['MARCA'] == 'DENTRO_DO_CADEADO']
        self.assertEqual(1, len(dentro))
        self.assertEqual('OCUPADO', dentro[0]['VISTO_DE_DENTRO'],
                         'o cadeado nao estava preso enquanto o corpo corria')
        self.assertTrue(any(m['MARCA'] == 'REBENTOU' for m in marcas))
        # E depois da morte, um processo novo entra sem esperar.
        t0 = time.monotonic()
        codigo, marcas, err = self._correr('SONDAR')
        self.assertEqual(0, codigo, err[-800:])
        self.assertEqual('LIVRE', marcas[-1]['VISTO'], 'o cadeado ficou preso depois da falha')
        self.assertLess(time.monotonic() - t0, 60)
        self.assertFalse(os.path.exists(os.path.join(self.saida, NOME_DO_LOTE)),
                         'um lote que rebentou a meio deixou ficheiro escrito')

    def test_e_neste_processo_a_falha_tambem_solta(self):
        """A mesma garantia sem subprocesso: o `finally` solta e fecha o descritor."""
        antes, rt.SAIDA = rt.SAIDA, self.saida
        original = rt._gravar_lote_travado
        rt._gravar_lote_travado = lambda registos, caminho: (_ for _ in ()).throw(
            RuntimeError('rebentou'))
        try:
            with self.assertRaises(RuntimeError):
                rt.gravar_lote([{'REEL': {'POST_ID': 'Y'}}], nome=NOME_DO_LOTE)
        finally:
            rt._gravar_lote_travado = original
            rt.SAIDA = antes
        codigo, marcas, err = self._correr('SONDAR')
        self.assertEqual(0, codigo, err[-800:])
        self.assertEqual('LIVRE', marcas[-1]['VISTO'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
