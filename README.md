# quant-lab —— 个人量化工作台（P0 阶段）

> 量化学习路线 v3（Q-Agent 融合版）· P0 基础速通 + 第一闭环
> 数据源：baostock（主）/ akshare（备）· 回测全手写，不用 backtrader

## 文件说明

| 文件 | 用途 |
|---|---|
| `check_env.py` | 环境自检：核心包版本检查 |
| `fetch_data.py` | 拉取 A 股日线行情存 CSV（baostock 失败自动切 akshare） |
| `hello_quant.py` | 双均线策略 + 手写回测 + 绩效指标 + 三图输出 |
| `pd_practice.py` | pandas 练习（read_csv / rolling / shift / pct_change / cumprod） |
| `agent_tools.md` | 工具清单：每个函数的参数/返回/示例，供 Agent 调用 |
| `data/` | 行情 CSV（前复权日线） |
| `report_01.png` | 第一张净值曲线图 |

## 运行

```powershell
cd D:\Documents\ChatGPT\Quant学习路线\quant-lab
venv\Scripts\python fetch_data.py        # 拉数据（默认 sz.000001 平安银行）
venv\Scripts\python hello_quant.py       # 跑回测出图
```

⚠️ 必须先 cd 进项目目录再运行——脚本内部用相对路径 `data/...`。

## 核心知识点：shift(1) 防未来函数

```python
df["position"] = df["signal"].shift(1).fillna(0)
```

今天收盘才算出的信号，明天才能建仓。不 shift 就是未来函数，净值虚高几十倍。

## 当前实测（双均线 5/20，平安银行 2021-2026 前复权）

年化 -8.28%｜夏普 -0.45｜最大回撤 -54.1%｜净值终值 0.577
→ 趋势策略在震荡下行市失效，回测诚实（没踩未来函数）。
