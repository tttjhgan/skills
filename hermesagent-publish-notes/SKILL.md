---
name: hermesagent-publish-notes
description: Distill knowledge learned during a Codex conversation into a reviewable Markdown note and submit it to the user's authenticated HermesAgent blog-ingestion API. Also publish approved standalone Markdown posts. Use when the user asks to publish, archive, sync, summarize-and-send, or send chat learnings to HermesAgent/Hermes Agent, including Chinese requests such as "发给 HermesAgent", "发布学习笔记", "发布博客", or "把聊天学到的内容同步到博客".
---

# HermesAgent Notes

Turn a conversation's durable technical learning into a source note for the SecurityClaw learning series. HermesAgent later analyzes and publishes the note; do not claim that publication has completed after the HTTP submission.

## Workflow

1. Extract only durable, evidenced conclusions from the current conversation. Do not invent facts, outcomes, sources, or commands.
2. Remove secrets, access tokens, private hostnames/IPs, personal data, and exploit-ready instructions unless the user explicitly authorizes their inclusion and it is safe to publish.
3. Produce a concise Markdown draft with a clear title, a short context section, key conclusions, and practical takeaways. Preserve useful code only when it is complete and safe.
4. Choose one chapter: `rag-engine`, `langgraph`, `skill-system`, `llm-layer`, or `tuning`. For a genuinely new subject, use a short lowercase hyphenated chapter name.
5. Show the draft and selected chapter before submission unless the user has explicitly requested immediate publishing in the same instruction.
6. Save the approved draft as a UTF-8 Markdown file and run the bundled script with `--send`. Report the returned HTTP status and response body. Clearly distinguish accepted-for-processing from live-on-blog.

## Submission

Set `HERMESAGENT_NOTES_TOKEN` in the local user environment. Never place the token in a command, note, blog post, or skill file. Use `scripts/submit_note.py`; it prints the request body without sending by default.

```powershell
python "$env:USERPROFILE\.codex\skills\hermesagent-publish-notes\scripts\submit_note.py" `
  --title "RAG retrieval evaluation" `
  --chapter rag-engine `
  --content-file .\note.md `
  --tags rag,retrieval,evaluation `
  --send
```

Override the endpoint only when the user provides a replacement:

```powershell
$env:HERMESAGENT_NOTES_ENDPOINT = "http://host:7800/api/notes"
```

The configured default is `http://49.232.56.77:7800/api/notes`.

## Standalone Posts

Use `scripts/publish_post.py` for an approved ordinary blog post. It also requires `HERMESAGENT_NOTES_TOKEN` and previews by default. `draft` is false unless `--draft` is supplied; that means `--send` creates a public post.

```powershell
python "$env:USERPROFILE\.codex\skills\hermesagent-publish-notes\scripts\publish_post.py" `
  --title "Article title" `
  --content-file .\article.md `
  --tags codex,automation `
  --categories "SecurityClaw" `
  --send
```

## Failure Handling

Treat timeouts, connection failures, and non-2xx responses as failed submissions. Keep the local draft and state that it was not accepted. Do not retry automatically against the public endpoint; report the error and ask the user whether to retry.
