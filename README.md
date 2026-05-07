# 🔬 BioVista Scientific Analysis Dashboard

A general-purpose Streamlit and Seaborn analysis platform for scientific datasets, business intelligence, anomaly detection, and predictive modeling.

## Features

### 📊 **Overview Tab**
- Dataset statistics and key metrics
- Numeric distribution visualization
- Categorical group counts and summaries
- Overall data quality assessment

### 🔍 **Anomaly Detection**
- Advanced anomaly detection using IQR and Z-score methods
- Identifies unusual observations based on:
  - Extreme values in numeric features
  - Unexpected deviations from typical distributions
  - Rare or inconsistent measurement outcomes
- Anomaly score ranking system
- Detailed breakdown by feature and record
### 💡 **Intelligent Insights**
- **Trend Analysis**: Detects strong increasing or decreasing patterns
- **Feature Importance**: Identifies top numeric drivers
- **Volatility Detection**: Flags high-variance signals
- **Risk Assessment**: Highlights unstable or noisy features
- **Actionable Guidance**: Provides dataset-specific recommendations

### 🔧 **Problems & Solutions** ⭐ **NEW**
- **Data Quality Checks**: Identifies missing values, outliers, and irregularities
- **Analysis Pitfall Detection**: Correlation bias, sample size concerns, and drift
- **Actionable Solutions**: Domain-neutral recommendations for data and model improvement
- **Model Readiness Assessment**: Helps determine if the dataset is suitable for predictive analytics

### 🔮 **Predictive Analytics** ⭐ **NEW**
- **Machine Learning Models**: Random Forest classification and regression
- **Target Selection**: Choose any numeric feature as a prediction target
- **Model Evaluation**: Accuracy or RMSE metrics depending on task
- **Feature Importance**: Understand what drives predictions
- **Scientific & Business Use Cases**: Forecast operational, experimental, or performance outcomes

### 📈 **Group Analysis**
- Compare categories, cohorts, or experimental groups
- Aggregate numeric summaries by group
- Identify group-level differences and trends
- Discover high-performing or risky segments

### 📉 **Detailed Statistical Analysis**
- Individual metric deep-dive
- Distribution analysis with mean/median overlays
- Box plot outlier detection
- Correlation heatmap for all key metrics

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create your local environment file:**
```bash
copy .env.example .env
```
- Then update `.env` with your Stripe secret key and URLs.

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Access in browser:**
The app will open automatically at `http://localhost:8501`

## Data Requirements

The app accepts any CSV dataset with numeric and categorical columns. For best results:
- Include a timestamp or date column when available
- Provide clear numeric measurements for predictions and anomaly detection
- Use consistent categorical labels for cohort/group analysis
- Include at least 10-20 records for basic predictive modeling

## Usage Guide

### Navigation
Use the sidebar to switch between different analysis modes:
- **📊 Overview**: Start here for general data exploration
- **🔍 Anomalies**: Identify unusual records and outliers
- **💡 Insights**: Get AI-generated recommendations
- **🔧 Problems & Solutions**: Identify data issues and get actionable fixes ⭐ **NEW**
- **🔮 Predictive Analytics**: Train models on your dataset ⭐ **NEW**
- **📈 Group Analysis**: Compare categories or cohorts
- **📉 Detailed Stats**: Deep statistical analysis

### New Features Usage

#### 🔧 Problems & Solutions
- **Automatic Detection**: The app automatically identifies common data analysis problems
- **Severity Levels**: High and medium severity issues are categorized
- **Data-Driven Solutions**: Get actionable recommendations for dataset issues
- **Business Impact**: See quantified benefits of implementing improvements

#### 🔮 Predictive Analytics
- **Model Training**: Click to train ML models (cached for performance)
- **Target Selection**: Choose any numeric feature for prediction
- **Feature Importance**: Discover which variables matter most
- **Risk Assessment**: Understand prediction uncertainty and variance

### Filters
- Use the dataset columns to focus on relevant segments
- In Group Analysis, select multiple categories for comparison

### Export Tips
- Click on tables to sort and filter
- Screenshot visualizations for reports
- Use browser's "Save As" for data tables

## Key Metrics Explained

- **Anomaly Score**: Count of variables with abnormal values
- **Trend Stability**: How consistent signals are over time
- **Feature Importance**: Which measurements matter most for predictions
- **Group Differences**: Cohort comparisons across categories

## Business Insights Examples

The app generates insights like:
- ✅ Detecting strongly trending variables in your dataset
- ✅ Identifying high-variance features requiring robust methods
- ✅ Highlighting data quality risks before modeling
- ✅ Recommending feature engineering opportunities
- ✅ Providing model-ready guidance for scientific analysis

## What Makes This App Different

### Problems Other Analysis Apps Struggle With:

#### ❌ **Data Quality Issues**
- **Problem**: Missing data, outliers, and inconsistent measurements
- **Our Solution**: Automated quality checks and robust statistical diagnostics

#### ❌ **Overly Narrow Analysis**
- **Problem**: Tailored to one domain or fixed metrics
- **Our Solution**: Generic, dataset-agnostic analysis with domain-flexible insights

#### ❌ **Lack of Actionable Guidance**
- **Problem**: Presents results without recommendations
- **Our Solution**: Suggests concrete next steps for data and modeling

#### ❌ **No Predictive Context**
- **Problem**: Only historical summary statistics
- **Our Solution**: Builds prediction-ready models and evaluates performance

#### ❌ **Weak Anomaly Detection**
- **Problem**: Outliers undetected or misclassified
- **Our Solution**: Multiple anomaly methods for robust detection and ranking

#### ❌ **Insufficient Group Analysis**
- **Problem**: Fails to compare categories or cohorts effectively
- **Our Solution**: Group-level summaries and trend comparisons

### ✅ **Why BioVista Works:**
- **Smart Data Validation**: Automatic quality checks and missing data handling
- **Contextual Analytics**: Finds patterns beyond simple averages
- **Predictive Intelligence**: Train classification or regression models on your dataset
- **Actionable Recommendations**: Both data and modeling guidance
- **Flexible Deployment**: Works with scientific, operational, and business data

## Technical Stack

- **Streamlit**: Interactive web framework
- **Pandas**: Data manipulation and analysis
- **Seaborn/Matplotlib**: Advanced visualizations
- **Scipy**: Statistical analysis
- **Scikit-learn**: Machine learning and predictions ⭐ **NEW**
- **NumPy**: Numerical computations

## Customization

You can extend the app by:
1. Adding more anomaly detection methods in `detect_anomalies_*` functions
2. Creating new insight generators in `generate_insights()`
3. Adding more visualizations in any analysis section
4. Creating custom feature engineering and grouping logic

## Performance

- Data is cached on first load for fast interactions
- Designed for responsive performance on moderate datasets
- Real-time filtering and analysis

## Future Enhancements

- Custom anomaly detection methods
- Support for additional data formats
- Export reports and charts
- Enhanced predictive workflows
- Automated data validation pipelines
- Domain-specific feature engineering templates

## Deployment

This app can be deployed to Streamlit Community Cloud, Docker-friendly cloud hosts, or any service that supports Python web apps.

### Streamlit Community Cloud
1. Push this project to a GitHub repository.
2. Visit https://share.streamlit.io
3. Connect your GitHub account and select the repository and branch.
4. Choose `app.py` as the main app file.

### Docker deployment
1. Build the Docker image:
   ```bash
   docker build -t biovista-analytics .
   ```
2. Run the container:
   ```bash
   docker run -p 8501:8501 biovista-analytics
   ```

### Notes
- The app listens on port `8501`.
- `requirements.txt` contains all Python dependencies.
- `.streamlit/config.toml` is included for Streamlit host configuration.
