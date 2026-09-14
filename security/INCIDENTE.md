# INCIDENTE — uma pagina, e executavel

Nao ha manual. Ha cinco casos, e cada um comeca pelo que CONTEM o dano, nao
pelo que o explica.

    PRIMEIRO FECHA-SE A PORTA. DEPOIS ESCREVE-SE O RELATORIO.

**Dono do incidente:** Luciano (London Creative). Hoje nao ha mais ninguem, e
dizer que ha seria pior do que dizer que nao ha. Contactos da ADAMA nao entram
aqui: entram quando houver contrato e uma pessoa nomeada do lado deles.

**Antes de tudo:** nao colar o segredo, o token, o DSN ou a linha de dados em
nenhum sitio — nem em chat, nem em issue, nem em commit. O relato diz o TIPO,
o FICHEIRO e o INTERVALO. Nunca o valor.

---

## 1 · Um segredo foi exposto

1. **Rodar primeiro.** Supabase: Settings, API, rodar a chave. GitHub: revogar o
   token na conta que o emitiu. Apify e Google: rodar na consola respectiva.
   Rodar antes de investigar — enquanto se investiga, a chave antiga funciona.
2. Actualizar o segredo em Settings, Secrets and variables, Actions.
3. **Nao apagar o historico como primeiro reflexo.** Reescrever o Git nao
   desfaz o que ja foi clonado, e custa a toda a gente que tem a arvore.

       SECRET REMOVED FROM HEAD != SECRET NEVER EXPOSED.

4. So depois: `python3 guarda/social_guarda.py` para achar a origem, e corrigir
   a origem.

## 2 · Alguma coisa privada ficou publica

1. Medir o que esta la, antes de mexer: `python3 security/superficie_publica.py`.
2. Se e um ficheiro que nao devia ser servido: acrescentar a regra ao
   `.vercelignore` e fazer push. O deploy seguinte deixa de o enviar.
3. **Isso nao apaga o que foi descarregado.** Se era proprietario ou pessoal,
   a exposicao aconteceu e fica registada — a correccao trava o futuro, nao o
   passado.
4. Se e urgente e o conteudo esta em producao: Vercel, Deployments, escolher o
   deployment anterior bom, Promote to Production. Rollback e a unica coisa
   nesta pagina que age em segundos.

## 3 · Acesso nao autorizado a base de dados

1. Medir antes de mudar: correr o workflow `rls-censo-metadados`. Ele diz o que
   `anon` consegue de facto, e nao o que devia conseguir.
2. Conter pelo privilegio, e nao pela RLS: `revoke` a `anon` na tabela em causa
   fecha a porta sem mudar o comportamento de quem entra pela `service_role`.
3. Rodar a chave da API do Supabase (caso 1).
4. **Antes de qualquer `revoke` mais largo, perguntar quem parte.** A Collection
   escreve por `service_role`, que ignora RLS — mas confirmar, nao assumir.

       SECURE BY BREAKING PRODUCTION nao e conter: e trocar de incidente.

## 4 · Commit ou workflow malicioso

1. Nao fazer merge. Nao correr o workflow.
2. Se ja correu num runner self-hosted: desligar o runner da rede antes de
   tudo. Cinco workflows correm na maquina do dono.
3. Rodar todos os segredos do repositorio: um workflow que correu leu-os todos.
4. `git log --all --oneline --since=...` para o alcance, e o SECURITY CHECK
   para saber o que ele deixou para tras.

## 5 · Deploy mau

1. Vercel, Deployments, o ultimo bom, Promote to Production.
2. Depois descobrir porque. A ordem importa: um deploy mau em producao custa
   por minuto, e a causa nao foge.

---

## Preservar a prova

Antes de corrigir, guardar o que prova o que aconteceu: o ID da corrida do
workflow, o SHA do commit, o URL do deployment, a hora. Corrigir apaga o
sintoma; se ninguem guardou o sintoma, ninguem consegue explicar depois o que
houve — nem a nos, nem a TI da ADAMA.

## O que esta pagina nao resolve

Revogar a sessao de um utilizador, porque nao ha sessoes: nao ha autenticacao.
Saber quem leu o que, porque nao ha registo de acesso. As duas coisas chegam
com a S3, e ate la a resposta honesta a «quem entrou?» e: nao sabemos.
