# Guia de Configuração do Ambiente de Engenharia de Dados (VM Local com SQLite)

Este guia detalha o passo a passo para configurar sua máquina virtual (VM) local com o **SQLite**, ideal para o ambiente de desenvolvimento e testes, e todas as dependências Python necessárias para executar o pipeline de ingestão de dados do agronegócio.

## 1. Configuração do Banco de Dados SQLite

O SQLite é um banco de dados *serverless*, o que significa que ele não requer um servidor de banco de dados instalado e configurado (como MySQL ou PostgreSQL). O banco de dados é simplesmente um arquivo no seu sistema.

### 1.1. Instalação e Configuração

O SQLite já vem pré-instalado com a maioria das distribuições Linux e com o Python. Não é necessária nenhuma instalação adicional de servidor.

**Parâmetros de Conexão:**
*   **Nome do Arquivo:** `agronegocio.db` (Este arquivo será criado automaticamente na primeira execução do script de configuração).

## 2. Configuração do Ambiente Python

O pipeline será executado em Python. É altamente recomendado o uso de um ambiente virtual para isolar as dependências.

### 2.1. Instalação de Dependências

```bash
# 1. Instalar o pip e o venv (se ainda não estiverem instalados)
sudo apt install python3-pip python3-venv

# 2. Criar um diretório para o projeto
mkdir projeto_agronegocio_sqlite
cd projeto_agronegocio_sqlite

# 3. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar as bibliotecas Python necessárias
# O 'sqlite3' já vem com o Python, mas precisamos das bibliotecas de scraping e manipulação de dados.
pip install pandas requests beautifulsoup4 openpyxl lxml
# Nota: 'lxml' é um parser rápido para BeautifulSoup. 'openpyxl' é para ler arquivos Excel.
```

### 2.2. Estrutura de Diretórios do Projeto

Para manter o código organizado, utilize a seguinte estrutura:

```
projeto_agronegocio_sqlite/
├── venv/
├── pipeline.py          # Script principal de orquestração (ETL)
├── config.py            # Arquivo com o nome do arquivo do banco de dados
├── extract_data.py      # Módulo de extração de dados
├── setup_db.sql         # Script para criar as tabelas no SQLite
└── data/                # Diretório para armazenar arquivos temporários (Excel, PDF)
```

## 3. Agendamento Semanal (Orquestração via Cron Job)

Para garantir que o pipeline seja executado automaticamente toda semana, utilizaremos o `cron`, o agendador de tarefas padrão do Linux.

### 3.1. Configuração do Cron Job

Recomendamos agendar a execução para o início da semana (ex: Segunda-feira de manhã), para que os dados mais recentes sejam processados a tempo para os relatórios.

1.  **Abrir o Crontab:**
    ```bash
    crontab -e
    ```
    Se for a primeira vez, escolha um editor (ex: `nano` ou `vim`).

2.  **Adicionar a Linha de Agendamento:**
    Adicione a seguinte linha no final do arquivo. Esta linha agendará a execução do script toda **Segunda-feira às 08:00 da manhã**.

    ```cron
    # M H Dm M Dw Comando
    # 0 8 * * 1 /caminho/completo/para/o/seu/projeto_agronegocio_sqlite/venv/bin/python /caminho/completo/para/o/seu/projeto_agronegocio_sqlite/pipeline.py >> /tmp/agronegocio_cron.log 2>&1
    
    # Exemplo (Substitua o caminho completo):
    0 8 * * 1 /home/seu_usuario/projeto_agronegocio_sqlite/venv/bin/python /home/seu_usuario/projeto_agronegocio_sqlite/pipeline.py >> /tmp/agronegocio_cron.log 2>&1
    ```

    **Explicação da Linha Cron:**
    *   `0 8 * * 1`: Significa 0 minutos, 8 horas, qualquer dia do mês, qualquer mês, e **1** (Segunda-feira).
    *   `/caminho/completo/.../python`: É o caminho completo para o interpretador Python dentro do seu ambiente virtual. **Você deve substituir `/home/seu_usuario/projeto_agronegocio_sqlite` pelo caminho real do seu projeto na VM.**
    *   `>> /tmp/agronegocio_cron.log 2>&1`: Redireciona a saída (stdout e stderr) para um arquivo de log, o que é crucial para monitorar a execução e diagnosticar erros.

3.  **Salvar e Sair:**
    *   Se estiver usando `nano`, pressione `Ctrl+O` para salvar e `Ctrl+X` para sair.
    *   O `cron` irá notificar que a nova crontab foi instalada.

Com isso, o pipeline será executado automaticamente toda semana, garantindo que sua base de dados esteja sempre atualizada para os relatórios da diretoria.
