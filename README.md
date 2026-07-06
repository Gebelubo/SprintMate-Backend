# SprintMate - Backend

SprintMate é um sistema de gerenciamento de projetos desenvolvido para equipes que utilizam metodologias ágeis, permitindo organizar projetos, sprints, tarefas e acompanhar o progresso das atividades de forma simples e eficiente.

Este repositório contém o **backend** da aplicação, responsável pela API, regras de negócio e persistência dos dados.

---

# Tecnologias

O projeto foi desenvolvido utilizando:

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Docker Compose

---

# Funcionalidades

- Gerenciamento de usuários
- Gerenciamento de projetos
- Gerenciamento de sprints
- Gerenciamento de tarefas
- Associação de usuários às tarefas
- Controle de status das tarefas
- Persistência em banco de dados PostgreSQL

# Estrutura do Projeto

```text
SprintMate-Backend/
│
├── src/
│   ├──db/
│   ├── entities/
│   ├── repositories/
│   ├── routers/
│   ├── service/
│   ├── utils/
|   |── websocket
│   └── config.py
│
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── main.py
├── LICENSE
├── poetry.lock
├── pyproject.toml
└── README.md
```

---

# Como executar

## Pré-requisitos

- Docker
- Docker Compose

---

## Executando o projeto

Na raiz do projeto execute:

```bash
docker compose up --build
```

Após a inicialização, a API estará disponível em:

```
http://localhost:8001
```

---

# Documentação da API

O FastAPI disponibiliza automaticamente a documentação interativa.

Swagger UI

```
http://localhost:8001/docs
```

ReDoc

```
http://localhost:8001/redoc
```

---

# Arquitetura

O backend segue uma arquitetura em camadas, separando responsabilidades entre:

- Routers
- Entities
- Services
- Repositories
- Schemas

Essa organização facilita a manutenção, testes e evolução do sistema.

---

# Metodologia

O SprintMate foi concebido para apoiar equipes que utilizam metodologias ágeis, especialmente o **Scrum**, oferecendo recursos para:

- Organização de projetos
- Planejamento de sprints
- Distribuição de tarefas
- Acompanhamento do progresso

---

# Licença

Este projeto foi desenvolvido para fins acadêmicos.
