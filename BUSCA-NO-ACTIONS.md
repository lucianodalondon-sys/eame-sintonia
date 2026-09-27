# BUSCA-NO-ACTIONS — a busca do Google pela API oficial, no GitHub Actions

> Missão da coordenação (27/09 11:25), com a resposta do dono (11:28). Ramo `busca-no-actions-v1`, a partir de
> `linha-busca-v1 @ 99eebc26`, que já desce do vivo `2ef6fef8`. **Sem rede e sem ler segredo nenhum**: nenhuma
> chamada ao Google saiu daqui, e o workflow **não correu**. PRONTO-SEM-MAPA: as peças da LINHA-BUSCA (esta
> e a de partida) ainda não têm lugar no mapa, e isso fica para a integração.

## 1 · O que ficou pronto

| peça | o quê |
|---|---|
| `.github/workflows/linha-busca-google.yml` | `workflow_dispatch` (inputs) **ou** push do pedido no ramo de disparo; `ubuntu-latest`, **sem VPN**; `permissions: contents: read` |
| passo 0 | a guarda de segredos da casa (`guarda/social_guarda.py`) |
| passo 1 | lê o pedido: os **NOMES** dos secrets (por omissão `YOUTUBE_DATA_API_KEY` e `GOOGLE_CSE_CX`), N, «só diagnóstico». Um nome que não seja `MAIÚSCULAS_E_ALGARISMOS` é recusado: não entra texto livre em `secrets[...]` |
| passo 2 · **diagnóstico** | **UMA chamada** à Custom Search JSON API (`--diagnosticar-cse`). Diz: a API está ativa no projeto? a chave pode usá-la? há CX? e, se funcionar, de quantos sites vêm 10 resultados. Grava `DIAGNOSTICO.json` com **o que o dono tem de fazer**, em palavras simples |
| passo 3 · busca | só se o diagnóstico disser que dá **e** o pedido não for «só diagnóstico»: `--buscar --motor=GOOGLE_CSE --n=N` sobre as 473 consultas de `data/derivados/LINHA-BUSCA/CONSULTAS.json` |
| passos 4–6 | resumo na página da corrida; artifact `DIAGNOSTICO.json` + `RESULTADOS.json` + `serp/` **sempre**; a corrida fica vermelha se a busca não é possível (depois de o artifact sair) |
| `ferramentas/linha_busca/api_oficial.py` | o pedido às APIs oficiais **sem robots** (D91: API pública oficial documentada segue os próprios termos) e **sem o teto de 5/domínio das páginas**. Quem manda é a **quota: 100 consultas/dia** (`--n` fora de 1..100 é recusado). E a **tesoura**: a chave e o CX saem de qualquer texto antes de ele ser gravado |
| `coleta/linha_busca.py` | `--diagnosticar-cse`; e `--sem-portao-it`, que **só** vale para o diagnóstico e para `--buscar` com motor de API oficial. `--colher`, `--medir-motores` e os motores HTML recusam-no. **As páginas continuam a ser colhidas nesta máquina, com a VPN IT, pelo `--colher`** |

**A chave nunca é impressa.**
- Entra só nos passos 2 e 3, pelo ambiente.
- Todo erro passa pela tesoura, e o Actions esconde os segredos no log.
- Os testes provam, com uma chave falsa, que ela não aparece em nenhum ficheiro nem em nenhuma saída.

⚠️ As respostas cruas do Google (`serp/`) repetem o **CX**, porque o Google o devolve em `queries.request`. O CX
não é uma senha: sem a chave, não serve para nada.

## 2 · Como disparar (coordenador)

Desta máquina o `gh` não tem sessão, então dispara-se por **push do pedido para o ramo de disparo**.
**Nenhum ramo de código dispara**: entregar ou integrar esta linha não gasta quota nem usa a chave. Há um
teste que o impede.

```bash
# a partir de uma copia do ramo busca-no-actions-v1 (o pedido ja vem em «so diagnostico», N=4)
git push origin HEAD:disparo-linha-busca-google
```

- **1.ª corrida: só o diagnóstico (1 chamada).** Ler o `DIAGNOSTICO.json` no artifact, ou o resumo da corrida.
- **Para buscar:**
  - editar `ferramentas/linha_busca/PEDIDO-BUSCA-GOOGLE.json` (`"SO_DIAGNOSTICO": false`, `"N": 4`);
  - fazer commit e push para o mesmo ramo de disparo;
  - depois baixar o `RESULTADOS.json` do artifact e colher as páginas aqui, com a VPN IT:
    `py coleta/linha_busca.py --colher --autorizado --resultados=RESULTADOS.json --fila=<fila> --saida=<pasta>`.
- ⚠️ **Precisa do workflow no GitHub:** o push do ramo de disparo só corre o workflow se o ficheiro já estiver
  nesse commit. É o caso quando o ramo de disparo sai deste ramo.
- ⚠️ **Não testado no GitHub:** não usei a sintaxe `secrets[steps.pedido.outputs.x]` (acesso ao secret pelo nome)
  em nenhuma corrida real. O YAML foi validado pelo leitor (PyYAML) e pelos testes; **a 1.ª corrida é a prova**.

## 3 · O CX é obrigatório?

- **No código da casa: sim.** O motor `GOOGLE_CSE` (`motores.google_cse_pedido`) nem monta o pedido sem chave **e** CX.
- **Na API: o diagnóstico MEDE-O** na 1.ª corrida.
  - Sem o secret do CX, a chamada vai sem `cx`.
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
   - gravá-lo no GitHub em Settings › Secrets and variables › Actions › `GOOGLE_CSE_CX`.
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
- `tests/test_busca_no_actions.py`: **29 testes, OK**. O teste do YAML estrutural corre quando há PyYAML;
  com o PyYAML do Python312, passou.
  - Cobrem: a tesoura; os 9 formatos de resposta do Google; «uma chamada só»; «sem chave, nenhuma chamada»;
    a linha de comando (quota, `--sem-portao-it` só para API, a API nunca pelo transporte das páginas, o portão
    IT nunca chamado no Actions); o pedido (nomes recusados, N, `GITHUB_*`); e o workflow (segredo só nos passos
    2 e 3, nenhum input direto num `run`, artifact sempre, só o ramo de disparo corre).
- **Mutação: 17 de 17 mortos** (`provas/busca_no_actions/MUTANTES.json`). Cada regra nova foi estragada de
  propósito, e algum teste acusou.
- **Vizinhos:** 7 baterias, no ramo de partida e neste.
  - `test_linha_busca` OK nos dois.
  - Os vermelhos restantes (`test_security_secret_shapes` errors=2, `test_social_sessao` failures=1) são
    **iguais** nos dois lados.
  - **Nada piorou**; 2 testes melhoraram (§6).

## EM PALAVRAS SIMPLES

**O que fiz.** Deixei pronta uma "receita" no GitHub que faz buscas no Google pela porta oficial (a API), sem
precisar da VPN italiana. As páginas que a busca encontrar continuam a ser baixadas aqui, com a VPN, como
sempre. A chave do Google usada é a do YouTube, como o dono disse, e ela nunca aparece escrita em lugar
nenhum.

**O primeiro passo é um teste de uma pergunta só.** Antes de gastar a cota de 100 buscas por dia, a receita
faz **uma** chamada ao Google e descobre três coisas: a busca está ligada no projeto? a chave tem permissão? o
"código do mecanismo de busca" (CX) existe? O resultado vem escrito em palavras simples, com a lista do que o
dono precisa fazer.

**O que o dono provavelmente vai ter de fazer.** No Google Cloud, no mesmo projeto da chave do YouTube:
1. ligar a "Custom Search API";
2. deixar a chave usar essa API, porque chaves do YouTube costumam estar travadas só para o YouTube;
3. criar o mecanismo de busca e copiar o código dele (CX) para o GitHub.

Sem o CX não há busca.

**O que eu não sei.** Não sei se o Google ainda deixa um mecanismo novo pesquisar "a web inteira". Tenho a
lembrança, não confirmada, de que isso acabou para mecanismos novos, e de que a própria API deixou de aceitar
clientes novos. Sem internet não consigo confirmar. O dono vê isso no painel do Google, e o teste de uma
pergunta também dá uma pista.

**Um problema que achei no caminho.** O "detector de senhas" que roda antes de todo robô do GitHub estava
barrando **todos** eles. Ele achava 20 arquivos antigos com coisas que parecem senha, mas não são: o nome da
pasta do usuário deste computador, e duas chaves públicas de sites (um mapa, um botão de acessibilidade).
Anotei os 20 na lista oficial de "já conhecidos", cada um com o motivo. O detector volta a funcionar e
continua barrando qualquer senha nova. A limpeza de verdade desses 20 fica para outra tarefa.

**Cuidado que tomei.** Do jeito que estava, a receita teria rodado sozinha quando eu enviasse o trabalho, e
faria a chamada ao Google. Mudei: agora ela só roda quando o coordenador mandar, por um caminho próprio.
