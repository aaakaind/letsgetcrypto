# Getting Started with LetsGetCrypto

Welcome! You've just cloned the LetsGetCrypto repository. This guide will get you up and running in minutes.

## 🚀 Quick Start (One Command)

```bash
./setup.sh
```

Then:

```bash
./run.sh
```

That's it! 🎉

## 📋 What Just Happened?

### The Setup Script (`./setup.sh`)
- ✅ Checked your Python version (3.8+ required)
- ✅ Created a virtual environment in `venv/`
- ✅ Installed all Python dependencies
- ✅ Created necessary directories (`model_weights/`, `data_cache/`, etc.)
- ✅ Set up your `.env` configuration file
- ✅ Ran Django database migrations
- ✅ Optionally trained initial ML models

### The Run Script (`./run.sh`)
Starts the application with your choice of:
- 🌐 **Web Dashboard** - Browser-based interface at http://localhost:8000
- 🖥️ **Desktop GUI** - Full-featured PyQt5 application
- 📊 **Both** - Run web and desktop together

## 🧠 Machine Learning Environment

To set up the ML learning environment with pre-trained models:

```bash
./init_ml_environment.sh
```

This creates:
- Model storage directories
- Sample cryptocurrency training data
- Pre-trained models (Logistic Regression, XGBoost)
- Feature scalers and documentation

The ML environment supports:
- Automatic model training with real cryptocurrency data
- Feedback loop for continuous learning
- Multiple model types (LSTM, XGBoost, Logistic Regression)
- Ensemble predictions

## 🌐 GitHub Pages Frontend

The repository includes a static frontend that can be deployed to GitHub Pages.

### Deploy Your Own
1. Go to your repository on GitHub
2. Navigate to: **Settings → Pages**
3. Set source to: **GitHub Actions**
4. Push to `main` branch to deploy

Your dashboard will be at: `https://[username].github.io/letsgetcrypto/`

### Connect to Backend
See **[GITHUB_PAGES_INTEGRATION.md](GITHUB_PAGES_INTEGRATION.md)** for connecting the frontend to your backend API.

## 🛠️ Manual Setup (Alternative)

If you prefer to set up manually or the script didn't work:

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Set Up Environment
```bash
cp .env.example .env
# Edit .env to add your API keys (optional)
```

### 4. Initialize Database
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Create Directories
```bash
mkdir -p model_weights data_cache staticfiles media
```

### 6. Start Application
```bash
# Web Dashboard
python manage.py runserver

# OR Desktop GUI
python main.py
```

## 📱 First-Time Usage

### Web Dashboard
1. Open browser to http://localhost:8000
2. Select a cryptocurrency (Bitcoin, Ethereum, etc.)
3. Click "Refresh Data" to fetch market data
4. Click "Train Models" to train ML models
5. Click "Get Predictions" for trading signals

### Desktop GUI
1. Run `python main.py`
2. Select cryptocurrency from dropdown
3. Click "Fetch Market Data"
4. Click "Train Models"
5. View predictions and charts

## 🔑 API Keys (Optional)

The app works without API keys, but you can add these for enhanced features:

### Anthropic Claude (Recommended)
- **What it does**: AI-powered market analysis and insights
- **Get it from**: https://console.anthropic.com/
- **Add to `.env`**: `ANTHROPIC_API_KEY=your-key-here`

### CoinGecko Pro (Optional)
- **What it does**: Higher rate limits for market data
- **Get it from**: https://www.coingecko.com/en/api/pricing
- **Add to `.env`**: `COINGECKO_API_KEY=your-key-here`

## 📚 Documentation

### Essential Guides
- **[GITHUB_CLONE_GUIDE.md](GITHUB_CLONE_GUIDE.md)** - Detailed setup instructions
- **[GITHUB_PAGES_INTEGRATION.md](GITHUB_PAGES_INTEGRATION.md)** - Frontend/backend integration
- **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Web dashboard features
- **[FEEDBACK_LOOP.md](FEEDBACK_LOOP.md)** - ML training system

### Deployment
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)** - Deploy to AWS
- **[GITHUB_PAGES.md](GITHUB_PAGES.md)** - GitHub Pages setup

### Advanced
- **[README_MCP.md](README_MCP.md)** - MCP server for AI assistants
- **[CLAUDE_SETUP.md](CLAUDE_SETUP.md)** - Claude AI configuration
- **[CICD_GUIDE.md](CICD_GUIDE.md)** - CI/CD pipeline

## 🧪 Testing

### Validate Setup
```bash
python validate_setup.py
```

### Test API Integration (for GitHub Pages)
Open in browser: `docs/test-api.html`

### Run All Tests
```bash
python test_all.py
```

## 🏗️ Project Structure

```
letsgetcrypto/
├── setup.sh                    # One-command setup script ⭐
├── run.sh                      # One-command run script ⭐
├── init_ml_environment.sh      # ML environment setup ⭐
├── validate_setup.py           # Setup validation ⭐
│
├── main.py                     # Desktop GUI application
├── manage.py                   # Django management
│
├── crypto_api/                 # Django REST API
│   ├── views.py
│   ├── models.py
│   └── urls.py
│
├── letsgetcrypto_django/       # Django project settings
│   └── settings.py
│
├── docs/                       # GitHub Pages frontend
│   ├── index.html
│   ├── test-api.html          # API integration test ⭐
│   ├── js/
│   └── css/
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
│
└── Documentation files (.md)
```

## ⚠️ Important Disclaimers

**🎓 EDUCATIONAL PURPOSE ONLY**
- This tool is for learning and research
- Cryptocurrency trading involves substantial risk
- Never invest more than you can afford to lose
- Always use testnet/sandbox mode initially

**📈 NO INVESTMENT ADVICE**
- Predictions are NOT guaranteed
- Past performance does NOT predict future results
- Always conduct your own research
- Consult financial advisors before trading

## 🐛 Troubleshooting

### "Python not found"
Make sure Python 3.8+ is installed:
```bash
python3 --version
```

### "pip install fails"
Upgrade pip first:
```bash
pip install --upgrade pip
```

### "Port 8000 already in use"
Use a different port:
```bash
python manage.py runserver 8080
```

### "Virtual environment not activating"
Try:
```bash
# Linux/Mac
source venv/bin/activate

# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat
```

## 💡 Quick Tips

1. **Start Simple**: Use the web dashboard first (easier than desktop GUI)
2. **Use Testnet**: Always test with testnet before real trading
3. **Read Logs**: Check console output for errors
4. **API Keys Optional**: The app works fine without them
5. **Documentation**: All guides are in the repository

## 🆘 Need Help?

1. Check the documentation in the repository
2. Run `./validate_setup.py` to diagnose issues
3. See [GITHUB_CLONE_GUIDE.md](GITHUB_CLONE_GUIDE.md) for detailed troubleshooting
4. Open an issue on GitHub

## 🎯 Next Steps

1. ✅ You've cloned the repository
2. ▶️ Run `./setup.sh` to complete setup
3. ▶️ Run `./run.sh` to start the application
4. 📖 Read [GITHUB_CLONE_GUIDE.md](GITHUB_CLONE_GUIDE.md) for more details
5. 🚀 Start exploring cryptocurrency predictions!

---

**Ready?** Run:
```bash
./setup.sh && ./run.sh
```

Enjoy! 🚀
