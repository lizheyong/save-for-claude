# 首次引导

偏好文件不存在，或用户要求重新设置时执行。整个过程控制在一两轮对话内完成；由某个任务触发时，引导结束后直接继续那个任务。

## 1. 一段话说明

用三四句话告诉用户：
- 这个插件做什么：给 Claude 订阅省额度。Claude 只做思考、讨论、判断和评审，编码执行、调研等体力活派给本机的 Codex、Grok 等 CLI。
- 派单会消耗对应 CLI 自己的额度。
- 接下来会检测本机环境，并问两三个偏好问题。

## 2. 检测本机环境

依次运行，全部用 `< /dev/null` 关闭 stdin：

```bash
for c in codex grok gemini; do command -v "$c" >/dev/null && echo "installed: $c"; done
```

```bash
codex login status < /dev/null
```

```bash
grok models < /dev/null
```

只对已安装的 CLI 检查登录。把结果整理成一张表告诉用户：CLI、是否安装、是否登录、能承担的任务。

未登录的 CLI 给出登录命令，请用户在自己的终端里运行（登录需要浏览器交互，Claude 不代为执行）：
- Codex：`codex login`
- Grok：`grok login`；没有浏览器时用 `grok login --device-code`
- 其他 CLI：按 `new-executor.md` 的清单验证后再启用。

未安装的 CLI 只简单提一句可选安装，不展开。一个可用执行器都没有时，说明插件暂时不会派单，引导到此结束，不写偏好文件。

## 3. 询问偏好

用提问工具一次问完，每题第一个选项是默认偏好（标注“推荐”）：

1. 派单时机：方案确认后直接派（推荐）／每次派单前先问我。
2. Codex 模型（Codex 可用时才问）：gpt-6-astra，按任务难度选 medium 或 high（推荐）／使用 Codex 自己的默认配置。
3. 调研任务（Grok 可用时才问）：交给 Grok（推荐）／交给 Codex／Claude 自己做。

用户已经在 `CLAUDE.md` 或对话中表达过的偏好，不再重复询问。

## 4. 写入并确认

以 `preferences.md` 中的默认偏好为底，按回答修改：未启用或未登录的执行器标为“未启用”，再写入 `~/.claude/save-for-claude/preferences.md`。

最后用一两句话告诉用户：
- 已启用哪些执行器，各自负责什么；
- 随时可以直接说“以后调研交给 Codex”这类话来改偏好，或运行 `/save-for-claude:setup` 重新设置；
- 登录了新的 CLI 后，运行 `/save-for-claude:setup` 重新检测即可启用。
