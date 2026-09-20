// MF1 shared scene helpers (synthetic frames + depth + motion + timing).
#import <mach/mach.h>
#import <math.h>
#import <stdint.h>
#import <stdio.h>
#import <stdlib.h>
#import <string.h>
#import <sys/time.h>

// --- float -> half bits (for RG16Float motion / RGBA16Float color fill) ---
static uint16_t f32_to_f16(float f) {
    uint32_t u; memcpy(&u, &f, 4);
    uint32_t sign = (u >> 16) & 0x8000;
    int32_t exp = ((u >> 23) & 0xff) - 112;
    uint32_t mant = u & 0x7fffff;
    if (exp >= 31) return (uint16_t)(sign | 0x7bff); // saturate (no inf)
    if (exp <= 0) {
        if (exp < -10) return (uint16_t)sign;
        mant |= 0x800000;
        uint32_t t = mant >> (14 - exp);
        if ((mant >> (13 - exp)) & 1) t++;
        return (uint16_t)(sign | t);
    }
    return (uint16_t)(sign | (exp << 10) | (mant >> 13));
}

static double nowSec(void) {
    struct timeval tv; gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1e6;
}

static uint64_t residentBytes(void) {
    struct mach_task_basic_info info; mach_msg_type_number_t n = MACH_TASK_BASIC_INFO_COUNT;
    if (task_info(mach_task_self(), MACH_TASK_BASIC_INFO, (task_info_t)&info, &n) != KERN_SUCCESS) return 0;
    return info.resident_size;
}

static int cmpd(const void *a, const void *b) {
    double x = *(double *)a, y = *(double *)b; return (x > y) - (x < y);
}

static void writeRaw(const char *dir, const char *name, const void *data, size_t len) {
    char path[1024]; snprintf(path, sizeof(path), "%s/%s", dir, name);
    FILE *f = fopen(path, "wb");
    if (!f) { fprintf(stderr, "cannot write %s\n", path); exit(1); }
    if (fwrite(data, 1, len, f) != len) { fprintf(stderr, "short write %s\n", path); exit(1); }
    fclose(f);
}

// Scene params: rect translates +S px from A to B; GT middle at half.
// Depth convention: depthReversed=YES default => 0.0 = far, 1.0 = near.
typedef struct { int w, h, stride; float rectX; } FrameCtx;

static void paintFrame(uint8_t *rgba, float *depth, const FrameCtx *c, int hudMode /*0 none,1 composited*/) {
    int W = c->w, H = c->h;
    int rectW = W / 4, rectH = H / 2, rectY = (H - rectH) / 2;
    int rectX = (int)roundf(c->rectX);
    int hudH = H * 8 / 100;
    for (int y = 0; y < H; y++) {
        for (int x = 0; x < W; x++) {
            uint8_t r, g, b; float d;
            int inRect = (x >= rectX && x < rectX + rectW && y >= rectY && y < rectY + rectH);
            if (inRect) {
                int stripe = ((x - rectX) / 16) & 1; // 16px vertical stripes
                r = stripe ? 220 : 40; g = stripe ? 60 : 180; b = 60;
                d = 0.9f; // near
            } else {
                int chk = ((x / 32) + (y / 32)) & 1; // 32px checker + gradient
                uint8_t base = (uint8_t)(40 + 120 * x / (W - 1));
                r = chk ? base : (uint8_t)(base / 2 + 20);
                g = chk ? (uint8_t)(base / 2 + 30) : base;
                b = 90;
                d = 0.1f; // far
            }
            if (hudMode == 1 && y < hudH) { // composited HUD strip overwrites color
                int blk = (x / 48) & 1;
                r = blk ? 240 : 20; g = 240; b = blk ? 20 : 240;
                d = 0.1f; // HUD keeps world depth (session-1 choice, tabled)
            }
            uint8_t *p = rgba + (y * W + x) * 4;
            p[0] = b; p[1] = g; p[2] = r; p[3] = 255; // BGRA
            depth[y * W + x] = d;
        }
    }
}

// Convert BGRA8 host frame to RGBA16F host frame (normalized 0..1).
static void bgra8_to_rgba16f(uint16_t *dst, const uint8_t *src, size_t px) {
    for (size_t i = 0; i < px; i++) {
        dst[i * 4 + 0] = f32_to_f16(src[i * 4 + 2] / 255.0f);
        dst[i * 4 + 1] = f32_to_f16(src[i * 4 + 1] / 255.0f);
        dst[i * 4 + 2] = f32_to_f16(src[i * 4 + 0] / 255.0f);
        dst[i * 4 + 3] = f32_to_f16(1.0f);
    }
}

static void paintUI(uint8_t *rgba, int W, int H) {
    // Separate UI texture: HUD strip content, transparent black elsewhere.
    memset(rgba, 0, (size_t)W * H * 4);
    int hudH = H * 8 / 100;
    for (int y = 0; y < hudH; y++)
        for (int x = 0; x < W; x++) {
            int blk = (x / 48) & 1;
            uint8_t *p = rgba + (y * W + x) * 4;
            p[0] = blk ? 20 : 240; p[1] = 240; p[2] = blk ? 240 : 20; p[3] = 255;
        }
}

// Motion for current frame: exact => rect pixels point back (-S,0), else (0,0).
// scaleDiv: divide pixel motion by this (1 = pixels; W/2 = NDC-ish halves).
static void paintMotionEx(uint16_t *rg, int W, int H, float rectXcur, int S,
                          int mode /*0 exact,1 zero,2 uniform*/, float scaleDiv) {
    int rectW = W / 4, rectH = H / 2, rectY = (H - rectH) / 2;
    int rx = (int)roundf(rectXcur);
    float ux = -4.0f / scaleDiv, uy = 0.0f; // uniform fallback: global mean-ish flow
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            float mx = 0, my = 0;
            if (mode == 0 && x >= rx && x < rx + rectW && y >= rectY && y < rectY + rectH) { mx = -(float)S / scaleDiv; }
            else if (mode == 2) { mx = ux; my = uy; }
            rg[(y * W + x) * 2 + 0] = f32_to_f16(mx);
            rg[(y * W + x) * 2 + 1] = f32_to_f16(my);
        }
}

static void paintMotion(uint16_t *rg, int W, int H, float rectXB, int S, int mode) {
    paintMotionEx(rg, W, H, rectXB, S, mode, 1.0f);
}
