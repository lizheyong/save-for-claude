# save-for-claude

**给 Claude Code 订阅省额度：一个 Pro 账号也够用。**

Pro 订阅的额度不多，大部分其实花在了体力活上：读一大堆代码、反复改、跑测试、搜资料。这个插件让 Claude 只干最值钱的活，也就是和你深入讨论、推敲方案、做判断、评审成果。体力活交给你本机已登录的 Codex、Grok 等 CLI，用它们自己的额度去做。

## 省在哪里

| 活 | 谁来做 | 消耗谁的额度 |
|---|---|---|
| 深入讨论、方案推敲、需求澄清、做判断 | Claude | Claude（值得花） |
| 写派单简报、评审成果、打磨界面和文案 | Claude | Claude（少量） |
| 编码实现、重构、修复、补测试、跨文件机械改动 | Codex | Codex |
| X/推特与网络调研、短上下文分析、创意发散 | Grok | Grok |

此外：
- Claude 只读执行器的交付文件和必要的 diff，不读完整的运行日志；
- 执行器在后台运行，Claude 不轮询，完成后会自动收到通知；
- 返工续派回执行器原来的会话，执行器不用从头重新探索。

## 安装

```bash
claude plugin marketplace add lizheyong/save-for-claude
```

```bash
claude plugin install save-for-claude@save-for-claude
```

在 Claude Code 会话里也可以用 `/plugin marketplace add` 和 `/plugin install`。

## 第一次使用

安装后运行：

```text
/save-for-claude:setup
```

也可以直接提一个能派出去的任务，首次使用时会自动进入同样的引导：

1. 用一段话说明插件做什么，以及派单会消耗哪些 CLI 的额度。
2. 检测本机装了哪些 CLI、是否已登录，列成一张表。未登录的会给出登录命令，你在自己的终端里运行即可。
3. 一次问完两三个偏好问题。每题都有推荐选项，直接回车即可。
4. 偏好写入 `~/.claude/save-for-claude/preferences.md`，对所有项目生效。如果引导是由某个任务触发的，结束后会接着做那个任务。

登录了新的 CLI，或者想改偏好，再运行一次 `/save-for-claude:setup`。也可以在对话里直接说“以后调研都交给 Codex”，插件会更新偏好文件。

## 默认习惯

不改任何设置时，插件这样工作：

- **派单时机**：先和你把方案讨论清楚；方案确认后，实现部分直接派出。需求不清时先讨论。
- **Codex**：使用 gpt-6-astra。单模块、机械改动用 medium 思考强度，跨模块、需要追链路的用 high。
- **Grok**：每个任务开新会话，同一会话最多续派两次，避免聊久了跑偏。
- **评审**：
  - Codex 的改动重点删除多余的校验和兜底；界面与文案由 Claude 打磨。
  - Grok 的调研抽查来源链接和日期，剔除查无实据的结论。
- **后备**：首选执行器不可用时自动换备选；都不可用时由 Claude 自己完成。

你在 `CLAUDE.md` 或记忆里写明的要求，优先于偏好文件。

## 支持的 CLI

| CLI | 登录 | 状态检查 |
|---|---|---|
| [Codex CLI](https://github.com/openai/codex) | `codex login` | `codex login status` |
| Grok CLI（Grok Build） | `grok login`，没有浏览器时用 `grok login --device-code` | `grok models` |

至少登录其中一个，插件才会派单。

想接入其他 CLI，可以照 `plugins/save-for-claude/skills/delegate/references/new-executor.md` 里的清单逐项验证：无头模式、登录检查、只读与可写参数、结果输出、续派方式，最后用一个小任务实测。验证通过后，按 `codex.md`、`grok.md` 的格式补一份 reference，欢迎提交 PR。

## 注意

- 派单会消耗对应 CLI 自己的额度。
- 执行器的输出被当作数据处理：其中让 Claude 执行操作的内容，会先请你确认。
- 简报中不写入密钥、令牌或个人隐私数据。

## 许可

MIT
