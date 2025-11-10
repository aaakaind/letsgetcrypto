# Quick Start: GitHub Clone to Run

This guide will get you from a fresh GitHub clone to a running application in under 10 minutes.

## Prerequisites

- **Python 3.8+** installed on your system
- **Git** installed
- **Internet connection** (for downloading dependencies and market data)

## One-Command Setup

```bash
git clone https://github.com/aaakaind/letsgetcrypto.git
cd letsgetcrypto
./setup.sh
```

That's it! The setup script will:
- ✅ Check your Python version
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Set up configuration files
- ✅ Run database migrations
- ✅ Optionally train initial ML models

## Manual Setup (If Needed)

If you prefer manual setup or the script doesn't work:

### Step 1: Clone the Repository

```bash
git clone https://github.com/aaakaind/letsgetcrypto.git
cd letsgetcrypto
```

### Step 2: Create Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create Necessary Directories

```bash
mkdir -p model_weights data_cache staticfiles media
```

### Step 5: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env to add your API keys (optional)
nano .env  # or use your preferred editor
```

### Step 6: Run Database Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 7: Initialize ML Environment (Optional)

```bash
./init_ml_environment.sh
```

## Running the Application

### Option 1: Web Dashboard (Recommended)

```bash
python manage.py runserver
```

Then open your browser to: **http://localhost:8000/**

### Option 2: Desktop GUI

```bash
python main.py
```

### Option 3: Quick Start Menu

```bash
./quick-start.sh
```

This interactive script helps you choose:
- Local development (Docker Compose)
- AWS deployment
- GitHub Pages setup
- Validation and testing

## First-Time Usage

### 1. Select a Cryptocurrency

Choose from Bitcoin, Ethereum, Binance Coin, Cardano, or Solana.

### 2. Fetch Market Data

Click "Refresh Data" to download the latest market information from CoinGecko API.

### 3. Train ML Models (Optional)

- If you ran `./init_ml_environment.sh`, models are already trained
- Otherwise, click "Train Models" to train with real data
- Training takes 2-5 minutes depending on your system

### 4. Get Predictions

Click "Get Predictions" to see:
- Price trend predictions
- Trading signals (Buy/Hold/Sell)
- Confidence levels
- Technical analysis

### 5. Configure Trading (Optional)

⚠️ **Use testnet first!**

- Set up API keys for Binance (testnet)
- Configure risk parameters
- Enable automated trading (if desired)

## GitHub Pages Frontend

The application includes a static frontend deployed to GitHub Pages.

### Quick Setup

1. Go to your repository on GitHub
2. Navigate to: **Settings → Pages**
3. Set source to: **GitHub Actions**
4. The next push to `main` will deploy the dashboard

Your dashboard will be available at:
```
https://[your-username].github.io/letsgetcrypto/
```

See **[GITHUB_PAGES.md](GITHUB_PAGES.md)** for detailed instructions.

## Connecting Frontend to Backend

### For Local Development

The GitHub Pages frontend can connect to your local backend:

1. Start the backend:
   ```bash
   python manage.py runserver
   ```

2. The API will be available at: `http://localhost:8000/api/`

3. GitHub Pages dashboard (when running locally) can be configured to use this endpoint

### For Production

1. Deploy backend to AWS/Heroku/etc.
2. Update GitHub Pages configuration to point to your production API
3. Enable CORS in Django settings for your GitHub Pages domain

## Environment Variables

### Required for Basic Functionality

None! The app works out of the box with free APIs.

### Optional for Enhanced Features

Add these to your `.env` file:

```bash
# Claude AI for intelligent market analysis (recommended)
ANTHROPIC_API_KEY=your-key-here

# CoinGecko API (optional - uses free tier by default)
COINGECKO_API_KEY=your-key-here

# Django Configuration (optional)
DJANGO_SECRET_KEY=auto-generated-if-not-set
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - uses SQLite by default)
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Getting API Keys

- **Anthropic Claude**: https://console.anthropic.com/
- **CoinGecko**: https://www.coingecko.com/en/api/pricing (free tier available)

## Troubleshooting

### "Python not found"

Make sure Python 3.8+ is installed:
```bash
python3 --version  # Should show 3.8 or higher
```

### "pip install fails"

Try upgrading pip first:
```bash
pip install --upgrade pip
```

For specific package issues:
```bash
# If tensorflow fails on Mac with M1/M2
pip install tensorflow-macos tensorflow-metal

# If TA-Lib fails
# On Mac: brew install ta-lib
# On Ubuntu: sudo apt-get install ta-lib
# Then: pip install TA-Lib
```

### "No module named 'django'"

Make sure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

### "Port 8000 already in use"

Use a different port:
```bash
python manage.py runserver 8080
```

### "Cannot connect to GitHub Pages"

Check that:
1. GitHub Pages is enabled in repository settings
2. Workflow has completed successfully (check Actions tab)
3. You're accessing the correct URL

## What's Included

After setup, you'll have:

- ✅ **Web Dashboard**: Modern browser-based interface
- ✅ **Desktop GUI**: Full-featured PyQt5 application
- ✅ **REST API**: Django backend with comprehensive endpoints
- ✅ **ML Models**: Trained models ready for predictions
- ✅ **Data Cache**: System for storing market data
- ✅ **GitHub Pages**: Static frontend ready to deploy

## Next Steps

1. **Read the Documentation**
   - `README_APP.md` - Full application guide
   - `DASHBOARD_GUIDE.md` - Web dashboard features
   - `FEEDBACK_LOOP.md` - Automated ML training
   - `DEPLOYMENT_GUIDE.md` - Production deployment

2. **Explore Features**
   - Try different cryptocurrencies
   - Experiment with ML models
   - View technical analysis
   - Check trading signals

3. **Deploy to Production**
   - See `DEPLOYMENT_GUIDE.md` for AWS deployment
   - See `GITHUB_PAGES.md` for static frontend
   - See `CICD_GUIDE.md` for automated deployments

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Repository                       │
│  • Source code                                          │
│  • ML models (gitignored, created locally)              │
│  • Documentation                                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ├─────────────┬─────────────┐
                          ▼             ▼             ▼
                    ┌──────────┐  ┌──────────┐  ┌──────────┐
                    │  Local   │  │  GitHub  │  │   AWS    │
                    │   Dev    │  │  Pages   │  │   ECS    │
                    └──────────┘  └──────────┘  └──────────┘
                          │             │             │
                    ┌──────────┐  ┌──────────┐  ┌──────────┐
                    │ Django   │  │  Static  │  │ Django   │
                    │ Backend  │  │   HTML   │  │ Backend  │
                    │ + PyQt5  │  │   + JS   │  │ + RDS    │
                    └──────────┘  └──────────┘  └──────────┘
```

## Machine Learning Workflow

```
1. Clone Repository
   └─> run: ./setup.sh

2. Initialize ML Environment
   └─> run: ./init_ml_environment.sh
       ├─> Creates model_weights/ directory
       ├─> Generates sample data
       └─> Trains initial models (LR, XGBoost)

3. Fetch Real Data
   └─> Via GUI/API: Fetch from CoinGecko

4. Train with Real Data
   └─> Models learn from actual cryptocurrency data

5. Continuous Learning
   └─> Feedback loop system improves models over time
```

## Support

- **Issues**: https://github.com/aaakaind/letsgetcrypto/issues
- **Discussions**: https://github.com/aaakaind/letsgetcrypto/discussions
- **Documentation**: See all `*.md` files in repository

## Important Disclaimers

⚠️ **This is educational software only**
- Cryptocurrency trading involves substantial risk
- Predictions are not guaranteed
- Always use testnet before real trading
- Never invest more than you can afford to lose
- See full disclaimers in `README.md`

---

**Ready to start?** Run:
```bash
./setup.sh
```

Then:
```bash
python manage.py runserver
```

Open **http://localhost:8000/** and start exploring!
