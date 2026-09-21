"""Apply the reviewed E18 handwritten MPEG-only behavior change once."""
from e18_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
assert (E/'OWNERSHIP.md').exists()
path = R/'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp'
baseline = next(r for r in json.loads((E/'checkpoint.json').read_text())['inputs_sources'] if r['path'] == str(path))
assert sha(path) == baseline['sha256']
resources = sample(); admission(resources); save('admission-at-mutation.json', resources)
s = path.read_text()
def replace(old, new):
    global s
    assert s.count(old) == 1, old[:100]
    s = s.replace(old, new)
replace('namespace ps2_stubs\n{\n    namespace', '''namespace ps2_stubs
{
    static void getMpegPicture(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime, bool requestInput);

    namespace''')
replace('        struct MpegStubState\n', '''        // One caller-owned request, retained by its invocation/wait continuations.
        // The global index is weak so it cannot outlive an EE scheduler/runtime.
        struct MpegNonStreamDelivery
        {
            PS2Runtime *runtime = nullptr;
            uint32_t mpegAddr = 0u;
            uint32_t type = 0u;
            int ownerThread = 0;
            std::vector<MpegRegisteredCallback> callbacks;
            size_t nextCallback = 0u;
            uint32_t callbackData = 0u;
            uint32_t callbackEntry = 0u;
            uint64_t tag = 0u;
            bool cancelled = false;
        };

        struct MpegStubState
''')
replace('            std::unordered_map<uint32_t, MpegPlaybackState> playbackByMpeg;\n', '''            std::unordered_map<uint32_t, MpegPlaybackState> playbackByMpeg;
            std::unordered_map<uint64_t, std::weak_ptr<MpegNonStreamDelivery>> nonStreamDeliveries;
''')
replace('        void queueStreamCallbackEvent(uint32_t mpegAddr,\n', '''        std::vector<MpegRegisteredCallback> matchingNonStreamCallbacks(uint32_t mpegAddr, uint32_t requestedType)
        {
            std::vector<MpegRegisteredCallback> out;
            const auto it = g_mpeg_stub_state.callbacksByMpeg.find(mpegAddr);
            if (it != g_mpeg_stub_state.callbacksByMpeg.end())
            {
                for (const MpegRegisteredCallback &callback : it->second)
                {
                    if (!callback.stream && callback.type == requestedType)
                    {
                        out.push_back(callback);
                    }
                }
            }
            return out;
        }

        uint64_t nonStreamDeliveryKey(uint32_t mpegAddr, uint32_t type)
        {
            return (static_cast<uint64_t>(mpegAddr) << 32u) | type;
        }

        // Called under the MPEG lock. Cancelling a queued entry changes only
        // that owned invocation; an already executing callback retains its data
        // until onComplete and cannot dispatch the rest of the collected list.
        void invalidateNonStreamDeliveries(uint32_t mpegAddr)
        {
            for (auto it = g_mpeg_stub_state.nonStreamDeliveries.begin();
                 it != g_mpeg_stub_state.nonStreamDeliveries.end();)
            {
                if (static_cast<uint32_t>(it->first >> 32u) != mpegAddr)
                {
                    ++it;
                    continue;
                }
                if (const auto delivery = it->second.lock())
                {
                    delivery->cancelled = true;
                    EeScheduler &scheduler = delivery->runtime->eeScheduler();
                    if (GuestThread *owner = scheduler.thread(delivery->ownerThread))
                    {
                        for (GuestInvocation &invocation : owner->invocations)
                        {
                            if (invocation.kind == GuestInvocationKind::HleCall &&
                                invocation.tag == delivery->tag &&
                                invocation.context.pc == delivery->callbackEntry)
                            {
                                invocation.context.pc = 0u;
                            }
                        }
                    }
                    // This schedules a wake; it never executes guest code here.
                    scheduler.completeExternalWait(kMpegPictureWaitType, mpegAddr, KE_WAIT_DELETE);
                }
                it = g_mpeg_stub_state.nonStreamDeliveries.erase(it);
            }
        }

        void queueStreamCallbackEvent(uint32_t mpegAddr,
''')
replace('        void dispatchStreamCallbacks(uint8_t *rdram,\n', '''        void dispatchGuestNonStreamCallback(uint8_t *rdram,
                                            R5900Context *callerCtx,
                                            const std::shared_ptr<MpegNonStreamDelivery> &delivery)
        {
            PS2Runtime *runtime = delivery->runtime;
            while (!delivery->cancelled && delivery->nextCallback < delivery->callbacks.size())
            {
                const MpegRegisteredCallback callback = delivery->callbacks[delivery->nextCallback++];
                if (callback.func == 0u || !runtime->hasFunction(callback.func))
                {
                    continue;
                }
                // The observed non-stream producer initializes only word 0.
                // Do not reuse the unrelated 0x20-byte stream-event layout.
                const uint32_t cbDataAddr = runtime->guestMalloc(sizeof(uint32_t), alignof(uint32_t));
                uint8_t *data = cbDataAddr != 0u ? getMemPtr(rdram, cbDataAddr) : nullptr;
                if (!data)
                {
                    runtime->guestFree(cbDataAddr);
                    continue;
                }
                ps2_e3::Tap tap = ps2_e3::tapBegin(rdram, cbDataAddr, sizeof(uint32_t));
                std::memcpy(data, &delivery->type, sizeof(uint32_t));
                ps2_e3::tapEnd(std::move(tap), "mpeg-nonstream-cb", rdram, "-");
                delivery->callbackData = cbDataAddr;
                delivery->callbackEntry = callback.func;
                delivery->tag = 0x4D50454700000000ull | callback.handle;

                GuestInvocation invocation{};
                invocation.kind = GuestInvocationKind::HleCall;
                invocation.tag = delivery->tag;
                invocation.context = *callerCtx;
                invocation.context.pc = callback.func;
                SET_GPR_U32(&invocation.context, 4, delivery->mpegAddr);
                SET_GPR_U32(&invocation.context, 5, cbDataAddr);
                SET_GPR_U32(&invocation.context, 6, callback.data);
                // Keep the caller's stack. Zero RA is the scheduler's HLE
                // continuation sentinel; the original RA/PC remain in parent.
                SET_GPR_U32(&invocation.context, 31, 0u);
                invocation.onComplete = [rdram, runtime, delivery](const R5900Context &, R5900Context &parent)
                {
                    runtime->guestFree(delivery->callbackData);
                    delivery->callbackData = 0u;
                    if (delivery->cancelled)
                    {
                        setReturnS32(&parent, KE_WAIT_DELETE);
                        return;
                    }
                    // Callback v0 is deliberately ignored. Preserve registration
                    // order, then continue this request without re-triggering it.
                    dispatchGuestNonStreamCallback(rdram, &parent, delivery);
                    getMpegPicture(rdram, &parent, runtime, false);
                };
                runtime->eeScheduler().invokeCurrent(std::move(invocation));
            }
        }

        void dispatchStreamCallbacks(uint8_t *rdram,
''')
replace('        void resetMpegStubStateUnlocked()\n        {\n', '''        void resetMpegStubStateUnlocked()
        {
            while (!g_mpeg_stub_state.nonStreamDeliveries.empty())
            {
                invalidateNonStreamDeliveries(static_cast<uint32_t>(
                    g_mpeg_stub_state.nonStreamDeliveries.begin()->first >> 32u));
            }
''')
replace('            getPlaybackState(param_1) = makeFreshPlaybackState();\n', '''            invalidateNonStreamDeliveries(param_1);
            getPlaybackState(param_1) = makeFreshPlaybackState();
''')
replace('            g_mpeg_stub_state.callbacksByMpeg.erase(mpegAddr);\n', '''            invalidateNonStreamDeliveries(mpegAddr);
            g_mpeg_stub_state.callbacksByMpeg.erase(mpegAddr);
''')
replace('    void sceMpegGetPicture(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)\n', '    static void getMpegPicture(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime, bool requestInput)\n')
replace('        bool haveFrame = false;\n        MpegDecodedFrame frame;\n', '''        bool haveFrame = false;
        MpegDecodedFrame frame;
        std::shared_ptr<MpegNonStreamDelivery> delivery;
        bool dispatchInput = false;
        {
            std::lock_guard<std::mutex> lock(g_mpeg_stub_mutex);
            // Original GetPicture's IPU-busy input request produces cbData
            // word0=1. No other non-stream type or trigger is synthesized.
            constexpr uint32_t inputRequestType = 1u;
            const uint64_t key = nonStreamDeliveryKey(mpegAddr, inputRequestType);
            auto &pending = g_mpeg_stub_state.nonStreamDeliveries[key];
            delivery = pending.lock();
            MpegPlaybackState &playback = getPlaybackState(mpegAddr);
            if (requestInput && !delivery && playback.decodedFrames.empty() &&
                !g_mpeg_stub_state.currentCdStreamEofSeen && !playback.streamEnded && !playback.decoderFailed)
            {
                auto callbacks = matchingNonStreamCallbacks(mpegAddr, inputRequestType);
                if (!callbacks.empty())
                {
                    delivery = std::make_shared<MpegNonStreamDelivery>();
                    delivery->runtime = runtime;
                    delivery->mpegAddr = mpegAddr;
                    delivery->type = inputRequestType;
                    delivery->callbacks = std::move(callbacks);
                    pending = delivery;
                    dispatchInput = true;
                }
            }
            if (!delivery)
            {
                g_mpeg_stub_state.nonStreamDeliveries.erase(key);
            }
        }
        if (dispatchInput)
        {
            // AddBs re-enters the MPEG mutex. Dispatch only after collecting
            // under the lock, on the GetPicture caller rather than an RPC thread.
            runtime->eeScheduler().bindMainContextForSyscall(*ctx, rdram);
            delivery->ownerThread = runtime->eeScheduler().currentThreadId();
            dispatchGuestNonStreamCallback(rdram, ctx, delivery);
        }
''')
# Both wait continuations retain the request until its real completion/cancel.
s = s.replace('[rdram, runtime](R5900Context &resumeContext)', '[rdram, runtime, delivery](R5900Context &resumeContext)')
assert s.count('[rdram, runtime, delivery](R5900Context &resumeContext)') == 2
replace('    void sceMpegGetPictureRAW8(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)\n', '''    void sceMpegGetPicture(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
    {
        getMpegPicture(rdram, ctx, runtime, true);
    }

    void sceMpegGetPictureRAW8(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
''')
replace('            MpegPlaybackState &playback = getPlaybackState(param_1);\n            MpegPlaybackState resetState', '''            invalidateNonStreamDeliveries(param_1);
            MpegPlaybackState &playback = getPlaybackState(param_1);
            MpegPlaybackState resetState''')
path.write_text(s)
save('mpeg-edit.json',dict(utc=utc(),before=baseline,after=pin(path),files=[str(path)],generator_runs=0))
print('MPEG.cpp edited; MPEG.h/main/scheduler/CSV/generated sources untouched.')
print('# E18 MPEG EDIT TAIL COMPLETE')
