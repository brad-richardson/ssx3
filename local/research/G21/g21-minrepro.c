// g21-minrepro.c — standalone Adreno O4 repro (UNTESTED on device).
//
// Calls bare vkCreateComputePipelines on the named crashing SPIR-V
// (sampler_feedback, sha b0a09fa0..., 5049 words) with the exact pipeline
// inputs Granite used: DESCRIPTOR_BUFFER_BIT (+ flags2 twin), entry
// "main", stage COMPUTE, pSpecializationInfo NULL, no robustness / subgroup /
// heap pNext, empty pipeline cache. Single-threaded, no Granite.
//
// Build (host, Android arm64, NDK r30): see g21-build.sh.
// Device run (NOT performed in G21): push binary + g21-sampler-feedback.spv
// to one dir, run ./g21-minrepro. Expected on Adreno 830 / 512.800.58:
// SIGSEGV inside libllvm-qgl.so before "SURVIVED" prints. Exit 0 + SURVIVED
// on drivers that compile the shader.
//
// License: MIT (standalone G21 artifact; no third-party code).

#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vulkan/vulkan.h>

#define EXPECT_WORDS 5049u
#define EXPECT_FNV 0xc61f1a8116a82d4bull
#define SPV_MAGIC 0x07230203u

static void *lib;
static PFN_vkGetInstanceProcAddr gpa;

#define LOAD_GLOBAL(name) \
    PFN_##name name = (PFN_##name)gpa(NULL, #name); \
    if (!name) { fprintf(stderr, "missing %s\n", #name); return 2; }

static uint64_t fnv1a64(const uint32_t *w, size_t n) {
    uint64_t h = 0xcbf29ce484222325ull;
    for (size_t i = 0; i < n; i++)
        h = ((h * 0x100000001b3ull) ^ w[i]) & 0xFFFFFFFFFFFFFFFFull;
    return h;
}

int main(int argc, char **argv) {
    const char *spv_path = argc > 1 ? argv[1] : "g21-sampler-feedback.spv";
    int rc = 0;

    // 1. Load SPIR-V sidecar, verify identity.
    FILE *f = fopen(spv_path, "rb");
    if (!f) { fprintf(stderr, "open %s failed\n", spv_path); return 2; }
    fseek(f, 0, SEEK_END);
    long bytes = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (bytes != (long)(EXPECT_WORDS * 4)) {
        fprintf(stderr, "size %ld, want %u\n", bytes, EXPECT_WORDS * 4);
        fclose(f);
        return 2;
    }
    uint32_t *code = (uint32_t *)malloc((size_t)bytes);
    if (!code || fread(code, 1, (size_t)bytes, f) != (size_t)bytes) {
        fprintf(stderr, "read failed\n");
        fclose(f);
        return 2;
    }
    fclose(f);
    if (code[0] != SPV_MAGIC) {
        fprintf(stderr, "bad magic 0x%08x\n", code[0]);
        return 2;
    }
    uint64_t fnv = fnv1a64(code, EXPECT_WORDS);
    printf("spv: %u words, fnv %016llx %s\n", EXPECT_WORDS,
           (unsigned long long)fnv, fnv == EXPECT_FNV ? "MATCH" : "MISMATCH");
    fflush(stdout);
    if (fnv != EXPECT_FNV)
        return 2;

    // 2. Loader + instance (Vulkan 1.3, no layers, no instance extensions).
    lib = dlopen("libvulkan.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib)
        lib = dlopen("libvulkan.so.1", RTLD_NOW | RTLD_LOCAL);
    if (!lib) {
        fprintf(stderr, "dlopen libvulkan failed: %s\n", dlerror());
        return 2;
    }
    gpa = (PFN_vkGetInstanceProcAddr)dlsym(lib, "vkGetInstanceProcAddr");
    if (!gpa) {
        fprintf(stderr, "no vkGetInstanceProcAddr\n");
        return 2;
    }
    LOAD_GLOBAL(vkCreateInstance);
    LOAD_GLOBAL(vkEnumeratePhysicalDevices);
    LOAD_GLOBAL(vkGetPhysicalDeviceProperties);
    LOAD_GLOBAL(vkGetPhysicalDeviceQueueFamilyProperties);
    LOAD_GLOBAL(vkGetPhysicalDeviceFeatures2);
    LOAD_GLOBAL(vkCreateDevice);
    LOAD_GLOBAL(vkGetDeviceProcAddr);

    VkApplicationInfo app = {
        .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
        .pApplicationName = "g21-minrepro",
        .apiVersion = VK_API_VERSION_1_3,
    };
    VkInstanceCreateInfo ici = {
        .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        .pApplicationInfo = &app,
    };
    VkInstance inst = VK_NULL_HANDLE;
    if (vkCreateInstance(&ici, NULL, &inst) != VK_SUCCESS || !inst) {
        fprintf(stderr, "vkCreateInstance failed\n");
        return 2;
    }

    // 3. Pick GPU (first; print all), verify compute queue exists.
    uint32_t ngpu = 0;
    vkEnumeratePhysicalDevices(inst, &ngpu, NULL);
    if (!ngpu) {
        fprintf(stderr, "no GPUs\n");
        return 2;
    }
    VkPhysicalDevice *gpus = malloc(ngpu * sizeof(*gpus));
    vkEnumeratePhysicalDevices(inst, &ngpu, gpus);
    for (uint32_t i = 0; i < ngpu; i++) {
        VkPhysicalDeviceProperties p;
        vkGetPhysicalDeviceProperties(gpus[i], &p);
        printf("gpu%u: %s api %u.%u.%u driver 0x%x\n", i, p.deviceName,
               VK_VERSION_MAJOR(p.apiVersion), VK_VERSION_MINOR(p.apiVersion),
               VK_VERSION_PATCH(p.apiVersion), p.driverVersion);
    }
    fflush(stdout);
    VkPhysicalDevice gpu = gpus[0];
    free(gpus);

    uint32_t nqf = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(gpu, &nqf, NULL);
    VkQueueFamilyProperties *qfs = malloc(nqf * sizeof(*qfs));
    vkGetPhysicalDeviceQueueFamilyProperties(gpu, &nqf, qfs);
    uint32_t qf = UINT32_MAX;
    for (uint32_t i = 0; i < nqf; i++)
        if (qfs[i].queueFlags & VK_QUEUE_COMPUTE_BIT) { qf = i; break; }
    free(qfs);
    if (qf == UINT32_MAX) {
        fprintf(stderr, "no compute queue\n");
        return 2;
    }

    // 4. Device extensions: Granite's exact 15 (g20-logcat.txt order).
    static const char *exts[] = {
        "VK_KHR_external_semaphore_fd",
        "VK_KHR_external_memory_fd",
        "VK_KHR_calibrated_timestamps",
        "VK_EXT_conservative_rasterization",
        "VK_KHR_push_descriptor",
        "VK_EXT_index_type_uint8",
        "VK_KHR_maintenance5",
        "VK_EXT_astc_decode_mode",
        "VK_EXT_image_compression_control",
        "VK_EXT_image_compression_control_swapchain",
        "VK_KHR_ray_query",
        "VK_KHR_acceleration_structure",
        "VK_KHR_deferred_host_operations",
        "VK_EXT_descriptor_buffer",
        "VK_EXT_shader_image_atomic_int64",
    };

    // 5. Features the crashing compile needs; verify support first.
    VkPhysicalDevice16BitStorageFeatures sb16 = {
        .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_16BIT_STORAGE_FEATURES,
    };
    VkPhysicalDeviceBufferDeviceAddressFeatures bda = {
        .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_BUFFER_DEVICE_ADDRESS_FEATURES,
        .pNext = &sb16,
    };
    VkPhysicalDeviceDescriptorBufferFeaturesEXT dbf = {
        .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DESCRIPTOR_BUFFER_FEATURES_EXT,
        .pNext = &bda,
    };
    VkPhysicalDeviceFeatures2 f2 = {
        .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2,
        .pNext = &dbf,
    };
    vkGetPhysicalDeviceFeatures2(gpu, &f2);
    printf("features: shaderInt16=%d sb16=%d uandsb16=%d bda=%d descBuf=%d\n",
           f2.features.shaderInt16, sb16.storageBuffer16BitAccess,
           sb16.uniformAndStorageBuffer16BitAccess, bda.bufferDeviceAddress,
           dbf.descriptorBuffer);
    fflush(stdout);
    if (!f2.features.shaderInt16 || !sb16.storageBuffer16BitAccess ||
        !sb16.uniformAndStorageBuffer16BitAccess || !bda.bufferDeviceAddress ||
        !dbf.descriptorBuffer) {
        fprintf(stderr, "required feature unsupported; repro N/A here\n");
        return 2;
    }
    // Re-chain with all required bits TRUE for device creation.
    f2.features.shaderInt16 = VK_TRUE;
    sb16.storageBuffer16BitAccess = VK_TRUE;
    sb16.uniformAndStorageBuffer16BitAccess = VK_TRUE;
    bda.bufferDeviceAddress = VK_TRUE;
    dbf.descriptorBuffer = VK_TRUE;

    float prio = 1.0f;
    VkDeviceQueueCreateInfo qci = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
        .queueFamilyIndex = qf,
        .queueCount = 1,
        .pQueuePriorities = &prio,
    };
    VkDeviceCreateInfo dci = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        .pNext = &f2,
        .queueCreateInfoCount = 1,
        .pQueueCreateInfos = &qci,
        .enabledExtensionCount = sizeof(exts) / sizeof(exts[0]),
        .ppEnabledExtensionNames = exts,
    };
    VkDevice dev = VK_NULL_HANDLE;
    VkResult vr = vkCreateDevice(gpu, &dci, NULL, &dev);
    if (vr != VK_SUCCESS || !dev) {
        fprintf(stderr, "vkCreateDevice -> %d\n", vr);
        return 2;
    }
    printf("device created\n");
    fflush(stdout);

#define LOAD_DEV(name) \
    PFN_##name name = (PFN_##name)vkGetDeviceProcAddr(dev, #name); \
    if (!name) { fprintf(stderr, "missing %s\n", #name); rc = 2; goto out; }

    LOAD_DEV(vkCreateDescriptorSetLayout);
    LOAD_DEV(vkCreatePipelineLayout);
    LOAD_DEV(vkCreateShaderModule);
    LOAD_DEV(vkCreatePipelineCache);
    LOAD_DEV(vkCreateComputePipelines);
    LOAD_DEV(vkDestroyDevice);

    // 6. Descriptor set layouts from the disassembled interface.
    // set0: b4/b7/b8 STORAGE_BUFFER, b9/b15 UNIFORM_BUFFER; set1: b0 UBO.
    VkDescriptorSetLayoutBinding s0[] = {
        { 4, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1, VK_SHADER_STAGE_COMPUTE_BIT, NULL },
        { 7, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1, VK_SHADER_STAGE_COMPUTE_BIT, NULL },
        { 8, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1, VK_SHADER_STAGE_COMPUTE_BIT, NULL },
        { 9, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1, VK_SHADER_STAGE_COMPUTE_BIT, NULL },
        { 15, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1, VK_SHADER_STAGE_COMPUTE_BIT, NULL },
    };
    VkDescriptorSetLayoutBinding s1[] = {
        { 0, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1, VK_SHADER_STAGE_COMPUTE_BIT, NULL },
    };
    VkDescriptorSetLayoutCreateInfo lci = {
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
        .flags = VK_DESCRIPTOR_SET_LAYOUT_CREATE_DESCRIPTOR_BUFFER_BIT_EXT,
    };
    VkDescriptorSetLayout setlayouts[2];
    lci.bindingCount = sizeof(s0) / sizeof(s0[0]);
    lci.pBindings = s0;
    if (vkCreateDescriptorSetLayout(dev, &lci, NULL, &setlayouts[0]) != VK_SUCCESS) {
        fprintf(stderr, "set0 layout failed\n");
        rc = 2;
        goto out;
    }
    lci.bindingCount = sizeof(s1) / sizeof(s1[0]);
    lci.pBindings = s1;
    if (vkCreateDescriptorSetLayout(dev, &lci, NULL, &setlayouts[1]) != VK_SUCCESS) {
        fprintf(stderr, "set1 layout failed\n");
        rc = 2;
        goto out;
    }
    VkPushConstantRange push = { VK_SHADER_STAGE_COMPUTE_BIT, 0, 12 };
    VkPipelineLayoutCreateInfo plci = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .setLayoutCount = 2,
        .pSetLayouts = setlayouts,
        .pushConstantRangeCount = 1,
        .pPushConstantRanges = &push,
    };
    VkPipelineLayout layout = VK_NULL_HANDLE;
    if (vkCreatePipelineLayout(dev, &plci, NULL, &layout) != VK_SUCCESS) {
        fprintf(stderr, "pipeline layout failed\n");
        rc = 2;
        goto out;
    }

    VkShaderModuleCreateInfo smci = {
        .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
        .codeSize = (size_t)bytes,
        .pCode = code,
    };
    VkShaderModule mod = VK_NULL_HANDLE;
    if (vkCreateShaderModule(dev, &smci, NULL, &mod) != VK_SUCCESS || !mod) {
        fprintf(stderr, "shader module failed\n");
        rc = 2;
        goto out;
    }
    // Empty pipeline cache (Granite's cache starts empty on a fresh dir).
    VkPipelineCacheCreateInfo cci = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_CACHE_CREATE_INFO,
    };
    VkPipelineCache cache = VK_NULL_HANDLE;
    if (vkCreatePipelineCache(dev, &cci, NULL, &cache) != VK_SUCCESS) {
        fprintf(stderr, "pipeline cache failed\n");
        rc = 2;
        goto out;
    }

    // 7. THE call: flags + flags2 descriptor-buffer bit, NULL spec info,
    // no robustness / subgroup / heap pNext — Granite's exact inputs.
    VkPipelineCreateFlags2CreateInfo f2c = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_CREATE_FLAGS_2_CREATE_INFO,
        .flags = VK_PIPELINE_CREATE_2_DESCRIPTOR_BUFFER_BIT_EXT,
    };
    VkComputePipelineCreateInfo cpi = {
        .sType = VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO,
        .pNext = &f2c,
        .flags = VK_PIPELINE_CREATE_DESCRIPTOR_BUFFER_BIT_EXT,
        .stage = {
            .sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            .stage = VK_SHADER_STAGE_COMPUTE_BIT,
            .module = mod,
            .pName = "main",
            .pSpecializationInfo = NULL,
        },
        .layout = layout,
        .basePipelineIndex = -1,
    };
    printf("calling vkCreateComputePipelines ...\n");
    fflush(stdout);
    VkPipeline pipe = VK_NULL_HANDLE;
    vr = vkCreateComputePipelines(dev, cache, 1, &cpi, NULL, &pipe);
    printf("SURVIVED: vkCreateComputePipelines -> %d\n", vr);
    fflush(stdout);

out:
    if (dev)
        vkDestroyDevice(dev, NULL);
    free(code);
    return rc;
}
