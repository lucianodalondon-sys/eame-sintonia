# -*- coding: utf-8 -*-
"""D140 · OS MUTANTES DA EXCEÇÃO PREVIEW_E2E — a guarda morde?

    python provas/l1_governanca/mutantes_excecao_preview.py [saida.json]

Cada mutante estraga UMA verificacao da guarda em `leis/fundacao_da_coleta.py` — o
vazamento para producao, o escopo que alarga, a Sala que se escreve, o objeto
nao liberado que passa, a D140 que deixa de contar — e corre
`tests.test_excecao_preview_e2e`. Mutante MORTO = a suite reprovou.

Reversivel e local: escreve so no ficheiro da lei, desfaz no fim de cada
mutante e confere o sha256 byte a byte. Zero rede, zero Git.
Cada corrida usa uma pasta de .pyc propria: um mutante do mesmo tamanho no
mesmo segundo nao pode ser servido pelo .pyc do original.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALVO = os.path.join(RAIZ, "leis", "fundacao_da_coleta.py")
SUITE = "tests.test_excecao_preview_e2e"

# (nome, pergunta da missao, trecho original, trecho mutado)
MUTANTES = [
    ('M01_excecao_destrava_a_inteligencia', 'a',
     "    if COLLECTION_FOUNDATION_CLOSED:\n        return True, 'COLLECTION_FOUNDATION_CLOSED=SIM",
     "    if COLLECTION_FOUNDATION_CLOSED or excecao_vigente(*carregar()[:2]):\n        return True, 'COLLECTION_FOUNDATION_CLOSED=SIM"),
    ('M02_entrada_que_fecha_a_fundacao_vale', 'a',
     "or e.get('NAO_FECHA_A_FUNDACAO') is not True:",
     ':'),
    ('M03_branch_de_producao_aceite', 'b',
     'if not ramo or ramo_de_producao(ramo, publicacao):',
     'if not ramo:'),
    ('M04_host_canonico_aceite', 'b',
     "if host and host == nome_do_host(publicacao.get('CANONICAL_HOST'))[0]:",
     'if False:'),
    ('M05_contrato_alarga_o_escopo', 'b',
     'tipos = set(DESTINOS_DO_PREVIEW) & set(',
     'tipos = set(DESTINOS_DO_PREVIEW) | set('),
    ('M06_para_cliente_aceite', 'b',
     "if d.get('PARA_CLIENTE') is not False:",
     "if d.get('PARA_CLIENTE') is True:"),
    ('M07_build_local_com_host_publico', 'b',
     "if d.get('TIPO') == 'BUILD_LOCAL' and host not in HOSTS_LOCAIS:",
     'if False:'),
    ('M08_artefatos_autorizados_em_producao', 'b',
     'if e is None or any(ramo_de_producao(r, publicacao) for r in ramos):',
     'if e is None:'),
    ('M09_objeto_nao_liberado_passa', 'c',
     "if o.get('LIBERACAO') != LIBERADO:",
     'if False:'),
    ('M10_conferencia_falhada_passa', 'c',
     "elif any(c.get(k) != 'PASSOU' for k in CONFERENCIAS_QUE_PASSAM):",
     'elif False:'),
    ('M11_c8_falhou_em_qualquer_caixa_passa', 'auditor-L10',
     "elif not c8.strip() or 'falhou' in c8.casefold():",
     'elif not c8.strip():'),
    ('M12_gates_do_pote_v2_saltados', 'c',
     'violacoes = validar(pote)',
     'violacoes = []'),
    ('M13_pote_vazio_passa', 'c',
     'if n == 0:',
     'if False:'),
    ('M14_escrever_na_sala_aceite', 'd',
     "if pedido.get('OPERACAO') != PUBLICAR_NO_PREVIEW:",
     "if pedido.get('OPERACAO') not in (PUBLICAR_NO_PREVIEW, 'ESCREVER_NA_SALA', 'MARCAR_CONSUMIDO_EM', None):"),
    ('M15_sala_real_sem_read_only', 'd',
     "if not isinstance(ent, dict) or ent.get('TIPO') != ENTRADA_READ_ONLY or ent.get('READ_ONLY') is not True:",
     'if not isinstance(ent, dict):'),
    ('M17_d140_fora_do_diario_vale', 'e',
     "if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW or not _d140_vigente_no_diario(diario):",
     "if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW:"),
    ('M18_outra_autoridade_vale', 'e',
     "if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW or not _d140_vigente_no_diario(diario):",
     'if not _d140_vigente_no_diario(diario):'),
    ('M19_revogada_no_contrato_vale', 'e',
     "if e.get('REVOGADA') is not False or",
     "if e.get('REVOGADA') is True or"),
    ('M20_sem_excecao_passa_igual', 'e',
     "    if e is None:\n        return False, '%s · sem a excecao",
     "    if False:\n        return False, '%s · sem a excecao"),
    ('M21_excecao_removida_da_guarda', 'f',
     "    return True, ('EXCECAO %s (%s)",
     "    return False, ('EXCECAO %s (%s)"),
    ('M22_ambito_exato_ignorado', 'e',
     '        if any(ambito.get(k) != v for k, v in AMBITO_EXATO.items()):\n            return None\n',
     ''),
    ('M23_consumido_em_aceite', 'auditor-L08',
     '    if _tem_consumido_em(pedido):',
     '    if False:'),
    ('M24_o_codigo_passa_a_conhecer_producao', 'b',
     "DESTINOS_DO_PREVIEW = ('BUILD_LOCAL', 'VERCEL_PREVIEW')",
     "DESTINOS_DO_PREVIEW = ('BUILD_LOCAL', 'VERCEL_PREVIEW', 'PRODUCAO')"),
    ('M25_destino_ilegivel_vira_vazio', 'b',
     "    if not isinstance(d, dict):\n        return False, '%s · destino ilegivel",
     "    if not isinstance(d, dict):\n        d = {}\n    if False:\n        return False, '%s · destino ilegivel"),
    ('M26_redteam_lab_inexistente_aceite', 'red-team-1',
     "        return 'a prova do LAB %r nao existe' % lab.get('ONDE')",
     '        return None'),
    ('M30_redteam_c8_texto_livre_aceite', 'red-team-2',
     '            elif decisao_registada(c8, diario)[0] is None:',
     '            elif False:'),
    ('M31_c8_revogado_aceite', 'red-team-2',
     '    if _revogada_no_diario(ident, diario, sec):',
     '    if False:'),
    ('M32_c8_que_nao_e_do_dono_aceite', 'red-team-2',
     "    if not re.search(r'\\bdono\\b', sec, re.I):",
     '    if False:'),
    ('M33_c8_com_id_no_meio_do_texto', 'red-team-2',
     "    m = re.match(r'\\s*(D\\d{2,4})\\b', str(c8 or ''))",
     "    m = re.search(r'(D\\d{2,4})\\b', str(c8 or ''))"),
    ('M34_redteam_read_only_sem_copia', 'red-team-3',
     "        return 'READ_ONLY sem prova: falta a copia/snapshot da Sala'",
     '        return None'),
    ('M35_copia_inexistente_aceite', 'red-team-3',
     "        return 'READ_ONLY sem prova: a copia/snapshot da Sala nao existe'",
     '        return None'),
    ('M36_sha_da_copia_nao_conferido', 'red-team-3',
     '    if len(declarado) != 64 or _sha256_ficheiro(f) != declarado:',
     '    if False:'),
    ('M37_pote_nao_ligado_a_copia', 'red-team-3',
     '    if not isinstance(corte, dict) or declarado not in {str(v).lower() for v in _valores(corte)}:',
     '    if not isinstance(corte, dict):'),
    ('M38_entrada_na_sala_viva_aceite', 'red-team-3',
     '        if _aponta_a_sala_viva(ent.get(k)):',
     '        if False:'),
    ('M39_corte_sem_read_only_aceite', 'red-team-3',
     "    if ro is not None and not str(ro).lower().startswith('on'):",
     '    if False:'),
    ('M40_branch_real_diferente_aceite', 'adendo',
     '        if normalizar_ramo(real) != normalizar_ramo(ramo):',
     '        if False:'),
    ('M41_branch_nao_medida_vira_prova', 'adendo',
     "        if not real:\n            return 'a branch real nao se consegue medir",
     "        if not real:\n            return None, []\n        if False:\n            return 'a branch real nao se consegue medir"),
    ('M43_deployment_mudo_aceite', 'adendo',
     '    if not isinstance(dep, dict):\n        return (',
     '    if not isinstance(dep, dict):\n        return None, []\n    if False:\n        return ('),
    ('M45_deployment_de_outra_branch_aceite', 'adendo',
     '    if normalizar_ramo(src) != normalizar_ramo(ramo):',
     '    if False:'),
    ('M46_consumido_em_so_no_topo', 'auditor-L08',
     "        return any('consumido_em' in str(k).casefold() or _tem_consumido_em(v) for k, v in x.items())",
     "        return any('consumido_em' in str(k).casefold() for k in x)"),
    ('M47_d140_revogada_no_diario_vale', 'auditor-L11',
     '    return not _revogada_no_diario(AUTORIDADE_PREVIEW, diario,',
     '    return True or not _revogada_no_diario(AUTORIDADE_PREVIEW, diario,'),
    ('M48_d140_citada_no_meio_do_texto_vale', 'auditor-L11',
     '    if not any(linha.startswith(MARCA_NO_DIARIO) for linha in diario.splitlines()):',
     '    if MARCA_NO_DIARIO not in diario:'),
    ('M49_branch_sem_normalizar', 'auditor-L04-06',
     '    r = ramo.strip().casefold()',
     '    r = ramo'),
    ('M50_branch_sem_tirar_prefixos', 'auditor-L04-05',
     '            if r.startswith(pre):',
     '            if False:'),
    ('M51_branch_sem_casefold', 'auditor-L06',
     '    r = ramo.strip().casefold()',
     '    r = ramo.strip()'),
    ('M52_host_que_nao_e_nome_limpo_aceite', 'auditor-L01-03',
     '    if not nome or nome != bruto or porta is not None:',
     '    if not nome:'),
    ('M53_host_sem_normalizar', 'auditor-L02',
     '    bruto = host.strip().casefold()',
     '    bruto = host'),
    ('M54_host_vercel_nao_conferido', 'auditor-L03',
     "    if d.get('TIPO') == 'VERCEL_PREVIEW' and not (host and host.endswith('.vercel.app')",
     "    if False and not (host and host.endswith('.vercel.app')"),
    ('M55_chave_desconhecida_no_topo_ignorada', 'auditor-L09',
     '    estranhas = _chaves_estranhas(pedido, CHAVES_DO_PEDIDO)',
     '    estranhas = []'),
    ('M56_chave_desconhecida_por_dentro_ignorada', 'auditor-L09',
     '        estranhas = _chaves_estranhas(sub, perm)',
     '        estranhas = []'),
    ('M58_lab_fora_da_pasta_do_lab_aceite', 'adendo-LAB',
     '    if not _dentro_de(f, pastas_do_lab):',
     '    if False:'),
    ('M60_lab_sem_sha_fixado_aceite', 'adendo-LAB',
     '    if len(fixado) != 64 or _sha256_ficheiro(f) != fixado:',
     '    if False:'),
    ('M59_pote_do_produtor_na_pasta_do_lab_aceite', 'LB5',
     '    if pote_ficheiro and _dentro_de(pote_ficheiro, pastas_do_lab):',
     '    if False:'),
    ('M16_prova_do_lab_nem_conferida', 'd',
     "    problema = conferir_prova_do_lab(lab, sha256_do_pote(pote), pote.get('INTELLIGENCE_RUN_ID'),",
     "    problema = None and conferir_prova_do_lab(lab, sha256_do_pote(pote), pote.get('INTELLIGENCE_RUN_ID'),"),
    ('M27_versao_mais_recente_FAIL_aceite', 'LB2/VER-a',
     "    if obj.get('VEREDITO') != 'PASS':\n        return 'a prova mais recente",
     "    if False:\n        return 'a prova mais recente"),
    ('M28_sha_do_pote_nao_comparado', 'LB1',
     "if obj.get('POTE_SHA256') != sha_canonico or run_id is None or obj.get('RUN_ID') != str(run_id):",
     "if run_id is None or obj.get('RUN_ID') != str(run_id):"),
    ('M57_run_id_nao_comparado', 'LB4',
     "if obj.get('POTE_SHA256') != sha_canonico or run_id is None or obj.get('RUN_ID') != str(run_id):",
     "if obj.get('POTE_SHA256') != sha_canonico or run_id is None:"),
    ('M62_lab_origin_ignorado', 'LB6',
     "    if obj.get('LAB_ORIGIN') != LAB_ORIGIN:",
     '    if False:'),
    ('M63_lab_origin_igual_ao_produtor_aceite', 'LB6',
     "    if str(obj.get('LAB_ORIGIN')).strip().casefold() in {str(x).strip().casefold() for x in produtores if x}:",
     '    if False:'),
    ('M64_texto_solto_volta_a_valer', 'LB1',
     "        return 'a prova do LAB nao e estruturada (JSON): texto solto nao prova nada'",
     "        obj = {'POTE_SHA256': sha_canonico, 'RUN_ID': str(run_id), 'VEREDITO': 'PASS', 'LAB_ORIGIN': LAB_ORIGIN, 'ENVELOPE_HASH': envelope or ENVELOPE_INEXISTENTE}"),
    ('M65_lista_lida_pela_ultima_entrada', 'LB2',
     "    if not isinstance(obj, dict):\n        return 'a prova do LAB nao e UM objeto",
     "    if not isinstance(obj, dict):\n        obj = obj[-1] if isinstance(obj, list) and obj else {}\n    if False:\n        return 'a prova do LAB nao e UM objeto"),
    ('M66_veredito_fora_de_PASS_FAIL_aceite', 'formato-real',
     "    if obj.get('VEREDITO') not in ('PASS', 'FAIL'):",
     '    if False:'),
    ('M67_produtores_do_pote_esquecidos', 'LB6',
     '_produtores_do_pote(pote), _envelope_do_pote(pote))',
     '(), _envelope_do_pote(pote))'),
    ('M68_envelope_nao_conferido', 'formato-real',
     "    if obj.get('ENVELOPE_HASH') != esperado:",
     '    if False:'),
    ('M69_envelope_do_pote_esquecido', 'formato-real',
     '_produtores_do_pote(pote), _envelope_do_pote(pote))',
     '_produtores_do_pote(pote), None)'),
    ('M70_nome_da_prova_nao_conferido', 'formato-real',
     '    if _versao_do_nome(os.path.basename(f), sha_canonico, run_id) is None:',
     '    if False:'),
    ('M71_mais_recente_pela_ordem_do_nome', 'VER-b',
     '    no_topo = [(c, v) for q, c, v in versoes if q == ultima]',
     '    no_topo = [(c, v) for q, c, v in versoes][-1:]'),
    ('M72_empate_de_data_aceite', 'VER-c',
     '    if len(no_topo) > 1:',
     '    if False:'),
    ('M73_prova_antiga_vale_com_uma_mais_recente', 'VER-a',
     '    if os.path.normcase(os.path.realpath(caminho)) != os.path.normcase(os.path.realpath(f)):',
     '    if False:'),
    ('M75_versao_irma_de_outro_par_ignorada', 'VER',
     "            return 'a versao %s tem o nome deste par e o conteudo de outro: FAIL' % nome",
     '            continue'),
    ('M76_versao_menos_1_ou_menos_02_aceite', 'formato-real',
     '        if meio.isdigit() and int(meio) >= 2 and str(int(meio)) == meio:',
     '        if meio.isdigit():'),
    ('M77_nome_sem_distinguir_caixa', 'formato-real',
     "    if nome == base + '.json':",
     "    if nome.lower() == (base + '.json').lower():"),
    ('M78_data_utc_sem_validar', 'VER-data',
     '    if not isinstance(valor, str) or not valor.strip():\n        return None',
     '    if not isinstance(valor, str) or not valor.strip():\n        from datetime import datetime as _d\n        return _d(2000, 1, 1, tzinfo=timezone.utc)'),
    ('M29_marca_de_rejeicao_ignorada', 'K2',
     '    if _tem_marca_de_rejeicao(obj):',
     '    if False:'),
    ('M79_rejeicao_so_em_maiusculas_e_no_topo', 'K2',
     "        return any('rejeit' in str(k).casefold() or _tem_marca_de_rejeicao(v) for k, v in x.items())",
     "        return any('REJEIT' in str(k) for k in x)"),
    ('M80_chaves_da_prova_abertas', 'K1',
     '    estranhas = sorted(k for k in obj if k not in CHAVES_DA_PROVA_DO_LAB)',
     '    estranhas = []'),
    ('M83_elos_em_falta_aceites', 'K4',
     '        if not isinstance(elos, dict) or any(e not in elos for e in ELOS_DA_PROVA):',
     '        if not isinstance(elos, dict):'),
    ('M84_so_FALHOU_conta_como_elo_mau', 'K4',
     '        maus = sorted(k for k, v in elos.items() if v not in ELO_QUE_PASSA)',
     "        maus = sorted(k for k, v in elos.items() if v == 'FALHOU')"),
    ('M87_versoes_sem_descer_nas_subpastas', 'V4b',
     '        for pasta, _subs, nomes in os.walk(r):',
     '        for pasta, _subs, nomes in [next(os.walk(r))]:'),
    ('M74_versao_sem_data_ignorada_em_silencio', 'VER-data',
     "            return 'a versao %s da prova deste par tem DATA_UTC ausente ou invalida: FAIL' % nome",
     '            continue'),
    ('M85_versao_no_futuro_aceite', 'V3c',
     '    for q, c in futuras:',
     '    for q, c in []:'),
    ('M86_versoes_so_na_pasta_do_pedido', 'V4a',
     '    caminhos, anomalias = _provas_do_par(pastas_do_lab, sha_canonico, run_id)',
     '    caminhos, anomalias = _provas_do_par([os.path.dirname(f)], sha_canonico, run_id)'),
    ('M88_tolerancia_ajuda_a_vencer_outra', 'V3c',
     '    sozinha = (len(versoes) == 1 and',
     '    sozinha = (len(versoes) >= 1 and'),
    ('M89_futuro_da_propria_sem_teto', 'V3c',
     '        if not (sozinha and q <= agora + timedelta(seconds=TOLERANCIA_DO_RELOGIO_S)):',
     '        if not sozinha:'),
    ('M90_anomalias_ignoradas', 'V4d',
     '    if anomalias:',
     '    if False:'),
    ('M91_par_citado_pelo_nome_ignorado', 'V4d',
     '                cita = base in nome.casefold()',
     '                cita = False'),
    ('M92_par_citado_pelo_conteudo_ignorado', 'V4d',
     "                    cita = (isinstance(v, dict) and v.get('POTE_SHA256') == sha_canonico",
     "                    cita = False and (isinstance(v, dict) and v.get('POTE_SHA256') == sha_canonico"),
]


def _sha(caminho):
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _correr_suite():
    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = tempfile.mkdtemp(prefix="mut-l1-")
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        env[k] = "http://127.0.0.1:9"
    r = subprocess.run([sys.executable, "-m", "unittest", SUITE], cwd=RAIZ, env=env,
                       capture_output=True, text=True, timeout=600)
    return r.returncode == 0, r.stderr


def main(argv):
    with open(ALVO, "rb") as f:
        original = f.read()
    sha0 = _sha(ALVO)
    texto = original.decode("utf-8")
    # checkout Windows com core.autocrlf=true: a lei vem em CRLF (nota do auditor)
    nl = "\r\n" if "\r\n" in texto else "\n"

    passou, _ = _correr_suite()
    if not passou:
        print("ABORTA: a suite ja reprova sem mutante nenhum; nao se prova nada assim.")
        return 2

    res = []
    for nome, pergunta, antes, depois in MUTANTES:
        antes, depois = antes.replace("\n", nl), depois.replace("\n", nl)
        n = texto.count(antes)
        if n != 1:
            res.append({"MUTANTE": nome, "PERGUNTA": pergunta, "ESTADO": "NAO_APLICADO",
                        "PORQUE": "o trecho aparece %d vezes" % n})
            continue
        try:
            with open(ALVO, "wb") as f:
                f.write(texto.replace(antes, depois).encode("utf-8"))
            vivo, erro = _correr_suite()
        finally:
            with open(ALVO, "wb") as f:
                f.write(original)
        falhas = [l.split(" (")[0].replace("FAIL: ", "").replace("ERROR: ", "")
                  for l in erro.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res.append({"MUTANTE": nome, "PERGUNTA": pergunta,
                    "ESTADO": "SOBREVIVEU" if vivo else "MORTO", "MORTO_POR": falhas[:5]})
        print("%-40s (%s) %s" % (nome, pergunta, res[-1]["ESTADO"]))

    desfeito = _sha(ALVO) == sha0
    mortos = sum(1 for r in res if r["ESTADO"] == "MORTO")
    saida = {"ALVO": "leis/fundacao_da_coleta.py", "SHA256_DO_ALVO": sha0, "SUITE": SUITE,
             "MUTANTES": len(MUTANTES), "MORTOS": mortos, "DESFEITO_E_CONFERIDO": desfeito,
             "RESULTADOS": res}
    print("MORTOS %d/%d · alvo desfeito e conferido: %s" % (mortos, len(MUTANTES),
                                                           "SIM" if desfeito else "NAO <-- GRAVE"))
    if len(argv) > 1:
        with open(argv[1], "w", encoding="utf-8") as f:
            json.dump(saida, f, ensure_ascii=False, indent=1)
    return 0 if (mortos == len(MUTANTES) and desfeito) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
