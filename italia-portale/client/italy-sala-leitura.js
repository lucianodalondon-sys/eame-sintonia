/* CASCO-LEITURA (D78) · o CARREGADOR da vista #sala — este ficheiro NAO tem dados.

   Os dados da Sala (com o trecho do texto de cada documento) vivem em `italy-sala-leitura.local.js`,
   GERADO por audit/casco/sala-leitura.mjs a partir de um export so-leitura, e fora do Git
   (.gitignore) e de qualquer deploy (.vercelignore).

   So se pedem com `?sala=local` no endereco. Sem isso nada e pedido: nenhum portao (link-asset percorre
   todas as vistas e reprova um 404) nem nenhum deploy publico pede um ficheiro que nao existe, e a vista
   diz que o export nao foi carregado. */
window.ITALY_SALA_LEITURA = window.ITALY_SALA_LEITURA || null;
(function () {
  try {
    if (/[?&]sala=local(?:&|$)/.test(window.location.search)) {
      document.write('<script src="italy-sala-leitura.local.js"><\/script>');
    }
  } catch (e) { /* sem location: fica null */ }
})();
