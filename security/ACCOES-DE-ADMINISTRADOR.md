# O QUE DEPENDE DE UM CLIQUE

Tudo o que se conseguia fazer em codigo foi feito em codigo. O que sobra precisa
de uma sessao de administrador, e esta pagina existe para que isso seja um
minuto de trabalho e nao uma investigacao.

Um passo por definicao. O efeito, e como desfazer.

---

## 1 · Proteger os previews da Vercel

**Onde** Vercel, projecto `sintonia-eame-preview`, Settings, Deployment
Protection, Vercel Authentication, **Standard Protection** (so previews).

**Efeito** Os URLs longos de preview passam a exigir sessao Vercel. O endereco
canonico continua aberto: `sintonia-eame-preview.vercel.app` e producao, e a
Standard Protection nao lhe toca.

    PREVIEW URL != USER URL. E proteger um nao pode fechar o outro.

**PRE-REQUISITO, e nao e opcional.** Medido: `system-map-deploy-verify.yml`
chama `system-map/scripts/verificar_deploy.py`, que faz um pedido ANONIMO ao
URL de preview do commit para ler `system-map/deployment.generated.json`. Com a
autenticacao ligada, esse pedido passa a receber a pagina de login e o portao
do System Map fica vermelho em todos os ramos.

Entao, pela ordem: gerar um **Protection Bypass for Automation** (Settings,
Deployment Protection), guarda-lo como segredo do repositorio, ensinar
`verificar_deploy.py` a enviar o cabecalho `x-vercel-protection-bypass`, provar
que o portao volta a verde — e so depois ligar a proteccao.

    NAO SE LIGA UMA PROTECCAO E DEPOIS SE DESCOBRE QUEM ELA PARTIU.

**Desfazer** Desligar Vercel Authentication. Efeito imediato.

**Custo** Incluido no plano Pro actual.

---

## 2 · Proteger os ramos que sao autoridade

**Onde** GitHub, Settings, Rules, Rulesets, New branch ruleset.

**Medido hoje** `/rulesets` devolve `[]`. Zero de 85 ramos protegidos.

**Alvo** `main` primeiro. Nao os 85: a maior parte sao linhas de trabalho, e
proteger tudo pararia o fluxo em que o Claude escreve em ramos.

    DEFAULT BRANCH != CURRENT PRODUCT AUTHORITY, e por isso o alvo mede-se
    antes de se aplicar. Hoje o `main` nao e a linha mais avancada.

**Regras minimas** Bloquear force push. Bloquear apagar o ramo. Exigir um PR.

**Sobre exigir verificacoes:** so depois de o SECURITY CHECK ter corrido em
`main` pelo menos uma vez, para que o nome exista na lista. Exigir uma
verificacao que nunca correu naquele ramo bloqueia todos os PR para sempre.

    NAO SE EXIGE UM CHECK QUE AINDA NAO EXISTE NAQUELE RAMO.

O nome a escolher e exactamente `security`.

**Desfazer** Apagar o ruleset.

---

## 3 · Confirmar as tres proteccoes gratuitas do GitHub

**Onde** GitHub, Settings, Code security.

**Medido hoje** Desconhecido. As tres APIs respondem 403 atraves do proxy desta
sessao, e um 403 nao diz se a funcionalidade esta ligada — diz que nao posso
perguntar.

    AVAILABLE != ENABLED. E NAO POSSO PERGUNTAR != ESTA DESLIGADO.

**Ligar, se estiverem desligadas** — as tres sao gratuitas em repositorio
publico:
- **Secret scanning** e **Push protection**. A push protection e a que interessa
  mais: torna continua a prova que hoje e pontual. A varredura diz que nao
  detectou nada em 9.809 blobs; a push protection impede o proximo.
- **CodeQL, Default Setup.** As linguagens reais sao JavaScript e Python.
  Nao criei workflow de Advanced Setup de proposito: se o Default Setup ja
  estiver ligado, dois donos analisariam o mesmo codigo e reportariam em
  duplicado.

      ONE CODEQL OWNER.

**Desfazer** Desligar no mesmo ecra.

---

## 4 · Onde ficam os backups

**Onde** Supabase, Settings, Database, Backups.

**Medido hoje** Nada. A API de gestao do Supabase nao e alcancavel daqui, e
nao ha numeros a inventar: retencao, PITR e RPO ficam `UNKNOWN` ate alguem
abrir esse ecra.

**O que anotar** Ha backup automatico? Qual retencao? PITR esta disponivel no
plano? Basta escrever a resposta em `security-baseline.json`, em SEC-015.

**E depois** O Art. 32(1)(c) do GDPR nao pede backup: pede capacidade de
**restaurar**. Um backup que nunca foi restaurado e uma hipotese. Um restauro
para uma base descartavel, uma vez, datado, transforma SEC-015 de UNKNOWN em
PROVED — e e a diferenca entre dizer e mostrar quando a TI da ADAMA perguntar.

    BACKUP CONFIGURADO != RESTAURO PROVADO.
