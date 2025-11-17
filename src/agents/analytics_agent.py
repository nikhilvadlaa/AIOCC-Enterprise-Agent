import pandas as pd
import numpy as np
from scipy.stats import zscore

class AnalyticsAgent:
    def __init__(self, lookback_days=14):
        self.lookback_days = lookback_days

    def _z_anomaly(self, series):
        if len(series) < 5:
            return False, 0
        z = zscore(series)
        latest = z[-1]
        return abs(latest) > 2.5, latest  # anomaly if z > 2.5

    def _sales_conversion_change(self, df):
        df['date'] = pd.to_datetime(df['date'])
        conv = df.groupby(df['date'].dt.date).apply(lambda g: (g['stage']=='SQL').sum()/max(1,len(g)))

        anomaly, z_val = self._z_anomaly(conv)
        percent_change = (conv.iloc[-1] - conv.mean()) / (conv.mean() + 1e-9)

        return {
            "latest_rate": float(conv.iloc[-1]),
            "avg_rate": float(conv.mean()),
            "pct_change": float(percent_change),
            "z_score": float(z_val),
            "anomaly": anomaly
        }

    def _marketing_conversion_change(self, df):
        df['date'] = pd.to_datetime(df['date'])
        conv = df.groupby(df['date'].dt.date)['conversion_rate'].mean()

        anomaly, z_val = self._z_anomaly(conv)
        percent_change = (conv.iloc[-1] - conv.mean()) / (conv.mean() + 1e-9)

        return {
            "latest_rate": float(conv.iloc[-1]),
            "avg_rate": float(conv.mean()),
            "pct_change": float(percent_change),
            "z_score": float(z_val),
            "anomaly": anomaly
        }

    def _support_spike(self, df):
        df['created_at'] = pd.to_datetime(df['created_at'])
        daily = df.groupby(df['created_at'].dt.date).size()

        anomaly, z_val = self._z_anomaly(daily)
        change = (daily.iloc[-1] - daily.mean()) / (daily.mean() + 1e-9)

        return {
            "latest_count": int(daily.iloc[-1]),
            "avg_count": float(daily.mean()),
            "pct_change": float(change),
            "z_score": float(z_val),
            "anomaly": anomaly
        }

    def analyze(self, datasets):
        s = self._sales_conversion_change(datasets['sales'])
        m = self._marketing_conversion_change(datasets['marketing'])
        sp = self._support_spike(datasets['support'])

        summary_parts = []
        if s["anomaly"]: summary_parts.append("Sales anomaly detected")
        if m["anomaly"]: summary_parts.append("Marketing anomaly detected")
        if sp["anomaly"]: summary_parts.append("Support spike anomaly detected")

        return {
            "sales": s,
            "marketing": m,
            "support": sp,
            "summary": " | ".join(summary_parts) if summary_parts else "No major anomalies"
        }
