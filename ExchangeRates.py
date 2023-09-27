import pandas as pd
import networkx as nx
import time
import os
from datetime import datetime
import requests

def fetch_exchange_rates(api_key):
    url = f"http://api.exchangeratesapi.io/latest?base=EUR&access_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()['rates']
        except KeyError:
            print("Unexpected response format:", response.json())
            return None
    else:
        print("Failed to fetch data:", response.json())
        return None

def get_profit_path(G, src, dst):
    all_paths = list(nx.all_simple_paths(G, source=src, target=dst))
    best_paths = []
    
    for path in all_paths:
        profit = 1
        for i in range(len(path) - 1):
            profit *= G[path[i]][path[i+1]]['weight']
        best_paths.append((path, profit))
    
    best_paths.sort(key=lambda x: x[1], reverse=True)
    return best_paths[:5]


if __name__ == "__main__":
    start_time = time.time()
    api_key = '6ca4cb52f0c8ec1347f9cc474661b774'

    rates = fetch_exchange_rates(api_key)
    df = pd.DataFrame(list(rates.items()), columns=['Currency', 'Rate'])
    G = nx.DiGraph()

    for index, row in df.iterrows():
        G.add_edge('EUR', row['Currency'], weight=row['Rate'])

    base_currency = input("Enter the base currency: ").upper()
    target_currency = input("Enter the target currency: ").upper()

    top_5_paths = get_profit_path(G, base_currency, target_currency)

    log_str = []
    log_str.append(f"Base currency: {base_currency}, Target currency: {target_currency}\n")

    for i, (path, profit) in enumerate(top_5_paths):
        log_str.append(f"Path {i+1}: {path} - Profit rate: {profit}\n")

    elapsed_time = time.time() - start_time
    log_str.append(f"Execution Time: {elapsed_time} seconds\n")

    print("".join(log_str))

    if not os.path.exists('logs'):
        os.makedirs('logs')

    filename = f"logs/{datetime.now().strftime('%Y%m%d%H%M%S')}_{base_currency}.txt"
    with open(filename, 'w') as f:
        f.write("".join(log_str))

    print(f"Log saved in: {filename}")