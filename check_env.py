"""check_env.py —— 环境自检（2026-10-08 任务 A）

用法：
    cd /d/quant-lab
    source venv/Scripts/activate      # Git Bash
    python check_env.py
"""
import sys

MODULES = ["pandas", "numpy", "matplotlib", "baostock", "akshare", "pytest"]

ok, miss = [], []
for name in MODULES:
    try:
        mod = __import__(name)
        ver = getattr(mod, "__version__", "")
        print(f"OK   {name:12s} {ver}")
        ok.append(name)
    except Exception as exc:  # noqa: BLE001
        print(f"MISS {name:12s} {exc}")
        miss.append(name)

print("-" * 40)
print(f"Python {sys.version.split()[0]}")
print(f"通过 {len(ok)}/{len(MODULES)}")
if miss:
    print("缺失：" + ", ".join(miss))
    print("补装：pip install " + " ".join(miss) + " -i https://pypi.tuna.tsinghua.edu.cn/simple")
else:
    print("全部通过，可以开工。")
