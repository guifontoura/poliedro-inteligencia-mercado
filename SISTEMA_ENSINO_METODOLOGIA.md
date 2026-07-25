# Metodologia — Identificação do Sistema de Ensino das Golden Leads (Roadmap 3.0)

Bônus pós-entrega formal (tag `entrega-formal-23-07`, commit `b151aed`). Objetivo: para cada uma das 1.127 Golden Leads, descobrir se ela já usa um sistema de ensino licenciado (Anglo, Bernoulli, SAS, Positivo etc.) e, principalmente, **mapear clientes ocultos do próprio Poliedro** — escolas que já usam o sistema Poliedro sob outra marca/identidade visual, não capturadas pelo filtro de nome do Censo.

Coluna gerada: `sistema_ensino_identificado` em `data/outputs/14_escolas_powerbi.csv`, junto com `confianca_sistema_ensino` e `fonte_sistema_ensino` (justificativa/evidência). Registro-fonte: `poliedro_19_sistema_ensino_identificado.py`, dicionário `REGISTROS` (`codigo_escola → (sistema, confiança, fonte)`).

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

## 4. Resultado final (24/07/2026, 100% das 1.127 Golden Leads pesquisadas)

| Confiança | Quantidade | O que significa |
|---|---|---|
| `confirmado` | 306 | Evidência direta e razoavelmente inequívoca de qual sistema de terceiros a escola usa. |
| `provavel_proprio` | 93 | Evidência de que a escola usa material/metodologia própria (não de terceiros) — nome da própria marca, rede confessional com metodologia documentada, franquia com currículo próprio (ex. Maple Bear). |
| `não identificado` | 728 | Busca não trouxe evidência confiável o suficiente pra confirmar nada — ver seção 5. |

### 4.1. Sistemas concorrentes mais encontrados (entre os 306 confirmados)

Anglo (~44), Bernoulli (~39), Marista/FTD (35, rede fechada), Sistema Poliedro (31 — ver 4.2), SAS/Ari de Sá (~33 somando as duas grafias usadas ao longo do projeto), Objetivo (17), COC (15), Positivo (14), FTD (10), pH/SOMOS (~12).

### 4.2. Clientes Poliedro mapeados — o principal objetivo desta pesquisa

**31 escolas** das 1.127 Golden Leads já usam o Sistema Poliedro — a maioria sob **marca própria/outro nome**, não capturável por um filtro de nome do Censo. Cada um tem confirmação direta (site oficial, Instagram da própria escola, ou campo estruturado de diretório) registrada em `fonte_sistema_ensino`. Exemplos de clientes ocultos encontrados: Colégio Contato (Maceió — achado original que motivou a mudança de critério), Bosque Mananciais (Curitiba), Colégio Arnaldo (BH), Colégio Oficina (Salvador), Colégio Auge (Itabira), Colégio Classe A (Campo Grande e Porto Velho, 2 unidades), Vem Ser Colégio (São José do Rio Preto), São José Externato (Atibaia), Canadian School of Niterói, Colégio Sêneca (Vitória da Conquista), Ideal Colégio (Santa Bárbara d'Oeste), IEPROL (Itabuna), Delta Educacional (Araçatuba), Progressão Colégio (rede de 3 unidades — Taubaté, Caçapava, Pindamonhangaba), Alfa de Umuarama, Complexo Educacional Dom Bosco (Imperatriz), São José Colégio Agostiniano (SP, confirmado por Gui em 24/07), entre outros.

Coluna `ja_cliente_poliedro_qualquer_marca` (em `poliedro_14_consolidar_dataset_powerbi.py`) combina esse achado com a flag por nome (`rede_propria_poliedro`) num único filtro pronto pro Power BI.

## 5. O que "não identificado" quer dizer (e o que NÃO quer dizer)

**Não significa** "a escola não usa nenhum sistema" — significa apenas que a busca pública não trouxe evidência confiável o bastante para confirmar qual sistema é. Dentro dos 728, há duas situações bem diferentes:

1. **Ausência real de sinal** (a maioria, ~419 vieram do balde `20d` sem nenhuma palavra-chave de sistema no resultado da busca) — pode ser que a escola realmente não tenha presença digital detalhada sobre isso, ou que de fato não use sistema licenciado.
2. **Sinal presente mas descartado por ambiguidade** (a maior parte do trabalho fino nas 9 levas) — o nome de um sistema apareceu na busca, mas pertencia a outra escola no mesmo ranking/lista agregada (list-adjacency, seção 3.2), ou era homônimo de rede não relacionada, ou a frase estava truncada antes de nomear a marca. Nesses casos, a decisão deliberada foi **não adivinhar** — melhor não confirmar do que confirmar errado.

Ou seja: `não identificado` é o resultado correto e esperado da metodologia quando a evidência não é boa o suficiente — não é uma lacuna de trabalho, é o próprio critério de rigor sendo aplicado.

## 6. Itens flagados para revisão futura (não bloqueiam nada, ficam documentados no código)

- Confiança média/ambígua a reverificar: Colégio Contemporâneo (Natal), Escola Autonomia (Florianópolis), Colégio Evolução (Juazeiro do Norte), Colégio Mãe de Deus (Porto Alegre, menção ambígua a evento Poliedro), Colégio Lumiere (Dourados, menção ambígua a estatística agregada Poliedro).
- Leblon Santo Agostinho (RJ) tem evidência contraditória de uma unidade-irmã — merece nova checagem individual.
- 2 escolas com "Maxi" no nome (fora as já confirmadas) valem reconsideração agora que "Sistema Maxi" foi confirmado como marca real do Grupo SOMOS.

## 7. Como reproduzir

1. `python poliedro_20_buscar_sistema_ensino_serper.py` — **roda localmente** (sandbox do Claude bloqueia a API), precisa de `data/raw/.serper_key` (nunca versionada). Gera `data/outputs/20_snippets_para_classificar.csv`.
2. Triagem por regex nos 3 baldes (script ad-hoc, não versionado — lógica descrita na seção 2).
3. Classificação manual, linha a linha, seguindo as regras da seção 3 → escrita direto em `REGISTROS` (`poliedro_19_sistema_ensino_identificado.py`).
4. `python poliedro_19_sistema_ensino_identificado.py` — valida e gera `data/outputs/19_sistema_ensino_identificado.csv` com o resumo estatístico.
5. `python poliedro_14_consolidar_dataset_powerbi.py` — propaga pro dataset final do Power BI.
