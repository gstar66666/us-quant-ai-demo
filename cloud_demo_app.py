"""Streamlit Community Cloud演示专用入口。仅使用cloud_demo纯合成数据与离线计算。"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from cloud_demo.data import DEMO_LABEL,DEMO_AS_OF,STOCKS,demo_holdings,demo_bars
from cloud_demo.analytics import indicators,signal_mask,risk_scenario,backtest

st.set_page_config(page_title='usquant 中文投资看板｜演示版',page_icon='📊',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
.block-container{max-width:1440px;padding-top:1.2rem;padding-bottom:3rem}
h1{font-size:2rem!important;letter-spacing:-.02em}
.demo-banner{background:#38221a;border:1px solid #f2ae61;color:#ffe0b7;padding:16px 20px;border-radius:12px;font-size:1.15rem;font-weight:750;margin-bottom:18px}
div[data-testid="stMetric"]{background:#141e2e;border:1px solid #26354b;border-radius:12px;padding:14px}
@media(max-width:700px){h1{font-size:1.4rem!important}.block-container{padding:1rem .8rem}.demo-banner{font-size:1rem;padding:12px}button{min-height:44px}}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="demo-banner">演示数据，不是真实账户 · 无账户连接 · 无交易功能</div>',unsafe_allow_html=True)
st.title('usquant 中文统一投资看板')
st.caption('CLOUD DEMO / 为 iPhone、iPad 和电脑浏览器设计')
st.info(DEMO_LABEL+'。所有持仓、成本、行情、风险场景和回测均由内置合成样本计算，不是投资建议或收益预测。')
st.caption('样本日期：'+DEMO_AS_OF+'。不提供文件上传、账户登录、密钥输入或真实持仓同步。')
holdings=demo_holdings()
stocks=holdings[holdings.category=='美股']
crypto=holdings[holdings.category=='数字资产']
left,right=st.columns(2)
left.metric('美股演示市值 / USD',f'{stocks.market_value.sum():,.2f}',f'示例浮盈亏 {stocks.unrealized.sum():+,.2f}')
right.metric('数字资产演示市值 / USDT',f'{crypto.market_value.sum():,.2f}',f'示例浮盈亏 {crypto.unrealized.sum():+,.2f}')
labels={'symbol':'资产','quantity':'示例数量','cost_price':'合成单位成本','price':'合成价格',
        'currency':'计价币种','cost_value':'演示成本','market_value':'演示市值','unrealized':'演示浮盈亏'}
tabs=st.tabs(['统一持仓','资产分布与风险','美股短线分析','离线回测演示'])
with tabs[0]:
    st.subheader('美股示例持仓')
    st.dataframe(stocks[list(labels)].rename(columns=labels),hide_index=True,use_container_width=True)
    st.subheader('BTC · ETH · BNB 演示资产')
    st.caption('这些数量不是币安余额，价格不是币安行情。本入口不调用任何账户或市场API。')
    st.dataframe(crypto[list(labels)].rename(columns=labels),hide_index=True,use_container_width=True)
    st.download_button('下载合成持仓示例CSV',holdings.rename(columns=labels).assign(数据性质=DEMO_LABEL).to_csv(index=False).encode('utf-8-sig'),
                       file_name='usquant_合成演示持仓.csv',mime='text/csv')
with tabs[1]:
    st.subheader('资产分布 / 演示折算')
    st.warning('仅为展示统一分布，以下假设1 USDT = 1 USD；不是真实汇率。上方USD与USDT市值分别列示，不应直接视作真实账户总资产。')
    fig=go.Figure(go.Pie(labels=holdings.symbol,values=holdings.market_value,hole=.67,
                        hovertemplate='%{label}<br>演示折算市值 %{value:,.2f}<br>%{percent}<extra></extra>'))
    fig.update_layout(template='plotly_dark',height=390,margin=dict(l=5,r=5,t=10,b=5),paper_bgcolor='#0b1019',legend=dict(orientation='h'))
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
    a,b=st.columns(2)
    stock_drop=a.slider('美股压力跌幅（%）',-40,0,-10,key='cloud_stock_stress')
    crypto_drop=b.slider('数字资产压力跌幅（%）',-70,0,-20,key='cloud_crypto_stress')
    risk=risk_scenario(holdings,stock_drop/100,crypto_drop/100)
    a,b,c=st.columns(3)
    a.metric('数字资产演示权重',f"{risk['crypto_weight']:.1%}")
    b.metric('最大单项演示权重',f"{risk['max_weight']:.1%}")
    c.metric('所选场景折算损益',f"{risk['loss']:+,.2f}")
    if risk['crypto_weight']>=.4:st.warning('演示阈值提醒：数字资产权重达到40%。这是界面规则，不是已验证的最优配置。')
    if risk['max_weight']>=.35:st.warning('演示阈值提醒：单项权重达到35%，关注集中度。')
    st.caption('压力结果=各类演示市值×假设跌幅。未估计发生概率、相关性、流动性或汇率变化，不是VaR或确定性最大损失。')
with tabs[2]:
    st.subheader('2—5日美股短线分析 / 合成日线')
    symbol=st.selectbox('演示股票',[r[0] for r in STOCKS],key='cloud_symbol')
    d=indicators(demo_bars(symbol))
    row=d.iloc[-1]
    a,b,c=st.columns(3)
    a.metric('合成末日收盘 / USD',f'{row.close:.2f}')
    b.metric('演示RSI14',f'{row.RSI14:.1f}')
    c.metric('演示量比',f'{row.volume_ratio:.2f}')
    fig=make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[.75,.25],vertical_spacing=.05)
    p=d.tail(90)
    fig.add_trace(go.Candlestick(x=p.date,open=p.open,high=p.high,low=p.low,close=p.close,name='合成K线',
                                increasing_line_color='#36d6ac',decreasing_line_color='#ff647c'),row=1,col=1)
    for n,color in [(5,'#e8c26c'),(10,'#65afff'),(20,'#b68cff')]:
        fig.add_trace(go.Scatter(x=p.date,y=p[f'MA{n}'],name=f'MA{n}',line=dict(color=color,width=1.2)),row=1,col=1)
    fig.add_trace(go.Bar(x=p.date,y=p.volume,name='合成成交量',marker_color='#3c7389'),row=2,col=1)
    fig.update_layout(template='plotly_dark',height=520,xaxis_rangeslider_visible=False,legend=dict(orientation='h'),
                      margin=dict(l=5,r=5,t=20,b=10),paper_bgcolor='#0b1019')
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'scrollZoom':False})
    hit=bool(signal_mask(d).iloc[-1])
    st.write('演示条件状态：'+('满足设定条件' if hit else '未满足全部条件'))
    st.caption('条件：收盘>MA5>MA10>MA20，RSI14在35—75，成交量/此前20日均量≥0.8。RSI使用14次涨跌的简单平均，仅为此独立演示；不改变原策略。')
    st.caption('日期是普通工作日序列，不是交易所日历；满足指标条件不代表未来上涨。')
with tabs[3]:
    st.subheader('离线回测演示 / 单仓做多、无杠杆')
    st.warning('只回测内置合成价格；结果不能证明真实策略有效，不提供AI胜率或实盘收益承诺。')
    a,b=st.columns(2)
    bt_symbol=a.selectbox('回测示例股票',[r[0] for r in STOCKS],key='cloud_bt_symbol')
    days=b.slider('持有合成工作日数',2,5,3,key='cloud_hold_days')
    a,b=st.columns(2)
    fee=a.number_input('每次模拟成交手续费（基点）',min_value=0.,max_value=100.,value=5.,step=1.,key='cloud_fee')
    slip=b.number_input('每次模拟成交滑点（基点）',min_value=0.,max_value=100.,value=5.,step=1.,key='cloud_slip')
    result=backtest(demo_bars(bt_symbol),hold_days=days,fee_bps=fee,slippage_bps=slip)
    a,b,c=st.columns(3)
    a.metric('合成样本累计收益',f"{result['return']:+.2%}")
    b.metric('合成样本最大回撤',f"{result['max_drawdown']:.2%}")
    c.metric('已结束模拟交易数',len(result['trades']))
    st.line_chart(result['curve'].set_index('date')[['equity']].rename(columns={'equity':'演示权益 / USD'}))
    st.caption('初始演示资金100,000 USD，每次最多使用可用现金的25%，整股；手续费和滑点均双边计入。1基点=0.01%。无持仓时，上日收盘满足上述条件，下一工作日开盘模拟入场；到持有期结束后的开盘退出，不在同一开盘重新入场。')
    st.caption('末日剩余持仓按该日合成收盘强制模拟平仓，可能不足2—5天；这只是离线终值约定，不代表现实中保证可成交。指标预热不足或无信号时保持现金，不虚构交易。')
    if result['trades'].empty:st.info('该合成样本和规则下没有完成的模拟交易。')
    else:
        mapping={'signal_date':'信号日','entry_date':'模拟入场日','exit_date':'模拟退出日','shares':'模拟股数',
                 'entry_price':'含滑点入场价','exit_price':'含滑点退出价','holding_days':'持有工作日数','pnl':'费用后演示盈亏','exit_reason':'演示退出原因'}
        st.dataframe(result['trades'].rename(columns=mapping),hide_index=True,use_container_width=True)
st.divider()
st.caption(DEMO_LABEL+' · 本演示无密钥配置、私人账户、持仓快照读取、后台同步或真实下单能力。')
