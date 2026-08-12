# Metodologia — Identificação do Sistema de Ensino das Golden Leads (Roadmap 3.0)

Bônus pós-entrega formal (tag `entrega-formal-23-07`, commit `b151aed`). Objetivo: para cada uma das 1.127 Golden Leads, descobrir se ela já usa um sistema de ensino licenciado (Anglo, Bernoulli, SAS, Positivo etc.) e, principalmente, **mapear clientes ocultos do próprio Poliedro** — escolas que já usam o sistema Poliedro sob outra marca/identidade visual, não capturadas pelo filtro de nome do Censo.

**Status atual (29/07/2026): 100% das 1.127 Golden Leads têm uma classificação final** — 722 `confirmado`, 302 `provavel_proprio`, 103 `não identificado` (evidência insuficiente, não lacuna de trabalho — ver seção 5). **62 escolas já são clientes do Sistema Poliedro sob qualquer marca** (4 com "Poliedro" no próprio nome do Censo + 58 clientes ocultos achados só pela pesquisa manual). Duas fases de trabalho, com métodos diferentes — ver seção 8 para a fase mais recente (a que fechou a lacuna de ~728 para 103 "não identificado").

Coluna gerada: `sistema_ensino_identificado` em `data/outputs/14_escolas_powerbi.csv`, junto com `confianca` (não `confianca_sistema_ensino` — nome de coluna corrigido nesta revisão) e `fonte_resumo` (justificativa/evidência, não `fonte_sistema_ensino`). Coluna derivada `ja_cliente_poliedro_qualquer_marca` (também em `14_escolas_powerbi.csv`) combina esse achado com a flag por nome do Censo (`rede_propria_poliedro`) num único filtro. Registro-fonte: `poliedro_19_sistema_ensino_identificado.py`, dicionário `REGISTROS` (`codigo_escola → (sistema, confiança, fonte)`).

## 1. Por que existe uma etapa de busca paga (Serper.dev) no meio do caminho

As primeiras ~180 escolas (líderes locais + maiores scores) foram pesquisadas uma por uma via WebSearch, sem custo. Para escalar às 1.127 inteiras, avaliamos alternativas de busca em lote:

- **Google Custom Search API**: descartada — fechada para novos usuários desde 2025, desligamento definitivo em jan/2027.
- **Tavily**: descartada — empacota extração de conteúdo (IA) que não precisávamos pagar, já que quem classifica é o Claude, não a API (~8x mais caro que a alternativa escolhida).
- **Serper.dev**: escolhida — proxy puro do resultado do Google, com parâmetros de país/idioma (`gl=br`, `hl=pt-br`), ~$0,30-1/1000 consultas, 2.500 grátis sem cartão.

Descoberta técnica: o sandbox onde o Claude roda tem uma lista de permissão de rede (`allowlist`) que bloqueia chamadas diretas a `google.serper.dev`, `api.tavily.com` e ao próprio `google.com` — confirmado testando cada domínio via `curl` (todos voltaram `403 Forbidden`). Não há como contornar isso a partir do ambiente do Claude; a solução foi Gui rodar o script localmente (`poliedro_20_buscar_sistema_ensino_serper.py`), salvar o CSV de snippets, e o Claude ler/classificar o resultado.

### 1.1. Correção de viés na query (achado do Gui, 24/07)

A primeira versão do script listava marcas específicas dentro do próprio termo de busca (`"SAS" OR "Bernoulli" OR "Anglo"...`). Gui identificou o problema: **isso enviesa o próprio Google a devolver só o que já sabíamos existir, em vez de deixar a escola se identificar**. Corrigido para termos genéricos de categoria (`"sistema de ensino" OR "material didático" OR "apostila"...`) — cada sistema real se encaixa em pelo menos um termo, mas a query não pressupõe qual é a resposta. O cache inteiro foi invalidado e a busca refeita do zero com a query corrigida, para manter o dataset metodologicamente consistente (não só corrigir daqui pra frente).

### 1.2. Rate limit e cache

Erro inicial: 697 de 947 chamadas retornaram "429 Rate limit exceeded" — causa raiz era `CONCORRENCIA_MAXIMA=10` disparando tudo de uma vez, sem espaçamento, contra o limite de 5 req/s do plano gratuito do Serper (confundir "limite de concorrência" com "limite de taxa de disparo"). Corrigido com um `LimitadorDeTaxa` (token-bucket, 4 req/s) + cache em disco por escola (nunca repete uma chamada já bem-sucedida ou com erro definitivo; só re-tenta especificamente erros 429).

## 2. Triagem — de 946 snippets brutos a 3 arquivos de trabalho

Ler 946 snippets um por um seria lento demais. Dividimos por regex em 3 baldes, sem viés (mesma lógica de "não adivinhar" da correção da query):

| Arquivo | Critério | Tamanho | Tratamento |
|---|---|---|---|
| `20d_sem_sinal_nenhum.csv` | Nenhuma palavra-chave de sistema nem indício de material próprio/confessional no snippet | 419 | Registradas em bloco como `não identificado` — é evidência de ausência, não atalho: a busca não trouxe nada, então não há o que confirmar. |
| `20c_com_sinal_proprio.csv` | Indício de material próprio/confessional (ex.: "material didático próprio", nome de congregação) | 64 | Lidas individualmente, 1 leva. |
| `20b_com_sinal_sistema.csv` | Presença de nome de sistema conhecido no snippet | 449 | Lidas individualmente, uma a uma, em 9 levas de ~50 — a maior parte do trabalho, porque é onde mora o risco de erro (ver seção 3). |

## 3. Regras de classificação (a parte que evita erro caro)

### 3.1. Hierarquia de qualidade da evidência

1. **Fonte primária oficial** (lista de material da própria escola, PDF de matrícula) — mais forte.
2. **Campo estruturado de diretório** (ex.: melhorescola.com.br tem um campo literal "Sistema de ensino: X") — muito confiável, formato padronizado.
3. **Declaração direta no próprio domínio/rede social da escola** — confiável se inequívoco.
4. **Trecho ambíguo de lista/ranking agregado** (OBMEP, ENEM, diretório de bairro) — risco alto, tratado com máxima cautela (ver 3.2).

### 3.2. Risco de "list-adjacency" (a lição mais cara do processo)

A maior parte do tempo gasto nas 9 levas foi descartando falsos positivos desse tipo: um nome de sistema aparece no mesmo trecho de busca, mas pertence à escola VIZINHA numa lista de premiados, ranking de ENEM ou diretório — não à escola-alvo. Regra: só confirmar quando o texto amarra explicitamente o nome do sistema ao nome da escola-alvo; qualquer ambiguidade genuína vira `não identificado`, nunca uma suposição otimista.

**Erro real que gerou essa regra**: o Claude chegou a afirmar em chat (não commitado) que o Colégio Santo Antônio (BH) usava "Sistema Fibonacci", baseado num trecho ambíguo do Instagram. Gui subiu a lista oficial de material da 3ª série do colégio — livros avulsos de Moderna/Ática/SM/Saraiva, várias disciplinas com "material a ser fornecido pelo professor" — provando que não há sistema fechado ali. Corrigido antes de qualquer commit, e a lição (fonte primária > trecho de rede social ambíguo) ficou documentada no próprio código.

### 3.3. Reaproveitamento de rede — só em 2 casos específicos

Nunca aplicado por padrão. Só é seguro presumir que a unidade B usa o mesmo sistema da unidade A (mesma rede) quando:

- **(a) é fato institucional/estrutural**: ex. toda a Rede Marista usa material FTD exclusivo nacionalmente (confirmado e reaplicado a 35 unidades); Sistema Mackenzie de Ensino é produzido pela própria Universidade Presbiteriana Mackenzie para as escolas Presbiterianas Mackenzie da rede.
- **(b) ≥2 unidades da mesma marca já confirmam o mesmo sistema, de forma independente.**

**Explicitamente NÃO seguro** para nomes genéricos/comuns (ex.: "Santo Agostinho", "Gabarito", "São José" — usados por congregações/redes totalmente diferentes em cidades diferentes) nem para redes que já mostraram sistemas DIFERENTES entre unidades-irmãs (La Salle apareceu com 3 sistemas diferentes entre 3 unidades: Positivo em Caxias do Sul/Carmo, Conquista Solução Educacional em Canoas, nenhum confirmado em Águas Claras e São João/Porto Alegre — tratado individualmente, sempre).

### 3.4. Validade temporal

Classificação não é permanente. Dois casos documentados nesta rodada: Escola Avance (Tangará da Serra) anunciou publicamente a troca para Sistema COC em 2026; Centro de Ensino Classe A (Porto Velho) anunciou troca futura para Sistema Anglo a partir de 2027. A classificação registrada reflete o sistema em uso na data da busca (24/07/2026), não uma garantia permanente.

## 4. Resultado final (histórico da Fase 1 — 24/07/2026)

Estes números refletem o corte da Fase 1 (busca em lote via Serper, seção 1-3 abaixo). **Superados pela Fase 2 — ver seção 8 e a tabela atualizada logo abaixo.**

| Confiança | Quantidade (24/07) | O que significa |
|---|---|---|
| `confirmado` | 306 | Evidência direta e razoavelmente inequívoca de qual sistema de terceiros a escola usa. |
| `provavel_proprio` | 93 | Evidência de que a escola usa material/metodologia própria (não de terceiros) — nome da própria marca, rede confessional com metodologia documentada, franquia com currículo próprio (ex. Maple Bear). |
| `não identificado` | 728 | Busca não trouxe evidência confiável o suficiente pra confirmar nada — ver seção 5. |

### 4.1. Resultado final ATUAL (29/07/2026, 100% das 1.127 Golden Leads pesquisadas, Fase 1 + Fase 2)

| Confiança | Quantidade | O que significa |
|---|---|---|
| `confirmado` | 722 | Evidência direta e razoavelmente inequívoca de qual sistema de terceiros a escola usa. |
| `provavel_proprio` | 302 | Evidência de que a escola usa material/metodologia própria (não de terceiros) — nome da própria marca, rede confessional com metodologia documentada, franquia com currículo próprio (ex. Maple Bear). |
| `não identificado` | 103 | Busca (agora incluindo navegação direta a sites oficiais, não só snippet de busca) não trouxe evidência confiável o suficiente pra confirmar nada — ver seção 5. Caiu de 728 para 103 na Fase 2. |

### 4.2. Sistemas concorrentes mais encontrados (entre os 722 confirmados)

Além dos números da Fase 1 (Anglo ~44, Bernoulli ~39, Marista/FTD 35, SAS/Ari de Sá ~33, Objetivo 17, COC 15, Positivo 14, FTD 10, pH/SOMOS ~12), a Fase 2 confirmou dezenas de redes adicionais e reforçou padrões de rebranding regional já detectados: mais unidades Anglo (incluindo rebrands regionais como "Anglo Alante", "Anglo Acre", "Anglo Crescer", "Anglo Taubaté"), Sistema Etapa, Coleguium (rede própria de Belo Horizonte, 10+ unidades), Plataforma AZ/Grupo SEB (Rio de Janeiro/Brasília, 5+ unidades), redes confessionais inteiras (Rede ICM, Rede Salesiana, Rede Franciscana/SCALIFRA, Educação Vicentina, Rede Batista, Congregação Scalabriniana, Rede Notre Dame), Sistema Positivo, SAS Plataforma de Educação, Sistema Farias Brito, Fleming Educação, Pensi/Grupo Salta, entre outras.

### 4.3. Clientes Poliedro mapeados — o principal objetivo desta pesquisa

**62 escolas** das 1.127 Golden Leads já usam o Sistema Poliedro — apenas **4 têm "Poliedro" no próprio nome do Censo** (`rede_propria_poliedro`); as outras **58 são clientes ocultos**, sob marca própria/outro nome, só descobertas pela pesquisa manual (Fase 1 + Fase 2). Cada uma tem confirmação direta (site oficial, Instagram da própria escola, ou campo estruturado de diretório) registrada em `fonte_resumo`.

Exemplos de clientes ocultos da Fase 1: Colégio Contato (Maceió — achado original que motivou a mudança de critério), Bosque Mananciais (Curitiba), Colégio Arnaldo (BH), Colégio Oficina (Salvador), Colégio Classe A (Campo Grande e Porto Velho), Vem Ser Colégio (São José do Rio Preto), São José Externato (Atibaia), Canadian School of Niterói, Progressão Colégio (Taubaté/Caçapava/Pindamonhangaba), São José Colégio Agostiniano (SP), entre outros.

Exemplos de clientes ocultos da Fase 2 (achados navegando direto ao site oficial da escola, buscando a expressão "Sistema Poliedro"/"Sistema de Ensino Poliedro" no próprio domínio): **Colégio Status** (Passos/MG — "Status Poliedro 50 Anos"), **Novo Colégio** (Franca/SP — "Portal Edros"/"Banca Poliedro"), **Colégio e Curso Carvalho Braga** (Teresópolis/RJ), **Centro Educacional Delta** (Planaltina/Brasília-DF — Poliedro só no Ensino Médio, Sistema Positivo no Infantil/Fundamental) e **Esquema Único** (Presidente Prudente/SP — opera sob a marca "Colégio Poliedro Esquema Único", indicando ser uma unidade parceira/franqueada formal, não só cliente de material).

Coluna `ja_cliente_poliedro_qualquer_marca` (calculada em `poliedro_14_consolidar_dataset_powerbi.py`) combina esse achado com a flag por nome do Censo (`rede_propria_poliedro`) num único filtro booleano pronto pro Power BI: `rede_propria_poliedro OR sistema_ensino_identificado contém "Poliedro"`.

## 5. O que "não identificado" quer dizer (e o que NÃO quer dizer)

**Não significa** "a escola não usa nenhum sistema" — significa apenas que a busca pública não trouxe evidência confiável o bastante para confirmar qual sistema é. Dentro dos 728, há duas situações bem diferentes:

1. **Ausência real de sinal** (a maioria, ~419 vieram do balde `20d` sem nenhuma palavra-chave de sistema no resultado da busca) — pode ser que a escola realmente não tenha presença digital detalhada sobre isso, ou que de fato não use sistema licenciado.
2. **Sinal presente mas descartado por ambiguidade** (a maior parte do trabalho fino nas 9 levas) — o nome de um sistema apareceu na busca, mas pertencia a outra escola no mesmo ranking/lista agregada (list-adjacency, seção 3.2), ou era homônimo de rede não relacionada, ou a frase estava truncada antes de nomear a marca. Nesses casos, a decisão deliberada foi **não adivinhar** — melhor não confirmar do que confirmar errado.

Ou seja: `não identificado` é o resultado correto e esperado da metodologia quando a evidência não é boa o suficiente — não é uma lacuna de trabalho, é o próprio critério de rigor sendo aplicado. Os **103 casos atuais** (pós Fase 2) passaram pelo mesmo padrão de rigor, agora com navegação direta ao site oficial (não só snippet de busca) — a maioria é escola sem site institucional ativo, ou site que não menciona sistema/material de forma alguma.

## 6. Itens flagados na Fase 1 para revisão futura (histórico — não confirmado se foram revisitados individualmente na Fase 2)

- Confiança média/ambígua a reverificar: Colégio Contemporâneo (Natal), Escola Autonomia (Florianópolis), Colégio Evolução (Juazeiro do Norte), Colégio Mãe de Deus (Porto Alegre, menção ambígua a evento Poliedro), Colégio Lumiere (Dourados, menção ambígua a estatística agregada Poliedro).
- Leblon Santo Agostinho (RJ) tem evidência contraditória de uma unidade-irmã — merece nova checagem individual.
- 2 escolas com "Maxi" no nome (fora as já confirmadas) valem reconsideração agora que "Sistema Maxi" foi confirmado como marca real do Grupo SOMOS.

## 7. Como reproduzir (Fase 1 — busca em lote via Serper)

1. `python poliedro_20_buscar_sistema_ensino_serper.py` — **roda localmente** (sandbox do Claude bloqueia a API), precisa de `data/raw/.serper_key` (nunca versionada). Gera `data/outputs/20_snippets_para_classificar.csv`. Hoje serve principalmente para gerar candidatos: filtra `19_sistema_ensino_identificado.csv` por `confianca == "nao_identificado"` — como esse conjunto caiu para 103 (Fase 2), rodar de novo só é útil se se quiser reabrir esses 103 casos especificamente.
2. Triagem por regex nos 3 baldes (script ad-hoc, não versionado — lógica descrita na seção 2).
3. Classificação manual, linha a linha, seguindo as regras da seção 3 → escrita direto em `REGISTROS` (`poliedro_19_sistema_ensino_identificado.py`).
4. `python poliedro_19_sistema_ensino_identificado.py` — valida e gera `data/outputs/19_sistema_ensino_identificado.csv` com o resumo estatístico.
5. `python poliedro_14_consolidar_dataset_powerbi.py` — propaga pro dataset final do Power BI (recalcula `sistema_ensino_identificado`, `confianca` e `ja_cliente_poliedro_qualquer_marca` em `14_escolas_powerbi.csv` a partir do zero, incluindo o resto do dataset — geo, renda etc. — então também corrige qualquer drift de formatação introduzido por edições manuais no CSV).
6. **Depois do passo 5**, se alguma decisão de negócio depende de `ja_cliente_poliedro_qualquer_marca` (parceiro vs. prospect), rodar também `python poliedro_18_risco_canibalizacao.py`, `python poliedro_24_canibalizacao_parceiros.py` e `python poliedro_26_ranking_local_parceiro.py`, nessa ordem — ver seção 8.3.

## 8. Fase 2 (27-29/07/2026): fechamento manual via navegação direta (Claude in Chrome)

### 8.1. Por que uma segunda fase

A Fase 1 (Serper, seções 1-3) deixou **728 escolas em `não identificado`** — o balde `20d_sem_sinal_nenhum.csv` (sem nenhuma palavra-chave no snippet de busca) sozinho tinha 419. Um snippet de busca é uma janela estreita: se a página da escola não usa a palavra exata "sistema de ensino" perto do nome da marca, ou se o Google simplesmente não indexou aquele trecho, a Fase 1 não tinha como confirmar mesmo quando a informação estava lá, publicada no site oficial. Gui decidiu (27/07) fechar essa lacuna manualmente em vez de aceitar ~65% de cobertura direta como teto, usando navegação de página inteira (não só snippet) via Claude in Chrome.

### 8.2. Método

- **Fila de trabalho**: `data/outputs/21_pesquisa_manual_sistema_ensino.csv` — todo código com `confianca == "nao_identificado"`, com uma busca sugerida pronta (nome + cidade + UF + "lista de material ensino médio 2026"). Processado em lotes de 6, ordenado por `score_destaque` decrescente (prioriza primeiro as escolas de maior valor comercial).
- **Ferramenta**: busca no Bing (não Google — mesma allowlist de rede do sandbox que motivou a escolha do Serper na Fase 1 bloqueia buscas diretas ao Google) via `claude-in-chrome`, 3 abas em paralelo (`browser_batch`), navegando direto ao domínio oficial da escola quando o resultado de busca aponta um.
- **Mesmas regras de rigor da Fase 1** (seção 3): hierarquia de evidência (fonte primária > diretório estruturado > declaração própria > trecho ambíguo de lista agregada), risco de list-adjacency, reaproveitamento de rede só quando institucional/estrutural ou com ≥2 unidades já confirmadas independentemente, validade temporal.
- **Armadilhas de colisão de nome — a lição mais cara desta fase específica**: nomes de escola genéricos ou populares (Santo Agostinho, São José, Instituto São José, Colégio Dinâmico, Colégio Criarte, Colégio Bom Jesus, Colégio Fátima/Senhora de Fátima, Colégio CEI) se repetem em cidades diferentes, pertencendo a redes/mantenedoras completamente distintas. Regra aplicada: sempre confirmar endereço/CEP do site oficial contra o endereço do Censo antes de aceitar a evidência; quando a colisão é real e não dá pra resolver com confiança, a nota "ARMADILHA DE COLISÃO" fica registrada em `fonte_resumo` para a próxima pessoa não cair no mesmo erro.
- **Extrapolação de rede**: quando uma rede já tinha 2+ unidades confirmadas independentemente na Fase 1/2 (ex.: Coleguium, Pensi, Plataforma AZ, Fleming Educação, Rede Inspira), unidades adicionais da mesma marca foram classificadas por extrapolação direta, citando o código da unidade-irmã como evidência — sem precisar reabrir o site de cada unidade individualmente.
- **Checagem antes de sobrescrever**: antes de gravar um achado nesse `REGISTROS`, sempre conferir (via `grep`) se o código já tinha uma entrada de uma sessão anterior — pelo menos um caso (código 43123090) já tinha uma confirmação de cliente oculto Poliedro de sessão anterior que uma pesquisa nova (achando a rede confessional mantenedora) quase sobrescreveu; a entrada mais antiga e mais específica foi preservada.
- **Sincronização em lote, não por escola**: por custo, o ciclo completo (remover do `21`, rodar `poliedro_19`, refazer o merge em `14_escolas_powerbi.csv`) rodou a cada ~6 escolas resolvidas, não a cada uma.

### 8.3. Resultado da Fase 2

`não identificado` caiu de 728 (Fase 1) para **103** (queda de 86%). `confirmado` subiu de 306 para 722; `provavel_proprio` de 93 para 302. Clientes Poliedro de qualquer marca subiram de um total histórico de ~39-49 (marcos intermediários registrados no `README.md`) para **62** — 58 deles clientes ocultos, achados só por essa pesquisa manual.

Como o campo `ja_cliente_poliedro_qualquer_marca` alimenta diretamente os passos de canibalização/ranking de parceiro, a Fase 2 terminou com uma reexecução completa da cadeia downstream (29/07):

1. `python poliedro_14_consolidar_dataset_powerbi.py` — regenerou `14_escolas_powerbi.csv` do zero (também corrigiu um drift de formato: edições manuais incrementais do CSV ao longo da Fase 2 tinham derrapado o separador decimal de `,` para `.` em `LATITUDE`/`LONGITUDE`, quebrando a leitura downstream — resolvido reconstruindo o arquivo pelo pipeline canônico em vez de manter patches manuais).
2. `python poliedro_18_risco_canibalizacao.py` — não usa `ja_cliente_poliedro_qualquer_marca` diretamente (só as 4 unidades próprias por coordenada fixa), mas foi rerrodado por consistência.
3. `python poliedro_24_canibalizacao_parceiros.py` — recalculado com os 62 parceiros: **688 prospects** dividem cidade com algum parceiro (era 308 num marco intermediário anterior); 77 a ≤1km, 113 entre 1-2km, 215 entre 2-5km, 283 a mais de 5km; 42 cidades cobertas.
4. `python poliedro_26_ranking_local_parceiro.py` — recalculado com os 62 parceiros: **51 municípios** com parceria Poliedro mapeados (475 linhas de ranking); em 13 cidades o parceiro é líder local, em 17 está em 2º-3º, em 10 está em 4º-5º, em 8 está em 6º-10º e em 3 está fora do Top 10 (São Paulo — 26ª posição local —, Niterói e Florianópolis são os casos mais distantes, candidatos naturais a revisão comercial da parceria atual).
