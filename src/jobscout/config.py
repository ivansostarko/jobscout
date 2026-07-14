"""Configuration loading: config/jobscout.yaml + .env."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

PROJECT_ROOT = Path(os.environ.get("JOBSCOUT_HOME", Path(__file__).resolve().parents[2]))
CONFIG_PATH = Path(os.environ.get("JOBSCOUT_CONFIG", str(PROJECT_ROOT / "config" / "jobscout.yaml")))


def _load_dotenv(path: Path) -> None:
    """Tiny .env loader (no external dependency). Does not override existing env."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def load_config() -> dict:
    _load_dotenv(PROJECT_ROOT / ".env")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    data_dir = Path(cfg["general"].get("data_dir", "./data"))
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    cfg["general"]["data_dir_resolved"] = str(data_dir)
    cfg["general"]["excel_path"] = str(data_dir / cfg["general"].get("excel_file", "jobs.xlsx"))
    return cfg


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)
