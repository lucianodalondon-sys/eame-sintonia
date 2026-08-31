// Camada B · UI CHROME I18N
//
// Duas camadas independentes de idioma convivem no portal:
//
//   A · CONTENT  — representacoes de objeto e evidencia (H9). Tem fallback,
//       porque uma traducao que nao existe nao pode ser inventada.
//   B · CHROME   — menu, titulo de pagina, rotulo, botao, filtro. Vocabulario
//       fixo da interface: aqui NAO ha fallback, tem que estar completo.
//
// O casco canonico nao carrega marcacao de i18n e nao vai carregar: quem
// traduz e o runtime derivado, trocando o texto ja renderizado. A chave e o
// proprio texto em portugues, entao nenhuma tag nova entra no HTML.
//
// LEI: rotulo de tela nao e valor canonico. ATTENTION_READY continua
// ATTENTION_READY no dado, no ID e na evidencia — so a etiqueta lida muda.

import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
export const LANGS = ['pt', 'en', 'es', 'fr', 'it']

export function loadDict() {
  return JSON.parse(readFileSync(join(HERE, 'ui-translations.json'), 'utf8'))
}

/** Falha o build se faltar chave em qualquer idioma. */
export function auditDict(dict) {
  const keys = Object.keys(dict.keys)
  const missing = { pt: [], en: [], es: [], fr: [], it: [] }
  for (const k of keys) {
    const e = dict.keys[k]
    if (!k || !k.trim()) missing.pt.push(k)
    for (const l of ['en', 'es', 'fr', 'it']) {
      if (!e[l] || !String(e[l]).trim()) missing[l].push(k)
    }
  }
  const required = dict._REQUIRED || []
  const faltamObrigatorias = required.filter(r => !(r in dict.keys))
  return { total: keys.length, missing, faltamObrigatorias }
}

/** Gera o script de runtime que aplica o vocabulario na arvore renderizada. */
export function emitRuntime(dict) {
  const table = {}
  for (const l of ['en', 'es', 'fr', 'it']) {
    table[l] = {}
    for (const [k, v] of Object.entries(dict.keys)) table[l][k] = v[l]
  }
  return `
// ── UI CHROME I18N (camada B) ──────────────────────────────────────────────
(function () {
  var T = ${JSON.stringify(table)};
  var LANGS = ${JSON.stringify(LANGS)};
  var KEY = 'sintonia.ui.lang';
  var cur = 'pt';

  // Idioma preservado entre recargas — preferencia de apresentacao.
  window.__INIT_LANG__ = function () {
    try { var v = localStorage.getItem(KEY); if (v && LANGS.indexOf(v) >= 0) return v; } catch (e) {}
    return 'pt';
  };

  // O texto original em portugues fica guardado no proprio no. Assim trocar
  // de idioma varias vezes nunca traduz em cima de traducao.
  function original(node) {
    if (node.__pt == null) node.__pt = node.nodeValue;
    return node.__pt;
  }

  function apply(root) {
    if (cur === 'pt') {
      walk(root, function (n) { if (n.__pt != null) n.nodeValue = n.__pt; });
      return;
    }
    var tbl = T[cur] || {};
    walk(root, function (n) {
      var pt = original(n);
      var trimmed = pt.trim();
      if (!trimmed) return;
      var hit = tbl[trimmed];
      if (hit == null && trimmed.indexOf(' · ') > 0) {
        // Muitos rotulos do casco sao compostos ("MAQUINA DE ATENCAO · ITALIA").
        // Traduz peca por peca; se nenhuma peca for conhecida, deixa como esta.
        var parts = trimmed.split(' · '), any = false;
        var out = parts.map(function (p) {
          var t = tbl[p]; if (t != null) { any = true; return t; } return p;
        });
        if (any) hit = out.join(' · ');
      }
      if (hit != null) n.nodeValue = pt.replace(trimmed, hit);
    });
  }

  function walk(root, fn) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentNode;
        if (!p) return NodeFilter.FILTER_REJECT;
        var tag = p.nodeName;
        if (tag === 'SCRIPT' || tag === 'STYLE') return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n, list = [];
    while ((n = w.nextNode())) list.push(n);
    for (var i = 0; i < list.length; i++) fn(list[i]);
  }

  // O casco redesenha a arvore a cada mudanca de estado. O observer garante
  // que o vocabulario seja reaplicado no que acabou de nascer.
  var pending = null;
  function schedule() {
    if (pending) return;
    pending = requestAnimationFrame(function () { pending = null; apply(document.body); });
  }

  window.__UI_LANG__ = function (l) {
    cur = LANGS.indexOf(l) >= 0 ? l : 'pt';
    try { localStorage.setItem(KEY, cur); } catch (e) {}
    document.documentElement.lang = cur;
    apply(document.body);
  };
  window.__UI_LANG_CURRENT__ = function () { return cur; };
  window.__UI_LANG_TABLE__ = T;

  document.addEventListener('DOMContentLoaded', function () {
    cur = window.__INIT_LANG__();
    document.documentElement.lang = cur;
    apply(document.body);
    new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true, characterData: true });
  });
})();
`
}
