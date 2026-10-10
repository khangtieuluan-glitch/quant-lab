"""fetch_data.py —— 拉取日线行情并存 CSV（2026-10-08 任务 B）

主数据源 baostock，失败自动切 akshare。
用法：
    python fetch_data.py                 # 默认 平安银行 sz.000001
    python fetch_data.py sh.600519       # 换成贵州茅台
"""
from __future__ import annotations

import os
import sys

import pandas as pd

OUT_DIR = "data"


def fetch_baostock(code: str, start: str, end: str, adjustflag: str = "2") -> pd.DataFrame:
    """用 baostock 拉日线。code 形如 'sz.000001' / 'sh.600519'。"""
    import baostock as bs

    lg = bs.login()
    if lg.error_code != "0":
        raise RuntimeError(f"baostock 登录失败: {lg.error_msg}")
    try:
        rs = bs.query_history_k_data_plus(
            code,
            "date,open,high,low,close,volume,amount,turn",
            start_date=start,
            end_date=end,
            frequency="d",
            adjustflag=adjustflag,  # 1=后复权 2=前复权 3=不复权
        )
        if rs.error_code != "0":
            raise RuntimeError(f"查询失败: {rs.error_msg}")
        rows = []
        while rs.next():
            rows.append(rs.get_row_data())
        df = pd.DataFrame(rows, columns=rs.fields)
    finally:
        bs.logout()

    if df.empty:
        raise RuntimeError("baostock 返回空数据")
    return df


def fetch_akshare(code: str, start: str, end: str) -> pd.DataFrame:
    """备用源：akshare。code 形如 'sz.000001' → '000001'。"""
    import akshare as ak

    symbol = code.split(".")[-1]
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start.replace("-", ""),
        end_date=end.replace("-", ""),
        adjust="qfq",  # 前复权
    )
    df = df.rename(
        columns={
            "日期": "date", "开盘": "open", "最高": "high", "最低": "low",
            "收盘": "close", "成交量": "volume", "成交额": "amount", "换手率": "turn",
        }
    )
    return df


def main() -> None:
    code = sys.argv[1] if len(sys.argv) > 1 else "sz.000001"
    start, end = "2021-01-01", "2026-10-08"

    try:
        df = fetch_baostock(code, start, end)
        src = "baostock"
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] baostock 失败({exc})，切 akshare")
        df = fetch_akshare(code, start, end)
        src = "akshare"

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{code.replace('.', '')}.csv")
    df.to_csv(path, index=False)

    print(f"数据源 {src}｜{len(df)} 行｜{df['date'].iloc[0]} → {df['date'].iloc[-1]}")
    print(f"已保存 {path}")
    print(df.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()
