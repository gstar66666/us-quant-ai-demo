"""仅离线演示的指标、风险场景与回测。计算不产生任何真实订单。"""
import math
import numpy as np
import pandas as pd


def indicators(bars):
    required={'date','open','high','low','close','volume'}
    if not isinstance(bars,pd.DataFrame) or not required.issubset(bars.columns) or bars.empty:
        raise ValueError('日线格式或记录无效。')
    d=bars.copy().reset_index(drop=True)
    try:
        d[['open','high','low','close','volume']]=d[['open','high','low','close','volume']].astype(float)
        values=d[['open','high','low','close','volume']].to_numpy(dtype=float)
    except (ValueError,TypeError):
        raise ValueError('日线数字无法解析。') from None
    if not np.isfinite(values).all() or (values[:,:4]<=0).any() or (values[:,4]<0).any():
        raise ValueError('价格与成交量必须是有限的有效值。')
    if (d.high<d[['open','close','low']].max(axis=1)).any() or (d.low>d[['open','close','high']].min(axis=1)).any():
        raise ValueError('最高/最低价关系无效。')
    d['date']=pd.to_datetime(d.date,errors='coerce')
    if d.date.isna().any() or d.date.duplicated().any() or not d.date.is_monotonic_increasing:
        raise ValueError('日期须有效、唯一并递增。')
    for n in (5,10,20):d[f'MA{n}']=d.close.rolling(n).mean()
    delta=d.close.diff()
    gain=delta.clip(lower=0).rolling(14).mean()
    loss=(-delta.clip(upper=0)).rolling(14).mean()
    d['RSI14']=100-100/(1+gain/loss.replace(0,np.nan))
    d.loc[(loss==0)&(gain>0),'RSI14']=100
    d.loc[(loss==0)&(gain==0),'RSI14']=50
    d['volume_ratio']=d.volume/d.volume.shift().rolling(20).mean().replace(0,np.nan)
    return d


def signal_mask(d,rsi_low=35,rsi_high=75,volume_ratio=.8):
    if not 0<=rsi_low<=rsi_high<=100 or not math.isfinite(volume_ratio) or volume_ratio<=0:
        raise ValueError('RSI区间或量比阈值无效。')
    return ((d.close>d.MA5)&(d.MA5>d.MA10)&(d.MA10>d.MA20)&d.RSI14.between(rsi_low,rsi_high)&(d.volume_ratio>=volume_ratio)).fillna(False)


def risk_scenario(holdings,stock_drop=-.1,crypto_drop=-.2):
    if not all(math.isfinite(v) and -1<=v<=0 for v in (stock_drop,crypto_drop)):
        raise ValueError('压力情景跌幅须在-100%与0之间。')
    d=holdings.copy()
    if d.empty:return {'total':0.,'loss':0.,'max_weight':None,'crypto_weight':None}
    values=d.market_value.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values<0).any():raise ValueError('演示市值无效。')
    total=float(values.sum())
    impacts=d.category.map({'美股':stock_drop,'数字资产':crypto_drop})
    if impacts.isna().any():raise ValueError('不支持的演示资产类别。')
    return {'total':total,'loss':float((d.market_value*impacts).sum()),
            'max_weight':float(values.max()/total) if total else None,
            'crypto_weight':float(d.loc[d.category=='数字资产','market_value'].sum()/total) if total else None}


def backtest(bars,*,capital=100000.,hold_days=3,fraction=.25,fee_bps=5.,slippage_bps=5.,
             rsi_low=35,rsi_high=75,volume_ratio=.8):
    """t日收盘产生信号，最早t+1开盘模拟成交；单仓做多，无杠杆。"""
    if (not all(math.isfinite(v) for v in (capital,fraction,fee_bps,slippage_bps)) or capital<=0 or capital>1e12
        or not 0<fraction<=1 or type(hold_days) is not int or not 2<=hold_days<=5
        or not 0<=fee_bps<=100 or not 0<=slippage_bps<=100):
        raise ValueError('本金、持有天数、仓位或费用参数无效。')
    d=indicators(bars)
    if len(d)<22:raise ValueError('至少需要22条日线以覆盖指标预热及次日成交。')
    signals=signal_mask(d,rsi_low,rsi_high,volume_ratio)
    cash=float(capital);qty=0;entry_i=None;entry_cash=None;entry_price=None
    fee=fee_bps/10000;slip=slippage_bps/10000
    ledger=[];curve=[];peak=float(capital)
    for i,row in d.iterrows():
        # 决策仅使用前一日信号与此前持仓；不能使用本日收盘决定本日开盘成交。
        j=len(curve)
        exiting=bool(qty and j-entry_i>=hold_days)
        if exiting:
            exit_price=float(row.open)*(1-slip)
            proceeds=qty*exit_price*(1-fee)
            cash+=proceeds
            ledger.append({'signal_date':d.date.iloc[entry_i-1], 'entry_date':d.date.iloc[entry_i],
                           'exit_date':row.date,'shares':qty,'entry_price':entry_price,'exit_price':exit_price,
                           'holding_days':j-entry_i,'pnl':proceeds-entry_cash,'exit_reason':'持有期结束：次日开盘模拟退出'})
            qty=0;entry_i=None
        if not qty and not exiting and j>0 and j<len(d)-1 and bool(signals.iloc[j-1]):
            price=float(row.open)*(1+slip)
            shares=math.floor((cash*fraction)/(price*(1+fee)))
            if shares>0:
                qty=shares;entry_i=j;entry_price=price;entry_cash=qty*price*(1+fee)
                cash-=entry_cash
        if j==len(d)-1 and qty:
            exit_price=float(row.close)*(1-slip)
            proceeds=qty*exit_price*(1-fee);cash+=proceeds
            ledger.append({'signal_date':d.date.iloc[entry_i-1],'entry_date':d.date.iloc[entry_i],
                           'exit_date':row.date,'shares':qty,'entry_price':entry_price,'exit_price':exit_price,
                           'holding_days':j-entry_i,'pnl':proceeds-entry_cash,'exit_reason':'演示结束：末日收盘强制模拟平仓'})
            qty=0
        equity=cash+qty*float(row.close)
        peak=max(peak,equity)
        curve.append({'date':row.date,'equity':equity,'drawdown':equity/peak-1})
    result=pd.DataFrame(curve)
    return {'curve':result,'trades':pd.DataFrame(ledger),'return':float(result.equity.iloc[-1]/capital-1),
            'max_drawdown':float(result.drawdown.min()),'final_equity':float(result.equity.iloc[-1])}
