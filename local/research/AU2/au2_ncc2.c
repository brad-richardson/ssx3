// AU2: long-window match. Mono (L+R), decimate both by D (box average), then
// full normalized cross-correlation of the capture window against the ref.
// Usage: au2_ncc2 <ref s16le stereo raw> <cap s16le stereo raw> <cap_start_frame> <frames> <D>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
static float *dec(const char *p, long start, long frames, int D, long *n) {
    FILE *f = fopen(p, "rb"); if (!f) { perror(p); exit(1); }
    fseek(f, 0, SEEK_END); long total = ftell(f) / 4; if (frames <= 0 || start + frames > total) frames = total - start;
    short *s = malloc(frames * 4); fseek(f, start * 4, SEEK_SET); fread(s, 4, frames, f); fclose(f);
    *n = frames / D; float *o = malloc(*n * sizeof(float));
    for (long i = 0; i < *n; i++) { double a = 0; for (int k = 0; k < D; k++) a += s[2 * (i * D + k)] + s[2 * (i * D + k) + 1]; o[i] = a / D; }
    free(s); return o;
}
int main(int argc, char **argv) {
    int D = atoi(argv[5]); long rn, cn;
    float *r = dec(argv[1], 0, 0, D, &rn), *c = dec(argv[2], atol(argv[3]), atol(argv[4]), D, &cn);
    double cm = 0, cs = 0; for (long i = 0; i < cn; i++) cm += c[i]; cm /= cn;
    for (long i = 0; i < cn; i++) { c[i] -= cm; cs += c[i] * c[i]; }
    double best = -2, second = -2; long bp = -1;
    for (long p = 0; p + cn <= rn; p++) {
        double rm = 0, rr = 0, rc = 0;
        for (long i = 0; i < cn; i++) rm += r[p + i]; rm /= cn;
        for (long i = 0; i < cn; i++) { double a = r[p + i] - rm; rr += a * a; rc += a * c[i]; }
        double v = rr > 0 ? rc / sqrt(rr * cs) : 0;
        if (v > best) { if (labs(p - bp) > cn) second = best; best = v; bp = p; }
        else if (v > second && labs(p - bp) > cn) second = v;
    }
    printf("window %ld frames (D=%d): best_ncc=%.4f at %.3f s; best elsewhere=%.4f\n", cn * D, D, best, bp * D / 36000.0, second);
    return 0;
}
