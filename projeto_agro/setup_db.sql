-- Script SQL para criação do esquema do banco de dados agronegocio_db (MySQL)

-- 1. Tabela de Dimensão: dim_produto
CREATE TABLE IF NOT EXISTS dim_produto (
    id_dim_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome_produto VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL
);

-- Inserção inicial de dados de dimensão (produtos)
INSERT IGNORE INTO dim_produto (nome_produto, categoria) VALUES
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
    id_dim_localidade INT AUTO_INCREMENT PRIMARY KEY,
    uf VARCHAR(2) NOT NULL UNIQUE,
    regiao VARCHAR(50) NOT NULL
);

-- Inserção inicial de dados de dimensão (localidades - UFs e Regiões)
INSERT IGNORE INTO dim_localidade (uf, regiao) VALUES
('AC', 'Norte'), ('AL', 'Nordeste'), ('AP', 'Norte'), ('AM', 'Norte'), ('BA', 'Nordeste'),
('CE', 'Nordeste'), ('DF', 'Centro-Oeste'), ('ES', 'Sudeste'), ('GO', 'Centro-Oeste'),
('MA', 'Nordeste'), ('MT', 'Centro-Oeste'), ('MS', 'Centro-Oeste'), ('MG', 'Sudeste'),
('PA', 'Norte'), ('PB', 'Nordeste'), ('PR', 'Sul'), ('PE', 'Nordeste'), ('PI', 'Nordeste'),
('RJ', 'Sudeste'), ('RN', 'Nordeste'), ('RS', 'Sul'), ('RO', 'Norte'), ('RR', 'Norte'),
('SC', 'Sul'), ('SP', 'Sudeste'), ('SE', 'Nordeste'), ('TO', 'Norte'),
('BR', 'Brasil'); -- Para dados nacionais

-- 3. Tabela Fato: fato_producao_agronegocio
CREATE TABLE IF NOT EXISTS fato_producao_agronegocio (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    data_referencia DATE NOT NULL,
    id_dim_produto INT NOT NULL,
    id_dim_localidade INT NOT NULL,
    
    -- Métricas de Produção (CONAB/IBGE)
    area_plantada_ha DECIMAL(18, 2),
    producao_ton DECIMAL(18, 2),
    estimativa_ton DECIMAL(18, 2),
    
    -- Métricas de Abate (IBGE)
    abates_cabecas INT,
    peso_carcaca_kg DECIMAL(18, 2),
    
    -- Métricas de Mercado (CEPEA/USP)
    preco_medio_rs DECIMAL(10, 2),
    
    data_ingestao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves Estrangeiras
    FOREIGN KEY (id_dim_produto) REFERENCES dim_produto(id_dim_produto),
    FOREIGN KEY (id_dim_localidade) REFERENCES dim_localidade(id_dim_localidade),
    
    -- Restrição para evitar duplicidade de dados na mesma data/localidade/produto
    UNIQUE KEY uk_fato (data_referencia, id_dim_produto, id_dim_localidade)
);

-- Opcional: Criar índices para otimizar consultas
CREATE INDEX idx_data_referencia ON fato_producao_agronegocio (data_referencia);
CREATE INDEX idx_produto ON fato_producao_agronegocio (id_dim_produto);
CREATE INDEX idx_localidade ON fato_producao_agronegocio (id_dim_localidade);
