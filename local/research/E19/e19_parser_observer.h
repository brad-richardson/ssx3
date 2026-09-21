#pragma once
#include <stdint.h>
typedef struct E19ParserStats {
    uint64_t parseCalls, offered, consumed, packets, packetBytes;
    uint64_t sendCalls, sendEof, receiveCalls, frames, errors;
    uint64_t pending, returned, textTruncated, payloadTruncated, ioErrors;
} E19ParserStats;
/* Evidence-only exports. They do not invoke the parser or guest runtime. */
typedef void (*E19Snapshot)(E19ParserStats *);
typedef void (*E19Mark)(const char *, uint64_t);
