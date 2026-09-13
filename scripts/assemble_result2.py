# -*- coding: utf-8 -*-
"""将问题二结果的二进制分片还原为 result2.xlsx。"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    ROOT / "outputs/q2/result2.xlsx.part00",
    ROOT / "outputs/q2/result2.xlsx.part01",
    ROOT / "outputs/q2/result2.xlsx.part02",
    ROOT / "outputs/q2/result2.xlsx.part03",
    ROOT / "outputs/q2/result2.xlsx.part04",
]
TARGET = ROOT / "outputs/q2/result2.xlsx"
EXPECTED_SHA256 = "33e0ff32215b4d455216ed2847477047cdde5e75d2b2b6e366bab8c6e02c7a3e"

def main():
    with TARGET.open("wb") as destination:
        for part in PARTS:
            destination.write(part.read_bytes())
    actual = sha256(TARGET.read_bytes()).hexdigest()
    if actual != EXPECTED_SHA256:
        raise RuntimeError(f"校验失败：{actual}")
    print(f"已还原：{TARGET}")

if __name__ == "__main__":
    main()
