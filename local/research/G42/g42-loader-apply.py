#!/usr/bin/env python3
"""G42: loader-swap hunk applier (Mission 1).

Inserts the PGS_G42_TURNIP-gated HAL/HMI loader into
tools/gs_dump_replayer.cpp. Default (env unset) = Context::init_loader(nullptr),
byte-identical behavior. 3 asserted edits; --dry for verification.
"""
import sys

EDITS = []

# 1. dlfcn include for dlopen/dlsym.
EDITS.append((
"""#include <stdio.h>
#include <stdint.h>
""",
"""#include <stdio.h>
#include <stdint.h>
#include <dlfcn.h>
"""))

# 2. G42 helper before main().
EDITS.append((
"""int main(int argc, char **argv)
""",
"""// G42 local experiment hook (not upstream): Mesa Turnip contrast on Adreno.
// Env-gated (PGS_G42_TURNIP=<Turnip driver .so path>), default = system
// loader (zero behavior change). Adrenotools-format Turnip builds export a
// single OBJECT symbol "HMI" (legacy pointer-layout hw module: tag@0, api
// versions@4, id@8, name@16, author@24, methods@32); we open it as the
// Vulkan HAL module and hand its GetInstanceProcAddr to Granite's loader.
// Every Turnip-path failure exits non-zero: a silent fallback to the
// system driver would mislabel the run.
struct G42HalModuleMethods
{
	int (*open)(const void *module, const char *id, void **device);
};
struct G42HalModule
{
	uint32_t tag;
	uint16_t module_api_version;
	uint16_t hal_api_version;
	const char *id;
	const char *name;
	const char *author;
	G42HalModuleMethods *methods;
};
struct G42HalDevice
{
	uint32_t tag;
	uint32_t version;
	void *module;
	int (*close)(void *dev);
	void *enumerate_instance_ext;
	void *create_instance;
	PFN_vkGetInstanceProcAddr get_instance_proc_addr;
};

static bool g42_init_loader()
{
	const char *turnip = getenv("PGS_G42_TURNIP");
	LOGI("G42: Vulkan loader: %s.\\n", turnip ? turnip : "(system)");
	if (!turnip)
		return Context::init_loader(nullptr);
	void *mod = dlopen(turnip, RTLD_NOW | RTLD_LOCAL);
	if (!mod)
	{
		LOGE("G42: dlopen failed: %s.\\n", dlerror());
		return false;
	}
	G42HalModule *hmi = reinterpret_cast<G42HalModule *>(dlsym(mod, "HMI"));
	if (!hmi)
	{
		LOGE("G42: no HMI symbol: %s.\\n", dlerror());
		return false;
	}
	LOGI("G42: HMI tag=%08x id=%s name=%s author=%s methods=%p.\\n",
	     hmi->tag, hmi->id ? hmi->id : "(null)",
	     hmi->name ? hmi->name : "(null)",
	     hmi->author ? hmi->author : "(null)",
	     (const void *)hmi->methods);
	if (hmi->tag != 0x48574d54 || !hmi->methods || !hmi->methods->open)
	{
		LOGE("G42: HMI layout mismatch.\\n");
		return false;
	}
	void *dev = nullptr;
	int rc = hmi->methods->open(hmi, "vulkan0", &dev);
	LOGI("G42: HAL open rc=%d dev=%p.\\n", rc, dev);
	if (rc != 0 || !dev)
	{
		LOGE("G42: HAL open failed.\\n");
		return false;
	}
	G42HalDevice *vdev = reinterpret_cast<G42HalDevice *>(dev);
	LOGI("G42: HAL dev tag=%08x get_proc=%p.\\n",
	     vdev->tag, (const void *)vdev->get_instance_proc_addr);
	if (!vdev->get_instance_proc_addr)
	{
		LOGE("G42: HAL has no GetInstanceProcAddr.\\n");
		return false;
	}
	return Context::init_loader(vdev->get_instance_proc_addr);
}

int main(int argc, char **argv)
"""))

# 3. Route init through the helper.
EDITS.append((
"""	if (!Context::init_loader(nullptr))
		return EXIT_FAILURE;
""",
"""	if (!g42_init_loader())
		return EXIT_FAILURE;
"""))


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry"]
    if len(args) != 1:
        print("usage: g42-loader-apply.py [--dry] <clone>")
        return 2
    path = args[0] + "/tools/gs_dump_replayer.cpp"
    src = open(path, encoding="utf-8").read()
    for i, (find, repl) in enumerate(EDITS):
        n = src.count(find)
        if n != 1:
            print("EDIT %d: found %d occurrences, need exactly 1" % (i, n))
            return 1
        src = src.replace(find, repl, 1)
    if dry:
        print("DRY-OK %d" % len(EDITS))
        return 0
    open(path, "w", encoding="utf-8").write(src)
    print("APPLIED %d" % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
