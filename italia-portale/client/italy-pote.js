/* CASCO-POTE · o CARREGADOR do pote da Intelligence — este ficheiro NAO tem dados.

   Fluxo unico (D97): SALA -> INTELLIGENCE -> POTE -> CASCO. O pote (POTE_INTELLIGENCE_CASCO/v1) e escrito pela
   Intelligence; o casco so o desenha. Os dados vivem em `italy-pote.local.js`, GERADO por
   audit/casco/pote-casco.mjs, fora do Git (.gitignore) e de qualquer deploy (.vercelignore), porque o pote e
   EXPERIMENTAL · NAO_PARA_CLIENTE com GATE_PARA_CLIENTE = FECHADO.

   So se pede com `?pote=local` no endereco. Sem isso nada e pedido, e cada ferramenta diz que a Intelligence
   da corrida corrente nao foi carregada neste endereco. */
window.SINTONIA_POTE = window.SINTONIA_POTE || null;
(function () {
  try {
    if (/[?&]pote=local(?:&|$)/.test(window.location.search)) {
      document.write('<script src="italy-pote.local.js"><\/script>');
    }
  } catch (e) { /* sem location: fica null */ }
})();
