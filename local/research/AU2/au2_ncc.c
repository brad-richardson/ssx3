// AU2: normalized cross-correlation of a PCM slice (s16le stereo) against a
// reference (s16le stereo raw). Prints the best offset and NCC per channel.
// Usage: au2_ncc <ref.raw> <slice.bin> <slice_offset_bytes> <slice_frames>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static short *load(const char *p, long *n) {
    FILE *f = fopen(p, "rb"); if (!f) { perror(p); exit(1); }
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    short *b = malloc(sz); fread(b, 1, sz, f); fclose(f); *n = sz / 2; return b;
}
int main(int argc, char **argv) {
    long rn, sn; short *r = load(argv[1], &rn), *s0 = load(argv[2], &sn);
    long off = atol(argv[3]) / 2, m = atol(argv[4]);
    short *s = s0 + off;
    for (int ch = 0; ch < 2; ch++) {
        double ss = 0, sm = 0;
        for (long i = 0; i < m; i++) sm += s[2 * i + ch];
        sm /= m;
        for (long i = 0; i < m; i++) { double d = s[2 * i + ch] - sm; ss += d * d; }
        double best = -2; long bp = -1; long frames = rn / 2;
        for (long p = 0; p + m < frames; p++) {
            double rs = 0, rr = 0, rsum = 0;
            for (long i = 0; i < m; i++) rsum += r[2 * (p + i) + ch];
            double rm = rsum / m;
            for (long i = 0; i < m; i++) {
                double a = r[2 * (p + i) + ch] - rm, b = s[2 * i + ch] - sm;
                rs += a * b; rr += a * a;
            }
            double ncc = (rr > 0 && ss > 0) ? rs / sqrt(rr * ss) : 0;
            if (ncc > best) { best = ncc; bp = p; }
        }
        printf("ch%d best_ncc=%.4f at_frame=%ld (%.3f s @36k) slice_rms=%.0f\n", ch, best, bp, bp / 36000.0, sqrt(ss / m));
    }
    return 0;
}
