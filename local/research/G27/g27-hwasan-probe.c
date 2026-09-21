// G27 trivial HWASan loadability probe (G27-original, session file).
// Mode clean (default): malloc + print + free, exit 0 -- proves the
// HWASan runtime loads and malloc/free interceptors work on Odin3.
// Mode fault (argv[1]=="fault"): 1-byte heap-buffer-overflow write --
// proves the detector FIRES and shows the on-device report shape.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
  char *p = (char *)malloc(32);
  if (!p) {
    printf("G27-PROBE: malloc FAILED\n");
    return 2;
  }
  strcpy(p, "G27-HWASAN-PROBE-LOAD-OK");
  printf("G27-PROBE: %s\n", p);
  if (argc > 1 && strcmp(argv[1], "fault") == 0) {
    volatile char *q = (volatile char *)p;
    q[40] = 'X'; // OOB past the 32-byte granule: must trip HWASan
    printf("G27-PROBE: fault NOT detected (BAD)\n");
  }
  free(p);
  printf("G27-PROBE: done exit=0\n");
  return 0;
}
