    // Non-title, scheduler-driven MPEG requests. No callback is invoked manually.
    constexpr uint32_t kNonStreamMain = 0x00125500u;
    constexpr uint32_t kNonStreamResume = 0x00125510u;
    constexpr uint32_t kNonStreamCallback = 0x00125520u;
    constexpr uint32_t kNonStreamObserver = 0x00125530u;
    constexpr uint32_t kNonStreamDelete = 0x00125540u;
    constexpr uint32_t kNonStreamHandle = 0x00127000u;
    constexpr uint32_t kNonStreamImage = 0x00150000u;
    constexpr uint32_t kNonStreamInput = 0x00126000u;
    constexpr uint32_t kNonStreamHeap = 0x00800000u;
    constexpr uint32_t kNonStreamStack = 0x01E00000u;

    struct NonStreamProbe
    {
        std::vector<uint32_t> delivered;
        R5900Context parent{};
        unsigned feedBytes = 0u;
        unsigned copied = 0u;
        unsigned resumed = 0u;
        uint32_t callbackResult = 0u;
        int result = -999;
        int teardown = 0; // 1: delete; 2: reset, before pending callback dispatch.
        bool args = true;
        bool ownership = true;
        bool wordOnly = true;
        bool saved = true;
        bool blocked = false;
        bool freed = false;
        bool pendingAtTeardown = false;
        bool setup = true;
        uint32_t width = 0u, height = 0u, pixel = 0u;
    };
    NonStreamProbe gNonStream;

    bool nonStreamSaved(const R5900Context &ctx)
    {
        for (int reg : {16, 17, 18, 19, 20, 21, 22, 23, 28, 29, 30, 31})
        {
            if (std::memcmp(&ctx.r[reg], &gNonStream.parent.r[reg], sizeof(ctx.r[reg])) != 0)
                return false;
        }
        return true;
    }

    void nonStreamCheckFreed(PS2Runtime *runtime)
    {
        const uint32_t reused = runtime->guestMalloc(4u, 4u);
        gNonStream.freed = reused == kNonStreamHeap;
        runtime->guestFree(reused);
    }

    void nonStreamMain(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
    {
        setRegU32(*ctx, 4, kNonStreamHandle);
        setRegU32(*ctx, 5, kNonStreamImage);
        setRegU32(*ctx, 31, kNonStreamResume);
        ctx->pc = kNonStreamResume; // The generated GetPicture wrapper supplies this continuation.
        gNonStream.parent = *ctx;
        if (gNonStream.teardown != 0)
        {
            int oldPriority = 0;
            gNonStream.setup &= runtime->eeScheduler().changePriority(1, 20, false, oldPriority) == 0;
        }
        ps2_stubs::sceMpegGetPicture(rdram, ctx, runtime);
    }

    void nonStreamCallback(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
    {
        const uint32_t cbData = ::getRegU32(ctx, 5);
        gNonStream.delivered.push_back(::getRegU32(ctx, 6));
        gNonStream.args &= ::getRegU32(ctx, 4) == kNonStreamHandle &&
                          cbData == kNonStreamHeap && Ps2FastRead32(rdram, cbData) == 1u;
        gNonStream.wordOnly &= Ps2FastRead32(rdram, cbData + 4u) == 0xA5A5A5A5u;
        gNonStream.ownership &= runtime->eeScheduler().currentThreadId() == 1 &&
                               ::getRegU32(ctx, 29) == kNonStreamStack;
        if (gNonStream.feedBytes != 0u)
        {
            setRegU32(*ctx, 4, kNonStreamHandle);
            setRegU32(*ctx, 5, kNonStreamInput);
            setRegU32(*ctx, 6, gNonStream.feedBytes);
            ps2_stubs::sceMpegAddBs(rdram, ctx, runtime);
            gNonStream.copied += ::getRegU32(ctx, 2);
        }
        // A callback's scratch context cannot replace the suspended caller.
        ctx->r[16] = _mm_set_epi64x(0x1122334455667788LL, 0x8877665544332211ULL);
        setRegU32(*ctx, 2, gNonStream.callbackResult);
        ctx->pc = 0u;
    }

    void nonStreamResume(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
    {
        ++gNonStream.resumed;
        gNonStream.result = getRegS32(*ctx, 2);
        gNonStream.saved &= nonStreamSaved(*ctx);
        gNonStream.width = Ps2FastRead32(rdram, kNonStreamHandle);
        gNonStream.height = Ps2FastRead32(rdram, kNonStreamHandle + 4u);
        gNonStream.pixel = Ps2FastRead32(rdram, kNonStreamImage);
        nonStreamCheckFreed(runtime);
        ctx->pc = 0u;
        runtime->requestStop();
    }

    void nonStreamObserve(uint8_t *, R5900Context *ctx, PS2Runtime *runtime)
    {
        const GuestThread *owner = runtime->eeScheduler().thread(1);
        gNonStream.blocked = owner && owner->wait.reason == EeWaitReason::Mpeg;
        gNonStream.saved &= owner && nonStreamSaved(owner->context);
        nonStreamCheckFreed(runtime);
        ctx->pc = 0u;
        runtime->requestStop();
    }

    void nonStreamTeardown(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
    {
        const GuestThread *owner = runtime->eeScheduler().thread(1);
        gNonStream.pendingAtTeardown = owner && owner->invocations.size() == 1u &&
                                      gNonStream.delivered.empty();
        setRegU32(*ctx, 4, kNonStreamHandle);
        if (gNonStream.teardown == 1)
            ps2_stubs::sceMpegDelete(rdram, ctx, runtime);
        else
            ps2_stubs::sceMpegReset(rdram, ctx, runtime);
        ctx->pc = 0u;
    }

    NonStreamProbe runNonStreamProbe(unsigned feedBytes = 0u, uint32_t callbackResult = 0u,
                                     bool ordered = false, int teardown = 0, bool streamOnly = false)
    {
        PS2Runtime runtime;
        std::vector<uint8_t> rdram(PS2_RAM_SIZE, 0u);
        ps2_stubs::resetMpegStubState();
        ps2_stubs::notifyMpegCdStreamStart();
        runtime.configureGuestHeap(kNonStreamHeap, kNonStreamHeap + 0x10000u);
        std::memset(rdram.data() + kNonStreamHeap, 0xA5, 64u);
        gNonStream = NonStreamProbe{};
        gNonStream.feedBytes = feedBytes;
        gNonStream.callbackResult = callbackResult;
        gNonStream.teardown = teardown;
        for (auto entry : {std::pair<uint32_t, PS2Runtime::RecompiledFunction>{kNonStreamMain, nonStreamMain},
                           {kNonStreamResume, nonStreamResume}, {kNonStreamCallback, nonStreamCallback},
                           {kNonStreamObserver, nonStreamObserve}, {kNonStreamDelete, nonStreamTeardown}})
            gNonStream.setup &= runtime.registerFunction(entry.first, entry.second);

        // Four authored 16x16 red MPEG-2 I-frames (ffmpeg lavfi color, g=1, bf=0).
        // This decoder integration case requires the FFmpeg-enabled host build.
        static constexpr uint8_t inputFrames[] = {
            0x00u, 0x00u, 0x01u, 0xB3u, 0x01u, 0x00u, 0x10u, 0x13u, 0xFFu, 0xFFu, 0xE0u, 0x18u,
            0x00u, 0x00u, 0x01u, 0xB5u, 0x14u, 0x8Au, 0x00u, 0x01u, 0x00u, 0x00u, 0x00u, 0x00u,
            0x01u, 0xB8u, 0x00u, 0x08u, 0x00u, 0x40u, 0x00u, 0x00u, 0x01u, 0x00u, 0x00u, 0x0Fu,
            0xFFu, 0xF8u, 0x00u, 0x00u, 0x01u, 0xB5u, 0x8Fu, 0xFFu, 0xF3u, 0x41u, 0x80u, 0x00u,
            0x00u, 0x01u, 0x01u, 0x13u, 0xF2u, 0x14u, 0xA5u, 0x2Fu, 0x99u, 0xBFu, 0x70u, 0x80u,
            0x00u, 0x00u, 0x01u, 0xB3u, 0x01u, 0x00u, 0x10u, 0x13u, 0xFFu, 0xFFu, 0xE0u, 0x18u,
            0x00u, 0x00u, 0x01u, 0xB5u, 0x14u, 0x8Au, 0x00u, 0x01u, 0x00u, 0x00u, 0x00u, 0x00u,
            0x01u, 0xB8u, 0x00u, 0x08u, 0x00u, 0xC0u, 0x00u, 0x00u, 0x01u, 0x00u, 0x00u, 0x0Fu,
            0xFFu, 0xF8u, 0x00u, 0x00u, 0x01u, 0xB5u, 0x8Fu, 0xFFu, 0xF3u, 0x41u, 0x80u, 0x00u,
            0x00u, 0x01u, 0x01u, 0x13u, 0xF2u, 0x14u, 0xA5u, 0x2Fu, 0x99u, 0xBFu, 0x70u, 0x80u,
            0x00u, 0x00u, 0x01u, 0xB3u, 0x01u, 0x00u, 0x10u, 0x13u, 0xFFu, 0xFFu, 0xE0u, 0x18u,
            0x00u, 0x00u, 0x01u, 0xB5u, 0x14u, 0x8Au, 0x00u, 0x01u, 0x00u, 0x00u, 0x00u, 0x00u,
            0x01u, 0xB8u, 0x00u, 0x08u, 0x01u, 0x40u, 0x00u, 0x00u, 0x01u, 0x00u, 0x00u, 0x0Fu,
            0xFFu, 0xF8u, 0x00u, 0x00u, 0x01u, 0xB5u, 0x8Fu, 0xFFu, 0xF3u, 0x41u, 0x80u, 0x00u,
            0x00u, 0x01u, 0x01u, 0x13u, 0xF2u, 0x14u, 0xA5u, 0x2Fu, 0x99u, 0xBFu, 0x70u, 0x80u,
            0x00u, 0x00u, 0x01u, 0xB3u, 0x01u, 0x00u, 0x10u, 0x13u, 0xFFu, 0xFFu, 0xE0u, 0x18u,
            0x00u, 0x00u, 0x01u, 0xB5u, 0x14u, 0x8Au, 0x00u, 0x01u, 0x00u, 0x00u, 0x00u, 0x00u,
            0x01u, 0xB8u, 0x00u, 0x08u, 0x01u, 0xC0u, 0x00u, 0x00u, 0x01u, 0x00u, 0x00u, 0x0Fu,
            0xFFu, 0xF8u, 0x00u, 0x00u, 0x01u, 0xB5u, 0x8Fu, 0xFFu, 0xF3u, 0x41u, 0x80u, 0x00u,
            0x00u, 0x01u, 0x01u, 0x13u, 0xF2u, 0x14u, 0xA5u, 0x2Fu, 0x99u, 0xBFu, 0x70u, 0x80u,
        };
        if (feedBytes == sizeof(inputFrames))
            std::memcpy(rdram.data() + kNonStreamInput, inputFrames, sizeof(inputFrames));
        else
            for (unsigned i = 0; i < 4u; ++i)
                Ps2FastWrite32(rdram.data(), kNonStreamInput + 4u * i, 0xB7010000u);

        auto add = [&](uint32_t type, uint32_t func, uint32_t userdata)
        {
            R5900Context registration{};
            setRegU32(registration, 4, kNonStreamHandle);
            setRegU32(registration, 5, type);
            setRegU32(registration, 6, func);
            setRegU32(registration, 7, userdata);
            ps2_stubs::sceMpegAddCallback(rdram.data(), &registration, &runtime);
        };
        if (streamOnly)
        {
            R5900Context registration{};
            setRegU32(registration, 4, kNonStreamHandle);
            setRegU32(registration, 5, 1u);
            setRegU32(registration, 6, 0u);
            setRegU32(registration, 7, kNonStreamCallback);
            setRegU32(registration, 29, kNonStreamStack);
            Ps2FastWrite32(rdram.data(), kNonStreamStack + 16u, 99u);
            ps2_stubs::sceMpegAddStrCallback(rdram.data(), &registration, &runtime);
        }
        else
        {
            add(1u, kNonStreamCallback, 11u);
            if (ordered)
            {
                add(2u, kNonStreamCallback, 99u);
                add(1u, 0u, 99u);
                add(1u, 0x001255F0u, 99u); // Unbound function must not dispatch.
                add(1u, kNonStreamCallback, 22u);
            }
        }
        R5900Context mainContext{};
        mainContext.pc = kNonStreamMain;
        for (int reg : {16, 17, 18, 19, 20, 21, 22, 23, 28, 30})
            mainContext.r[reg] = _mm_set_epi64x(0x1234567800000000LL + reg, 0x7654321000000000LL + reg);
        setRegU32(mainContext, 29, kNonStreamStack);
        EeScheduler &ee = runtime.eeScheduler();
        ee.reset(rdram.data(), mainContext);
        const int observer = ee.createThread(EeThreadCreateParams{0u, kNonStreamObserver, 0u, 0u, 0u, 30, 0u});
        gNonStream.setup &= observer > 1 && ee.startThread(observer, 0u, mainContext, false) == 0;
        if (teardown != 0)
        {
            const int deleter = ee.createThread(EeThreadCreateParams{0u, kNonStreamDelete, 0u, 0u, 0u, 10, 0u});
            gNonStream.setup &= deleter > 1 && ee.startThread(deleter, 0u, mainContext, false) == 0;
        }
        ee.run();
        return gNonStream;
    }

