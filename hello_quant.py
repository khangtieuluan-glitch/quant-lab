"""hello_quant.py —— 人生第一张净值曲线（2026-10-08 任务 C+D）

双均线策略 + 手写回测 + 绩效指标 + 三图输出。
用法：
    python hello_quant.py                 # 默认读 data/sz000001.csv
    python hello_quant.py data/sh600519.csv

⚠️ 今天唯一要刻进脑子的一行：position = signal.shift(1)
   不 shift 就是未来函数，回测收益会假到离谱。
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False  # 负号正常显示

RED, GREEN, GRAY = "#d62728", "#2ca02c", "#7f7f7f"  # A股习惯：红涨绿跌


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    for col in ("open", "high", "low", "close", "volume"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["close"]).reset_index(drop=True)


def build_signal(df: pd.DataFrame, fast: int = 5, slow: int = 20) -> pd.DataFrame:
    """双均线信号：快线在慢线上方 → 持有(1)，否则空仓(0)。"""
    df = df.copy()
    df["ma_fast"] = df["close"].rolling(fast).mean()
    df["ma_slow"] = df["close"].rolling(slow).mean()
    df["signal"] = (df["ma_fast"] > df["ma_slow"]).astype(int)

    # ⭐ 命根子：今天收盘才知道信号 → 明天才建仓
    df["position"] = df["signal"].shift(1).fillna(0)

    df["ret"] = df["close"].pct_change().fillna(0)
    df["strat_ret"] = df["position"] * df["ret"]
    df["nav"] = (1 + df["strat_ret"]).cumprod()
    df["bench"] = (1 + df["ret"]).cumprod()
    return df


def metrics(df: pd.DataFrame) -> dict:
    """绩效指标：全部手写，不用库。"""
    r = df["strat_ret"]
    ann_ret = r.mean() * 252
    ann_vol = r.std() * (252 ** 0.5)
    sharpe = ann_ret / ann_vol if ann_vol else 0.0
    nav = df["nav"]
    mdd = (nav / nav.cummax() - 1).min()
    win = (r[r != 0] > 0).mean() if (r != 0).any() else 0.0
    return {
        "年化收益": ann_ret,
        "年化波动": ann_vol,
        "夏普": sharpe,
        "最大回撤": mdd,
        "日胜率": win,
        "净值终值": nav.iloc[-1],
    }


def plot(df: pd.DataFrame, out: str = "report_01.png") -> None:
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True,
                             gridspec_kw={"height_ratios": [2, 2, 1]})

    ax = axes[0]
    ax.plot(df["date"], df["close"], color=GRAY, lw=1, label="收盘价")
    ax.plot(df["date"], df["ma_fast"], color=RED, lw=1.2, label="MA5")
    ax.plot(df["date"], df["ma_slow"], color=GREEN, lw=1.2, label="MA20")
    ax.set_title("价格与双均线", fontsize=12)
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(df["date"], df["nav"], color=RED, lw=1.5, label="双均线策略")
    ax.plot(df["date"], df["bench"], color=GRAY, lw=1.2, label="买入持有")
    ax.axhline(1, color="#bbbbbb", lw=0.8, ls="--")
    ax.set_title("净值曲线", fontsize=12)
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)

    ax = axes[2]
    dd = df["nav"] / df["nav"].cummax() - 1
    ax.fill_between(df["date"], dd * 100, 0, color=GREEN, alpha=0.35)
    ax.set_title("策略回撤 (%)", fontsize=12)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out, dpi=120)
    print(f"图已保存 {out}")


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "sz000001.csv")
    df = load(path)
    df = build_signal(df)

    m = metrics(df)
    print("=" * 46)
    print(f"标的 {path}｜{df['date'].iloc[0]:%Y-%m-%d} → {df['date'].iloc[-1]:%Y-%m-%d}｜{len(df)} 个交易日")
    for k, v in m.items():
        print(f"{k:8s} {v:.2%}" if k != "夏普" else f"{k:8s} {v:.2f}")
    print("=" * 46)
    if m["净值终值"] > 20:
        print("⚠️ 净值 > 20，几乎肯定踩了未来函数，检查 shift(1) 和复权")
    print("提醒：这不是好策略，今天只验证「链路通了」。")

    plot(df)


if __name__ == "__main__":
    main()
