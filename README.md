
📌 Overview
Real-Time Stock Price Prediction System is an AI/ML-powered application that fetches live stock market data and predicts future stock prices using advanced machine learning and deep learning models such as LSTM, GRU, XGBoost, and Linear Regression. 
The system provides real-time visualization, technical indicators, and buy/sell signals to assist traders and investors in making data-driven decisions.

The goal of this project is to democratize financial intelligence by combining live market feeds with predictive analytics — helping users understand market trends and make informed decisions.

🎯 Features
📡 Real-Time Data Fetching — Live stock prices via Yahoo Finance / Alpha Vantage / NSE APIs

🤖 Multiple ML/DL Models — LSTM, GRU, XGBoost, Random Forest, Linear Regression, ARIMA

📊 Interactive Charts — Candlestick charts, moving averages, RSI, MACD, Bollinger Bands

🔮 Next-Day / Multi-Day Prediction — Forecast closing prices for upcoming days

📈 Technical Indicators — SMA, EMA, RSI, MACD, Bollinger Bands

🖥️ Web Dashboard — Streamlit-based interactive UI

⚡ Auto-Refresh — Real-time updates at configurable intervals

📁 Historical Data Support — Backtesting on past data

💾 Model Persistence — Save/load trained models using Joblib/Pickle

🏗️ Tech Stack
Category	Tools/Libraries
Language	Python 3.8+
Data Source	yfinance, Alpha Vantage API, NSEpy
ML/DL	Scikit-learn, XGBoost, TensorFlow/Keras, Statsmodels
Data Handling	Pandas, NumPy
Visualization	Matplotlib, Plotly, Seaborn
Web Framework	Streamlit
Technical Analysis	TA-Lib, pandas-ta
Others	Joblib, Pickle, Requests

📂 Project Structure
real-time-stock-prediction/
│
├── data/
│   ├── raw/                     # Raw downloaded stock data
│   └── processed/               # Cleaned & feature-engineered data
│
├── models/
│   ├── trained_models/          # Saved .pkl / .h5 / .keras models
│   └── model_training.py        # Training scripts
│
├── notebooks/
│   └── EDA_and_Modeling.ipynb
│
├── src/
│   ├── data_fetcher.py          # Real-time & historical data fetching
│   ├── preprocess.py            # Cleaning, scaling, feature engineering
│   ├── indicators.py            # Technical indicators (RSI, MACD, etc.)
│   ├── predict.py               # Prediction logic
│   └── utils.py
│
├── app/
│   └── app.py                   # Streamlit dashboard
│
├── requirements.txt
├── config.py                    # API keys & config
├── README.md
└── main.py
⚙️ Installation
Clone the repository


git clone https://github.com/vnvikas/real-time-stock-prediction.git
cd real-time-stock-prediction
Create virtual environment

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
Install dependencies

pip install -r requirements.txt
Configure API keys (in config.py)

python
ALPHA_VANTAGE_API_KEY = "your_api_key_here"
🚀 Usage
Fetch Live Data

python src/data_fetcher.py --ticker AAPL
Train Model

python models/model_training.py --ticker AAPL --model lstm
Run Web Dashboard

streamlit run app/app.py
CLI Prediction

python main.py --ticker AAPL --days 7

📊 Model Performance
Stock	Model	RMSE	MAE	MAPE	R² Score
AAPL	LSTM	2.14	1.68	1.85%	0.96
GOOGL	GRU	3.42	2.71	2.03%	0.94
TSLA	XGBoost	5.87	4.32	2.91%	0.91
MSFT	Linear Regression	4.11	3.25	1.97%	0.93
RELIANCE.NS	LSTM	12.35	9.44	1.72%	0.95
⚠️ These metrics are based on historical backtesting. Real-world predictions may vary due to market volatility.

📁 Data Sources
Yahoo Finance — via yfinance library

Alpha Vantage — Free API for real-time quotes

NSE India — via nsepy / yfinance (for Indian stocks)

Kaggle Datasets — Historical OHLCV data

