#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_extract.py — GB 标准 PDF 的文本层判定与页面渲染（供 AI 内置 PDF 解析引擎使用）。

零配置说明（面向无编程基础的用户）：
    本脚本由 AI 助手在本地自动执行，最终用户全程无需安装或配置任何软件：
    1. 运行时自动检测所需依赖（PyMuPDF），同时兼容 pymupdf / fitz 两种导入名；
    2. 依赖缺失时自动通过 pip 安装，无需用户手动操作；
    3. 若自动安装失败（离线/受限环境），脚本返回明确退出码，
       AI 助手自动降级用内置文档解析/图像识别能力完成同样任务，流程不中断。

两种能力（对应 GB2MD「内置 PDF 引擎」流程）：
    A. 判定（--analyze）：检查 PDF 是否有可提取的文本层。
       输出末尾打印 `DECISION: TEXT`（可直接提取文字）或 `DECISION: OCR`（扫描件/乱码，需 OCR）。
    B. 渲染（--render）：当判定为 OCR 时，把每一页渲染成高清 PNG，
       交给 AI 内置的图像识别（视觉 OCR）能力逐页提取文字。

用法：
    python pdf_extract.py <pdf> --analyze            # 先判定能否识别文字
    python pdf_extract.py <pdf> --render -o pages    # 需要时强制渲染，供 OCR
    python pdf_extract.py --check                    # 仅检查环境是否就绪

退出码：
    0 成功（--analyze 完成，无论结论是 TEXT 还是 OCR）
    1 找不到文件 / 通用错误
    2 依赖不可用且自动安装失败（AI 助手据此降级到内置能力）
    3 参数错误
"""

import argparse
import importlib
import os
import subprocess
import sys


def _import_pymupdf():
    """按优先级尝试导入 PyMuPDF，兼容新旧两种模块名。任一成功返回模块，均失败返回 None。"""
    for name in ("pymupdf", "fitz"):
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


def _install_pymupdf() -> bool:
    """用当前解释器自动安装 PyMuPDF，成功返回 True。"""
    print("未检测到 PyMuPDF（PDF 解析库），正在自动安装，请稍候……")
    print("提示：此过程由 AI 助手自动完成，无需用户手动操作。")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install",
             "--disable-pip-version-check", "--quiet", "PyMuPDF"],
        )
    except Exception as exc:  # noqa: BLE001
        print(f"自动安装失败：{exc}", file=sys.stderr)
        print(
            "提示：AI 助手将自动改用内置文档解析/图像识别能力完成 PDF 处理，"
            "本任务不会因此中断，用户无需做任何操作。",
            file=sys.stderr,
        )
        return False
    importlib.invalidate_caches()
    return True


def ensure_module():
    """返回可用的 PyMuPDF 模块；必要时自动安装。失败返回 None。"""
    module = _import_pymupdf()
    if module is not None:
        return module
    if not _install_pymupdf():
        return None
    module = _import_pymupdf()
    if module is None:
        print("依赖安装后仍无法加载 PyMuPDF，请向 AI 助手反馈。", file=sys.stderr)
    return module


def check_only() -> int:
    """仅检查环境是否就绪（不安装、不解析）。"""
    print(f"Python 版本：{sys.version.split()[0]}")
    print(f"解释器路径：{sys.executable}")
    module = _import_pymupdf()
    if module is not None:
        ver = getattr(module, "__version__", None) or getattr(module, "VersionBind", None)
        print(f"PyMuPDF 已就绪（导入名：{module.__name__}，版本：{ver or '未知'}）")
        return 0
    print("PyMuPDF 尚未安装（首次运行时会自动安装，用户无需操作）。")
    return 1


def _is_readable(ch: str) -> bool:
    """判断单个字符是否属于「正文可读字符」（汉字、全角标点、ASCII 可打印、常见符号）。"""
    o = ord(ch)
    if 0x4E00 <= o <= 0x9FFF:        # CJK 统一汉字
        return True
    if 0x3000 <= o <= 0x303F:        # CJK 标点（。、《》等）
        return True
    if 0xFF00 <= o <= 0xFFEF:        # 全角字符（，：；！？（）等）
        return True
    if 0x20 <= o <= 0x7E:            # ASCII 可打印（字母、数字、符号）
        return True
    if ch in "℃±×÷·—～≈≤≥㎡Ωμ·′″":  # 科技常用符号
        return True
    if o in (0x09, 0x0A, 0x0D):      # 制表/换行
        return True
    return False


def analyze(path: str) -> int:
    """判定 PDF 文本层是否可直接提取。末尾打印 DECISION。"""
    pymupdf = ensure_module()
    if pymupdf is None:
        return 2
    doc = pymupdf.open(path)
    total = doc.page_count
    total_chars = 0
    readable_chars = 0
    cjk_chars = 0
    per_page_empty = 0
    for i in range(total):
        text = doc.load_page(i).get_text("text")
        # 去掉空白后统计
        stripped = "".join(text.split())
        if len(stripped) < 20:        # 该页几乎无可提取字符（很可能是扫描图）
            per_page_empty += 1
        for ch in stripped:
            total_chars += 1
            if _is_readable(ch):
                readable_chars += 1
            if 0x4E00 <= ord(ch) <= 0x9FFF:
                cjk_chars += 1
    doc.close()

    readable_ratio = (readable_chars / total_chars) if total_chars else 0.0
    avg_chars = (total_chars / total) if total else 0.0
    print(f"页数: {total}")
    print(f"提取字符总数: {total_chars}")
    print(f"可读字符占比: {readable_ratio:.1%}")
    print(f"平均每页字符: {avg_chars:.0f}")
    print(f"近空页数: {per_page_empty}")

    # 判定规则：可读占比偏低、平均字符过少、或多数页近空 → 需要 OCR
    need_ocr = (
        total_chars == 0
        or readable_ratio < 0.60
        or avg_chars < 30
        or (total and per_page_empty >= max(1, total * 0.5))
    )
    if need_ocr:
        print("结论: 文本层不可用（扫描件/乱码），请用 --render 渲染后做 OCR。")
        print("DECISION: OCR")
    else:
        print(f"（其中中文字符约 {cjk_chars} 个）")
        print("结论: 文本层可直接提取。")
        print("DECISION: TEXT")
    return 0


def render(path: str, out_dir: str, dpi: int, pages: str = None) -> int:
    """把页面渲染为高清 PNG，供 AI 内置视觉 OCR。"""
    pymupdf = ensure_module()
    if pymupdf is None:
        return 2
    os.makedirs(out_dir, exist_ok=True)
    doc = pymupdf.open(path)
    total = doc.page_count
    if pages:
        idx = _parse_pages(pages, total)
    else:
        idx = list(range(total))
    print(f"总页数: {total}，待渲染: {len(idx)}")
    for i in idx:
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=dpi)
        out_path = os.path.join(out_dir, f"p{i + 1:02d}.png")
        pix.save(out_path)
        print(f"{out_path}\t{pix.width}x{pix.height}")
    doc.close()
    print("渲染完成。AI 助手将把以上 PNG 逐页（或整批）交给图像识别能力，"
          "要求逐字完整提取、保留条款编号/公式/表格，不总结、不改写。")
    return 0


def _parse_pages(spec: str, total: int):
    """解析 --pages 形如 '1-10,15'（1 起始），返回 0 起始页索引列表。"""
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo = max(1, int(a or 1)); hi = min(total, int(b or total))
            out.update(range(lo - 1, hi))
        else:
            p = int(part)
            if 1 <= p <= total:
                out.add(p - 1)
    return sorted(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GB 标准 PDF 文本层判定与页面渲染（零配置）。"
    )
    parser.add_argument("pdf", nargs="?", help="PDF 文件路径")
    parser.add_argument("--check", action="store_true", help="仅检查环境是否就绪")
    parser.add_argument("--analyze", action="store_true",
                        help="判定文本层能否直接提取（默认动作）")
    parser.add_argument("--render", action="store_true", help="渲染页面为 PNG 供 OCR")
    parser.add_argument("-o", "--out-dir", default="pdf_pages",
                        help="渲染输出目录（默认 pdf_pages）")
    parser.add_argument("--dpi", type=int, default=300, help="渲染分辨率（默认 300）")
    parser.add_argument("--pages", default=None, help="页码范围，如 1-10,15")
    args = parser.parse_args()

    if args.check:
        return check_only()
    if not args.pdf:
        print("错误：请提供 PDF 文件路径（或使用 --check 检查环境）。", file=sys.stderr)
        return 3
    if not os.path.isfile(args.pdf):
        print(f"错误：找不到 PDF 文件：{args.pdf}", file=sys.stderr)
        return 1

    if args.render:
        return render(args.pdf, args.out_dir, args.dpi, args.pages)
    # 默认与 --analyze 相同：判定文本层
    return analyze(args.pdf)


if __name__ == "__main__":
    sys.exit(main())
