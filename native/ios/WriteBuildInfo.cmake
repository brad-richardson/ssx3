# Executed after linking, so this is the binary's build time, not configure time.
string(TIMESTAMP BUILT_AT "%Y-%m-%dT%H:%M:%SZ" UTC)
file(WRITE "${OUTPUT}" "{\"build_id\":\"${BUILD_ID}\",\"built_at\":\"${BUILT_AT}\"}\n")
