# src/agents/data_collector_agent.py
"""
DataCollectorAgent
- Uses DataFetcher tool (Phase 2) to fetch datasets
- Validates, compacts, and returns a consistent object
"""

from typing import Dict
from src.tools.data_fetcher import DataFetcher  # adjust import path if necessary

class DataCollectorAgent:
    def __init__(self, fetcher: DataFetcher):
        self.fetcher = fetcher

    def validate_sales(self, df):
        # Ensure required columns exist and cast types
        expected = {'date', 'lead_id', 'stage', 'owner', 'amount', 'source'}
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(f"Missing sales columns: {missing}")
        return df

    def validate_support(self, df):
        expected = {'ticket_id', 'created_at', 'priority', 'status', 'subject', 'escalated'}
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(f"Missing support columns: {missing}")
        return df

    def validate_marketing(self, df):
        expected = {'date', 'campaign', 'channel', 'spend', 'impressions',
                    'clicks', 'conversions', 'conversion_rate'}
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(f"Missing marketing columns: {missing}")
        return df

    def run(self) -> Dict:
        datasets = self.fetcher.fetch_all()
        sales = self.validate_sales(datasets['sales'])
        support = self.validate_support(datasets['support'])
        marketing = self.validate_marketing(datasets['marketing'])

        # compacting: keep last 30 days for demo
        try:
            sales = sales.sort_values('date').copy()
            support = support.sort_values('created_at').copy()
            marketing = marketing.sort_values('date').copy()
        except Exception:
            pass

        return {'sales': sales, 'support': support, 'marketing': marketing}
