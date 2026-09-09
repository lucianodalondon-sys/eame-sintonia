# SINTONIA · THREAT MODEL (S0)

Medido em 2026-09-09 sobre `baaddcf1`. Cada linha diz o que o actor **alcanca
hoje**, nao o que alcancaria num sistema imaginado.

| Actor | O que alcanca hoje | O que quer | O que temos de impedir | O que nao conseguimos impedir |
|---|---|---|---|---|
| **Anonimo na internet** | Portal inteiro; 11,2 MB de corpus canonico; 197 MB de repo; todos os previews; System Map | curiosidade, indexacao | acesso a dados de cliente e a escrita | que leia o que decidimos publicar |
| **Concorrente** | O mesmo — mais o registo de 3.352 URLs de fonte, as formulas de derivacao e o mapa de 145 componentes | replicar o metodo | exposicao do motor, das regras e do acervo | que copie uma resposta que ja viu |
| **Funcionario ADAMA autorizado** | Tudo (nao ha autorizacao) | fazer o trabalho | acesso a paises e papeis que nao lhe pertencem | que leia o que tem direito a ler |
| **Autorizado mas curioso** | Tudo | ver mais do que precisa | travessia entre paises e exportacao em massa | que veja bem o seu proprio scope |
| **Conta ADAMA comprometida** | Tudo | dados | scope alargado; ausencia de revogacao e de log | o primeiro acesso antes da deteccao |
| **Programador SINTONIA** | Tudo, incluindo push directo em qualquer das 85 branches | trabalhar | push nao revisto para linhas criticas; introducao de exposicao nova | erro honesto — por isso o gate e automatico |
| **Conta de programador comprometida** | Tudo + 5 workflows em runner self-hosted Windows via `workflow_dispatch` | execucao na maquina do dono | dispatch nao autorizado; ausencia de branch protection | acesso com credencial valida antes da revogacao |
| **CI/CD comprometido** | `contents: write` em 5 workflows | escrever no repo | `pull_request_target`; `write-all`; actions de terceiros | comprometimento a montante do GitHub |
| **Dependencia maliciosa** | Superficie quase nula: 0 dependencias npm em runtime, vendor commitado, 0 CDN | execucao no cliente | reintroducao de CDN ou de dependencia nao fixada | um vendor ja commitado estar comprometido a montante |
| **Token vazado** | Nada encontrado: 0 segredos reais em 9.809 blobs | credenciais | novo segredo commitado (push protection) | um segredo que vaze fora do Git |
| **Scraper automatizado** | 30 MB por deployment, sem rate limit, sem WAF | copiar o corpus | descarga em massa nao autenticada | copia de um ecra legitimamente visto |

## Red team — o que foi executado

Provas seguras, so contra a nossa propria superficie. Nada da ADAMA, nada de
terceiros, nada destrutivo.

| Vector | Resultado |
|---|---|
| Visitante anonimo em producao | **ALCANCA** — 11.198.842 bytes de corpus, HTTP 200 |
| Descoberta de preview | **ALCANCA** — Deployment Protection desligada; System Map e `italy-v21.js` em 200 |
| URL directo, sem passar pelo ecra de acesso | **ALCANCA** — `/portale` responde 200 sem nada antes |
| Utilizador de pais errado | **N/A** — nao existe conceito de pais |
| Sessao roubada / token repetido | **N/A** — nao existe sessao |
| Fuga de source map do nosso codigo | **NAO** — 0 `.map` proprios publicados |
| `service_role` no cliente | **NAO** — 0 ocorrencias em `italia-portale/client` |
| Acervo bruto no output publico | **NAO** — `/supabase/...`, `/package.json`, `/.vercelignore` em 404 |
| Segredo na historia do Git | **NAO** — 9.809 blobs, 0 reais |
| PR malicioso a alcancar runner self-hosted | **NAO** — 0 `pull_request_target`; self-hosted so em `workflow_dispatch` |
| CORS aberto | **PARCIAL** — `access-control-allow-origin: *` em conteudo estatico ja publico |
| Clickjacking | **ALCANCA** — sem `frame-ancestors` nem `X-Frame-Options` |
| XSS no DOM | **NAO ALCANCADO** — `innerHTML` existe, mas nao ha input controlado por terceiros: sem API, sem leitura de parametros de URL para o DOM |
| IDOR / BOLA | **N/A** — nao ha objectos por identidade |
| Enumeracao em massa | **ALCANCA** — sem rate limit e sem autenticacao |
| Escrita anonima na base de dados | **NAO MEDIDO** — 12 tabelas sem RLS; medicao live proibida nesta missao. Unico candidato a P0. |

## A licao que o modelo devolve

Quase tudo o que um atacante quer, hoje, obtem-se **sem atacar nada**: esta
publicado. A prioridade nao e endurecer o portal contra intrusao. E mover a
fronteira, para que o que esta do lado de fora seja a resposta, e nao o motor.
