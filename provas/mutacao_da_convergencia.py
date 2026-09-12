#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DA CONVERGENCIA DO GASTO — SCRAP-CV-01.

    py provas/mutacao_da_convergencia.py

Uma suite verde nao prova que a lei esta viva: prova que a suite corre. Esta
prova ESTRAGA a lei, de 20 maneiras nomeadas, e pergunta se alguma prova cai.

    UM MUTANTE QUE SOBREVIVE E UMA LINHA QUE NINGUEM ESTA A MEDIR.

E A ANCORA TAMBEM E MEDIDA
---------------------------
Uma substituicao cujo texto aparece duas vezes no ficheiro nao mutou o que eu
pensava que mutou — mutou tambem outra coisa, ou nada. Ancora nao-unica conta
como SOBREVIVEU, nunca como morto: um mutante que nao chegou a nascer nao prova
defesa nenhuma.

O FICHEIRO VOLTA BYTE A BYTE
-----------------------------
Antes de cada mutacao guarda-se o sha256 do original; depois repoe-se e
confere-se o sha256. Uma prova de mutacao que deixa o codigo estragado e pior do
que nenhuma.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_AQUI)
SAIDA = os.path.join(RAIZ, 'data', 'derivados', 'MUTACAO-CONVERGENCIA-V1.json')

GUARDA = os.path.join(RAIZ, 'leis', 'autorizacao_de_gasto.py')
COLETOR = os.path.join(RAIZ, 'coleta', 'coletor.py')
SENSOR = os.path.join(RAIZ, 'regras', 'sensor_coleta.py')
ROTAS = os.path.join(RAIZ, 'coleta', 'social_rotas.py')

MORTO = 'MORTO'
SOBREVIVEU = 'SOBREVIVEU'

# (id, ficheiro, o que se estraga, ancora, substituicao)
MUTANTES = [
    ('M01', GUARDA, 'a guarda deixa de exigir o ledger',
     "    if orcamento_autorizado is None:\n"
     "        raise GastoRecusado('SEM_LEDGER_NAO_GASTEI', CAUSAS['SEM_LEDGER_NAO_GASTEI'])",
     "    if orcamento_autorizado is None:\n"
     "        orcamento_autorizado = autorizacao.max_usd"),

    ('M02', GUARDA, 'a relacao entre limite humano e ledger inverte-se',
     "    if float(orcamento_autorizado) > float(autorizacao.max_usd) + 1e-9:",
     "    if float(orcamento_autorizado) < float(autorizacao.max_usd) - 1e-9:"),

    ('M03', GUARDA, 'a conferencia deixa de olhar para as execucoes restantes',
     "    if autorizacao.restantes <= 0:\n"
     "        raise GastoRecusado('AUTORIZACAO_ESGOTADA', CAUSAS['AUTORIZACAO_ESGOTADA'])\n"
     "\n"
     "    recibo = autorizacao.para_o_manifesto()",
     "    recibo = autorizacao.para_o_manifesto()"),

    ('M04', GUARDA, 'consumir deixa de gastar a unidade',
     "    autorizacao._gastas += 1\n"
     "    return autorizacao.para_o_manifesto()",
     "    return autorizacao.para_o_manifesto()"),

    ('M05', GUARDA, 'consumir aceita autorizacao esgotada',
     "    if autorizacao.restantes <= 0:\n"
     "        raise GastoRecusado('AUTORIZACAO_ESGOTADA', CAUSAS['AUTORIZACAO_ESGOTADA'])\n"
     "    autorizacao._gastas += 1",
     "    autorizacao._gastas += 1"),

    ('M06', GUARDA, 'a guarda deixa de conferir o MOTIVO do gasto',
     "    if autorizacao.motivo != motivo:",
     "    if False and autorizacao.motivo != motivo:"),

    ('M07', GUARDA, 'a guarda deixa de conferir o PROPOSITO',
     "    if str(autorizacao.proposito) != str(proposito or '').strip():",
     "    if False and str(autorizacao.proposito) != str(proposito or '').strip():"),

    ('M08', GUARDA, 'a guarda deixa de conferir a FONTE',
     "        if str(source_id or '').strip() != autorizacao.source_id:",
     "        if False and str(source_id or '').strip() != autorizacao.source_id:"),

    ('M09', GUARDA, 'coleta normal volta a poder ser cheque em branco',
     "        if max_usd is None or float(max_usd) <= 0:\n"
     "            raise AutorizacaoInvalida(\n"
     "                'SEM_TETO_DE_DOLARES: %s' % CAUSAS['SEM_TETO_DE_DOLARES'])\n"
     "        n = int(max_execucoes) if max_execucoes else 1",
     "        n = int(max_execucoes) if max_execucoes else 1"),

    ('M10', GUARDA, 'a coleta normal deixa de perguntar ao dono da relevancia',
     "        if v['VEREDITO'] != rel.AUTORIZA:",
     "        if False and v['VEREDITO'] != rel.AUTORIZA:"),

    ('M11', GUARDA, 'o selo deixa de ser conferido no nascimento',
     "        if self._selo is not _SELO:",
     "        if False and self._selo is not _SELO:"),

    ('M12', GUARDA, 'a conferencia aceita qualquer objecto',
     "    if (not isinstance(autorizacao, Autorizacao)\n"
     "            or autorizacao._selo is not _SELO\n"
     "            or not _foi_concedida(autorizacao)):\n"
     "        raise GastoRecusado('AUTORIZACAO_FABRICADA', CAUSAS['AUTORIZACAO_FABRICADA'])\n"
     "    if autorizacao.motivo != motivo:",
     "    if autorizacao.motivo != motivo:"),

    ('M13', GUARDA, 'a conferencia autoriza tudo na primeira linha',
     "    if autorizacao is None:\n"
     "        raise GastoRecusado('AUTORIZACAO_AUSENTE', CAUSAS['AUTORIZACAO_AUSENTE'])",
     "    if autorizacao is None:\n"
     "        return {'VEREDITO': AUTORIZADO, 'ORCAMENTO_AUTORIZADO': 0.0}"),

    ('M14', COLETOR, 'a porta paga nunca conta a execucao gasta',
     "    recibo_da_autorizacao = dict(ag.consumir(autorizacao),",
     "    recibo_da_autorizacao = dict(autorizacao.para_o_manifesto(),"),

    ('M15', COLETOR, 'a guarda passa a receber sempre None em vez do ledger',
     "        orcamento_autorizado=(orcamento.autorizado if orcamento is not None else None))",
     "        orcamento_autorizado=autorizacao.max_usd if autorizacao is not None else None)"),

    ('M16', COLETOR, 'o teto do fornecedor deixa de ser rebaixado ao saldo',
     "        teto_usd = reserva.cap",
     "        pass"),

    ('M17', COLETOR, 'custo desconhecido volta a devolver o dinheiro ao saldo',
     "                    reserva.desconhecer()",
     "                    reserva.anular('MUTANTE')"),

    ('M18', COLETOR, 'a reserva deixa de rebaixar o pedido ao que resta',
     "            cap = resto if pedido_micros is None else min(pedido_micros, resto)",
     "            cap = resto if pedido_micros is None else pedido_micros"),

    ('M19', COLETOR, 'o POST volta a ser retentado',
     "    vezes = 1 if metodo.upper() in ('POST', 'PUT', 'PATCH', 'DELETE') else tentativas",
     "    vezes = tentativas"),

    ('M20', COLETOR, 'a recusa desta casa volta a vestir-se de falha da fonte',
     "    except _recusas_nossas():",
     "    except ():"),

    # ── O TRANSPORTE TROCADO (regras/sensor_coleta.py) ──────────────────────
    ('M21', SENSOR, 'o transporte substituto deixa de pagar o teto de acessos',
     "        _rede = coletor._orcamento_de_rede()",
     "        _rede = None"),

    ('M22', SENSOR, 'o transporte substituto volta a repetir o POST',
     "    vezes = 1 if metodo.upper() in ('POST', 'PUT', 'PATCH', 'DELETE') else 4",
     "    vezes = 4"),

    ('M23', SENSOR, 'a queda do POST volta a ser uma falha qualquer',
     "        raise coletor.PostTalvezCriado(",
     "        raise RuntimeError("),

    # ── A RECUSA QUE NAO SE PODE VESTIR DE OUTRA COISA ──────────────────────
    ('M27', COLETOR, 'a rede recusa e a execucao autorizada nao volta',
     "            if autorizacao is not None:\n"
     "                recibo_da_autorizacao = dict(\n"
     "                    ag.devolver(autorizacao,",
     "            if autorizacao is None:\n"
     "                recibo_da_autorizacao = dict(\n"
     "                    ag.devolver(autorizacao,"),

    ('M28', COLETOR, 'a execucao volta mesmo quando o POST talvez tenha saido',
     "        if not post_tentado:",
     "        if True:"),

    ('M29', COLETOR, 'o POST deixa de marcar que foi tentado',
     "            post_tentado = True\n"
     "        except PostTalvezCriado as e:",
     "            pass\n"
     "        except PostTalvezCriado as e:"),

    ('M30', GUARDA, 'devolver aceita uma autorizacao que nao foi concedida',
     "    if not isinstance(autorizacao, Autorizacao) or not _foi_concedida(autorizacao):\n"
     "        raise GastoRecusado('AUTORIZACAO_FABRICADA', CAUSAS['AUTORIZACAO_FABRICADA'])\n"
     "    if autorizacao._gastas <= 0:",
     "    if autorizacao._gastas <= 0:"),

    ('M24', GUARDA, 'a recusa de gasto volta a ser um OSError',
     "class GastoRecusado(RuntimeError):",
     "class GastoRecusado(PermissionError):"),

    ('M25', ROTAS, 'a rota deixa de deixar passar a recusa de autorizacao',
     "    except (SemOrcamentoDeRede, SemOrcamentoFinanceiro, GastoRecusado):",
     "    except (SemOrcamentoDeRede, SemOrcamentoFinanceiro):"),

    ('M26', GUARDA, 'copiar uma autorizacao volta a valer',
     "            or not _foi_concedida(autorizacao)):\n"
     "        raise GastoRecusado('AUTORIZACAO_FABRICADA', CAUSAS['AUTORIZACAO_FABRICADA'])\n"
     "    if autorizacao.motivo != motivo:",
     "            or False):\n"
     "        raise GastoRecusado('AUTORIZACAO_FABRICADA', CAUSAS['AUTORIZACAO_FABRICADA'])\n"
     "    if autorizacao.motivo != motivo:"),
]

PROVAS = (
    [sys.executable, '-m', 'pytest', 'tests/test_cv01_convergencia.py',
     'tests/test_c10_8af_orcamento_financeiro.py', '-q', '-p', 'no:cacheprovider'],
    [sys.executable, 'provas/red_team_da_convergencia.py'],
)


def sha(caminho):
    return hashlib.sha256(io.open(caminho, 'rb').read()).hexdigest()


def correr():
    """→ (morreu, quem_matou). Qualquer prova vermelha mata o mutante."""
    for cmd in PROVAS:
        r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True,
                           timeout=600)
        if r.returncode != 0:
            return True, os.path.basename(cmd[-1] if cmd[-1].endswith('.py')
                                          else cmd[2])
    return False, ''


def main():
    linhas, sobreviventes = [], 0
    for ident, ficheiro, o_que, ancora, troca in MUTANTES:
        original = io.open(ficheiro, encoding='utf-8').read()
        antes = sha(ficheiro)
        n = original.count(ancora)
        if n != 1:
            # ⚠️ NAO conta como morto. Um mutante que nao nasceu nao prova nada.
            linhas.append({'ID': ident, 'FICHEIRO': os.path.relpath(ficheiro, RAIZ),
                           'MUTACAO': o_que, 'VEREDITO': SOBREVIVEU,
                           'PORQUE': 'ancora aparece %d vezes: a mutacao nao e a '
                                     'que eu penso que e' % n})
            sobreviventes += 1
            print('  !  %-5s %-58s ANCORA x%d' % (ident, o_que[:58], n))
            continue

        io.open(ficheiro, 'w', encoding='utf-8').write(original.replace(ancora, troca, 1))
        try:
            morreu, quem = correr()
        finally:
            io.open(ficheiro, 'w', encoding='utf-8').write(original)
            depois = sha(ficheiro)
            assert depois == antes, 'o ficheiro %s NAO voltou ao original' % ficheiro

        sobreviventes += 0 if morreu else 1
        linhas.append({'ID': ident, 'FICHEIRO': os.path.relpath(ficheiro, RAIZ),
                       'MUTACAO': o_que,
                       'VEREDITO': MORTO if morreu else SOBREVIVEU,
                       'MORTO_POR': quem if morreu else ''})
        print('  %s  %-5s %-58s %s' % ('·' if morreu else '!', ident, o_que[:58],
                                       (MORTO + ' por ' + quem) if morreu else SOBREVIVEU))

    print()
    print('  MUTANTES = %d · MORTOS = %d · SURVIVORS = %d'
          % (len(linhas), len(linhas) - sobreviventes, sobreviventes))

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with io.open(SAIDA, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'CONTRATO': 'MUTACAO_CONVERGENCIA/v1',
                            'MUTANTES': len(linhas),
                            'MORTOS': len(linhas) - sobreviventes,
                            'SURVIVORS': sobreviventes,
                            'LINHAS': linhas}, ensure_ascii=False, indent=1))
    print('  escrito: %s' % os.path.relpath(SAIDA, RAIZ))
    return 1 if sobreviventes else 0


if __name__ == '__main__':
    raise SystemExit(main())
