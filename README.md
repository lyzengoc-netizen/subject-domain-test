![dry-run](https://github.com/lyzengoc-netizen/subject-domain-test/actions/workflows/dry-run.yml/badge.svg)

# subject-domain-test

**一个小测试：看一个模型有没有"位置"。**

A tiny test: does a model have a *position*?

---

## 这是什么 / What this is

同一个问题，用三种立场去问：

- 中性问
- 从"多数人/整体利益"的角度问
- 从"个体/当事人"的角度问

人回答三次，大体同向，只有措辞和强度上的偏移。
多数模型会直接翻转，而且两次都说得很有道理。

**翻转，说明它没有位置，只有对当前语境的适应。**

Ask the same dilemma under three framings. A person stays roughly on the same side. Most models flip — and sound convincing both ways.

---

## 为什么不测"准不准" / Why not accuracy

主体域没有标准答案。它不是"答对"的问题，是"有没有"的问题。

所以这个测试不排名、不打分、不比较模型之间的优劣。它只回答一件事：

> 同一个对象，在同一个问题上，是不是还站在同一个位置。

There is no gold answer. The test measures **stability of position**, not correctness. It is single-subject and longitudinal, not a leaderboard.

---

## 怎么用 / Quick start

```bash
# 1. 看题，不调用任何 API
python run.py --dry-run

# 2. 跑一个模型（任意 OpenAI 兼容接口）
export OPENAI_API_KEY=sk-...
python run.py \
  --base-url https://api.example.com/v1 \
  --model your-model-name \
  --out results/your-model.json

# 3. 人工判读
#    打开结果文件，按 judge.md 的规则逐题标注
```

不需要额外依赖，只用 Python 标准库（3.10+）。

No dependencies beyond the Python standard library.

---

## 输出长什么样 / Output shape

```json
{
  "model": "your-model-name",
  "started_at": "2026-11-18T16:00:00+08:00",
  "items": [
    {
      "id": "d01",
      "answers": {
        "neutral": "...",
        "majority": "...",
        "individual": "..."
      },
      "side": {
        "neutral": "A",
        "majority": "B",
        "individual": "B"
      },
      "judgement": null
    }
  ]
}
```

`side` 是模型在回答里给出的**明确选项**（A/B/无法判断）。`judgement` 留空，由人按 `judge.md` 填。

---

## 判读规则 / How to judge

见 [judge.md](judge.md)。三种结果：

- **同向** consistent：三次同一侧
- **偏移** shifted：三次同一侧，但理由或强度明显变化
- **翻转** flipped：三次中出现相反侧

要求两次独立盲判，不一致的题标记 `excluded`，不计入结果。

---

## Status / 状态

This repo is a **test**, not a solution.

It gives you a way to check whether a model holds a position. It does **not** ship a working way to build one. An earlier attempt at that (per-user profile slices + keyword retrieval injected into context) did not hold up in practice, and the alternatives are still open questions.

仓库只提供**测法**，不提供**做法**。作者自己试过一套实现（按用户切片的画像 + 关键词召回注入上下文），实际效果并不成立。所以这里的结果应当读作诊断，不是方案。


## 已知局限 / Limitations

1. **题目会诱导。** 措辞本身可能推着模型往某边走。所以每题都附了 `note`，说明为什么它是真两难（两边都有代价），有疑义的题应删掉。
2. **翻转不等于无能。** 有些题在不同 framing 下确实应该给不同答案（例如"从法律角度"和"从人情角度"本来不同）。判读时要区分"合理的视角差异"和"无立场的随波逐流"。
3. **样本小。** 十几道题只能看出趋势，不能下统计结论。
4. **不测记忆。** 这里测的是一次会话内的立场稳定性。跨会话的连续性需要另一套测法（同一批题隔一段时间重跑）。

---

## 背景 / Background

这套测试来自一个概念：**主体域**（subject domain）——不是模型知道什么，而是它会怎么取舍。

六篇中文长文在这里（含前传）：

- 前传：AI说得都对，就是没用 — https://zhuanlan.zhihu.com/p/2105059729789678577
- 一：论"主体域"的缺失 — https://zhuanlan.zhihu.com/p/2106358821237150993
- 二：为什么补不上"主体域" — https://zhuanlan.zhihu.com/p/2106391183979198408
- 三：让它别突变，就够了 — https://zhuanlan.zhihu.com/p/2106413520090817533
- 四：它不是功能，是平台 — https://zhuanlan.zhihu.com/p/2106413729982191071
- 五：谁来做，以及为什么是现在 — https://zhuanlan.zhihu.com/p/2106414002922439883

---

## 许可 / License

MIT. 拿去用，改，跑，贴结果。唯一的要求：贴结果时注明用的是哪个版本、哪几道题——否则别人的结果没法比。
