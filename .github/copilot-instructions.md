# GitHub Copilot Instructions for LetsGetCrypto

## Project Overview

LetsGetCrypto is an advanced cryptocurrency trading and prediction tool combining machine learning, technical analysis, and automated trading capabilities. The project includes:

- **Desktop GUI** (PyQt5) for interactive trading
- **Web Dashboard** (Django) for browser-based access
- **MCP Server** for AI assistant integration (Claude Desktop, VS Code)
- **Machine Learning Pipeline** with LSTM, XGBoost, and ensemble methods
- **Feedback Loop System** for continuous model training
- **AWS Deployment** with ECS, RDS, and CI/CD pipeline
- **GitHub Pages** static dashboard deployment

## Technology Stack

### Core Technologies
- **Python 3.11+**: Primary language
- **Django 4.2+**: Web framework for REST API and dashboard
- **PyQt5**: Desktop GUI framework
- **TensorFlow/Keras**: Deep learning (LSTM models)
- **XGBoost**: Gradient boosting models
- **scikit-learn**: Classical ML algorithms

### Data Sources
- **CoinGecko API**: Historical price data
- **Binance API (via CCXT)**: Real-time trading
- **NewsAPI**: News sentiment
- **Fear & Greed Index**: Market sentiment
- **Anthropic Claude API**: AI-powered market analysis

### Infrastructure
- **AWS ECS**: Container orchestration
- **AWS RDS**: PostgreSQL database
- **AWS CodeBuild/CodePipeline**: CI/CD
- **Docker**: Containerization
- **nginx**: Reverse proxy

## Code Style Guidelines

### Python Style
- Follow **PEP 8** conventions
- Use **type hints** for function parameters and return values
- Add comprehensive **docstrings** (Google or NumPy style preferred)
- Use descriptive variable names (e.g., `price_data`, `prediction_accuracy`)
- Prefer **list comprehensions** for simple iterations
- Use **f-strings** for string formatting

### Error Handling
- Use **try-except blocks** for API calls and external operations
- Implement **graceful degradation** when optional features fail (e.g., Claude API)
- Log errors with appropriate severity levels
- Provide user-friendly error messages in GUI/API responses

### Security
- **Never commit API keys** or secrets to version control
- Use environment variables via `python-dotenv` for sensitive data
- Keep `.env` file in `.gitignore`
- Validate user inputs to prevent injection attacks

## Project Structure

```
letsgetcrypto/
├── main.py                      # Desktop GUI application
├── manage.py                    # Django management
├── crypto_mcp_server.py         # MCP server for AI assistants
├── claude_analyzer.py           # Claude AI integration
├── crypto_api/                  # Django app for REST API
│   ├── views.py                 # API endpoints
│   ├── models.py                # Database models
│   └── urls.py                  # URL routing
├── letsgetcrypto_django/        # Django project settings
├── docs/                        # GitHub Pages dashboard
├── aws/                         # AWS deployment configs
└── examples/                    # Example code and usage

Key files:
- requirements.txt               # Python dependencies
- Dockerfile                     # Container image
- buildspec.yml                  # AWS CodeBuild config
- docker-compose.yml             # Local development stack
```

## Development Workflow

### Setting Up Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run Django migrations
python manage.py migrate

# Start Django development server
python manage.py runserver

# Or run desktop GUI
python main.py
```

### Testing
- Use **pytest** for unit and integration tests
- Test files follow `test_*.py` naming convention
- Run tests before committing: `python -m pytest`
- Key test files:
  - `test_integration.py`: Full integration tests
  - `test_mcp_server.py`: MCP server tests
  - `test_claude_integration.py`: AI integration tests
  - `test_feedback_loop.py`: ML feedback loop tests

### Deployment
- **Local**: `python manage.py runserver` or `python main.py`
- **Docker**: `docker-compose up`
- **AWS**: Use CI/CD pipeline or `./deploy-aws.sh`
- **GitHub Pages**: Push to `main` branch triggers deployment

## Key Patterns and Conventions

### Machine Learning Models
- Models stored in `model_weights/` directory (gitignored)
- Use `save_model()` and `load_model()` helper functions
- Implement **graceful fallback** when models aren't trained yet
- Track model performance in feedback loop
- Support ensemble predictions combining multiple models

### API Integration
- Use `@retry` decorator for resilient API calls
- Implement **rate limiting** awareness
- Cache responses when appropriate
- Handle API errors gracefully with fallback data

### Django REST API
- Follow RESTful conventions
- Return JSON responses with appropriate HTTP status codes
- Use Django's built-in CSRF protection for forms
- Implement proper CORS headers for frontend access

### MCP Server
- Follow Model Context Protocol specification
- Provide clear tool descriptions and schemas
- Handle both stdio and SSE transport modes
- Validate tool inputs before processing

### GUI Development
- Use PyQt5 signal/slot pattern for events
- Run long operations in separate threads to prevent UI freezing
- Update UI with `QTimer` for periodic refreshes
- Provide progress feedback for lengthy operations

## Feature-Specific Guidelines

### Feedback Loop System
- Three-tier training: Basic (1hr), Intermediate (6hr), Advanced (24hr)
- Log predictions vs actual outcomes for continuous learning
- Track model performance metrics over time
- Automatic retraining on performance degradation
- Configurable thresholds and intervals

### Claude AI Integration
- Optional feature with graceful degradation
- Check `ANTHROPIC_API_KEY` environment variable
- Fall back to standard predictions if unavailable
- Provide clear indicators when AI features are active
- Use `claude_analyzer.py` module for all Claude interactions

### Cryptocurrency Trading
- **IMPORTANT**: Include risk disclaimers in trading code
- Default to testnet/paper trading
- Implement position sizing and risk management
- Use stop-loss and take-profit orders
- Log all trading decisions and outcomes

### Web Dashboard
- Responsive design for mobile and desktop
- Real-time updates using WebSocket or polling
- Interactive charts with Chart.js or similar
- RESTful API backend with Django REST framework

## Documentation Guidelines

- Update relevant `.md` files when adding features
- Key documentation files:
  - `README.md`: Main project overview
  - `FEEDBACK_LOOP.md`: ML training system
  - `CLAUDE_SETUP.md`: AI integration setup
  - `AWS_DEPLOYMENT.md`: Cloud deployment
  - `README_MCP.md`: MCP server usage
  - `INTEGRATION_GUIDE.md`: Client integration

## Common Tasks

### Adding a New Cryptocurrency
1. Update supported coin list in configuration
2. Test data fetching from all APIs
3. Verify ML models work with new coin
4. Update documentation with supported coins

### Adding a New ML Model
1. Create model class in `main.py` or separate module
2. Implement `train()` and `predict()` methods
3. Add to ensemble prediction logic
4. Update feedback loop to include new model
5. Add model selection in GUI

### Adding a New API Endpoint
1. Define Django view in `crypto_api/views.py`
2. Add URL route in `crypto_api/urls.py`
3. Update API documentation
4. Add integration tests
5. Consider rate limiting and caching

### Extending MCP Server
1. Add tool definition in `crypto_mcp_server.py`
2. Provide JSON schema for inputs
3. Implement tool handler function
4. Update MCP documentation
5. Test with MCP client

## Important Notes

### Risk Disclosure
This tool is for **educational purposes only**. Cryptocurrency trading involves substantial risk. Always:
- Include risk disclaimers in user-facing code
- Default to testnet/paper trading
- Never guarantee prediction accuracy
- Encourage users to do their own research

### Performance Considerations
- Cache expensive computations (market data, ML predictions)
- Use background threads for long operations
- Implement connection pooling for databases
- Consider rate limits on external APIs
- Optimize model inference time

### Security Best Practices
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authentication/authorization
- Keep dependencies updated
- Never log sensitive data (API keys, passwords)

## Contributing

When suggesting code changes:
1. Maintain backward compatibility when possible
2. Update tests to cover new functionality
3. Follow existing code patterns and style
4. Update relevant documentation
5. Consider impact on all deployment targets (desktop, web, cloud)
6. Test with and without optional features (Claude, trading APIs)

## Resources

- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)
