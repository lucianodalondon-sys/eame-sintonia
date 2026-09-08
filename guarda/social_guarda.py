#!/usr/bin/env python3
"""
GUARDA DE CREDENCIAL — a trava que impede o cookie de entrar no Git.

    py guarda/social_guarda.py            # varre o que está RASTREADO e o que está EM STAGE
    py guarda/social_guarda.py --staged   # só o que está a um `git commit` de distância

    O GITHUB NÃO É COFRE DE SENHA HUMANA.

Existe porque a regra "não commitar cookie" não se cumpre sozinha. Ela se cumpre
quando alguém a executa antes do commit — e a única forma de garantir isso é ter
um programa que falha.

O QUE ELE PROCURA, E POR QUE ESSAS COISAS
-------------------------------------------
Duas famílias, e as duas já vazaram em projetos reais:

    ARQUIVO   o Chrome guarda sessão em arquivos de nome conhecido — `Cookies`,
              `Login Data`, `Web Data`, `History`, `cookies.sqlite`. Um
              `git add -A` dentro de um perfil leva todos de uma vez, e o
              `.gitignore` não pega o que já está rastreado.
    CONTEÚDO  `Cookie: sessionid=...`, `Authorization: Bearer ...`, `li_at`,
              `ds_user_id`. Esses entram por caminho tortuoso: um traceback
              colado num JSON de teste, um HTML de prova salvo com o cabeçalho
              da requisição junto.

A SEGUNDA É A QUE PEGA GENTE CUIDADOSA. Ninguém escreve `senha = "..."` num
commit; o que acontece é salvar a evidência de uma coleta e não perceber que a
evidência trouxe o cabeçalho.

POR QUE ELE OLHA O RASTREADO, E NÃO SÓ O STAGE
------------------------------------------------
`.gitignore` só protege o que ainda NÃO entrou. Arquivo já rastreado continua
sendo versionado a cada mudança, ignorado ou não. Então a varredura tem que
perguntar as duas coisas: "isto está para entrar?" e "isto já entrou?".

FALSO POSITIVO É BARATO; FALSO NEGATIVO É PERMANENTE
------------------------------------------------------
Um segredo commitado não sai do histórico com `git rm` — ele fica no pack para
sempre, e a limpeza custa reescrever histórico. Por isso a guarda erra para o
lado de reclamar demais, e por isso ela tem `PERMITIDOS`: a exceção é explícita,
uma linha por caso, revisável — nunca uma regex frouxa.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Nomes de arquivo que o navegador usa para guardar sessão e credencial.
ARQUIVOS_PROIBIDOS = re.compile(
    r'(?i)(^|/)(cookies(\.sqlite)?|cookies-journal|login data|login data-journal|'
    r'web data|web data-journal|history|history-journal|'
    r'local storage|session storage|leveldb|'
    r'key4\.db|key3\.db|logins\.json|signons\.sqlite|'
    r'\.chrome-profile|chrome-profile|browser-profile|'
    r'credentials\.json|token\.json|cookies\.txt|cookiejar)(/|$)')

# Diretórios inteiros que nunca podem entrar.
PASTAS_PROIBIDAS = re.compile(
    r'(?i)(^|/)(default/(cookies|login data|web data)|'
    r'\.sintonia-browser|chrome-profile|firefox-profile)(/|$)')

# Conteúdo. Cada padrão aqui já foi um vazamento real em algum projeto.
CONTEUDO_PROIBIDO = (
    # `(?!<)` e a MESMA excecao que o padrao de caminho Windows abaixo ja
    # usava: um marcador `<REDIGIDO ...>` nao e segredo, e valor de cookie
    # real nunca comeca por `<`. Sem ela, redigir a origem virava um achado
    # novo, e o unico jeito de calar o guarda seria apagar o cabecalho —
    # perder a prova de que o servidor o mandou.
    ('cabeçalho Cookie', re.compile(r'(?i)\bcookie\s*:\s*(?!<)\S{8,}')),
    ('Set-Cookie', re.compile(r'(?i)\bset-cookie\s*:\s*(?!<)\S{8,}')),
    ('Authorization', re.compile(r'(?i)\bauthorization\s*:\s*(bearer|basic)\s+\S{8,}')),
    ('sessionid', re.compile(r'(?i)\b(sessionid|sessid|session_token)\s*[:=]\s*["\']?\S{8,}')),
    ('token de sessão LinkedIn', re.compile(r'(?i)\bli_at\s*[:=]\s*["\']?\S{8,}')),
    ('id de usuário Instagram', re.compile(r'(?i)\bds_user_id\s*[:=]\s*["\']?\S{6,}')),
    ('csrf token', re.compile(r'(?i)\b(csrftoken|x-csrf-token)\s*[:=]\s*["\']?\S{8,}')),
    ('access/refresh token', re.compile(r'(?i)\b(access_token|refresh_token)\s*[:=]\s*["\']?\S{12,}')),
    ('senha literal', re.compile(r'(?i)\b(password|passwd|senha)\s*[:=]\s*["\'][^"\']{3,}["\']')),
    ('chave de API literal', re.compile(r'(?i)\b(api[_-]?key|client[_-]?secret)\s*[:=]\s*["\'][^"\']{8,}["\']')),
    ('caminho pessoal Windows', re.compile(r'(?i)[A-Z]:\\Users\\(?!<)[^\\\s"\']{2,}')),
)

# A exceção é sempre explícita e sempre nomeada. Estes arquivos DESCREVEM os
# padrões (é o trabalho deles) e por isso casariam com as próprias regras.
# Os caminhos seguem as GAVETAS: quando o SCRAP entrou na árvore canônica,
# `scripts/` deixou de existir, e esta lista ficou apontando para o vazio — a
# guarda passou a acusar a própria docstring, que descreve `Cookie: sessionid=…`
# porque descrever é o trabalho dela. Uma exceção que aponta para um caminho
# morto não é exceção: é ruído, e ruído é o que faz alguém desligar a guarda.
PERMITIDOS = {
    'guarda/social_guarda.py',
    'guarda/social_sessao.py',
    'tests/test_social_sessao.py',
    'docs/operacao/HOW-TO-PROVISION-LOCAL-SESSION.md',
}

# ── O QUE NÃO É SEGREDO, POR MAIS QUE PAREÇA ────────────────────────────────
# Medido na primeira execução desta guarda, em 2026-09-08: ela acusou quatro
# arquivos e TRÊS eram `Authorization: Bearer $SUPABASE_SECRET_KEY` — referência
# a variável, que é exatamente o jeito CERTO de escrever. Uma guarda que reclama
# do jeito certo é desligada na terceira vez, e aí não guarda mais nada.
#
#     GUARDA QUE GRITA DEMAIS VIRA GUARDA DESLIGADA.
#
# Então o valor é examinado: se ele é uma variável de shell, uma expressão de
# workflow, um marcador de exemplo ou uma redação nossa, não é segredo.
_NAO_E_SEGREDO = re.compile(
    r'^\s*["\']?('
    r'\$[A-Za-z_{(]'              # $VAR, ${VAR}, $(cmd)
    r'|\$\{\{'                    # ${{ secrets.X }}
    r'|%[A-Za-z_]+%'              # %VAR% do Windows
    r'|<[^>]+>'                   # <SHA>, <TOKEN>, <CAMINHO-LOCAL>
    r'|\{\{?[A-Za-z_]'            # {var} / {{var}}
    r'|xxx|yyy|zzz|\.\.\.'
    r'|exemplo|example|placeholder|redigido|redacted|seu[_-]|your[_-]'
    r')')


def _valor_e_segredo(trecho):
    """O padrão casou. Mas o VALOR é um segredo ou é uma referência a um?"""
    corte = re.split(r'[:=]', trecho, 1)
    valor = corte[1] if len(corte) > 1 else trecho
    valor = re.sub(r'(?i)^\s*(bearer|basic)\s+', '', valor.strip())
    return not _NAO_E_SEGREDO.match(valor)


# ── DÍVIDA CONHECIDA ────────────────────────────────────────────────────────
# Achado REAL, anterior a esta missão, em código que NÃO é do SINTONIA SCRAP.
# Fica listado — não silenciado. Listar é diferente de ignorar: a linha abaixo
# obriga quem mexer a decidir de novo, e o relatório continua mostrando.
DIVIDA_CONHECIDA = {
    'scripts/v21_tm_colher.py':
        ('caminho pessoal de Windows embutido como padrão de `LOCALAPPDATA`. '
         'Expõe o nome de usuário da máquina. É da cadeia v21, fora do escopo '
         'desta missão — reportado, não alterado, para não colidir com a missão '
         'paralela.'),
}

# Extensões que não vale a pena abrir procurando texto.
BINARIOS = re.compile(r'(?i)\.(png|jpg|jpeg|gif|webp|pdf|zip|gz|woff2?|ttf|otf|ico|mp4|mp3)$')

LIMITE_BYTES = 2_000_000


def _git(*args):
    try:
        out = subprocess.run(['git'] + list(args), cwd=ROOT, capture_output=True,
                             text=True, timeout=60)
        return [l for l in out.stdout.splitlines() if l.strip()]
    except Exception:
        return []


def rastreados():
    return _git('ls-files')


def em_stage():
    return _git('diff', '--cached', '--name-only')


def varrer(caminhos, rotulo):
    achados = []
    for rel in caminhos:
        if rel in PERMITIDOS:
            continue
        if PASTAS_PROIBIDAS.search(rel) or ARQUIVOS_PROIBIDOS.search(rel):
            achados.append((rotulo, rel, 'NOME DE ARQUIVO',
                            'nome típico de dado de sessão do navegador'))
            continue
        if BINARIOS.search(rel):
            continue
        caminho = os.path.join(ROOT, rel)
        if not os.path.isfile(caminho) or os.path.getsize(caminho) > LIMITE_BYTES:
            continue
        try:
            with open(caminho, encoding='utf-8', errors='ignore') as f:
                texto = f.read()
        except OSError:
            continue
        for nome, padrao in CONTEUDO_PROIBIDO:
            m = padrao.search(texto)
            if m and _valor_e_segredo(m.group(0)):
                linha = texto[:m.start()].count('\n') + 1
                achados.append((rotulo, '%s:%d' % (rel, linha), nome,
                                # O trecho NUNCA é impresso. Dizer QUE achou e
                                # ONDE é suficiente para consertar; imprimir o
                                # valor seria vazar no próprio log da guarda.
                                'padrão encontrado — trecho não é exibido de propósito'))
                break
    return achados


def main():
    so_stage = '--staged' in sys.argv
    alvos = [('EM STAGE', em_stage())]
    if not so_stage:
        alvos.append(('RASTREADO', rastreados()))

    achados, divida = [], []
    for rotulo, caminhos in alvos:
        for a in varrer(caminhos, rotulo):
            (divida if a[1].split(':')[0] in DIVIDA_CONHECIDA else achados).append(a)

    print('\nGUARDA DE CREDENCIAL\n' + '═' * 70)
    for rotulo, caminhos in alvos:
        print('  %-12s %d arquivos varridos' % (rotulo, len(caminhos)))
    if divida:
        print('\n  DÍVIDA CONHECIDA (achado real, fora do escopo desta missão):')
        for _, onde, tipo, _ in divida:
            arq = onde.split(':')[0]
            print('    %s — %s' % (onde, tipo))
            print('        %s' % DIVIDA_CONHECIDA[arq])
    if not achados:
        print('\n  NENHUM segredo, cookie, perfil de navegador ou caminho pessoal novo.')
        print('  O repositório continua sem credencial humana.\n')
        return 0
    print('\n  %d ACHADO(S) — o commit NÃO deve seguir:\n' % len(achados))
    for rotulo, onde, tipo, porque in achados:
        print('    [%s] %s' % (rotulo, onde))
        print('        %s · %s' % (tipo, porque))
    print('\n  Conserte a ORIGEM. Um segredo commitado não sai do histórico com')
    print('  `git rm` — ele fica no pack para sempre.\n')
    return 1


if __name__ == '__main__':
    sys.exit(main())
