/* G15 instrumentation: force MTE synchronous tag checks, then exec target.
 * No app source changes; session-only device artifact. */
#include <sys/prctl.h>
#include <unistd.h>
#include <stdio.h>
#ifndef PR_SET_TAGGED_ADDR_CTRL
#define PR_SET_TAGGED_ADDR_CTRL 55
#endif
#ifndef PR_MTE_TCF_SHIFT
#define PR_MTE_TCF_SHIFT 1
#endif
#ifndef PR_MTE_TCF_SYNC
#define PR_MTE_TCF_SYNC (1UL << PR_MTE_TCF_SHIFT)
#endif
#ifndef PR_TAGGED_ADDR_ENABLE
#define PR_TAGGED_ADDR_ENABLE (1UL << 0)
#endif
int main(int argc, char **argv) {
	if (argc < 2) { printf("usage: mtewrap prog args...\n"); return 2; }
	long rc = prctl(PR_SET_TAGGED_ADDR_CTRL,
	                PR_TAGGED_ADDR_ENABLE | PR_MTE_TCF_SYNC, 0, 0, 0);
	printf("mtewrap: prctl_sync rc=%ld\n", rc);
	fflush(stdout);
	execv(argv[1], argv + 1);
	perror("mtewrap: execv");
	return 127;
}
