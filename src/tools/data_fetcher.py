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
