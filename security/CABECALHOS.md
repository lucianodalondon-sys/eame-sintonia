# CABECALHOS DE SEGURANCA — porque estes, e porque nao os outros

O `vercel.json` e validado contra um esquema fechado: uma chave que a Vercel
nao conhece — `$comment` incluida — faz a build inteira falhar. Tentei explicar
as decisoes dentro do proprio ficheiro e derrubei o deploy da branch.

    UM FICHEIRO DE CONFIGURACAO VALIDADO NAO E UM SITIO PARA EXPLICAR NADA.

O raciocinio vive aqui, e o `vercel.json` fica com a configuracao e mais nada.

CABECALHOS DE SEGURANCA — medidos antes de escritos.

A CSP aqui tem UMA directiva. Isso e de proposito e nao e timidez: uma CSP
so restringe as directivas que nomeia, e por isso `frame-ancestors` sozinha
fecha o embedding sem tocar em scripts, estilos ou imagens.

    UMA CSP COM UMA DIRECTIVA NAO E MEIA CSP. E A DIRECTIVA INTEIRA.

A CSP COMPLETA fica por fazer, e fica por medicao e nao por esquecimento:
accesso.html e casa.html tem <script> inline, todas as paginas tem <style>
inline, o favicon e um data: URI e o vendor traz babel-standalone, que
avalia codigo em tempo de execucao. Um `script-src 'self'` copiado da
internet parte o portal hoje. Fica em SEC-013 com BREAKAGE_RISK=HIGH.

    UM CABECALHO QUE PARTE O PRODUTO E DESLIGADO NO DIA SEGUINTE.

frame-ancestors 'none': medido em 2026-09-09 — zero <iframe>, <embed> e
<object> em todo o portal, e nada no repositorio embebe o portal noutro
sitio. Fechar o embedding nao tira nada a ninguem, e fecha o clickjacking.
X-Frame-Options acompanha para os navegadores que nao leem frame-ancestors.

Permissions-Policy: negado so o que foi medido como NAO usado. O portal usa
navigator.clipboard em portale.html, e por isso a area de transferencia NAO
aparece nesta lista. Negar por reflexo o que o produto usa e como negar por
reflexo o que ele nao usa: nos dois casos ninguem mediu.

O QUE NAO FOI TOCADO, E PORQUE:
Access-Control-Allow-Origin: * vem da plataforma para ficheiros estaticos.
O portal nao faz um unico pedido cross-origin — o unico fetch e para
state.generated.json, na mesma origem. Mas a linha do URL canonico do
System Map esta a trabalhar em paralelo, e fechar o CORS as escuras podia
partir-lhe uma leitura entre dominios que eu nao consigo ver daqui.

    NAO SE FECHA UMA PORTA SEM SABER QUEM ESTA A PASSAR POR ELA.

Strict-Transport-Security ja vem da plataforma, com dois anos e preload —
medido no curl, nao assumido. Nao se repete aqui o que ja e verdade.
