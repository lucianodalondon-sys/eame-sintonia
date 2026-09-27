ANÁLISE INDEPENDENTE — IDENTIDADE DO CRUZAMENTO

Escopo: li integralmente o PACOTE.md e conferi, só por leitura, os trechos de Git citados. Não abri a Sala nem li respostas de outros analistas. [M] A linha viva local está em 18461b92d; nela, a Bíblia da Intelligence é V0.3. O ramo 21cc06c0 contém a V0.4, que acrescenta as leis 078 e 079. Portanto, trato essas duas leis como regra presente no ramo medido e decisão relatada no pacote, mas não digo que já estejam na linha viva. [M: BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:3-10 @18461b92d e @21cc06c0; diff entre esses refs]

Diagnóstico

[M: PACOTE.md:38-49] Os IDs atuais de SIGNAL, FUTURO e parte dos CROSSING incluem corrida, posição ou origem. Na comparação informada de R6 com R7, 43 objetos tinham o mesmo conteúdo de prova e IDs diferentes. O pote só impede repetição do mesmo ID dentro de um compartimento da mesma corrida; não reconcilia corridas. [M: pacote/pote_intelligence_casco.py:466-468,566-568 @8982ce40e]

[INF] Isso prova um defeito de continuidade da identidade, mas não prova que todo cartão parecido deva ser fundido. Os 13 PORTFOLIO_MATCH de olivo × mosca podem ser uma pergunta geral recorrente e, simultaneamente, aplicações territoriais ou temporais distintas. Transformá-los cegamente em uma só resposta perderia informação. O caso FOLPET × vite mostra outro perigo: estados diferentes em boletins diferentes não podem ser resolvidos escolhendo o cartão mais otimista. [M do pacote, não recontado: PACOTE.md:50-66]

P1 — Chave por família

[HIP] Separaria três identificadores que hoje tendem a ser confundidos:

1. ID da pergunta recorrente: “que questão estamos acompanhando?”. Serve para navegação; não é uma resposta nem uma chave de cache.
2. ID do episódio: a aplicação da pergunta a um escopo factual comprovado — lugar, intervalo, cultura/alvo e, quando pertinente, produto. É a identidade do cruzamento que pode receber provas adicionais.
3. ID da avaliação: resposta produzida numa execução, com provas, edição da referência oficial, regras e configuração usadas. Uma nova avaliação não apaga a anterior.

Isso respeita a distinção legal entre CROSSING, SIGNAL, FINDING e OPPORTUNITY; e a Bíblia já avisa que “parece a mesma pergunta” não basta para reutilizar uma resposta. [M: BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:256-280,304-318,411-419 @21cc06c0; as mesmas leis preexistentes permanecem na V0.3]

[HIP] Chaves candidatas — sujeitas a teste com os objetos reais:

- Rótulo × substância citada: pergunta regulatória por produto/registro, uso declarado — cultura e alvo quando exigido —, jurisdição e escopo de validade. A edição da bula pertence obrigatoriamente à avaliação e à prova; mudança material de registro ou de escopo abre episódio distinto e liga-o ao anterior. A menção da substância num boletim é outra prova/aresta: não autoriza, sozinha, o uso de um produto. É preciso consultar a edição aplicável da referência oficial. [M: PACOTE.md:92-100; BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:1816-1829 @21cc06c0]
- PORTFOLIO_MATCH: cultura canônica × alvo canônico × jurisdição, com produto/registro quando a pergunta for “qual produto cobre o par”; para decisão de campo, acrescentar território e episódio temporal comprovados. “Existe registro?” e “tratar aqui agora?” são perguntas diferentes. [M: BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:1758-1769 @21cc06c0; supabase/migrations/005_camada_analitica_observado_vs_derivado.sql:3-9,65-80 @18461b92d]
- COMPETITIVE_SET: declarar primeiro o grão. Uma relação por produto concorrente e registro não é a mesma coisa que um agrupamento por substância; preservar o vínculo ao produto/uso da ADAMA efetivamente comparado. Os 122 PRODUCT_ID distintos entre 125 objetos impedem chamar o conjunto inteiro de “duplicata”. [M do pacote: PACOTE.md:59-61; motor/cruzamentos_max.py:1038-1049 @399e79f8a]
- Janela olivo × mosca: cultura × alvo × lugar do fato × estágio fenológico × janela factual. Isso acompanha as chaves já previstas para CAP-WIN. [M: BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:1841-1855 @21cc06c0]
- Futuro: questão/evento tipado × lugar comprovado × horizonte da previsão. Previsões de horizontes diferentes não são o mesmo fato; o identificador atual dependente de RUN não serve como identidade entre corridas. [M: PACOTE.md:39,86-88; BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:1781-1794 @21cc06c0]

[HIP] Igualdade de chave só após normalização comprovada e versionada. “Mosca” isolada continua ambígua; “drupacee” não vira uma cultura específica; comune, província e região podem ter relação de abrangência, mas não são a mesma chave. “Zona costeira” não resolvida conserva a expressão original, sem ganhar um código geográfico inventado. Intervalos sobrepostos também não são automaticamente o mesmo episódio: sobreposição não é uma regra segura de equivalência. [M: PACOTE.md:102-113; BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:549-571,579-585,615-619 @21cc06c0] O PostgreSQL dispõe de tipos de intervalo e operadores de sobreposição, mas isso resolve comparação técnica de intervalos, não a decisão agronômica de identidade: https://www.postgresql.org/docs/16/rangetypes.html

[HIP] Faltou chave indispensável ou ela está em conflito? Não gerar ID canônico por `NAO SEI`, vazio, nome parecido, local da fonte ou data de publicação. Guardar candidato ligado à observação e ao motivo do bloqueio; não fundir com outros candidatos desconhecidos. [M: BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:579-585,615-619,822-832 @21cc06c0]

P2 — Setembro versus outubro

[HIP] Mesma pergunta recorrente, mas episódios distintos quando a janela de aplicabilidade muda. Uma série liga os episódios sem transformar setembro em outubro. Se uma bula vigente cobre ambos, a prova regulatória pode ser reutilizada após verificar sua validade; a recomendação agronômica de setembro não é transferida automaticamente. No exemplo ARIF, o FACT_TIME gravado para n.38 diverge do cabeçalho relatado: esse dado precisa de revisão antes de servir de chave temporal. [M do pacote: PACOTE.md:64-66; M: BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:615-647 @21cc06c0]

P3 — Prova e independência

[HIP] Acrescentar vínculos imutáveis de prova ao episódio, cada qual apontando para item/observação/documento, trecho ou campo de origem, papel (“sustenta”, “contraria”, “contextualiza”), versão e execução que criou o vínculo. Contar separadamente aplicações territoriais, originadores independentes e validações estruturais. Republicação ou dois ingressos do mesmo boletim não viram duas confirmações. Divergência entre instituições permanece aberta até comparar escopo; recomendação diferente da mesma instituição em outro período é mudança de recomendação, não prova de mudança no campo. [M: PACOTE.md:62-66; BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:476-526,528-541,587-594 @21cc06c0. Nota: leis 078–079 ainda não constam na V0.3 da linha viva.] Como referência de modelagem, PROV-O distingue entidade, derivação e revisão; não exige instalar uma plataforma: https://www.w3.org/TR/prov-o/

P4 — Estados e reavaliação

[HIP] Não usar um único “SIM/NÃO” para esconder perguntas diferentes. Registrar, ao menos, estado da evidência (suficiente, parcial, conflitante, desconhecida), estado temporal (válido, vencido, desconhecido) e conclusão específica da pergunta. Nova prova, correção append-only da Sala, edição oficial nova, regra de normalização alterada ou passagem dos limites D117 disparam nova avaliação; não sobrescrevem a antiga. A transição leva estado anterior, novo estado, motivo, provas afetadas e versões. Aos 14 dias sem checagem, mostrar possível desatualização; aos 30, autorização “a confirmar”, sem converter isso em “não autorizado”. [M: PACOTE.md:81-100; BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:729-736,1003-1015,1025-1039 @21cc06c0; supabase/migrations/033_a_sala_guarda_a_base_as_chaves_e_as_revisoes.sql:194-243 @18461b92d]

P5 — Composição

[HIP] Finding, Opportunity e Future referenciam IDs e versões das avaliações das quais realmente dependem — não todos os objetos que participaram da mesma corrida. Quando uma avaliação muda, localizar dependentes, marcá-los para reavaliação e publicar nova versão ou retirada justificada; não corrigir retroativamente o julgamento histórico. Proibir ciclos entre derivados ou fazê-los falhar antes da publicação. Para contagem, percorrer a prova até os originadores e contar cada família independente uma vez, não cada caminho do grafo. A especificação OpenLineage recomenda registrar arestas explícitas por saída, justamente para evitar relações falsas entre todo input e todo output de um run: https://openlineage.io/docs/spec/facets/job-facets/lineage . Isso é um padrão transferível, não recomendação de adotar OpenLineage. [M: BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:351-373 @21cc06c0]

P6 — Livro, pote e casco

[HIP] Manter o pote como fotografia de uma corrida, mas tornar o livro de identidades e avaliações responsabilidade exclusiva da Intelligence no PostgreSQL já existente — em estrutura própria e com permissões próprias, sem fazer da tabela de revisões da Sala um escritor de Intelligence. Um arquivo JSON pode ser exportação auditável, não a autoridade concorrente. Não afirmo que essa estrutura já exista: nas migrações locais examinadas não encontrei uma tabela específica de identidade de CROSSING; não consultei o banco vivo. A migração 005 contém uma tabela `derivacao`, porém seu próprio cabeçalho diz “NÃO EXECUTADA” e ela não prova resolver a identidade proposta. [M: supabase/migrations/005_camada_analitica_observado_vs_derivado.sql:11-16,43-63 @18461b92d; PACOTE.md:92-100]

[HIP] Delta mínimo por objeto: `OBJETO_ID`, `AVALIACAO_ANTERIOR`, `AVALIACAO_NOVA`, `TIPO` (entrou, prova acrescentada, conclusão mudou, saiu justificadamente), `MOTIVO`, `RUN_ANTERIOR`, `RUN_ATUAL`. A Intelligence o calcula a partir de duas publicações consecutivas confirmadas; o casco apenas mostra. Corrida parcial, falha ou ausência de item numa entrada incompleta não autorizam “saiu”. A gravação do estado e a escolha da versão publicada precisam de controle de concorrência e repetição segura: conferir antes não basta para impedir duas corridas simultâneas de criarem a mesma identidade. PostgreSQL documenta `ON CONFLICT` para o conflito de chave e a necessidade de tratar corretamente transações concorrentes: https://www.postgresql.org/docs/16/sql-insert.html e https://www.postgresql.org/docs/16/transaction-iso.html .

[M] O schema v2 não proíbe expressamente campos extras, mas o gerador monta campos fixos no topo e o leitor atual não interpreta DELTA. Logo “o JSON aceita” não significa “funciona no casco”: seriam necessárias mudança contratada, geração, validação e teste do consumidor, sem transferir cálculo para o navegador. [M: docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json:6-24 @8982ce40e; pacote/pote_intelligence_casco.py:390-404,560-575 @8982ce40e; italia-portale/client/sintonia-pote-casco.js:1-17,80-97 @60ee56b2c]

P7 — Migração

[HIP] Preservar XC-, XMAX-, SG- e FUT- como IDs legados e provar uma correspondência `ID_LEGADO → episódio/avaliação`, com grau de certeza e motivo. Não recalcular os IDs antigos nem declarar equivalência só porque o texto é parecido. Correspondência ambígua fica sem fusão automática. Testar especialmente R6/R7, os dois FOLPET e os boletins ARIF. Para IDs novos, esperar o critério aprovado pelo dono; D119 proíbe uma equipe de inventar o esquema antes da conclusão. [M: PACOTE.md:38-49,56-66,99-100; BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:1037-1039 @21cc06c0]

P8 — Antes da publicação de hoje

[HIP] Não introduzir apressadamente um novo ID “definitivo”, uma fusão automática ou um delta que ninguém testou. Cumprir D119: marcar IDs novos como provisórios e impedir que cartões com conclusões diferentes pareçam uma única autorização confirmada. Se não houver tempo para revisão, apresentar o recorte como experimental ou reter essa resposta, mantendo as provas visíveis; decisão de publicação é do dono. [M: PACOTE.md:56-60,99-100]

[M] Há uma divergência a esclarecer antes de afirmar que “o pote já alimenta o portal público”: o código do ramo do casco só solicita o pote com `?pote=local`, diz que o arquivo gerado fica fora do deploy e o marca `EXPERIMENTAL · NAO_PARA_CLIENTE`. D114 no pacote expressa a intenção de ir ao ar hoje; estes trechos não provam que o pote esteja público ou que o problema já apareça para clientes. [M: italia-portale/client/sintonia-pote-casco.js:1-29 @60ee56b2c; PACOTE.md:13-14]

Menor teste e veredito

[HIP] TESTAR, fora da produção: reconciliar R6/R7 e os casos FOLPET, olivo × mosca e ARIF com uma tabela de decisões feita à mão. Reexecutar a mesma entrada, mudar a ordem dos itens, acrescentar uma prova, corrigir uma data, trocar uma edição da bula e simular uma corrida incompleta. Sucesso: identidade persistente somente quando todas as dimensões essenciais forem equivalentes; nenhuma prova perdida; nenhuma confirmação falsa; histórico e delta reproduzíveis; duas execuções iguais sem cartões novos. Falha: qualquer fusão de territórios/tempos distintos, separação injustificada dos mesmos episódios, “saiu” por corrida incompleta ou autorização derivada apenas de substância. Ainda não executei esse teste. [HIP] Veredito: TESTAR, não PRONTO PARA PROPOR uma migração ou publicação automática.

CONTENT_CLASSIFICATION: KNOW_HOW = YES (método e defeito de reconciliação candidatos); ITALIAN_AGRO_BRAIN = NO (nenhum fato agronômico novo validado); BIBLE_CHANGE = NO (eventuais regras de identidade são candidatas, não decisão do dono); HANDOFF_ONLY = YES (diferença entre ramo V0.4 e linha viva V0.3 e pendência D119). Nada foi escrito nessas casas.

RECOMENDAÇÃO EM 10 LINHAS

1. Não chamar ID de corrida de identidade permanente.
2. Separar pergunta recorrente, episódio factual e avaliação versionada.
3. Usar chaves próprias por família, nunca uma fórmula universal.
4. Exigir lugar, tempo e entidades provados antes de fundir episódios.
5. Conservar NÃO SEI como bloqueio, não como valor de igualdade.
6. Acumular provas sem multiplicar artificialmente fontes independentes.
7. Registrar cada mudança de conclusão sem apagar o julgamento anterior.
8. Fazer a Intelligence produzir fotografia e delta; o casco só os mostra.
9. Hoje, manter IDs provisórios e não publicar confirmação nascida de fusão incerta.
10. Aprovar um esquema definitivo apenas após o teste R6/R7 e decisão do dono.

ONDE POSSO ESTAR ERRADO

- [INF] Os 43 objetos “de mesmo conteúdo” usam uma assinatura resumida informada no pacote; campos relevantes não incluídos nela podem mostrar que alguns não são equivalentes. [M: PACOTE.md:44-47]
- [INF] Os 13 olivo × mosca talvez pertençam a escopos distintos; sem lugar e janela de cada um, NÃO SEI quantos devem realmente virar um episódio. [M: PACOTE.md:59-60]
- [INF] Não medi o banco vivo nem o deploy. Pode já existir mecanismo fora das migrações e ramos lidos; NÃO SEI. 
- [HIP] A separação em três IDs pode ser complexidade demais para o primeiro piloto; se uma chave de episódio mais versões de avaliação resolver os casos, prefiro a alternativa menor.
- [INF] A Bíblia V0.4 está num ramo medido, mas não na linha viva local; sua promoção operacional precisa ser conferida, não presumida.

EM PALAVRAS SIMPLES

Hoje o sistema pode dar um nome novo à mesma informação a cada rodada. Isso dificulta perceber que chegou uma prova nova para algo já acompanhado. A solução provável é dar um endereço duradouro à pergunta situada no lugar e no período corretos, guardar cada resposta com suas provas e mostrar o que mudou. Mas juntar cartões apenas porque parecem iguais também pode produzir uma resposta errada. Antes de colocar essa união na tela pública, precisamos testar casos reais e deixar como “provisório” o que ainda não sabemos identificar com segurança. Nenhum arquivo do projeto foi alterado por esta análise.
