// Extrai os 139 pontos do documento primario preservado.
// Uso, de dentro desta pasta:  node extract-points.js monitoraggio-2026-09-07.html
// O JSON gerado e DERIVADO. A evidencia e o HTML com o SHA256 do MANIFEST.json.
const fs = require("fs");
const src = process.argv[2] || "monitoraggio-2026-09-07.html";
const h = fs.readFileSync(src, "utf8");
const re = /<div class="row reports_points" id="(\d+)"[\s\S]*?<h3>([\s\S]*?)<a [\s\S]*?Latitudine:\s*([-\d.]+),\s*Longitudine:\s*([-\d.]+)[\s\S]*?Data di campionamento:\s*([^<]*?)\s*<[\s\S]*?Infestazione attiva:\s*([^<]*?)\s*<[\s\S]*?Catture adulti:\s*<strong>([^<]*)<\/strong>/g;
let m, out = [];
while ((m = re.exec(h))) {
  const chunk = h.slice(m.index, re.lastIndex);
  const c = chunk.match(/mosca-status-dot" style="background:\s*([A-Z]+)/);
  out.push({
    point_id: m[1],
    name: m[2].replace(/&#39;/g, "'").replace(/&nbsp;/g, " ").trim(),
    lat: +m[3], lon: +m[4],
    sampling_date: m[5],
    infestation: m[6],
    color: c ? c[1] : "LIGHTGREY",
    catture_adulti: m[7]
  });
}
const st = {};
out.forEach(o => { st[o.infestation] = (st[o.infestation] || 0) + 1; });
console.log("pontos:", out.length, "| ids unicos:", new Set(out.map(o => o.point_id)).size);
console.log(JSON.stringify(st, null, 1));
fs.writeFileSync("points-" + src.replace(/^monitoraggio-|\.html$/g, "") + ".json", JSON.stringify(out, null, 1));
