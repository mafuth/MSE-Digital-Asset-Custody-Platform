# MSE Digital Asset Custody Platform

Modern, secure, institutional-grade storage and administration utility for physical and digital assets.

## Quick Start

To get the project up and running locally, follow these steps:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/mafuth/MSE-Customer-Inquiry-Management
    cd MSE-Customer-Inquiry-Management
    ```

2.  **Environment Setup**:
    Copy the example environment file and update any necessary values:
    ```bash
    cp .env.example .env
    ```

3.  **Start Services**:
    Use Docker Compose to build and start all containers:
    ```bash
    docker-compose up --build
    ```

4.  **Access the Application**:
    [http://localhost:8000](http://localhost:8000)

---

## Architectural Diagrams

### 1. Request Handling Flow
This diagram illustrates how a user request is handled from the browser through the proxy, application, and database layers.

```mermaid
sequenceDiagram
    participant User as "User (Browser)"
    participant Nginx as "NGINX Proxy (8000)"
    participant FE as "Svelte Frontend (Vite)"
    participant BE as "FastAPI Backend"
    participant PB as "PgBouncer (6432)"
    participant DB as "YugabyteDB (5433)"

    User->>Nginx: HTTP Request (Port 8000)
    Note over Nginx: Routes by Path
    alt /api/*
        Nginx->>BE: Forward to Backend
        BE->>PB: SQL Query (Pooled)
        PB->>DB: Execute Query
        DB-->>PB: Data Results
        PB-->>BE: Results
        BE-->>Nginx: JSON Response
    else Static Assets
        Nginx->>FE: Request Frontend Assets
        FE-->>Nginx: HTML / JS / CSS
    end
    Nginx-->>User: Final Response
```

---

### 2. Regional Scaling Design
The project is designed to scale horizontally across multiple regions using a Global Load Balancer and YugabyteDB's distributed SQL capabilities.

```mermaid
graph TD
    subgraph "Global Load Balancer"
        GLB[Anycast IP / Route53]
    end

    subgraph "Region A (Primary)"
        R1_Proxy[NGINX Cluster]
        R1_APP[Backend/Frontend Replicas]
        R1_DB[(Yugabyte Node 1)]
    end

    subgraph "Region B (Secondary)"
        R2_Proxy[NGINX Cluster]
        R2_APP[Backend/Frontend Replicas]
        R2_DB[(Yugabyte Node 2)]
    end

    subgraph "Region C (Quorum)"
        R3_DB[(Yugabyte Node 3)]
    end

    GLB --> R1_Proxy
    GLB --> R2_Proxy

    R1_Proxy --> R1_APP
    R2_Proxy --> R2_APP

    R1_APP --> R1_DB
    R2_APP --> R2_DB

    R1_DB <--> R2_DB
    R2_DB <--> R3_DB
    R3_DB <--> R1_DB
```

---

### 3. High Availability (HA) Standards
The architecture ensures no single point of failure by implementing redundancy and health monitoring at every layer.

```mermaid
graph TD
    subgraph "Resilient Traffic Entry"
        direction LR
        ELB["Global Load Balancer / DNS"]
        Proxy1["NGINX Proxy A"]
        Proxy2["NGINX Proxy B"]
    end

    subgraph "Frontend Layer (High Availability)"
        direction LR
        FE1["FE Instance A"]
        FE2["FE Instance B"]
    end

    subgraph "Application Layer (Scalable Backend)"
        direction LR
        BE1["BE Instance A"]
        BE2["BE Instance B"]
        BE3["BE Instance C"]
    end

    subgraph "Connection Pooling (Pooled HA)"
        direction LR
        PB1["PgBouncer Node 1"]
        PB2["PgBouncer Node 2"]
    end

    subgraph "Database Layer (Distributed SQL Cluster)"
        direction LR
        DB1[("Yugabyte Node 1")]
        DB2[("Yugabyte Node 2")]
        DB3[("Yugabyte Node 3")]
    end

    %% Networking Links
    ELB --> Proxy1
    ELB --> Proxy2

    Proxy1 --> FE1
    Proxy1 --> FE2
    Proxy2 --> FE1
    Proxy2 --> FE2

    FE1 -.-> BE1
    FE1 -.-> BE2
    FE2 -.-> BE2
    FE2 -.-> BE3

    Proxy1 --> BE1
    Proxy1 --> BE2
    Proxy2 --> BE2
    Proxy2 --> BE3

    BE1 --> PB1
    BE2 --> PB1
    BE2 --> PB2
    BE3 --> PB2

    PB1 --> DB1
    PB2 --> DB2

    %% Replication and Heartbeats (Full Mesh Cluster)
    DB1 <--> DB2
    DB2 <--> DB3
    DB3 <--> DB1

    classDef ha fill:#ff99cc,stroke:#333,stroke-width:2px,color:#000;
    class DB1,DB2,DB3,PB1,PB2,FE1,FE2 ha;
```

---

### 4. Database Design (ERD)
The following Entity Relationship Diagram shows the core table relationships for asset management and transaction tracking.

```mermaid
erDiagram
    ACCOUNT ||--o{ DEPOSIT : has
    ACCOUNT ||--o{ TRANSACTION : performs
    ACCOUNT ||--o{ REQUEST : submits
    
    METAL ||--o{ DEPOSIT : "stored in"
    METAL ||--o{ TRANSACTION : "traded in"
    METAL ||--o{ REQUEST : "requested for"
    METAL ||--o{ MARKET_HISTORY : "tracks price of"

    VAULT ||--o{ DEPOSIT : "holds"
    VAULT ||--o{ TRANSACTION : "physically occurs in"
    VAULT ||--o{ REQUEST : "assigned to"

    TRANSACTION ||--o| REQUEST : "fulfills"

    ACCOUNT {
        uuid id PK
        string name
        string email
        string hashed_password
        enum type
        enum status
        float purchased_storage_kg
    }

    METAL {
        uuid id PK
        string code
        string name
        string category
        float current_price_kg
        float bar_kg
    }

    VAULT {
        uuid id PK
        string name
        string location
        float capacity_kg
        float current_load_kg
        enum status
    }

    TRANSACTION {
        uuid id PK
        uuid account_id FK
        uuid metal_id FK
        uuid vault_id FK
        string bar_ref_id
        enum type
        float quantity
        enum status
    }

    REQUEST {
        uuid id PK
        uuid account_id FK
        uuid metal_id FK
        uuid vault_id FK
        uuid transaction_id FK
        enum type
        float quantity_kg
        enum storage_type
        string serial_number
        enum status
    }

    DEPOSIT {
        uuid id PK
        uuid account_id FK
        uuid metal_id FK
        uuid vault_id FK
        float quantity_kg
        enum storage_type
        string serial_number
    }

    MARKET_HISTORY {
        uuid id PK
        uuid metal_id FK
        float price
        datetime timestamp
    }
```
