# RELATÓRIO — R2 · ÍNDICE, SITE PENDURADO E ETag

Branch `recollection-prova-v2`, a partir de `recollection-prova-v1` @ `d759a602`, 2026-09-23.
Travas: nenhuma coleta real, nada na Sala, nenhum serviço vivo tocado. Rede real só
na medição dos validadores (VPN IT medida antes de cada site; 1 HEAD por site + robots).
Código de produção alterado: SÓ `coleta/italy_pilot_collect.mjs`, porque a prova do
timeout falhou (544 s por 3 matérias) — causa raiz, na peça existente.

## ENTREGA

```
INDICE                 2.a corrida: índice 1 · matérias conhecidas 0 · nova 1 (só ela)
                       FALSO_NOVO_POR_RUIDO = 0  (data, contador, modified_time, ordem,
                       #fragmento, paginação, feed, css, matéria ligada 2x)
                       REMOVIDA_NAO_APAGADA = YES (bytes com o sha256 do livro, linha intacta,
                       nada escrito sobre ela)
                       LIMITE CONHECIDO: a mesma matéria com outra grafia (sem a barra final)
                       custa 1 pedido e 0 documentos novos; 0 casos nos 4 livros reais
TIMEOUT                estado: FAILED com motivo («timed out», curl 28), no livro, sem DOCUMENT_ID
                       retoma: YES — a que falhou e as adiadas são colhidas quando o site volta
                       tempo máximo por fonte: era 180 s × matérias (544 s medidos com 3;
                       ~90 min com 30); agora ~180 s (183 s medidos) — 1 pedido pendurado
                       ⚠️ só o timeout dispara; um site lento que responde continua a custar
                       o tempo de cada resposta
ETAG                   ETag 0/8 · Last-Modified 3/8 (1 deles é a hora do pedido → útil ≤ 2/8)
                       ganho estimado: ≤ 2 corpos de índice por corrida (Chianti ≈ 119 KB)
                       proposta: NÃO implementar. O custo real é a revalidação MUTABLE
                       (até 44 corpos por corrida: Zootecnica 14 + Riunite 30), e as 2 MUTABLE
                       não mandam validador. Alavanca proposta, não aplicada: TTL_SECONDS
                       a limitar a revalidação MUTABLE (decisão do dono)
TESTS                  recollection_indice_local 13/0 · recollection_timeout_local 8/0 ·
                       recollection_http_local 15/0 · paridade_duas_rodadas 13/0 ·
                       incrementalidade_test 26/0 · recollection_test 31/0 · paridade_test 32/0 ·
                       motor_de_rota_test 47/0 · italy_contract_test 349/76 — os MESMOS 76
                       vermelhos sem a mudança (comparados por nome)
MUTATION               5/5 mortos, execução provada por marca (MI1 salto, MI2 livro
                       sobrescrito, MI3 dedup do índice, MT1 disjuntor, MT2 adiada no livro)
FINAL_HEAD = REMOTE_HEAD   conferido após o push (hash na mensagem de entrega)
SYSTEM_MAP_CHECK       ver a mensagem de entrega (cadeia REGERAR + VALIDAR sobre o estado final)
```

## Erros meus, corrigidos antes da entrega

1. O mutante MI3 sobreviveu na 1.ª versão: o meu índice de teste nunca ligava a mesma
   matéria duas vezes, e os sites reais ligam (foto e título). Corrigido o teste.
2. A 1.ª medição de robots deu a Agrofarma como barrada. O leitor do Python bate à porta
   com outro nome; pelo curl, com o nome do coletor, o robots é 404 (tudo permitido).
   Corrigido o instrumento; a Agrofarma recebeu 3 leituras de robots e 1 HEAD.

## O que NÃO se provou

- Validadores nas páginas de MATÉRIA (só o índice foi medido: 1 pedido por site).
- 304 real: sem pedido condicional (o briefing dá 1 pedido por site).
- Site lento que responde (só o pendurado).
- Arpae (IT-T2-051) não tem contrato nesta linha: entra no cutover pelo pacote G1; o
  endereço medido é o da rota provada da M3.

Detalhe completo: secção RECOLLECTION-R2 do `SINTONIA-EAME-KNOW-HOW.md`.
