# API Documentation

Quantum Trading AI REST API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.quantumtrading.ai
```

## Authentication

All protected endpoints require Bearer token authentication.

```http
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Health Check

#### GET /health

Check API health status.

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### Signals

#### GET /api/v1/signals

Get recent trading signals.

**Parameters**
- `symbol` (optional): Filter by symbol
- `limit` (optional): Maximum signals to return (default: 10)

**Response**
```json
{
  "signals": [
    {
      "id": "uuid",
      "symbol": "EURUSD",
      "action": "BUY",
      "confidence": 0.87,
      "entry_price": 1.1000,
      "stop_loss": 1.0950,
      "take_profit": 1.1100,
      "risk_reward": 2.0,
      "timeframe": "H1",
      "reason": "Bullish cycle detected",
      "created_at": "2025-11-15T10:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2025-11-15T10:30:00Z"
}
```

#### GET /api/v1/signals/{signal_id}

Get specific signal by ID.

#### POST /api/v1/analyze

Run quantum analysis (Pro+ plans only).

**Request Body**
```json
{
  "symbols": ["EURUSD", "GBPUSD"],
  "timeframe": "H1",
  "max_signals": 5
}
```

### Users

#### POST /api/v1/users

Create new user account.

**Request Body**
```json
{
  "email": "user@example.com",
  "name": "John Trader",
  "phone": "+27821234567",
  "plan": "basic"
}
```

#### GET /api/v1/users/me

Get current user information.

### Subscriptions

#### POST /api/v1/subscriptions

Create subscription.

**Request Body**
```json
{
  "plan": "pro",
  "payment_method": "payfast"
}
```

#### GET /api/v1/subscriptions/me

Get current subscription.

## Error Responses

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {}
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

- 60 requests per minute per user
- 1000 requests per hour per user

## WebSocket

Connect to `/ws` for real-time signal delivery.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Signal received:', data);
};
```
