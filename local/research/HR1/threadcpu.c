// HR1: per-thread CPU time + name for one pid (macOS libproc, same uid, no root).
// Usage: threadcpu <pid>   -> one line per thread: name user_ns system_ns cpu_usage
#include <libproc.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/proc_info.h>

int main(int argc, char **argv)
{
    if (argc < 2)
        return 2;
    const int pid = atoi(argv[1]);
    uint64_t handles[512];
    const int bytes = proc_pidinfo(pid, PROC_PIDLISTTHREADS, 0, handles, sizeof(handles));
    if (bytes <= 0)
    {
        perror("PROC_PIDLISTTHREADS");
        return 1;
    }
    const int n = bytes / (int)sizeof(uint64_t);
    for (int i = 0; i < n; ++i)
    {
        struct proc_threadinfo ti;
        if (proc_pidinfo(pid, PROC_PIDTHREADINFO, handles[i], &ti, sizeof(ti)) != (int)sizeof(ti))
            continue;
        printf("%d\t%s\t%llu\t%llu\t%d\n", i, ti.pth_name[0] ? ti.pth_name : "-",
               (unsigned long long)ti.pth_user_time, (unsigned long long)ti.pth_system_time,
               ti.pth_cpu_usage);
    }
    return 0;
}
