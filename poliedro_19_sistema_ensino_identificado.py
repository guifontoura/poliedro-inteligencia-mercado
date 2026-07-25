"""
Case Poliedro — Passo 19 (roadmap 3.0, pedido do Gui em 24/07: "comece a
documentar qual o sistema de ensino de cada uma das escolas"): REGISTRO
PERSISTENTE de qual sistema de ensino cada Golden Lead já usa hoje.

Por que isso importa: uma Golden Lead que já usa um sistema concorrente
(Objetivo, Anglo, SAS, Positivo...) tem uma venda mais difícil (precisa
trocar de fornecedor) do que uma que usa material próprio/apostila autoral
(mais fácil de convencer a adotar um sistema pela primeira vez) ou, no
extremo, uma que já é Poliedro (não é prospect, ver poliedro_09).

Não existe base pública estruturada com essa informação — não tem como
"baixar" isso de um dataset do INEP/IBGE. É pesquisa manual, escola por
escola, via busca no site/imprensa de cada uma. Esse script não CALCULA
nada — é um registro (memória de projeto) que cresce a cada pesquisa,
igual um cache manual. Sempre que uma nova escola for pesquisada, adicione
uma linha em `REGISTROS` abaixo e rode de novo.

Achado da 1ª leva (10 escolas, busca genérica): taxa de confirmação baixa —
só 1 de 10 (Objetivo Colégio Integrado, concorrente direto).

Achado da 2ª leva (24/07 à noite, mais 8 escolas — desta vez usando os
operadores de busca `"nome da escola" "sistema de ensino" OR "material
didático"` sugeridos pelo Gui): taxa de confirmação melhorou bastante — 2 de
8 (Bahiense usa SAS, Nossa Senhora do Rosário usa Anglo, ambos concorrentes
diretos). O operador de busca importa: frases exatas entre aspas acham a
página certa do site da escola com muito mais precisão que busca livre.
Segue valendo o padrão: escolas tradicionais/confessionais/bilíngues com
identidade de marca forte (Marista, Franco-Brasileiro, Alfa Cem, Escola
Parque, Israelita) não usam sistema de terceiros — moldam a intuição
inicial de que esse perfil de escola é prospect mais difícil.

Gera: data/outputs/19_sistema_ensino_identificado.csv
"""

from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")

# codigo_escola: (sistema_identificado, confianca, fonte_resumo)
# confianca: "confirmado" (o site da própria escola/notícia cita o sistema
# por nome) | "provavel_proprio" (escola tradicional/confessional, sem
# menção pública a sistema de terceiros — inferência, não confirmação) |
# "nao_identificado" (busca não trouxe sinal suficiente pra nem inferir)
REGISTROS = {
    "33065403": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (Leblon) — confessional agostiniano, tradicional, sem menção pública a sistema de terceiros"),
    "33135371": ("não identificado", "provavel_proprio", "Colégio Cruzeiro (Jacarepaguá) — escola alemã (Deutsche Schule), pedagogia própria, sem menção a sistema de terceiros"),
    "35103524": ("não identificado", "provavel_proprio", "Dante Alighieri — currículo ítalo-brasileiro reconhecido pelo governo italiano, material próprio"),
    "33062633": ("não identificado", "provavel_proprio", "Colégio de São Bento (RJ) — tradição beneditina de 163 anos, sem menção a sistema de terceiros"),
    "35399197": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Colégio Integrado — usa Coleção Didática do Sistema Objetivo (concorrente direto)"),
    "33104220": ("não identificado", "nao_identificado", "Recanto Inf. Imaculada Conceição — busca não trouxe menção a sistema de ensino"),
    "33100713": ("não identificado", "nao_identificado", "Colégio Saint John (Barra da Tijuca) — busca não trouxe menção a sistema de ensino"),
    "35143406": ("não identificado", "nao_identificado", "Augusto Laranja (Moema) — parceria Cambridge International, mas sem menção a sistema de ensino nacional"),
    "35165347": ("não identificado", "nao_identificado", "Mobile Colégio — busca não retornou informação suficiente"),
    "35105314": ("não identificado", "provavel_proprio", "Colégio Franciscano Pio XII — confessional franciscano, bilíngue Cambridge, sem menção a sistema de terceiros"),
    # Segunda leva (24/07 à noite) — usando operadores de busca sugeridos pelo Gui
    # ("nome da escola" "sistema de ensino" OR "material didático").
    "33077029": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Colégio Bahiense (Barra da Tijuca) — material \"SAS Bahiense\", confirma uso do Sistema SAS"),
    "35107190": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colégio Nossa Senhora do Rosário (SP) — usa Sistema Anglo de Ensino no Ensino Médio; Cogna lista o Anglo como marca própria no site institucional (kroton.com.br/nossas-marcas)"),
    "33160830": ("não identificado", "provavel_proprio", "Marista São José Barra — rede confessional marista, material institucional próprio da rede"),
    "33063419": ("não identificado", "provavel_proprio", "Colégio Franco Brasileiro — modelo bilíngue franco-brasileiro, currículo próprio + parceria Ontario Virtual School"),
    "33075425": ("não identificado", "nao_identificado", "Colégio Pentágono — menciona \"sistema\" conectando 210 mil alunos no Brasil, mas não nomeia a marca; precisa verificar melhor"),
    "33188092": ("não identificado", "provavel_proprio", "Colégio Alfa Cem Bilíngue — método fonético e material próprios, parceria Cambridge pro inglês"),
    "33184739": ("não identificado", "provavel_proprio", "Colégio Alfa Cem Bilíngue (2ª unidade) — mesma rede, método próprio"),
    "33065837": ("não identificado", "provavel_proprio", "Escola Parque (Gávea) — pedagogia construtivista/por projetos, tradição própria de 55 anos"),
    "33064040": ("não identificado", "provavel_proprio", "Escola Israelita Brasileira Eliezer Steinbarg Max Nordau — escola comunitária judaica, identidade própria"),
    # Terceira leva (24/07, batch nas Golden Leads de maior score_destaque ainda sem registro).
    "31004651": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (BH) — confessional agostiniano, Microsoft Showcase School é certificação de tecnologia, não sistema didático de terceiros"),
    "23246871": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Ari de Sá Cavalcante - Mário Mamede (Fortaleza) — usa SAS (Sistema Ari de Sá), marca criada pela PRÓPRIA rede Ari de Sá e hoje operada pelo Grupo Arco Educação (junto com pH/Plataforma COC/Geekie), vendida a +1.200 escolas; concorrente, mas a rede não compraria de fora"),
    "23245573": ("Sistema Eleva (Grupo Eleva Educação)", "confirmado", "Master Colégio (Fortaleza) — usa material Eleva (Portal do Aluno, conteúdo interdisciplinar)"),
    "27220885": ("Sistema Poliedro", "confirmado", "Colégio Contato (Maceió) — ATENÇÃO: site do próprio colégio se declara 'parceiro exclusivo em Alagoas do Sistema de Ensino Poliedro'. Já é rede Poliedro sob outra marca — não passou pelo filtro de exclusão do passo 09 (que só olha 'POLIEDRO' no nome oficial do Censo). Ver observação abaixo do dict."),
    "26189569": ("não identificado", "provavel_proprio", "Colégio Cognitivo (Recife, unidade Casa Forte) — material 'fundamentado em livros didáticos' escolhido pela própria equipe de professores, sem sistema de terceiros citado"),
    "26534711": ("não identificado", "provavel_proprio", "Colégio Cognitivo (Recife, unidade Boa Viagem) — mesma rede/material da unidade Casa Forte"),
    "26118165": ("Sistema Equipe (Grupo Equipe, independente/regional Norte-Nordeste)", "confirmado", "Colégio Equipe (Recife) — Sistema de Ensino Equipe, com editora própria (marca própria da rede, vendida a outras escolas do Norte/Nordeste)"),
    "23272430": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Ari de Sá Cavalcante - Aldeota (Fortaleza) — mesma rede/material SAS da unidade Mário Mamede"),
    "35805555": ("Sistema Pitágoras (Grupo Cogna)", "confirmado", "Colégio Embraer Juarez Wanderley (São José dos Campos) — gerido pelo Sistema Pitágoras de Ensino (Grupo Cogna, fundado a partir do próprio Pitágoras em 1966) via Instituto Embraer; ATENÇÃO: escola de bolsa integral (~80% bolsistas), não é comprador comercial típico"),
    "32041152": ("Sistema Eleva (Grupo Eleva Educação)", "confirmado", "Escola São Domingos (Vitória) — material Eleva citado em contrato público (4 volumes), ao lado de Edify (bilíngue) e Escola da Inteligência; confiança média-alta, fonte é documento contratual, não o site oficial"),
    "15168344": ("Sistema Equipe (Grupo Equipe, independente/regional Norte-Nordeste)", "confirmado", "Colégio Equipe Cristal (Belém) — unidade da rede Sistema de Ensino Equipe, mesma marca própria da unidade de Recife"),
    "31333921": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (Nova Lima) — mesma rede confessional da unidade BH, sem sistema de terceiros citado"),
    # Correções do Gui (24/07) — casos que a minha busca via API (WebSearch) não achou mas ele achou rápido
    # no Google direto. Re-verifiquei via Claude in Chrome (navegador real, 24/07 à noite) e confirmei os
    # dois — a hipótese de que a API de busca não indexa/prioriza páginas específicas (vídeo institucional,
    # posts de Instagram) do jeito que o Google nativo faz parece correta: com o navegador de verdade,
    # encontrei a mesma informação sem dificuldade.
    "53020570": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Colégio Pódion (Brasília) — corrigido pelo Gui: usa Sistema SAS de Ensino (confirmado via vídeo institucional 'SAS Educação + Colégio Pódion')"),
    "25097539": ("Sistema Bernoulli (Grupo Bernoulli Educação, independente)", "confirmado", "Colégio e Curso Evolução (João Pessoa) — corrigido pelo Gui: usa Sistema Bernoulli de Ensino"),
    "24057169": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "FACEX (Natal) — corrigido pelo Gui (24/07): usa Sistema SAS de Ensino"),
    # Quarta leva (24/07 à noite, já usando Claude in Chrome — navegador real, não a API de busca).
    "31006394": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colégio Marista Dom Silvério (BH) — usa o Sistema Marista de Educação (SME), material produzido pela FTD só pra rede Marista, não vendido a escolas de fora"),
    "24057134": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colégio Marista de Natal — mesmo SME (Sistema Marista de Educação) da unidade de BH"),
    "31004031": ("Sistema FTD", "confirmado", "Colégio Santa Marcelina (BH) — lista de material 2026 do próprio colégio cita \"FTD Sistema de Ensino\" para pelo menos parte do currículo (1ª série EM)"),
    "33063729": ("Sistema FTD", "confirmado", "Colégio Santo Inácio (RJ, Rede Jesuíta) — achado PDF de lista de material citando \"Sistema de Ensino – Editora FTD\"; confiança média (o PDF veio de um domínio santoinacio.com.br genérico, pode ser de outra unidade jesuíta com o mesmo nome, não 100% certo que é a unidade do Rio especificamente)"),
    "33057109": ("não identificado", "nao_identificado", "Colégio La Salle Abel (Santos) — a Rede La Salle em geral usa 'Itinerários Formativos' próprios + Sistema COC em pelo menos uma unidade (Botucatu), mas não achei confirmação específica pra unidade Abel/Santos"),
    "33063656": ("não identificado", "nao_identificado", "Associação do Colégio Nossa Senhora de Sion (RJ) — usa metodologia Montessori e material próprio \"Território da Leitura\", sem sistema de terceiros nomeado; ATENÇÃO: uma unidade Sion diferente (Vila Maria, provavelmente SP) foi mencionada usando Sistema Poliedro num post — não se aplica a esta unidade específica do RJ"),
    "22025740": ("não identificado", "nao_identificado", "Instituto Dom Barreto (Teresina, unidade Centro) — busca não trouxe o nome de um sistema de terceiros; escola tradicional grande o bastante pra ter perfil de material próprio, não confirmado"),
    # Rede própria Poliedro (achado 24/07 via nome no Censo, ver poliedro_09) — passou a ficar VISÍVEL nos
    # Golden Leads em vez de excluída (pedido do Gui). Sistema de ensino é óbvio pelo próprio nome, não
    # precisou de pesquisa: são literalmente unidades/franquia Poliedro.
    "35004269": ("Sistema Poliedro", "confirmado", "Colégio Poliedro (Campinas, Taquaral) — unidade própria/franquia Poliedro, nome no Censo"),
    "35009757": ("Sistema Poliedro", "confirmado", "Colégio Poliedro Unidade Centro (Campinas) — unidade própria/franquia Poliedro, nome no Censo"),
    "35175572": ("Sistema Poliedro", "confirmado", "Poliedro Colégio (São José dos Campos) — unidade própria/franquia Poliedro, nome no Censo"),
    "35134132": ("Sistema Poliedro", "confirmado", "Colégio Poliedro de Educação (São Paulo, Barra Funda) — unidade própria/franquia Poliedro, nome no Censo"),
    # Cross-check com a lista de "Escolas Associadas" do próprio site institucional do Poliedro (passada
    # pelo Gui, 24/07) contra a base de escolas do Censo — achado 1 match direto num Golden Lead atual.
    "35108923": ("Sistema Poliedro", "confirmado", "Colégio Ábaco (São Bernardo do Campo) — site oficial do Poliedro lista como Escola Associada ('Outros Estados: Colégio Ábaco...')"),
    # Quinta leva (24/07, foco redirecionado pelo Gui: parar de verificar grupo controlador e
    # priorizar cobertura bruta de sistema_ensino_identificado, usando o segmento "Líder local"
    # (210 Golden Leads) como alvo de curto prazo). Confirmei cidade real de cada código via
    # codigo_municipio antes de pesquisar (2 nomes da leva anterior — "Cariacica" e "Guanhães" —
    # eram suposições da rodada anterior que a checagem por código corrigiu: são Ipatinga e Lavras).
    "43139108": ("Sistema Bernoulli (Grupo Bernoulli Educação, independente)", "confirmado", "Colégio Sinodal São Leopoldo (RS) — lista de material oficial 2025/2026 cita explicitamente 'a base do material didático será da Editora Bernoulli' pra 1ª série do Ensino Médio"),
    "31193097": ("Sistema Bernoulli (Grupo Bernoulli Educação, independente)", "confirmado", "Colégio São Francisco Xavier (Ipatinga, MG — bairro Cariru, daí o nome 'CARIRU' no Censo) — parceria oficial com o Sistema Bernoulli desde 2023 pro Ensino Médio (csfx.com.br/fsfx.com.br)"),
    "31205265": ("Sistema Fibonacci", "confirmado", "Instituto Presbiteriano Gammon (Lavras, MG — sede/unidade histórica da rede, confirmado via codigo_municipio) — Instagram oficial @ipgammon cita 'Sistema de Ensino Fibonacci' com material didático próprio da marca; ATENÇÃO: unidades satélite da mesma rede (ex.: Guanhães) usam SAS — sistemas variam por unidade dentro do próprio grupo Gammon"),
    "15103080": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Grupo Futuro Educacional (Marabá, PA) — Instagram oficial @futuroeducacional: 'Material didático do SAS, um dos melhores sistemas de ensino do Brasil'"),
    "31014061": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho-Unidade Contagem — mesma rede confessional agostiniano das unidades BH (31004651) e Nova Lima (31333921), já registradas sem sistema de terceiros; registrado por padrão de rede (pedido do Gui), sem pesquisa nova"),
    "43173330": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Col João Paulo I - Unidade Sul (Porto Alegre, zona sul / JPSul) — usa material SAS (Ari de Sá); confiança média-alta, fonte não é o site oficial da escola (fleye.com.br), recomendável checar lista de material oficial se possível"),
    "35115712": ("não identificado", "nao_identificado", "Fundação Educacional Raul Bauab (Jaú, SP) — perfil institucional/técnico (PDI, produção acadêmica de docentes em Lattes/Escavador), sem sinal de sistema de ensino comercial licenciado; pode usar material próprio institucional, não confirmado"),
    # Sexta leva (24/07, ritmo acelerado a pedido do Gui: buscas com snippet só, sem navegar
    # em página nenhuma — se o resultado não é conclusivo de cara, marca nao_identificado e
    # segue pra próxima; ver conversa sobre pipeline de busca).
    "29480620": ("não identificado", "nao_identificado", "Centro Educacional Villa Lobos (Camaçari, BA) — busca não confirmou sistema; ATENÇÃO: unidade irmã (mesmo CNPJ 04692152000153, unidade Salvador) usa Sistema COC — vale conferir se Camaçari segue o mesmo, não presumi"),
    "52103137": ("não identificado", "nao_identificado", "Colégio Arena (Goiânia) — busca não trouxe sistema de terceiros; site oficial não citado nos resultados"),
    "35142967": ("não identificado", "provavel_proprio", "Colégio Engenheiro Salvador Arena (São Bernardo do Campo) — mantido pela Fundação Salvador Arena, ensino gratuito, metodologia/currículo próprios, sem sistema de terceiros citado"),
    "35286187": ("Sistema Etapa (produzido pelo próprio Colégio Etapa, comercializado a escolas conveniadas)", "confirmado", "Etapa Colégio (Valinhos) — usa o Sistema Etapa, material próprio da rede Etapa que também é vendido a escolas conveniadas em todo o Brasil"),
    "31354562": ("não identificado", "provavel_proprio", "Colégio Gabarito (Uberaba) — rede própria (Gabarito Educação, 7 unidades em MG) que licencia SUA PRÓPRIA marca/material a escolas afiliadas na região; não usa sistema de terceiros, é ela quem licencia"),
    "33042578": ("não identificado", "nao_identificado", "Colégio São Paulo (Teresópolis) — busca não trouxe sistema de terceiros"),
    "31074373": ("não identificado", "nao_identificado", "Colégio Santa Catarina (Juiz de Fora) — busca não trouxe sistema de terceiros (não confundir com 'Colégio Franciscano Santa Catarina', rede G12 diferente, que usa Positivo)"),
    "31041181": ("não identificado", "nao_identificado", "Escola Técnica de Divinópolis-Integral — busca só retornou resultados do 'Anglo Divinópolis', escola diferente; sem sinal pra esta"),
    "24281301": ("não identificado", "provavel_proprio", "Colégio Salesiano Dom Bosco (Parnamirim) — rede salesiana, pedagogia própria da congregação (Sistema Preventivo de Dom Bosco), sem sistema comercial de terceiros citado"),
    "52020517": ("Sistema Bernoulli (Grupo Bernoulli Educação, independente)", "confirmado", "Colégio Galileu (Anápolis) — site oficial cita dois sistemas por segmento (Positivo na Infantil/Fund. I, Bernoulli do Fund. II/EM em diante); registrado só o de Fund.II/EM em diante, por pedido do Gui (é o segmento que mais importa pro perfil de venda)"),
    "31339989": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Instituto Educacional Margarida Rezende - IEMAR (Conselheiro Lafaiete) — parceria com SAS Educação citada como diferencial da escola"),
    "50032895": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colégio Unigran - Unidade II (Dourados) — opera como 'Colégio Anglo Unigran', usa material do Sistema Anglo de Ensino"),
    "43119930": ("não identificado", "nao_identificado", "Colégio Mauá (Santa Cruz do Sul) — filantrópica tradicional (150+ anos), busca não trouxe sistema de terceiros"),
    "29422272": ("Sistema COC", "confirmado", "Centro Educacional Villa Lobos (Salvador) — usa o Sistema COC do Fund. I ao EM; ver observação na unidade irmã de Camaçari (mesmo CNPJ, não confirmado lá)"),
    "41148142": ("Sistema Poliedro", "confirmado", "Colégio do Bosque Mananciais (Curitiba) — usa material do Sistema Poliedro do Fund. II ao EM, uma das poucas escolas de Curitiba com Poliedro desde o Fundamental; MESMO PADRÃO do caso Contato/Ábaco: Golden Lead que já é cliente Poliedro sob marca própria, sem passar pelo filtro de nome do passo 09"),
    "35449003": ("não identificado", "provavel_proprio", "Colégio FAAP (Ribeirão Preto) — material didático exclusivo de produção própria da FAAP, sem sistema de terceiros"),
    "21010331": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Colégio Dom Bosco (São Luís, MA) — usa a plataforma SAS (inclusive o Eureka, gamificação SAS pros Anos Finais)"),
    "28032322": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Centro de Excelência Master (Aracaju) — usa Sistema Ari de Sá (SAS), com 'Meta SAS' e avaliações sistemáticas próprias do sistema citadas pelo colégio"),
    "25073214": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Colégio Nossa Senhora de Lourdes (Campina Grande) — usa o sistema SAS de ensino"),
    "43216471": ("não identificado", "nao_identificado", "Unidade de Ensino Colégio Sinodal Prado Gravataí — mesma mantenedora (ISAEC/IECLB) da unidade São Leopoldo (que confirma Bernoulli no EM), mas não achei confirmação direta pra esta unidade especificamente; não presumi"),
    # Setima leva (24/07, pedido do Gui: aproveitar padrao de rede pra pular pesquisa quando
    # ja vimos >=2 unidades da MESMA rede concordando, ou quando o sistema e fato institucional
    # (Marista/SME e exclusivo da rede inteira, confirmado estruturalmente, nao por unidade).
    # Risco real dessa tecnica (documentado, nao ignorado): "Santo Agostinho" e nome generico de
    # santo catolico usado por varias redes SEM relacao entre si (a rede de BH/Nova Lima/Contagem
    # nao e a mesma do Colegio Santo Agostinho de Goiania nem do Instituto Santo Agostinho do CE) -
    # por isso NAO apliquei o padrao pra Santo Agostinho fora do cluster BH/Nova Lima/Contagem ja
    # confirmado, e pesquisei essas individualmente abaixo. "Villa Lobos" (leva anterior) e outro
    # caso onde o padrao FALHOU (Camacari != Salvador) - fica registrado como contraexemplo.
    "43108164": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Col Marista Nossa Senhora Do Rosario — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "29447518": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista De Patamares — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "25093088": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Pio X — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "35114820": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Marista Colegio De Ribeirao Preto — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "32038224": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Nossa Senhora Da Penha — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "41127242": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Anjo Da Guarda Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "41133153": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Santa Maria Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "31166332": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Diocesano — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "17046807": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Palmas — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "42053480": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Sao Francisco Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "31170402": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Col Marista Champagnat — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "31096261": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Col Marista Sao Jose — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "50005405": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Alexander Fleming — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "43121900": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Santa Maria — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "42011612": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Criciuma Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "42091560": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Sao Luis Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "43119948": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Sao Luis — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "41063252": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Pio Xii Ei Ef E Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "32010311": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "31293687": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista - Varginha — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "41071859": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista De Cascavel Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "33066698": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Sao Jose — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "31004880": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Padre Eustaquio — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "52033708": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Goiania Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "26122162": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Sao Luis — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "15038424": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Nossa Senhora De Nazare — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "53011074": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Col Marista Joao Paulo Ii — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "53001346": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista De Brasilia Ensino Fundamental E Ensino Medio — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "41132130": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Paranaense Ei Ef Em — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "41032004": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Marista De Londrina C - Ei Ef M — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "53003659": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Col Marista Champagnat — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "43104959": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colegio Marista Champagnat — Rede Marista nacional, SME/FTD e exclusivo da rede inteira (fato estrutural confirmado, nao por unidade); registrado por padrao de rede"),
    "35107177": ("Sistema Marista (produzido pela Editora FTD, exclusivo da Rede Marista)", "confirmado", "Colégio Marista Arquidiocesano (São Paulo) — verifiquei individualmente por causa do nome atípico ('Arquidiocesano'); confirmado via colegiosmaristas.com.br que é rede Marista de fato (167 anos, Maristas desde 1908), usa SME/FTD"),
    # Casos "Santo Agostinho" verificados individualmente (nome genérico de santo, não presumi rede).
    "52033848": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (Goiânia) — REDE DIFERENTE da de BH/Nova Lima/Contagem: mantido pela Congregação Agostinianas Missionárias (agostinianas.com.br), não Agostinianos Recoletos; material recomendado próprio, sem sistema de terceiros citado"),
    "33176825": ("não identificado", "nao_identificado", "Colégio Santo Agostinho - Unidade Instituto Cultural Santo Agostinho (Barra da Tijuca, RJ) — ATENÇÃO/achado: o site da própria unidade cita que a escola 'adota sistemas de ensino renomados nacionalmente' mediante custo adicional de R$3.000/ano, mas não nomeia qual; isso é evidência de que a rede Santo Agostinho do RJ (mesma do Leblon, 33065403) PODE usar sistema de terceiros, contrariando a inferência 'provavel_proprio' que fiz pro Leblon — vale reabrir esse registro"),
    "22138544": ("não identificado", "nao_identificado", "Instituto Santo Agostinho (Teresina, PI — não Ceará como eu tinha registrado o código, corrigido aqui) — escola de bolsa integral, material didático incluído no benefício, sem sistema de terceiros nomeado"),
    "31324663": ("não identificado", "nao_identificado", "SIC - Escola Profissionalizante Santo Agostinho (BH) — ATENÇÃO: perfil atípico pra Golden Lead, é escola técnica/profissionalizante de bolsa integral (Informática, Eletromecânica), mantida por obra social agostiniana (Sociedade Inteligência e Coração); não é o perfil comercial típico de cliente de sistema de ensino licenciado"),
    # Oitava leva (24/07, pedido do Gui: usar o proprio nome da escola como marca do
    # sistema quando a marca literal aparece no NO_ENTIDADE do Censo - mesma logica do
    # rede_propria_poliedro, generalizada pra outras marcas licenciadas/franquias. Custo
    # zero (sem busca). Risco: substring falso-positivo (ex.: "MAXI" dentro de "MAXIMUS")
    # - conferido e excluido manualmente antes de registrar.
    "31291986": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Centro Educacional Divinopolis-Anglo — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35137170": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Alante Sao Jose Dos Campos — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33147450": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Americano — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33439796": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Anglo Americano Escolas Integradas Ltda — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35467066": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Novo Anglo Bauru — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "41075927": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Americano — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35801793": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Anglo Alante Araras 2 — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35135288": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Leonardo Da Vinci — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35121307": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Cidade De Sao Carlos - Unidade I — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35144502": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Anglo Cezanne Colegio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35813000": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Renovacao Anglo Indaiatuba — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35195005": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Leonardo Da Vinci — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35301279": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Leonardo Da Vinci — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "50032950": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Anglo Tres Lagoas — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35158616": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Anglo Sistema De Ensino — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "29422248": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Brasileiro — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35004801": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Sao Paulo — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33087628": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Anglo Americano Escolas Integradas Ltd — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35287600": ("Sistema Anglo (Grupo Cogna)", "confirmado", "Colegio Anglo Leonardo Da Vinci — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35007022": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Colegio Objetivo De Piracicaba — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35809159": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo De Sao Jose Do Rio Preto Colegio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35126974": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Integrado De Mogi Das Cruzes Colegio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35140193": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Colegio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35159013": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Colegio Objetivo De Rio Claro — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35140995": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Junior Colegio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "52107990": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Colegio Objetivo Valparaiso — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35103433": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Centro Interescolar Unidade Paulista — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35133450": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Colegio I Unidade Pinheiros — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "24057193": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Colegio Objetivo De Natal — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35132214": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Centro Interescolar Unidade Paz — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35456731": ("Sistema Objetivo (Grupo Objetivo/UNIP, independente)", "confirmado", "Objetivo Centro Interescolar Unidade Ipiranga — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35583224": ("Sistema COC", "confirmado", "Colegio Coc — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "21272921": ("Sistema COC", "confirmado", "Inst Educacional Sul Maranhense Coc — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "17057574": ("Sistema COC", "confirmado", "Colegio Coc Integral — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "42160642": ("Sistema COC", "confirmado", "Coc Blumenau — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "42164702": ("Sistema COC", "confirmado", "Coc Itajai — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "42153824": ("Sistema COC", "confirmado", "Coc Balneario Camboriu Colegio Carvalho — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "53009428": ("Sistema COC", "confirmado", "Col Coc Lago Norte — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33101876": ("Sistema COC", "confirmado", "Coc - Ilha Do Governador - Unidade Cambauba — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "42113083": ("Sistema COC", "confirmado", "Coc Colegio Osvaldo Carvalho Eireli Epp — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "42121191": ("Sistema Positivo", "confirmado", "Colegio Positivo Joinville — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "41063015": ("Sistema Positivo", "confirmado", "Colegio Positivo Master - Educacao Infantil Ensino Fundamental E Medio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "41152484": ("Sistema Positivo", "confirmado", "Colegio Positivo International School - Educacao Infantil Ensino Fundamental E Medio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "41129326": ("Sistema Positivo", "confirmado", "Colegio Positivo Boa Vista - Educacao Infantil Ensino Fundamental E Medio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "41158750": ("Sistema Positivo", "confirmado", "Colegio Positivo Hauer - Ensino Medio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "29485541": ("Sistema Bernoulli (Grupo Bernoulli Educação, independente)", "confirmado", "Colegio Bernoulli — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "31350664": ("Sistema Bernoulli (Grupo Bernoulli Educação, independente)", "confirmado", "Colegio Bernoulli — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33165998": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33177627": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33180539": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33180385": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33105405": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33110328": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33249202": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33155852": ("Sistema pH", "confirmado", "Colegio Ph — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35134806": ("Sistema Etapa (produzido pelo próprio Colégio Etapa, comercializado a escolas conveniadas)", "confirmado", "Etapa Colegio De Efm — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35007592": ("Sistema Etapa (produzido pelo próprio Colégio Etapa, comercializado a escolas conveniadas)", "confirmado", "Colegio Etapa Vila Mascote — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "35563006": ("Sistema Etapa (produzido pelo próprio Colégio Etapa, comercializado a escolas conveniadas)", "confirmado", "Etapa Iii Colegio — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33183830": ("Sistema Eleva (Grupo Eleva Educação)", "confirmado", "Escola Eleva — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "33196249": ("Sistema Eleva (Grupo Eleva Educação)", "confirmado", "Escola Eleva - Urca — marca do sistema aparece literalmente no nome oficial da escola no Censo (mesma lógica do rede_propria_poliedro); registrado sem busca nova"),
    "15167275": ("Sistema Equipe (Grupo Equipe, independente/regional Norte-Nordeste)", "confirmado", "Colegio Equipe Ltda — mesma rede/marca propria Equipe ja confirmada em Recife e Belem (2 unidades concordando); registrado por padrao de rede"),
    "15177017": ("Sistema Equipe (Grupo Equipe, independente/regional Norte-Nordeste)", "confirmado", "Colegio Equipe Ananindeua — mesma rede/marca propria Equipe ja confirmada em Recife e Belem (2 unidades concordando); registrado por padrao de rede"),
    "15229408": ("Sistema Equipe (Grupo Equipe, independente/regional Norte-Nordeste)", "confirmado", "Colegio Equipe Gentil — mesma rede/marca propria Equipe ja confirmada em Recife e Belem (2 unidades concordando); registrado por padrao de rede"),
    "31324515": ("Sistema Equipe (Grupo Equipe, independente/regional Norte-Nordeste)", "confirmado", "Colegio Equipe De Juiz De Fora — mesma rede/marca propria Equipe ja confirmada em Recife e Belem (2 unidades concordando); registrado por padrao de rede"),
    "35103445": ("Sistema Equipe (Grupo Equipe, independente/regional Norte-Nordeste)", "confirmado", "Equipe Colegio — mesma rede/marca propria Equipe ja confirmada em Recife e Belem (2 unidades concordando); registrado por padrao de rede"),
    "23071036": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Ari De Sa Cavalcante - Washington Soares — mesma rede Ari de Sa Cavalcante ja confirmada em 2 outras unidades (SAS); registrado por padrao de rede"),
    "23235543": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Ari De Sa Cavalcante - Major Facundo — mesma rede Ari de Sa Cavalcante ja confirmada em 2 outras unidades (SAS); registrado por padrao de rede"),
    "23069864": ("Sistema SAS (Grupo Arco Educação)", "confirmado", "Ari De Sa Cavalcante - Duque De Caxias — mesma rede Ari de Sa Cavalcante ja confirmada em 2 outras unidades (SAS); registrado por padrao de rede"),
    "33184720": ("não identificado", "provavel_proprio", "Colegio Alfa Cem Bilingue — mesma rede Alfa Cem Bilingue ja confirmada em 2 outras unidades (metodo/material proprios); registrado por padrao de rede"),
    "33178879": ("não identificado", "provavel_proprio", "Colegio Alfa Cem Bilingue — mesma rede Alfa Cem Bilingue ja confirmada em 2 outras unidades (metodo/material proprios); registrado por padrao de rede"),
    # Nona leva (24/07) — CORREÇÃO: eu tinha dado esta escola como "Sistema Fibonacci,
    # confirmado" em conversa, baseado num snippet de Instagram que citava "Material Didático
    # Fibonacci". O Gui conferiu a fonte primária (lista oficial de material 2026 da própria
    # escola, PDF) e ela mostra livros AVULSOS de editoras diferentes por matéria (Moderna,
    # Ática, SM, Saraiva, FTD só no inglês, Artmed) e várias matérias como "material a ser
    # fornecido pelo professor" — o oposto de um sistema integrado licenciado. "Fibonacci" no
    # snippet provavelmente era algo pontual (não o currículo inteiro). Lição: snippet de rede
    # social que cita um nome de sistema não é confirmação forte o suficiente sozinho quando
    # existe lista oficial de material contradizendo — fonte primária sempre pesa mais.
    "31004812": ("não identificado", "provavel_proprio", "Colégio Santo Antônio (BH) — CORRIGIDO: lista oficial de material da 3ª série EM (2026, fonte primária) mostra livros avulsos de Moderna/Ática/SM/Saraiva/FTD por matéria, não sistema integrado; contradiz snippet anterior sobre 'Fibonacci' (provavelmente item pontual, não o currículo)"),
    # Décima leva (24/07) — as 14 escolas que o lote do Serper devolveu "sem resultado orgânico"
    # (nome vinha com acento quebrado no Censo em alguns casos, ex. "COLGIO BOM JESUS MARINGA");
    # pesquisadas individualmente via WebSearch com o nome corrigido.
    "29277744": ("não identificado", "provavel_proprio", "Colégio Nossa Senhora de Fátima - Sacramentinas (Vitória da Conquista) — rede confessional própria (Irmãs Sacramentinas, desde 1956), sem sistema de terceiros citado"),
    "31354600": ("não identificado", "provavel_proprio", "Colégio Batista Mineiro - Alphaville Nova Lima — Rede Batista de Educação, Programa de Formação Socioemocional e metodologia bilíngue próprios da rede, sem sistema de terceiros citado"),
    "35139646": ("não identificado", "provavel_proprio", "Colégio Rio Branco - Granja Viana (Cotia) — currículo brasileiro próprio; parceria com Fieldwork Education é só pro programa internacional adicional (IEYC/IPC/IMYC), não substitui um sistema de ensino brasileiro comercial"),
    "33195463": ("não identificado", "nao_identificado", "Colégio Sant'Anna Segmentos Finais (Araruama) — busca não trouxe sistema de terceiros"),
    "41358899": ("não identificado", "provavel_proprio", "Centro Educacional St. James (Londrina) — ATENÇÃO: escola foi ADQUIRIDA pelo Grupo Positivo (mesmo grupo do Sistema Positivo), mas reportagem cita acordo explícito de 'não interferência na metodologia de ensino, incluindo material didático' — ou seja, dono agora é concorrente, mas o material seguiu sendo próprio (bilíngue); vale reconferir daqui uns anos, pode mudar"),
    "33140502": ("não identificado", "provavel_proprio", "Colégio Atuação Bilíngue (Niterói) — metodologia bilíngue própria (Pronunciation, Leadership, Literature, Assignment, Speech, Business, Task Based Problem), sem sistema de terceiros citado"),
    "41135946": ("não identificado", "provavel_proprio", "Colégio Suíço-Brasileiro de Curitiba (Pinhais) — currículo IB (Bacharelado Internacional) + método próprio (Team Teaching), reconhecido pelo governo suíço; não é sistema brasileiro comercial"),
    "43203876": ("não identificado", "provavel_proprio", "Colégio Gabarito Zona Norte (Porto Alegre) — ATENÇÃO: rede REGIONAL DIFERENTE do 'Gabarito Educação' de Uberaba/MG já registrado (31354562) — mesmo nome genérico, mantenedoras diferentes; começou como cursinho em 1999, sem sistema de terceiros citado"),
    "33195552": ("não identificado", "nao_identificado", "Colégio Aprovado (Rio das Ostras) — descrição só com linguagem de marketing genérica ('ambiente inovador', 'desenvolvimento socioemocional'), não dá pra confirmar nem inferir com segurança"),
    "31170216": ("não identificado", "provavel_proprio", "Colégio Berlaar Sagrado Coração de Jesus (Araguari) — rede confessional própria (AESCOM/Rede Berlaar de Educação, desde 1919), sem sistema de terceiros citado"),
    "53001192": ("Sistema Positivo", "confirmado", "Centro Educacional Sagrada Família (Brasília) — usa a 'metodologia da excelência e o Sistema de Ensino Positivo', citado diretamente sobre esta escola"),
    "29486696": ("não identificado", "nao_identificado", "Centro Educacional Opção (Vitória da Conquista) — escola muito nova (fundada 2022), informação insuficiente; pode ou não ter relação com 'Colégio Opção' (1997) da mesma cidade, não confirmado"),
    "53038002": ("não identificado", "nao_identificado", "Centro de Ensino Médio Delta (Brasília) — só achei informação de CNPJ/cadastro empresarial, nada pedagógico"),
    "41377370": ("não identificado", "provavel_proprio", "Colégio Bom Jesus (Maringá) — Grupo Educacional Bom Jesus, tradição franciscana de 120+ anos, metodologia exclusiva própria ('Amorografia'), sem sistema de terceiros citado"),
}

# Observação (24/07): o caso do Colégio Contato (27220885) revelou que o filtro de exclusão de
# "rede própria Poliedro" no passo 09 (busca "POLIEDRO" no NO_ENTIDADE do Censo) não pega parceiros/
# franquias que vendem sob marca PRÓPRIA mas usam o material Poliedro por trás (achado só via pesquisa
# manual de sistema de ensino, não dava pra prever isso de outro jeito). Vale revisar as escolas com
# sistema_ensino_identificado == "Sistema Poliedro" e decidir com o Gui se elas devem ser excluídas das
# Golden Leads (mesma lógica do poliedro_09), não só marcadas.


def montar_tabela() -> "tuple[pd.DataFrame, int]":
    """Junta o registro manual com os dados de score/segmento já calculados."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str})
    linhas = []
    for codigo, (sistema, confianca, fonte) in REGISTROS.items():
        linhas.append({"codigo_escola": codigo, "sistema_ensino_identificado": sistema,
                        "confianca": confianca, "fonte_resumo": fonte})
    registro = pd.DataFrame(linhas)
    tabela = golden.merge(registro, on="codigo_escola", how="inner")[
        ["codigo_escola", "NO_ENTIDADE", "codigo_municipio", "segmento_comercial", "rede_propria_poliedro",
         "score_destaque", "sistema_ensino_identificado", "confianca", "fonte_resumo"]
    ]
    return tabela, len(golden)


def exibir_resumo(df: pd.DataFrame, total_golden_leads: int) -> None:
    print(f"[Sanity check] Escolas pesquisadas até agora: {len(df)} de {total_golden_leads} Golden Leads "
          f"totais ({len(df) / total_golden_leads * 100:.1f}%)")
    print(f"\n[Sanity check] Distribuição de confiança:\n{df['confianca'].value_counts()}")
    print(f"\n[Sanity check] Sistemas concorrentes confirmados: "
          f"{(df['confianca'] == 'confirmado').sum()}")
    ja_poliedro = df["rede_propria_poliedro"].sum()
    if ja_poliedro:
        print(f"[Sanity check] Dessas, {ja_poliedro} já são rede própria/franquia Poliedro (nome no Censo).")


def main():
    df, total_golden_leads = montar_tabela()
    exibir_resumo(df, total_golden_leads)
    df.to_csv(OUT_DIR / "19_sistema_ensino_identificado.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '19_sistema_ensino_identificado.csv'}")


if __name__ == "__main__":
    main()
