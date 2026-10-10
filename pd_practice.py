import pandas as pd
df = pd.read_csv("data/sz000001.csv")
print(df.shape)
print(df.head(3))
print(df["close"].head(3))                 # 只把 close 这一列的前 3 个打印出来
print(df["close"].mean())                  # close 这一列的【平均值】
print(df["close"].max()) 


# 移动平均线
df["ma5"] = df["close"].rolling(5).mean()
print(df[["date", "close", "ma5"]].head(10))

# # 整列往后移一个，今天的信号，今天收盘后才能算出来 → 只能明天用
# df["yesterday_close"] = df["close"].shift(1)
# # 完全等价于手写循环："每一行，取上一行的 close"
# df["position"] = df["signal"].shift(1).fillna(0)
# # 今天的信号 往后挪一天 = 明天才持仓

# 昨天的收盘价：整列往下挪一格
df["close_lag1"] = df["close"].shift(1)

print(df[["date", "close", "close_lag1"]].head(5))

# pct_change() —— 算每天的涨跌幅
df["ret"] = df["close"].pct_change().fillna(0)

# cumprod() —— 把每天的收益滚成净值曲线
# 策略每天赚一点亏一点，怎么算“最后总共多少钱”？复利累乘。
df["nav"] = (1 + df["ret"]).cumprod()






# 投进一张股票表 → 算两条均线 → 
# 快线在上记 1 否则 0 → 信号延后一天（shift）→ 
# 算每天涨跌幅 → 只让持仓的日子吃收益 → 
# 累乘成净值 → 吐出这张加工过的表。

import pandas as pd


def build_signal(df, fast=5, slow=20):
    """双均线策略：快线上穿慢线持有，信号延后一天生效。
    输入: df 含 date/close 列
    输出: df 加了 signal/position/ret/strat_ret/nav 列
    """
    df = df.copy()

    # TODO 1: 算两条均线
    df["ma_fast"] = df["close"].rolling(fast).mean()
    df["ma_slow"] = df["close"].rolling(slow).mean()

    # TODO 2: 算 signal（快线在上=1，否则=0）
    df["signal"] = (df["ma_fast"] > df["ma_slow"]).astype(int)

    # TODO 3: 算 position = signal 延后一天，首行填 0   ← 命根子
    df["position"] = df["signal"].shift(1).fillna(0)

    # TODO 4: 算 ret = 每日涨跌幅，首行填 0
    df["ret"] = df["close"].pct_change().fillna(0)

    # TODO 5: 算 strat_ret；nav = (1 + strat_ret) 累乘
    df["strat_ret"] = df["position"] * df["ret"]
    df["nav"] = (1 + df["strat_ret"]).cumprod()

    return df


# 自测
df = pd.read_csv("data/sz000001.csv")
df = build_signal(df)
print(df[["date", "close", "signal", "position", "ret", "strat_ret", "nav"]].tail(10))
print("净值终值:", df["nav"].iloc[-1])

