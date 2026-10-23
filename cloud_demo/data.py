"""固定种子合成样本；不读取本地文件、快照或任何外部数据。"""
import numpy as np
import pandas as pd

DEMO_LABEL='演示数据，不是真实账户'
DEMO_AS_OF='2025-09-10（合成场景日期，不是最新行情）'
STOCKS=(('AAPL',15,180,190),('NVDA',20,100,110),('MSFT',5,350,380),
        ('AMD',10,130,140),('MU',12,75,80),('ORCL',8,120,130))
CRYPTO=(('BTC',.08,50000,60000),('ETH',1.5,2500,3000),('BNB',4,400,500))


def demo_bars(symbol,periods=180):
    symbols=[r[0] for r in STOCKS]
    if symbol not in symbols or not isinstance(periods,int) or not 30<=periods<=260:
        raise ValueError('仅支持内置演示股票及30—260条合成日线。')
    index=symbols.index(symbol)
    rng=np.random.default_rng(2200+index)
    target=STOCKS[index][3]
    close=np.exp(np.cumsum(rng.normal(.001,.018,periods)))
    close=close/close[-1]*target
    opened=np.r_[close[0],close[:-1]]*np.exp(rng.normal(0,.004,periods))
    return pd.DataFrame({'date':pd.bdate_range(end='2025-09-10',periods=periods),
                         'open':opened.round(2),'high':(np.maximum(opened,close)*(1+rng.uniform(.002,.015,periods))).round(2),
                         'low':(np.minimum(opened,close)*(1-rng.uniform(.002,.015,periods))).round(2),
                         'close':close.round(2),'volume':rng.integers(5_000_000,40_000_000,periods)})


def demo_holdings():
    rows=[]
    for category,currency,source in [('美股','USD',STOCKS),('数字资产','USDT',CRYPTO)]:
        for symbol,qty,cost,price in source:
            rows.append(dict(symbol=symbol,category=category,currency=currency,quantity=qty,cost_price=cost,
                             price=price,cost_value=qty*cost,market_value=qty*price,unrealized=qty*(price-cost)))
    return pd.DataFrame(rows)
