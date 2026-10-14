# Grok CLI（Grok Build）

## 特点

- 长处：内置 X 搜索工具（关键词、语义、用户、帖子串）和网络搜索，适合 X/推特与网络近期信息调研；短上下文的分析理解和创意发散也不错；单次调用便宜。
- 短板：会话拉长后容易跑偏、产生幻觉。每个任务开新会话，同一会话最多续派一两次；调研结论要求附链接和日期，评审时抽查。

## 登录检查

```bash
grok models < /dev/null
```

输出含 `You are not authenticated` 时未登录，请用户运行 `grok login`。登录过期时，这次检查会让 Grok 清掉失效凭据，属正常现象。

## 调用

调研和创意任务在空的临时目录里运行，避免碰到项目文件：

```bash
mkdir -p /tmp/save-for-claude/<任务名>/work
grok --cwd /tmp/save-for-claude/<任务名>/work --prompt-file /tmp/save-for-claude/<任务名>/brief.md \
  --output-format json < /dev/null > /tmp/save-for-claude/<任务名>/result.json 2>/tmp/save-for-claude/<任务名>/run.log
```

只读分析某个仓库：

```bash
grok --cwd <repo> --permission-mode plan --prompt-file <brief.md> --output-format json < /dev/null > <result.json>
```

- `--output-format json` 的结果对象：`text` 是回答，`sessionId` 用于续派，`usage` 和 `total_cost_usd` 是用量与花费。评审时只读 `text`：

  ```bash
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['text']);print('session',d['sessionId'],'cost',d['total_cost_usd'])" <result.json>
  ```

- `--max-turns <N>` 限制回合数，防止长时间发散。
- 模型按偏好文件传入 `-m <模型>`，未指定时沿用 Grok 默认配置；可选值见 `grok models`。

## 续派

```bash
grok -r <sessionId> --prompt-file <fix.md> --output-format json < /dev/null > <result-2.json>
```
