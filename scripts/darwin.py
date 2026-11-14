#!/usr/bin/env python3
"""达尔文.skill 3.0 的确定性工具（只用标准库，不联网，不改被检查的 skill）。

  check  零 token 体检：frontmatter、路由、体积、引用可达、安全与可移植性
  pair   盲评配对：把两组产出随机标成 A/B，去掉执行记录和能看出来历的路径
  tally  计票与棘轮裁决：按固定规则给出 keep / revert，不靠主 agent 自己掂量

用法见 SKILL.md；每个子命令都支持 -h。
"""
import argparse
import json
import random
import re
import shutil
import statistics
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "_archive", ".trash", "synced", "__pycache__"}
WHEN_CUES = ("use when", "use on", "use for", "when ", "trigger", "触发", "时用", "时使用",
             "时触发", "适用于", "当用户", "说「", "说\"")
SOFT_WORDS = ("可以考虑", "视情况", "根据情况", "灵活把握", "酌情", "as appropriate", "if needed", "as needed")
RUNTIME_LOCK = re.compile(r"在 Claude Code 里|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|/plugin install\b")
HOME_PATH = re.compile(r"(/Users/(?!you\b|me\b|name\b|xxx\b|username\b|user\b|<)[A-Za-z0-9_.-]+/|/home/(?!user\b|<)[a-z0-9_.-]+/|C:\\Users\\(?!<)[A-Za-z0-9_.-]+\\)")
SECRET = re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[bp]-[A-Za-z0-9-]{20,})")
RISKY = re.compile(r"\brm\s+(-[a-z]*\s+)*-[a-z]*(r[a-z]*f|f[a-z]*r)|\brm\s+-r\s+-f|git\s+reset\s+--hard|git\s+clean\s+-[a-z]*f|push\s+(--force|-f)\b"
                   r"|--no-verify|DROP\s+TABLE|shutil\.rmtree|curl[^\n|]*\|\s*(ba)?sh", re.I)
GUARD = ("确认", "confirm", "禁止", "不要", "不许", "never", "don't", "do not", "avoid", "禁用", "🔴", "STOP", "CHECKPOINT")
UNFINISHED = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|【待补】")
REF_PATH = re.compile(r"(?<![\w/.-])((?:references|reference|scripts|assets|templates|agents|examples)/[\w./-]+\.[A-Za-z0-9]{1,5})")


def split_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    m = re.search(r"^---\s*$", text[3:], re.M)
    if not m:
        return None, text
    return text[3:3 + m.start()], text[3 + m.end():]


def read_field(fm, key):
    """取顶层标量字段；支持引号、> / | 块和缩进续行。"""
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{key}:\s*(.*)$", line)
        if not m:
            continue
        val = m.group(1).strip()
        if val[:1] in (">", "|") or val == "":
            block = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt.startswith((" ", "\t")):
                    break
                block.append(nxt.strip())
            return " ".join(b for b in block if b)
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            return val[1:-1]
        for nxt in lines[i + 1:]:  # 不带引号的多行标量：缩进的续行接在后面
            if not nxt.strip() or not nxt.startswith((" ", "\t")):
                break
            val += " " + nxt.strip()
        return val
    return None


def check_skill(skill_dir):
    """返回 (错误, 警告, 提示) 三个列表和几项体积数字。"""
    err, warn, info = [], [], []
    path = skill_dir / "SKILL.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    body_lines = body.count("\n") + 1
    off = text.count("\n") - body.count("\n")  # 报行号用文件行号，不用正文相对行号
    stats = {"lines": body_lines, "bytes": len(text.encode("utf-8"))}

    if fm is None:
        err.append("没有 frontmatter：runtime 读不到 name 和 description，这个 skill 不会被发现")
        name = desc = None
    else:
        name, desc = read_field(fm, "name"), read_field(fm, "description")
    if fm is not None and not name:
        err.append("frontmatter 缺 name")
    elif name:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
            warn.append(f"name「{name}」不符合规范（小写字母、数字、连字符，≤64 字符）")
        if name != skill_dir.name:
            info.append(f"name「{name}」和目录名「{skill_dir.name}」不一致")
    if fm is not None and not desc:
        err.append("frontmatter 缺 description")
    elif desc:
        stats["desc_chars"] = len(desc)
        low = desc.lower()
        if len(desc) > 1024:
            err.append(f"description {len(desc)} 字符，超过 1024 上限")
        if len(desc) < 30:
            warn.append(f"description 只有 {len(desc)} 字符，说不清做什么和何时用")
        if not any(c in low for c in WHEN_CUES):
            warn.append("description 没写何时用（触发场景或触发词），agent 难以判断该不该加载")
        elif len(desc) > 250 and not any(c in low[:250] for c in WHEN_CUES):
            info.append("触发场景写在 description 第 250 字符之后，部分 runtime 会截断")
        if re.match(r"^(i |i'm |我可以|我能|我是|you can )", low):
            warn.append("description 用了第一或第二人称，应写成第三人称")

    if body_lines > 500:
        warn.append(f"正文 {body_lines} 行，超过 500 行；分支用到的细节应下沉到 references/")

    refs = sorted(set(REF_PATH.findall(body)))
    for ref in refs:
        if not (skill_dir / ref).exists():
            warn.append(f"引用的文件不存在：{ref}（若只是举例的路径可忽略）")
    for sub in ("references", "reference"):
        d = skill_dir / sub
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.is_file() and f.name not in body and not f.name.startswith("."):
                    info.append(f"{sub}/{f.name} 没有在 SKILL.md 里被提到，agent 不会去读它")

    lines = body.splitlines()
    for i, line in enumerate(lines):
        n = i + 1 + off
        if SECRET.search(line):
            err.append(f"第 {n} 行疑似写了密钥")
        if HOME_PATH.search(line):
            warn.append(f"第 {n} 行有个人目录的绝对路径，换台机器就失效，也泄露用户名")
        if RISKY.search(line):
            ctx = " ".join(lines[max(0, i - 1):i + 2])
            if not any(g in ctx for g in GUARD):
                warn.append(f"第 {n} 行有破坏性命令，上下一行内没有确认或禁止说明")
        if RUNTIME_LOCK.search(line):
            info.append(f"第 {n} 行出现绑定单一 runtime 的措辞（讲解或举例时属误报，需读上下文）")
        if UNFINISHED.search(line):
            info.append(f"第 {n} 行有未完成标记")
    for sub in ("references", "reference", "scripts"):  # 密钥和个人路径连同附带文件一起扫
        d = skill_dir / sub
        for f in sorted(d.rglob("*")) if d.is_dir() else []:
            if not f.is_file() or f.stat().st_size > 1_000_000 or "__pycache__" in f.parts:
                continue
            try:
                extra = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            rel = f.relative_to(skill_dir)
            if SECRET.search(extra):
                err.append(f"{rel} 里疑似写了密钥")
            if HOME_PATH.search(extra):
                warn.append(f"{rel} 里有个人目录的绝对路径")
    soft = sum(body.count(w) for w in SOFT_WORDS)
    if soft >= 3:
        info.append(f"软化措辞 {soft} 处（可以考虑、视情况等），执行时等于没说")

    tests = skill_dir / "test-prompts.json"
    if not tests.exists():
        info.append("没有 test-prompts.json，实测维度无从评起")
    else:
        try:
            items = json.loads(tests.read_text(encoding="utf-8"))
            n_hold = sum(1 for t in items if isinstance(t, dict) and t.get("split") == "holdout")
            stats["tests"] = len(items)
            if n_hold == 0:
                info.append(f"测试集 {len(items)} 条，没有留出集（split=holdout），无法查过拟合")
        except (ValueError, OSError):
            warn.append("test-prompts.json 不是合法 JSON")
    return err, warn, info, stats


def find_skills(paths):
    found = []
    for p in map(Path, paths):
        p = p.expanduser()
        if (p / "SKILL.md").is_file():
            found.append(p.resolve())
            continue
        for depth in (1, 2, 3):
            for f in p.glob("/".join(["*"] * depth) + "/SKILL.md"):
                parts = f.relative_to(p).parts[:-1]
                if any(x in SKIP_DIRS or x.startswith(".") for x in parts):
                    continue
                found.append(f.parent.resolve())
    return sorted(set(found))


def cmd_check(args):
    skills = find_skills(args.paths)
    if not skills:
        sys.exit("没找到 SKILL.md。传入一个 skill 目录，或装有多个 skill 的上级目录。")
    rows = []
    for s in skills:
        err, warn, info, stats = check_skill(s)
        rows.append({"skill": s.name, "path": str(s), "errors": err, "warnings": warn, "info": info, **stats})
    rows.sort(key=lambda r: (-len(r["errors"]), -len(r["warnings"]), r["skill"]))
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    print(f"体检 {len(rows)} 个 skill（证据等级 E0：只读文件，没有运行）\n")
    print(f"{'skill':<34}{'错误':>4}{'警告':>4}{'提示':>4}{'正文行':>7}{'描述字符':>8}")
    for r in rows:
        print(f"{r['skill'][:33]:<34}{len(r['errors']):>6}{len(r['warnings']):>6}{len(r['info']):>6}"
              f"{r['lines']:>9}{r.get('desc_chars', 0):>10}")
    detail = rows if len(rows) == 1 or args.verbose else [r for r in rows if r["errors"] or r["warnings"]][:args.top]
    for r in detail:
        print(f"\n■ {r['skill']}  {r['path']}")
        for tag, key in (("错误", "errors"), ("警告", "warnings"), ("提示", "info")):
            for msg in r[key]:
                print(f"  [{tag}] {msg}")
    if len(detail) < len(rows) and not args.verbose:
        print(f"\n只展开了前 {len(detail)} 个有错误或警告的；加 -v 看全部。")


def scrub(root, secrets):
    """抹掉产出里能看出来历的路径（产出目录、skill快照目录），评委才是真的盲评。"""
    both = set()
    for x in secrets:
        if x:
            both.update({x, x.replace("/private/", "/", 1) if x.startswith("/private/") else x})
    secrets = sorted(both, key=len, reverse=True)
    for f in root.rglob("*"):
        if not f.is_file() or f.stat().st_size > 2_000_000:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        cleaned = text
        for x in secrets:  # 连同路径后面的部分一起抹，不留 s0、s1 这类尾巴
            cleaned = re.sub(re.escape(x) + r"[^\s\"'`)>\]，。；]*", "<路径已隐去>", cleaned)
        if cleaned != text:
            f.write_text(cleaned, encoding="utf-8")


def cmd_pair(args):
    a_root, b_root, out = Path(args.a), Path(args.b), Path(args.out)
    tests = sorted(d.name for d in a_root.iterdir() if d.is_dir() and (b_root / d.name).is_dir())
    if args.tests:
        tests = [t for t in tests if t in set(args.tests.split(","))]
    if not tests:
        sys.exit("两组产出里没有同名的测试目录。每条测试的产出应放在 <组>/<测试id>/ 下。")
    key_path = Path(args.key)
    if out.resolve() in [key_path.resolve(), *key_path.resolve().parents]:
        sys.exit("密钥文件不能放在评委看得到的 --out 目录里。")
    rng = random.Random(args.seed)
    key = {}
    for j in range(1, args.judges + 1):
        jname = f"j{j}"
        key[jname] = {}
        for t in tests:
            a_is_first = rng.random() < 0.5
            key[jname][t] = {"A": "a" if a_is_first else "b", "B": "b" if a_is_first else "a"}
            for label, side in key[jname][t].items():
                dst = out / jname / t / label
                if dst.exists():
                    shutil.rmtree(dst)
                src = (a_root if side == "a" else b_root) / t
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("transcript.md", "__pycache__"))
                scrub(dst, [str(src.resolve()), str(src), f"{src.parent.parent.name}/{src.parent.name}/{t}", f"{src.parent.name}/{t}"]
                      + [str(Path(r).expanduser().resolve()) for r in args.redact] + [str(Path(r).expanduser()) for r in args.redact])
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"已为 {args.judges} 位评委、{len(tests)} 条测试生成盲评材料：")
    for j in key:
        print(f"  评委 {j} 只读这个目录：{out / j}")
    print(f"密钥在 {key_path}（a=旧版或裸跑，b=新版或带 skill）。计票前不要打开，也不要给评委。")


def cmd_tally(args):
    key = json.loads(Path(args.key).read_text(encoding="utf-8"))
    per_test, facts, problems = {}, [], []
    slight = decided = 0
    for jname, mapping in key.items():
        vf = Path(args.votes) / f"{jname}.json"
        if not vf.exists():
            sys.exit(f"缺评委 {jname} 的投票文件：{vf}")
        votes = json.loads(vf.read_text(encoding="utf-8"))
        seen = [v.get("test") for v in votes if isinstance(v, dict)]
        for t in mapping:
            if seen.count(t) != 1:
                problems.append(f"{jname} 对 {t} 的投票有 {seen.count(t)} 条，应为 1 条")
        for t in seen:
            if t not in mapping:
                problems.append(f"{jname} 投了不存在的测试 id：{t}")
        for v in votes:
            t = v.get("test")
            if t not in mapping:
                continue
            side = {"A": mapping[t]["A"], "B": mapping[t]["B"]}
            rec = per_test.setdefault(t, {"b": 0, "a": 0, "tie": 0, "chk_a": [], "chk_b": []})
            prefer = str(v.get("prefer", "")).strip().upper()
            if prefer not in ("A", "B", "TIE"):
                problems.append(f"{jname} / {t} 的 prefer 是「{v.get('prefer')}」，只能是 A、B 或 tie")
                continue
            rec[side[prefer] if prefer in side else "tie"] += 1
            if prefer in side:
                decided += 1
                slight += str(v.get("margin", "")).strip().lower() == "slight"
            got = {}
            for label in ("A", "B"):
                n = v.get(f"{label}_checks_passed")
                try:
                    got[label] = float(n)
                except (TypeError, ValueError):
                    pass
            if len(got) == 1 or (not got and (v.get("A_checks_passed") or v.get("B_checks_passed"))):
                problems.append(f"{jname} / {t} 的检查项通过数不是成对的数字")
            for label, n in got.items():
                rec["chk_" + side[label]].append(n)
            if str(v.get("fact_claim", "")).strip():
                facts.append(f"{jname} / {t}：{v['fact_claim']}")
    for t, r in per_test.items():
        if len(r["chk_a"]) not in (0, len(key)):
            problems.append(f"{t} 只有部分评委填了检查项通过数，倒退检测不可靠")
    if problems or not per_test:
        print("投票文件有问题，不出裁决。让对应评委补齐或重写后再计票：")
        for x in problems or ["没有任何有效投票"]:
            print("  - " + x)
        sys.exit(2)
    win = lose = tie = 0
    regress, split = [], []
    print("逐条结果（b=新版或带 skill，a=旧版或裸跑）")
    for t, r in sorted(per_test.items()):
        res = "胜" if r["b"] > r["a"] else "负" if r["a"] > r["b"] else "平"
        win, lose, tie = win + (res == "胜"), lose + (res == "负"), tie + (res == "平")
        chk = ""
        if r["chk_a"] and r["chk_b"]:
            ma, mb = statistics.median(r["chk_a"]), statistics.median(r["chk_b"])
            chk = f"  检查项通过 a={ma:g} b={mb:g}"
            if mb < ma:
                regress.append(t)
        if r["b"] and r["a"]:
            split.append(t)
        print(f"  {t}: {res}（票 b{r['b']} / a{r['a']} / 平{r['tie']}）{chk}")
    print(f"\n合计：{win} 胜 {tie} 平 {lose} 负")
    if any(r["chk_a"] for r in per_test.values()):
        sa = sum(statistics.median(r["chk_a"]) for r in per_test.values() if r["chk_a"])
        sb = sum(statistics.median(r["chk_b"]) for r in per_test.values() if r["chk_b"])
        print(f"检查项通过合计（各条取评委中位数）：a={sa:g} b={sb:g}；分母是这几条测试的检查项总数")
    if decided:
        print(f"选了边的 {decided} 票里，{slight} 票是 slight" + ("（多数只是略好）" if slight * 2 > decided else ""))

    shorter = None
    if args.old_skill and args.new_skill:
        o, n = Path(args.old_skill).stat().st_size, Path(args.new_skill).stat().st_size
        shorter = n < o
        print(f"SKILL.md 体积：{o} → {n} 字节（{(n - o) / o:+.0%}）")
    if shorter is None:
        kind = "多数胜" if win > lose else "多数负" if lose > win else "胜负相当" if win else "多数平"
        print(f"增益：{kind}（没给 --old-skill 和 --new-skill，按增益评审输出，不做棘轮裁决）")
        verdict = None
    elif regress:
        verdict, why = "revert", f"检查项倒退：{', '.join(regress)}"
    elif win > lose:
        verdict, why = "keep", "严格更好"
    elif win == lose and shorter:
        verdict, why = "keep", "效果打平且更短——平局归短的那版"
    elif win == lose:
        verdict, why = "revert", "效果打平又没有变短——没有证据的改动不保留"
    else:
        verdict, why = "revert", "更差"
    if verdict:
        print(f"裁决：{verdict}（{why}）")
    if abs(win - lose) <= 1 and split and not regress:
        print(f"提醒：胜负只差一条且评委有分歧（{', '.join(split)}）。这几条两版各重跑一次再裁，单次运行的波动足以翻盘。")
    if facts:
        print("\n⚠ 有评委提出可核实的事实性指控。先去验证，成立则以事实为准，不看票数：")
        for f in facts:
            print("  - " + f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="零 token 体检")
    c.add_argument("paths", nargs="+", help="skill 目录，或装有多个 skill 的目录")
    c.add_argument("--json", action="store_true")
    c.add_argument("-v", "--verbose", action="store_true", help="展开所有 skill 的明细")
    c.add_argument("--top", type=int, default=10)
    c.set_defaults(fn=cmd_check)
    p = sub.add_parser("pair", help="生成盲评材料")
    p.add_argument("--a", required=True, help="旧版或裸跑的产出目录，下面每条测试一个子目录")
    p.add_argument("--b", required=True, help="新版或带 skill 的产出目录")
    p.add_argument("--out", required=True, help="盲评材料输出目录（给评委看）")
    p.add_argument("--key", required=True, help="密钥文件路径（不能在 --out 里面）")
    p.add_argument("--judges", type=int, default=3)
    p.add_argument("--tests", help="只取这些测试 id，逗号分隔")
    p.add_argument("--redact", action="append", default=[], help="额外要从产出里抹掉的路径，如skill快照目录；可重复")
    p.add_argument("--seed", type=int, default=None)
    p.set_defaults(fn=cmd_pair)
    t = sub.add_parser("tally", help="计票并给出棘轮裁决")
    t.add_argument("--key", required=True)
    t.add_argument("--votes", required=True, help="目录，内含 j1.json、j2.json……")
    t.add_argument("--old-skill", help="旧版 SKILL.md，用于平局时比体积（比的是每次必读的 SKILL.md，不含 references）")
    t.add_argument("--new-skill", help="新版 SKILL.md")
    t.set_defaults(fn=cmd_tally)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
