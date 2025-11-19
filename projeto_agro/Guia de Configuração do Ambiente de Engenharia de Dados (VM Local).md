# Guia de Configuração do Ambiente de Engenharia de Dados (VM Local)

Este guia detalha o passo a passo para configurar sua máquina virtual (VM) local com o MySQL e todas as dependências Python necessárias para executar o pipeline de ingestão de dados do agronegócio.

## 1. Configuração do Servidor MySQL

Assumindo que sua VM esteja rodando uma distribuição Linux baseada em Debian/Ubuntu.

### 1.1. Instalação do MySQL Server

Execute os seguintes comandos no terminal da sua VM:

```bash
# 1. Atualizar a lista de pacotes
sudo apt update

# 2. Instalar o MySQL Server
sudo apt install mysql-server

# 3. Executar o script de segurança (opcional, mas recomendado)
sudo mysql_secure_installation
# Siga as instruções. Defina uma senha forte para o usuário 'root'.
```

### 1.2. Criação do Banco de Dados e Usuário Dedicado

É fundamental criar um banco de dados e um usuário específico para o projeto, com permissões limitadas.

```bash
# Acessar o console do MySQL como root
sudo mysql -u root -p

# Digite a senha do root que você definiu.

# 1. Criar o banco de dados
CREATE DATABASE agronegocio_db;

# 2. Criar um usuário dedicado e definir uma senha forte
# Substitua 'sua_senha_forte' pela senha real
CREATE USER 'data_user'@'localhost' IDENTIFIED BY 'sua_senha_forte';

# 3. Conceder permissões ao novo usuário no banco de dados
GRANT ALL PRIVILEGES ON agronegocio_db.* TO 'data_user'@'localhost';

# 4. Aplicar as mudanças
FLUSH PRIVILEGES;

# 5. Sair do console
EXIT;
```

**Parâmetros de Conexão:**
*   **Host:** `localhost`
*   **Database:** `agronegocio_db`
*   **User:** `data_user`
*   **Password:** `sua_senha_forte` (Mantenha esta senha em segredo e substitua no código Python)

## 2. Configuração do Ambiente Python

O pipeline será executado em Python. É altamente recomendado o uso de um ambiente virtual para isolar as dependências.

### 2.1. Instalação de Dependências

```bash
# 1. Instalar o pip e o venv (se ainda não estiverem instalados)
sudo apt install python3-pip python3-venv

# 2. Criar um diretório para o projeto
mkdir projeto_agronegocio
cd projeto_agronegocio

# 3. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar as bibliotecas Python necessárias
pip install pandas requests beautifulsoup4 mysql-connector-python openpyxl lxml
# Nota: 'lxml' é um parser rápido para BeautifulSoup. 'openpyxl' é para ler arquivos Excel.
```

### 2.2. Teste de Conexão com o MySQL (Opcional)

Para garantir que a biblioteca Python possa se conectar ao MySQL, você pode executar um teste rápido:

```python
import mysql.connector

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="data_user",
        password="sua_senha_forte",
        database="agronegocio_db"
    )
    print("Conexão com MySQL bem-sucedida!")
    mydb.close()
except mysql.connector.Error as err:
    print(f"Erro de conexão: {err}")
```

Se a mensagem "Conexão com MySQL bem-sucedida!" for exibida, seu ambiente está pronto para a próxima fase.

## 3. Estrutura de Diretórios do Projeto

Para manter o código organizado, utilize a seguinte estrutura:

```
projeto_agronegocio/
├── venv/
├── pipeline.py          # Script principal de orquestração (ETL)
├── config.py            # Arquivo com as credenciais do banco de dados
├── setup_db.sql         # Script para criar as tabelas no MySQL
└── data/                # Diretório para armazenar arquivos temporários (Excel, PDF)
```

## 4. Agendamento Semanal (Orquestração via Cron Job)

Para garantir que o pipeline seja executado automaticamente toda semana, utilizaremos o `cron`, o agendador de tarefas padrão do Linux.

### 4.1. Configuração do Cron Job

Recomendamos agendar a execução para o início da semana (ex: Segunda-feira de manhã), para que os dados mais recentes (geralmente publicados no final da semana anterior) sejam processados a tempo para os relatórios.

1.  **Abrir o Crontab:**
    ```bash
    crontab -e
    ```
    Se for a primeira vez, escolha um editor (ex: `nano` ou `vim`).

2.  **Adicionar a Linha de Agendamento:**
    Adicione a seguinte linha no final do arquivo. Esta linha agendará a execução do script toda **Segunda-feira às 08:00 da manhã**.

    ```cron
    # M H Dm M Dw Comando
    # 0 8 * * 1 /caminho/completo/para/o/seu/projeto_agronegocio/venv/bin/python /caminho/completo/para/o/seu/projeto_agronegocio/pipeline.py >> /tmp/agronegocio_cron.log 2>&1
    
    # Exemplo (Substitua o caminho completo):
    0 8 * * 1 /home/seu_usuario/projeto_agronegocio/venv/bin/python /home/seu_usuario/projeto_agronegocio/pipeline.py >> /tmp/agronegocio_cron.log 2>&1
    ```

    **Explicação da Linha Cron:**
    *   `0 8 * * 1`: Significa 0 minutos, 8 horas, qualquer dia do mês, qualquer mês, e **1** (Segunda-feira).
    *   `/caminho/completo/.../python`: É o caminho completo para o interpretador Python dentro do seu ambiente virtual. **Você deve substituir `/home/seu_usuario/projeto_agronegocio` pelo caminho real do seu projeto na VM.**
    *   `>> /tmp/agronegocio_cron.log 2>&1`: Redireciona a saída (stdout e stderr) para um arquivo de log, o que é crucial para monitorar a execução e diagnosticar erros.

3.  **Salvar e Sair:**
    *   Se estiver usando `nano`, pressione `Ctrl+O` para salvar e `Ctrl+X` para sair.
    *   O `cron` irá notificar que a nova crontab foi instalada.

Com isso, o pipeline será executado automaticamente toda semana, garantindo que sua base de dados esteja sempre atualizada para os relatórios da diretoria.
