-- Script SQL para criação do esquema do banco de dados SQLite

-- 1. Tabela de Dimensão: dim_produto
CREATE TABLE IF NOT EXISTS dim_produto (
    id_dim_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_produto TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL
);

-- Inserção inicial de dados de dimensão (produtos)
INSERT OR IGNORE INTO dim_produto (nome_produto, categoria) VALUES
('Soja', 'Grãos'),
('Milho', 'Grãos'),
('Arroz', 'Grãos'),
('Feijão', 'Grãos'),
('Algodão', 'Fibras'),
('Bovino', 'Pecuária'),
('Suíno', 'Pecuária'),
('Frango', 'Pecuária');

-- 2. Tabela de Dimensão: dim_localidade
CREATE TABLE IF NOT EXISTS dim_localidade (
    id_dim_localidade INTEGER PRIMARY KEY AUTOINCREMENT,
    uf TEXT NOT NULL UNIQUE,
    regiao TEXT NOT NULL
);

-- Inserção inicial de dados de dimensão (localidades - UFs e Regiões)
INSERT OR IGNORE INTO dim_localidade (uf, regiao) VALUES
('AC', 'Norte'), ('AL', 'Nordeste'), ('AP', 'Norte'), ('AM', 'Norte'), ('BA', 'Nordeste'),
('CE', 'Nordeste'), ('DF', 'Centro-Oeste'), ('ES', 'Sudeste'), ('GO', 'Centro-Oeste'),
('MA', 'Nordeste'), ('MT', 'Centro-Oeste'), ('MS', 'Centro-Oeste'), ('MG', 'Sudeste'),
('PA', 'Norte'), ('PB', 'Nordeste'), ('PR', 'Sul'), ('PE', 'Nordeste'), ('PI', 'Nordeste'),
('RJ', 'Sudeste'), ('RN', 'Nordeste'), ('RS', 'Sul'), ('RO', 'Norte'), ('RR', 'Norte'),
('SC', 'Sul'), ('SP', 'Sudeste'), ('SE', 'Nordeste'), ('TO', 'Norte'),
('BR', 'Brasil'); -- Para dados nacionais

-- 3. Tabela Fato: fato_producao_agronegocio
CREATE TABLE IF NOT EXISTS fato_producao_agronegocio (
    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
    data_referencia TEXT NOT NULL, -- SQLite usa TEXT para datas
    id_dim_produto INTEGER NOT NULL,
    id_dim_localidade INTEGER NOT NULL,
    
    -- Métricas de Produção (CONAB/IBGE)
    area_plantada_ha REAL,
    producao_ton REAL,
    estimativa_ton REAL,
    
    -- Métricas de Abate (IBGE)
    abates_cabecas INTEGER,
    peso_carcaca_kg REAL,
    
    -- Métricas de Mercado (CEPEA/USP)
    preco_medio_rs REAL,
    
    data_ingestao TEXT DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves Estrangeiras (SQLite não impõe FOREIGN KEY por padrão, mas é bom para documentação)
    FOREIGN KEY (id_dim_produto) REFERENCES dim_produto(id_dim_produto),
    FOREIGN KEY (id_dim_localidade) REFERENCES dim_localidade(id_dim_localidade),
    
    -- Restrição para evitar duplicidade de dados na mesma data/localidade/produto
    UNIQUE (data_referencia, id_dim_produto, id_dim_localidade)
);

-- Opcional: Criar índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_data_referencia ON fato_producao_agronegocio (data_referencia);
CREATE INDEX IF NOT EXISTS idx_produto ON fato_producao_agronegocio (id_dim_produto);
CREATE INDEX IF NOT EXISTS idx_localidade ON fato_producao_agronegocio (id_dim_localidade);
