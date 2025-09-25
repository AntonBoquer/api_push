# Bus Occupancy API Push System

A Python FastAPI application for handling push requests with bearer token authentication and Supabase database integration. Designed for deployment on Vercel.

## Features

- 🔐 Bearer token authentication
- 📡 RESTful API endpoints for push requests
- 🚌 Specialized bus occupancy data handling
- 🗄️ Supabase database integration
- 🚀 Ready for Vercel deployment
- 📊 Comprehensive logging and error handling
- 🔍 Health check endpoints
- 📝 Automatic API documentation

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# API Security
BEARER_TOKEN=your_bearer_token_for_authentication

# Environment
ENVIRONMENT=development
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check API health and database connectivity

### General Push Endpoint
- **POST** `/api/v1/push` - Handle generic JSON push requests

### Bus Occupancy Specific
- **POST** `/api/v1/bus-occupancy` - Update bus occupancy data
- **GET** `/api/v1/bus-occupancy/{bus_id}` - Get current bus occupancy

## Authentication

All endpoints (except `/` and `/health`) require a bearer token in the Authorization header:

```
Authorization: Bearer your_bearer_token_here
```

## Example Usage

### Push Generic Data

```bash
curl -X POST "https://your-api.vercel.app/api/v1/push" \
  -H "Authorization: Bearer your_bearer_token" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "message": "Hello from bus system",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "metadata": {
      "source": "mobile_app",
      "version": "1.0"
    }
  }'
```

### Update Bus Occupancy

```bash
curl -X POST "https://your-api.vercel.app/api/v1/bus-occupancy" \
  -H "Authorization: Bearer your_bearer_token" \
  -H "Content-Type: application/json" \
  -d '{
    "bus_id": "BUS_001",
    "route_id": "ROUTE_A1",
    "occupancy_count": 25,
    "max_capacity": 50,
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }'
```

## Deployment on Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Set Environment Variables

In your Vercel dashboard, add these environment variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `BEARER_TOKEN`

### 3. Deploy

```bash
vercel --prod
```

## Supabase Database Schema

### Simplified Schema (3 columns only)

Both tables use the same simplified structure:

#### push_requests
```sql
CREATE TABLE push_requests (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  json_data JSONB NOT NULL
);
```

#### bus_occupancy
```sql
CREATE TABLE bus_occupancy (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  json_data JSONB NOT NULL
);
```

**Column Descriptions:**
- `id`: Auto-incrementing primary key
- `created_at`: Automatically set timestamp when record is created
- `json_data`: All the actual data stored as JSON (flexible structure)

## Response Format

All endpoints return responses in this format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Development

### Running with Auto-reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

When running in development mode, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Security Considerations

1. **Bearer Token**: Use a strong, randomly generated bearer token (this is your only authentication)
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure CORS properly for your domain
4. **Environment Variables**: Never commit sensitive data to version control
5. **Rate Limiting**: Consider implementing rate limiting for production use

## Error Handling

The API includes comprehensive error handling:
- 401: Invalid or missing bearer token
- 404: Resource not found
- 422: Validation errors
- 500: Internal server errors

## Logging

All requests and errors are logged with appropriate levels:
- INFO: Successful operations
- WARNING: Invalid authentication attempts
- ERROR: System errors and exceptions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
