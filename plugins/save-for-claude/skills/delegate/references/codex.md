# Codex CLI

## 特点

- 长处：执行稳定，肯追链路、跑测试，适合需求清楚的编码实现、重构、修复和补测试。
- 短板：界面审美、中文文案、与人沟通较弱；倾向添加多余的校验和防御代码，简报里写明“只在系统边界做必要校验”，评审时重点删减。

## 登录检查

```bash
codex login status < /dev/null
```

## 调用

```bash
codex exec -C <repo> -s workspace-write -o /tmp/save-for-claude/<任务名>/result.md - \
  < /tmp/save-for-claude/<任务名>/brief.md > /tmp/save-for-claude/<任务名>/run.log 2>&1
```

- `-s workspace-write`：可改工作目录；只读调研用 `-s read-only`。
- `-o`：把最终回复写入文件，评审时只读这个文件，不读完整日志。
- 模型与思考强度按偏好文件传入：`-m <模型>`、`-c model_reasoning_effort=<low|medium|high>`。偏好写明“使用 Codex 默认配置”时省略这两个参数，沿用 `~/.codex/config.toml`。
- 不在 git 仓库里运行时加 `--skip-git-repo-check`。
- 会话 id 在 `run.log` 开头的 `session id:` 行。

## 返工

```bash
codex exec resume <session id> -o /tmp/save-for-claude/<任务名>/result-2.md - \
  < /tmp/save-for-claude/<任务名>/fix.md > /tmp/save-for-claude/<任务名>/run-2.log 2>&1
```

## 评审

```bash
codex exec review
```

可作为 Claude 改动的第二意见。
