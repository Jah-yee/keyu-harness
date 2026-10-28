"""audit_boundary.py — 沙箱红线终审 (Phase G; spec §1).

AST 静态扫描 replica_2024 全部 Python 文件（docstring/注释不参与——报道摘录
原文出现在 docstring 里是 F0 引文，不是代码）：
1. 禁止网络库 import（socket/urllib/http/requests/ftp/smtp/telnet/ssl…）；
2. 禁止绝对路径字符串常量（/Users/、/home/、/etc/… 或以 / 开头的路径）；
3. subprocess 仅允许出现在声明模块（sim_c2 / sim_kill）；
4. os.system 调用全禁（沙箱用 subprocess+白名单替代）。

零违例 = 红线终审通过（spec §6 验收第 6 条）。
"""
from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_IMPORTS = {"socket", "urllib", "http", "requests", "ftplib", "smtplib",
                     "poplib", "telnetlib", "socketserver", "ssl", "asyncio"}
SUBPROCESS_ALLOWED = {"sim_c2.py", "sim_kill.py"}


def _root_of(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _root_of(node.value)
    return ""


def _strings(tree: ast.AST):
    """字符串常量；跳过 f-string 片段（JoinedStr 的子常量不是独立路径字面量）。"""
    fragment_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            for child in ast.walk(node):
                fragment_ids.add(id(child))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in fragment_ids:
            yield node.value


def scan_file(py: Path) -> list[str]:
    rel = py.relative_to(py.parents[2]).as_posix() if len(py.parents) > 2 else py.name
    src = py.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [f"{rel}: syntax error: {exc}"]
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    out.append(f"{rel}: forbidden network import '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                out.append(f"{rel}: forbidden network import 'from {node.module}'")
        elif isinstance(node, ast.Call):
            root = _root_of(node.func)
            if root == "os" and getattr(node.func, "attr", "") == "system":
                out.append(f"{rel}: os.system is forbidden (use allow-listed subprocess)")
        elif isinstance(node, ast.Import) and False:
            pass
    imports_subprocess = any(isinstance(n, ast.Import) and any(a.name == "subprocess" for a in n.names)
                             for n in ast.walk(tree))
    if imports_subprocess and py.name not in SUBPROCESS_ALLOWED:
        out.append(f"{rel}: subprocess outside declared modules {sorted(SUBPROCESS_ALLOWED)}")
    for s in _strings(tree):
        if s.startswith("/") or s.startswith("/Users") or s.startswith("/home") or s.startswith("/tmp"):
            out.append(f"{rel}: absolute path literal {s[:48]}")
    return out


def check(root: Path) -> list[str]:
    root = Path(root)
    violations: list[str] = []
    for py in sorted(root.rglob("*.py")):
        if py.name == "audit_boundary.py":
            continue  # 终审器自身：含禁用模式清单（正则/名单），豁免自扫
        violations.extend(scan_file(py))
    return violations


def main() -> int:
    root = Path(__file__).resolve().parent
    violations = check(root)
    print(f"audit_boundary: {len(violations)} violations over {root.name}/")
    for v in violations:
        print("  ✗", v)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
