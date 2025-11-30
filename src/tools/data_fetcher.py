import pandas as pd

class DataFetcher:
    def __init__(self, sales_path, support_path, marketing_path):
        self.sales_path = sales_path
        self.support_path = support_path
        self.marketing_path = marketing_path

    def fetch_sales(self):
        df = pd.read_csv(self.sales_path)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def fetch_support(self):
        df = pd.read_csv(self.support_path)
        df['created_at'] = pd.to_datetime(df['created_at'])
        # Ensure timestamps are timezone-naive to match injected data
        if df['created_at'].dt.tz is not None:
            df['created_at'] = df['created_at'].dt.tz_localize(None)
        
        # Inject anomaly for demo purposes
        import os
        if os.getenv("DEMO_MODE", "false").lower() == "true":
             # Add 100 dummy tickets for today to trigger anomaly
             new_rows = pd.DataFrame({
                 'ticket_id': [f'mock-{i}' for i in range(100)],
                 'customer_id': ['mock-cust']*100,
                 'issue_type': ['login_failure']*100,
                 'priority': ['High']*100,
                 'status': ['New']*100,
                 'created_at': [pd.Timestamp.now().replace(tzinfo=None)] * 100,
                 'resolved_at': [None]*100
             })
             df = pd.concat([df, new_rows], ignore_index=True)
        
        return df

    def fetch_marketing(self):
        df = pd.read_csv(self.marketing_path)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def fetch_all(self):
        return {
            "sales": self.fetch_sales(),
            "support": self.fetch_support(),
            "marketing": self.fetch_marketing()
        }
