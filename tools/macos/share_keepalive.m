// A bounded, noninteractive SMB reconnect check for a per-user LaunchAgent.
// Authentication stays with NetAuth/Keychain. No credentials are read here.
#import <Foundation/Foundation.h>
#import <NetFS/NetFS.h>
#include <signal.h>
#include <sys/mount.h>
#include <unistd.h>

static void timedOut(int unused) {
  (void)unused;
  const char message[] = "Share check timed out; the next scheduled run will retry.\n";
  write(STDERR_FILENO, message, sizeof(message) - 1);
  _exit(75);
}

static int report(NSString *statePath, NSString *status, int code) {
  NSDictionary *state = @{@"checkedAt": [[NSDate date] description],
                          @"status": status, @"exitCode": @(code)};
  NSData *data = [NSJSONSerialization dataWithJSONObject:state options:NSJSONWritingPrettyPrinted error:nil];
  [data writeToFile:statePath options:NSDataWritingAtomic error:nil];
  if (code) fprintf(stderr, "%s\n", status.UTF8String);
  return code;
}

// Read the kernel's mount table without waiting for a disconnected SMB server.
// Refuse an unexpected filesystem or a duplicate mount at another path.
static NSString *mountState(NSURL *url, NSString *expected) {
  struct statfs *mounts;
  int count = getmntinfo(&mounts, MNT_NOWAIT);
  if (count <= 0) return @"cannot-read-mount-table";
  BOOL found = NO;
  for (int i = 0; i < count; ++i) {
    NSString *path = @(mounts[i].f_mntonname);
    BOOL smb = strcmp(mounts[i].f_fstypename, "smbfs") == 0;
    NSURL *source = smb ? [NSURL URLWithString:[@"smb:" stringByAppendingString:@(mounts[i].f_mntfromname)]] : nil;
    BOOL same = source && [source.host.lowercaseString isEqual:url.host.lowercaseString] &&
                [source.path isEqual:url.path];
    if ([path isEqual:expected]) {
      if (!same) return @"mount-path-used-by-another-filesystem";
      found = YES;
    } else if (same) {
      return @"share-mounted-at-another-path";
    }
  }
  return found ? @"mounted" : @"missing";
}

int main(int argc, const char *argv[]) {
  @autoreleasepool {
    if (argc != 4) {
      fprintf(stderr, "Usage: share-keepalive smb://host/share /Volumes/share state.json\n");
      return 64;
    }
    NSURL *url = [NSURL URLWithString:@(argv[1])];
    NSString *expected = @(argv[2]), *statePath = @(argv[3]);
    if (![url.scheme isEqual:@"smb"] || !url.host.length || url.password ||
        url.query || url.fragment || url.path.pathComponents.count != 2 ||
        ![expected hasPrefix:@"/Volumes/"] || expected.pathComponents.count != 3 ||
        ![expected.lastPathComponent isEqual:url.path.lastPathComponent]) {
      fprintf(stderr, "Expected a password-free SMB share URL and matching /Volumes mount path.\n");
      return 64;
    }
    signal(SIGALRM, timedOut);
    alarm(25);
    report(statePath, @"checking", 0);
    NSString *state = mountState(url, expected);
    if ([state isEqual:@"missing"]) {
      NSMutableDictionary *options = [@{(__bridge NSString *)kNAUIOptionKey:
                                        (__bridge NSString *)kNAUIOptionNoUI} mutableCopy];
      CFArrayRef points = NULL;
      int status = NetFSMountURLSync((__bridge CFURLRef)url, NULL, NULL, NULL,
                                    (__bridge CFMutableDictionaryRef)options, NULL, &points);
      if (points) CFRelease(points);
      if (status) return report(statePath, [NSString stringWithFormat:@"mount-failed (%d); retry scheduled", status], 75);
      state = mountState(url, expected);
    }
    if (![state isEqual:@"mounted"]) return report(statePath, state, 78);
    // Avoid reading the volume from a background agent: those reads require
    // separate macOS privacy consent and can hold up an otherwise healthy mount.
    // Existing SMB sessions reconnect in the OS; we never force-detach files.
    alarm(0);
    return report(statePath, @"mounted", 0);
  }
}
