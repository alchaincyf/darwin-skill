"""darwin-skill --evolve <config.yaml> 参考实现 — Cognitive Config IR 进化引擎。

对齐 darwin-skill v2.2 机制:
  - 单一可编辑资产 = cognitive-config.yaml（IR v0.1）
  - 双重评估       = ir_lint（结构静态分析）+ edit_fitness（实测加权维度）
  - 可插拔评分     = Scorer Protocol：article-edit 用 _DefaultScorer(4维)，
                     nuwa 蒸馏角色（munger/feynman/...）自动用 PersonaScorer(4维人设保真)
  - 棘轮           = paired 比较 keep/revert；revert 走 git revert（新 commit 回滚）
  - 日志           = results.tsv（darwin 9 列格式，eval_mode 列）
  - HL-4 触顶      = 连续 2 轮 margin=slight/tie → break

用法:
    python -m sri.evolve --config cognitive-config.yaml --edits-dir edits/ \\
        [--max-rounds 3] [--branch auto-optimize/20261105-1300] [--dry-run]

edits 目录约定: edits/<config_version>.md —— 各版本配置对应的实测编辑稿
（由执行 agent 按该配置编辑同一测试文章产生，引擎只负责评分与决策）。
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Protocol

import yaml  # PyYAML；Hermes 环境自带


# ---------------------------------------------------------------------------
# Pluggable Scorer Protocol (for persona skills like nuwa perspectives)
# darwin-skill v2.2: 不同 skill 类型用不同评估维度；引擎只依赖该协议。
# ---------------------------------------------------------------------------
class Scorer(Protocol):
    """Scorer for edit_fitness evaluation. Different skill types use different dimensions."""
    @property
    def dimensions(self) -> dict[str, float]:
        """Returns {dimension_name: weight} for this scorer."""
        ...

    def score(self, text: str, ir: dict) -> Fitness:
        """Score edited text against the IR context. Returns Fitness with dimension scores."""
        ...


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------
@dataclass
class LintResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def score(self) -> float:
        """结构分: 每个 warning -0.05, 每个 error -0.2, clamp [0,1]"""
        return max(0.0, 1.0 - 0.05 * len(self.warnings) - 0.2 * len(self.errors))


@dataclass
class Fitness:
    dimensions: dict[str, float]     # 4 维得分
    weighted_sum: float
    lint_score: float
    total: float                     # = weighted_sum * lint_score（lint 作为 gate 乘子）

    def as_row(self) -> str:
        dims = " ".join(f"{k}={v:.3f}" for k, v in self.dimensions.items())
        return f"{dims} wsum={self.weighted_sum:.3f} lint={self.lint_score:.3f} total={self.total:.3f}"


@dataclass
class Mutation:
    op: str                 # 变异算子名
    target_dim: str         # 诊断出的加权短板维度
    rationale: str          # darwin Step 2「为什么改」
    edit: tuple             # (yaml_path尾串, old, new) 便于 diff 展示


# ---------------------------------------------------------------------------
# IR 读写 + 结构 lint（静态分析 = darwin 双重评估之一）
# ---------------------------------------------------------------------------
def load_ir(path: Path) -> dict:
    ir = yaml.safe_load(path.read_text(encoding="utf-8"))
    if ir.get("schema_version") != "0.1":
        raise ValueError(f"不支持的 schema_version: {ir.get('schema_version')}")
    if "cognitive_config" not in ir or "identity" not in ir["cognitive_config"]:
        raise ValueError("IR 缺少 cognitive_config.identity")
    return ir


def save_ir(ir: dict, path: Path) -> None:
    path.write_text(yaml.safe_dump(ir, allow_unicode=True, sort_keys=False),
                    encoding="utf-8")


def lint_ir(ir: dict) -> LintResult:
    """IR 规范 §5 冲突检测规则。"""
    errors: list[str] = []
    warnings: list[str] = []
    cc = ir.get("cognitive_config", {})

    if not cc.get("identity", {}).get("anchor"):
        errors.append("identity.anchor 缺失（原理一: 身份锚点必须存在）")

    beliefs = cc.get("beliefs", [])
    heuristics = cc.get("decision_heuristics", [])
    if len(beliefs) + len(heuristics) > 7:
        warnings.append(f"规则堆砌: beliefs+heuristics={len(beliefs)+len(heuristics)} > 7（工作空间容量）")

    for i, b in enumerate(beliefs):
        if re.match(r"^(不要|不许|禁止|别)", b):
            warnings.append(f"否定残留: beliefs[{i}] 以否定句开头，应转正面定义")

    neg = cc.get("workspace_hygiene", {}).get("negative_frames", []) or []
    if neg:
        warnings.append(f"negative_frames 非空({len(neg)})，建议转换为正面 beliefs")

    for h in heuristics:
        if not re.match(r"^if .+: .+$", h):
            warnings.append(f"锚定精度: 启发式非 'if ...: ...' 格式 → '{h[:30]}...'")

    dims = ir.get("evaluation_harness", {}).get("dimensions", [])
    weights = [d.get("weight", 0) for d in dims]
    if weights and max(weights) > 0.5:
        warnings.append(f"权重失衡: max weight={max(weights)} > 0.5（单维主导风险）")
    if dims and abs(sum(weights) - 1.0) > 1e-6:
        warnings.append(f"权重和={sum(weights):.3f} ≠ 1.0")

    # 容量卫生: beliefs+heuristics 超过 5 条时检查矛盾对（正面扫描: 同时要求相反倾向）
    text_all = " ".join(beliefs)
    if ("短" in text_all or "删" in text_all) and ("详细" in text_all or "补充" in text_all):
        warnings.append("一致性: beliefs 同时倾向删减与扩充，疑似矛盾对（原理三）")

    return LintResult(errors, warnings)


# ---------------------------------------------------------------------------
# 实测 fitness: 4 维代理指标（与 A/B 实验同一把尺，确定性可重复）
# ---------------------------------------------------------------------------
_CLICHES = ["总而言之", "在当今", "飞速发展", "不可或缺", "不断地", "极大地",
            "深刻地", "数字化", "日新月异", "立于不败之地", "迎接更加美好的未来", "可以看到"]
_CLAIMS = {
    "efficiency": ["效率", "节省", "省下", "时间"],
    "decision": ["决策", "参考", "数据"],
    "education": ["教育", "因材施教", "学生"],
    "job_fear": ["取代", "替代", "工作岗位", "抢工作", "位置"],
    "embrace": ["拥抱", "规避", "风险", "竞争力", "换位置"],
}
_WEIGHTS = {"correctness": 0.4, "elegance": 0.3, "cognitive_load": 0.2, "style_stability": 0.1}


def _sentences(t: str) -> list[str]:
    t = re.sub(r"^#.*$|^\*\*.*$", "", t, flags=re.M)
    return [s.strip() for s in re.split(r"[。！？!?]", t) if len(s.strip()) > 4]


def score_edit(text: str) -> Fitness:
    dims: dict[str, float] = {}
    # correctness: 原文关键论点保留率
    dims["correctness"] = sum(
        1 for kws in _CLAIMS.values() if any(k in text for k in kws)) / len(_CLAIMS)
    # elegance: 套话密度(60%) + 平均句长向 27.5 收敛(40%)
    sents = _sentences(text)
    n = max(len(sents), 1)
    avg = sum(len(s) for s in sents) / n
    cliche = max(0.0, 1.0 - sum(text.count(c) for c in _CLICHES) * 0.2)
    lensc = 1.0 - min(abs(avg - 27.5) / 40.0, 1.0)
    dims["elegance"] = 0.6 * cliche + 0.4 * lensc
    # cognitive_load: 短句率(50%) + ##结构(30%) + 列表(20%)
    short = sum(1 for s in sents if len(s) <= 35) / n
    dims["cognitive_load"] = (0.5 * short
                              + 0.3 * (1.0 if re.search(r"^## .+$", text, re.M) else 0.0)
                              + 0.2 * (1.0 if re.search(r"^[-*] |^\d+\.", text, re.M) else 0.0))
    # style_stability: 结构可复现性
    paras = [p for p in text.split("\n\n") if p.strip()]
    dims["style_stability"] = (0.3 * (1.0 if re.match(r"^# ", text) else 0.0)
                               + 0.3 * (1.0 if text.rstrip().endswith(("。", "！", "?", "？")) else 0.0)
                               + 0.2 * (1.0 if "**" in text else 0.0)
                               + 0.2 * (1.0 if 4 <= len(paras) <= 8 else 0.5))
    wsum = sum(dims[k] * _WEIGHTS[k] for k in _WEIGHTS)
    return Fitness(dims, wsum, lint_score=1.0, total=wsum)


# ---------------------------------------------------------------------------
# Persona Scorer (for nuwa distilled perspectives: munger/feynman/...)
# darwin-skill v2.2: 角色一致性 = 人设保真而非文章优雅。
# ---------------------------------------------------------------------------
class PersonaScorer:
    """Scorer for nuwa distilled perspectives (munger, feynman, etc.)."""
    @property
    def dimensions(self) -> dict[str, float]:
        return {
            "role_consistency": 0.35,    # 语气/词汇/句式是否稳定像该人
            "belief_alignment": 0.30,    # 编辑结果是否体现 IR 的 beliefs/heuristics
            "heuristic_relevance": 0.20, # 关键 heuristics 是否在文中被应用
            "cognitive_load": 0.15,      # 保留一点结构可读性
        }

    def score(self, text: str, ir: dict) -> Fitness:
        dims: dict[str, float] = {}
        cfg = ir.get("cognitive_config", {})
        beliefs = cfg.get("beliefs", [])
        heuristics = cfg.get("decision_heuristics", [])

        # role_consistency: 简单代理——文本词汇与信念/启发式的重叠率
        words = set(re.findall(r"[\u4e00-\u9fff\w]+", text.lower()))
        belief_words = set()
        for b in beliefs:
            belief_words.update(re.findall(r"[\u4e00-\u9fff\w]+", b))
        heuristic_words = set()
        for h in heuristics:
            heuristic_words.update(re.findall(r"[\u4e00-\u9fff\w]+", h))
        dims["role_consistency"] = min(
            len(words & belief_words) / max(len(belief_words), 1) * 0.6
            + len(words & heuristic_words) / max(len(heuristic_words), 1) * 0.4,
            1.0)

        # belief_alignment: 显式 belief 推断语义覆盖
        dims["belief_alignment"] = sum(
            1 for b in beliefs if any(w in text for w in b.split())
        ) / max(len(beliefs), 1)

        # heuristic_relevance: if-then heuristics 被触发/体现
        def _heuristic_applied(h: str) -> bool:
            if "if" in h and "then" in h or ":" in h:
                cond = h.split("if")[1].split(":")[0].split("then")[0]
                return any(w in text for w in cond.split())
            return False
        dims["heuristic_relevance"] = sum(
            1 for h in heuristics if _heuristic_applied(h)
        ) / max(len(heuristics), 1)

        # cognitive_load: 复用默认 scorer 的结构指标（轻量）
        sents = [s.strip() for s in re.split(r"[。！？!?]", text) if len(s.strip()) > 4]
        n = max(len(sents), 1)
        short = sum(1 for s in sents if len(s) <= 35) / n
        dims["cognitive_load"] = (0.5 * short
                                  + 0.3 * (1.0 if re.search(r"^## .+$", text, re.M) else 0.0)
                                  + 0.2 * (1.0 if re.search(r"^[-*] |^\d+\.", text, re.M) else 0.0))

        weights = self.dimensions
        wsum = sum(dims.get(k, 0) * weights.get(k, 0) for k in weights)
        return Fitness(dims, wsum, lint_score=1.0, total=wsum)


# ---------------------------------------------------------------------------
# Default scorer wrapper (article-edit 4 维) + registry
# ---------------------------------------------------------------------------
class _DefaultScorer:
    """Wrapper to make score_edit conform to Scorer protocol."""
    @property
    def dimensions(self) -> dict[str, float]:
        return _WEIGHTS.copy()

    def score(self, text: str, ir: dict) -> Fitness:
        return score_edit(text)


def get_scorer(ir: dict) -> Scorer:
    """Select scorer based on IR's cognitive_config.identity or skill field."""
    cfg = ir.get("cognitive_config", {})
    anchor = cfg.get("identity", {}).get("anchor", "").lower()
    skill = ir.get("skill", "").lower()
    # nuwa distilled perspectives
    if any(k in anchor for k in ["munger", "feynman", "charlie", "person_"]) or "perspective" in skill:
        return PersonaScorer()
    # default: article-edit style
    return _DefaultScorer()


# ---------------------------------------------------------------------------
# 诊断（darwin Step 1: 加权短板最大维度）
# ---------------------------------------------------------------------------
def diagnose(fit: Fitness, scorer: Scorer) -> tuple[str, float]:
    gaps = {k: w * (1.0 - fit.dimensions.get(k, 0)) for k, w in scorer.dimensions.items()}
    dim = max(gaps, key=gaps.get)
    return dim, gaps[dim]


# ---------------------------------------------------------------------------
# 变异算子库（darwin Step 2: 每轮取针对短板维度的一个具体方案）
# ---------------------------------------------------------------------------
def _next_version(v: str) -> str:
    m = re.match(r"^(.*-v)(\d+)(\.\d+)?$", v)
    if not m:
        return v + "-mut1"
    if m.group(3):  # x.y 形式 → 递增小数
        return f"{m.group(1)}{m.group(2)}.{int(float(m.group(3)[1:])) + 1}"
    return f"{m.group(1)}{int(m.group(2)) + 1}"


MUTATORS: dict[str, list[dict]] = {
    "cognitive_load": [
        {"op": "add_heuristic_sentence_cap",
         "inject": ("decision_heuristics",
                    "if 单句 > 35 字: 拆成两句，一句只说一件事"),
         "why": "短句率是 cognitive_load 的 50% 权重项；加句长硬约束直接抬升"},
        {"op": "add_belief_structure_externalize",
         "inject": ("beliefs",
                    "结构是给读者的外化工作空间：小标题先行，段落一句话立住一个论点"),
         "why": "## 结构占 cognitive_load 的 30%；把结构写进信念层"},
        {"op": "add_heuristic_para_split",
         "inject": ("decision_heuristics",
                    "if 段落 > 3 句: 拆段，一段只承载一个论点"),
         "why": "段落密度影响重读次数；与句长约束互补"},
    ],
    "elegance": [
        {"op": "add_belief_cliche_zero",
         "inject": ("beliefs",
                    "套话零容忍：出现「总而言之/在当今/深刻地」即为编辑失败信号"),
         "why": "elegance 的 60% 权重在套话密度；把禁词转为正面失败信号（原理二）"},
        {"op": "add_heuristic_cut_modifiers",
         "inject": ("decision_heuristics",
                    "if 句含两个以上「的」: 删修饰语或拆句"),
         "why": "平均句长向黄金值收敛靠删修饰，精确锚定优于模糊的『简洁』"},
    ],
    "correctness": [
        {"op": "add_heuristic_fact_lock",
         "inject": ("decision_heuristics",
                    "if 原句含事实/数据: 只重组结构不改措辞，拿不准就原样保留"),
         "why": "correctness 权重 0.4 最高；锁住事实句防止编辑引入失真"},
    ],
    "style_stability": [
        {"op": "add_belief_structure_template",
         "inject": ("beliefs",
                    "文章骨架固定：标题点观点，小节立论点，末句给转发理由"),
         "why": "style_stability 考结构可复现性；把骨架写成身份级信念"},
    ],
}


def _norm_heuristic(s: str) -> str:
    """归一化启发式/信念文本用于等价检测：去括号注释、去空白。"""
    s = re.sub(r"[（(].*?[)）]", "", s)
    return re.sub(r"\s+", "", s)


def mutate(ir: dict, target_dim: str, skip_ops: set[str], scorer: Optional[Scorer] = None) -> tuple[dict, Mutation]:
    """按诊断维度选第一个未用过且能注入新基因的变异算子；全部用过则回退到任意维度轮换。"""
    mutators = getattr(scorer, "mutators", MUTATORS)
    # 若目标维度无专用算子，自动降级到有算子的维度
    if target_dim not in mutators:
        available = [d for d in mutators if mutators[d]]
        if not available:
            raise RuntimeError("变异算子库为空")
        print(f"  ⚠️ 维度 '{target_dim}' 无专用算子，自动降级到 '{available[0]}'")
        target_dim = available[0]
    order = [target_dim] + [d for d in mutators if d != target_dim]
    for dim in order:
        for spec in mutators.get(dim, []):
            if spec["op"] in skip_ops:
                continue
            new_ir = copy.deepcopy(ir)
            key, item = spec["inject"]
            bucket = new_ir["cognitive_config"].setdefault(key, [])
            # 等价基因检测：防止措辞微差的重复条目（重复规则挤占工作空间）
            if any(_norm_heuristic(x) == _norm_heuristic(item) for x in bucket):
                skip_ops.add(spec["op"])
                continue
            bucket.append(item)
            # 升版本号 + parent 指针（可进化的血统链）
            prov = new_ir.setdefault("provenance", {})
            old_v = prov.get("config_version", "v0")
            prov["config_version"] = _next_version(old_v)
            prov["parent"] = old_v
            mut = Mutation(spec["op"], dim, spec["why"], (key, "", item))
            return new_ir, mut
    raise RuntimeError("变异算子库已耗尽")


# ---------------------------------------------------------------------------
# git 棘轮（keep=commit / revert=git revert 新 commit）
# ---------------------------------------------------------------------------
def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def _score_or_none(edits_dir: Path, version: str, ir: dict, scorer: Scorer) -> Optional[Fitness]:
    p = edits_dir / f"{version}.md"
    if not p.exists():
        return None
    fit = scorer.score(p.read_text(encoding="utf-8"), ir)
    fit.lint_score = lint_ir(ir).score
    fit.total = fit.weighted_sum * fit.lint_score
    return fit


# ---------------------------------------------------------------------------
# 主进化循环
# ---------------------------------------------------------------------------
def evolve(config_path: Path, edits_dir: Path, max_rounds: int,
           repo: Optional[Path], dry_run: bool) -> int:
    ir = load_ir(config_path)
    scorer = get_scorer(ir)
    base_lint = lint_ir(ir)
    if not base_lint.ok:
        print("❌ IR 结构错误（不可进化）:", *base_lint.errors, sep="\n   ")
        return 1
    print(f"初始 IR: {ir['provenance']['config_version']}  lint: "
          f"{len(base_lint.warnings)} warning / 0 error")
    print(f"Scorer: {scorer.__class__.__name__}  dims: {list(scorer.dimensions.keys())}")

    repo = repo or config_path.parent
    has_git = (repo / ".git").exists()
    if has_git and not dry_run:
        branch = datetime.now().strftime("auto-optimize/%Y%m%d-%H%M")
        _git(repo, "checkout", "-q", "-b", branch)
        print(f"分支: {branch}")

    tsv = repo / "results.tsv"
    if not tsv.exists():
        tsv.write_text("timestamp\tcommit\tskill\told_score\tnew_score\t"
                       "status\tdimension\tnote\teval_mode\n", encoding="utf-8")

    def log(commit: str, old: str, new: str, status: str, dim: str, note: str, mode: str):
        row = (f"{datetime.now().isoformat(timespec='minutes')}\t{commit}\t"
               f"{ir['skill']}\t{old}\t{new}\t{status}\t{dim}\t{note}\t{mode}\n")
        with tsv.open("a", encoding="utf-8") as f:
            f.write(row)

    version = ir["provenance"]["config_version"]
    cur_fit = _score_or_none(edits_dir, version, ir, scorer)
    eval_mode = "full_test" if cur_fit else "dry_run"
    if cur_fit:
        print(f"基线实测 [{version}]: {cur_fit.as_row()}")
    else:
        print(f"⚠️ edits/{version}.md 缺失 → dry_run（仅 lint，HL: dry_run>30% 评估失效）")
        cur_fit = Fitness({k: 0.0 for k in scorer.dimensions}, 0.0, base_lint.score, 0.0)

    skip: set[str] = set()
    slight_or_tie = 0          # HL-4 连续触顶计数
    for rnd in range(1, max_rounds + 1):
        dim, gap = diagnose(cur_fit, scorer)
        cand_ir, mut = mutate(ir, dim, skip, scorer)
        skip.add(mut.op)
        new_v = cand_ir["provenance"]["config_version"]
        print(f"\n— Round {rnd} | 短板: {dim}(gap={gap:.3f}) → 变异 {mut.op} → {new_v}")
        print(f"  理由: {mut.rationale}")

        cand_path = config_path.parent / f"cognitive-config-{new_v}.yaml"
        cand_fit = _score_or_none(edits_dir, new_v, cand_ir, scorer)

        if cand_fit is None:
            # 无实测稿 → dry_run：只做结构 lint gate，提示需要执行 agent 产出编辑稿
            cand_lint = lint_ir(cand_ir)
            print(f"  ⚠️ edits/{new_v}.md 缺失 → dry_run 结构检查: "
                  f"{len(cand_lint.warnings)} warning, lint {cand_lint.score:.2f}")
            log("dry-run", f"{cur_fit.total:.3f}", "-", "defer", dim,
                f"{mut.op} 需实测稿", "dry_run")
            save_ir(cand_ir, cand_path)
            print(f"  → 候选已写入 {cand_path.name}")
            print("  🛑 CHECKPOINT: 无实测稿无法 paired 决策 → 暂停。"
                  "请执行 agent 按候选配置产出编辑稿后重跑。")
            break

        # paired 比较: 同一把尺（确定性代理指标）量改前/改后 → noise=0
        delta = cand_fit.total - cur_fit.total
        margin = "clear" if abs(delta) >= 0.05 else "slight"
        verdict = "keep" if delta > 0 or (delta == 0 and cand_fit.lint_score >= cur_fit.lint_score) else "revert"
        print(f"  paired: {cur_fit.total:.3f} → {cand_fit.total:.3f} "
              f"(Δ={delta:+.3f}, margin={margin}) → {verdict.upper()}")
        print(f"    改后: {cand_fit.as_row()}")

        if verdict == "keep":
            old_fit = cur_fit          # 先捕获旧分，再推进基线（日志要用真实 old_score）
            ir = cand_ir
            version = new_v
            cur_fit = cand_fit
            save_ir(ir, config_path)   # 资产演进到最新（单文件棘轮）
            if cand_path.exists():
                cand_path.unlink()
            if has_git and not dry_run:
                _git(repo, "add", "-A")
                _git(repo, "-c", "user.email=hermes@local", "-c", "user.name=hermes",
                     "commit", "-qm",
                     f"evolve({ir['skill']}): {mut.op} -> {new_v} | "
                     f"paired Δ={delta:+.3f} {margin}")
                log(_git(repo, "rev-parse", "--short", "HEAD"),
                    f"{old_fit.total:.3f}", f"{cand_fit.total:.3f}",
                    "keep", dim, mut.op, eval_mode)
            else:
                log("local", f"{old_fit.total:.3f}", f"{cand_fit.total:.3f}",
                    "keep", dim, mut.op, eval_mode)
            if margin == "slight":
                slight_or_tie += 1
            else:
                slight_or_tie = 0
            if slight_or_tie >= 2:      # HL-4 触顶自动 break
                print("  HL-4: 连续 2 轮 slight → break")
                break
        else:
            if has_git and not dry_run:
                # darwin 规范: revert 用新 commit 回滚，不用 reset
                if cand_path.exists():
                    cand_path.unlink()
                save_ir(ir, config_path)  # 恢复基线内容
                _git(repo, "add", "-A")
                _git(repo, "-c", "user.email=hermes@local", "-c", "user.name=hermes",
                     "commit", "-qm", f"revert({ir['skill']}): {mut.op} 退步回滚")
                log(_git(repo, "rev-parse", "--short", "HEAD"),
                    f"{cur_fit.total:.3f}", f"{cand_fit.total:.3f}",
                    "revert", dim, mut.op, eval_mode)
            print("  → 已回滚（棘轮: 只保留改进）")
            break

    print(f"\n最终 IR: {ir['provenance']['config_version']}  fitness={cur_fit.total:.3f}")
    print(f"results.tsv: {tsv}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="sri.evolve", description="darwin --evolve: IR 进化引擎")
    ap.add_argument("--config", required=True, type=Path, help="cognitive-config.yaml 路径")
    ap.add_argument("--edits-dir", type=Path, help="实测编辑稿目录 (edits/<config_version>.md)")
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true", help="不创建分支/不 commit")
    a = ap.parse_args(argv)
    if not a.config.exists():
        print(f"❌ 配置不存在: {a.config}", file=sys.stderr)
        return 1
    edits = a.edits_dir or (a.config.parent / "edits")
    return evolve(a.config, edits, a.max_rounds, a.config.parent, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
