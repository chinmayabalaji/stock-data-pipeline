import os
import json
import finnhub
from prefect import flow, task
from datetime import datetime

finnhub_api = os.getenv('ainnhub_api_key')
finnhub_client = finnhub.Client(api_key=finnhub_api)

@task(name = "get_stock_data", retries = 3, retry_delay_seconds = 10, log_prints = True)
def fetch_stock_data(symbol):

    try:

        print(f"Getting stock data for the symbol: {symbol}")
        quote = finnhub_client.quote(symbol)
        profile = finnhub_client.company_profile2(symbol)
        fundamentals = finnhub_client.company_basic_financials(symbol,'all')

        data = {
            "name" : profile.get('name'),
            "exchnage" : profile.get("exchange"),
            "sector" : profile.get("finnhubIndustry"),
            "ipo" : profile.get("ipo"),
            "symbol" : symbol,
            "current price" : quote.get('c'),
            "open price" : quote.get('o'),
            "high price" : quote.get('h'),
            "low price" : quote.get('l'),
            "previous_close" : quote.get('pc'),
            "volume" : quote.get('v'),
            "pe_ratio" : fundamentals.get("metric", {}).get("peNormalizedAnnual"),
            "eps" : fundamentals.get("metric", {}).get("epsTTM"),
            "market_cap" : fundamentals.get("metric", {}).get("marketCapitalization"),
            "dividend_yield" : fundamentals.get("metric",{}).get("dividendYieldIndicatedAnnual"),
            "date_time" : datetime.now().strftime("%Y-%m-%dt%H:%M:%S")
        }

        print(data)

    except Exception as e:
        print(f"{e}")
        raise 

@task(name = 'get_stocks_symbols', retries = 3, retry_delay_seconds = 10, log_prints = True)
def get_stocks_symbols(config_file):

    print("Getting stocks data for the Doe Jones Stocks")
    with open(config_file) as f:
        symbols = json.load(f)

    return symbols['symbols']


@flow(
    name = "extraction_flow"
)
def data_extraction():

    config_file = r'config/dow_jones_stocks_data.json'

    symbols = get_stocks_symbols(config_file)
    
    fetch_stock_data.map(symbols)

if __name__ == "__main__":
    data_extraction()