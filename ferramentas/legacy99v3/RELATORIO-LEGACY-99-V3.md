# LEGACY-99 v3 — a rota VIDEO (D53) e o plano de instalação de A+C+D+VIDEO

Ramo `legacy-99-v3`, a partir de `legacy-99-v2` @ 6e51f88b, **com `janela-formas-v1` (d0093df0) junta** (commit 72505cd2), para a VIDEO entrar no **mesmo desenho** da rota PDF/PÁGINA-BOLETIM (D42). **Não instalado.**

## Em palavras simples

- **A régua do Curator ganhou a forma VIDEO.** Um vídeo do YouTube passa se estiverem provadas **as 4 coisas** da D53:
  1. a página pública do vídeo abre;
  2. tem título;
  3. tem data de publicação;
  4. é do canal certo.

  **Falta uma, não passa.** A transcrição **não é exigida e nunca se inventa**: só entra se o Scrap a trouxer. As três horas ficam separadas: quando o vídeo foi publicado, quando aconteceu o facto (desconhecido) e quando o vimos.
- **Resultado nas 41 fontes YouTube antigas:**
  - **com as páginas já guardadas (sem rede), 39 passariam**. As 2 que não passariam tinham guardada uma página vazia (título « - YouTube», sem data nem canal);
  - **com o canário real em 2 canais**, um por corrida e 3 pedidos cada: **os 2 passam e ficam elegíveis**, incluindo um dos 2 «vazios» (IT-T5-037), que hoje tem um vídeo normal;
  - **por isso, o esperado é até 41 de 41.** ⚠️ Só 2 foram medidos hoje com rede; os outros 39 são uma estimativa sobre páginas de 20/09.
- Somado ao bloco A da v2 (**11 HTML elegíveis**), a LEGACY-99 pode levar **até ~52 fontes antigas de volta ao portão**, sem baixar régua nenhuma.

## Um desenho só (a coordenação com a JANELA-FORMAS)

A D42 (JANELA-FORMAS) criou o padrão:
- a forma é **explícita** no contrato (`FORMA`);
- cada forma tem uma **régua irmã** em `ready_split.passos_da_promocao`;
- o portão aceita qualquer régua de `REGUAS_CORRENTES`;
- o vocabulário vive em `validar_contratos` (`FORMAS`, `OUTPUTS`).

A VIDEO entrou exactamente aí:

| Onde (dono) | O que a VIDEO acrescenta |
|---|---|
| `curadoria/validar_contratos.py` | `OUTPUTS` + `VIDEO`; `FORMAS` + `VIDEO`; `form_resolved`: VIDEO exige o canal (`CUSTOM_ADAPTER CANAL_PUBLICO_YOUTUBE_V1`, `CHANNEL_ID UC…`), saída `VIDEO` e identidade pelo vídeo |
| `curadoria/ready_split.py` | `REGUA_VIDEO = "VIDEO/v1"` em `REGUAS_CORRENTES`; `_passos_video` (as 4 provas + saída VIDEO + contrato atual; `INFO` com PUBLICATION_TIME / FACT_TIME=UNKNOWN / COLLECTION_TIME / TRANSCRICAO) |
| `curadoria/canario.py` | `canario_video`: a aba /videos do canal e **um** vídeo (2 pedidos, sem transcrição); `retrato_do_video` lê título, data e canal da página |
| `curadoria/worker.py` | o despacho: `FORMA == VIDEO` → `canario_video` (ao lado de `PAGINA_E_BOLETIM`) |
| `curadoria/importar_do_coletor.py`, `escrever_contratos.py` | o canal importado e o molde novo declaram `FORMA: VIDEO` e `OUTPUT_TYPE: VIDEO`. A rota continua **byte a byte** a do coletor; o `HTML` da tabela do coletor fica escrito na proveniência (`OUTPUT_TYPE_NO_COLETOR`) |

**Conflitos da junção, resolvidos:**
- **`canario.hrefs_da_entrada`:** os dois ramos tinham consertado o mesmo link malformado («[»), cada um à sua maneira. Ficou uma guarda só (`urljoin` + validação de host e porta).
- **`worker`:** o endereço da rota tem um dono (`canario.url_da_rota`, que passou a saber o `URL` da rota fixa da D42).
- **Os ficheiros gerados do mapa** ficam para a cadeia, quando a LOCK-PRIORIDADE sair.

## Provas

- **Testes da VIDEO:** `tests/test_rota_video.py`, **17 testes**. ⚠️ A mensagem do commit cf41e603 diz «22»; contei mal, são 17. Dois deles percorrem cada uma das 4 provas em sub-casos. Cobrem:
  - falta cada prova = reprova;
  - HTTP ≠ 200 reprova;
  - saída VIDEO explícita;
  - tempos separados;
  - transcrição não exigida nem inventada;
  - validador;
  - canário (2 pedidos, nenhum de transcrição; sem data não inventa data; 429; canal vazio pára antes do 2.º pedido);
  - despacho do worker.
- **Todos os testes dos dois ramos juntos:** 121 OK. Os 68 do motor de rota (Node) também OK.
- **Mutação VIDEO: 14/14 mortos**, 0 a escrever em livros (`MUTACAO-VIDEO.json`).
- **Regressão:** 35 módulos (os 31 da v2 + os 4 da JANELA-FORMAS). **493 testes, 2 falhas, as mesmas 2 na base** (a junção antes da VIDEO): `onda_web.py` por declarar e o censo dos livros reais. **0 novas.** Os livros ficaram iguais.
- **Ensaio** (cópia do vivo **df0865e6** + este código; sha256 em `ENSAIO-copia-livros.sha256`):
  - importar as 41 YouTube sem rede: **41 com FORMA/OUTPUT VIDEO, 41 em CANARY_PENDING, 0 READY**;
  - `video_com_o_guardado.py` (sem rede; Sala só leitura, sha256 de cada ficheiro conferido): **39 PASSARIA, 2 NAO_PASSARIA** (páginas guardadas vazias);
  - canário real, 1 canal por corrida: IT-T10-017 e IT-T5-037 → **VIDEO/v1, READY_CURRENT e elegíveis**, 3 pedidos cada.

## PLANO DE INSTALAÇÃO — A + C + D + VIDEO (quem instala é o coordenador; um escritor; bot quieto)

**0 · Antes**
- Corte: `curadoria/italy_contracts_curator.json`, `curadoria/LIFECYCLE-*.json` e `regras/italy_contracts_onboarded.json`, com sha256.
- VPN IT: portão de consenso PASS.

**1 · Código.** Este ramo leva **legacy-99-v1 → v2 → v3 + janela-formas-v1**. Se a PACOTE-ONDA3 já juntar a JANELA-FORMAS, juntar este ramo por cima, porque os conflitos de `canario.py` e `worker.py` já estão resolvidos aqui:
```
git fetch origin legacy-99-v3
git merge --no-ff origin/legacy-99-v3
```
Reiniciar o supervisor liga o **C** (re-check das READY_LEGACY HTML, 10 por 24 h, 1 por domínio). `--sem-revalidar-legacy` desliga-o. O **D** (links com colchetes) é só código.

**2 · A — as 21 HTML, em 2 lotes** (1 fonte por domínio por lote; as listas estão em `LOTES-DE-INSTALACAO.json`, tiradas das rodadas do ensaio):
```
py curadoria/importar_do_coletor.py                                  # conferir: as 21 aparecem como SEM_CONTRATO_NO_CURATOR
py curadoria/importar_do_coletor.py --aplicar --ids=<LOTE A1: 19 fontes>
#   esperar: nenhuma do lote em CANARY_PENDING  (py curadoria/collection_gate.py --ids=<lote>)
py curadoria/importar_do_coletor.py --aplicar --ids=<LOTE A2: 2 fontes>
```
Esperado, pelo ensaio: ~11 elegíveis.

**3 · VIDEO — as 41 YouTube, 1 canal por lote** (D38: YouTube é uma plataforma, 5 pedidos por corrida; cada canal gasta 3):
```
py curadoria/importar_do_coletor.py --aplicar --ids=<1 canal>
#   esperar: o canal fora de CANARY_PENDING e >= 60 s; depois o seguinte (41 lotes)
```
Esperado: até 41 elegíveis (39 pela estimativa sobre o guardado + 2 medidos).

**Desfazer**
- **A/VIDEO:** repor `italy_contracts_curator.json` do corte. As fontes voltam ao estado anterior por uma transição nova (o livro é append-only).
- **Código:** `git reset --keep <sha de antes>` e reiniciar o supervisor.
- **C:** `--sem-revalidar-legacy`.

**Aviso à PACOTE-ONDA3:** escrito em `auditoria-madrugada/aviso-legacy-99-v3-para-pacote-onda3.txt` (juntar A/C/D e, se a D53 entrar na onda, VIDEO).

## O que isto não prova

- Que os vídeos dão SIM na Admissão. É prova de rota e de identidade do vídeo, não de régua de universo; os T8 continuam sem régua.
- Que os 39 estimados passam hoje. As páginas são de 20/09, e 2 delas estavam vazias.
- A coleta de YouTube continua na onda social (D35.4). Isto só faz as fontes passarem no portão do Curator.
