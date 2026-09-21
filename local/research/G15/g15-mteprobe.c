/* G15 instrumentation: report this process's MTE tagged-addr control word. */
#include <sys/prctl.h>
#include <stdio.h>
#ifndef PR_GET_TAGGED_ADDR_CTRL
#define PR_GET_TAGGED_ADDR_CTRL 56
#endif
int main(void) {
	long rc = prctl(PR_GET_TAGGED_ADDR_CTRL, 0, 0, 0, 0);
	printf("probe: tagged_addr_ctrl=0x%lx\n", (unsigned long)rc);
	return 0;
}
