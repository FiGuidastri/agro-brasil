import mysql.connector
import pandas as pd
from mysql.connector import Error
from projeto_agro.config import DB_CONFIG
from projeto_agro_sqlite.extract_data import run_extraction # Importa a função de extração

# --- 1. Funções de Conexão e Auxiliares ---

def create_db_connection():
    """Cria e retorna a conexão com o banco de dados MySQL."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Conexão com MySQL estabelecida com sucesso.")
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def get_dimension_id(connection, table_name, column_name, value):
    """Busca o ID de uma dimensão (produto ou localidade) pelo seu valor."""
    cursor = connection.cursor()
    query = f"SELECT id_{table_name} FROM {table_name} WHERE {column_name} = %s"
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
    
    # Query de inserção na tabela fato. Usamos ON DUPLICATE KEY UPDATE para
    # garantir que dados existentes (pela chave UNIQUE) sejam atualizados,
    # o que é útil para dados mensais/trimestrais que podem ser reprocessados.
    insert_query = f"""
    INSERT INTO fato_producao_agronegocio ({', '.join(fato_columns)})
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        area_plantada_ha = VALUES(area_plantada_ha),
        producao_ton = VALUES(producao_ton),
        estimativa_ton = VALUES(estimativa_ton),
        abates_cabecas = VALUES(abates_cabecas),
        peso_carcaca_kg = VALUES(peso_carcaca_kg),
        preco_medio_rs = VALUES(preco_medio_rs),
        data_ingestao = CURRENT_TIMESTAMP
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
    
    # Preenche valores NaN (ausentes) com None para compatibilidade com MySQL
    df_combined = df_combined.where(pd.notna(df_combined), None)
    
    print(f"-> Iniciando transformação e carga de {len(df_combined)} registros...")
    
    rows_inserted = 0
    for index, row in df_combined.iterrows():
        try:
            # 1. Mapeamento de Dimensões
            id_produto = get_dimension_id(connection, 'dim_produto', 'nome_produto', row['produto'])
            id_localidade = get_dimension_id(connection, 'dim_localidade', 'uf', row['localidade'])
            
            if not id_produto or not id_localidade:
                print(f"   [AVISO] Dimensão não encontrada para Produto: {row['produto']} ou Localidade: {row['localidade']}. Pulando registro.")
                continue
            
            # 2. Preparação dos Dados
            # Os campos que não vieram na extração específica (ex: area_plantada no CEPEA)
            # serão None, o que é tratado pelo .where(pd.notna(df_combined), None)
            
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
    
    print("--- INÍCIO DO PIPELINE ETL AGRONEGÓCIO ---")
    
    # 1. Extração (Extract)
    raw_data = run_extraction()
    
    # 2. Conexão com o Banco de Dados
    connection = create_db_connection()
    
    if connection:
        try:
            # 3. Transformação e Carga (Transform & Load)
            transform_and_load_data(connection, raw_data)
            
        finally:
            # 4. Fechar Conexão
            connection.close()
            print("Conexão com MySQL fechada.")
    
    print("--- FIM DO PIPELINE ETL AGRONEGÓCIO ---")

if __name__ == '__main__':
    run_pipeline()
