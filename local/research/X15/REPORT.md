# X15 — dense Qwen bounded source trial (orchestrator audit)

**No accepted table.** The first pane was stopped after the orchestrator found that its pinned excerpt omitted the SMODE2 bitfield and two renderer assignments; it had read the brief but not the excerpt. The corrected 11,013-byte excerpt is committed at SHA-256 `eac602143522d2ec2fe3c6b062070ee822c32a5fecd258400a9e66a1a102c146`.

The corrected dense Qwen pane read only its brief and excerpt, then remained in visible thinking for about four minutes without writing the required early `rows.tsv` or `REPORT.md`. The orchestrator stopped it at that file-delivery gate, before the eight-minute overall cap. Visible context remained about 13.5k. No LSP call, checker result, source edit, build, boot, device action, worker commit or push was observed. There is no accuracy score. A short-thinking-budget retry would test whether the delay is mostly pre-output reasoning.
