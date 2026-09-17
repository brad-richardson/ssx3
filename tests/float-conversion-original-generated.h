// DolRecomp output
// cpu: gekko

#ifndef RECOMP_GENERATED_H
#define RECOMP_GENERATED_H

#define DOLRECOMP_CPU_GEKKO 1
#define DOLRECOMP_CPU_NAME "gekko"

#include <string.h>
#include <math.h>
#ifndef DOLRECOMP_CPU_HEADER
#define DOLRECOMP_CPU_HEADER "cpu/cpu.h"
#endif
#include DOLRECOMP_CPU_HEADER

#ifndef DOLRECOMP_C_LOOP_CYCLE_BUDGET
#define DOLRECOMP_C_LOOP_CYCLE_BUDGET 256
#endif

/* Cross-chunk calls turn guest recursion into host recursion, and a
   chunk frame is not small. Without a ceiling a deep guest call chain
   overflows the host stack, which is a crash rather than a slow
   emulator. Past the limit the call site falls back to returning to
   the chassis, which is always correct -- ctx->pc already names the
   target, so the chassis simply dispatches it as it did before.
   The counter is plain static, not atomic: the chassis runs the module
   on one CPU thread. */
#ifndef DOLRECOMP_C_MAX_CALL_DEPTH
#define DOLRECOMP_C_MAX_CALL_DEPTH 24
#endif
extern unsigned dolrecomp_call_depth;
static inline int dolrecomp_call_enter(void) {
    if (dolrecomp_call_depth >= (unsigned)DOLRECOMP_C_MAX_CALL_DEPTH)
        return 0;
    dolrecomp_call_depth++;
    return 1;
}
static inline void dolrecomp_call_leave(void) {
    if (dolrecomp_call_depth)
        dolrecomp_call_depth--;
}

static inline u32 dolrecomp_rotl32(u32 value, u32 sh) {
    sh &= 31u;
    return sh ? ((value << sh) | (value >> (32u - sh))) : value;
}

static inline f64 dolrecomp_f32_from_bits(u32 bits) {
    u64 x = bits;
    u64 exp = (x >> 23) & 0xFFu;
    u64 frac = x & 0x007FFFFFu;
    u64 result;
    if (exp > 0 && exp < 255) {
        u64 y = !(exp >> 7);
        u64 z = (y << 61) | (y << 60) | (y << 59);
        result = ((x & 0xC0000000u) << 32) | z |
                 ((x & 0x3FFFFFFFu) << 29);
    } else if (exp == 0 && frac != 0) {
        exp = 1023 - 126;
        do {
            frac <<= 1;
            exp -= 1;
        } while ((frac & 0x00800000u) == 0);
        result = ((x & 0x80000000u) << 32) | (exp << 52) |
                 ((frac & 0x007FFFFFu) << 29);
    } else {
        u64 y = exp >> 7;
        u64 z = (y << 61) | (y << 60) | (y << 59);
        result = ((x & 0xC0000000u) << 32) | z |
                 ((x & 0x3FFFFFFFu) << 29);
    }
    f64 value;
    memcpy(&value, &result, sizeof(value));
    return value;
}

static inline u32 dolrecomp_f32_to_bits(f64 value) {
    u64 bits;
    memcpy(&bits, &value, sizeof(bits));
    u32 exp = (u32)((bits >> 52) & 0x7FFu);
    if (exp > 896 || (bits & 0x7FFFFFFFFFFFFFFFull) == 0) {
        return (u32)(((bits >> 32) & 0xC0000000u) |
                     ((bits >> 29) & 0x3FFFFFFFu));
    }
    if (exp >= 874) {
        u32 result =
            (u32)(0x80000000u | ((bits & 0x000FFFFFFFFFFFFFull) >> 21));
        result >>= 905 - exp;
        result |= (u32)((bits >> 32) & 0x80000000u);
        return result;
    }
    return (u32)(((bits >> 32) & 0xC0000000u) |
                 ((bits >> 29) & 0x3FFFFFFFu));
}

static inline f64 dolrecomp_f64_from_bits(u64 bits) {
    f64 value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static inline u64 dolrecomp_f64_to_bits(f64 value) {
    u64 bits;
    memcpy(&bits, &value, sizeof(bits));
    return bits;
}

static inline f64 dolrecomp_ps_from_bits(u32 bits) {
    return dolrecomp_f32_from_bits(bits);
}

static inline u32 dolrecomp_ps_to_bits(f64 value) {
    return dolrecomp_f32_to_bits(value);
}


// Function entry points
void func_80003100(CPUState* ctx);
void func_800057A0(CPUState* ctx);
void func_800097A0(CPUState* ctx);
void func_8000D7A0(CPUState* ctx);
void func_800117A0(CPUState* ctx);
void func_800157A0(CPUState* ctx);
void func_800197A0(CPUState* ctx);
void func_8001D7A0(CPUState* ctx);
void func_800217A0(CPUState* ctx);
void func_800257A0(CPUState* ctx);
void func_800297A0(CPUState* ctx);
void func_8002D7A0(CPUState* ctx);
void func_800317A0(CPUState* ctx);
void func_800357A0(CPUState* ctx);
void func_800397A0(CPUState* ctx);
void func_8003D7A0(CPUState* ctx);
void func_800417A0(CPUState* ctx);
void func_800457A0(CPUState* ctx);
void func_800497A0(CPUState* ctx);
void func_8004D7A0(CPUState* ctx);
void func_800517A0(CPUState* ctx);
void func_800557A0(CPUState* ctx);
void func_800597A0(CPUState* ctx);
void func_8005D7A0(CPUState* ctx);
void func_800617A0(CPUState* ctx);
void func_800657A0(CPUState* ctx);
void func_800697A0(CPUState* ctx);
void func_8006D7A0(CPUState* ctx);
void func_800717A0(CPUState* ctx);
void func_800757A0(CPUState* ctx);
void func_800797A0(CPUState* ctx);
void func_8007D7A0(CPUState* ctx);
void func_800817A0(CPUState* ctx);
void func_800857A0(CPUState* ctx);
void func_800897A0(CPUState* ctx);
void func_8008D7A0(CPUState* ctx);
void func_800917A0(CPUState* ctx);
void func_800957A0(CPUState* ctx);
void func_800997A0(CPUState* ctx);
void func_8009D7A0(CPUState* ctx);
void func_800A17A0(CPUState* ctx);
void func_800A57A0(CPUState* ctx);
void func_800A97A0(CPUState* ctx);
void func_800AD7A0(CPUState* ctx);
void func_800B17A0(CPUState* ctx);
void func_800B57A0(CPUState* ctx);
void func_800B97A0(CPUState* ctx);
void func_800BD7A0(CPUState* ctx);
void func_800C17A0(CPUState* ctx);
void func_800C57A0(CPUState* ctx);
void func_800C97A0(CPUState* ctx);
void func_800CD7A0(CPUState* ctx);
void func_800D17A0(CPUState* ctx);
void func_800D57A0(CPUState* ctx);
void func_800D97A0(CPUState* ctx);
void func_800DD7A0(CPUState* ctx);
void func_800E17A0(CPUState* ctx);
void func_800E57A0(CPUState* ctx);
void func_800E97A0(CPUState* ctx);
void func_800ED7A0(CPUState* ctx);
void func_800F17A0(CPUState* ctx);
void func_800F57A0(CPUState* ctx);
void func_800F97A0(CPUState* ctx);
void func_800FD7A0(CPUState* ctx);
void func_801017A0(CPUState* ctx);
void func_801057A0(CPUState* ctx);
void func_801097A0(CPUState* ctx);
void func_8010D7A0(CPUState* ctx);
void func_801117A0(CPUState* ctx);
void func_801157A0(CPUState* ctx);
void func_801197A0(CPUState* ctx);
void func_8011D7A0(CPUState* ctx);
void func_801217A0(CPUState* ctx);
void func_801257A0(CPUState* ctx);
void func_801297A0(CPUState* ctx);
void func_8012D7A0(CPUState* ctx);
void func_801317A0(CPUState* ctx);
void func_801357A0(CPUState* ctx);
void func_801397A0(CPUState* ctx);
void func_8013D7A0(CPUState* ctx);
void func_801417A0(CPUState* ctx);
void func_801457A0(CPUState* ctx);
void func_801497A0(CPUState* ctx);
void func_8014D7A0(CPUState* ctx);
void func_801517A0(CPUState* ctx);
void func_801557A0(CPUState* ctx);
void func_801597A0(CPUState* ctx);
void func_8015D7A0(CPUState* ctx);
void func_801617A0(CPUState* ctx);
void func_801657A0(CPUState* ctx);
void func_801697A0(CPUState* ctx);
void func_8016D7A0(CPUState* ctx);
void func_801717A0(CPUState* ctx);
void func_801757A0(CPUState* ctx);
void func_801797A0(CPUState* ctx);
void func_8017D7A0(CPUState* ctx);
void func_801817A0(CPUState* ctx);
void func_801857A0(CPUState* ctx);
void func_801897A0(CPUState* ctx);
void func_8018D7A0(CPUState* ctx);
void func_801917A0(CPUState* ctx);
void func_801957A0(CPUState* ctx);
void func_801997A0(CPUState* ctx);
void func_8019D7A0(CPUState* ctx);
void func_801A17A0(CPUState* ctx);
void func_801A57A0(CPUState* ctx);
void func_801A97A0(CPUState* ctx);
void func_801AD7A0(CPUState* ctx);
void func_801B17A0(CPUState* ctx);
void func_801B57A0(CPUState* ctx);
void func_801B97A0(CPUState* ctx);
void func_801BD7A0(CPUState* ctx);
void func_801C17A0(CPUState* ctx);
void func_801C57A0(CPUState* ctx);
void func_801C97A0(CPUState* ctx);
void func_801CD7A0(CPUState* ctx);
void func_801D17A0(CPUState* ctx);
void func_801D57A0(CPUState* ctx);
void func_801D97A0(CPUState* ctx);
void func_801DD7A0(CPUState* ctx);
void func_801E17A0(CPUState* ctx);
void func_801E57A0(CPUState* ctx);
void func_801E97A0(CPUState* ctx);
void func_801ED7A0(CPUState* ctx);
void func_801F17A0(CPUState* ctx);
void func_801F57A0(CPUState* ctx);
void func_801F97A0(CPUState* ctx);
void func_801FD7A0(CPUState* ctx);
void func_802017A0(CPUState* ctx);
void func_802057A0(CPUState* ctx);
void func_802097A0(CPUState* ctx);
void func_8020D7A0(CPUState* ctx);
void func_802117A0(CPUState* ctx);
void func_802157A0(CPUState* ctx);
void func_802197A0(CPUState* ctx);
void func_8021D7A0(CPUState* ctx);
void func_802217A0(CPUState* ctx);
void func_802257A0(CPUState* ctx);
void func_802297A0(CPUState* ctx);
void func_8022D7A0(CPUState* ctx);
void func_802317A0(CPUState* ctx);
void func_802357A0(CPUState* ctx);
void func_802397A0(CPUState* ctx);
void func_8023D7A0(CPUState* ctx);
void func_802417A0(CPUState* ctx);
void func_802457A0(CPUState* ctx);
void func_802497A0(CPUState* ctx);
void func_8024D7A0(CPUState* ctx);
void func_802517A0(CPUState* ctx);
void func_802557A0(CPUState* ctx);
void func_802597A0(CPUState* ctx);
void func_8025D7A0(CPUState* ctx);
void func_802617A0(CPUState* ctx);
void func_802657A0(CPUState* ctx);
void func_802697A0(CPUState* ctx);
void func_8026D7A0(CPUState* ctx);
void func_802717A0(CPUState* ctx);
void func_802757A0(CPUState* ctx);
void func_802797A0(CPUState* ctx);
void func_8027D7A0(CPUState* ctx);
void func_802817A0(CPUState* ctx);
void func_802857A0(CPUState* ctx);
void func_802897A0(CPUState* ctx);
void func_8028D7A0(CPUState* ctx);
void func_802917A0(CPUState* ctx);
void func_802957A0(CPUState* ctx);
void func_802997A0(CPUState* ctx);
void func_8029D7A0(CPUState* ctx);
void func_802A17A0(CPUState* ctx);
void func_802A57A0(CPUState* ctx);
void func_802A97A0(CPUState* ctx);
void func_802AD7A0(CPUState* ctx);
void func_802B17A0(CPUState* ctx);
void func_802B57A0(CPUState* ctx);
void func_802B97A0(CPUState* ctx);
void func_802BD7A0(CPUState* ctx);

#define DOLRECOMP_ENTRY_POINT 0x80003154u

typedef void (*DolRecompFunction)(CPUState* ctx);

#if defined(__GNUC__) || defined(__clang__)
#define DOLRECOMP_UNUSED __attribute__((unused))
#else
#define DOLRECOMP_UNUSED
#endif

#if defined(DOLRECOMP_ENABLE_REPLACEMENTS)
int dolrecomp_dispatch_replacement(CPUState* ctx, u32 address);
#else
static inline int dolrecomp_dispatch_replacement(CPUState* ctx, u32 address) {
    (void)ctx;
    (void)address;
    return 0;
}
#endif

static inline DolRecompFunction dolrecomp_find_original(u32 address) {
    if (address >= 0x80003100u && address < 0x800056C0u && ((address - 0x80003100u) & 3u) == 0u) return func_80003100;
    {
        u32 offset = address - 0x800057A0u;
        if (offset < 0x002BB660u && (offset & 3u) == 0u) {
            static const DolRecompFunction chunk_functions[] = {
                func_800057A0,
                func_800097A0,
                func_8000D7A0,
                func_800117A0,
                func_800157A0,
                func_800197A0,
                func_8001D7A0,
                func_800217A0,
                func_800257A0,
                func_800297A0,
                func_8002D7A0,
                func_800317A0,
                func_800357A0,
                func_800397A0,
                func_8003D7A0,
                func_800417A0,
                func_800457A0,
                func_800497A0,
                func_8004D7A0,
                func_800517A0,
                func_800557A0,
                func_800597A0,
                func_8005D7A0,
                func_800617A0,
                func_800657A0,
                func_800697A0,
                func_8006D7A0,
                func_800717A0,
                func_800757A0,
                func_800797A0,
                func_8007D7A0,
                func_800817A0,
                func_800857A0,
                func_800897A0,
                func_8008D7A0,
                func_800917A0,
                func_800957A0,
                func_800997A0,
                func_8009D7A0,
                func_800A17A0,
                func_800A57A0,
                func_800A97A0,
                func_800AD7A0,
                func_800B17A0,
                func_800B57A0,
                func_800B97A0,
                func_800BD7A0,
                func_800C17A0,
                func_800C57A0,
                func_800C97A0,
                func_800CD7A0,
                func_800D17A0,
                func_800D57A0,
                func_800D97A0,
                func_800DD7A0,
                func_800E17A0,
                func_800E57A0,
                func_800E97A0,
                func_800ED7A0,
                func_800F17A0,
                func_800F57A0,
                func_800F97A0,
                func_800FD7A0,
                func_801017A0,
                func_801057A0,
                func_801097A0,
                func_8010D7A0,
                func_801117A0,
                func_801157A0,
                func_801197A0,
                func_8011D7A0,
                func_801217A0,
                func_801257A0,
                func_801297A0,
                func_8012D7A0,
                func_801317A0,
                func_801357A0,
                func_801397A0,
                func_8013D7A0,
                func_801417A0,
                func_801457A0,
                func_801497A0,
                func_8014D7A0,
                func_801517A0,
                func_801557A0,
                func_801597A0,
                func_8015D7A0,
                func_801617A0,
                func_801657A0,
                func_801697A0,
                func_8016D7A0,
                func_801717A0,
                func_801757A0,
                func_801797A0,
                func_8017D7A0,
                func_801817A0,
                func_801857A0,
                func_801897A0,
                func_8018D7A0,
                func_801917A0,
                func_801957A0,
                func_801997A0,
                func_8019D7A0,
                func_801A17A0,
                func_801A57A0,
                func_801A97A0,
                func_801AD7A0,
                func_801B17A0,
                func_801B57A0,
                func_801B97A0,
                func_801BD7A0,
                func_801C17A0,
                func_801C57A0,
                func_801C97A0,
                func_801CD7A0,
                func_801D17A0,
                func_801D57A0,
                func_801D97A0,
                func_801DD7A0,
                func_801E17A0,
                func_801E57A0,
                func_801E97A0,
                func_801ED7A0,
                func_801F17A0,
                func_801F57A0,
                func_801F97A0,
                func_801FD7A0,
                func_802017A0,
                func_802057A0,
                func_802097A0,
                func_8020D7A0,
                func_802117A0,
                func_802157A0,
                func_802197A0,
                func_8021D7A0,
                func_802217A0,
                func_802257A0,
                func_802297A0,
                func_8022D7A0,
                func_802317A0,
                func_802357A0,
                func_802397A0,
                func_8023D7A0,
                func_802417A0,
                func_802457A0,
                func_802497A0,
                func_8024D7A0,
                func_802517A0,
                func_802557A0,
                func_802597A0,
                func_8025D7A0,
                func_802617A0,
                func_802657A0,
                func_802697A0,
                func_8026D7A0,
                func_802717A0,
                func_802757A0,
                func_802797A0,
                func_8027D7A0,
                func_802817A0,
                func_802857A0,
                func_802897A0,
                func_8028D7A0,
                func_802917A0,
                func_802957A0,
                func_802997A0,
                func_8029D7A0,
                func_802A17A0,
                func_802A57A0,
                func_802A97A0,
                func_802AD7A0,
                func_802B17A0,
                func_802B57A0,
                func_802B97A0,
                func_802BD7A0,
            };
            return chunk_functions[offset / 0x00004000u];
        }
    }
    return NULL;
}

static inline int dolrecomp_call_original(CPUState* ctx, u32 address) {
    DolRecompFunction fn = dolrecomp_find_original(address);
    if (!fn) return 0;
    ctx->pc = address;
    fn(ctx);
    return 1;
}

static inline bool dolrecomp_physical_pc_alias(CPUState* ctx, u32 address, u32* alias_out) {
    if (address < ctx->ram_size) {
        *alias_out = address | GC_RAM_BASE;
        return *alias_out != address;
    }
    return false;
}

static inline int dolrecomp_call(CPUState* ctx, u32 address) {
    u32 alias;
    ctx->pc = address;
    if (dolrecomp_dispatch_replacement(ctx, address)) return 1;
    if (ctx->host_call && ppc_host_call(ctx, address)) return 1;
    if (dolrecomp_call_original(ctx, address)) return 1;
    if (dolrecomp_physical_pc_alias(ctx, address, &alias)) {
        ctx->pc = alias;
        if (dolrecomp_dispatch_replacement(ctx, alias)) return 1;
        if (ctx->host_call && ppc_host_call(ctx, alias)) return 1;
        if (dolrecomp_call_original(ctx, alias)) return 1;
    }
    return 0;
}

static inline DOLRECOMP_UNUSED int dolrecomp_run_blocks(CPUState* ctx, u32 max_blocks) {
    u32 blocks = 0;
    while (max_blocks == 0u || blocks < max_blocks) {
        if (!dolrecomp_call(ctx, ctx->pc)) return 0;
        if (ctx->exception) return 0;
        blocks++;
    }
    return 1;
}

#undef DOLRECOMP_UNUSED

#endif /* RECOMP_GENERATED_H */

// end
