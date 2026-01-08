# AutoBoss AI Assistant

An intelligent troubleshooting chatbot microservice for AutoBoss net cleaning machines. This service provides multilingual, interactive support through natural language processing and machine learning.

## Features

- **Multilingual Support**: Supports 6 languages (English, Greek, Arabic, Spanish, Turkish, Norwegian)
- **OpenAI Integration**: Uses GPT-4 with GPT-3.5-turbo fallback for reliable AI responses
- **Network Resilience**: Robust error handling with retries and graceful degradation
- **RESTful API**: Clean REST endpoints for chat and problem analysis
- **Health Monitoring**: Comprehensive health checks and service discovery
- **Property-Based Testing**: Extensive test coverage with property-based tests

## Architecture

The AI Assistant is designed as an independent microservice that integrates with the ABParts application:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ABParts UI    │    │  AI Assistant    │    │    OpenAI       │
│                 │    │    Service       │    │     API         │
│ ┌─────────────┐ │    │                  │    │                 │
│ │ Chat Widget │◄┼────┼► FastAPI Server  │◄───┤                 │
│ └─────────────┘ │    │                  │    │                 │
└─────────────────┘    │ ┌──────────────┐ │    └─────────────────┘
                       │ │ LLM Client   │ │
                       │ │ (Resilient)  │ │
                       │ └──────────────┘ │
                       └──────────────────┘
```

## API Endpoints

### Health & Info
- `GET /` - Service information
- `GET /info` - Configuration details
- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness check with dependencies
- `GET /health/live` - Liveness check

### AI Chat
- `POST /api/ai/chat` - General chat interaction
- `POST /api/ai/analyze-problem` - Problem analysis and diagnostics
- `GET /api/ai/models` - Available models and languages
- `GET /api/ai/session/{id}/status` - Session status

## Configuration

The service is configured through environment variables:

### Required
- `OPENAI_API_KEY` - OpenAI API key

### Optional
- `OPENAI_MODEL` - Primary model (default: gpt-4)
- `OPENAI_FALLBACK_MODEL` - Fallback model (default: gpt-3.5-turbo)
- `OPENAI_MAX_TOKENS` - Max tokens per response (default: 1000)
- `OPENAI_TEMPERATURE` - Response creativity (default: 0.7)
- `OPENAI_TIMEOUT` - API timeout in seconds (default: 30)
- `OPENAI_MAX_RETRIES` - Max retry attempts (default: 3)
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `CORS_ALLOWED_ORIGINS` - Allowed CORS origins

## Development

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Setup
1. Add your OpenAI API key to `.env.development`:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. Build and run the service:
   ```bash
   docker-compose up ai_assistant
   ```

3. The service will be available at `http://localhost:8001`

### Testing
Run the test suite:
```bash
docker run --rm -v $(pwd)/ai_assistant:/app ai-assistant-test python -m pytest
```

Run property-based tests specifically:
```bash
docker run --rm -v $(pwd)/ai_assistant:/app ai-assistant-test python -m pytest tests/test_llm_reliability_final.py
```

## Network Resilience

The AI Assistant implements comprehensive network resilience:

- **Retry Logic**: Exponential backoff for transient failures
- **Model Fallback**: Automatic fallback from GPT-4 to GPT-3.5-turbo
- **Error Handling**: Graceful degradation with user-friendly error messages
- **Rate Limit Management**: Intelligent handling of API rate limits
- **Timeout Protection**: Configurable timeouts to prevent hanging requests

## Property-Based Testing

The service includes property-based tests that validate:

- **Network Resilience**: Handles various network conditions gracefully
- **Error Recovery**: Proper fallback behavior under different error scenarios
- **Model Switching**: Correct fallback from primary to secondary models
- **Response Consistency**: Consistent response format across all conditions

## Integration with ABParts

The AI Assistant integrates with ABParts through:

1. **Docker Compose**: Runs as part of the ABParts development environment
2. **Shared Database**: Access to machine and user data for context
3. **CORS Configuration**: Allows frontend integration
4. **Environment Variables**: Shared configuration management

## Deployment

The service is containerized and ready for deployment:

- **Health Checks**: Built-in health checks for container orchestration
- **Security**: Runs as non-root user
- **Monitoring**: Comprehensive logging and error tracking
- **Scalability**: Stateless design allows horizontal scaling

## Future Enhancements

The current implementation provides the foundation for:

- Session management with Redis
- Machine-specific troubleshooting context
- Voice input/output capabilities
- Knowledge base integration
- Learning from user interactions
- Escalation to human support