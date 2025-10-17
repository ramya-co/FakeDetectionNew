# Instagram Fake Account Detection System

A comprehensive web application that detects fake Instagram accounts using advanced machine learning with explainable AI (XGBoost + SHAP).

![Instagram Fake Account Detection](https://img.shields.io/badge/AI-Powered-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![Django](https://img.shields.io/badge/Django-4.2-blue) ![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange) ![SHAP](https://img.shields.io/badge/SHAP-Explainable%20AI-purple)

## 🚀 Features

- **Dual Input Methods**: Manual input forms and Instagram URL scraping
- **AI-Powered Detection**: XGBoost model with high accuracy
- **Explainable AI**: SHAP values show exactly why a prediction was made
- **Real-time Analysis**: Instant results with confidence scores
- **Analysis History**: Track and review past analyses
- **Mobile Responsive**: Works perfectly on all devices
- **Professional UI**: Modern, clean design with smooth animations

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5, Chart.js
- **Backend**: Django 4.2 (Python)
- **Database**: SQLite
- **ML Framework**: XGBoost 2.0
- **Explainable AI**: SHAP 0.44
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Web Scraping**: Instaloader 4.10

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fake_account_detection
```

### 2. Create Virtual Environment
```bash
python -m venv instagram_detector_env
source instagram_detector_env/bin/activate  # On macOS/Linux
# or
instagram_detector_env\Scripts\activate     # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Sample Training Data
```bash
cd training
python generate_sample_data.py --real-samples 1500 --fake-samples 1500 --split
```

### 5. Train the Model
```bash
python train_model.py --data-files datasets/dataset1.csv datasets/dataset2.csv datasets/dataset3.csv
```

### 6. Set Up Django
```bash
cd ..
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
```

### 7. Run the Application
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📊 Model Training

### Generate Custom Training Data
```bash
cd training
python generate_sample_data.py --real-samples 2000 --fake-samples 2000 --output-dir custom_data
```

### Train with Custom Data
```bash
python train_model.py --data-files custom_data/instagram_data.csv --test-size 0.2
```

### Training Results
The training script will output:
- Model accuracy, precision, recall, F1-score
- Confusion matrix
- Feature importance rankings
- Model artifacts saved to `ml_model/` directory

## 🎯 Usage

### Method 1: Manual Input
1. Navigate to "Manual Input Analysis"
2. Fill in all account metrics:
   - Username, follower/following counts
   - Post count, bio length
   - Average likes/comments per post
   - Profile features (profile pic, external URL)
3. Submit for instant analysis

### Method 2: URL Scraping
1. Navigate to "URL Scraping Analysis"
2. Enter Instagram profile URL (e.g., `https://www.instagram.com/username/`)
3. System automatically scrapes and analyzes the account
4. Handles both public and private accounts

### Understanding Results
- **Prediction**: Real or Fake classification
- **Confidence Score**: Model certainty (0-100%)
- **Risk Level**: Very Low to Very High based on confidence
- **SHAP Explanation**: Top 5 features influencing the decision
- **Feature Breakdown**: Complete account metrics analysis

## 🔍 Model Features

The ML model analyzes these key features:

| Feature | Description |
|---------|-------------|
| `follower_count` | Number of followers |
| `following_count` | Number of accounts following |
| `post_count` | Total number of posts |
| `bio_length` | Character count of bio text |
| `has_profile_pic` | Has profile picture (boolean) |
| `has_external_url` | Has external URL in bio (boolean) |
| `avg_likes_per_post` | Average likes per post |
| `avg_comments_per_post` | Average comments per post |
| `follower_following_ratio` | Follower/following ratio |
| `engagement_rate` | (Likes + Comments) / Followers * 100 |
| `is_private` | Account privacy setting |

## 📁 Project Structure

```
fake_account_detection/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── README.md                   # This file
│
├── instagram_detector/         # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── detector/                   # Main Django app
│   ├── models.py              # Database models
│   ├── views.py               # View controllers
│   ├── forms.py               # Django forms
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin interface
│   ├── scraper.py             # Instagram scraping
│   ├── predictor.py           # ML prediction logic
│   ├── feature_engineering.py  # Feature processing
│   └── utils.py               # Utility functions
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── manual_form.html
│   ├── url_form.html
│   ├── results.html
│   └── history.html
│
├── static/                     # Static files
│   ├── css/style.css          # Custom styles
│   └── js/main.js             # JavaScript functionality
│
├── ml_model/                   # Trained model artifacts
│   ├── instagram_model.json   # XGBoost model
│   ├── scaler.pkl             # Feature scaler
│   └── feature_names.pkl      # Feature names
│
└── training/                   # Model training
    ├── train_model.py         # Training script
    ├── generate_sample_data.py # Data generation
    └── datasets/              # Training data
        ├── dataset1.csv
        ├── dataset2.csv
        └── dataset3.csv
```

## 🎨 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage |
| `/manual/` | GET/POST | Manual input form |
| `/url/` | GET/POST | URL scraping form |
| `/results/` | GET | Analysis results |
| `/history/` | GET | Analysis history |
| `/api/analyze/manual/` | POST | Manual analysis API |
| `/api/analyze/url/` | POST | URL analysis API |
| `/save-analysis/` | POST | Save analysis to history |

## ⚙️ Configuration

### Model Parameters
Edit `training/train_model.py` to adjust:
- XGBoost hyperparameters
- Train/test split ratio
- Feature engineering logic

### Django Settings
Edit `instagram_detector/settings.py` for:
- Database configuration
- Static files settings
- Model file paths
- Logging configuration

## 🚨 Important Notes

### Instagram Rate Limiting
- Instagram may rate limit scraping requests
- If scraping fails, users can fallback to manual input
- Delays are built-in to minimize rate limiting

### Model Accuracy
- The model is trained on synthetic data for demonstration
- For production use, train with real Instagram account data
- Current model achieves ~95% accuracy on synthetic data

### Privacy & Ethics
- This tool is for educational/research purposes
- Respect Instagram's Terms of Service
- Don't use for malicious purposes or harassment

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Model Not Found**: Train the model first
   ```bash
   cd training
   python train_model.py --data-files datasets/*.csv
   ```

3. **Scraping Fails**: Use manual input as fallback
   - Instagram blocks requests frequently
   - This is expected behavior

4. **Database Errors**: Run migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Performance Optimization

1. **For High Traffic**: Use production database (PostgreSQL)
2. **For Scaling**: Deploy with Gunicorn + Nginx
3. **For Speed**: Implement Redis caching
4. **For Reliability**: Add Celery for background tasks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- XGBoost team for the excellent ML framework
- SHAP developers for explainable AI capabilities
- Django community for the robust web framework
- Bootstrap team for responsive UI components
- Instaloader developers for Instagram scraping tools

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing issues on GitHub
3. Create a new issue with detailed description
4. Include error messages and system information

## 🚀 Future Enhancements

- [ ] Real-time dashboard with analytics
- [ ] Batch analysis for multiple accounts
- [ ] Export results to PDF/Excel
- [ ] Integration with other social media platforms
- [ ] Advanced visualization charts
- [ ] API rate limiting and authentication
- [ ] Docker containerization
- [ ] Automated model retraining pipeline

---

**⚠️ Disclaimer**: This tool provides AI-based predictions for educational and research purposes. Results should not be used as the sole basis for important decisions. Always respect platform terms of service and user privacy.
