import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const C=process.argv[2], P=Number(process.argv[3]||8960);
const T={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css','.png':'image/png','.svg':'image/svg+xml','.ttf':'font/ttf','.otf':'font/otf'};
http.createServer((q,r)=>{let x=decodeURIComponent((q.url||'/').split('?')[0]);if(x==='/')x='/portale.html';if(!path.extname(x))x+='.html';const f=path.join(C,x);fs.readFile(f,(e,b)=>{if(e){r.writeHead(404).end('404');return;}r.writeHead(200,{'content-type':T[path.extname(f)]||'application/octet-stream'}).end(b);});}).listen(P,()=>console.log('serving '+P));
