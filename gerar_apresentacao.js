/**
 * Gera Poliedro_Apresentacao_Completa.pptx a partir dos gráficos já produzidos
 * pelos scripts poliedro_07 a poliedro_12 (data/outputs/*.png).
 *
 * Rodar da raiz do projeto:
 *   npm install pptxgenjs
 *   node gerar_apresentacao.js
 */
const pptxgen = require("pptxgenjs");

const BG = "141B2C";
const BG_DEEP = "0F1626";
const CARD = "1E2A3F";
const GOLD_TINT = "2E2712";
const BORDER = "2E3D54";
const GOLD = "D4AF37";
const WHITE = "F5F7FA";
const MUTED = "9AA7BD";
const FAINT = "6B7A93";

const FONT_HEAD = "Cambria";
const FONT_BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const IMG = "data/outputs/";

function bgSlide(s) { s.background = { color: BG }; }

function addFooter(slide, pageNum) {
  slide.addText("Poliedro — Inteligência de Mercado  |  Censo Escolar INEP 2025 + Microdados ENEM 2025 + IBGE (Censo 2022)", {
    x: 0.5, y: 7.13, w: 10.5, h: 0.3, fontFace: FONT_BODY, fontSize: 8.5, color: FAINT, align: "left",
  });
  slide.addText(String(pageNum), { x: 12.6, y: 7.13, w: 0.4, h: 0.3, fontFace: FONT_BODY, fontSize: 8.5, color: FAINT, align: "right" });
}

function cardHeader(s, title) {
  s.addText(title, { x: 0.6, y: 0.42, w: 12.1, h: 0.75, fontFace: FONT_HEAD, fontSize: 28, bold: true, color: WHITE });
}

// ============ SLIDE 1 — Título ============
{
  const s = pres.addSlide();
  s.background = { color: BG_DEEP };
  s.addShape("ellipse", { x: 9.8, y: -2.3, w: 6, h: 6, fill: { color: CARD, transparency: 30 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 11.3, y: 4.6, w: 4, h: 4, fill: { color: GOLD, transparency: 88 }, line: { type: "none" } });

  s.addText("INTELIGÊNCIA DE MERCADO — NOVOS NEGÓCIOS", { x: 0.9, y: 1.4, w: 10, h: 0.4, fontFace: FONT_BODY, fontSize: 13, color: GOLD, charSpacing: 2, bold: true });
  s.addText("Onde Construir Share de Prestígio", { x: 0.85, y: 1.85, w: 11, h: 1.5, fontFace: FONT_HEAD, fontSize: 46, bold: true, color: WHITE });
  s.addText("Mapeamento de Escolas Privadas com Alto Potencial Econômico", {
    x: 0.9, y: 3.2, w: 10.8, h: 0.5, fontFace: FONT_BODY, fontSize: 16.5, color: MUTED,
  });

  const chips = [["R$80M", "TAM do Conviver e Integrar"], ["330", "escolas Desafiantes (foco)"], ["10", "cidades prioritárias"]];
  let cx = 0.9;
  chips.forEach(([num, label]) => {
    s.addText(num, { x: cx, y: 5.05, w: 2.9, h: 0.55, fontFace: FONT_HEAD, fontSize: 28, bold: true, color: GOLD });
    s.addText(label, { x: cx, y: 5.62, w: 3.3, h: 0.5, fontFace: FONT_BODY, fontSize: 11.5, color: MUTED });
    cx += 3.6;
  });

  s.addText("Fontes: Site Institucional Poliedro · Censo Escolar INEP 2025 · Microdados ENEM 2025 · IBGE  · Análise de Mercado", {
    x: 0.9, y: 6.85, w: 11, h: 0.35, fontFace: FONT_BODY, fontSize: 10.5, color: FAINT, italic: true,
  });
}

// ============ SLIDE 2 — Ecossistema LTV ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Maximizando LTV: Cross-Sell e Upsell Sem Aumentar o CAC");
  s.addText("Quatro produtos, um mesmo cliente — o faturamento cresce sem gastar mais em aquisição", { x: 0.6, y: 1.1, w: 12, h: 0.4, fontFace: FONT_BODY, fontSize: 13, color: MUTED, italic: true });

  const cards = [
    { t: "Conviver e Integrar", sub: "Socioemocional", d: "Saúde Mental, Acolhimento e Combate ao Bullying\n\nLinha de receita nova e autofinanciável via repasse de material\n\nEscolas com forte apelo socioemocional reduzem o churn e aumentam a indicação orgânica\n\nEntrega um valor intangível altíssimo: a segurança de que o filho está sendo desenvolvido integralmente" },
    { t: "Cosmos + P+", sub: "IA e Diagnóstico Pedagógico", d: "Hub de IA que apoia o professor e o P+, que diagnostica gargalos pedagógicos por turma.\n\nMais detalhes nos próximos slides." },
    { t: "Bilinguismo", sub: "Diferenciação Curricular", d: "Retenção de famílias de padrão mais alto e diferenciação frente a escolas monolíngues." },
    { t: "Polígono", sub: "Expansão de Público", d: "Mesmo time editorial do Poliedro, material mais enxuto e ticket mais acessível — não é upsell, é a porta de entrada para escolas fora do perfil de preço do sistema principal.\n\nCaptura demanda que hoje não fecha negócio com a Poliedro por preço, sem canibalizar a marca premium." },
  ];
  let cx = 0.6;
  const cw = 2.95;
  cards.forEach((c) => {
    s.addShape("roundRect", { x: cx, y: 1.75, w: cw, h: 4.95, rectRadius: 0.1, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("roundRect", { x: cx, y: 1.75, w: cw, h: 0.08, fill: { color: GOLD }, line: { type: "none" } });
    s.addText(c.t, { x: cx + 0.25, y: 2.05, w: cw - 0.5, h: 0.6, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: WHITE, valign: "top" });
    s.addText(c.sub, { x: cx + 0.25, y: 2.62, w: cw - 0.5, h: 0.4, fontFace: FONT_BODY, fontSize: 10, color: GOLD, bold: true });
    s.addText(c.d, { x: cx + 0.25, y: 3.15, w: cw - 0.5, h: 3.4, fontFace: FONT_BODY, fontSize: 10, color: MUTED, valign: "top", lineSpacingMultiple: 1.1 });
    cx += cw + 0.2;
  });

  addFooter(s, 2);
}

// ============ SLIDE 3 — TAM/SOM barra de progresso ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Potencial Represado de até R$80M na Base Atual");
  s.addText("Antes de olhar pra fora: quanto ainda dá pra crescer com quem já é cliente?", { x: 0.6, y: 1.1, w: 12, h: 0.4, fontFace: FONT_BODY, fontSize: 13.5, color: MUTED, italic: true });

  const barX = 0.9, barY = 3.0, barW = 11.3, barH = 0.85;
  const somFrac = 0.5;

  s.addText("SOM", { x: barX, y: barY - 0.32, w: 3.0, h: 0.3, fontFace: FONT_BODY, fontSize: 10.5, color: GOLD, bold: true, charSpacing: 1 });
  s.addText("TAM", { x: barX + barW - 2.2, y: barY - 0.32, w: 2.0, h: 0.3, fontFace: FONT_BODY, fontSize: 10.5, color: MUTED, align: "right", charSpacing: 1 });

  s.addShape("roundRect", { x: barX, y: barY, w: barW, h: barH, rectRadius: 0.12, fill: { color: CARD }, line: { color: BORDER, width: 1 } });
  s.addShape("roundRect", { x: barX, y: barY, w: barW * somFrac, h: barH, rectRadius: 0.12, fill: { color: GOLD }, line: { type: "none" } });

  s.addText("R$ 40M", { x: barX + 0.25, y: barY, w: 3.0, h: barH, fontFace: FONT_HEAD, fontSize: 24, bold: true, color: BG_DEEP, valign: "middle" });
  s.addText("R$ 80M", { x: barX + barW - 2.2, y: barY, w: 2.0, h: barH, fontFace: FONT_HEAD, fontSize: 22, bold: true, color: MUTED, align: "right", valign: "middle" });

  s.addText("SOM — meta de curto/médio prazo (50% de adesão da base atual)", {
    x: barX, y: barY + barH + 0.15, w: 6.0, h: 0.4, fontFace: FONT_BODY, fontSize: 11.5, color: GOLD, bold: true,
  });
  s.addText("TAM — teto de mercado se 100% da base aderir", {
    x: barX + barW - 5.0, y: barY + barH + 0.15, w: 5.0, h: 0.4, fontFace: FONT_BODY, fontSize: 11.5, color: MUTED, align: "right",
  });

  s.addText("À medida que escolas forem aderindo ao Conviver e Integrar, esta barra é o KPI natural de acompanhamento comercial.", {
    x: barX, y: barY + barH + 0.75, w: barW, h: 0.5, fontFace: FONT_BODY, fontSize: 11, color: FAINT, italic: true,
  });

  const stats = [
    ["230 mil", "alunos na base (site institucional)"],
    ["R$300-450", "ticket/aluno/ano cobrado pela concorrência (pesquisa própria)"],
    ["50%", "premissa de adesão de curto prazo usada no SOM"],
  ];
  let sx = 0.9;
  stats.forEach(([num, label]) => {
    s.addShape("roundRect", { x: sx, y: 5.15, w: 3.63, h: 1.45, rectRadius: 0.08, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addText(num, { x: sx + 0.25, y: 5.28, w: 3.13, h: 0.6, fontFace: FONT_HEAD, fontSize: 22, bold: true, color: GOLD });
    s.addText(label, { x: sx + 0.25, y: 5.9, w: 3.13, h: 0.6, fontFace: FONT_BODY, fontSize: 10.5, color: MUTED, valign: "top" });
    sx += 3.83;
  });

  s.addText("Estimativa com premissas explícitas.", {
    x: 0.9, y: 6.75, w: 11, h: 0.3, fontFace: FONT_BODY, fontSize: 9.5, color: FAINT, italic: true,
  });

  addFooter(s, 3);
}

// ============ SLIDE 4 — Cosmos hero ============
{
  const s = pres.addSlide();
  s.background = { color: BG_DEEP };
  s.addImage({ path: IMG + "cosmos_visual.png", x: 7.15, y: 0, w: 6.18, h: 7.5 });

  s.addText("O MOTOR DE DIFERENCIAÇÃO — IA APLICADA À SALA DE AULA", { x: 0.7, y: 0.55, w: 6.2, h: 0.35, fontFace: FONT_BODY, fontSize: 12, color: GOLD, charSpacing: 1.5, bold: true });
  s.addText("Expansão do Cosmos: IA que Reduz a Sobrecarga do Professor", { x: 0.65, y: 0.95, w: 6.3, h: 1.1, fontFace: FONT_HEAD, fontSize: 26, bold: true, color: WHITE });
  s.addText("O cosmos está sempre em expansão — o hub de IA da Poliedro também", { x: 0.7, y: 1.85, w: 6.1, h: 0.5, fontFace: FONT_BODY, fontSize: 13, color: MUTED, italic: true });

  s.addText(
    "Cosmos é o hub de IA integrado ao P+, a ferramenta de diagnóstico pedagógico da Poliedro: identifica dificuldades por turma e aluno, e apoia o professor na adaptação de atividades para alunos com TDAH, TEA e demais perfis de inclusão — aliviando o que hoje é uma das maiores fontes de sobrecarga do educador na escola particular.",
    { x: 0.7, y: 2.55, w: 6.1, h: 1.9, fontFace: FONT_BODY, fontSize: 12.5, color: WHITE, valign: "top", lineSpacingMultiple: 1.2 }
  );

  s.addShape("roundRect", { x: 0.7, y: 4.6, w: 6.1, h: 2.05, rectRadius: 0.1, fill: { color: GOLD_TINT }, line: { color: GOLD, width: 1 } });
  s.addText("Tese de posicionamento", { x: 0.95, y: 4.78, w: 5.6, h: 0.35, fontFace: FONT_HEAD, fontSize: 13, bold: true, color: GOLD });
  s.addText(
    "Concorrentes (SAS, Arco) usam IA de forma pontual — correção automática de redação. O Cosmos amplia o espectro de alunos atendidos e a carga pedagógica coberta.\n\nImportante: isto é um argumento de diferenciação, não uma medição comparativa de aprovação — esse dado não está disponível.",
    { x: 0.95, y: 5.15, w: 5.6, h: 1.4, fontFace: FONT_BODY, fontSize: 10.5, color: WHITE, valign: "top", lineSpacingMultiple: 1.1 }
  );

  addFooter(s, 4);
}

// ============ SLIDE 5 — PIVÔ: o teto do crescimento interno (NOVO) ============
{
  const s = pres.addSlide();
  s.background = { color: BG_DEEP };
  s.addShape("ellipse", { x: 10.5, y: -3, w: 7, h: 7, fill: { color: CARD, transparency: 35 }, line: { type: "none" } });

  s.addText("ATO II — O LIMITE DO CRESCIMENTO INTERNO", { x: 0.9, y: 0.7, w: 11, h: 0.4, fontFace: FONT_BODY, fontSize: 12.5, color: GOLD, charSpacing: 2, bold: true });
  s.addText("Mesmo com 100% de Adesão, Existe um Teto", { x: 0.85, y: 1.15, w: 11.5, h: 1.0, fontFace: FONT_HEAD, fontSize: 34, bold: true, color: WHITE });

  const cw = 5.35;
  s.addShape("roundRect", { x: 0.9, y: 2.7, w: cw, h: 2.9, rectRadius: 0.1, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
  s.addText("HOJE", { x: 1.2, y: 2.95, w: cw - 0.6, h: 0.35, fontFace: FONT_BODY, fontSize: 11, color: GOLD, bold: true, charSpacing: 1.5 });
  s.addText("Crescer dentro da base atual", { x: 1.2, y: 3.3, w: cw - 0.6, h: 0.6, fontFace: FONT_HEAD, fontSize: 17, bold: true, color: WHITE, valign: "top" });
  s.addText("230 mil alunos já matriculados na rede. Mesmo com 100% de adesão ao Conviver e Integrar, o teto de receita adicional é o TAM de R$80M já mostrado.", {
    x: 1.2, y: 4.05, w: cw - 0.6, h: 1.4, fontFace: FONT_BODY, fontSize: 12, color: MUTED, valign: "top", lineSpacingMultiple: 1.2,
  });

  s.addShape("ellipse", { x: 0.9 + cw + 0.35, y: 3.95, w: 0.9, h: 0.9, fill: { color: GOLD }, line: { type: "none" } });
  s.addText("→", { x: 0.9 + cw + 0.35, y: 3.95, w: 0.9, h: 0.9, fontFace: FONT_HEAD, fontSize: 26, bold: true, color: BG_DEEP, align: "center", valign: "middle" });

  const x2 = 0.9 + cw + 0.35 + 0.9 + 0.35;
  const cw2 = 12.1 - (x2 - 0.9);
  s.addShape("roundRect", { x: x2, y: 2.7, w: cw2, h: 2.9, rectRadius: 0.1, fill: { color: GOLD_TINT }, line: { color: GOLD, width: 1 } });
  s.addText("DEPOIS", { x: x2 + 0.3, y: 2.95, w: cw2 - 0.6, h: 0.35, fontFace: FONT_BODY, fontSize: 11, color: GOLD, bold: true, charSpacing: 1.5 });
  s.addText("Conquistar novas escolas", { x: x2 + 0.3, y: 3.3, w: cw2 - 0.6, h: 0.6, fontFace: FONT_HEAD, fontSize: 17, bold: true, color: WHITE, valign: "top" });
  s.addText("A pergunta muda: não é mais \"como vender mais pra quem já é cliente\", é \"quais das milhares de escolas privadas do Brasil têm o perfil certo pra se tornar cliente\".", {
    x: x2 + 0.3, y: 4.05, w: cw2 - 0.6, h: 1.4, fontFace: FONT_BODY, fontSize: 12, color: WHITE, valign: "top", lineSpacingMultiple: 1.2,
  });

  s.addText("É exatamente essa pergunta que o restante desta apresentação responde — com rigor de dados públicos (Censo Escolar INEP, ENEM, IBGE).", {
    x: 0.9, y: 6.0, w: 11.2, h: 0.6, fontFace: FONT_BODY, fontSize: 13, color: MUTED, italic: true, valign: "top",
  });

  addFooter(s, 5);
}

// ============ SLIDE 6 — Recorte e fontes ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Como Delimitar a Busca");
  const cards = [
    { t: "Escopo Geográfico", d: "Municípios com população total acima de 100.000 habitantes (filtro do case) — recorte nacional, sem restrição de região.", n: "319 municípios no Brasil" },
    { t: "Escopo de Escola", d: "Privada, não-filantrópica (exclui categoria 4 — APAE e similares), em atividade, com ao menos Ensino Médio (Censo 2025).", n: "8.095 escolas elegíveis" },
    { t: "Fontes Consultadas", d: "Censo Escolar INEP 2025 e Microdados ENEM 2025 — ambas de 2025, evitando descompasso de ano entre bases — mais IBGE (Censo 2022, renda e população).", n: "2 bases + IBGE" },
    { t: "Após o Filtro de População", d: "318 dos 319 municípios >100k têm ao menos 1 escola elegível (exceção: Ibirité/MG).", n: "5.647 escolas no recorte final" },
  ];
  let cy = 1.35;
  cards.forEach((c) => {
    s.addShape("roundRect", { x: 0.6, y: cy, w: 12.1, h: 1.28, rectRadius: 0.08, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("roundRect", { x: 0.6, y: cy, w: 0.09, h: 1.28, fill: { color: GOLD }, line: { type: "none" } });
    s.addText(c.t, { x: 0.95, y: cy + 0.12, w: 6.4, h: 0.4, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: WHITE });
    s.addText(c.d, { x: 0.95, y: cy + 0.52, w: 8.3, h: 0.65, fontFace: FONT_BODY, fontSize: 11, color: MUTED, valign: "top" });
    s.addText(c.n, { x: 9.5, y: cy, w: 3.05, h: 1.28, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: GOLD, align: "right", valign: "middle" });
    cy += 1.36;
  });
  addFooter(s, 6);
}

// ============ SLIDE 7 — Metodologia Parte 1 ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "O Potencial de uma Cidade Depende de 3 Fatores");
  s.addText("Score = média ponderada de 3 critérios, normalizados por percentil entre os 318 municípios elegíveis", { x: 0.6, y: 1.1, w: 11.5, h: 0.4, fontFace: FONT_BODY, fontSize: 13, color: MUTED, italic: true });

  const criterios = [
    { peso: "40%", t: "Potencial Socioeconômico", d: "Renda domiciliar per capita alta (Censo 2022, Tabela 10296) + população 0-17 anos. Mede poder de compra real das famílias — não PIB per capita, que mistura riqueza industrial com renda doméstica." },
    { peso: "30%", t: "Volume de Escolas Relevantes já Instaladas", d: "Quantidade de escolas privadas elegíveis no município. A pergunta não é só “onde tem dinheiro” — é onde já existe concentração de mercado educacional privado." },
    { peso: "30%", t: "Qualidade Acadêmica da Praça (ENEM)", d: "Média ENEM 2025 das escolas elegíveis do município. Proxy mais direto de prestígio acadêmico já reconhecido." },
  ];
  let cx = 0.6;
  const cw = 3.95;
  criterios.forEach((c) => {
    s.addShape("roundRect", { x: cx, y: 1.75, w: cw, h: 4.95, rectRadius: 0.1, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("ellipse", { x: cx + 0.35, y: 2.1, w: 1.1, h: 1.1, fill: { color: BG_DEEP }, line: { color: GOLD, width: 1 } });
    s.addText(c.peso, { x: cx + 0.35, y: 2.1, w: 1.1, h: 1.1, fontFace: FONT_HEAD, fontSize: 20, bold: true, color: GOLD, align: "center", valign: "middle" });
    s.addText(c.t, { x: cx + 0.35, y: 3.4, w: cw - 0.7, h: 0.9, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: WHITE, valign: "top" });
    s.addText(c.d, { x: cx + 0.35, y: 4.3, w: cw - 0.7, h: 2.25, fontFace: FONT_BODY, fontSize: 11, color: MUTED, valign: "top" });
    cx += cw + 0.25;
  });
  addFooter(s, 7);
}

// ============ SLIDE 8 — Top 10 cidades ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "As 10 Cidades Onde Renda e Prestígio Mais se Concentram");
  s.addImage({ path: IMG + "grafico_top10_cidades_dark.png", x: 1.1, y: 1.15, w: 11.1, h: 6.0 });
  addFooter(s, 8);
}

// ============ SLIDE 9 — Dispersão ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Por Que Praças Concentradas Superam Capitais Diluídas");
  s.addImage({ path: IMG + "grafico_dispersao_cidades_dark.png", x: 0.5, y: 1.0, w: 7.6, h: 6.05 });

  s.addShape("roundRect", { x: 8.35, y: 1.3, w: 4.4, h: 5.3, rectRadius: 0.1, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
  s.addText("O que Chama Atenção", { x: 8.7, y: 1.6, w: 3.7, h: 0.4, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: GOLD });
  s.addText(
    "São Paulo e Rio ficam fora do Top 10 — não por serem mercados fracos, mas por serem heterogêneos: riqueza e pobreza lado a lado diluem o percentil.\n\nPraças menores e concentradas (Niterói, Florianópolis, Vitória) pontuam mais alto: a riqueza ali é mais homogênea.\n\nSão José dos Campos é a sede do Poliedro — sua presença no Top 10 provavelmente reflete domínio de marca já existente, não oportunidade nova. Ler como \"defender\", não \"conquistar\".",
    { x: 8.7, y: 2.1, w: 3.75, h: 4.3, fontFace: FONT_BODY, fontSize: 11, color: MUTED, valign: "top", lineSpacingMultiple: 1.12 }
  );
  addFooter(s, 9);
}

// ============ SLIDE 10 — Metodologia Parte 2 ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Nem Toda Escola de Prestígio Representa a Mesma Oportunidade");
  s.addText("Aplicado às 4 cidades de maior score (Belo Horizonte, Niterói, Goiânia, Vitória) — topo do ranking anterior, cobrindo as duas versões do critério de qualidade ENEM", { x: 0.6, y: 1.1, w: 12, h: 0.5, fontFace: FONT_BODY, fontSize: 11.5, color: MUTED, italic: true });

  const criterios2 = [
    { peso: "60%", t: "Qualidade Acadêmica — ENEM 2025", d: "Média geral das 5 áreas dos participantes vinculados à escola. Resultado externo e verificável, o que constrói reputação publicamente visível." },
    { peso: "40%", t: "Infraestrutura de Prestígio — Censo 2025", d: "Índice 0-5: laboratório de ciências, laboratório de informática, biblioteca, quadra coberta, auditório." },
  ];
  let cx = 0.6;
  const cw = 5.85;
  criterios2.forEach((c) => {
    s.addShape("roundRect", { x: cx, y: 1.75, w: cw, h: 3.2, rectRadius: 0.1, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("ellipse", { x: cx + 0.35, y: 2.05, w: 1.0, h: 1.0, fill: { color: BG_DEEP }, line: { color: GOLD, width: 1 } });
    s.addText(c.peso, { x: cx + 0.35, y: 2.05, w: 1.0, h: 1.0, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: GOLD, align: "center", valign: "middle" });
    s.addText(c.t, { x: cx + 1.55, y: 2.05, w: cw - 1.9, h: 0.95, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: WHITE, valign: "top" });
    s.addText(c.d, { x: cx + 0.35, y: 3.15, w: cw - 0.7, h: 1.7, fontFace: FONT_BODY, fontSize: 11, color: MUTED, valign: "top" });
    cx += cw + 0.3;
  });

  s.addShape("roundRect", { x: 0.6, y: 5.2, w: 12.1, h: 1.55, rectRadius: 0.08, fill: { color: GOLD_TINT }, line: { color: GOLD, width: 1 } });
  s.addText("Critério de confiabilidade: escolas com menos de 10 participantes do ENEM vinculados não competem pelo Top 5. Volume de matrículas entra como contexto, não como score — mesmo tratamento dado ao PIB per capita nas versões anteriores deste projeto.", {
    x: 0.95, y: 5.35, w: 11.4, h: 1.25, fontFace: FONT_BODY, fontSize: 11, color: WHITE, valign: "middle",
  });
  addFooter(s, 10);
}

// ============ SLIDE 11 — Tabela Top5 ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "As Escolas que Melhor Traduzem Prestígio Acadêmico Local");
  s.addText("Top 5 por cidade — as duas versões (simples e ponderada) do critério de qualidade concordam nas 2 primeiras", { x: 0.6, y: 1.1, w: 12, h: 0.4, fontFace: FONT_BODY, fontSize: 11.5, color: MUTED, italic: true });

  const cidades = [
    {
      nome: "Belo Horizonte", nota: null,
      escolas: [
        ["Colégio Santo Agostinho", "722", "0.954"],
        ["Colégio Magnum Agostiniano", "695", "0.941"],
        ["Colégio Logosófico González Pecotche", "694", "0.940"],
        ["Escola SEB Unimaster", "686", "0.933"],
        ["Colégio Olimpo BH", "683", "0.931"],
      ],
    },
    {
      nome: "Niterói", nota: null,
      escolas: [
        ["Colégio Marília Mattoso", "728", "0.955"],
        ["Instituto Gaylussac", "713", "0.951"],
        ["ISJB - Col. Salesiano Região Oceânica", "655", "0.887"],
        ["Colégio e Curso Pensi", "759", "0.868"],
        ["Colégio Salesiano Santa Rosa", "644", "0.857"],
      ],
    },
    {
      nome: "Goiânia", nota: "Colégio Arena já é parceira Poliedro (depoimento no site institucional) — cidade já defendida, não é alvo de prospecção",
      escolas: [
        ["Colégio Arena", "695", "0.942"],
        ["Colégio Progressivo", "677", "0.925"],
        ["Colégio Prevest", "671", "0.918"],
        ["Colégio Visão", "670", "0.917"],
        ["Colégio JAO", "661", "0.901"],
      ],
    },
    {
      nome: "Vitória", nota: null,
      escolas: [
        ["Escola São Domingos", "713", "0.950"],
        ["Colégio Primeiro Mundo", "702", "0.946"],
        ["CE Leonardo da Vinci", "696", "0.942"],
        ["Colégio Salesiano Jardim Camburi", "689", "0.937"],
        ["Centro de Ensino Charles Darwin", "686", "0.933"],
      ],
    },
  ];

  const cw = 5.95, ch = 2.75;
  const posicoes = [[0.6, 1.65], [6.75, 1.65], [0.6, 4.55], [6.75, 4.55]];
  cidades.forEach((c, i) => {
    const [x, y] = posicoes[i];
    s.addShape("roundRect", { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("roundRect", { x, y, w: cw, h: 0.08, fill: { color: GOLD }, line: { type: "none" } });
    s.addText(c.nome, { x: x + 0.25, y: y + 0.12, w: cw - 0.5, h: 0.35, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: WHITE });

    s.addText("Escola", { x: x + 0.25, y: y + 0.5, w: cw - 2.0, h: 0.2, fontFace: FONT_BODY, fontSize: 7.5, color: FAINT, bold: true, charSpacing: 0.5 });
    s.addText("ENEM", { x: x + cw - 1.7, y: y + 0.5, w: 0.75, h: 0.2, fontFace: FONT_BODY, fontSize: 7.5, color: FAINT, bold: true, align: "center", charSpacing: 0.5 });
    s.addText("SCORE", { x: x + cw - 0.9, y: y + 0.5, w: 0.65, h: 0.2, fontFace: FONT_BODY, fontSize: 7.5, color: FAINT, bold: true, align: "center", charSpacing: 0.5 });

    let ly = y + 0.72;
    c.escolas.forEach((e) => {
      s.addText(e[0], { x: x + 0.25, y: ly, w: cw - 2.0, h: 0.28, fontFace: FONT_BODY, fontSize: 9.5, color: MUTED, valign: "middle" });
      s.addText(e[1], { x: x + cw - 1.7, y: ly, w: 0.75, h: 0.28, fontFace: FONT_BODY, fontSize: 9.5, color: FAINT, align: "center", valign: "middle" });
      s.addText(e[2], { x: x + cw - 0.9, y: ly, w: 0.65, h: 0.28, fontFace: FONT_HEAD, fontSize: 10, bold: true, color: GOLD, align: "center", valign: "middle" });
      ly += 0.3;
    });

    if (c.nota) {
      s.addText(c.nota, { x: x + 0.25, y: y + ch - 0.44, w: cw - 0.5, h: 0.38, fontFace: FONT_BODY, fontSize: 7.5, color: GOLD, italic: true, valign: "top" });
    }
  });

  addFooter(s, 11);
}

// ============ SLIDE 12 — Tabela completa de dados coletados ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "A Tabela Completa Por Trás do Score de Cada Escola");
  s.addText("As 20 escolas do Top 5 × 4 cidades — todas as variáveis usadas no score_destaque, lado a lado", { x: 0.6, y: 1.1, w: 12, h: 0.4, fontFace: FONT_BODY, fontSize: 12, color: MUTED, italic: true });

  const dadosEscolas = [
    ["Belo Horizonte", "Colégio Santo Agostinho", "314", "722", "62", "5", "1.070", "0.954"],
    ["Belo Horizonte", "Colégio Magnum Agostiniano", "11", "695", "20", "5", "63", "0.941"],
    ["Belo Horizonte", "Colégio Logosófico González Pecotche", "45", "694", "29", "5", "150", "0.940"],
    ["Belo Horizonte", "Escola SEB Unimaster", "26", "686", "27", "5", "69", "0.933"],
    ["Belo Horizonte", "Colégio Olimpo BH", "10", "683", "7", "5", "38", "0.931"],
    ["Niterói", "Colégio Marília Mattoso*", "10", "728", "202*", "5", "80", "0.955"],
    ["Niterói", "Instituto Gaylussac", "100", "713", "37", "5", "300", "0.951"],
    ["Niterói", "ISJB - Col. Salesiano Região Oceânica", "49", "655", "35", "5", "151", "0.887"],
    ["Niterói", "Colégio e Curso Pensi", "29", "759", "14", "4", "277", "0.868"],
    ["Niterói", "Colégio Salesiano Santa Rosa", "83", "644", "50", "5", "316", "0.857"],
    ["Goiânia", "Colégio Arena", "340", "695", "24", "5", "1.403", "0.942"],
    ["Goiânia", "Colégio Progressivo", "79", "677", "6", "5", "263", "0.925"],
    ["Goiânia", "Colégio Prevest", "124", "671", "21", "5", "490", "0.918"],
    ["Goiânia", "Colégio Visão", "55", "670", "20", "5", "119", "0.916"],
    ["Goiânia", "Colégio JAO", "55", "661", "16", "5", "218", "0.901"],
    ["Vitória", "Escola São Domingos", "74", "713", "26", "5", "256", "0.950"],
    ["Vitória", "Colégio Primeiro Mundo", "29", "702", "40", "5", "95", "0.946"],
    ["Vitória", "CE Leonardo da Vinci", "50", "696", "62", "5", "219", "0.942"],
    ["Vitória", "Colégio Salesiano Jardim Camburi", "57", "689", "32", "5", "225", "0.937"],
    ["Vitória", "Centro de Ensino Charles Darwin", "235", "686", "48", "5", "655", "0.933"],
  ];

  const headerCells = ["Cidade", "Escola", "Part. ENEM", "Média ENEM", "Salas", "Infra (0-5)", "Matríc. EM", "Score"].map((t) => ({
    text: t,
    options: { fill: { color: BG_DEEP }, color: GOLD, bold: true, fontFace: FONT_BODY, fontSize: 8.5, align: "center", valign: "middle" },
  }));

  const bodyRows = dadosEscolas.map((row, i) => {
    const bg = i % 2 === 0 ? CARD : BG_DEEP;
    return row.map((val, j) => ({
      text: val,
      options: {
        fill: { color: bg },
        color: j === 7 ? GOLD : j === 1 ? WHITE : MUTED,
        bold: j === 7,
        fontFace: j === 7 ? FONT_HEAD : FONT_BODY,
        fontSize: 8.5,
        align: j === 1 || j === 0 ? "left" : "center",
        valign: "middle",
      },
    }));
  });

  s.addTable([headerCells, ...bodyRows], {
    x: 0.6, y: 1.62, w: 12.1, h: 4.95,
    colW: [1.35, 4.2, 1.0, 1.1, 0.75, 0.9, 1.05, 0.85],
    border: { type: "solid", color: BORDER, pt: 0.5 },
    autoPage: false,
  });

  s.addText(
    "*Colégio Marília Mattoso reporta 202 salas para 80 matrículas no Médio — valor provavelmente top-codado pelo Censo: outras 12 escolas no Brasil, sem nenhuma relação entre si, reportam esse mesmo exato número (não afeta o score, que usa o índice de infraestrutura, não a contagem de salas).",
    { x: 0.6, y: 6.68, w: 12.1, h: 0.4, fontFace: FONT_BODY, fontSize: 8.5, color: FAINT, italic: true }
  );

  addFooter(s, 12);
}

// ============ SLIDE 13 — Funil (fomos além do case) ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Além do Case: de 8.095 Escolas a 869 Golden Leads");
  s.addText("O case pedia 3 cidades — aplicamos a mesma régua ao Brasil inteiro (recorte >100k hab.) pra abrir uma lista de prospecção comercial", { x: 0.6, y: 1.1, w: 12.1, h: 0.4, fontFace: FONT_BODY, fontSize: 12, color: MUTED, italic: true });
  s.addImage({ path: IMG + "funil_escolas.png", x: 0.9, y: 1.6, w: 11.5, h: 5.5 });
  addFooter(s, 13);
}

// ============ SLIDE 14 — Segmentação comercial ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "A Tese Comercial: as 330 “Desafiantes” São o Alvo Primário");
  s.addText("As 869 Golden Leads não são uma lista só — a posição de cada escola na própria cidade define a prioridade", { x: 0.6, y: 1.1, w: 12.1, h: 0.5, fontFace: FONT_BODY, fontSize: 12.5, color: MUTED, italic: true });

  s.addImage({ path: IMG + "segmentacao_comercial.png", x: 0.55, y: 1.7, w: 12.2, h: 4.35 });

  s.addShape("roundRect", { x: 0.6, y: 6.15, w: 12.1, h: 0.85, rectRadius: 0.08, fill: { color: GOLD_TINT }, line: { color: GOLD, width: 1 } });
  s.addText(
    "Tese comercial, não comprovada por dado (o Censo não informa o sistema de ensino atual de cada escola): a Desafiante tem motivo pra buscar uma vantagem sobre a líder, que já é referência e tem menos urgência de trocar.",
    { x: 0.95, y: 6.25, w: 11.4, h: 0.65, fontFace: FONT_BODY, fontSize: 10, color: WHITE, valign: "middle" }
  );

  addFooter(s, 14);
}

// ============ SLIDE 15 — Bairros piloto ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Já Sabemos Onde Começar: Bairro a Bairro");
  s.addText("167 Golden Leads das 10 cidades prioritárias, geocodificadas por CEP (ViaCEP)", { x: 0.6, y: 1.1, w: 12.1, h: 0.5, fontFace: FONT_BODY, fontSize: 12, color: MUTED, italic: true });

  const bairros = [
    { cidade: "Belo Horizonte", lider: "Santo Agostinho", desafiantes: ["Lourdes", "Santa Efigênia", "Buritis", "Mangabeiras"] },
    { cidade: "Niterói", lider: "São Domingos", desafiantes: ["São Francisco", "Piratininga", "Icaraí", "Santa Rosa"] },
    { cidade: "Goiânia", lider: "Setor Bueno", desafiantes: ["Cidade Jardim", "Setor Central", "Setor Bueno*", "Setor Jaó"] },
    { cidade: "Vitória", lider: "Bento Ferreira", desafiantes: ["Praia do Canto", "Santa Lúcia", "Jardim Camburi", "Mata da Praia"] },
  ];
  let cx = 0.6;
  const cw = 2.95;
  bairros.forEach((c) => {
    s.addShape("roundRect", { x: cx, y: 1.75, w: cw, h: 3.75, rectRadius: 0.1, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("roundRect", { x: cx, y: 1.75, w: cw, h: 0.08, fill: { color: GOLD }, line: { type: "none" } });
    s.addText(c.cidade, { x: cx + 0.25, y: 2.0, w: cw - 0.5, h: 0.4, fontFace: FONT_HEAD, fontSize: 14, bold: true, color: WHITE });
    s.addText("Líder local", { x: cx + 0.25, y: 2.45, w: cw - 0.5, h: 0.3, fontFace: FONT_BODY, fontSize: 9, color: GOLD, bold: true });
    s.addText(c.lider, { x: cx + 0.25, y: 2.72, w: cw - 0.5, h: 0.4, fontFace: FONT_BODY, fontSize: 11, color: WHITE });
    s.addText("Desafiantes (2º-5º)", { x: cx + 0.25, y: 3.25, w: cw - 0.5, h: 0.3, fontFace: FONT_BODY, fontSize: 9, color: GOLD, bold: true });
    s.addText(c.desafiantes.join("\n"), { x: cx + 0.25, y: 3.52, w: cw - 0.5, h: 1.85, fontFace: FONT_BODY, fontSize: 10.5, color: MUTED, valign: "top", lineSpacingMultiple: 1.3 });
    cx += cw + 0.2;
  });

  s.addShape("roundRect", { x: 0.6, y: 5.7, w: 12.1, h: 1.3, rectRadius: 0.08, fill: { color: GOLD_TINT }, line: { color: GOLD, width: 1 } });
  s.addText(
    "Leitura qualitativa: líder e desafiantes caem nos bairros mais tradicionais das 4 cidades — nenhuma Golden Lead é periférica. *Em Goiânia, líder e desafiante (Col. Visão) dividem o Setor Bueno. Bairro não é renda comprovada; cruzar com setor censitário do IBGE é o próximo passo, fora do escopo desta entrega.",
    { x: 0.95, y: 5.82, w: 11.4, h: 1.05, fontFace: FONT_BODY, fontSize: 9.5, color: WHITE, valign: "top", lineSpacingMultiple: 1.15 }
  );

  addFooter(s, 15);
}

// ============ SLIDE 16 — Limitações ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Rigor Executivo: o que os Dados Revelam e o que Não Capturam");
  const limites = [
    ["Vínculo Escola-Participante Mudou em 2025", "~36% dos participantes do ENEM têm escola vinculada — isso é por aluno, não por escola. Das 5.647 elegíveis, 73% (4.121) têm média confiável (≥10 vinculados). As 1.526 restantes são majoritariamente escolas menores (mediana de 31 matrículas no Médio, ante 114 das confiáveis) — 93% delas têm zero participante vinculado, não “poucos”."],
    ["Viés Regional na Adesão ao ENEM", "Praças com vestibular próprio forte (SP: USP, Unicamp) podem ter escolas de elite subestimadas na média ENEM."],
    ["“Salas Vitrine” de Redes de Ensino", "Padrão nacional, não isolado: 4 grupos confirmados (ex. Farias Brito, Fortaleza/CE — uma unidade com 220 alunos e média 656 convive com outra do mesmo grupo, 30 alunos e média 793). Não afeta as 20 escolas do Top 5×4 aqui, mas atinge ~4 das 869 Golden Leads."],
    ["Segmento Comercial não é o Sistema de Ensino Real", "A tag Líder/Desafiante usa só posição acadêmica. Cerca de metade já usa sistema concorrente — checagem individual é necessária antes de prospectar."],
  ];
  let cy = 1.35;
  limites.forEach((l) => {
    s.addShape("roundRect", { x: 0.6, y: cy, w: 12.1, h: 1.28, rectRadius: 0.08, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("ellipse", { x: 0.85, y: cy + 0.29, w: 0.7, h: 0.7, fill: { color: GOLD }, line: { type: "none" } });
    s.addText("!", { x: 0.85, y: cy + 0.29, w: 0.7, h: 0.7, fontFace: FONT_HEAD, fontSize: 20, bold: true, color: BG_DEEP, align: "center", valign: "middle" });
    s.addText(l[0], { x: 1.75, y: cy + 0.1, w: 4.7, h: 1.08, fontFace: FONT_HEAD, fontSize: 12.5, bold: true, color: WHITE, valign: "middle" });
    s.addText(l[1], { x: 6.55, y: cy + 0.1, w: 6.0, h: 1.08, fontFace: FONT_BODY, fontSize: 9.5, color: MUTED, valign: "middle" });
    cy += 1.36;
  });
  addFooter(s, 16);
}

// ============ SLIDE 17 — Encerramento: plano de ação faseado ============
{
  const s = pres.addSlide();
  s.background = { color: BG_DEEP };
  s.addShape("ellipse", { x: -2, y: 5.2, w: 6, h: 6, fill: { color: CARD, transparency: 35 }, line: { type: "none" } });
  s.addText("ATO IV — PLANO DE AÇÃO", { x: 0.6, y: 0.55, w: 10, h: 0.4, fontFace: FONT_BODY, fontSize: 13, color: GOLD, bold: true, charSpacing: 1.5 });
  s.addText("Do Pipeline de Dados à Prospecção de Campo", { x: 0.6, y: 0.95, w: 12, h: 0.85, fontFace: FONT_HEAD, fontSize: 30, bold: true, color: WHITE });

  const fases = [
    {
      fase: "FASE 1", prazo: "Semanas 1-2", titulo: "Validação",
      d: "Em paralelo — não depende de validação, começa já: campanha de adesão ao Conviver e Integrar na safra de rematrícula (ago-set). No lado externo: selecionar ~15 “Desafiantes” em BH, Niterói e Vitória para piloto — confirmar manualmente o sistema de ensino atual antes de qualquer oferta.",
    },
    {
      fase: "FASE 2", prazo: "Mês 1", titulo: "Piloto",
      d: "Expandir para as 330 “Desafiantes” das 10 cidades prioritárias — exceto cidades onde já temos presença confirmada (ex.: Goiânia, via Colégio Arena). Cruzar com a carteira atual de escolas parceiras para priorizar cross-sell de Conviver e Integrar e Cosmos.",
    },
    {
      fase: "FASE 3", prazo: "Mês 2+", titulo: "Escala",
      d: "Levar o piloto de geolocalização por bairro (hoje 167 escolas) às 869 Golden Leads nacionais. Sobrepor a presença de concorrentes por cidade para fechar os gaps reais de cobertura.",
    },
  ];
  let cx = 0.6;
  const cw = 3.97;
  fases.forEach((f) => {
    s.addShape("roundRect", { x: cx, y: 2.05, w: cw, h: 3.55, rectRadius: 0.1, fill: { color: CARD }, line: { color: BORDER, width: 0.75 } });
    s.addShape("roundRect", { x: cx, y: 2.05, w: cw, h: 0.08, fill: { color: GOLD }, line: { type: "none" } });
    s.addText(f.fase, { x: cx + 0.3, y: 2.3, w: cw - 0.6, h: 0.3, fontFace: FONT_BODY, fontSize: 11, color: GOLD, bold: true, charSpacing: 1.5 });
    s.addText(f.prazo, { x: cx + 0.3, y: 2.3, w: cw - 0.6, h: 0.3, fontFace: FONT_BODY, fontSize: 10.5, color: FAINT, align: "right" });
    s.addText(f.titulo, { x: cx + 0.3, y: 2.65, w: cw - 0.6, h: 0.55, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: WHITE, valign: "top" });
    s.addText(f.d, { x: cx + 0.3, y: 3.3, w: cw - 0.6, h: 2.15, fontFace: FONT_BODY, fontSize: 11, color: MUTED, valign: "top", lineSpacingMultiple: 1.2 });
    cx += cw + 0.19;
  });

  s.addText("Metodologia completa, código-fonte e limitações documentadas no material em anexo.", {
    x: 0.6, y: 6.0, w: 12, h: 0.5, fontFace: FONT_BODY, fontSize: 11.5, color: FAINT, italic: true,
  });
}

// ============ SLIDE 18 — Roadmap técnico de evolução ============
{
  const s = pres.addSlide();
  bgSlide(s);
  cardHeader(s, "Da Inteligência Descritiva à Inteligência Preditiva");
  s.addText("Cada etapa depende da anterior — do pipeline atual a um modelo preditivo de prospecção", { x: 0.6, y: 1.1, w: 12, h: 0.4, fontFace: FONT_BODY, fontSize: 12.5, color: MUTED, italic: true });

  const passos = [
    { v: "1.0", tag: "ATUAL", t: "Pipeline Reproduzível", d: "Python + Censo Escolar, ENEM e IBGE — score de cidades e escolas, funil, segmentação comercial e piloto de geolocalização, documentado e pronto para reexecução.", destaque: false },
    { v: "2.0", tag: "PRÓXIMO", t: "Inteligência Comercial em Tempo Real", d: "Painel interativo (Power BI): filtros por UF, cidade e segmento comercial, para o time comercial explorar os dados sem depender de planilha.", destaque: false },
    { v: "3.0", tag: "CURTO PRAZO", t: "Microsegmentação Geográfica", d: "Cruzar o CEP já geocodificado com o setor censitário do IBGE (join espacial via geopandas) — fecha o piloto de bairros com renda de verdade, não só leitura qualitativa.", destaque: false },
    { v: "4.0", tag: "MÉDIO PRAZO", t: "Visibilidade da Concorrência", d: "Geolocalizar unidades de sistemas concorrentes (Arco, SAS, Eleva etc.) nas 10 cidades prioritárias para achar os gaps reais de cobertura.", destaque: false },
    { v: "5.0", tag: "PROJETO FUTURO — PRÓXIMAS SEMANAS", t: "Modelo Preditivo de Prospecção (Lookalike)", d: "Usar dado interno de engajamento dos clientes atuais do Poliedro para treinar um modelo que aponta escolas com o mesmo perfil dos melhores clientes já existentes. Depende de dado interno que não temos hoje — não incluído nesta entrega.", destaque: true },
  ];

  let py = 1.6;
  const rowH = 0.92;
  passos.forEach((p) => {
    const bg = p.destaque ? GOLD_TINT : CARD;
    const border = p.destaque ? GOLD : BORDER;
    s.addShape("roundRect", { x: 0.6, y: py, w: 12.1, h: rowH - 0.1, rectRadius: 0.08, fill: { color: bg }, line: { color: border, width: p.destaque ? 1 : 0.75 } });
    s.addShape("ellipse", { x: 0.85, y: py + 0.11, w: 0.65, h: 0.65, fill: { color: BG_DEEP }, line: { color: GOLD, width: 1 } });
    s.addText(p.v, { x: 0.85, y: py + 0.11, w: 0.65, h: 0.65, fontFace: FONT_HEAD, fontSize: 12, bold: true, color: GOLD, align: "center", valign: "middle" });
    s.addText(p.t, { x: 1.7, y: py + 0.06, w: 4.65, h: 0.4, fontFace: FONT_HEAD, fontSize: 12.5, bold: true, color: WHITE, valign: "top" });
    if (p.tag) {
      s.addText(p.tag, { x: 1.7, y: py + 0.46, w: 4.65, h: 0.28, fontFace: FONT_BODY, fontSize: 7.5, color: GOLD, bold: true, charSpacing: 1 });
    }
    s.addText(p.d, { x: 6.45, y: py + 0.06, w: 6.05, h: rowH - 0.2, fontFace: FONT_BODY, fontSize: 9, color: p.destaque ? WHITE : MUTED, valign: "middle", lineSpacingMultiple: 1.08 });
    py += rowH;
  });

  s.addText("Cada etapa reduz a dependência de decisões intuitivas e aumenta a precisão da prospecção comercial.", {
    x: 0.6, y: py + 0.08, w: 12.1, h: 0.4, fontFace: FONT_BODY, fontSize: 10.5, color: FAINT, italic: true,
  });

  addFooter(s, 18);
}

pres.writeFile({ fileName: "Poliedro_Apresentacao_Completa.pptx" }).then(() => {
  console.log("Apresentação gerada com sucesso: Poliedro_Apresentacao_Completa.pptx");
});
