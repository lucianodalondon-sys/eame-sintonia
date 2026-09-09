#!/usr/bin/env python3
"""O CONTRATO DA EVOLUCAO — so a espinha, e a promocao continua sendo humana.

    APRENDER AUTOMATICAMENTE  !=  PROMOVER AUTOMATICAMENTE.

Um sistema pode medir sozinho, comparar sozinho e ate ter razao sozinho. Nada
disso o autoriza a trocar a politica em producao sem alguem assinar. A
distancia entre as duas coisas e onde mora a diferenca entre um sistema que
melhora e um que muda de opiniao sem ninguem dar por isso.

O QUE ISTO E
------------
A ESPINHA: o vocabulario para representar que houve uma alternativa, que ela
foi comparada, e o que se decidiu. Nao ha ML, nao ha bandit, nao ha nada a
correr. Sem esta espinha, uma experiencia futura nao teria onde ser guardada —
e uma experiencia que nao fica guardada e uma experiencia que ninguem consegue
repetir nem desfazer.

    NAO SE APRENDE SEM PODER VOLTAR ATRAS.

⚠️ E SEM BASELINE NAO HA APRENDIZAGEM, HA SO MUDANCA
-----------------------------------------------------
Trocar uma politica e medir depois nao diz nada: nao se sabe como estava
antes. O `BASELINE` e o que torna a comparacao possivel, e ele e um artefato
guardado, nao uma lembranca.
"""

CONTRATO = 'EVOLUCAO/v1'

# ─────────────────────────────────────────────────────────────────────────
# O QUE COMPETE COM O QUE
# ─────────────────────────────────────────────────────────────────────────
PAPEIS = {
    'BASELINE': ('como estava antes de se mexer. Guardado, nao lembrado — sem '
                 'ele, trocar e medir depois nao diz nada'),
    'CHAMPION': 'a politica em uso hoje',
    'CHALLENGER': 'a alternativa que quer o lugar',
    'SHADOW': ('corre em paralelo e NAO afeta nada. O resultado dela e '
               'observado, nunca usado'),
}

# ⚠️ SHADOW NAO E CHALLENGER A MEIO.
# Uma sombra que influencia alguma decisao deixou de ser sombra — e a partir
# dai a comparacao esta contaminada, porque o campeao ja nao esta a jogar
# sozinho.
SOMBRA_NAO_TOCA = (
    'uma sombra que influencia qualquer decisao deixou de ser sombra, e a '
    'comparacao fica contaminada: o campeao ja nao esta a jogar sozinho.'
)

CAMPOS_DA_EXPERIENCIA = (
    'EXPERIMENT_ID', 'PERGUNTA', 'BASELINE_REF', 'CHAMPION_REF',
    'CHALLENGER_REF', 'MODO',              # SHADOW ou LIVE
    'METRICA_DECIDIDA_ANTES',              # ⚠️ ANTES, e nao depois
    'JANELA', 'AMOSTRA_MINIMA',
    'QUEM_ABRIU', 'QUANDO', 'POLICY_VERSION',
)

# ⚠️ A METRICA DECIDE-SE ANTES DE OLHAR O RESULTADO.
# Escolher a metrica depois de ver os numeros e escolher quem ganha. E o erro
# mais facil de cometer de boa fe: olha-se, ve-se que melhorou nalguma coisa, e
# passa-se a chamar «a metrica» a essa coisa.
METRICA_ANTES = (
    'escolher a metrica depois de ver os numeros e escolher quem ganha. E o '
    'erro mais facil de cometer de boa fe.'
)

RESULTADOS = (
    'CHALLENGER_BETTER',
    'CHAMPION_BETTER',
    'NO_DIFFERENCE',
    'INCONCLUSIVE',      # amostra pequena demais. NAO e NO_DIFFERENCE
    'ABORTED',
    'NOT_RUN',
)

# ⚠️ INCONCLUSIVE != NO_DIFFERENCE.
# «Nao deu para saber» e «sao iguais» levam a decisoes opostas: a primeira pede
# mais dados, a segunda fecha a questao.

# ─────────────────────────────────────────────────────────────────────────
# A PROMOCAO — e ela e SEMPRE um ato humano registado
# ─────────────────────────────────────────────────────────────────────────
CAMPOS_DA_PROMOCAO = (
    'PROMOTION_ID', 'EXPERIMENT_ID', 'DE_VERSAO', 'PARA_VERSAO',
    'PORQUE', 'QUEM_APROVOU', 'QUANDO',
    'COMO_SE_DESFAZ',                      # ⚠️ obrigatorio ANTES de promover
)
CAMPOS_DO_ROLLBACK = (
    'ROLLBACK_ID', 'PROMOTION_ID', 'PORQUE', 'QUEM_DECIDIU', 'QUANDO',
    'VOLTOU_PARA',
)

# Sem caminho de volta escrito ANTES, a promocao e uma porta de sentido unico.
SEM_VOLTA_NAO_SE_PROMOVE = (
    'COMO_SE_DESFAZ escreve-se antes de promover, nao depois de correr mal. '
    'Depois de correr mal, ninguem tem calma para o desenhar.'
)

PROIBIDO_HOJE = ('ML_LIVE', 'BANDIT_LIVE', 'AUTO_PROMOTION')
PORQUE_PROIBIDO = (
    'a fundacao da coleta ainda nao fechou. Um sistema que troca a propria '
    'politica sozinho, em cima de uma coleta que ainda nao sabe contar-se, '
    'muda de opiniao sem ninguem dar por isso — e sem baseline nem sequer da '
    'para saber se melhorou.'
)

LEIS = (
    'APRENDER AUTOMATICAMENTE != PROMOVER AUTOMATICAMENTE',
    'SEM BASELINE NAO HA APRENDIZAGEM, HA SO MUDANCA',
    'SHADOW NAO TOCA EM NADA',
    'A METRICA DECIDE-SE ANTES DE OLHAR O RESULTADO',
    'INCONCLUSIVE != NO_DIFFERENCE',
    'SEM CAMINHO DE VOLTA ESCRITO, NAO SE PROMOVE',
    'TODA PROMOCAO TEM UM HUMANO COM NOME',
)


def pode_promover(experiencia, resultado, aprovacao):
    """A porta. Devolve (pode?, porque).

    ⚠️ Ela e estreita de proposito. Cada `False` aqui e uma maneira conhecida
    de promover mal.
    """
    if resultado not in RESULTADOS:
        return False, 'resultado fora do vocabulario'
    if resultado != 'CHALLENGER_BETTER':
        return False, 'so se promove quem ganhou: %s' % resultado
    if not experiencia.get('METRICA_DECIDIDA_ANTES'):
        return False, 'metrica escolhida depois de ver os numeros'
    if not experiencia.get('BASELINE_REF'):
        return False, 'sem baseline nao ha com que comparar'
    if not aprovacao.get('QUEM_APROVOU'):
        return False, 'promocao sem humano com nome'
    if not aprovacao.get('COMO_SE_DESFAZ'):
        return False, 'sem caminho de volta escrito antes'
    return True, 'ganhou, com metrica declarada antes, baseline, dono e volta'


def main():
    print('CONTRATO %s' % CONTRATO)
    print('papeis %d · resultados %d' % (len(PAPEIS), len(RESULTADOS)))
    print('PROIBIDO HOJE: %s' % ', '.join(PROIBIDO_HOJE))
    for l in LEIS:
        print('  · %s' % l)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
