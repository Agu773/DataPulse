import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler, MinMaxScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="BioVista Analytics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['axes.facecolor'] = '#060608'
plt.rcParams['figure.facecolor'] = '#060608'
plt.rcParams['savefig.facecolor'] = '#060608'
plt.rcParams['text.color'] = '#e8e8e8'
plt.rcParams['axes.edgecolor'] = '#e8e8e8'
plt.rcParams['axes.labelcolor'] = '#e8e8e8'
plt.rcParams['axes.titlecolor'] = '#e8e8e8'
plt.rcParams['xtick.color'] = '#e8e8e8'
plt.rcParams['ytick.color'] = '#e8e8e8'
plt.rcParams['grid.color'] = '#222222'
plt.rcParams['legend.facecolor'] = '#0d0d11'
plt.rcParams['legend.edgecolor'] = '#1e1e1e'

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500;700&display=swap');
      html, body, [class*="css"], .stApp, .stSidebar, .stSidebar .css-1d391kg, .stSidebar .css-1n76uvr, .stSidebar .css-1lcbmhc {
        font-family: 'DM Mono', monospace !important;
        color: #e8e8e8 !important;
        background: #060608 !important;
      }
      .stApp {
        background: #060608 !important;
        color: #e8e8e8 !important;
      }
      .css-1ehd9qt, .css-1n76uvr, .css-1lcbmhc, .css-1d391kg, .stSidebar .css-1d391kg, .stSidebar .css-1n76uvr {
        background: rgba(8, 8, 10, 0.92) !important;
        border: 1px solid #1e1e1e !important;
        color: #e8e8e8 !important;
      }
      .stButton>button, button, .css-1emrehy.edgvbvh3 {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: #e8e8e8 !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 16px 40px rgba(124, 58, 237, 0.28) !important;
      }
      .stButton>button:hover, button:hover, .css-1emrehy.edgvbvh3:hover {
        opacity: 0.96 !important;
      }
      .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div, .stMultiSelect>div, .stNumberInput>div>input, .stDateInput>div>input, .stFileUploader>div {
        background: #09090b !important;
        color: #e8e8e8 !important;
        border: 1px solid #1e1e1e !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04) !important;
      }
      .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stHeader, h1, h2, h3 {
        color: #f3f3f3 !important;
        text-shadow: 0 0 20px rgba(124, 58, 237, 0.35), 0 0 40px rgba(167, 139, 250, 0.18);
      }
      .stMarkdown p, .stMarkdown span, .stText, .css-1x0uki3, .stMetricValue {
        color: #e8e8e8 !important;
      }
      .stMarkdown a, a {
        color: #a78bfa !important;
      }
      .css-1v0mbdj.e1fqkh3o4, .css-1d391kg, .css-1n76uvr, .css-1lcbmhc {
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.20) !important;
      }
      .stExpanderHeader, .stExpanderContent, .streamlit-expanderHeader, .streamlit-expanderContent {
        background: rgba(12,12,14,0.9) !important;
        border: 1px solid #1e1e1e !important;
      }
      .stSidebar .stButton>button, .stSidebar button {
        width: 100% !important;
      }
    </style>
    """,
    unsafe_allow_html=True
)

DEFAULT_CSV = 'epl_final.csv'
EXPECTED_FOOTBALL_COLS = [
    'Season', 'MatchDate', 'HomeTeam', 'AwayTeam', 'FullTimeHomeGoals',
    'FullTimeAwayGoals', 'FullTimeResult', 'HomeShots', 'AwayShots',
    'HomeShotsOnTarget', 'AwayShotsOnTarget', 'HomeCorners', 'AwayCorners',
    'HomeFouls', 'AwayFouls', 'HomeYellowCards', 'AwayYellowCards',
    'HomeRedCards', 'AwayRedCards'
]

@st.cache_data
def load_data(file=None):
    if file is not None:
        df = pd.read_csv(file)
    else:
        df = pd.read_csv(DEFAULT_CSV)

    for date_col in ['MatchDate', 'Date', 'Timestamp']:
        if date_col in df.columns:
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                break
            except Exception:
                pass

    return df


def is_football_dataset(df):
    return all(col in df.columns for col in EXPECTED_FOOTBALL_COLS)


def get_numeric_columns(df):
    return df.select_dtypes(include=[np.number]).columns.tolist()


def has_categorical_columns(df):
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def prepare_football_data(df):
    df = df.copy()
    df['MatchDate'] = pd.to_datetime(df['MatchDate'])
    df['TotalGoals'] = df['FullTimeHomeGoals'] + df['FullTimeAwayGoals']
    df['GoalDifference'] = abs(df['FullTimeHomeGoals'] - df['FullTimeAwayGoals'])
    df['HomeAttackRating'] = (df['HomeShots'] + df['HomeShotsOnTarget']) / 2
    df['AwayAttackRating'] = (df['AwayShots'] + df['AwayShotsOnTarget']) / 2
    df['HomeDefenseRating'] = df['HomeFouls'] + df['HomeYellowCards']
    df['AwayDefenseRating'] = df['AwayFouls'] + df['AwayYellowCards']
    df['HomeEfficiency'] = np.divide(
        df['HomeShotsOnTarget'], df['HomeShots'], where=df['HomeShots'] != 0, out=np.zeros_like(df['HomeShots'])
    )
    df['AwayEfficiency'] = np.divide(
        df['AwayShotsOnTarget'], df['AwayShots'], where=df['AwayShots'] != 0, out=np.zeros_like(df['AwayShots'])
    )
    return df


def summarize_missing(df):
    missing = df.isnull().sum()
    total_missing = missing.sum()
    percent = (missing / len(df) * 100).round(2)
    return pd.DataFrame({'missing_count': missing, 'missing_pct': percent}).sort_values('missing_count', ascending=False), total_missing


def impute_missing_values(df, strategy='median'):
    df = df.copy()
    numeric_cols = get_numeric_columns(df)
    for col in numeric_cols:
        if df[col].isnull().any():
            if strategy == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
            elif strategy == 'median':
                df[col].fillna(df[col].median(), inplace=True)
            elif strategy == 'zero':
                df[col].fillna(0, inplace=True)
            elif strategy == 'mode':
                mode_val = df[col].mode()
                df[col].fillna(mode_val.iloc[0] if not mode_val.empty else 0, inplace=True)
    return df


def scale_numeric_data(df, method='none'):
    df = df.copy()
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols or method == 'none':
        return df

    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'robust':
        scaler = RobustScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    else:
        return df

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df


def preprocess_dataset(df, impute=False, strategy='median', scaling='none'):
    df = df.copy()
    if impute:
        df = impute_missing_values(df, strategy)
    if scaling != 'none':
        df = scale_numeric_data(df, scaling)
    return df


USER_DB_FILE = Path("user_accounts.json")
ADMIN_TOKEN = os.getenv("AZREAL", "biovista-admin-token")
TRIAL_ANALYSES = int(os.getenv("BIOVISTA_TRIAL_COUNT", 3))
PREMIUM_DURATION_DAYS = int(os.getenv("BIOVISTA_PREMIUM_DAYS", 30))
STRIPE_SECRET_KEY = os.getenv("AXILIUM", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:8501/?payment=success")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "http://localhost:8501/?payment=cancel")

try:
    import stripe
    if STRIPE_SECRET_KEY:
        stripe.api_key = STRIPE_SECRET_KEY
except ImportError:
    stripe = None


def verify_stripe_webhook(request_body, signature):
    """Verify webhook signature and return event data."""
    if not stripe or not STRIPE_WEBHOOK_SECRET:
        return None
    try:
        event = stripe.Webhook.construct_event(
            request_body, signature, STRIPE_WEBHOOK_SECRET
        )
        return event
    except Exception:
        return None


def handle_checkout_completed(session_id, user_email=None):
    """Handle Stripe checkout.session.completed event."""
    if not stripe or not STRIPE_SECRET_KEY:
        return False
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid" and user_email:
            mark_user_paid(user_email, days=PREMIUM_DURATION_DAYS)
            return True
    except Exception:
        pass
    return False


def load_user_db():
    if not USER_DB_FILE.exists():
        return {}
    try:
        return json.loads(USER_DB_FILE.read_text())
    except Exception:
        return {}


def save_user_db(db):
    USER_DB_FILE.write_text(json.dumps(db, indent=2))


def get_paid_until(user):
    paid_until = user.get("paid_until")
    if not paid_until:
        return None
    try:
        return datetime.fromisoformat(paid_until)
    except Exception:
        return None


def user_is_paid(user):
    if not user:
        return False
    if user.get("is_admin"):
        return True
    if user.get("paid"):
        return True
    paid_until = get_paid_until(user)
    return bool(paid_until and paid_until > datetime.now())


def format_paid_until(user):
    paid_until = get_paid_until(user)
    if paid_until:
        return paid_until.strftime("%Y-%m-%d %H:%M")
    return None


def get_user(email):
    db = load_user_db()
    return db.get(email.lower()) if email else None


def create_user(email):
    db = load_user_db()
    email_key = email.lower()
    if email_key not in db:
        db[email_key] = {
            "email": email_key,
            "paid": False,
            "paid_until": None,
            "trial_remaining": TRIAL_ANALYSES,
            "is_admin": False,
            "created_at": str(pd.Timestamp.now())
        }
        save_user_db(db)
    return db[email_key]


def update_user(email, updates):
    db = load_user_db()
    email_key = email.lower()
    user = db.get(email_key)
    if not user:
        return None
    user.update(updates)
    db[email_key] = user
    save_user_db(db)
    return user


def consume_trial(email):
    user = get_user(email)
    if not user or user_is_paid(user):
        return True
    if user.get("trial_remaining", 0) > 0:
        user["trial_remaining"] -= 1
        update_user(email, {"trial_remaining": user["trial_remaining"]})
        return True
    return False


def user_has_access(email, premium=False):
    if not email:
        return False if premium else True
    user = get_user(email)
    if not user:
        return False if premium else True
    if user.get("is_admin"):
        return True
    if not premium:
        return True
    return user_is_paid(user) or user.get("trial_remaining", 0) > 0


def build_stripe_success_url():
    if "{CHECKOUT_SESSION_ID}" in STRIPE_SUCCESS_URL:
        return STRIPE_SUCCESS_URL
    if "?" in STRIPE_SUCCESS_URL:
        return STRIPE_SUCCESS_URL + "&session_id={CHECKOUT_SESSION_ID}"
    return STRIPE_SUCCESS_URL + "?payment=success&session_id={CHECKOUT_SESSION_ID}"


def create_stripe_checkout(email=None):
    if not stripe or not STRIPE_SECRET_KEY:
        return None
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "BioVista Premium Access",
                        "description": "Unlimited premium analytics access for 30 days"
                    },
                    "unit_amount": 4999,
                },
                "quantity": 1,
            }],
            success_url=build_stripe_success_url(),
            cancel_url=STRIPE_CANCEL_URL,
            metadata={"user_email": email} if email else {},
        )
        if email:
            update_user(email, {"last_checkout_session": session.id})
        return session.url
    except Exception:
        return None


def mark_user_paid(email, days=PREMIUM_DURATION_DAYS):
    user = get_user(email)
    if not user:
        return None
    paid_until = datetime.now() + timedelta(days=days)
    return update_user(email, {"paid": True, "paid_until": paid_until.isoformat()})


def ensure_user_session():
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "paid" not in st.session_state:
        st.session_state.paid = False
    if "paid_until" not in st.session_state:
        st.session_state.paid_until = None
    if "trial_remaining" not in st.session_state:
        st.session_state.trial_remaining = TRIAL_ANALYSES


def sign_in_user(email, admin_token=None):
    if not email:
        return None
    user = create_user(email)
    if admin_token and admin_token == ADMIN_TOKEN:
        user["is_admin"] = True
        user = update_user(email, {"is_admin": True})
    st.session_state.user_email = user["email"]
    st.session_state.is_admin = user.get("is_admin", False)
    st.session_state.paid = user_is_paid(user)
    st.session_state.paid_until = format_paid_until(user)
    st.session_state.trial_remaining = user.get("trial_remaining", TRIAL_ANALYSES)
    return user


def load_session_user():
    ensure_user_session()
    if st.session_state.user_email:
        user = get_user(st.session_state.user_email)
        if user:
            st.session_state.paid = user_is_paid(user)
            st.session_state.paid_until = format_paid_until(user)
            st.session_state.trial_remaining = user.get("trial_remaining", TRIAL_ANALYSES)
            st.session_state.is_admin = user.get("is_admin", False)
            return user
    return None


def get_trial_status():
    if st.session_state.paid:
        if st.session_state.paid_until:
            return f"Premium active until {st.session_state.paid_until}"
        return "Premium access active"
    return f"{st.session_state.trial_remaining} free premium analyses left"


def register_payment(email):
    if STRIPE_SECRET_KEY and stripe:
        return create_stripe_checkout(email)
    mark_user_paid(email)
    return None


def can_use_premium_feature():
    if st.session_state.is_admin:
        return True
    if st.session_state.paid:
        return True
    if st.session_state.trial_remaining > 0:
        return True
    return False


def consume_premium_allowance():
    if st.session_state.is_admin or st.session_state.paid:
        return True
    if st.session_state.trial_remaining > 0:
        st.session_state.trial_remaining -= 1
        update_user(st.session_state.user_email, {"trial_remaining": st.session_state.trial_remaining})
        return True
    return False


def premium_prompt():
    if st.session_state.paid:
        if st.session_state.paid_until:
            st.success(f"Premium active until {st.session_state.paid_until}")
        else:
            st.success("Premium access active")
        return
    if st.session_state.trial_remaining > 0:
        st.warning(f"You have {st.session_state.trial_remaining} free premium analyses remaining.")
    else:
        st.error("Free trial exhausted. Upgrade to premium to continue.")


def admin_panel():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin tools")
    if st.button("Refresh user database"):
        load_user_db()
        st.sidebar.success("User database refreshed.")
    users = load_user_db()
    st.sidebar.write(f"Total users: {len(users)}")
    if st.button("Reset all free trials"):
        for email, user in users.items():
            user["trial_remaining"] = TRIAL_ANALYSES
            users[email] = user
        save_user_db(users)
        st.sidebar.success("All trial counts reset.")


def detect_anomalies_iqr(data, column, multiplier=1.5):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    return (data[column] < lower_bound) | (data[column] > upper_bound)


def detect_anomalies_zscore(data, column, threshold=2.5):
    return np.abs(stats.zscore(data[column].dropna())) > threshold


def find_anomalies(df):
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        return pd.DataFrame()

    anomaly_scores = pd.DataFrame()
    for col in numeric_cols:
        anomaly_scores[col] = detect_anomalies_iqr(df, col).astype(int)

    df['AnomalyScore'] = anomaly_scores.sum(axis=1)
    return df[df['AnomalyScore'] > 0].sort_values('AnomalyScore', ascending=False)


def generate_insights(df):
    insights = []
    numeric_cols = get_numeric_columns(df)

    if is_football_dataset(df):
        recent_avg_goals = df.tail(50)['TotalGoals'].mean()
        historical_avg_goals = df.head(50)['TotalGoals'].mean() if len(df) > 50 else df['TotalGoals'].mean()
        if recent_avg_goals > historical_avg_goals * 1.15:
            insights.append({
                'type': '⬆️ TREND',
                'title': 'Increased Scoring Trend',
                'description': f'Recent matches show {recent_avg_goals:.2f} avg goals vs historical {historical_avg_goals:.2f}.',
                'recommendation': 'Monitor defense and incorporate trend-aware modeling.'
            })

        home_eff = df['HomeEfficiency'].mean()
        away_eff = df['AwayEfficiency'].mean()
        if home_eff > away_eff * 1.25:
            insights.append({
                'type': '🎯 EFFICIENCY',
                'title': 'Home Conversion Advantage',
                'description': f'Home conversion is {home_eff:.1%} vs away {away_eff:.1%}.',
                'recommendation': 'Capture game-location signal in predictive models.'
            })
    else:
        if numeric_cols:
            mean_counts = df[numeric_cols].mean().sort_values(ascending=False).head(3)
            insights.append({
                'type': '📊 GENERAL TREND',
                'title': 'Top Numeric Drivers',
                'description': f'Top metrics by average value: {", ".join(mean_counts.index.astype(str))}.',
                'recommendation': 'Validate these features and use them for exploratory modeling.'
            })

            if df[numeric_cols].std().mean() > df[numeric_cols].mean().mean() * 0.8:
                insights.append({
                    'type': '⚠️ VOLATILITY',
                    'title': 'High Feature Variability',
                    'description': 'The dataset shows strong variability across numeric features.',
                    'recommendation': 'Use robust scaling and ensemble models for analysis.'
                })

    return insights


def identify_problems(df):
    problems = []
    missing_data = df.isnull().sum().sum()
    if missing_data > 0:
        problems.append({
            'category': 'Data Quality',
            'severity': 'High',
            'problem': f'Missing data detected ({missing_data} values)',
            'impact': 'Skewed analysis and unreliable insights',
            'solution': 'Implement data validation and automated imputation.'
        })

    numeric_cols = get_numeric_columns(df)
    if numeric_cols:
        outlier_pct = np.mean([detect_anomalies_iqr(df, col).sum() / len(df) for col in numeric_cols]) * 100
        if outlier_pct > 15:
            problems.append({
                'category': 'Statistical Analysis',
                'severity': 'Medium',
                'problem': f'High outlier presence ({outlier_pct:.1f}%) across numeric features',
                'impact': 'Misleading mean-based analytics',
                'solution': 'Use median, IQR and robust scaling.'
            })

    if len(df) < 50:
        problems.append({
            'category': 'Statistical Power',
            'severity': 'Medium',
            'problem': 'Small dataset size',
            'impact': 'Reduced model reliability',
            'solution': 'Collect more observations or use regularized methods.'
        })

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().abs()
        strong_corr = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack()
        max_corr = strong_corr.max() if not strong_corr.empty else 0
        if max_corr < 0.3:
            problems.append({
                'category': 'Feature Correlation',
                'severity': 'High',
                'problem': 'Weak correlation among numeric features.',
                'impact': 'Potentially unreliable predictive features.',
                'solution': 'Engineer domain-specific features or add external signals.'
            })

    if is_football_dataset(df):
        team_matches = df.groupby('HomeTeam').size().min()
        if team_matches < 10:
            problems.append({
                'category': 'Sampling',
                'severity': 'Medium',
                'problem': f'Insufficient matches for some teams ({team_matches} min).',
                'impact': 'Team-level signals are noisy.',
                'solution': 'Aggregate across seasons or use hierarchical models.'
            })

    return problems


def generate_solutions(df):
    solutions = []
    numeric_cols = get_numeric_columns(df)

    if is_football_dataset(df):
        low_eff_teams = []
        for team in df['HomeTeam'].unique():
            team_data = df[df['HomeTeam'] == team]
            if len(team_data) > 5:
                efficiency = team_data['HomeEfficiency'].mean()
                if efficiency < 0.3:
                    low_eff_teams.append((team, efficiency))
        if low_eff_teams:
            solutions.append({
                'area': 'Domain Performance',
                'issue': 'Low shot conversion efficiency',
                'affected': [team for team, _ in low_eff_teams[:3]],
                'solutions': [
                    'Improve shot selection and quality.',
                    'Use biomechanics-based finishing drills.',
                    'Analyze attacker movement patterns.'
                ]
            })

    else:
        if numeric_cols:
            low_var_cols = df[numeric_cols].std().sort_values().head(3).index.tolist()
            solutions.append({
                'area': 'Feature Engineering',
                'issue': 'Low signal features detected',
                'affected': low_var_cols,
                'solutions': [
                    'Create derived, domain-specific features.',
                    'Use normalization to align scales.',
                    'Remove redundant variables before modeling.'
                ]
            })

        if df.isnull().sum().sum() > 0:
            solutions.append({
                'area': 'Data Quality',
                'issue': 'Missing scientific measurements',
                'affected': ['All incomplete records'],
                'solutions': [
                    'Implement robust imputation strategies.',
                    'Validate experimental recording processes.',
                    'Flag and exclude unreliable samples.'
                ]
            })

    return solutions


@st.cache_data
def prepare_prediction_data(df):
    features = df.copy()
    categorical_cols = has_categorical_columns(features)
    encoders = {}
    for col in categorical_cols:
        try:
            codes, uniques = pd.factorize(features[col].astype(str), sort=True)
            features[col] = codes
            encoders[col] = list(uniques)
        except Exception:
            pass
    return features, encoders


def is_discrete_classification_target(y, max_unique=20):
    y_clean = y.dropna()
    if y_clean.empty:
        return False

    unique_count = y_clean.nunique()
    if unique_count < 2:
        return False

    if y_clean.dtype.kind in 'iub':
        return unique_count <= max_unique

    if y_clean.dtype.kind == 'f':
        integer_like = np.all(np.mod(y_clean, 1) == 0)
        return integer_like and unique_count <= max_unique

    return unique_count <= max_unique


@st.cache_data(show_spinner=False)
def train_generic_model(df, target, model_type='regression'):
    features, encoders = prepare_prediction_data(df)
    numeric_cols = get_numeric_columns(features)
    if target not in numeric_cols and target not in features.columns:
        return None

    X = features[numeric_cols].drop(columns=[target], errors='ignore')
    y = features[target]

    valid_mask = X.notnull().all(axis=1) & y.notnull()
    X = X.loc[valid_mask]
    y = y.loc[valid_mask]

    if X.empty or len(y) < 10:
        return None

    stratify = y if model_type == 'classification' and is_discrete_classification_target(y) else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    if model_type == 'classification':
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        score = accuracy_score(y_test, model.predict(X_test))
        return model, score, X_test, y_test

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    score = np.sqrt(mean_squared_error(y_test, preds))
    return model, score, X_test, y_test


uploaded_file = st.sidebar.file_uploader("Upload a dataset (CSV)", type=["csv"])
df = load_data(uploaded_file)
if is_football_dataset(df):
    df = prepare_football_data(df)

ensure_user_session()
user = load_session_user()
params = st.query_params
if user and params.get("payment", [None])[0] == "success":
    session_id = params.get("session_id", [None])[0]
    if session_id and stripe:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            if checkout_session.payment_status == "paid":
                mark_user_paid(user["email"])
        except Exception:
            mark_user_paid(user["email"])
    else:
        mark_user_paid(user["email"])
    user = load_session_user()
    st.rerun()
elif user and params.get("payment", [None])[0] == "cancel":
    st.sidebar.warning("Payment was canceled. You can try again or use the free trial.")

st.sidebar.title("BioVista Account")
with st.sidebar.form("login_form"):
    email_input = st.text_input("Email", value=st.session_state.user_email)
    admin_token_input = st.text_input("Admin token (optional)", type="password")
    login_clicked = st.form_submit_button("Sign in")

if login_clicked:
    if email_input:
        user = sign_in_user(email_input, admin_token_input)
        st.sidebar.success(f"Signed in as {user['email']}")
        if user['is_admin']:
            st.sidebar.info("Admin access granted")
    else:
        st.sidebar.error("Enter an email to sign in.")

if user:
    st.sidebar.markdown(f"**Signed in as:** {user['email']}")
    status_label = 'Admin' if user.get('is_admin') else 'Premium' if user_is_paid(user) else 'Trial'
    st.sidebar.markdown(f"**Status:** {status_label}")
    st.sidebar.markdown(f"**Trial remaining:** {user.get('trial_remaining', 0)}")
    if user_is_paid(user):
        expiration = format_paid_until(user)
        if expiration:
            st.sidebar.markdown(f"**Subscription expires:** {expiration}")
else:
    st.sidebar.info("Sign in to track trial usage and premium access.")

with st.sidebar.expander("Premium access", expanded=True):
    if user and user_is_paid(user):
        expiration = format_paid_until(user)
        if expiration:
            st.success(f"Premium access active until {expiration}.")
        else:
            st.success("Premium access is active.")
        st.write("Enjoy unlimited premium analytics, faster model training, and full prediction access.")
    else:
        st.write("Premium unlocks advanced predictive analytics, premium model training, and priority insights.")
        if STRIPE_SECRET_KEY and stripe:
            if user:
                checkout_url = create_stripe_checkout(user['email'])
                if checkout_url:
                    st.markdown("[Upgrade to Premium — $49.99 / 30 days](" + checkout_url + ")")
                else:
                    st.warning("Stripe payment setup is available but could not create a checkout session.")
            else:
                st.info("Sign in above to unlock premium access and purchase a plan.")
        else:
            st.info("Stripe is not configured yet. Use the button below to unlock premium for demo purposes.")
            if user and st.button("Unlock premium for demo"):
                mark_user_paid(user['email'])
                user = load_session_user()
                st.rerun()
            elif not user:
                st.info("Sign in first to use the demo unlock button.")

st.sidebar.markdown("---")
st.sidebar.title("BioVista Workflow")
user_goal = st.sidebar.selectbox(
    "What is your primary goal?",
    [
        "Explore data and understand quality",
        "Clean data and fix missing values",
        "Detect anomalies",
        "Build predictive models",
        "Compare groups or cohorts"
    ]
)
priority = st.sidebar.radio(
    "What should BioVista focus on?",
    [
        "Data quality review",
        "Feature signal and scaling",
        "Anomaly detection",
        "Predictive modeling",
        "General exploration"
    ]
)

with st.sidebar.expander("Data preparation options", expanded=True):
    impute_missing = st.checkbox("Enable missing value imputation", value=False)
    imputation_method = st.selectbox(
        "Imputation strategy",
        ["median", "mean", "mode", "zero"],
        index=0
    )
    scaling_method = st.selectbox(
        "Feature scaling",
        ["none", "robust", "standard", "minmax"],
        index=0
    )

if priority == "Data quality review":
    default_mode = "🔧 Problems & Solutions"
elif priority == "Feature signal and scaling":
    default_mode = "💡 Insights"
elif priority == "Anomaly detection":
    default_mode = "🔍 Anomalies"
elif priority == "Predictive modeling":
    default_mode = "🔮 Predictive Analytics"
else:
    default_mode = "📊 Overview"

if user and user.get('is_admin'):
    admin_panel()

analysis_modes = ["📊 Overview", "🔍 Anomalies", "💡 Insights", "🔧 Problems & Solutions", "🔮 Predictive Analytics", "📈 Group Analysis", "📉 Detailed Stats"]
default_index = analysis_modes.index(default_mode) if default_mode in analysis_modes else 0
analysis_mode = st.sidebar.radio(
    "Select Analysis Mode",
    analysis_modes,
    index=default_index
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset type:** " + ("Football sample" if is_football_dataset(df) else "General data"))

if impute_missing or scaling_method != "none":
    df = preprocess_dataset(df, impute=impute_missing, strategy=imputation_method, scaling=scaling_method)

st.markdown(
    """
    <div style='display:flex;align-items:flex-start;gap:1rem;margin-bottom:1.25rem;'>
      <div style='width:56px;height:56px;border-radius:18px;background:linear-gradient(135deg,#7c3aed,#a78bfa);display:flex;align-items:center;justify-content:center;box-shadow:0 16px 36px rgba(124,58,237,0.28);'>
        <span style='color:#e8e8e8;font-family:DM Mono,monospace;font-weight:800;font-size:1.3rem;'>B</span>
      </div>
      <div>
        <div style='font-size:0.8rem;letter-spacing:0.22em;text-transform:uppercase;color:#7c3aed;font-weight:700;font-family:DM Mono,monospace;margin-bottom:0.35rem;'>BioVista Analytics</div>
        <div style='font-size:2.4rem;font-weight:800;line-height:1.05;color:#e8e8e8;margin:0;'>Data · Biology · Intelligence</div>
        <div style='margin-top:0.75rem;font-size:1rem;color:#c4c4c4;max-width:740px;'>BioVista bridges biochemistry research and business intelligence with elegant analytics and actionable insight.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    [role="button"], [role="listbox"], [role="option"], .stRadio label, .stSelectbox div, .css-1x0uki3 { cursor: pointer !important; }
    </style>
    """,
    unsafe_allow_html=True
)
if impute_missing or scaling_method != "none":
    st.info(f"Preprocessing applied: imputation={imputation_method if impute_missing else 'disabled'}, scaling={scaling_method}")

if analysis_mode == "📊 Overview":
    st.header("Dataset Overview")
    numeric_cols = get_numeric_columns(df)
    categorical_cols = has_categorical_columns(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Records", len(df))
    with col2:
        st.metric("Numeric Features", len(numeric_cols))
    with col3:
        st.metric("Categorical Features", len(categorical_cols))
    with col4:
        st.metric("Missing Values", int(df.isnull().sum().sum()))

    st.markdown("---")
    if is_football_dataset(df):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Goals Distribution")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.histplot(data=df, x='TotalGoals', bins=15, kde=True, ax=ax, color='steelblue')
            ax.set_xlabel('Total Goals')
            ax.set_ylabel('Frequency')
            st.pyplot(fig)
        with col2:
            st.subheader("Result Distribution")
            result_counts = df['FullTimeResult'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = ['#2ecc71', '#e74c3c', '#95a5a6']
            result_counts.plot(kind='bar', ax=ax, color=colors)
            ax.set_title('Match Results')
            ax.set_xlabel('Result')
            ax.set_ylabel('Count')
            plt.xticks(rotation=0)
            st.pyplot(fig)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Attack vs Defense")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(['Home Attack', 'Away Attack'], [df['HomeAttackRating'].mean(), df['AwayAttackRating'].mean()], color=['#3498db', '#e67e22'])
            ax.set_ylabel('Average Rating')
            st.pyplot(fig)
        with col2:
            st.subheader("Efficiency")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(['Home Efficiency', 'Away Efficiency'], [df['HomeEfficiency'].mean(), df['AwayEfficiency'].mean()], color=['#1abc9c', '#9b59b6'])
            ax.set_ylabel('Conversion Rate')
            st.pyplot(fig)
    else:
        if numeric_cols:
            st.subheader("Numeric Feature Summary")
            st.dataframe(df[numeric_cols].describe().T, use_container_width=True)
            st.markdown("---")
            top_cols = df[numeric_cols].mean().sort_values(ascending=False).head(4).index.tolist()
            fig, ax = plt.subplots(figsize=(10, 5))
            df[top_cols].plot(kind='line', ax=ax)
            ax.set_title('Top Numeric Feature Trends')
            ax.set_xlabel('Index')
            st.pyplot(fig)
        if categorical_cols:
            st.subheader("Categorical Overview")
            for col in categorical_cols[:3]:
                st.write(f"**{col}**")
                st.bar_chart(df[col].value_counts())

elif analysis_mode == "🔍 Anomalies":
    st.header("🔍 Anomaly Detection")
    anomalies = find_anomalies(df)
    st.metric("Anomalous Records", len(anomalies))
    st.markdown("---")
    if anomalies.empty:
        st.info("No numeric anomalies detected in this dataset.")
    else:
        sample_cols = get_numeric_columns(df)[:6]
        st.dataframe(anomalies[[*sample_cols, 'AnomalyScore']].head(20), use_container_width=True)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(data=anomalies, x='AnomalyScore', bins=10, kde=True, ax=ax, color='#e74c3c')
        ax.set_xlabel('Anomaly Score')
        ax.set_ylabel('Count')
        st.pyplot(fig)

elif analysis_mode == "💡 Insights":
    st.header("💡 Intelligent Insights")
    insights = generate_insights(df)
    if insights:
        for insight in insights:
            with st.container():
                st.markdown(f"### {insight['type']} - {insight['title']}")
                st.markdown(f"**Analysis:** {insight['description']}")
                st.markdown(f"**Recommendation:** {insight['recommendation']}")
                st.markdown("---")
    else:
        st.info("No strong insight patterns detected for this dataset.")

elif analysis_mode == "🔧 Problems & Solutions":
    st.header("🔧 Problems & Solutions")
    st.markdown("*Identify data and modeling issues, then apply targeted solutions.*")
    problems = identify_problems(df)
    solutions = generate_solutions(df)

    if problems:
        st.subheader("🚨 Problems Identified")
        for problem in problems:
            with st.expander(f"{problem['severity']}: {problem['category']}"):
                st.markdown(f"**Issue:** {problem['problem']}")
                st.markdown(f"**Impact:** {problem['impact']}")
                st.markdown(f"**Solution:** {problem['solution']}")

    if solutions:
        st.subheader("💡 Recommended Actions")
        for sol in solutions:
            with st.expander(f"{sol['area']}: {sol['issue']}"):
                st.markdown(f"**Affected:** {', '.join(sol.get('affected', []))}")
                st.markdown("**Recommendations:**")
                for idx, action in enumerate(sol['solutions'], 1):
                    st.markdown(f"{idx}. {action}")

elif analysis_mode == "🔮 Predictive Analytics":
    st.header("🔮 Predictive Analytics")
    st.markdown("*Build models using your dataset to predict scientific or business targets.*")
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        st.info("No numeric features available for predictive modeling.")
    else:
        premium_prompt()
        if not can_use_premium_feature():
            st.stop()

        if len(df) > 10000:
            st.info("Large dataset detected; model training will use parallel CPU cores and cached preprocessing for faster execution.")

        target = st.selectbox("Select target variable", numeric_cols)
        model_type = st.radio("Model type", ['regression', 'classification'])
        can_train = True
        if model_type == 'classification' and not is_discrete_classification_target(df[target]):
            st.warning(
                "The selected target appears continuous or has too many classes for classification. "
                "Switch to regression or choose a discrete/categorical target."
            )
            can_train = False

        if can_train and st.button("Train Model"):
            if not consume_premium_allowance():
                st.error("Your free premium trial has been used up. Please upgrade to continue.")
            else:
                with st.spinner("Training model..."):
                    result = train_generic_model(df, target, model_type=model_type)
                if result is None:
                    st.error("Not enough valid data to train a reliable model.")
                else:
                    model, score, X_test, y_test = result
                    if model_type == 'classification':
                        st.success(f"Accuracy: {score:.2%}")
                    else:
                        st.success(f"RMSE: {score:.2f}")
                    st.markdown("**Feature importance (top 10)**")
                    importances = pd.Series(model.feature_importances_, index=X_test.columns).sort_values(ascending=False).head(10)
                    st.bar_chart(importances)

elif analysis_mode == "📈 Group Analysis":
    st.header("📈 Group Analysis")
    if is_football_dataset(df):
        all_teams = sorted(set(df['HomeTeam'].unique()) | set(df['AwayTeam'].unique()))
        selected = st.multiselect("Select teams", all_teams, default=all_teams[:3])
        if selected:
            team_stats = []
            for team in selected:
                home = df[df['HomeTeam'] == team]
                away = df[df['AwayTeam'] == team]
                matches = len(home) + len(away)
                goals_for = home['FullTimeHomeGoals'].sum() + away['FullTimeAwayGoals'].sum()
                goals_against = home['FullTimeAwayGoals'].sum() + away['FullTimeHomeGoals'].sum()
                wins = (home['FullTimeResult'] == 'H').sum() + (away['FullTimeResult'] == 'A').sum()
                team_stats.append({
                    'Team': team,
                    'Matches': matches,
                    'Wins': wins,
                    'Win %': (wins / matches * 100) if matches else 0,
                    'Goal Diff': goals_for - goals_against,
                    'Avg Goals/Match': (goals_for / matches) if matches else 0
                })
            st.dataframe(pd.DataFrame(team_stats).sort_values('Win %', ascending=False), use_container_width=True)
    else:
        categorical_cols = has_categorical_columns(df)
        if not categorical_cols:
            st.info("No categorical columns available for group analysis.")
        else:
            group_col = st.selectbox("Group by", categorical_cols)
            agg_cols = get_numeric_columns(df)
            if agg_cols:
                grouped = df.groupby(group_col)[agg_cols].mean().sort_values(agg_cols[0], ascending=False)
                st.dataframe(grouped, use_container_width=True)

elif analysis_mode == "📉 Detailed Stats":
    st.header("📉 Detailed Statistical Analysis")
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        st.info("No numeric columns available for detailed statistics.")
    else:
        metric_choice = st.selectbox("Select metric", numeric_cols)
        st.metric("Mean", f"{df[metric_choice].mean():.2f}")
        st.metric("Median", f"{df[metric_choice].median():.2f}")
        st.metric("Std Dev", f"{df[metric_choice].std():.2f}")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{metric_choice} Distribution")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.histplot(data=df, x=metric_choice, bins=20, kde=True, ax=ax, color='steelblue')
            ax.axvline(df[metric_choice].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
            ax.axvline(df[metric_choice].median(), color='green', linestyle='--', linewidth=2, label='Median')
            ax.legend()
            st.pyplot(fig)
        with col2:
            st.subheader("Box Plot")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(data=df, y=metric_choice, ax=ax, color='steelblue')
            st.pyplot(fig)
        st.markdown("---")
        if len(numeric_cols) > 1:
            st.subheader("Correlation Heatmap")
            corr_matrix = df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax, cbar_kws={'label': 'Correlation'})
            st.pyplot(fig)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    BioVista Scientific Analysis Platform | Powered by Streamlit and Seaborn
    </div>
    """,
    unsafe_allow_html=True
)
