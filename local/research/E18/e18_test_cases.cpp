        tc.Run("MPEG non-stream R1 delivers in registration order on the caller", [](TestCase &t)
        {
            const auto p = runNonStreamProbe(0u, 0u, true);
            t.IsTrue(p.setup, "fixture entries and observer must bind");
            t.IsTrue(p.delivered == std::vector<uint32_t>{11u, 22u}, "only matching, bound callbacks should run once in order");
            t.IsTrue(p.args && p.wordOnly, "callback arguments and only cbData word0 must be initialized");
            t.IsTrue(p.ownership && p.saved, "caller thread, stack, and 128-bit saved registers must survive");
            t.IsTrue(p.blocked && p.freed, "no-input request must wait after callback buffers are freed");
        });

        tc.Run("MPEG non-stream R2 re-enters AddBs without holding the MPEG lock", [](TestCase &t)
        {
            const auto p = runNonStreamProbe(16u);
            t.IsTrue(p.setup && p.delivered == std::vector<uint32_t>{11u}, "registered callback should dispatch once");
            t.Equals(p.copied, 16u, "AddBs re-entry must return the delivered byte count");
            t.IsTrue(p.blocked && p.resumed == 0u, "input without a decoded frame must not complete GetPicture");
            t.IsTrue(p.ownership && p.saved && p.freed, "re-entry must preserve the caller and release callback data");
        });

        tc.Run("MPEG non-stream R3 resumes GetPicture after delivered input decodes", [](TestCase &t)
        {
            const auto p = runNonStreamProbe(240u);
            t.IsTrue(p.setup && p.delivered == std::vector<uint32_t>{11u}, "one input callback should deliver the authored MPEG frames");
            t.Equals(p.copied, 240u, "AddBs must accept the complete MPEG-2 fixture");
            t.Equals(p.resumed, 1u, "GetPicture must resume its caller after callback completion");
            t.Equals(p.result, 0, "the resumed picture request should succeed");
            t.IsTrue(p.width == 16u && p.height == 16u && p.pixel != 0u, "a decoded 16x16 picture must reach guest memory");
            t.IsTrue(p.ownership && p.saved && p.freed, "decoded-frame return must preserve ownership and release callback data");
        });

        tc.Run("MPEG non-stream R4 ignores valid-no-input callback return values", [](TestCase &t)
        {
            for (uint32_t value : {0u, 1u, 0xFFFFFFFFu})
            {
                const auto p = runNonStreamProbe(0u, value);
                t.IsTrue(p.setup && p.delivered == std::vector<uint32_t>{11u}, "the input request should dispatch exactly once");
                t.IsTrue(p.blocked && p.resumed == 0u && p.copied == 0u, "v0 alone must never imply input, EOF, or completion");
                t.IsTrue(p.saved && p.freed, "no-input return must restore its parent and release cbData");
            }
        });

        tc.Run("MPEG non-stream R5 invalidates pending callbacks on delete and reset", [](TestCase &t)
        {
            for (int teardown : {1, 2})
            {
                const auto p = runNonStreamProbe(0u, 0u, false, teardown);
                t.IsTrue(p.setup && p.pendingAtTeardown, "teardown must run after invocation attachment but before guest dispatch");
                t.IsTrue(p.delivered.empty(), "an invalidated callback must never enter guest code");
                t.Equals(p.resumed, 1u, "teardown must resume the suspended GetPicture caller");
                t.Equals(p.result, -425, "cancelled request must return KE_WAIT_DELETE");
                t.IsTrue(p.saved && p.freed, "cancellation must preserve its parent and release cbData in onComplete");
            }
        });

        tc.Run("MPEG non-stream R6 leaves stream callbacks to the existing Demux path", [](TestCase &t)
        {
            const auto p = runNonStreamProbe(0u, 0u, false, 0, true);
            t.IsTrue(p.setup && p.delivered.empty(), "GetPicture must not select a stream callback with the same type");
            t.IsTrue(p.blocked && p.resumed == 0u && p.saved, "an unmatched input request must retain its typed wait");
            // The existing Demux video/audio/EOF/reset/create stream test stays unchanged.
        });

