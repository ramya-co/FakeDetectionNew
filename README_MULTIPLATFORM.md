# Multi-Platform Fake Account Detection System

A comprehensive Django web application for detecting fake accounts across Instagram, Twitter, and Facebook using XGBoost machine learning models with SHAP explainability.

## 🌟 Features

- **Multi-Platform Support**: Analyze accounts from Instagram, Twitter/X, and Facebook
- **Dual Input Methods**: 
  - Manual input: Enter account metrics manually
  - URL Scraping: Automatically scrape public account data
- **XGBoost ML Models**: Separate trained models for each platform
- **SHAP Explanations**: Understand why an account was classified as fake or real
- **Beautiful UI**: Modern, responsive Bootstrap 5 interface
- **Analysis History**: Save and review past analyses
- **Risk Level Assessment**: Get clear risk indicators (Very Low to Very High)

## 📋 Requirements

- Python 3.8+
- Django 4.2.7
- XGBoost 2.0.3
- SHAP 0.44.0
- scikit-learn 1.3.2
- pandas 2.1.3
- tweepy 4.14.0
- beautifulsoup4 4.12.2
- instaloader 4.10.3

## 🚀 Installation

### 1. Clone the Repository

```bash
cd /Users/happyfox2025/Desktop/FinalYear
git clone https://github.com/ramya-co/FakeDetectionNew.git
cd FakeDetectionNew
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train Models

Train XGBoost models for all three platforms:

```bash
python training/train_all_platforms.py
```

This will:
- Load data from `training/datasets/fake_social_media.csv`
- Train separate models for Instagram, Twitter, and Facebook
- Save models to `ml_model/` directory as:
  - `instagram_model.json`, `instagram_scaler.pkl`, `instagram_feature_names.pkl`
  - `twitter_model.json`, `twitter_scaler.pkl`, `twitter_feature_names.pkl`
  - `facebook_model.json`, `facebook_scaler.pkl`, `facebook_feature_names.pkl`

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 📁 Project Structure

```
FakeDetectionNew/
├── detector/                      # Main Django app
│   ├── scrapers/                 # Platform-specific scrapers
│   │   ├── instagram_scraper.py
│   │   ├── twitter_scraper.py
│   │   └── facebook_scraper.py
│   ├── models.py                 # Database models
│   ├── views.py                  # View logic for all platforms
│   ├── forms.py                  # Input forms
│   ├── predictor.py              # ML prediction with SHAP
│   ├── feature_engineering.py    # Feature calculation
│   └── utils.py                  # Utility functions
├── templates/                     # HTML templates
│   ├── home.html                 # Platform selection page
│   ├── results.html              # Unified results page
│   ├── instagram/                # Instagram-specific templates
│   ├── twitter/                  # Twitter-specific templates
│   └── facebook/                 # Facebook-specific templates
├── ml_model/                     # Trained models
│   ├── instagram_model.json
│   ├── twitter_model.json
│   ├── facebook_model.json
│   └── *.pkl                     # Scalers and feature names
├── training/                      # Model training scripts
│   ├── train_all_platforms.py    # Train all models
│   └── datasets/                 # Training data
│       └── fake_social_media.csv
└── requirements.txt              # Python dependencies
```

## 🎯 Usage

### Instagram Analysis

1. Go to home page and select Instagram
2. Choose input method:
   - **Manual**: Enter follower count, posts, engagement metrics manually
   - **URL**: Paste Instagram profile URL (e.g., `https://instagram.com/username`)
3. Click "Analyze" and view results with SHAP explanations

### Twitter Analysis

1. Select Twitter from home page
2. Choose input method:
   - **Manual**: Enter followers, tweets, engagement data
   - **URL**: Paste Twitter URL (e.g., `https://twitter.com/username` or `https://x.com/username`)
3. Get instant analysis with AI explanations

### Facebook Analysis

1. Select Facebook from home page
2. Choose input method (Manual recommended due to Facebook's scraping restrictions)
3. Analyze and view detailed results

## 🔍 Features Analyzed

The ML models analyze these features for each platform:

- **Follower Count**: Number of followers/friends
- **Following Count**: Number of accounts being followed
- **Post Count**: Total posts/tweets
- **Bio Length**: Character count of profile description
- **Profile Picture**: Presence of profile image
- **External URL**: Link in bio
- **Average Likes**: Mean likes per post
- **Average Comments**: Mean comments/replies per post
- **Follower/Following Ratio**: Calculated metric
- **Engagement Rate**: (Likes + Comments) / Followers * 100
- **Account Privacy**: Public vs Private status

## 🧠 How It Works

1. **Data Collection**: Scrape or manually enter account metrics
2. **Feature Engineering**: Calculate derived features (ratios, engagement rates)
3. **Prediction**: XGBoost model classifies account as Real (0) or Fake (1)
4. **SHAP Explanation**: Generate feature importance scores
5. **Results Display**: Show prediction, confidence, risk level, and explanations

### SHAP Explanations

SHAP (SHapley Additive exPlanations) provides:
- Feature importance ranking
- Direction of impact (increases/decreases fake likelihood)
- Human-readable explanations
- Visual bar charts

## 🔧 Configuration

### Twitter API (Optional)

For better Twitter scraping, add API credentials to environment variables:

```bash
export TWITTER_BEARER_TOKEN="your_bearer_token"
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
```

### Facebook API (Optional)

For Facebook Graph API access:

```bash
export FACEBOOK_ACCESS_TOKEN="your_access_token"
export FACEBOOK_APP_ID="your_app_id"
export FACEBOOK_APP_SECRET="your_app_secret"
```

## 📊 Model Performance

Models are trained on 10,000+ samples per platform with:
- Accuracy: ~85-90%
- Precision: ~80-85%
- Recall: ~85-90%
- F1 Score: ~82-87%

## ⚠️ Important Notes

### Scraping Limitations

- **Instagram**: May be rate-limited; use manual input as fallback
- **Twitter**: API rate limits apply; requires authentication for best results
- **Facebook**: Highly restricted; manual input strongly recommended

### Privacy & Ethics

- Only analyze public accounts
- Do not use for harassment or malicious purposes
- Respect platform terms of service
- Results are probabilistic, not definitive

## 🐛 Troubleshooting

### Scraping Fails

If URL scraping fails:
1. Try manual input method
2. Check if account is private
3. Verify URL format is correct
4. Wait a few minutes and retry (rate limiting)

### Model Not Found

If you see "Model file not found":
```bash
python training/train_all_platforms.py
```

### Module Import Errors

Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 API Endpoints

- `GET /` - Home page with platform selection
- `GET /instagram/manual/` - Instagram manual form
- `GET /instagram/url/` - Instagram URL form
- `GET /twitter/manual/` - Twitter manual form
- `GET /twitter/url/` - Twitter URL form
- `GET /facebook/manual/` - Facebook manual form
- `GET /facebook/url/` - Facebook URL form
- `GET /results/` - Analysis results page
- `GET /history/` - Analysis history
- `POST /save-analysis/` - Save analysis to database

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational purposes only.

## 👥 Authors

- Ramya
- Team Members

## 🙏 Acknowledgments

- XGBoost for the ML framework
- SHAP for explainability
- Django for the web framework
- Bootstrap for UI components

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the development team.

---

**Note**: This system is designed for research and educational purposes. Results should not be used as the sole basis for important decisions about social media accounts.
