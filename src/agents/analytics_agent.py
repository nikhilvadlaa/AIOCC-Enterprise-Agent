import pandas as pd
import numpy as np
from scipy.stats import zscore
from typing import Dict, Any, Tuple

from src.config import Config
from src.utils.logger import logger

class AnalyticsAgent:
    def __init__(self, lookback_days: int = 14):
        self.lookback_days = lookback_days
        logger.info(f"AnalyticsAgent initialized with lookback_days={lookback_days}")

    def _z_anomaly(self, series: pd.Series) -> Tuple[bool, float]:
        if len(series) < 5:
            return False, 0.0
        z = zscore(series)
        latest = z[-1]
        return abs(latest) > 2.5, float(latest)  # anomaly if z > 2.5

    def _sales_conversion_change(self, df: pd.DataFrame) -> Dict[str, Any]:
        df['date'] = pd.to_datetime(df['date'])
        conv = df.groupby(df['date'].dt.date).apply(lambda g: (g['stage']=='SQL').sum()/max(1,len(g)))

        anomaly, z_val = self._z_anomaly(conv)
        percent_change = (conv.iloc[-1] - conv.mean()) / (conv.mean() + 1e-9)

        if anomaly:
            logger.info(f"Sales anomaly detected: z_score={z_val:.2f}")

        return {
            "latest_rate": float(conv.iloc[-1]),
            "avg_rate": float(conv.mean()),
            "pct_change": float(percent_change),
            "z_score": float(z_val),
            "anomaly": anomaly
        }

    def _marketing_conversion_change(self, df: pd.DataFrame) -> Dict[str, Any]:
        df['date'] = pd.to_datetime(df['date'])
        conv = df.groupby(df['date'].dt.date)['conversion_rate'].mean()

        anomaly, z_val = self._z_anomaly(conv)
        percent_change = (conv.iloc[-1] - conv.mean()) / (conv.mean() + 1e-9)

        if anomaly:
            logger.info(f"Marketing anomaly detected: z_score={z_val:.2f}")

        return {
            "latest_rate": float(conv.iloc[-1]),
            "avg_rate": float(conv.mean()),
            "pct_change": float(percent_change),
            "z_score": float(z_val),
            "anomaly": anomaly
        }

    def _support_spike(self, df: pd.DataFrame) -> Dict[str, Any]:
        df['created_at'] = pd.to_datetime(df['created_at'])
        daily = df.groupby(df['created_at'].dt.date).size()

        anomaly, z_val = self._z_anomaly(daily)
        change = (daily.iloc[-1] - daily.mean()) / (daily.mean() + 1e-9)

        # Force anomaly for demo
        if Config.DEMO_MODE:
            anomaly = True
            z_val = 5.0 # Fake high Z-score
            logger.info("DEMO MODE: Forcing support spike anomaly.")

        if anomaly:
            logger.info(f"Support spike detected: z_score={z_val:.2f}")

        return {
            "latest_count": int(daily.iloc[-1]),
            "avg_count": float(daily.mean()),
            "pct_change": float(change),
            "z_score": float(z_val),
            "anomaly": anomaly
        }

    def analyze(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        logger.info("Starting analysis on datasets...")
        s = self._sales_conversion_change(datasets['sales'])
        m = self._marketing_conversion_change(datasets['marketing'])
        sp = self._support_spike(datasets['support'])

        summary_parts = []
        if s["anomaly"]: summary_parts.append("Sales anomaly detected")
        if m["anomaly"]: summary_parts.append("Marketing anomaly detected")
        if sp["anomaly"]: summary_parts.append("Support spike anomaly detected")

        summary = " | ".join(summary_parts) if summary_parts else "No major anomalies"
        logger.info(f"Analysis complete. Summary: {summary}")

        return {
            "sales": s,
            "marketing": m,
            "support": sp,
            "summary": summary
        }
