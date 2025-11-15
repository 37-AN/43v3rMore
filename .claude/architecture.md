# System Architecture

## Overview
```
┌─────────────────────────────────────────┐
│         CLIENT INTERFACES               │
│  Web Dashboard | Telegram | WhatsApp    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         API GATEWAY (FastAPI)           │
│  Authentication | Rate Limiting          │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼─────┐  ┌─────▼──────┐
│  QUANTUM   │  │    MCP     │
│  ENGINE    │  │  SERVERS   │
│  (Qiskit)  │  │ (Claude AI)│
└──────┬─────┘  └─────┬──────┘
       │               │
       └───────┬───────┘
               │
┌──────────────▼──────────────────────────┐
│         DATA LAYER                      │
│  Supabase | Redis | Market Data (MT5)  │
└─────────────────────────────────────────┘
```

## Key Components

### 1. Quantum Trading Engine
- **Purpose**: Generate high-accuracy trading signals
- **Tech**: Python, Qiskit, NumPy, Pandas
- **Data Flow**: MT5 → QPE Analysis → Signal Generation
- **Output**: Trading signals with entry, SL, TP

### 2. MCP Servers (Business Automation)
- **Purpose**: Autonomous business operations
- **Tech**: Python, Anthropic Claude API
- **Functions**: Lead qualification, content generation, support, billing
- **Output**: Automated business decisions and actions

### 3. API Layer
- **Purpose**: Expose services to clients
- **Tech**: FastAPI, WebSockets, JWT auth
- **Endpoints**: /signals, /subscribe, /account, /admin
- **Security**: API keys, rate limiting, CORS

### 4. Communication Layer
- **Purpose**: Multi-channel signal delivery
- **Tech**: Telegram Bot API, Twilio, SendGrid
- **Channels**: Telegram, WhatsApp, Email, SMS
- **Reliability**: Retry logic, fallback channels

### 5. Data Layer
- **Purpose**: Persistent storage and caching
- **Tech**: Supabase (PostgreSQL), Redis
- **Data**: Users, subscriptions, signals, analytics
- **Backup**: Daily automated backups

## Data Flow: Signal Generation to Delivery
1. **Market Data** → MT5 streams real-time prices
2. **Analysis** → Quantum engine processes with QPE
3. **Signal** → Generated with confidence score
4. **Storage** → Saved to Supabase
5. **Filtering** → MCP determines recipient list
6. **Delivery** → Sent via Telegram/WhatsApp
7. **Tracking** → Performance logged for analytics

## Scaling Strategy
- **Phase 1 (0-100 clients)**: Single server, free tiers
- **Phase 2 (100-500 clients)**: Paid tiers, horizontal scaling
- **Phase 3 (500+ clients)**: Kubernetes, load balancing
