# Catalogador de Arquivos em Múltiplas Unidades

Ferramenta de linha de comando para catalogar arquivos distribuídos em várias unidades de armazenamento (discos físicos, NAS, Google Drive, etc.) e detectar duplicatas — sem copiar os arquivos, apenas lendo e indexando seus metadados.

## O problema

Quem mantém backups em vários HDs externos, NAS e serviços de nuvem acaba com muitas cópias dos mesmos arquivos e pastas espalhadas. Localizar o que é original e o que é duplicata manualmente é inviável quando se tem milhares de arquivos.

## A solução

O **catalogador** varre as unidades de armazenamento, registra metadados relevantes (hash, tamanho, datas, caminho completo) em um banco PostgreSQL e gera relatórios que permitem:

- **Localizar arquivos** por nome, extensão ou unidade de origem
- **Detectar duplicatas** por hash idêntico (arquivos iguais em locais diferentes)
- **Comparar pastas de backup** para identificar cópias redundantes
- **Exportar** o catálogo completo em CSV para análise externa

### Tipos de arquivo catalogados

| Categoria     | Extensões                                              |
|---------------|--------------------------------------------------------|
| Planilhas     | `.xls`, `.xlsx`, `.xlsm`, `.xlsb`, `.csv`             |
| Bancos Access | `.mdb`, `.accdb`                                       |
| Documentos    | `.pdf`, `.doc`, `.docx`                                |
| Imagens       | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, etc. |
| Vídeos        | `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`|
| Áudio         | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`                |
| Arquivos ZIP  | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`                   |
| Outros        | `.sfp` (extensível via configuração)                   |

Arquivos ignorados: `.exe`, `.com`, `.dll`, `.sys`, `.bat`, `.msi`, `.tmp`, `.log` e outros arquivos de sistema.

### Estratégia de hashing para arquivos grandes

| Tipo de arquivo | Tamanho     | Estratégia                              |
|-----------------|-------------|-----------------------------------------|
| Qualquer        | ≤ 100 MB    | Hash SHA-256 completo                   |
| Não-vídeo       | > 100 MB    | Hash parcial (início + meio + fim)      |
| Vídeo           | > 100 MB    | Sem hash (comparação apenas por tamanho)|

## Pré-requisitos

- **Python 3.12+**
- **PostgreSQL** (em execução, com um banco de dados criado)
- **Poetry** (gerenciador de dependências)

### Instalando o Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Criando o banco de dados

```bash
createdb catalogador
```

Ou via `psql`:

```sql
CREATE DATABASE catalogador;
```

## Instalação

```bash
# Clone o repositório
git clone https://github.com/fagner-net/catalog-arquivos-unidades.git
cd catalog-arquivos-unidades

# Instale as dependências
poetry install

# Aplique as migrações do banco de dados
poetry run alembic upgrade head
```

### Configuração

Por padrão, o catalogador conecta em `postgresql://localhost:5432/catalogador`. Para alterar, defina a variável de ambiente:

```bash
export CATALOGADOR_DATABASE_URL="postgresql://usuario:senha@host:5432/nome_do_banco"
```

Outras variáveis de ambiente disponíveis:

| Variável                            | Padrão   | Descrição                                |
|-------------------------------------|----------|------------------------------------------|
| `CATALOGADOR_DATABASE_URL`          | `postgresql://localhost:5432/catalogador` | URL de conexão ao PostgreSQL |
| `CATALOGADOR_LOG_LEVEL`             | `INFO`   | Nível de log (`DEBUG`, `INFO`, `WARNING`) |
| `CATALOGADOR_HASH_CHUNK_SIZE`       | `8192`   | Tamanho do chunk para leitura de hash (bytes) |
| `CATALOGADOR_LARGE_FILE_THRESHOLD_MB` | `100`  | Limite para considerar arquivo grande (MB) |

## Uso

### 1. Registrar unidades de armazenamento

Cada unidade precisa de um **alias** (nome curto e único) e um **tipo**:

```bash
# Registrar um HD externo
poetry run catalogador unit add --alias "hd-externo-1" --type disco_fisico

# Registrar um NAS
poetry run catalogador unit add --alias "nas-escritorio" --type nas

# Registrar Google Drive
poetry run catalogador unit add --alias "gdrive-pessoal" --type google_drive

# Tipos disponíveis: disco_fisico, nas, google_drive, outro
```

### 2. Listar unidades registradas

```bash
poetry run catalogador unit list
```

Exibe uma tabela com ID, alias, tipo e data de cadastro de todas as unidades.

### 3. Escanear uma unidade

O caminho é fornecido no momento do scan (não fica salvo na unidade), pois o ponto de montagem pode variar:

```bash
# Escanear um HD externo montado em /mnt/hd-externo
poetry run catalogador scan run --unit "hd-externo-1" --path /mnt/hd-externo

# Escanear uma pasta do NAS
poetry run catalogador scan run --unit "nas-escritorio" --path /mnt/nas/compartilhamento

# Escanear Google Drive montado localmente
poetry run catalogador scan run --unit "gdrive-pessoal" --path ~/Google\ Drive
```

O scanner percorre toda a árvore de diretórios, cataloga os arquivos incluídos e exibe o progresso no terminal.

### 4. Relatório de duplicatas

```bash
poetry run catalogador report duplicates
```

Exibe grupos de arquivos com hash idêntico encontrados em diferentes unidades/caminhos, mostrando unidade de origem, caminho completo e tamanho.

### 5. Exportar catálogo para CSV

```bash
poetry run catalogador report export --output catalogo.csv
```

### 6. Remover uma unidade

```bash
poetry run catalogador unit remove --alias "hd-externo-1"
```

Remove a unidade e **todos os dados de varredura associados**.

## Desenvolvimento

### Executar testes

```bash
poetry run pytest                # Todos os testes
poetry run pytest -v             # Saída detalhada
poetry run pytest tests/test_scanner.py                          # Arquivo específico
poetry run pytest tests/test_scanner.py::test_walk_directory     # Teste específico
poetry run pytest -k "test_hash_large_file"                      # Por palavra-chave
poetry run pytest --cov=catalogador --cov-report=term-missing    # Com cobertura
```

### Lint e formatação

```bash
poetry run ruff check src/ tests/        # Verificar lint
poetry run ruff check --fix src/ tests/  # Corrigir automaticamente
poetry run ruff format src/ tests/       # Formatar código
poetry run mypy src/                     # Verificação de tipos
```

### Migrações do banco

```bash
# Criar nova migração após alterar os models
poetry run alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrações pendentes
poetry run alembic upgrade head
```

## Estrutura do projeto

```
src/catalogador/
├── config.py              # Configurações via variáveis de ambiente
├── cli/
│   ├── main.py            # Entry point do CLI (typer)
│   ├── unit_commands.py   # Gerenciamento de unidades
│   ├── scan_commands.py   # Comandos de varredura
│   └── report_commands.py # Relatórios e exportação
├── db/
│   ├── models.py          # StorageUnit, ScanSession, FileRecord
│   ├── session.py         # Conexão com o banco
│   └── repository.py      # Camada de acesso a dados
├── scanner/
│   ├── filesystem.py      # Percorre diretórios e coleta metadados
│   └── hasher.py          # Estratégias de hashing
├── reports/
│   ├── duplicates.py      # Detecção de duplicatas
│   └── export.py          # Exportação CSV
└── utils/
    ├── exceptions.py      # Exceções customizadas
    └── filters.py         # Filtro de extensões
```

## Licença

Este projeto é de uso privado.
