/* Minimal static server for the client package, so the portal can be exercised
   in a real browser exactly as it will be served to the client. */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { CLIENT } from './lib/harness.mjs';

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.otf': 'font/otf' };
const PORT = Number(process.argv[2] || 8899);

http.createServer((req, res) => {
  const url = decodeURIComponent((req.url || '/').split('?')[0]);
  const rel = url === '/' ? '/portale.html' : url;
  const file = path.join(CLIENT, rel);
  if (!file.startsWith(CLIENT)) { res.writeHead(403).end('no'); return; }
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404, { 'content-type': 'text/plain' }).end('404 ' + rel); return; }
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' }).end(buf);
  });
}).listen(PORT, () => console.log('serving client on http://localhost:' + PORT));
