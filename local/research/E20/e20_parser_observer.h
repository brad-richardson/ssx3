#pragma once
#include <stdint.h>
typedef struct E20ParserStats {
    uint64_t parseCalls, offered, consumed, packets, packetBytes;
    uint64_t sendCalls, sendEof, receiveCalls, frames, errors;
    uint64_t pending, returned, textTruncated, payloadTruncated, ioErrors;
    uint64_t backendParse, backendSend, backendReceive, bindingChecks, recursionGuards;
} E20ParserStats;
/* Evidence-only exports. They do not invoke the parser or guest runtime. */
typedef void (*E20Snapshot)(E20ParserStats *);
typedef void (*E20Mark)(const char *, uint64_t);
