#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da PROVA-TETO-SOCIAL: 18 mutantes, cada um confirmado por git diff; corre
tests/test_prova_teto_social.py e repoe o ficheiro.  py provas/_mutantes_prova_teto_social.py"""
import io,subprocess,sys,os
M=[
 ("M1 contador fora do abridor","coleta/scrap_http.py","urllib.request.install_opener(urllib.request.build_opener(_PortaoEmCadaSalto(),\n                                                          _ContaCadaPedido()))","urllib.request.install_opener(urllib.request.build_opener(_PortaoEmCadaSalto()))"),
 ("M2 https nao conta","coleta/scrap_http.py","    https_request = http_request\n",""),
 ("M3 www nao se tira","coleta/scrap_http.py","    return h[4:] if h.startswith('www.') else h\n","    return h\n"),
 ("M4 nao contado vira zero","coleta/scrap_http.py","    if por_host is None:\n        nao_contado(quem)\n        return\n","    if por_host is None:\n        return\n"),
 ("M5 zerar nao zera","coleta/scrap_http.py","        _CONTAGEM['POR_HOST'].clear()\n","        pass\n"),
 ("M6 CONNECT conta","ferramentas/youtube_transcrever.py","(GET|POST|HEAD|PUT|DELETE|PATCH|OPTIONS)","(GET|POST|HEAD|PUT|DELETE|PATCH|OPTIONS|CONNECT)"),
 ("M7 sem Host ignora","ferramentas/youtube_transcrever.py","        if not m:\n            return None\n","        if not m:\n            continue\n"),
 ("M8 corpo de POST conta","ferramentas/youtube_transcrever.py","        if not _PEDIDO.match(linha):\n            continue\n","        if not linha.startswith('send:'):\n            continue\n"),
 ("M9 sem linha no ABORTED","coleta/scrap_colheita.py","        escrever_linha(linha_da_corrida(run_id=run_id, fase=fase, fonte=fonte,\n                                        inicio=inicio, abortada=e))\n        raise\n","        raise\n"),
 ("M10 ABORTED engole a excepcao","coleta/scrap_colheita.py","                                        inicio=inicio, abortada=e))\n        raise\n","                                        inicio=inicio, abortada=e))\n        return 1\n"),
 ("M11 fase fora conta","coleta/scrap_colheita.py","    if fase not in FASES_CONTADAS:\n","    if False:\n"),
 ("M12 nao contados ignorados","coleta/scrap_colheita.py","    nao_contados = list(de_fora)\n","    nao_contados = []\n"),
 ("M13 sem zerar por corrida","coleta/scrap_colheita.py","    http.zerar_contagem()\n    inicio = _agora()\n","    inicio = _agora()\n"),
 ("M14 D41 desligada","provas/prova_teto_dominio.py",'MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com"}','MESMO_ORCAMENTO = {}'),
 ("M15 D41 fora do verificar","provas/prova_teto_dominio.py","            dom = orcamento_de(host)\n","            dom = dominio_registavel(host)\n"),
 ("M16 XX ignorado","provas/prova_teto_dominio.py",'(?:IT|XX)-T','IT-T'),
 ("M17 D41 junta linkedin","provas/prova_teto_dominio.py",'MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com"}','MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com", "licdn.com": "linkedin.com"}'),
 ("M18 adaptador nao passa o yt-dlp","coleta/adaptador_youtube.py","        http.contar_de_fora(getattr(ytv, 'ULTIMO_TRAFEGO', None), quem='yt-dlp')\n","        pass\n"),
]
env=dict(os.environ,PYTHONUTF8="1")
for nome,f,a,b in M:
    orig=io.open(f,encoding="utf-8",newline="").read()
    s=orig.replace("\r\n","\n"); nl="\r\n" if "\r\n" in orig else "\n"
    if s.count(a)!=1: print(nome,"NAO_APLICOU",s.count(a)); continue
    try:
        io.open(f,"w",encoding="utf-8",newline="").write(s.replace(a,b).replace("\n",nl))
        d=subprocess.run(["git","diff","--quiet","--",f]).returncode
        r=subprocess.run([sys.executable,"-m","unittest","tests.test_prova_teto_social"],capture_output=True,text=True,env=env,timeout=600)
        print(nome,"MORTO" if r.returncode!=0 else "SOBREVIVEU", "(diff ok)" if d==1 else "(SEM DIFF!)")
    finally:
        io.open(f,"w",encoding="utf-8",newline="").write(orig)
