#!/usr/bin/env python3
"""
COBERTURA É SAÍDA DE PRIMEIRA CLASSE — nunca um detalhe do rodapé.

D-010 decidiu que 68,8% declarado vence 96,9% silenciosamente falso. Este módulo
generaliza a decisão **sem inventar score**: quem separa, normaliza ou casa qualquer
coisa devolve a contagem inteira, não só a lista que deu certo.

    TOTAL       linhas que entraram
    RESOLVED    linhas com resposta única e verificada
    AMBIGUOUS   linhas com mais de um candidato plausível — NÃO é resolvido
    UNRESOLVED  linhas sem candidato, com o motivo
    COVERAGE    RESOLVED / TOTAL

`AMBIGUOUS` existe separado de propósito: colapsá-lo em `RESOLVED` é a forma mais
comum de inflar cobertura, e colapsá-lo em `UNRESOLVED` esconde que a fonte tinha
sinal e o critério é que faltou.

E a regra que fecha a porta: `Coverage.require()` **levanta** se a cobertura ficar
abaixo do piso declarado. Um pipeline que degrada tem de parar, não de entregar um
número menor com a mesma cara de sempre.
"""
from collections import Counter


class CoverageError(RuntimeError):
    """Cobertura abaixo do piso declarado. Falha fechada, sem número parcial."""


class Coverage:
    def __init__(self, name):
        self.name = name
        self.resolved = []
        self.ambiguous = []
        self.unresolved = []
        self.reasons = Counter()

    def ok(self, item):
        self.resolved.append(item)

    def ambiguity(self, item, candidates, reason='MULTIPLE_CANDIDATES'):
        self.ambiguous.append({'item': item, 'candidates': candidates, 'reason': reason})
        self.reasons[reason] += 1

    def fail(self, item, reason):
        self.unresolved.append({'item': item, 'reason': reason})
        self.reasons[reason] += 1

    @property
    def total(self):
        return len(self.resolved) + len(self.ambiguous) + len(self.unresolved)

    @property
    def coverage(self):
        return round(len(self.resolved) / self.total, 4) if self.total else None

    def report(self):
        return {
            'NAME': self.name,
            'TOTAL': self.total,
            'RESOLVED': len(self.resolved),
            'AMBIGUOUS': len(self.ambiguous),
            'UNRESOLVED': len(self.unresolved),
            'COVERAGE': self.coverage,
            'REASONS': dict(self.reasons),
        }

    def require(self, floor):
        """Piso declarado. Abaixo dele o pipeline para — não entrega meio resultado."""
        if self.total == 0:
            raise CoverageError(f'{self.name}: zero linhas na entrada. '
                                'Zero não é resultado, é falha de fonte.')
        if self.coverage < floor:
            raise CoverageError(
                f'{self.name}: cobertura {self.coverage:.1%} abaixo do piso {floor:.1%} '
                f'({len(self.resolved)}/{self.total}); motivos: {dict(self.reasons)}')
        return self

    def __repr__(self):
        return (f'<Coverage {self.name} {len(self.resolved)}/{self.total} '
                f'= {self.coverage} · ambíguas {len(self.ambiguous)}>')
