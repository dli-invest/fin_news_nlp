"""
  Grab stocks from cad tickers 
"""
import pandas as pd


class TickerControllerV2:
    """
    Grabs cad_tickers dataframes and normalized them
    """

    def __init__(self, cfg: dict):
        """
        Extract yahoo finance tickers from website
        Consider using hardcoded csvs sheets for the tickers to
        increase speed, no need to grab all data dynamically.
        """
        self.yf_tickers = []
        default_url = cfg.get("default_url", "https://raw.githubusercontent.com/FriendlyUser/cad_tickers_list/main/static/latest/stocks.csv")
        # import csv from github
        ticker_df = pd.read_csv(default_url)
        # searchfor = [".WT", ".UN"]
        # ticker_df = ticker_df[~ticker_df.symbol.str.contains('|'.join(searchfor))]
        # purge tickers with .WT
        tickers_config = cfg.get("tickers_config")
        us_df = pd.DataFrame()
        if tickers_config != None:
            industries = tickers_config.get("industries")
            if industries != None:
                ticker_df = ticker_df[ticker_df["industry"].isin(industries)]
            price_filter = tickers_config.get("price", 5E5)
            us_df = us_df[us_df["price"] < price_filter]
            market_cap_filter = tickers_config.get("market_cap", 1E15)
            us_df = us_df[us_df["MarketCap"] < market_cap_filter]
            if industries != None:
                us_df = us_df[us_df["industry"].isin(industries)]

        # get symbols from tickers
        ytickers_series = ticker_df.apply(self.ex_to_yahoo_ex, axis=1)
        ytickers = ytickers_series.tolist()
        if us_df.empty == False:
            us_ytickers_series = us_df.apply(self.ex_to_yahoo_ex, axis=1)
            us_ytickers = us_ytickers_series.tolist()
            ytickers = [*ytickers, *us_ytickers]
        self.yf_tickers = ytickers

    def get_ytickers(self) -> list:
        return self.yf_tickers

    @staticmethod
    def ex_to_yahoo_ex(row: pd.Series) -> str:
        """
        Parameters:
          ticker: ticker from pandas dataframe from cad_tickers
          exchange: what exchange the ticker is for
        Returns:
        """
        ticker = str(row["symbol"])
        exchange = row["exShortName"]
        if exchange == "CSE":
            # strip :CNX from symbol
            ticker = ticker.replace(":CNX", "")
        
        # Missing a exchange code
        if exchange in ["OTCPK", "NYSE", "NASDAQ", "NYE", "NCM", "NSM", "NGS"]:
            ticker = ticker.replace(":US", "")
        ticker = ticker.replace(":US", "")
        # 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        switcher = {"TSXV": "V", "TSX": "TO", "CSE": "CN"}
        yahoo_ex = switcher.get(exchange, None)
        if yahoo_ex != None:
            return f"{ticker}.{yahoo_ex}"
        return ticker