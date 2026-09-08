# Procedência destas fixtures

Bytes REAIS da primeira execução operacional do YouTube.

    run          34258433872
    workflow     scrap-social
    ref          claude/scrap-social-na-biblia-v1
    sha          5941fd201dcabfc71c2825479aa7a2a8e1532146
    artefato     10068850407 · youtube-piloto-raw-34258433872

`commentThreads-ezRyN8vLVvc.json` é o corpo devolvido por `commentThreads.list`
para o vídeo `ezRyN8vLVvc` do canal `@viticolturariccardocastaldi`. A thread
`UgxoP_4_qUyfVrsKV6V4AaABAg` declara `totalReplyCount = 1` e entrega **zero**
respostas no envelope.

`comments-UgxoP_4_qUyfVrsKV6V4AaABAg.json` é o corpo devolvido por
`comments.list(parentId=…)` na tentativa de completar essa thread: **HTTP 200
com `items: []`**. A API respondeu, não recusou — e ainda assim trouxe menos do
que ela mesma declarou.

Isto NÃO é `deleted`, `moderated`, `hidden` nem `removed`. Nada disso foi
observado. É uma DISCREPÂNCIA OBSERVADA, e a única coisa honesta a registrar.
