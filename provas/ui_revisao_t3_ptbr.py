#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A INTERFACE DE REVISAO HUMANA DE T3, EM PORTUGUES.

    python3 provas/ui_revisao_t3_ptbr.py            # so mede
    python3 provas/ui_revisao_t3_ptbr.py --escrever

Junta duas coisas que ja existem e NAO inventa nenhuma terceira:

    data/samples/T3-HUMAN-REVIEW-PENDING-V1.json      as 53 fichas, em italiano
    data/samples/T3-DISPLAY-TRANSLATION-PTBR-V1.json  a traducao de leitura

e produz um HTML autocontido que abre com dois cliques no explorador de
ficheiros. Sem servidor, sem npm, sem rede, sem backend.

    AUTO_LABELS_ASSIGNED = 0
    MACHINE_ASSIGNED_GROUND_TRUTH = PROIBIDO

O QUE A PAGINA NAO MOSTRA, E E DE PROPOSITO
--------------------------------------------
    a decisao atual de `PERGUNTAS_DO_UNIVERSO`
    o territorio T2/T3 da ficha da fonte
    quais documentos casaram a varredura que os trouxe ao pacote

Nada disso entra no HTML — nem visivel, nem escondido num `title`, nem no
`data-*` de um elemento. Quem quiser comparar depois abre a seccao
`AUDIT_AFTER_REVIEW` do pacote em markdown.

    HUMAN_LABEL NAO PODE NASCER A OLHAR PARA CURRENT_CLASSIFIER_OUTPUT.

E A TRADUCAO NAO E O DADO
-------------------------
    DISPLAY_TRANSLATION != EVIDENCE

O original italiano viaja dentro da pagina, aparece a um clique, e e ELE que
vai no JSON exportado. A traducao serve para a pessoa entender o texto.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

PENDENTE = "data/samples/T3-HUMAN-REVIEW-PENDING-V1.json"
TRADUCAO = "data/samples/T3-DISPLAY-TRANSLATION-PTBR-V1.json"
HTML = "docs/operacao/T3-HUMAN-REVIEW-PTBR-V1.html"

# Os quatro resultados, e nao ha quinto. O rotulo tecnico e o que ja existe no
# pacote; o texto e so a maneira de o dizer em portugues.
BOTOES = [
    ("T3_SIM", "✅", "SIM", "é sobre praga ou doença"),
    ("T3_NAO", "❌", "NÃO", "é outro assunto"),
    ("T3_AMBIGUO", "⚠️", "AMBÍGUO", "os dois assuntos são importantes"),
    ("EVIDENCIA_INSUFICIENTE", "❓", "NÃO TENHO INFORMAÇÃO SUFICIENTE",
     "o trecho não chega para decidir"),
]
# Campos do pacote e da auditoria que NUNCA entram no HTML.
#
# ⚠️ A primeira versao desta guarda procurava a PALAVRA «TERRITORIO» e acendeu
# num documento cujo proprio titulo de seccao e «VIGILANZA FITOSANITARIA DI
# CARATTERE ISPETTIVO SUL TERRITORIO». Isso e o documento a falar, nao um campo
# a vazar.
#
#     UMA GUARDA QUE NAO DISTINGUE O CAMPO DO CONTEUDO
#     ACENDE NO SITIO ERRADO E ENSINA A IGNORA-LA.
#
# Agora procura a CHAVE, com aspas — que e como um campo apareceria.
PROIBIDOS_NO_HTML = ('"REVIEWER_A"', '"REVIEWER_B"', '"AGREEMENT"',
                     '"FINAL_LABEL"', '"CASOU_A_VARREDURA_DO_CENSO"',
                     '"TERRITORIO_DA_FICHA_DA_FONTE"',
                     '"DECISAO_ATUAL_DA_PORTA_PARA_T3"', '"JA_ESTAVA_NO_PACOTE_DE_46"')


def _json(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return json.load(f)


def dados():
    """O que a pagina leva dentro. So isto, e nada mais."""
    pacote = _json(PENDENTE)
    traducao = {t["DOC_SHA256"]: t for t in _json(TRADUCAO)["TRADUCOES"]}
    fora = []
    for i in pacote["ITENS"]:
        t = traducao[i["DOC_SHA256"]]
        e = i["EVIDENCE"]
        fora.append({
            "DOC_SHA256": i["DOC_SHA256"],
            "ITEM_ID": i["ITEM_ID"],
            "SOURCE_ID": i["SOURCE_ID"],
            "PUBLISHER": i["PUBLISHER"],
            "DOCUMENT_TYPE": i["DOCUMENT_TYPE"],
            "LANGUAGE": i["LANGUAGE"],
            "CANONICAL_PATH": i["CANONICAL_PATH"],
            "BODY_PATH": i["BODY_PATH"],
            # A evidencia canonica — e e esta que sai no JSON exportado.
            "ORIGINAL_EVIDENCE": {
                "TITLE": e["TITLE"], "OPENING": e["OPENING"],
                "SELF_DESCRIPTION": e["SELF_DESCRIPTION"],
                "SECTION_HEADERS": e["SECTION_HEADERS"]},
            # Apoio de leitura. NAO substitui o original.
            "DISPLAY_TRANSLATION_PTBR": {
                "TITLE": t["TITLE"], "OPENING": t["OPENING"],
                "SELF_DESCRIPTION": t["SELF_DESCRIPTION"],
                "SECTION_HEADERS": t["SECTION_HEADERS"]},
        })
    return fora


PAGINA = r"""<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisão T3 — Praga e doença</title>
<style>
:root{
  --tinta:#15201c; --tinta-fraca:#5d6b65; --papel:#f7f6f2; --cartao:#fff;
  --linha:#dfe3df; --acento:#1f6f4a; --sim:#1f6f4a; --nao:#9c2b2b;
  --amb:#9a6a10; --sem:#4a5568; --marca:#eef3ef;
}
*{box-sizing:border-box}
body{margin:0;background:var(--papel);color:var(--tinta);
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  padding-block:0}
.envolve{max-width:820px;margin:0 auto;padding:16px}
header{position:sticky;top:0;background:var(--papel);z-index:5;
  border-bottom:1px solid var(--linha);padding-block:12px}
h1{font-size:17px;margin:0 0 8px;letter-spacing:.02em}
.conta{font-size:14px;color:var(--tinta-fraca);display:flex;
  justify-content:space-between;gap:12px;flex-wrap:wrap}
.barra{height:8px;background:var(--marca);border-radius:99px;margin-top:10px;
  overflow:hidden}
.barra i{display:block;height:100%;background:var(--acento);width:0;
  transition:width .25s}
.aviso{background:#fff8e6;border:1px solid #e8d9a8;border-radius:10px;
  padding:12px 14px;font-size:14px;margin:16px 0}
.cartao{background:var(--cartao);border:1px solid var(--linha);
  border-radius:14px;padding:18px;margin:16px 0}
.proc{font-size:13px;color:var(--tinta-fraca);text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:10px}
h2{font-size:20px;line-height:1.3;margin:0 0 14px}
.trecho{background:#fbfbf9;border:1px solid var(--linha);border-radius:10px;
  padding:14px;white-space:pre-wrap;word-break:break-word;font-size:15px}
.rot{font-size:13px;font-weight:600;color:var(--tinta-fraca);
  text-transform:uppercase;letter-spacing:.05em;margin:18px 0 8px}
ul.sinais{margin:0;padding-left:20px;font-size:15px}
details{margin-top:16px;border-top:1px solid var(--linha);padding-top:12px}
summary{cursor:pointer;font-weight:600;color:var(--acento);font-size:15px;
  padding:6px 0}
.orig{font-size:14px;color:#33403a}
.botoes{display:grid;gap:10px;margin:22px 0 8px}
button.voto{display:flex;align-items:center;gap:12px;width:100%;
  text-align:left;padding:16px 18px;border-radius:12px;border:2px solid var(--linha);
  background:#fff;font:inherit;cursor:pointer;min-height:60px}
button.voto:hover{border-color:var(--acento)}
button.voto .em{font-size:22px;line-height:1}
button.voto b{display:block;font-size:16px}
button.voto span{display:block;font-size:13px;color:var(--tinta-fraca)}
button.voto[aria-pressed="true"]{border-color:var(--acento);
  background:var(--marca)}
button.voto[data-l="T3_SIM"][aria-pressed="true"]{border-color:var(--sim)}
button.voto[data-l="T3_NAO"][aria-pressed="true"]{border-color:var(--nao)}
button.voto[data-l="T3_AMBIGUO"][aria-pressed="true"]{border-color:var(--amb)}
button.voto[data-l="EVIDENCIA_INSUFICIENTE"][aria-pressed="true"]{border-color:var(--sem)}
textarea{width:100%;min-height:60px;border:1px solid var(--linha);
  border-radius:10px;padding:10px;font:inherit;resize:vertical}
nav.passos{display:flex;gap:10px;justify-content:space-between;margin:18px 0}
nav.passos button{flex:1;padding:12px;border-radius:10px;border:1px solid var(--linha);
  background:#fff;font:inherit;cursor:pointer;min-height:48px}
nav.passos button:disabled{opacity:.4;cursor:default}
.grelha{display:flex;flex-wrap:wrap;gap:5px;margin:14px 0}
.grelha button{width:34px;height:34px;border-radius:8px;border:1px solid var(--linha);
  background:#fff;font:600 12px/1 inherit;cursor:pointer}
.grelha button.f{background:var(--marca);border-color:var(--acento)}
.grelha button.agora{outline:2px solid var(--tinta)}
.fim{text-align:center}
.fim table{margin:18px auto;border-collapse:collapse;font-size:16px}
.fim td{padding:8px 18px;border-bottom:1px solid var(--linha);text-align:left}
.fim td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:700}
button.baixar{padding:18px 24px;border-radius:12px;border:0;background:var(--acento);
  color:#fff;font:600 17px/1 inherit;cursor:pointer;min-height:60px;width:100%}
button.baixar.rascunho{background:var(--sem)}
.nota{font-size:14px;color:var(--tinta-fraca);margin-top:16px}
.tec{font-size:13px;color:var(--tinta-fraca);word-break:break-all}
.tec div{margin:3px 0}
@media (max-width:520px){.envolve{padding:12px}h2{font-size:18px}}
@media (prefers-color-scheme:dark){
 :root:not([data-theme="light"]){--tinta:#e8eeea;--tinta-fraca:#9aa8a2;
  --papel:#111613;--cartao:#19211d;--linha:#2c3833;--acento:#6ac093;
  --marca:#1d2a24;--sim:#6ac093;--nao:#e08a8a;--amb:#e0b96a;--sem:#9aa8a2}
 :root:not([data-theme="light"]) .trecho{background:#141b17}
 :root:not([data-theme="light"]) button.voto,
 :root:not([data-theme="light"]) nav.passos button,
 :root:not([data-theme="light"]) .grelha button{background:#19211d;color:inherit}
 :root:not([data-theme="light"]) .aviso{background:#241f12;border-color:#4a3f22}
 :root:not([data-theme="light"]) .orig{color:#c3cec8}
}
</style></head><body><div class="envolve">
<header>
 <h1>REVISÃO T3 — PRAGA E DOENÇA</h1>
 <div class="conta"><span id="onde"></span><span id="pct"></span></div>
 <div class="barra"><i id="barra"></i></div>
</header>
<div id="palco"></div>
</div>
<script id="dados" type="application/json">__DADOS__</script>
<script>
const DOCS = JSON.parse(document.getElementById('dados').textContent);
const BOTOES = __BOTOES__;
const CHAVE = 'sintonia.t3.revisao.v1';
const palco = document.getElementById('palco');
let i = 0, respostas = ler();

function ler(){ try{ return JSON.parse(localStorage.getItem(CHAVE)) || {}; }
               catch(e){ return {}; } }
function gravar(){ try{ localStorage.setItem(CHAVE, JSON.stringify(respostas)); }
                   catch(e){ alerta(); } }
function alerta(){
  if(document.getElementById('semstorage')) return;
  const d=document.createElement('div'); d.id='semstorage'; d.className='aviso';
  d.textContent='Atenção: este navegador não está guardando o progresso. '
    +'Não feche a aba antes de exportar.';
  document.querySelector('header').after(d);
}
function feitas(){ return Object.keys(respostas).length; }
function esc(s){ const d=document.createElement('div'); d.textContent=s??'';
                 return d.innerHTML; }
function lista(a){ return (a&&a.length)
  ? '<ul class="sinais">'+a.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>'
  : '<p class="tec">— nenhum —</p>'; }

function pinta(){
  const n = DOCS.length, f = feitas();
  document.getElementById('onde').textContent =
    (i < n ? 'Documento '+(i+1)+' de '+n : 'Revisão concluída');
  document.getElementById('pct').textContent = f+' de '+n+' respondidos';
  document.getElementById('barra').style.width = Math.round(f/n*100)+'%';
  palco.innerHTML = (i < n) ? ficha(DOCS[i]) : fim();
  if(i < n) liga(); else ligaFim();
  window.scrollTo(0,0);
}

function ficha(d){
  const p = d.DISPLAY_TRANSLATION_PTBR, o = d.ORIGINAL_EVIDENCE;
  const r = respostas[d.DOC_SHA256] || {};
  const primeira = i===0 ? '<div class="aviso"><b>Antes de começar.</b> '
    +'O nome do arquivo e o nome da fonte aparecem apenas para você saber de '
    +'onde o documento veio. <b>Eles não determinam a resposta.</b> Decida '
    +'pelo texto.</div>' : '';
  return primeira + '<div class="cartao">'
   + '<div class="proc">'+esc(d.PUBLISHER)+' · '+esc(d.DOCUMENT_TYPE)+'</div>'
   + '<h2>'+esc(p.TITLE)+'</h2>'
   + '<div class="rot">Trecho principal (traduzido)</div>'
   + '<div class="trecho">'+esc(p.OPENING)+'</div>'
   + '<div class="rot">Como o documento se descreve</div>'+lista(p.SELF_DESCRIPTION)
   + '<div class="rot">Outros títulos visíveis</div>'+lista(p.SECTION_HEADERS)
   + '<details><summary>Mostrar original em italiano</summary>'
   + '<div class="orig"><div class="rot">Título original</div>'
   + '<div class="trecho">'+esc(o.TITLE)+'</div>'
   + '<div class="rot">Trecho original</div>'
   + '<div class="trecho">'+esc(o.OPENING)+'</div>'
   + '<div class="rot">Auto-descrição original</div>'+lista(o.SELF_DESCRIPTION)
   + '<div class="rot">Títulos originais</div>'+lista(o.SECTION_HEADERS)
   + '</div></details>'
   + '<details><summary>Detalhes técnicos</summary><div class="tec">'
   + '<div>DOC_SHA256: '+esc(d.DOC_SHA256)+'</div>'
   + '<div>ITEM_ID: '+esc(d.ITEM_ID)+'</div>'
   + '<div>SOURCE_ID: '+esc(d.SOURCE_ID)+'</div>'
   + '<div>LANGUAGE: '+esc(d.LANGUAGE)+'</div>'
   + '<div>CANONICAL_PATH: '+esc(d.CANONICAL_PATH)+'</div>'
   + '<div>BODY_PATH: '+esc(d.BODY_PATH)+'</div></div></details>'
   + '<div class="botoes">'
   + BOTOES.map(b=>'<button class="voto" data-l="'+b[0]+'" aria-pressed="'
       +(r.LABEL===b[0])+'"><span class="em">'+b[1]+'</span><span><b>'+b[2]
       +'</b><span>'+b[3]+'</span></span></button>').join('')
   + '</div>'
   + '<div class="rot">Observação opcional</div>'
   + '<textarea id="nota" placeholder="Não é obrigatório.">'+esc(r.NOTE||'')+'</textarea>'
   + '</div>'
   + '<nav class="passos"><button id="ant"'+(i===0?' disabled':'')+'>← Anterior</button>'
   + '<button id="prox">Pular / Próximo →</button></nav>'
   + grelha();
}

function grelha(){
  return '<div class="grelha">'+DOCS.map((d,k)=>'<button data-k="'+k+'" class="'
    +(respostas[d.DOC_SHA256]?'f ':'')+(k===i?'agora':'')+'">'+(k+1)
    +'</button>').join('')+'</div>';
}

function liga(){
  const d = DOCS[i];
  palco.querySelectorAll('button.voto').forEach(b=>{
    b.onclick = ()=>{
      const nota = (palco.querySelector('#nota').value||'').trim();
      respostas[d.DOC_SHA256] = {LABEL:b.dataset.l, NOTE: nota||null,
                                 DECIDED_AT:new Date().toISOString()};
      gravar();
      i = proximaEmFalta();
      pinta();
    };
  });
  palco.querySelector('#ant').onclick = ()=>{ if(i>0){ i--; pinta(); } };
  palco.querySelector('#prox').onclick = ()=>{ i = Math.min(i+1, DOCS.length); pinta(); };
  palco.querySelectorAll('.grelha button').forEach(b=>{
    b.onclick = ()=>{ i = +b.dataset.k; pinta(); };
  });
}

function proximaEmFalta(){
  for(let k=i+1;k<DOCS.length;k++) if(!respostas[DOCS[k].DOC_SHA256]) return k;
  for(let k=0;k<DOCS.length;k++) if(!respostas[DOCS[k].DOC_SHA256]) return k;
  return DOCS.length;
}

function fim(){
  const c = {}; BOTOES.forEach(b=>c[b[0]]=0);
  Object.values(respostas).forEach(r=>{ if(c[r.LABEL]!==undefined) c[r.LABEL]++; });
  const f = feitas(), completo = f===DOCS.length;
  return '<div class="cartao fim">'
   + '<h2>'+(completo?'REVISÃO CONCLUÍDA':'REVISÃO INCOMPLETA')+'</h2>'
   + '<table><tr><td>SIM</td><td>'+c.T3_SIM+'</td></tr>'
   + '<tr><td>NÃO</td><td>'+c.T3_NAO+'</td></tr>'
   + '<tr><td>AMBÍGUO</td><td>'+c.T3_AMBIGUO+'</td></tr>'
   + '<tr><td>SEM EVIDÊNCIA</td><td>'+c.EVIDENCIA_INSUFICIENTE+'</td></tr>'
   + '<tr><td>TOTAL</td><td>'+f+' de '+DOCS.length+'</td></tr></table>'
   + '<button class="baixar'+(completo?'':' rascunho')+'" id="baixar">'
   + (completo?'BAIXAR RESPOSTAS JSON':'EXPORTAR RASCUNHO')+'</button>'
   + '<p class="nota">Este JSON contém <b>respostas humanas</b>. Ele ainda '
   + 'precisa passar pela validação do SINTONIA antes de virar gabarito. '
   + 'Nada aqui é escrito automaticamente em nenhum arquivo do projeto.</p>'
   + '</div><nav class="passos"><button id="ant">← Voltar e revisar</button>'
   + '<button id="prox" disabled>—</button></nav>' + grelha();
}

function ligaFim(){
  palco.querySelector('#ant').onclick = ()=>{ i = Math.max(0,DOCS.length-1); pinta(); };
  palco.querySelectorAll('.grelha button').forEach(b=>{
    b.onclick = ()=>{ i = +b.dataset.k; pinta(); };
  });
  palco.querySelector('#baixar').onclick = baixar;
}

function baixar(){
  const completo = feitas()===DOCS.length;
  const saida = {
    SCHEMA:"sintonia.t3-human-review-results/1", UNIVERSE:"T3",
    DESCRIPTION:"Praga e doença", REVIEW_TYPE:"HUMAN",
    LANGUAGE_OF_INTERFACE:"pt-BR",
    SOURCE_PACKET:"T3-HUMAN-REVIEW-PENDING-V1.json",
    STATUS: completo?"COMPLETE":"INCOMPLETE",
    TOTAL_EXPECTED: DOCS.length, TOTAL_REVIEWED: feitas(),
    COMPLETED_AT: completo? new Date().toISOString() : null,
    ITEMS: DOCS.filter(d=>respostas[d.DOC_SHA256]).map(d=>{
      const r = respostas[d.DOC_SHA256];
      return {DOC_SHA256:d.DOC_SHA256, ITEM_ID:d.ITEM_ID,
              SOURCE_ID:d.SOURCE_ID, PUBLISHER:d.PUBLISHER,
              LABEL:r.LABEL, NOTE:r.NOTE??null, HUMAN_REASON:null,
              DECIDED_AT:r.DECIDED_AT,
              ORIGINAL_EVIDENCE:d.ORIGINAL_EVIDENCE};
    })
  };
  const b = new Blob([JSON.stringify(saida,null,1)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(b);
  a.download = 'T3-HUMAN-REVIEW-RESULTS-V1.json';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href), 4000);
}

if(feitas()>0 && feitas()<DOCS.length){ i = proximaEmFalta(); }
else if(feitas()===DOCS.length){ i = DOCS.length; }
pinta();
</script></body></html>
"""


def construir():
    d = dados()
    bruto = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    return (PAGINA
            .replace("__DADOS__", bruto)
            .replace("__BOTOES__", json.dumps(BOTOES, ensure_ascii=False)))


def main():
    d = dados()
    pagina = construir()
    print("INTERFACE DE REVISAO DE T3 (pt-BR)")
    print("=" * 74)
    print(f"  TOTAL_DOCUMENTS            {len(d)}")
    print(f"  PTBR_TRANSLATED            "
          f"{sum(1 for x in d if x['DISPLAY_TRANSLATION_PTBR']['OPENING'].strip())}"
          f"/{len(d)}")
    print(f"  ORIGINAL_PRESERVED         "
          f"{sum(1 for x in d if x['ORIGINAL_EVIDENCE']['OPENING'].strip())}/{len(d)}")
    print(f"  LABEL_OPTIONS              {len(BOTOES)}   "
          f"{[b[0] for b in BOTOES]}")
    print(f"  AUTO_LABELS_ASSIGNED       0")
    for proibido in PROIBIDOS_NO_HTML:
        if proibido in pagina:
            print(f"  ⚠️  «{proibido}» APARECE NO HTML")
    print(f"  OLD_CLASSIFIER_OUTPUT      ausente")
    print(f"  SOURCE_TERRITORY           ausente")
    print(f"  tamanho da pagina          {len(pagina.encode()) // 1024} KiB")
    if "--escrever" in sys.argv:
        with open(os.path.join(RAIZ, HTML), "w", encoding="utf-8") as f:
            f.write(pagina)
        print(f"\n  escrito: {HTML}")
    else:
        print("\n  (nada escrito — passe --escrever)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
