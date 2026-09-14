# COMO PROVISIONAR A SESSÃO LOCAL

> **O GITHUB DISPARA. O PC EXECUTA. O NAVEGADOR LOCAL MANTÉM A SESSÃO.
> A SENHA NÃO VIAJA. O COOKIE NÃO VAI PARA O REPO.**

Guia de operação, para a máquina do runner. Cinco minutos, uma vez.

---

## ANTES DE COMEÇAR — leia esta parte

Estar logado **não** autoriza automatizar. Hoje, contra conta de **terceiro**,
`LOCAL_SESSION` está **fechada nas sete plataformas prioritárias** — cada NÃO
cita a cláusula do contrato em `scripts/social_sessao.py`. A rota fica pronta
para **conta própria da ADAMA** e para o dia em que houver permissão escrita.

```
py scripts/social_sessao.py politica     # a tabela, com as cláusulas
```

Provisionar o perfil é útil mesmo assim: é o que permite ler o **nosso** canal,
a **nossa** página, a **nossa** conta — onde a permissão não está em dúvida.

---

## 1 · CRIAR O PERFIL DEDICADO

Nunca use o perfil pessoal do Chrome. Um perfil separado significa que uma
coleta com defeito não alcança seu e-mail, seu banco nem suas abas.

O padrão já serve, e fica fora do repositório:
`%USERPROFILE%\.sintonia-browser\chrome-profile` (ou `~/.sintonia-browser/…`).

Para outro lugar, defina **na máquina**, nunca no repositório:

```powershell
setx SINTONIA_BROWSER_PROFILE_DIR "D:\sintonia\chrome-profile"   # Windows
```

Para o workflow enxergar o caminho, cadastre-o como **Variable** do repositório
(`Settings → Variables`) — **nunca Secret, nunca no código**. Caminho não é
segredo; mas o nome de usuário dentro dele é dado pessoal.

---

## 2 · FAZER O LOGIN — À MÃO, UMA VEZ

Abra o Chrome **com esse perfil** e faça login você mesmo:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --user-data-dir="$env:SINTONIA_BROWSER_PROFILE_DIR" `
  --no-first-run --no-default-browser-check
```

Entre nas plataformas necessárias, resolva o MFA na hora, e feche.

**O SINTONIA nunca faz isto por você:** não abre página de login, não digita
e-mail nem senha, não lê OTP, SMS ou e-mail, não resolve CAPTCHA. Há um teste
que falha se alguém tentar acrescentar isso (`TestNaoAutentica`).

---

## 3 · CONFERIR

```
py scripts/social_scrap.py sessao        # o perfil existe? o Chrome existe?
py scripts/social_scrap.py guarda        # nenhum segredo entrou no Git
```

O `sessao` responde um destes:

| estado | o que fazer |
|---|---|
| `SESSION_AVAILABLE` | perfil e navegador presentes — a rota pode ser tentada |
| `SESSION_MISSING` | o perfil ainda não foi criado — volte ao passo 1 |
| `LOCAL_SESSION_UNHEALTHY` | sem Chrome, perfil ilegível, ou perfil **dentro do repo** |

`SESSION_AVAILABLE` diz que a rota é **tentável**. Não diz que você está logado,
e não diz que a automação é permitida — são três perguntas diferentes.

---

## 4 · QUANDO A SESSÃO CAI

Sessão de navegador expira. É normal, e o sistema **para** em vez de insistir:

| estado | significado | ação |
|---|---|---|
| `SESSION_EXPIRED` | a sessão caducou | refazer o passo 2 |
| `LOGIN_REQUIRED` | apareceu muro de login | refazer o passo 2 |
| `MFA_REQUIRED` | pediram segundo fator | **só humano** — nunca automatizado |
| `PLATFORM_BLOCKED` | a plataforma barrou | **parar**, não insistir |

A regra que protege o corpus:

> **MURO DE LOGIN NÃO É CONTA VAZIA. BLOQUEIO NÃO É CONTEÚDO INEXISTENTE.**

Uma sessão ruim nunca vira "não há posts". Isso envenenaria o dado sem ninguém
perceber, porque o número continuaria plausível.

---

## 5 · O QUE NUNCA VAI PARA O GITHUB

Senha · e-mail de login · cookie · session token · csrf token · `localStorage`
· `Login Data` · `Web Data` · `History` · `cookies.sqlite` · perfil do Chrome
· qualquer caminho com o seu nome de usuário.

Três travas, nesta ordem:

1. **`.gitignore`** — impede o que ainda não entrou;
2. **`scripts/social_guarda.py`** — **falha o commit**, e também varre o que já
   está rastreado (o `.gitignore` não protege arquivo já versionado);
3. **`social_sessao.redigir()`** — apaga segredo e caminho pessoal de log,
   exceção e manifesto, antes de qualquer coisa ser impressa.

O GitHub pode guardar **token de API**, como Secret. Não guarda senha humana nem
sessão web:

> **GITHUB NÃO É COFRE DE SENHA HUMANA.
> SE É SESSÃO WEB, MORA NO PC LOCAL.**

---

## 6 · RISCO PARA A CONTA, E COMO ELE FOI REDUZIDO

Automação sobre conta logada pode levar a bloqueio. Por isso: a conta **não é a
pessoal**; contra terceiro a rota está **fechada por política**, não por
descuido; `PLATFORM_BLOCKED` **para** a rota em vez de insistir; o executor não
esconde que é automação, não troca fingerprint e não evade limite de taxa; e a
rota pública deslogada continua preferida sempre que resolve.

> **USAR O PC LOCAL É VANTAGEM OPERACIONAL, NÃO ATALHO PARA VIOLAR REGRA.**
