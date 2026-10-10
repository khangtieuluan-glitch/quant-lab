# agent_tools.md —— 量化工具清单

> 用途：P1 的验收标准 —— 把这份文档丢给 Agent，它不看源码就能正确调用每个函数。
> 规则：每写完一个函数，立刻在这里登记一行。

## 数据获取

| 函数 | 文件 | 参数 | 返回 | 用途 | 示例 |
|---|---|---|---|---|---|
| `fetch_baostock(code, start, end, adjustflag="2")` | `fetch_data.py` | code: "sz.000001"/"sh.600519"；start/end: "YYYY-MM-DD"；adjustflag: 1后复权/**2前复权(回测用)**/3不复权 | DataFrame(date,open,high,low,close,volume,amount,turn) | 拉取 A 股日线行情（主源） | `fetch_baostock("sz.000001","2021-01-01","2026-10-08")` |
| `fetch_akshare(code, start, end)` | `fetch_data.py` | 同上（adjust 固定 qfq 前复权） | 同上 | 备用数据源，baostock 挂了才用 | `fetch_akshare("sz.000001","2021-01-01","2026-10-08")` |

## 信号与回测

| 函数 | 文件 | 参数 | 返回 | 用途 | 示例 |
|---|---|---|---|---|---|
| `load(path)` | `hello_quant.py` | path: CSV 路径 | DataFrame（date 已转 datetime，价格列已转数值） | 读入行情 CSV 并清洗 | `load("data/sz000001.csv")` |
| `build_signal(df, fast=5, slow=20)` | `hello_quant.py` | df: 行情表；fast/slow: 均线窗口 | df + ma_fast/ma_slow/signal/position/ret/strat_ret/nav/bench 列 | 双均线信号+回测净值；**position=signal.shift(1) 防未来函数** | `build_signal(df, 5, 20)` |
| `metrics(df)` | `hello_quant.py` | df: build_signal 的输出 | dict(年化收益/年化波动/夏普/最大回撤/日胜率/净值终值) | 绩效指标，全部手写 | `metrics(df)["夏普"]` |
| `plot(df, out="report_01.png")` | `hello_quant.py` | df: 同上；out: 图片路径 | PNG 文件 | 三图：价格均线/净值对比/回撤 | `plot(df)` |

## 已知结论（重要，避免重复踩坑）

- 双均线(5/20) 在平安银行 2021-2026 前复权数据上：**年化 -8.3%，夏普 -0.45，跑输买入持有** → 趋势策略在震荡下行市失效，这是正常现象不是 bug。
- 复权陷阱：回测必须用前复权（adjustflag="2"），不复权序列在除权日有假暴跌。
- matplotlib 中文：`plt.rcParams["font.sans-serif"]=["Microsoft YaHei"]` + `axes.unicode_minus=False`。
