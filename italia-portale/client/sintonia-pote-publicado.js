/* D126 · PORTAL-PUBLICA-SOZINHO — o LUGAR do pote PUBLICADO. Este ficheiro, no Git, NAO tem dados.

   O pote de uma corrida da Intelligence nunca entra no Git (sintonia-pote.js esta no .gitignore e no
   .vercelignore: tem dado real). Quem o leva ao ar e o publicador (portoes/publicar_portal_sozinho.py):
   confere o pote, monta uma copia da arvore, ESCREVE AQUI o envelope conferido — so nessa copia, nunca
   no repositorio —, corre todas as conferencias e so entao implanta.

       window.SINTONIA_POTE_PUBLICADO = { CONTRATO, POTE_SHA256, INTELLIGENCE_RUN_ID, PROMOCAO, ..., POTE }

   Sem publicacao (um deploy feito pela integracao Git, por exemplo), este ficheiro diz `null` e o casco
   fica exatamente como estava. Com o envelope, sintonia-pote-casco.js le o POTE dele como leria o
   `?pote=local`: cada ferramenta desenha so o seu compartimento, e o legado apaga-se. */
window.SINTONIA_POTE_PUBLICADO = window.SINTONIA_POTE_PUBLICADO || null;
