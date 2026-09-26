// GV1: the VR4 exact FMAC core (fork b97b241 ps2_vu1_fmac_simd.h) as GLSL, without fp64.
//
// Value path: IEEE fp32 add/sub/mul with `precise` (no contraction). Vulkan requires these to be
// correctly rounded; RTE is the default mode. Operands are normalized first (exp 0 -> signed 0,
// exp 255 -> signed 0x7F7FFFFF), so no denormal or Inf/NaN input reaches the hardware. The cases
// where a denormal or Inf *intermediate or result* matters (MADD/MSUB with a product below FLT_MIN,
// or a float result with exponent 0 or 255) take a software path, because the device may flush
// denormals (Apple: shaderDenormPreserveFloat32 = false).
// Classification path: VR4 classifies the *double* result (acc +- vs*b in double, i.e. the exact
// value rounded once to 53 bits). No GPU here has fp64, so the double rounding is emulated with
// int64 mantissas (exact alignment + sticky, then round-to-nearest-even to 53 bits).
#extension GL_EXT_shader_explicit_arithmetic_types_int64 : require

const uint kAdd = 0u, kSub = 1u, kMul = 2u, kMadd = 3u, kMsub = 4u, kOpmsub = 5u, kOpmula = 6u;
const uint kQ = 4u, kI = 5u, kVec = 6u, kCross = 7u;

uint normOp(uint b)
{
    uint s = b & 0x80000000u, e = b & 0x7F800000u;
    return e == 0u ? s : (e == 0x7F800000u ? (s | 0x7F7FFFFFu) : b);
}

int msb64(uint64_t v)
{
    uint hi = uint(v >> 32);
    return hi != 0u ? 32 + findMSB(hi) : findMSB(uint(v));
}

// Class of value (m * 2^e), m != 0: returns Z=1,S=2,U=4,O=8 bits for a *nonzero* value.
// MAX = 0xFFFFFF * 2^104, MIN = 2^-126.
uint classMag(uint64_t m, int e)
{
    int b = msb64(m);
    int L = b + e;
    if (L < -126) return 5u;          // U|Z
    if (L > 127) return 8u;           // O
    if (L == 127)
    {
        // compare the normalized 64-bit mantissa with 0xFFFFFF << 40
        uint64_t n = m << uint(63 - b);
        if (n > (uint64_t(0xFFFFFFu) << 40)) return 8u;
    }
    return 0u;
}

// Flags of a single exact term (sign kept for zero, as the double product's -0).
uint classifyTerm(bool n, uint64_t m, int e)
{
    if (m == uint64_t(0)) return n ? 3u : 1u;
    return classMag(m, e) | (n ? 2u : 0u);
}

// Term for a normalized float: m = 24-bit mantissa (0 if zero), e = exponent of the LSB.
void fterm(uint b, out bool neg, out uint64_t m, out int e)
{
    neg = (b >> 31) != 0u;
    uint ex = (b >> 23) & 0xFFu;
    m = ex == 0u ? uint64_t(0) : uint64_t((b & 0x7FFFFFu) | 0x800000u);
    e = int(ex) - 150;
}

// Flags nibble (Z1 S2 U4 O8) of the double RN(a + b) for two exact terms (sign, mantissa <= 48
// bits, LSB exponent). A zero term has m == 0. Also returns the sign used for value overrides.
uint classifySum(bool an, uint64_t am, int ae, bool bn, uint64_t bm, int be, out bool neg)
{
    if (am == uint64_t(0) && bm == uint64_t(0)) { neg = an && bn; return neg ? 3u : 1u; }
    if (am == uint64_t(0)) { neg = bn; return classMag(bm, be) | (bn ? 2u : 0u); }
    if (bm == uint64_t(0)) { neg = an; return classMag(am, ae) | (an ? 2u : 0u); }
    // normalize both to bit 61
    int sa = 61 - msb64(am), sb = 61 - msb64(bm);
    am <<= uint(sa); ae -= sa; bm <<= uint(sb); be -= sb;
    if (be > ae || (be == ae && bm > am))
    {
        bool tn = an; an = bn; bn = tn;
        uint64_t tm = am; am = bm; bm = tm;
        int te = ae; ae = be; be = te;
    }
    int d = ae - be;
    uint64_t s; bool sticky;
    if (d >= 63) { s = uint64_t(0); sticky = true; }
    else { s = bm >> uint(d); sticky = (bm & ((uint64_t(1) << uint(d)) - uint64_t(1))) != uint64_t(0); }
    uint64_t m; bool frac;
    neg = an;
    if (an == bn) { m = am + s; frac = sticky; }
    else
    {
        m = am - s; frac = sticky;
        if (sticky) m -= uint64_t(1);                  // m + (1 - f): integer part below, frac > 0
        if (m == uint64_t(0) && !frac) { neg = false; return 1u; }   // exact cancellation: +0
    }
    int e = ae;
    if (m == uint64_t(0)) { m = uint64_t(1); e -= 1; frac = false; } // only 0.5 left (d <= 1)
    int b = msb64(m);
    if (b >= 53)
    {
        uint sh = uint(b - 52);
        uint64_t keep = m >> sh;
        uint64_t rem = m & ((uint64_t(1) << sh) - uint64_t(1));
        uint64_t halfv = uint64_t(1) << (sh - 1u);
        bool up = rem > halfv || (rem == halfv && (frac || (keep & uint64_t(1)) != uint64_t(0)));
        keep += up ? uint64_t(1) : uint64_t(0);
        m = keep; e += int(sh);
    }
    else if (frac)
    {
        // exact value m + 0.5 (d <= 1): at most 53 significant bits
        m = (m << 1) | uint64_t(1); e -= 1;
    }
    return classMag(m, e) | (neg ? 2u : 0u);
}

// Round (sign, m, e) (value m*2^e, m < 2^63) to float bits, RN-even, denormals kept, overflow Inf.
uint roundToFloat(bool neg, uint64_t m, int e, bool stickyIn)
{
    uint sgn = neg ? 0x80000000u : 0u;
    if (m == uint64_t(0)) return sgn;
    int b = msb64(m);
    int L = b + e;                       // floor(log2 value)
    int lsb = max(L - 23, -149);         // exponent of the result's LSB
    int sh = lsb - e;
    uint64_t q; bool up;
    if (sh <= 0) { q = m << uint(-sh); up = false; }
    else if (sh >= 64) { q = uint64_t(0); up = false; /* below halfv of the LSB */ }
    else
    {
        q = m >> uint(sh);
        uint64_t rem = m & ((uint64_t(1) << uint(sh)) - uint64_t(1));
        uint64_t halfv = uint64_t(1) << uint(sh - 1);
        up = rem > halfv || (rem == halfv && (stickyIn || (q & uint64_t(1)) != uint64_t(0)));
    }
    q += up ? uint64_t(1) : uint64_t(0);
    // q is the significand at LSB exponent `lsb`; renormalize
    if (q == uint64_t(0)) return sgn;
    int qb = msb64(q);
    int exLsb = lsb;
    if (qb == 24) { q >>= 1u; exLsb += 1; }     // carry out of rounding
    int biased = exLsb + 150;                    // for a normal: q in [2^23, 2^24)
    if (msb64(q) < 23) return sgn | uint(q);     // denormal (exLsb == -149)
    if (biased >= 255) return sgn | 0x7F800000u;
    return sgn | (uint(biased) << 23) | (uint(q) & 0x7FFFFFu);
}

// Software RN(a + b) for two float bit patterns (any finite, denormal or Inf input), RN-even.
uint softAdd(uint a, uint b)
{
    uint ea = (a >> 23) & 0xFFu, eb = (b >> 23) & 0xFFu;
    bool na = (a >> 31) != 0u, nb = (b >> 31) != 0u;
    if (ea == 0xFFu || eb == 0xFFu)
    {
        if (ea == 0xFFu && eb == 0xFFu && na != nb) return 0x7FC00000u;
        return ea == 0xFFu ? a : b;
    }
    uint64_t ma = uint64_t(ea == 0u ? (a & 0x7FFFFFu) : ((a & 0x7FFFFFu) | 0x800000u));
    uint64_t mb = uint64_t(eb == 0u ? (b & 0x7FFFFFu) : ((b & 0x7FFFFFu) | 0x800000u));
    int xa = max(int(ea), 1) - 150, xb = max(int(eb), 1) - 150;
    if (ma == uint64_t(0) && mb == uint64_t(0)) return (na && nb) ? 0x80000000u : 0u;
    if (ma == uint64_t(0)) return b;
    if (mb == uint64_t(0)) return a;
    if (xb > xa) { uint t = a; a = b; b = t; bool tn = na; na = nb; nb = tn;
                   uint64_t tm = ma; ma = mb; mb = tm; int tx = xa; xa = xb; xb = tx; }
    int d = xa - xb;
    if (d > 38) return a;   // |b| < 2^-15 ulp(a): RN keeps a (also across a power-of-two edge)
    ma <<= uint(d);
    bool neg; uint64_t m;
    if (na == nb) { m = ma + mb; neg = na; }
    else if (ma >= mb) { m = ma - mb; neg = na; }
    else { m = mb - ma; neg = nb; }
    if (m == uint64_t(0)) return 0u;
    return roundToFloat(neg, m, xb, false);
}

// One FMAC on four lanes. Writes the destination row (dest-masked) and MAC/status (direct commit,
// as VU1Interpreter::commitFmacFlags with directFlags).
void fmacExact(uint arith, uint src, uint dest, uvec4 vsIn, uvec4 vtIn, uvec4 accIn, uint q, uint i,
               inout uvec4 row, inout uint mac, inout uint status)
{
    if (dest == 0u) return;
    uvec4 vs = uvec4(normOp(vsIn.x), normOp(vsIn.y), normOp(vsIn.z), normOp(vsIn.w));
    uvec4 vt = uvec4(normOp(vtIn.x), normOp(vtIn.y), normOp(vtIn.z), normOp(vtIn.w));
    uvec4 acc = uvec4(normOp(accIn.x), normOp(accIn.y), normOp(accIn.z), normOp(accIn.w));
    uvec4 b;
    if (src < 4u) b = uvec4(vt[src]);
    else if (src == kQ) b = uvec4(normOp(q));
    else if (src == kI) b = uvec4(normOp(i));
    else if (src == kVec) b = vt;
    else { vs = vs.yzxw; b = vt.zxyw; }
    bool cross = arith == kOpmsub || arith == kOpmula;
    bool usesAcc = arith == kMadd || arith == kMsub || arith == kOpmsub;
    bool productSum = usesAcc;
    uint macOut = 0u, stat = 0u, extra = 0u;
    uvec4 res;
    for (int k = 0; k < 4; ++k)
    {
        bool live = ((dest >> uint(3 - k)) & 1u) != 0u;
        float fs = uintBitsToFloat(vs[k]), fb = uintBitsToFloat(b[k]);
        float fa = uintBitsToFloat(usesAcc ? acc[k] : 0u);
        bool sn, bn, an; uint64_t sm, bm, am; int se, be, ae;
        fterm(vs[k], sn, sm, se); fterm(b[k], bn, bm, be); fterm(usesAcc ? acc[k] : 0u, an, am, ae);
        precise float r;
        uint fl; bool neg;
        bool wZero = cross && k == 3;
        if (arith == kAdd || arith == kSub)
        {
            if (arith == kSub) bn = !bn;
            r = arith == kAdd ? fs + fb : fs - fb;
            fl = classifySum(sn, sm, se, bn, bm, be, neg);
            uint rb = floatBitsToUint(r);
            uint rex = (rb >> 23) & 0xFFu;
            if ((rex == 0u || rex == 0xFFu) && (fl & 13u) == 0u)
                r = uintBitsToFloat(softAdd(vs[k], arith == kAdd ? b[k] : (b[k] ^ 0x80000000u)));
        }
        else
        {
            // exact product term (48-bit mantissa)
            bool pn = sn != bn;
            uint64_t pm = sm * bm;
            int pe = se + be;
            precise float p = fs * fb;
            if (arith == kMul || arith == kOpmula)
            {
                r = p;
                if (wZero) { r = 0.0; fl = 1u; neg = false; }
                else { fl = classifyTerm(pn, pm, pe); neg = pn; }
            }
            else
            {
                bool sub = arith == kMsub || arith == kOpmsub;
                r = sub ? fa - p : fa + p;
                bool en = sub ? !pn : pn;
                if (wZero) { r = 0.0; fl = 1u; neg = false; }
                else
                {
                    fl = classifySum(an, am, ae, en, pm, pe, neg);
                    // software value when a denormal/Inf product or result would differ under FTZ
                    bool tinyP = pm != uint64_t(0) && (msb64(pm) + pe) < -126;
                    uint rex = (floatBitsToUint(r) >> 23) & 0xFFu;
                    uint pex = (floatBitsToUint(p) >> 23) & 0xFFu;
                    if (tinyP || rex == 0u || rex == 0xFFu || pex == 0xFFu)
                    {
                        uint pf = roundToFloat(pn, pm, pe, false);
                        r = uintBitsToFloat(softAdd(acc[k], sub ? (pf ^ 0x80000000u) : pf));
                    }
                }
                if (productSum && live)
                {
                    extra |= classifyTerm(pn, pm, pe);
                }
            }
        }
        // value overrides (normalizeFmacExactResult)
        uint rb = floatBitsToUint(r);
        uint sbit = neg ? 0x80000000u : 0u;
        if ((fl & 1u) != 0u) rb = sbit;                 // zero or underflow -> signed 0
        if ((fl & 8u) != 0u) rb = sbit | 0x7F7FFFFFu;   // overflow -> signed MAX
        res[k] = rb;
        if (live)
        {
            uint lf = fl & 0xFu;
            stat |= lf;
            uint sh = uint(3 - k);
            macOut |= ((lf & 1u) << sh) | (((lf >> 1) & 1u) << (4u + sh)) |
                      (((lf >> 2) & 1u) << (8u + sh)) | (((lf >> 3) & 1u) << (12u + sh));
            row[k] = rb;
        }
    }
    mac = macOut;
    status = (status & 0xFF0u) | stat | ((stat | extra) << 6);
}

// Decode the upper word into (arith, src, accDest); returns false for non-FMAC ops.
bool decodeFmac(uint instr, out uint arith, out uint src, out bool accDest)
{
    uint op = instr & 0x3Fu;
    uint code = op < 0x3Cu ? op : ((instr & 3u) | ((instr >> 4) & 0x7Cu));
    accDest = op >= 0x3Cu;
    if (code <= 0x0Fu) { arith = code >> 2 == 0u ? kAdd : code >> 2 == 1u ? kSub : code >> 2 == 2u ? kMadd : kMsub; src = code & 3u; return true; }
    if (code >= 0x18u && code <= 0x1Bu) { arith = kMul; src = code & 3u; return true; }
    if (code == 0x1Cu) { arith = kMul; src = kQ; return true; }
    if (code == 0x1Eu) { arith = kMul; src = kI; return true; }
    if (code >= 0x20u && code <= 0x27u)
    {
        uint t = code - 0x20u;
        arith = t == 0u || t == 2u ? kAdd : t == 1u || t == 3u ? kMadd : t == 4u || t == 6u ? kSub : kMsub;
        src = (t & 2u) != 0u ? kI : kQ; return true;
    }
    if (code == 0x28u) { arith = kAdd; src = kVec; return true; }
    if (code == 0x29u) { arith = kMadd; src = kVec; return true; }
    if (code == 0x2Au) { arith = kMul; src = kVec; return true; }
    if (code == 0x2Cu) { arith = kSub; src = kVec; return true; }
    if (code == 0x2Du) { arith = kMsub; src = kVec; return true; }
    if (code == 0x2Eu) { arith = accDest ? kOpmula : kOpmsub; src = kCross; return true; }
    return false;
}
