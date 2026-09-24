# X17 orchestrator audit — DeepSeek V4.1 Flash Go pilot

The orchestrator launched `opencode --auto -m opencode-go/deepseek-v4.1-flash` in herdr pane `w2:p4D` with brief `local/muse/prompts/X17.md`. Before the brief could be read or a table written, the provider rejected the request:

> Upstream request failed: This Go model requires Global regions. Select Global in your workspace's Privacy settings to use it.

The same error appeared four times in the local OpenCode log for the pane session between 12:59:37 and 12:59:53 UTC. The orchestrator closed the pane to stop retries. No source, build, boot, device, project/global OpenCode configuration, account setting, or worker commit was changed. The model's task quality remains unmeasured. Brad approved Global regions; the available OpenCode CLI has no workspace Privacy command, so the console toggle is pending. Muse Contributor remains the routing choice meanwhile.
