# BUSCA-NO-ACTIONS — a busca do Google pela API oficial, no GitHub Actions

> Missão da coordenação (27/09 11:25), com a resposta do dono (11:28) e o ajuste das 12:20 (secrets medidos: não
> há CX nem chave de CSE; runners locais desligados; + piloto de comentários D106). Ramo `busca-no-actions-v1`, a partir de
> `linha-busca-v1 @ 99eebc26`, que já desce do vivo `2ef6fef8`. **Sem rede e sem ler segredo nenhum**: nenhuma
> chamada ao Google saiu daqui, e o workflow **não correu** (o push é do coordenador, §2). PRONTO-SEM-MAPA: as peças da LINHA-BUSCA (esta
> e a de partida) ainda não têm lugar no mapa, e isso fica para a integração.

## 1 · O que ficou pronto (versão das 12:20 da coordenação)

Uma corrida só, em `ubuntu-latest`, sem VPN, **sem commit**: tudo sai como **artifact**.

| passo | o quê |
|---|---|
| 0 | a guarda de segredos da casa (`guarda/social_guarda.py`) — ver §6 |
| 1 | lê o pedido `ferramentas/linha_busca/PEDIDO-BUSCA-GOOGLE.json`: N, só-diagnóstico, comentários, CX (opcional; é o ID **público** do mecanismo, não é segredo — hoje não existe) |
| 2 · **diagnóstico** | **UMA chamada** à Custom Search JSON API (`--diagnosticar-cse`): a API está ativa? a chave pode usá-la? há CX? → `DIAGNOSTICO.json` com **o que o dono tem de fazer** |
| 3 · busca | só se o diagnóstico disser que dá **e** o pedido não for «só diagnóstico» (hoje é: sem CX não há busca) |
| 4 · **piloto de comentários D106** | `commentThreads.list` nos **10 vídeos pais do §12** (`soP-t7nvvq8, F5uLnId6fJk, w87w51fSWAw, QGE7h4gztQ8, R5FJWJkCbKI, 5MNenAiGtlQ, QmeVN7SNnMU, 2cF0yHZXiMs, ioLYGSazexk, ezRyN8vLVvc`), `order=relevance` **e** `order=time`, `maxResults=100`, `part=snippet,replies`, **1 página** (o `nextPageToken` fica anotado e não se segue). **20 chamadas = 20 unidades** das 10 000 do dia. Cada resposta **crua**, byte a byte, em `comentarios/<video>__<ordem>.json`, e o manifesto `COMENTARIOS-PILOTO-D106.json` com o **sha256** de cada uma, o pedido **sem a chave**, HTTP, itens, respostas, erro (redigido) |
| 5–7 | resumo na página da corrida; **artifact sempre** (`retention-days: 7`); a corrida fica vermelha **se o piloto falhar** (depois de o artifact sair). O diagnóstico sem CX «falha» de propósito: isso **não** pinta a corrida de vermelho, só impede a busca |

**O segredo:**
- É **SÓ `secrets.YOUTUBE_DATA_API_KEY`**, escrito **fixo**, nos passos 2, 3 e 4. Nenhum `SUPABASE_*`.
- Achado: a versão anterior buscava o secret **pelo nome** (`secrets[...]`), e **esse jeito faz o GitHub entregar
  TODOS os secrets do repositório ao runner**, `SUPABASE_*` incluídos. Saiu. Há um teste e duas sabotagens que o
  impedem de voltar.
- A chave nunca é impressa: tesoura (`api_oficial.redigir`) + máscara do Actions. Os testes provam, com uma
  chave falsa, que ela não fica em nenhum ficheiro nem em nenhuma saída.

**Os comentários são dado pessoal.** A resposta crua traz o nome e o canal de quem comentou (é assim que a API
devolve). Por isso:
- o artifact vive 7 dias;
- a **minimização da D106** faz-se na entrada, aqui, pela porta canónica: sem perfil/avatar do comentarista,
  comentário = PUBLIC_ASSERTION e nunca FACT, FACT_LOCATION só do pai.

**Paradas do piloto:**
- Um erro do vídeo (ex.: `commentsDisabled`) fica anotado, e o piloto segue para os outros.
- Um erro da **chave ou do projeto** para as restantes chamadas, para não gastar quota à toa: quota, chave
  inválida, API desligada, chave restrita.

## 2 · Como disparar (coordenador)

O workflow dispara por **push no próprio ramo `busca-no-actions-v1`**, quando mudam o `.yml` ou o pedido
(`workflow_dispatch` exigiria o ficheiro no `main`).

**Eu NÃO fiz o push deste commit:** se o fizesse, a corrida partia sozinha e gastava as chamadas. O ramo no
GitHub continua no commit anterior (`e56b79c7`, que não dispara nada).

```bash
git -C C:/busca push origin busca-no-actions-v1
```

- **Esse push dispara a 1.ª corrida:** 1 chamada de diagnóstico + 20 de comentários; a busca não corre.
- **Depois, baixar o artifact** `linha-busca-google-<run_id>` (`gh run download`). A entrada dos comentários na
  Sala faz-se aqui, pela porta canónica.
- **Para correr de novo:** mudar o pedido (ex.: pôr o CX quando existir, `SO_DIAGNOSTICO: false`), fazer commit
  e push no mesmo ramo.
- ⚠️ **A 1.ª corrida é a prova do workflow no GitHub.** O YAML passou no leitor (PyYAML) e nos testes, mas nunca
  correu lá.

## 3 · O CX é obrigatório?

- **No código da casa: sim.** O motor `GOOGLE_CSE` (`motores.google_cse_pedido`) nem monta o pedido sem chave **e** CX.
- **Na API: o diagnóstico MEDE-O** na 1.ª corrida.
  - Sem CX no pedido (hoje não há), a chamada vai sem `cx`.
  - O Google confere primeiro se a API está ligada e se a chave pode usá-la, e só depois os parâmetros.
  - Então um `400 INVALID_ARGUMENT` quer dizer duas coisas ao mesmo tempo: **a API está ligada, a chave pode, e
    o CX é obrigatório (medido)**.
  - Um `403` diz qual das portas fechou: API desligada, chave restrita a outras APIs, chave inválida, projeto sem
    acesso ou quota.
- **Pela documentação oficial: NÃO SEI.** Sem rede não a li, e não há cópia dela nesta máquina (procurei o
  documento de descrição da API nas bibliotecas instaladas: não existe).

## 4 · «Pesquisar a web inteira» ainda existe para mecanismos novos?

**NÃO SEI — não o consigo provar pela documentação oficial sem rede.**

⚠️ Lembrança minha, **não verificada**, e por isso só como alerta: tenho a ideia de que o Google anunciou,
em 2025, duas coisas:
- a Custom Search JSON API deixaria de aceitar clientes novos;
- a opção de pesquisar a web inteira deixaria de existir para mecanismos novos (ficando só uma lista de sites).

Se for verdade, pode inviabilizar este caminho. Quem confirma é o dono, no painel do mecanismo
(programmablesearchengine.google.com) ou na página oficial da Custom Search JSON API.

O diagnóstico ajuda a ver:
- se o mecanismo funcionar, `ESCOPO_INDICIO` diz de quantos sites vêm 10 resultados para «agricoltura»
  (**indício, não prova**);
- se o projeto não tiver acesso à API, o diagnóstico reconhece a mensagem do Google e diz isso.

## 5 · O que o dono tem de conferir no Google Cloud (no MESMO projeto da `YOUTUBE_DATA_API_KEY`)

1. **Ativar a API:** APIs e serviços › Biblioteca › «Custom Search API» › Ativar.
2. **A chave pode chamá-la?** APIs e serviços › Credenciais › a chave › «Restrições de API». Uma chave feita
   para o YouTube costuma estar limitada à «YouTube Data API v3»: é preciso **acrescentar** a «Custom Search API»
   (ou tirar a restrição).
3. **Restrição de aplicação:** se a chave estiver presa a IP ou a site, o runner do GitHub é barrado, porque os
   IPs dele mudam a cada corrida. Para o Actions, a chave precisa de «Nenhuma» restrição de aplicação.
4. **Criar o mecanismo de busca e o CX:**
   - em programmablesearchengine.google.com, criar um mecanismo, ou abrir um que já exista;
   - ver se a opção «pesquisar a web inteira» aparece (§4);
   - copiar o **ID do mecanismo de pesquisa** (esse é o CX);
   - passá-lo à coordenação, que o põe no campo `CX` de `ferramentas/linha_busca/PEDIDO-BUSCA-GOOGLE.json`
     (o CX não é senha; o único secret usado é a chave).
5. **Quota:** 100 consultas/dia são grátis. Passar disso é pago e exige faturação no projeto: **não ativar sem
   decisão do dono**.

O próprio `DIAGNOSTICO.json` repete, na ordem, só os passos que faltarem.

## 6 · A guarda de segredos travava TODOS os workflows (achado)

Ao correr o passo 0 aqui, a guarda (`guarda/social_guarda.py`) **reprovou o repositório**. Eram **20
ficheiros** do vivo, todos anteriores a esta missão; a guarda mostra o primeiro achado de cada ficheiro:
- **18 com caminho pessoal do Windows.** 3 são código: `ferramentas/big_collection/onda_web.py`,
  `ferramentas/maestro_social/maestro_social.py` e `scripts/regua_t2/prova_d29_porta.py`. Os outros são
  relatórios e saídas de teste guardados como prova.
- **1 JWT**, que é a licença **pública** do widget de acessibilidade accessiweb, dentro de bytes de página de
  prova.
- **1 chave do Google**, que é a chave **pública do Google Maps do cifo.it**, dentro de uma página copiada para
  o teste C2-JUIZ.

Com isso, **nenhum workflow com esse passo 0 passava**, a partir de qualquer ramo que desça do vivo atual.
Nenhum dos 20 é credencial do SINTONIA.

Pus os 20 na `DIVIDA_CONHECIDA` da guarda, que é o mecanismo dela para «achado real, anterior, listado e não
silenciado». Cada um tem o seu porquê, o relatório mostra-os em cada corrida, e **um achado novo continua a
travar**. Resultado:
- a guarda passa (rc=0);
- duas medições da casa que estavam vermelhas no ramo de partida ficaram verdes:
  `test_security_secret_shapes` (a medição) e `test_social_sessao` (RED TEAM 2).

⚠️ **Limite da guarda:** ela perdoa o **ficheiro inteiro**, não a linha. Um segredo que entrasse depois num
destes 20 ficheiros não seria visto. A limpeza de verdade é outra missão:
- nos 3 ficheiros de código, trocar o caminho pessoal pela pasta do utilizador ou por uma variável de ambiente;
- nos relatórios de prova, decidir se se reescrevem ou se ficam.

## 7 · Provas
- `tests/test_busca_no_actions.py`: **37 testes, OK**. O do YAML estrutural corre com PyYAML; com o do
  Python312, passou. Os testes cobrem:
  - a tesoura e os formatos de erro do Google;
  - «uma chamada só» no diagnóstico, e «sem chave, nenhuma chamada»;
  - a linha de comando (quota; `--sem-portao-it` só para API; o portão IT nunca é chamado no Actions);
  - o pedido (N, CX só com forma de ID);
  - o workflow: só `secrets.YOUTUBE_DATA_API_KEY` fixo e só nos passos 2–4; nenhum `SUPABASE`; nenhum
    `secrets[...]`; push só no próprio ramo e nos próprios ficheiros; sem `workflow_dispatch`; sem commit;
    artifact sempre; nenhum `${{ }}` dentro de um `run`;
  - o piloto: os 10 pais e as 2 ordens; 20 chamadas cruas com sha256; `commentsDisabled` não para os outros;
    erro da chave para logo na 1.ª; sem chave, zero chamadas; a chave não fica no manifesto.
- **Mutação: 26 de 26 mortos** (`provas/busca_no_actions/MUTANTES.json`), incluindo «secret pelo nome», «um
  SUPABASE entra», «dispara noutro ramo», «permissão de escrita», «piloto só com uma ordem» e «erro da chave não
  para».
- **Vizinhos:** as mesmas 7 baterias, iguais teste a teste à rodada anterior. Essa já não tinha piorado nada face
  ao ramo de partida (2 melhoraram, §6).

## EM PALAVRAS SIMPLES

**O que fiz.** Deixei pronta uma "receita" no GitHub que, numa só rodada:
1. pergunta **uma vez** ao Google se a busca pela porta oficial está ligada e se temos o "código do mecanismo de
   busca" (CX);
2. pede os comentários dos **10 vídeos** escolhidos para o piloto: 2 vezes cada, por "mais relevantes" e por "mais
   recentes". São **20 pedidos**, do limite de 10 mil por dia;
3. entrega tudo num pacote para baixar, com uma "impressão digital" (sha256) de cada resposta.

Nada é gravado no repositório. A entrada na Sala continua a ser feita aqui, pelo caminho de sempre.

**A chave.** Só a chave do YouTube entra na receita, escrita pelo nome certo. Achei um detalhe perigoso na minha
versão anterior: do jeito que eu pegava a chave, o GitHub entregaria **todas** as senhas do repositório à
máquina da receita, inclusive as do banco de dados. Troquei, e há teste que impede de voltar. A chave nunca
aparece escrita em lugar nenhum.

**Como disparar.** Não enviei esta versão ao GitHub, porque enviar já faria a receita rodar e gastar os
pedidos. O coordenador envia com um comando e depois baixa o pacote.

**O que já se sabe.** Não existe o código do mecanismo (CX), então a busca do Google não vai rodar. O teste de
uma pergunta vai dizer exatamente o que falta. Os comentários não dependem disso: vão rodar.

**Cuidado com privacidade.** As respostas cruas trazem o nome de quem comentou. O pacote se apaga sozinho
em 7 dias, e a limpeza desses dados pessoais acontece na entrada da Sala, como a regra D106 manda.

**Um problema que achei no caminho.** O "detector de senhas" que roda antes de todo robô do GitHub estava
barrando **todos** eles. Ele achava 20 arquivos antigos com coisas que parecem senha, mas não são: o nome da
pasta do usuário deste computador, e duas chaves públicas de sites (um mapa, um botão de acessibilidade).
Anotei os 20 na lista oficial de "já conhecidos", cada um com o motivo. O detector continua barrando qualquer
senha nova. A limpeza de verdade desses 20 fica para outra tarefa.
