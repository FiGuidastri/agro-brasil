import sqlite3
import pandas as pd
import os
from config_sqlite import DB_FILE
from extract_data import run_extraction # Reutiliza a função de extração

# --- 1. Funções de Conexão e Auxiliares ---

def create_db_connection():
    """Cria e retorna a conexão com o banco de dados SQLite."""
    connection = None
    try:
        # O arquivo DB_FILE será criado se não existir
        connection = sqlite3.connect(DB_FILE)
        print(f"Conexão com SQLite ({DB_FILE}) estabelecida com sucesso.")
        return connection
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

def setup_database(connection):
    """Executa o script SQL para criar as tabelas e popular as dimensões."""
    try:
        cursor = connection.cursor()
        with open('setup_db_sqlite.sql', 'r') as f:
            sql_script = f.read()
            # SQLite não suporta múltiplos comandos em um único .execute(),
            # mas o módulo sqlite3 do Python lida com isso usando .executescript()
            cursor.executescript(sql_script)
        connection.commit()
        print("Estrutura do banco de dados SQLite criada/atualizada com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar o banco de dados: {e}")
        connection.rollback()

def get_dimension_id(connection, table_name, column_name, value):
    """Busca o ID de uma dimensão (produto ou localidade) pelo seu valor."""
    cursor = connection.cursor()
    query = f"SELECT id_{table_name} FROM {table_name} WHERE {column_name} = ?"
    cursor.execute(query, (value,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

# --- 2. Funções de Transformação e Carga (T&L) ---

def transform_and_load_data(connection, raw_data):
    """Transforma os DataFrames brutos e carrega na tabela fato."""
    
    cursor = connection.cursor()
    
    # Mapeamento de colunas para a tabela fato
    fato_columns = [
        'data_referencia', 'id_dim_produto', 'id_dim_localidade',
        'area_plantada_ha', 'producao_ton', 'estimativa_ton',
        'abates_cabecas', 'peso_carcaca_kg', 'preco_medio_rs'
    ]
    
    # Query de inserção na tabela fato. Usamos INSERT OR REPLACE para lidar com
    # a restrição UNIQUE do SQLite, garantindo que dados existentes sejam atualizados.
    # Nota: O SQLite não tem o "ON DUPLICATE KEY UPDATE" do MySQL, mas o "INSERT OR REPLACE"
    # ou "INSERT OR IGNORE" são as alternativas mais próximas. Usaremos REPLACE para
    # garantir que o dado mais novo substitua o antigo em caso de duplicidade.
    insert_query = f"""
    INSERT OR REPLACE INTO fato_producao_agronegocio ({', '.join(fato_columns)}, data_ingestao)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """
    
    # Combina todos os DataFrames em uma lista para processamento unificado
    all_data = []
    
    # Processa dados CEPEA (Preços)
    df_cepea = raw_data['cepea_prices']
    df_cepea['fonte'] = 'CEPEA'
    all_data.append(df_cepea)
    
    # Processa dados IBGE (Abates)
    df_ibge = raw_data['ibge_abates']
    df_ibge['fonte'] = 'IBGE'
    all_data.append(df_ibge)
    
    # Processa dados CONAB (Safras)
    df_conab = raw_data['conab_safras']
    df_conab['fonte'] = 'CONAB'
    all_data.append(df_conab)
    
    # DataFrame unificado para iteração
    df_combined = pd.concat(all_data, ignore_index=True)
    
    # Preenche valores NaN (ausentes) com None para compatibilidade com SQL
    df_combined = df_combined.where(pd.notna(df_combined), None)
    
    print(f"-> Iniciando transformação e carga de {len(df_combined)} registros...")
    
    rows_inserted = 0
    for index, row in df_combined.iterrows():
        try:
            # 1. Mapeamento de Dimensões
            id_produto = get_dimension_id(connection, 'dim_produto', 'nome_produto', row['produto'])
            id_localidade = get_dimension_id(connection, 'dim_localidade', 'uf', row['localidade'])
            
            if not id_produto or not id_localidade:
                # Tenta inserir a dimensão se não existir (apenas para o caso de produtos/localidades novos)
                # No nosso caso, as dimensões são fixas, então é um erro se não encontrar.
                print(f"   [AVISO] Dimensão não encontrada para Produto: {row['produto']} ou Localidade: {row['localidade']}. Pulando registro.")
                continue
            
            # 2. Preparação dos Dados
            # A ordem dos campos deve seguir a ordem da insert_query
            data_to_insert = (
                row['data_referencia'],
                id_produto,
                id_localidade,
                row.get('area_plantada_ha'),
                row.get('producao_ton'),
                row.get('estimativa_ton'),
                row.get('abates_cabecas'),
                row.get('peso_carcaca_kg'),
                row.get('preco_medio_rs')
            )
            
            # 3. Carga (Load)
            cursor.execute(insert_query, data_to_insert)
            rows_inserted += 1
            
        except Exception as e:
            print(f"   [ERRO] Falha ao processar o registro {index}: {e}")
            connection.rollback() # Reverte a transação em caso de erro
            
    # Commit das alterações
    connection.commit()
    cursor.close()
    print(f"-> Carga concluída. {rows_inserted} registros processados na tabela fato_producao_agronegocio.")

# --- 3. Função Principal do Pipeline ---

def run_pipeline():
    """Função principal que executa o pipeline ETL completo."""
    
    print("--- INÍCIO DO PIPELINE ETL AGRONEGÓCIO (SQLite) ---")
    
    # 1. Conexão com o Banco de Dados
    connection = create_db_connection()
    
    if connection:
        try:
            # 2. Configuração do Banco de Dados (Cria tabelas se não existirem)
            setup_database(connection)
            
            # 3. Extração (Extract)
            raw_data = run_extraction()
            
            # 4. Transformação e Carga (Transform & Load)
            transform_and_load_data(connection, raw_data)
            
        finally:
            # 5. Fechar Conexão
            connection.close()
            print("Conexão com SQLite fechada.")
    
    print("--- FIM DO PIPELINE ETL AGRONEGÓCIO (SQLite) ---")

if __name__ == '__main__':
    run_pipeline()
