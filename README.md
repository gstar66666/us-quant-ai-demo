# usquant Streamlit Community Cloud纯演示版

**演示数据，不是真实账户。** 所有持仓、价格、资产分布、风险和回测均为固定种子合成样本。本版本不需要任何API密钥、Secrets或账户授权；不要在该演示服务中配置真实密钥。

## 项目与入口

新增独立入口为 `cloud_demo_app.py`，只导入 `cloud_demo/` 的合成数据和离线计算，不导入原app.py、personal_v22、个人快照、长桥插件、币安私人账户、认证或交易模块。原V2.2的personal_local/personal_readonly代码和全部原测试保留。

推荐使用独立最小上传包 **usquant_cloud_demo.zip**：其中没有私人账户或快照模块。解压后，把下面这些文件放在GitHub新仓库的根目录（不是把ZIP本身上传后指望平台解压）：

```text
仓库根目录/
├── cloud_demo_app.py          # Streamlit入口
├── requirements.txt          # 云演示的4项运行依赖
├── README.md                 # 本文
├── .gitignore
├── .streamlit/
│   └── config.toml           # 深色主题；不固定端口，不含Secrets
└── cloud_demo/
    ├── __init__.py
    ├── data.py
    └── analytics.py
```

**GitHub上传清单共8个文件**（cloud_demo目录3个文件计3项）。无需上传原项目的app.py、personal_app.py、run_personal.py、personal_v22、binance_readonly.py、market.py、数据库、data目录、测试临时文件、.venv或任何.env/Secrets文件。

源码工作区中的 `deploy/cloud_demo/` 是同样的最小部署副本；可重新执行 `python build_cloud_demo_bundle.py` 生成。原根目录requirements.txt仍保留旧功能需要的依赖；上传包根目录的requirements.txt专供演示，仅需要：

```text
streamlit>=1.40,<2
pandas>=2.2,<3
numpy>=1.26,<3
plotly>=5.24,<7
```

本次验证使用Python 3.12。没有交易SDK或账户密钥依赖。Streamlit自身可能包含网络相关依赖，但演示业务代码不调用外部服务。

## 本机/云工作区启动检查

独立上传包解压目录中：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run cloud_demo_app.py --server.address 0.0.0.0 --server.port 8501
```

这只是启动命令，不代表已部署到Community Cloud。本机可打开localhost:8501；iPad需要部署后平台实际生成的HTTPS地址，不能用iPad的localhost访问云工作区。

## iPhone / iPad Safari部署步骤

1. 在Safari打开当前聊天，下载 `usquant_cloud_demo.zip`。打开系统“文件”App，在“下载”中点ZIP解压。
2. 登录 https://github.com/ ，新建一个专门存演示代码的仓库，例如 `usquant-cloud-demo`。不要选择包含私人快照或账户配置的旧仓库。
3. 将上面的8个文件按路径上传，确认GitHub仓库根目录能直接看到 `cloud_demo_app.py` 和 `requirements.txt`。不要只上传ZIP，也不要多嵌套一层同名文件夹。
4. Safari若不方便上传目录，可以在GitHub用“Add file → Create new file”，按完整相对路径创建文件（例如 `cloud_demo/data.py`）；`.streamlit/config.toml`也是同样方式。若手机看不到隐藏文件或多文件上传不便，最省操作的是在Mac完成这次文件上传，后续部署和访问均可在iPad/iPhone完成。
5. 在Safari打开 https://share.streamlit.io/ ，登录并连接刚才的GitHub账户。选择“Create app / New app”，选择对应仓库和实际分支（通常为main）。
6. **Main file path填写 `cloud_demo_app.py`**。不要选 `app.py`、`personal_app.py` 或 `run_personal.py`。高级设置如提供Python版本选项，选本次验证的Python 3.12。**Secrets保持空，不填任何真实密钥。**
7. 点击“Deploy”，等待依赖安装和应用启动。只有成功后平台显示的 `https://……streamlit.app` 才是访问入口。本次没有代你执行这些账户操作，也没有生成可用的公网网址。
8. iPhone/iPad用Safari打开该实际生成的网址。需要大屏操作时，在Safari页面菜单中“请求桌面网站”；iPad可横屏查看。表格可以横向滚动，图表支持触控缩放；本次未在真实iOS硬件上验收。
9. 可通过Safari“分享 → 添加到主屏幕”保存快捷入口。这不是离线安装，仍需网络；Community Cloud休眠后可能需等待唤醒。

无需额外配置启动命令、固定公网端口或认证网关。应用访问范围与仓库权限分别以平台设置为准；这里只承载合成公开演示，不应被改成真实账户实例。

## 展示内容与假设

- 美股6只示例持仓、成本、市值与计算浮盈亏；BTC/ETH/BNB为合成数量和合成价格，不是币安余额。
- USD与USDT分别列示。资产分布和压力情景仅为统一展示假设1 USDT=1 USD，页面明确提示不是真实汇率。情景跌幅不是概率预测或确定性最大损失。
- K线由固定种子生成，日期为普通工作日，不是交易所日历，最新样本日为2025-09-10，不冒充当前行情。
- 短线条件：收盘>MA5>MA10>MA20、RSI14在35—75、成交量/此前20日均量≥0.8。该独立演示的RSI采用14次涨跌简单平均；不修改原有策略/回测逻辑。
- 回测只用合成价格；信号日收盘生成，最早下一工作日开盘模拟入场。持有2—5个合成工作日后开盘模拟退出，单仓、无杠杆、每次最多25%可用现金，双边计手续费和滑点。末日剩余持仓收盘强制模拟平仓，可能不足设定持有期。没有真实订单。
- 指标缺数据留空，零均量不除零，无信号不虚构交易。结果不是策略有效性证据，没有AI胜率或实盘收益承诺。

## 安全与验证

演示入口不读取os.environ、os.getenv、st.secrets、.env、私人快照或账户文件；不导入私人模块，不使用requests/交易接口，不提供文件上传、密钥输入或账户同步。CSV下载只导出内存中的合成样本，不写私人账户数据。

新增测试对本地导入图作白名单检查，并在阻断网络、私人模块调用、密钥变量、st.secrets与私人文件访问时执行页面和交互；另验证确定性样本、量比除零、无效输入、费用核算、信号次日执行及未来价格不改变历史权益。最小上传包还会在与私人源码隔离的目录中检查启动与页面执行。

测试结果见工作区CLOUD_DEMO_REPORT.md。自动化AppTest与HTTP启动检查不能替代iPhone/iPad Safari实机或Streamlit Community Cloud真实部署验收。本次没有上传GitHub、部署或提交订单。
