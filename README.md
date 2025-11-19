# Projeto de Engenharia de Dados para Inteligência de Mercado do Agronegócio

## 1. Arquitetura do Projeto e Stack Tecnológica

O objetivo deste projeto é estabelecer um pipeline de dados automatizado e confiável para coletar, processar e armazenar informações do agronegócio brasileiro, garantindo a atualização semanal necessária para os relatórios de inteligência de mercado da diretoria.

### 1.1. Arquitetura Proposta: Pipeline ETL Simplificado

A arquitetura será baseada em um pipeline de **ETL (Extract, Transform, Load)**, ideal para processamento em lote e ingestão de dados estruturados de fontes externas.

| Etapa | Descrição | Ferramentas Chave | Frequência |
| :--- | :--- | :--- | :--- |
| **Extract (Extração)** | Coleta de dados brutos das fontes (CONAB, IBGE, CEPEA/USP) via Web Scraping ou APIs. | Python (`requests`, `BeautifulSoup`, `Selenium`, `pandas`) | Semanal |
| **Transform (Transformação)** | Limpeza, padronização, enriquecimento e estruturação dos dados brutos em um formato analítico. | Python (`pandas`, SQL) | Semanal |
| **Load (Carga)** | Inserção dos dados transformados no banco de dados central. | PostgreSQL (via Python `psycopg2` ou `SQLAlchemy`) | Semanal |
| **Orchestration (Orquestração)** | Agendamento e monitoramento da execução semanal do pipeline. | Apache Airflow (Recomendado para Escala) ou Cron Job (Para Início Rápido) | Semanal |

### 1.2. Stack Tecnológica Recomendada

A escolha da stack tecnológica visa a robustez, a facilidade de manutenção e a compatibilidade com o ecossistema de dados.

| Componente | Tecnologia | Justificativa |
| :--- | :--- | :--- |
| **Linguagem de Programação** | **Python 3.x** | Padrão da indústria para engenharia de dados, com bibliotecas maduras para web scraping (`BeautifulSoup`, `Selenium`), manipulação de dados (`pandas`) e conectividade com bancos de dados. |
| **Banco de Dados (Data Warehouse)** | **PostgreSQL** | Banco de dados relacional robusto, de código aberto, ideal para armazenar dados estruturados e suportar consultas analíticas complexas. |
| **Orquestração/Agendamento** | **Apache Airflow** | Ferramenta líder para definir, agendar e monitorar fluxos de trabalho (DAGs). Permite o agendamento preciso da execução semanal e o tratamento de falhas. |
| **Ambiente de Desenvolvimento** | **Git** e **Ambientes Virtuais** | Controle de versão e isolamento de dependências para garantir a reprodutibilidade do projeto. |

## 2. Estratégia de Ingestão de Dados (Extract)

A fase de extração é a mais crítica, pois lida com a heterogeneidade das fontes de dados. A estratégia detalhada para cada fonte é a seguinte:

### 2.1. CONAB (Companhia Nacional de Abastecimento)

A CONAB publica seus dados de safra em boletins mensais, geralmente em formato PDF ou Excel, e dados de mercado em painéis interativos.

| Fonte Específica | URL de Referência | Estratégia de Extração | Ferramentas Python |
| :--- | :--- | :--- | :--- |
| **Boletim da Safra de Grãos** | [CONAB Safras [1]]() | **Download e Parsing de Arquivos:** O pipeline deve monitorar a página de safras e, ao identificar um novo boletim (geralmente na segunda semana do mês), baixar o arquivo (PDF ou Excel) e utilizar bibliotecas para extrair as tabelas de área, produção e estimativas. | `requests`, `tabula-py` (para PDF), `openpyxl` (para Excel) |
| **Produtos 360° (Preços)** | [CONAB Produtos 360°]() | **Web Scraping:** Simular a navegação no painel interativo para selecionar o produto (milho, soja, etc.) e extrair a tabela de "Conjuntura Semanal" ou "Preço Mínimo x Preço Recebido pelo Produtor". | `requests`, `BeautifulSoup` ou `Selenium` |

### 2.2. IBGE (Instituto Brasileiro de Geografia e Estatística)

O IBGE é a fonte primária para dados de abates e produção agrícola municipal (LSPA).

| Fonte Específica | URL de Referência | Estratégia de Extração | Ferramentas Python |
| :--- | :--- | :--- | :--- |
| **Pesquisa Trimestral do Abate de Animais** | [IBGE Abates [2]]() | **Web Scraping/SIDRA:** Acessar a página da pesquisa e, idealmente, utilizar a interface do **SIDRA** (Sistema IBGE de Recuperação Automática) para extrair as tabelas de abates de bovinos, suínos e frangos. O SIDRA permite a exportação direta para formatos estruturados como CSV. | `requests`, `BeautifulSoup` (para simular a interação com o SIDRA) |
| **LSPA (Levantamento Sistemático da Produção Agrícola)** | [IBGE LSPA [3]]() | **Web Scraping/SIDRA:** Similar à pesquisa de abates, extrair as tabelas de área plantada e produção para as culturas de interesse. | `requests`, `BeautifulSoup` |

### 2.3. CEPEA/USP (Centro de Estudos Avançados em Economia Aplicada)

O CEPEA é a referência para cotações de mercado de alta frequência.

| Fonte Específica | URL de Referência | Estratégia de Extração | Ferramentas Python |
| :--- | :--- | :--- | :--- |
| **Cotações Diárias/Semanais** | [CEPEA/USP [4]]() | **Web Scraping:** Acessar as páginas de cotações de produtos específicos (Ex: Boi Gordo, Milho Esalq) e extrair as tabelas de preços mais recentes. A extração deve ser configurada para capturar o dado mais recente da semana. | `requests`, `BeautifulSoup`, `pandas` (para ler tabelas HTML) |

### 2.4. COMEX STAT (Comércio Exterior)

Para dados de exportação/importação, que impactam diretamente o mercado.

| Fonte Específica | URL de Referência | Estratégia de Extração | Ferramentas Python |
| :--- | :--- | :--- | :--- |
| **Estatísticas de Comércio Exterior** | [COMEX STAT [5]]() | **Download de Arquivos:** O COMEX STAT disponibiliza grandes bases de dados para download. A estratégia é baixar os arquivos mensais de exportação/importação e filtrar pelos códigos NCM (Nomenclatura Comum do Mercosul) dos produtos do agronegócio de interesse. | `requests`, `pandas` (para processamento de grandes CSVs) |

A orquestração via Airflow garantirá que essas rotinas de extração sejam executadas de forma sequencial e que as falhas sejam tratadas, garantindo a integridade dos dados antes da fase de Transformação.

## 3. Projeto do Esquema do Banco de Dados (Data Model)

A extração de dados requer abordagens específicas para cada fonte, devido à ausência de APIs públicas padronizadas para a maioria dos dados de agronegócio.

| Fonte de Dados | Tipo de Dado | Estratégia de Extração | Desafios e Soluções |
| :--- | :--- | :--- | :--- |
| **CONAB - Boletim da Safra de Grãos** | Área Plantada, Produção, Estimativas (Mensal) | **Web Scraping/Download de PDF/Excel:** Acessar a página de boletins mensais e extrair dados das tabelas ou baixar os arquivos anexos (PDF/Excel) para processamento. | **Desafio:** PDFs e Excel exigem bibliotecas específicas (ex: `tabula-py` para PDF, `openpyxl` para Excel) para extrair tabelas. **Solução:** Implementar rotinas de parsing robustas. |
| **IBGE - Pesquisa Trimestral do Abate de Animais** | Abates (Bovinos, Suínos, Frangos) (Trimestral) | **Web Scraping/SIDRA:** Utilizar o sistema SIDRA do IBGE, que permite a extração de tabelas de dados. Em alguns casos, pode ser necessário simular a navegação para obter a tabela desejada. | **Desafio:** A frequência é trimestral, não semanal. **Solução:** A ingestão semanal garantirá que o dado mais recente seja capturado assim que for publicado (a cada 3 meses). |
| **CEPEA/USP - Cotações e Preços** | Preços de Commodities (Diário/Semanal) | **Web Scraping:** Acessar as páginas de cotações e extrair as tabelas de preços semanais ou diários. | **Desafio:** Estrutura do site pode mudar. **Solução:** Usar seletores CSS/XPath robustos e monitorar a rotina de extração. |
| **COMEX STAT** | Dados de Comércio Exterior (Diário/Mensal) | **API/Download de Arquivos:** O COMEX STAT oferece APIs ou arquivos para download que podem ser consumidos diretamente. | **Solução:** Priorizar o uso de APIs para maior estabilidade e automação. |

## 3. Projeto do Esquema do Banco de Dados (Data Model)

O modelo de dados será um esquema relacional simples, focado na facilidade de consulta para relatórios. A estrutura será baseada em tabelas Fato (para métricas) e tabelas Dimensão (para contexto).

### Tabela Fato: `fato_producao_agronegocio`

Esta tabela armazenará as métricas principais de produção e abates.

| Coluna | Tipo de Dado | Descrição | Fonte |
| :--- | :--- | :--- | :--- |
| `id_registro` | SERIAL (PK) | Chave primária. | Gerado |
| `data_referencia` | DATE | Data de referência do dado (Ex: Fim da semana, Mês de publicação). | CONAB/IBGE/CEPEA |
| `id_dim_produto` | INT (FK) | Chave para a tabela `dim_produto`. | Gerado |
| `id_dim_localidade` | INT (FK) | Chave para a tabela `dim_localidade`. | Gerado |
| `area_plantada_ha` | NUMERIC | Área plantada em hectares (CONAB/IBGE). | CONAB/IBGE |
| `producao_ton` | NUMERIC | Quantidade produzida em toneladas (CONAB/IBGE). | CONAB/IBGE |
| `estimativa_ton` | NUMERIC | Estimativa de produção (CONAB). | CONAB |
| `abates_cabecas` | INT | Número de cabeças abatidas (IBGE). | IBGE |
| `peso_carcaca_kg` | NUMERIC | Peso total das carcaças em kg (IBGE). | IBGE |
| `preco_medio_rs` | NUMERIC | Preço médio por unidade (CEPEA/USP). | CEPEA/USP |
| `data_ingestao` | TIMESTAMP | Data e hora da ingestão no banco de dados. | Gerado |

### Tabela Dimensão: `dim_produto`

| Coluna | Tipo de Dado | Descrição |
| :--- | :--- | :--- |
| `id_dim_produto` | SERIAL (PK) | Chave primária. |
| `nome_produto` | VARCHAR | Nome do produto (Ex: 'Soja', 'Milho', 'Bovino'). |
| `categoria` | VARCHAR | Categoria (Ex: 'Grãos', 'Pecuária'). |

### Tabela Dimensão: `dim_localidade`

| Coluna | Tipo de Dado | Descrição |
| :--- | :--- | :--- |
| `id_dim_localidade` | SERIAL (PK) | Chave primária. |
| `uf` | VARCHAR | Unidade da Federação (Ex: 'MT', 'SP'). |
| `regiao` | VARCHAR | Região (Ex: 'Centro-Oeste'). |

## 4. Plano de Transformação e Camada de Apresentação (Reporting Layer)

A etapa de Transformação (T) é crucial para garantir que os dados sejam consistentes e prontos para o consumo.

### 4.1. Processos de Transformação (T)

1.  **Padronização de Datas:** Converter todas as referências de tempo (semanal, mensal, trimestral) para um formato de data consistente (Ex: o primeiro dia da semana ou o último dia do mês/trimestre).
2.  **Enriquecimento de Dados:** Utilizar as tabelas dimensão para adicionar contexto. Por exemplo, associar o estado (UF) a uma região.
3.  **Cálculo de Métricas Derivadas:** Calcular métricas importantes para a diretoria, como:
    *   Variação Semanal/Mensal/Anual (`producao_ton` vs. período anterior).
    *   Produtividade (`producao_ton` / `area_plantada_ha`).
    *   Margem Bruta (combinando `preco_medio_rs` com estimativas de custo, se disponíveis).
4.  **Tratamento de Nulos:** Preencher ou sinalizar dados ausentes (Ex: dados de abates são trimestrais, então 2 meses da semana terão valores nulos até a próxima publicação).

### 4.2. Camada de Apresentação (Reporting Layer)

A camada de apresentação é o conjunto de ferramentas e processos que transforma os dados do PostgreSQL em relatórios visuais para a diretoria.

| Ferramenta | Uso | Frequência de Relatório |
| :--- | :--- | :--- |
| **SQL Views/Stored Procedures** | Criar visões pré-agregadas no PostgreSQL para otimizar o desempenho das consultas de relatórios. | Semanal |
| **Ferramenta de BI (Business Intelligence)** | **Power BI, Tableau, Google Data Studio (Looker Studio)** ou **Metabase (Open Source)**. | Semanal |
| **Relatórios de Diretoria** | Apresentações semanais (PowerPoint/Google Slides) com gráficos e análises extraídas da ferramenta de BI. | Semanal |

### 4.3. Fluxo de Trabalho Semanal

1.  **Segunda-feira (Madrugada):** O Airflow dispara o pipeline ETL.
2.  **Segunda-feira (Manhã):** Extração, Transformação e Carga dos dados mais recentes.
3.  **Segunda-feira (Tarde):** As ferramentas de BI se conectam ao PostgreSQL (ou às Views) e atualizam os dashboards.
4.  **Terça-feira:** A equipe de inteligência de mercado utiliza os dashboards atualizados para montar a apresentação semanal para a diretoria.

Este plano fornece uma base sólida para a construção de um sistema de inteligência de mercado automatizado e escalável.

# Fontes de Dados para Inteligência de Mercado do Agronegócio Brasileiro

## Introdução

Este relatório compila as principais fontes de dados oficiais e confiáveis para a elaboração de relatórios de inteligência de mercado sobre o agronegócio no Brasil. As fontes foram selecionadas com foco em dados de alta frequência (diária, semanal ou mensal) sobre **área plantada**, **quantidade produzida**, **abates de frigoríficos** (gado, aves e suínos) e **estimativas de safras**.

Embora a frequência diária ou semanal seja rara para dados estruturais como área plantada e produção nacional (que são predominantemente mensais ou trimestrais), as fontes listadas abaixo oferecem a maior granularidade e confiabilidade disponíveis no mercado.

## 1. Companhia Nacional de Abastecimento (CONAB)

A CONAB é a principal fonte para dados de safras e estimativas de produção agrícola no Brasil.

| Tipo de Dado | Fonte Específica | Frequência de Atualização | Detalhamento |
| :--- | :--- | :--- | :--- |
| **Área Plantada, Produção e Estimativas** | **Boletim da Safra de Grãos** | Mensal | Abrange soja, milho, arroz, feijão, algodão e outros grãos. Contém projeções de área, produtividade e produção para a safra atual. |
| **Área Plantada, Produção e Estimativas** | **Boletim da Safra de Café e Cana-de-Açúcar** | Quadrimestral | Estimativas específicas para café e cana-de-açúcar. |
| **Preços e Conjuntura** | **Portal de Informações Agropecuárias - Produtos 360°** | Semanal/Diário (para preços) | Oferece dados de preços médios semanais por estado para diversos produtos (milho, soja, arroz, etc.) e análises de conjuntura. |
| **Acesso a Dados Brutos** | **Portal de Dados Abertos da CONAB** | Variável | Pode conter bases de dados para download, dependendo da política de dados abertos vigente. |

**Instruções de Acesso:**
*   **Boletins de Safra:** Acompanhe a seção "Acompanhamento da Safra Brasileira" no portal do Governo Federal: [https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras]()
*   **Produtos 360°:** Acesse o painel interativo para dados de preços e conjuntura: [https://portaldeinformacoes.conab.gov.br/produtos-360.html]()

## 2. Instituto Brasileiro de Geografia e Estatística (IBGE)

O IBGE é a fonte oficial para estatísticas de produção e abates de animais.

| Tipo de Dado | Fonte Específica | Frequência de Atualização | Detalhamento |
| :--- | :--- | :--- | :--- |
| **Abates de Frigoríficos** | **Pesquisa Trimestral do Abate de Animais** | Trimestral | Dados de número de cabeças abatidas e peso total das carcaças de **bovinos**, **suínos** e **frangos**, por Unidade da Federação. |
| **Área Plantada e Produção** | **Levantamento Sistemático da Produção Agrícola (LSPA)** | Mensal | Estimativas de área plantada, área colhida, produção e rendimento médio de culturas temporárias e permanentes. |
| **Acesso a Dados Brutos** | **SIDRA (Sistema IBGE de Recuperação Automática)** | Variável | Plataforma para consulta e download de tabelas detalhadas das pesquisas, permitindo maior granularidade e séries históricas. |

**Instruções de Acesso:**
*   **Abates de Animais:** Acesse a página da pesquisa: [https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9203-pesquisas-trimestrais-do-abate-de-animais.html]()
*   **LSPA:** Acesse a página da pesquisa: [https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9201-levantamento-sistematico-da-producao-agricola.html]()
*   **SIDRA:** Utilize o sistema para extrair dados em formato de tabela: [https://sidra.ibge.gov.br/]()

## 3. Fontes Complementares de Alta Frequência (Preços e Mercado)

Para obter a frequência diária ou semanal solicitada, o foco deve ser em dados de mercado, como preços e cotações, que refletem a dinâmica de oferta e demanda em tempo real.

| Tipo de Dado | Fonte Específica | Frequência de Atualização | Detalhamento |
| :--- | :--- | :--- | :--- |
| **Cotações e Preços** | **CEPEA/USP (Centro de Estudos Avançados em Economia Aplicada)** | Diária/Semanal | Referência em preços de commodities agrícolas e pecuárias (boi gordo, milho, soja, etc.). Publica boletins e índices de preços. |
| **Notícias e Análises de Mercado** | **Canal Rural, Agências de Notícias (Broadcast Agro, Reuters)** | Diária | Fornecem análises de conjuntura, notícias sobre escalas de abate, clima e estimativas de mercado de fontes privadas. |
| **Dados de Exportação/Importação** | **COMEX STAT (Ministério da Economia)** | Diária/Mensal | Dados detalhados de comércio exterior por produto e país, essenciais para a inteligência de mercado. |

**Instruções de Acesso:**
*   **CEPEA/USP:** [https://www.cepea.esalq.usp.br/]()
*   **COMEX STAT:** [https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/comex-stat]()

## Resumo e Recomendações para Relatórios

Para construir relatórios de inteligência de mercado robustos, a recomendação é integrar as informações das fontes oficiais com a alta frequência dos dados de mercado:

1.  **Dados Estruturais (Mensal/Trimestral):** Utilize **CONAB (Safras)** e **IBGE (Abates e LSPA)** para a base de área plantada, produção e volume de abates. Estes dados fornecem a visão macro e as tendências de longo prazo.
2.  **Dados de Conjuntura (Diário/Semanal):** Utilize **CEPEA/USP** para acompanhar a variação de preços e **notícias de mercado** para entender a dinâmica de curto prazo (ex: escalas de abate, impacto do clima, movimentação de exportação).

A combinação dessas fontes permitirá que seus relatórios forneçam tanto a análise fundamental (baseada em dados oficiais de produção) quanto a análise de mercado (baseada em preços e conjuntura em tempo real).

***

**Referências**

[1] Companhia Nacional de Abastecimento (CONAB). *Acompanhamento da Safra Brasileira*. [https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras]()
[2] Instituto Brasileiro de Geografia e Estatística (IBGE). *Pesquisa Trimestral do Abate de Animais*. [https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9203-pesquisas-trimestrais-do-abate-de-animais.html]()
[3] Instituto Brasileiro de Geografia e Estatística (IBGE). *Levantamento Sistemático da Produção Agrícola (LSPA)*. [https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9201-levantamento-sistematico-da-producao-agricola.html]()
[4] Centro de Estudos Avançados em Economia Aplicada (CEPEA/USP). *Cotações e Preços*. [https://www.cepea.esalq.usp.br/]()
[5] Ministério da Economia. *COMEX STAT - Estatísticas de Comércio Exterior*. [https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/comex-stat]()


[6] Companhia Nacional de Abastecimento (CONAB). *Acompanhamento da Safra Brasileira*. [https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras]()
[7] Instituto Brasileiro de Geografia e Estatística (IBGE). *Pesquisa Trimestral do Abate de Animais*. [https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9203-pesquisas-trimestrais-do-abate-de-animais.html]()
[8] Centro de Estudos Avançados em Economia Aplicada (CEPEA/USP). *Cotações e Preços*. [https://www.cepea.esalq.usp.br/]()
