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

    # ── FORMAS DE CREDENCIAL DE PLATAFORMA ──────────────────────────────────
    # As familias acima nasceram do SCRAP e cobrem cookie e cabecalho. Estas
    # nasceram do censo de seguranca: sao as chaves que ESTE projecto usa de
    # facto — Supabase, GitHub, Apify, Google — mais as duas formas genericas
    # que qualquer projecto acaba por colar num relatorio. Ficam aqui, e nao
    # num segundo varredor, porque a pergunta e a mesma e a pergunta tem um dono.
    #
    #     ONE CONCEPT -> ONE OWNER.
    ('chave Supabase', re.compile(r'\bsb_(secret|publishable)_[A-Za-z0-9_-]{15,}')),
    ('token de acesso Supabase', re.compile(r'\bsbp_[a-f0-9]{40}\b')),
    ('token GitHub', re.compile(r'\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b')),
    ('token GitHub (fine-grained)', re.compile(r'\bgithub_pat_[A-Za-z0-9_]{30,}')),
    ('token Apify', re.compile(r'\bapify_api_[A-Za-z0-9]{25,}')),
    ('chave de API Google', re.compile(r'\bAIza[A-Za-z0-9_-]{30,}')),
    ('chave de acesso AWS', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('chave OpenAI/generica sk-', re.compile(r'\bsk-[A-Za-z0-9]{40,}')),
    ('chave privada', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('JSON Web Token', re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}')),

    # DSN so conta quando aponta para FORA. O CI deste repositorio levanta um
    # Postgres descartavel em localhost com senha visivel de proposito, e
    # acusa-lo seria acusar exactamente a pratica correcta.
    #
    #     SENHA DE BANCO QUE MORRE COM O JOB NAO E SEGREDO.
    ('DSN de base de dados remota', re.compile(
        r'\bpostgres(?:ql)?://[^:@/\s"\']+:[^@/\s"\']{6,}@'
        r'(?!localhost|127\.0\.0\.1|db[:/]|postgres[:/])[A-Za-z0-9.-]+')),
)

# ── VALOR DECLARADO FALSO ────────────────────────────────────────────────────
# Uma forma de segredo pode aparecer legitimamente numa prova que precisa
# EXACTAMENTE dessa forma para provar que a redaccao funciona. A constante
# chama-se FAKE_JWT justamente para dizer isso a quem le. Sem esta excecao, a
# unica forma de calar a guarda seria apagar a prova — e ficariamos sem a prova.
#
#     FIXTURE WITH SECRET SHAPE IS SECRET TO THE SCANNER.
#     ENTAO A FIXTURE DECLARA-SE, OU CONSTROI-SE EM TEMPO DE EXECUCAO.
#
# A segunda familia sao os IDIOMAS DE PLACEHOLDER: ninguem tem uma senha que e
# literalmente a palavra «senha», nem um host chamado «host-interno». Quando o
# proprio VALOR se descreve como fictício, ele descreve-se para quem le o codigo
# e para a guarda ao mesmo tempo.
#
# A fronteira e `(?<![A-Za-z])`, e nao `\b`: o sublinhado E caracter de palavra,
# por isso `\bfake\b` NAO casa `FAKE_JWT` — que e precisamente o nome da
# constante que existe neste repositorio para provar a redaccao. A prova de
# formas apanhou este defeito antes de ele chegar a arvore.
#
#     A FRONTEIRA DE PALAVRA NAO E A FRONTEIRA QUE UM NOME DE CONSTANTE USA.
_DECLARADO_FALSO = re.compile(
    r'(?i)((?<![A-Za-z])(fake|dummy|exemplo|example|placeholder|redigido|redacted|'
    r'mock|sample|invalido|invalid|nao[_-]?e[_-]?segredo)(?![A-Za-z])'
    r'|senha[_-]?secreta|host[_-]?interno|:(senha|password|secret|pass|xxx)@)')


def _linha_declara_falso(texto, pos):
    ini = texto.rfind('\n', 0, pos) + 1
    fim = texto.find('\n', pos)
    return bool(_DECLARADO_FALSO.search(texto[ini:fim if fim != -1 else len(texto)]))

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


# ── O QUE É CÓDIGO, E NÃO UM SEGREDO ────────────────────────────────────────
# Medido em produção (`servico-20260923-0923`), `coleta/pesquisadores_t6.py:747`:
#
#     url += '&api_key=' + urllib.parse.quote(chave)
#
# A guarda acusou ESTA linha. O padrão de chave de API exige uma aspa depois de
# `api_key=`, e a encontra — a aspa que FECHA o literal `'&api_key='`. Dali, a
# classe do valor (`[^"']{8,}`) atravessa a linha, o `\n`, e só para na aspa
# SEGUINTE — sete linhas abaixo, dentro de uma docstring. O que a guarda leu
# como «valor» era, na verdade, um pedaço de código.
#
#     A ASPA QUE O PADRÃO ENCONTRA PODE SER A QUE FECHA O NOME, NÃO A QUE
#     ABRE O VALOR.
#
# A TENTAÇÃO ERA ENCURTAR O ALCANCE — proibir o `\n` na classe. Isso cala o
# falso positivo E CEGA A GUARDA: um segredo literal partido em duas linhas
# dentro de aspas deixaria de ser visto, e o dono mandou «não enfraquecer a
# guarda». O alcance FICA COMO ESTAVA; o que se acrescenta é o reconhecimento
# de que o valor apanhado é uma EXPRESSÃO e não um literal.
#
# Três famílias, todas ancoradas no INÍCIO do valor — de propósito. Ancorar no
# início é o que preserva o alcance: um literal que COMEÇA com o segredo (e
# segue por outras linhas) não casa nenhuma das três, e continua a ser achado.
_E_CODIGO = re.compile(
    r'^\s*["\']?\s*(?:'
    r'\+'                              # concatenação: ' + variavel
    r'|[A-Za-z_][A-Za-z0-9_.]*\s*\('   # chamada: quote( · urllib.parse.quote(
    r'|[fF][rR]?["\']'                 # f-string: f"{token}"
    r')')

# ── MAS RECONHECER CÓDIGO NÃO BASTA. FALTAVA A CONDIÇÃO. ────────────────────
# Medido contra a guarda ANTERIOR, caso a caso, e a primeira versão desta cura
# FOI REPROVADA POR ELA: cinco formas que o detector antigo apanhava passavam a
# escapar. A mais grave, porque é plausível:
#
#     api_key="+Ab1Cd2Ef3Gh4Ij5K"      um segredo a começar por `+`
#                                      (base64 começa por + com frequência)
#     password="abc(def)ghijkl"        um segredo com parêntese
#     sessionid=f"nao_isto"            um valor que só PARECE f-string
#
# Todas começam por `+`, por `nome(` ou por `f"` — exactamente as três famílias
# que `_E_CODIGO` reconhece. Reconhecer a FORMA não chegava; era preciso
# reconhecer a SITUAÇÃO. E a situação tem nome:
#
#     A ASPA QUE O PADRÃO CONSUMIU FECHA UM LITERAL ANTERIOR?
#
# Se fecha, o «valor» é código que vem depois — o falso positivo verdadeiro.
# Se ABRE, o valor é mesmo um literal, e nenhuma forma o pode absolver.
#
# Como se sabe: conta-se as aspas desde o início da linha até à aspa consumida.
# Ímpar = já estávamos dentro de um literal, logo esta fecha-o.
#
#     `api_key = "SEGREDO"`   → zero aspas antes → PAR → literal. Apanhado.
#     `url += '&api_key='`    → uma aspa antes  → ÍMPAR → fecha. Espúrio.
#
# A exclusão só dispara quando as DUAS coisas valem: a aspa é de fecho E o
# valor parece código. Assim as cinco formas acima continuam apanhadas, e o
# falso positivo de produção continua calado.
_CITACAO_DO_PADRAO = re.compile(r'[:=]\s*(["\'])')


def _citacao_espuria(texto, m):
    """A aspa consumida pelo padrão é de FECHO? (ímpares antes = sim)"""
    c = _CITACAO_DO_PADRAO.search(m.group(0))
    if not c:
        return False
    pos = m.start() + c.start(1)
    ini = texto.rfind('\n', 0, pos) + 1
    return (texto.count("'", ini, pos) % 2 == 1
            or texto.count('"', ini, pos) % 2 == 1)


def _valor_e_segredo(trecho, texto=None, m=None):
    """O padrão casou. Mas o VALOR é um segredo ou é uma referência a um?

    `texto` e `m` são o contexto do casamento. Sem eles a exclusão de código
    NÃO dispara — e o silêncio por omissão é o lado certo para o qual falhar:
    a guarda volta a acusar, e alguém olha. O contrário é que seria grave.
    """
    corte = re.split(r'[:=]', trecho, 1)
    valor = corte[1] if len(corte) > 1 else trecho
    valor = re.sub(r'(?i)^\s*(bearer|basic)\s+', '', valor.strip())
    if texto is not None and m is not None \
            and _E_CODIGO.match(valor) and _citacao_espuria(texto, m):
        return False
    return not _NAO_E_SEGREDO.match(valor)


# ── DÍVIDA CONHECIDA ────────────────────────────────────────────────────────
# Achado REAL, anterior a esta missão, em código que NÃO é do SINTONIA SCRAP.
# Fica listado — não silenciado. Listar é diferente de ignorar: a linha abaixo
# obriga quem mexer a decidir de novo, e o relatório continua mostrando.
#
# ⚠️ ESTAVA VAZIA DE VERDADE E CHEIA NO PAPEL. A única entrada apontava para
# `scripts/v21_tm_colher.py`, e isso deixou de ser um endereço: o ficheiro foi
# para a gaveta do que ele é (`motor/v21_tm_colher.py`) no commit `b8321b07`,
# o mesmo que desmontou `scripts/`. É a MESMA doença que o comentário do
# `PERMITIDOS` acima descreve, e a cura é a mesma.
#
# E a dívida em si também já não existe — medido, não presumido:
# `motor/v21_tm_colher.py` tem ZERO caminhos pessoais de Windows, e lê o
# `LOCALAPPDATA` do ambiente (`os.environ.get('LOCALAPPDATA')`, linha 59), que é
# a forma CERTA. Não havia o que perdoar, e o perdão continuava escrito.
#
#     UMA DIVIDA PERDOADA NUM ENDERECO QUE NAO EXISTE NAO PROTEGE NADA:
#     ELA SO ENSINA QUE A LISTA PODE ESTAR ERRADA.
#
# Fica vazia de propósito. Se o padrão voltar — ali ou em qualquer sítio — a
# guarda passa a acusá-lo como achado NOVO, que é o que ele seria.
DIVIDA_CONHECIDA = {
    # BUSCA-NO-ACTIONS (27/09): a pagina de cifo.it guardada como amostra RAW do juiz de pagina (C2-JUIZ, 74a76c2f)
    # traz a chave PUBLICA do Google Maps DO SITE (`maps.googleapis.com/maps/api/js?key=...`), que o site entrega a
    # qualquer visitante. Nao e credencial nossa, e o RAW nao se altera. Fica listada — o relatorio continua a mostra-la.
    'tests/dados/c2-juiz/raw-1558.html': 'chave publica do Google Maps do proprio cifo.it, dentro da pagina copiada '
                                         '(RAW de teste); nao e credencial do SINTONIA',
    # BUSCA-NO-ACTIONS (27/09): medido no ramo linha-busca-v1 @ 99eebc26 (sobre o vivo 2ef6fef8) — a guarda
    # acusava estes ficheiros, TODOS anteriores a esta missao, e por isso NENHUM workflow com o passo 0 passava.
    # Nenhum e credencial do SINTONIA. Ficam listados, um a um: o relatorio mostra-os em cada corrida, e um
    # achado NOVO continua a travar.
    'DEDUP-INSTALAR.md':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/PERIODO-E-CHAVES/testes-ANTES.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/PERIODO-E-CHAVES/testes-BATERIA-LEVE.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/PERIODO-E-CHAVES/testes-caderno-ANTES.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/QUATRO-CHAVES-MEDIR/testes-pendentes-ANTES.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/QUATRO-CHAVES-V2/testes-nuvem-sem-banco.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/QUATRO-CHAVES-V2/testes-por-nome-ANTES.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/RECEITA-T8-V1/testes-ANTES.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/RECEITA-T8-V1/vizinhos-ANTES.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'data/derivados/RECEITA-T8-V1/vizinhos-DEPOIS.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'ferramentas/big_collection/onda4/RODADA1-ROTEIRO.md':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'ferramentas/big_collection/onda_web.py':
        'caminho pessoal do Windows escrito no CODIGO (pasta de trabalho desta maquina); nao e credencial — trocar por ambiente/~ numa missao propria',
    'ferramentas/c9/ensaio/antes.err':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'ferramentas/c9/ensaio/depois.err':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'ferramentas/maestro_social/maestro_social.py':
        'caminho pessoal do Windows escrito no CODIGO (pasta de trabalho desta maquina); nao e credencial — trocar por ambiente/~ numa missao propria',
    'provas/integra_noite/lote3-pesado-sem036.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'provas/integra_noite/lote3-pesado-vivo.txt':
        'caminho pessoal do Windows dentro de um relatorio/saida guardado como prova; nao e credencial — a prova nao se reescreve',
    'provas/t2_boletins/rede/bytes/ae6395590f25cd3397f8.bin':
        'licenca PUBLICA do widget de acessibilidade accessiweb.it (data-license-key) dentro da pagina copiada (RAW de prova); nao e credencial do SINTONIA',
    'scripts/regua_t2/prova_d29_porta.py':
        'caminho pessoal do Windows escrito no CODIGO (pasta de trabalho desta maquina); nao e credencial — trocar por ambiente/~ numa missao propria',
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
            if m and _valor_e_segredo(m.group(0), texto, m) \
                    and not _linha_declara_falso(texto, m.start()):
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
