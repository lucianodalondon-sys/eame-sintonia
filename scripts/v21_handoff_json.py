# -*- coding: utf-8 -*-
import json

R = 'C:/eame-sintonia'
ac = json.load(open(R + '/build/ITALY-REALITY-HANDOFF-V2.1/ACCEPTANCE-REPORT.json',
                    encoding='utf-8'))
au = json.load(open(R + '/handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json',
                    encoding='utf-8'))
tm = json.load(open(R + '/data/i18n/v21-traducoes.json', encoding='utf-8'))

M, C, S, L, SEP = (ac['MASTER'], ac['CROSSINGS'], ac['SOURCES'], ac['LINGUA'],
                   ac['SEPARACAO'])

d = {
 "mission": "SINTONIA ITALY PILOT · REALITY HANDOFF V2.1 — transformar handoff "
            "anterior + coleta last-mile num pacote unico que o Design carregue "
            "sem adivinhar nada. Inteligencia EXTERNA sobre o mercado agricola "
            "italiano, para a ADAMA. Todo dado publico, com URL.",
 "paused_at": "2026-09-02",
 "paused_reason": "pausa deliberada para preservar limite de uso da conta Claude; "
                  "o trabalho continua em outra conta. A missao NAO falhou.",
 "repository": "C:/eame-sintonia",
 "remote": "https://github.com/lucianodalondon-sys/eame-sintonia.git",
 "branch": "claude/italy-v2-handoff",
 "branch_created_from": "claude/eame-competitor-public-communication @ "
                        "21c8ec705d9ceb140299e8351a889b2984fe2188",
 "branch_why_dedicated": "a branch de origem e usada AO MESMO TEMPO por outra "
                         "sessao Claude que trabalha no PORTAL/SITE. Empurrar o "
                         "V2 nela misturaria duas missoes.",
 "head": "PREENCHIDO_NO_COMMIT_FINAL",
 "site_branch_touched": False,
 "safe_to_resume": True,

 "completed": [
  {"item": "pacote V2.1 construido e medido",
   "artifact": "build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip",
   "evidence": "ACCEPTANCE-REPORT.json, recontado dos arquivos a cada build"},
  {"item": "defeito 1 do V2 — unificacao",
   "evidence": "CANONICAL-INTELLIGENCE-MASTER.json com %d registros e %d IDs "
               "duplicados" % (M['RECORDS_TOTAL'], M['DUPLICATE_IDS'])},
  {"item": "defeito 2 do V2 — cruzamentos refeitos por ID normalizado",
   "evidence": "%d emitidos · %d apoio orfao · %d apoio inseguro · %d cultura "
               "divergente (o V2 tinha 36 culturas erradas e 7 de 19 contaminados)"
               % (C['EMITIDOS'], C['APOIO_ORFAO'], C['APOIO_NAO_CLIENT_SAFE'],
                  C['CULTURA_DIVERGENTE'])},
  {"item": "defeito 3 do V2 — granularidade do ISTAT restaurada",
   "evidence": "CROP-ECONOMIC-WEIGHT com 2978 registros; 2945 linhas atomicas "
               "carimbadas LAST_MILE, nao DERIVED"},
  {"item": "defeito 4 do V2 — separacao ingest/arquivo",
   "evidence": "%d arquivos no DESIGN-INGEST · %d papel de trabalho dentro · %d "
               "itens no INTERNAL-ARCHIVE"
               % (SEP['ARQUIVOS_EM_DESIGN_INGEST'],
                  len(SEP['PAPEL_DE_TRABALHO_EM_DESIGN_INGEST']),
                  SEP['ITENS_EM_INTERNAL_ARCHIVE'])},
  {"item": "localizacao IT/EN",
   "evidence": "%d frases na memoria · %d campos com IT+EN · %d ainda so em "
               "portugues · %d com ORIGINAL_RESEARCH_TEXT preservado"
               % (tm['COUNT'], L['CAMPOS_COM_IT_E_EN'],
                  L['AINDA_SO_EM_PORTUGUES'], L['COM_ORIGINAL_PRESERVADO'])},
  {"item": "695 ressalvas subiram de RESEARCH para campo client-facing traduzido",
   "evidence": "campos *_PROMOVIDO_DE nos registros. Sem isso a tela mostraria "
               "NADA no lugar da ressalva."},
  {"item": "chave das fontes corrigida",
   "evidence": "de 13.280 citacoes, 56%% nao resolviam; agora %d fontes citadas "
               "sem cadastro" % S['CITADAS_SEM_CADASTRO']},
  {"item": "cruzamentos ganharam carimbo",
   "evidence": "CLIENT_SAFE=false + RENDERABLE_WITH_METHOD=true. Antes o "
               "cabecalho dizia 20 client-safe e os registros nao tinham campo "
               "nenhum — a tela teria filtrado os 20 e mostrado vazio."},
 ],

 "partial": [
  {"file": "handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json",
   "origin": "workflow v21-auditar-pacote (wf_2c05414f-38d)",
   "status": "38 agentes concluidos; a fase de REFUTACAO nao rodou",
   "integrated": False, "authoritative": False,
   "counts": dict({"total": au['TOTAL']}, **au['POR_GRAVIDADE']),
   "risk": "parte foi medida ENQUANTO o pacote era reescrito — um dos proprios "
           "achados diz isso. Varios ja foram corrigidos depois de medidos. "
           "NENHUM pode ser tratado como confirmado sem reverificacao.",
   "next_action": "reverificar os 35 BLOQUEIA_ENTREGA um a um contra o "
                  "DESIGN-INGEST atual"},
  {"file": "handoff/paused-v2/conferencia-de-sentido.json",
   "origin": "workflow v21-conferir-sentido (wf_2afbff77-eb9)",
   "status": "VAZIO — zero agentes concluidos antes da interrupcao",
   "integrated": False, "authoritative": False,
   "next_action": "opcional: refazer a leitura semantica das 1.017 traducoes — "
                  "e o que a trava mecanica declara nao alcancar"},
  {"file": "supabase/migrations/019_*.sql · 020_*.sql · 021_*.sql",
   "origin": "sessao anterior", "status": "escritas, NAO aplicadas",
   "integrated": False, "authoritative": True,
   "next_action": "nao aplicar sem pedido explicito do usuario — o despacho ja "
                  "foi negado por permissao uma vez"},
 ],

 "not_started": [
  "nenhuma tela construida — este pacote e contrato de dado",
  "nenhuma validacao com o cliente ADAMA",
  "nenhuma coleta nova (a missao V2.1 proibe: e de organizacao, nao de descoberta)",
  "nenhuma verificacao humana registro a registro dos 2.891 client-safe",
 ],

 "important_files": [
  "HANDOFF-V2-PAUSE.md",
  "HANDOFF-V2-PAUSE.json",
  "handoff/paused-v2/MANIFESTO.json",
  "handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json",
  "docs/design/ITALY-V2.1-README-FIRST.md",
  "scripts/v21_cadeia.sh",
  "data/i18n/v21-traducoes.json",
  "build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip",
  "build/ITALY-REALITY-HANDOFF-V2/",
 ],

 "datasets": {k: {"total": v["TOTAL"], "client_safe": v["CLIENT_SAFE"]}
              for k, v in sorted(ac['POR_COLECAO'].items())},

 "qa_state": {
  "gate_violations": ac['QA_GATE']['VIOLACOES'],
  "sem_qa_status": ac['QA_GATE']['SEM_QA_STATUS'],
  "contagens_divergentes": len(ac['QA_GATE']['CONTAGEM_DECLARADA_DIVERGE']),
  "master_total": M['RECORDS_TOTAL'],
  "master_client_safe": M['RECORDS_CLIENT_SAFE'],
  "duplicate_ids": M['DUPLICATE_IDS'],
  "by_origin": M['BY_ORIGIN'],
  "crossings": C,
  "sources": {"linhas": S['LINHAS_DE_FONTE'],
              "chaves_que_resolvem": S['CHAVES_QUE_RESOLVEM'],
              "citadas_sem_cadastro": S['CITADAS_SEM_CADASTRO']},
  "lingua": {"campos_com_it_en": L['CAMPOS_COM_IT_E_EN'],
             "ainda_so_em_portugues": L['AINDA_SO_EM_PORTUGUES']},
 },

 "known_failures": [
  "1 teste pre-existente falha: tests/test_comunicacao.py :: 'nenhuma casa nasce "
  "autorizada'. NAO e desta missao — o arquivo esta intocado no git e le "
  "scripts/comunicacao_*, que o V2.1 nao encostou.",
  "99 achados de auditoria nao refutados — ver partial",
 ],

 "quarantine": [
  "build/ITALY-REALITY-HANDOFF-V2/TOP-CROSSINGS.json — descartado, nao remendado. "
  "36 IDs com cultura errada, 7 de 19 contaminados. O METODO era o defeito "
  "(casamento por substring: 'riso' batia dentro de 'comparison').",
  "a voz QA_REJECTED em PUBLIC-VOICES — frase em <blockquote> sem aspas: destaque "
  "editorial do jornal, nao fala do rizicultor",
  "fullpage e max-ace como produtos de cultura — sao banner do site da ADAMA",
  "_COLECOES.json dentro de DESIGN-INGEST — rascunho de build que vira segundo "
  "indice ao lado do APP-MANIFEST; a cadeia move sozinha",
  "OPPORTUNITIES.json — 3 registros, nenhum client-safe. Nao promover.",
 ],

 "tests": {
  "trava_da_traducao": {
   "file": "tests/test_v21_traducao_trava.py", "count": 23,
   "status": "todos passam",
   "por_que_importa": "a trava foi corrigida SEIS vezes ate parar de reprovar "
                      "traducao correta, e cada correcao afrouxou algo. Estes "
                      "testes plantam mentira de proposito. Se comecarem a "
                      "falhar, a trava virou carimbo."},
  "suite_geral": {"status": "1 falha pre-existente de outra frente — ver "
                            "known_failures"},
 },

 "commands": {
  "python": "py (nao 'python'). SEMPRE com: export PYTHONIOENCODING=utf-8:replace",
  "verificacao_leve": "export PYTHONIOENCODING=utf-8:replace && "
                      "py scripts/v21_aceitacao.py",
  "reconstruir_pacote": "export PYTHONIOENCODING=utf-8:replace && "
                        "bash scripts/v21_cadeia.sh",
  "testes_da_trava": "export PYTHONIOENCODING=utf-8:replace && py -c "
                     "\"import sys;sys.path[:0]=['tests','scripts'];"
                     "import test_v21_traducao_trava as T;"
                     "[getattr(T,n)() for n in dir(T) if n.startswith('test_')];"
                     "print('ok')\"",
  "AVISO_DA_CADEIA": "v21_ingest.py faz rmtree da pasta do pacote. Rodar um passo "
                     "do meio sozinho apaga EM SILENCIO carimbos, rechaveamento "
                     "e traducoes. Rode a cadeia INTEIRA.",
 },

 "receitas": {
  "windows_maiuscula": "Windows nao distingue maiuscula: apagar Scripts/ apaga "
                       "scripts/. Ja custou 75 arquivos.",
  "ministero_pdf": "curl devolve 0 bytes com HTTP 200 nos PDFs do Ministero della "
                   "Salute; urllib devolve 222 KB. FERRAMENTA QUE RECUSA != PORTA "
                   "FECHADA.",
  "vpn_italiana": "abre ISMEA, ISTAT e ARPAV. NAO abre a ADAMA, que bloqueia por "
                  "navegador (Akamai) — so janela grafica passa.",
  "http_200_enganoso": "um HTTP 200 nao diz nada sobre a rota se voce nao sabe por "
                       "onde saiu. Um coletor ja concluiu 'o ISMEA nunca foi "
                       "bloqueado' porque recebeu 200 — com a VPN ligada, sem saber.",
  "catalogo_adama": "a listagem por categoria e bloqueada, mas as paginas por "
                    "cultura (/vite /mais /riso /cereali /pomodoro /pomacee /soia) "
                    "abrem e estao no menu da propria pagina 404.",
 },

 "background_tasks": [
  {"task": "v21-localizar-resto (wf_8918345b-2e3)", "status": "concluida",
   "output": "726 frases IT/EN, 33 refeitas apos reprovacao, 0 lotes perdidos",
   "terminated": True, "remains_to_integrate": False},
  {"task": "v21-auditar-pacote (wf_2c05414f-38d)",
   "status": "INTERROMPIDA por TaskStop",
   "output": "38 agentes -> 99 achados brutos, salvos em handoff/paused-v2/",
   "terminated": True, "remains_to_integrate": True},
  {"task": "v21-conferir-sentido (wf_2afbff77-eb9)",
   "status": "INTERROMPIDA por TaskStop", "output": "nenhuma",
   "terminated": True, "remains_to_integrate": False},
  {"task": "localizacao inicial (wimgu1ear)", "status": "concluida",
   "output": "94 registros / 300 campos", "terminated": True,
   "remains_to_integrate": False},
 ],
 "token_heavy_tasks_running": 0,

 "known_blockers": [
  "a pasta C:/eame-sintonia e um worktree COMPARTILHADO com outra sessao Claude "
  "(missao do PORTAL/SITE). Ha arquivos modificados que NAO sao desta missao: "
  "italia-portale/, scripts/instagram_*, tests/test_adama_es_gate.py, act.json, "
  "b.json, st*.json, tmp_ce/. Nunca inclui-los num commit desta missao.",
 ],

 "next_step": "Reverificar os 35 achados BLOQUEIA_ENTREGA de "
              "handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json, um a "
              "um, contra o DESIGN-INGEST atual — e so entao corrigir o que "
              "sobreviver. Comecar por: (1) PROVINCIAL virou REGIONAL em 24 "
              "registros client-safe; (2) 11 de 14 cruzamentos de rotulo casam a "
              "cultura certa com o problema errado; (3) um boletim do Friuli "
              "carimbado tambem como Toscana; (4) 2.222 registros citam 'fonte "
              "nao declarada' como unica fonte.",
}

json.dump(d, open(R + '/HANDOFF-V2-PAUSE.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('HANDOFF-V2-PAUSE.json escrito · %d colecoes · %d achados parciais'
      % (len(d['datasets']), au['TOTAL']))
