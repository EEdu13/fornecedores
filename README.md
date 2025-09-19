# 🍽️ Sistema de Pedidos LARSIL

Sistema completo de pedidos de refeições com validação facial, integração dupla de bancos de dados (SQL Server Azure + PostgreSQL Railway) e geração de PDFs.

## 🚀 Funcionalidades

- ✅ **Login por Fornecedor** com validação por CNPJ
- ✅ **Pedidos por Quinzena** com preços automatizados
- ✅ **Validação Facial** via QR Code para assinatura digital
- ✅ **Dual Database**: SQL Server Azure (fornecedores) + PostgreSQL Railway (pedidos)
- ✅ **Geração de PDF** com dados completos e QR Code
- ✅ **Sincronização Cross-Device** de fotos via servidor
- ✅ **Interface Responsiva** com design moderno

## 🏗️ Arquitetura

```
Frontend (HTML/JS/CSS)
    ↓
Backend Python (photo_server.py)
    ↓
SQL Server Azure ← → PostgreSQL Railway
```

## 📦 Instalação Local

### 1. Clone o repositório
```bash
git clone [seu-repositorio]
cd FORNECEDORES
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# SQL Server Azure Configuration
SQL_SERVER=seu-servidor.database.windows.net
SQL_DATABASE=sua-database
SQL_USERNAME=seu-usuario
SQL_PASSWORD=sua-senha
SQL_DRIVER={ODBC Driver 17 for SQL Server}

# PostgreSQL Railway Configuration
PGHOST=seu-host.rlwy.net
PGPORT=sua-porta
PGUSER=postgres
PGPASSWORD=sua-senha-pg
PGDATABASE=railway

# Server Configuration
PORT=8000
HOST=0.0.0.0
```

### 4. Execute o servidor
```bash
python photo_server.py
```

### 5. Acesse o sistema
Abra seu navegador em: `http://localhost:8000`

## � Deploy no Railway

### 1. Preparação
- Faça push do código para GitHub (sem o arquivo `.env`)
- Certifique-se que o `.gitignore` está protegendo credenciais

### 2. Conecte ao Railway
1. Acesse [railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Escolha o projeto "FORNECEDORES"

### 3. Configure as Variáveis de Ambiente
No painel do Railway, adicione todas as variáveis de ambiente:

#### SQL Server Azure:
- `SQL_SERVER`: Endereço do servidor Azure
- `SQL_DATABASE`: Nome da database
- `SQL_USERNAME`: Usuário SQL
- `SQL_PASSWORD`: Senha SQL
- `SQL_DRIVER`: `{ODBC Driver 17 for SQL Server}`

#### PostgreSQL Railway:
- `PGHOST`: Host do PostgreSQL
- `PGPORT`: Porta (geralmente 5432)
- `PGUSER`: Usuário PostgreSQL
- `PGPASSWORD`: Senha PostgreSQL
- `PGDATABASE`: Nome da database

#### Servidor:
- `PORT`: Porta do servidor (Railway define automaticamente)
- `HOST`: `0.0.0.0`

### 4. Deploy
O Railway irá automaticamente:
- Instalar dependências do `requirements.txt`
- Executar `python photo_server.py`
- Disponibilizar a aplicação

## �️ Estrutura do Banco de Dados

### SQL Server Azure (Fornecedores)
```sql
Tabela: Tabela_teste
Colunas:
- FORNECEDOR (VARCHAR)
- CPF_CNPJ (VARCHAR)
- VALOR (DECIMAL)
- TIPO_FORN (VARCHAR)
```

### PostgreSQL Railway (Pedidos)
```sql
Schema: fornecedores.refeicoes
Tabela: pedidos_refeicoes
Colunas:
- id (SERIAL PRIMARY KEY)
- data_pedido (DATE)
- fornecedor (VARCHAR)
- cafe, almoco_marmitex, almoco_local, etc. (INTEGER)
- valor_cafe, valor_almoco_marmitex, etc. (DECIMAL)
- data_criacao (TIMESTAMP)
```

## 🔐 Segurança

### Credenciais Protegidas
- ✅ Todas as credenciais em variáveis de ambiente
- ✅ Arquivo `.env` no `.gitignore`
- ✅ Senhas não commitadas no código

### Validação
- ✅ Login por CNPJ (primeiros 4 dígitos)
- ✅ Validação facial para assinatura
- ✅ Confirmações para ações críticas

## 📁 Estrutura de Arquivos

```
FORNECEDORES/
├── index.html              # Frontend principal
├── photo_server.py         # Backend Python
├── requirements.txt        # Dependências Python
├── .env                   # Variáveis de ambiente (LOCAL)
├── .gitignore             # Arquivos ignorados
├── railway.json           # Configuração Railway
├── Procfile              # Comando de inicialização
├── README.md             # Esta documentação
└── .venv/                # Ambiente virtual (LOCAL)
```

## 🛠️ Tecnologias Utilizadas

### Frontend
- HTML5 + CSS3
- JavaScript ES6+
- jsPDF para geração de PDFs
- Responsive Design

### Backend
- Python 3.x
- HTTP Server nativo
- CORS habilitado

### Bancos de Dados
- SQL Server Azure (pyodbc)
- PostgreSQL Railway (psycopg2)

### Deploy
- Railway (hosting)
- GitHub (versionamento)

## 🐞 Troubleshooting

### Erro de Conexão com SQL Server
- Verifique as credenciais no `.env`
- Confirme que o ODBC Driver 17 está instalado
- Teste conectividade de rede

### Erro de Conexão PostgreSQL
- Verifique host e porta do Railway
- Confirme usuário e senha
- Teste se o schema `fornecedores` existe

### Erro no Deploy Railway
- Verifique se todas as variáveis de ambiente estão configuradas
- Confirme que o `requirements.txt` está correto
- Veja logs no painel do Railway

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique este README
2. Consulte os logs do sistema
3. Teste conexões de banco separadamente

---

**⚡ Sistema pronto para produção com segurança enterprise!**
