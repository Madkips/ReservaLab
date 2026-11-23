# ReservaLab — Sistema de Reserva de Laboratórios

## Sobre o projeto

O ReservaLab é um sistema web desenvolvido para facilitar o gerenciamento de reservas de laboratórios de informática em instituições de ensino.

O sistema permite que professores consultem laboratórios, realizem reservas e gerenciem seus agendamentos.

O projeto foi desenvolvido como parte das atividades acadêmicas do curso de Análise e Desenvolvimento de Sistemas da Universidade Santo Amaro (UNISA).

## Tecnologias utilizadas

- **Python:** desenvolvimento da lógica do sistema.
- **Flask:** framework utilizado no backend.
- **HTML:** estrutura das páginas.
- **CSS:** estilização da interface.
- **JavaScript:** interatividade das páginas.
- **SQLite:** armazenamento dos dados.

## Funcionalidades

- Cadastro de professores.
- Login e logout.
- Consulta de laboratórios.
- Reserva de laboratórios por data e horário.
- Visualização de horários disponíveis.
- Bloqueio de horários ocupados.
- Validação de datas e horários.
- Consulta de reservas realizadas.
- Cancelamento de reservas.
- Controle de acesso por usuário.

## Como executar o projeto

### 1. Pré-requisitos

É necessário possuir Python instalado no computador.

### 2. Abrir o projeto

Abra a pasta do ReservaLab no Visual Studio Code ou em outro editor de sua preferência.

### 3. Criar o ambiente virtual

Execute no terminal:

`python -m venv .venv`

### 4. Ativar o ambiente virtual

No Windows PowerShell:

`.\.venv\Scripts\Activate.ps1`

Caso a execução de scripts esteja bloqueada, utilize o CMD:

`.venv\Scripts\activate.bat`

### 5. Instalar as dependências

`python -m pip install -r requirements.txt`

### 6. Configurar a chave secreta

Crie um arquivo chamado `.env` na pasta principal do projeto.

Gere uma chave aleatória executando:

`python -c "import secrets; print(secrets.token_hex(32))"`

Adicione ao arquivo `.env`:

`SECRET_KEY=sua_chave_gerada`

O arquivo `.env` não deve ser publicado no GitHub.

### 7. Executar o sistema

`python ReservaLab.py`

### 8. Acessar o sistema

Abra o navegador e acesse:

http://127.0.0.1:5000

## Banco de dados

O sistema utiliza SQLite para armazenar informações de professores, laboratórios e reservas.

O arquivo `reservalab.db` é utilizado para armazenamento local e pode ser criado automaticamente durante a inicialização do sistema.

Por segurança, os arquivos de banco de dados não são incluídos no repositório.

## Projeto acadêmico

**Projeto Integrador — Análise e Desenvolvimento de Sistemas**

Universidade Santo Amaro — UNISA

**Ano:** 2026

## Autor

Felipe Gonçalves Stahlberg