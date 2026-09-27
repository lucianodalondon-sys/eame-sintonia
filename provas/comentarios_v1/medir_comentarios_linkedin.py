"""COMENTARIOS-V1 · a medicao que falta para a rota gratuita de comentario do LinkedIn (D106).

    py provas/comentarios_v1/medir_comentarios_linkedin.py <url do POST publico> <pasta de saida nova>

O QUE ELA PROVA OU DERRUBA: que a pagina PUBLICA do post, pedida DESLOGADA pela mesma
porta do Scrap (`adaptador_linkedin._buscar_texto` sob `scrap_http.autorizacao_do_dono`),
serve um bloco JSON-LD com `comment[]`. Se servir, `leis/social_matriz.py`
LINKEDIN/FETCH_COMMENTS pode passar de POSSIBLE_NOT_PROVED a PROVED (com esta prova); se
nao servir, fica escrito que a rota gratuita NAO existe.

1 pedido ao linkedin.com (conta no teto de 5/24 h: conferir o contador antes). Portao de
egresso IT antes e depois. Sem login, sem cookie. Guarda os BYTES e o sha256 (a prova), e
o resultado do leitor `comentarios_do_jsonld` — com pseudonimo, sem nome, url, avatar.
E do servico/coordenador correr (D86-c): esta missao nao a correu.
"""
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import adaptador_linkedin as al  # noqa: E402
import scrap_http as http  # noqa: E402


def egresso_it():
    r = subprocess.run([sys.executable, os.path.join(RAIZ, 'superficie', 'rede.py'), '--portao-de-egresso', 'IT'],
                       cwd=RAIZ, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    return r.returncode == 0, (r.stdout or r.stderr or '')[-300:]


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    url, saida = sys.argv[1], sys.argv[2]
    al._alvo_e_post_publico(url)                  # a trava, sem rede: so post publico
    os.makedirs(saida, exist_ok=False)
    ok, txt = egresso_it()
    res = {'DATASET': 'MEDIDA-COMENTARIOS-LINKEDIN', 'POST_URL': url, 'EGRESSO_ANTES': {'IT': ok, 'SAIDA': txt}}
    if not ok:
        res['ESTADO'] = 'PAROU_EGRESSO_FORA_DE_IT'
    else:
        with http.autorizacao_do_dono(al.ROTA_POST_PUBLICO, al.HOSTS_DA_AQUISICAO,
                                      decisao=al.AUTORIZACAO_ESCRITA_D24, plataforma=al.PLATAFORMA):
            corpo = al._buscar_texto(url, None)
        b = corpo if isinstance(corpo, (bytes, bytearray)) else str(corpo).encode('utf-8', 'replace')
        sha = hashlib.sha256(b).hexdigest()
        open(os.path.join(saida, 'POST-%s.html' % sha[:16]), 'wb').write(b)
        objs = al.comentarios_do_jsonld(b, post_url=url, run_id='MEDIDA-COMENTARIOS-V1')
        res.update(ESTADO='MEDIDO', BYTES=len(b), SHA256=sha,
                   TEM_JSONLD=b'application/ld+json' in b, COMENTARIOS_NO_JSONLD=len(objs),
                   AMOSTRA=[{k: o.get(k) for k in ('NATIVE_ID', 'PUBLISHED_AT', 'SOURCE_ACCOUNT', 'CLAIM_KIND',
                                                   'PARENT_CONTENT_ID')} | {'TEXT_HEAD': (o.get('TEXT') or '')[:120]}
                           for o in objs[:5]],
                   VEREDITO=('ROTA_GRATUITA_PROVADA: a pagina publica serviu %d comentario(s) no JSON-LD' % len(objs)
                             if objs else 'A_PAGINA_NAO_SERVIU_COMENTARIO_NO_JSONLD — nao e «o post nao tem '
                                          'comentarios»: conferir a contagem da pagina antes de concluir'))
        ok2, txt2 = egresso_it()
        res['EGRESSO_DEPOIS'] = {'IT': ok2, 'SAIDA': txt2}
    with open(os.path.join(saida, 'MEDIDA-COMENTARIOS-LINKEDIN.json'), 'w', encoding='utf-8') as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: res.get(k) for k in ('ESTADO', 'BYTES', 'TEM_JSONLD', 'COMENTARIOS_NO_JSONLD', 'VEREDITO')},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
