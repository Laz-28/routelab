"""RouteLab environment check. Run: uv run python check_env.py"""
import importlib
import platform
import shutil
import subprocess
import sys

failures = []

def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}".rstrip())
    if not ok:
        failures.append(label)

print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()}")
print(f"Interpreter: {sys.executable}")
check("virtual environment active", sys.prefix != sys.base_prefix,
      "(run via `uv run`, or activate .venv)")

for name in ["numpy", "pandas", "matplotlib", "scipy", "networkx", "numba", "pytest"]:
    try:
        mod = importlib.import_module(name)
        check(f"import {name}", True, getattr(mod, "__version__", ""))
    except Exception as exc:
        check(f"import {name}", False, f"({exc})")

for tool in ["git", "uv", "ruff", "docker"]:
    check(f"{tool} on PATH", shutil.which(tool) is not None)

try:
    result = subprocess.run(["docker", "info"], capture_output=True, timeout=20)
    check("docker daemon reachable", result.returncode == 0,
          "(if this fails: is Docker running, and did you log out and back in after usermod?)")
except Exception as exc:
    check("docker daemon reachable", False, f"({exc})")

try:
    import numpy as np
    check("floating point: 0.1 + 0.2 != 0.3", 0.1 + 0.2 != 0.3)
    check("numpy matmul", (np.array([[1, 0], [0, 1]]) @ np.array([[2, 0], [0, 1]])).tolist() == [[2, 0], [0, 1]])
    check("numpy trapezoid exists (np.trapz is removed in NumPy 2.4+)", hasattr(np, "trapezoid"))
except Exception as exc:
    check("numpy smoke tests", False, f"({exc})")

try:
    from numba import njit

    @njit
    def total(n):
        s = 0.0
        for i in range(n):
            s += i
        return s

    check("numba JIT compiles and runs", total(1000) == 499500.0)
except Exception as exc:
    check("numba JIT compiles and runs", False, f"({exc})")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.savefig("env_check.png")
    check("matplotlib saves a figure", True, "(env_check.png)")
except Exception as exc:
    check("matplotlib saves a figure", False, f"({exc})")

print("\nALL GOOD" if not failures else f"\n{len(failures)} problem(s): {', '.join(failures)}")
sys.exit(1 if failures else 0)