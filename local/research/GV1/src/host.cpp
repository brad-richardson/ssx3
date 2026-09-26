// GV1 Vulkan compute harness (MoltenVK on the mini).
//   host test  <test.spv>  <cases.bin>            -> bit-exact compare vs the VR4 core's results
//   host bench <benchN.spv> <threads> <iters> <reps> -> GPU time (timestamps) and FMAC op rate
#include <vulkan/vulkan.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#define CK(x) do { VkResult r_ = (x); if (r_ != VK_SUCCESS) { std::fprintf(stderr, "%s -> %d\n", #x, r_); std::exit(2); } } while (0)

struct Ctx
{
    VkInstance inst; VkPhysicalDevice pd; VkDevice dev; VkQueue q; uint32_t qf;
    VkPhysicalDeviceProperties props;
};

static std::vector<char> readFile(const char *p)
{
    FILE *f = std::fopen(p, "rb"); if (!f) { std::perror(p); std::exit(2); }
    std::fseek(f, 0, SEEK_END); long n = std::ftell(f); std::fseek(f, 0, SEEK_SET);
    std::vector<char> v(n); std::fread(v.data(), 1, n, f); std::fclose(f); return v;
}

static Ctx init()
{
    Ctx c{};
    VkApplicationInfo ai{VK_STRUCTURE_TYPE_APPLICATION_INFO}; ai.apiVersion = VK_API_VERSION_1_2;
    const char *ext[] = {VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME};
    VkInstanceCreateInfo ici{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    ici.flags = VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR; ici.pApplicationInfo = &ai;
    ici.enabledExtensionCount = 1; ici.ppEnabledExtensionNames = ext;
    CK(vkCreateInstance(&ici, nullptr, &c.inst));
    uint32_t n = 1; VkPhysicalDevice pds[4]; n = 4;
    CK(vkEnumeratePhysicalDevices(c.inst, &n, pds)); c.pd = pds[0];
    vkGetPhysicalDeviceProperties(c.pd, &c.props);
    uint32_t qn = 0; vkGetPhysicalDeviceQueueFamilyProperties(c.pd, &qn, nullptr);
    std::vector<VkQueueFamilyProperties> qp(qn); vkGetPhysicalDeviceQueueFamilyProperties(c.pd, &qn, qp.data());
    for (uint32_t i = 0; i < qn; ++i) if (qp[i].queueFlags & VK_QUEUE_COMPUTE_BIT) { c.qf = i; break; }
    float prio = 1.0f;
    VkDeviceQueueCreateInfo qci{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
    qci.queueFamilyIndex = c.qf; qci.queueCount = 1; qci.pQueuePriorities = &prio;
    VkPhysicalDeviceFeatures f{}; f.shaderInt64 = VK_TRUE;
    VkPhysicalDeviceVulkan12Features f12{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES};
    const char *dext[] = {"VK_KHR_portability_subset"};
    VkDeviceCreateInfo dci{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
    dci.pNext = &f12; dci.queueCreateInfoCount = 1; dci.pQueueCreateInfos = &qci; dci.pEnabledFeatures = &f;
    dci.enabledExtensionCount = 1; dci.ppEnabledExtensionNames = dext;
    CK(vkCreateDevice(c.pd, &dci, nullptr, &c.dev));
    vkGetDeviceQueue(c.dev, c.qf, 0, &c.q);
    return c;
}

struct Buf { VkBuffer b; VkDeviceMemory m; void *p; VkDeviceSize n; };
static Buf mkbuf(Ctx &c, VkDeviceSize n)
{
    Buf b{}; b.n = n;
    VkBufferCreateInfo bi{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO}; bi.size = n; bi.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
    CK(vkCreateBuffer(c.dev, &bi, nullptr, &b.b));
    VkMemoryRequirements mr; vkGetBufferMemoryRequirements(c.dev, b.b, &mr);
    VkPhysicalDeviceMemoryProperties mp; vkGetPhysicalDeviceMemoryProperties(c.pd, &mp);
    uint32_t want = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT, idx = 0;
    for (uint32_t i = 0; i < mp.memoryTypeCount; ++i)
        if ((mr.memoryTypeBits & (1u << i)) && (mp.memoryTypes[i].propertyFlags & want) == want) { idx = i; break; }
    VkMemoryAllocateInfo ma{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO}; ma.allocationSize = mr.size; ma.memoryTypeIndex = idx;
    CK(vkAllocateMemory(c.dev, &ma, nullptr, &b.m)); CK(vkBindBufferMemory(c.dev, b.b, b.m, 0));
    CK(vkMapMemory(c.dev, b.m, 0, n, 0, &b.p));
    return b;
}

struct Pipe { VkPipeline p; VkPipelineLayout pl; VkDescriptorSet ds; };
static Pipe mkpipe(Ctx &c, const char *spv, Buf &a, Buf &b, uint32_t pcSize)
{
    auto code = readFile(spv);
    VkShaderModuleCreateInfo sm{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO}; sm.codeSize = code.size(); sm.pCode = (uint32_t *)code.data();
    VkShaderModule mod; CK(vkCreateShaderModule(c.dev, &sm, nullptr, &mod));
    VkDescriptorSetLayoutBinding bd[2]{};
    for (int i = 0; i < 2; ++i) { bd[i].binding = i; bd[i].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER; bd[i].descriptorCount = 1; bd[i].stageFlags = VK_SHADER_STAGE_COMPUTE_BIT; }
    VkDescriptorSetLayoutCreateInfo dl{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO}; dl.bindingCount = 2; dl.pBindings = bd;
    VkDescriptorSetLayout dsl; CK(vkCreateDescriptorSetLayout(c.dev, &dl, nullptr, &dsl));
    VkPushConstantRange pr{VK_SHADER_STAGE_COMPUTE_BIT, 0, pcSize};
    VkPipelineLayoutCreateInfo pli{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO}; pli.setLayoutCount = 1; pli.pSetLayouts = &dsl; pli.pushConstantRangeCount = 1; pli.pPushConstantRanges = &pr;
    Pipe p{}; CK(vkCreatePipelineLayout(c.dev, &pli, nullptr, &p.pl));
    VkComputePipelineCreateInfo cp{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
    cp.stage.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO; cp.stage.stage = VK_SHADER_STAGE_COMPUTE_BIT; cp.stage.module = mod; cp.stage.pName = "main"; cp.layout = p.pl;
    CK(vkCreateComputePipelines(c.dev, VK_NULL_HANDLE, 1, &cp, nullptr, &p.p));
    VkDescriptorPoolSize ps{VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 2};
    VkDescriptorPoolCreateInfo dp{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO}; dp.maxSets = 1; dp.poolSizeCount = 1; dp.pPoolSizes = &ps;
    VkDescriptorPool pool; CK(vkCreateDescriptorPool(c.dev, &dp, nullptr, &pool));
    VkDescriptorSetAllocateInfo da{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO}; da.descriptorPool = pool; da.descriptorSetCount = 1; da.pSetLayouts = &dsl;
    CK(vkAllocateDescriptorSets(c.dev, &da, &p.ds));
    VkDescriptorBufferInfo bi[2] = {{a.b, 0, VK_WHOLE_SIZE}, {b.b, 0, VK_WHOLE_SIZE}};
    VkWriteDescriptorSet w[2]{};
    for (int i = 0; i < 2; ++i) { w[i].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET; w[i].dstSet = p.ds; w[i].dstBinding = i; w[i].descriptorCount = 1; w[i].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER; w[i].pBufferInfo = &bi[i]; }
    vkUpdateDescriptorSets(c.dev, 2, w, 0, nullptr);
    return p;
}

// Record one dispatch between two timestamps, submit, wait. Returns {gpu ms, wall ms}.
static void run(Ctx &c, Pipe &p, const void *pcData, uint32_t pcSize, uint32_t groups, double &gpuMs, double &wallMs)
{
    VkCommandPoolCreateInfo cpi{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO}; cpi.queueFamilyIndex = c.qf;
    VkCommandPool pool; CK(vkCreateCommandPool(c.dev, &cpi, nullptr, &pool));
    VkCommandBufferAllocateInfo ca{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO}; ca.commandPool = pool; ca.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY; ca.commandBufferCount = 1;
    VkCommandBuffer cb; CK(vkAllocateCommandBuffers(c.dev, &ca, &cb));
    VkQueryPoolCreateInfo qi{VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO}; qi.queryType = VK_QUERY_TYPE_TIMESTAMP; qi.queryCount = 2;
    VkQueryPool qp; CK(vkCreateQueryPool(c.dev, &qi, nullptr, &qp));
    VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    CK(vkBeginCommandBuffer(cb, &bi));
    vkCmdResetQueryPool(cb, qp, 0, 2);
    vkCmdBindPipeline(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.p);
    vkCmdBindDescriptorSets(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.pl, 0, 1, &p.ds, 0, nullptr);
    vkCmdPushConstants(cb, p.pl, VK_SHADER_STAGE_COMPUTE_BIT, 0, pcSize, pcData);
    vkCmdWriteTimestamp(cb, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, qp, 0);
    vkCmdDispatch(cb, groups, 1, 1);
    vkCmdWriteTimestamp(cb, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, qp, 1);
    CK(vkEndCommandBuffer(cb));
    VkFenceCreateInfo fi{VK_STRUCTURE_TYPE_FENCE_CREATE_INFO}; VkFence fence; CK(vkCreateFence(c.dev, &fi, nullptr, &fence));
    VkSubmitInfo si{VK_STRUCTURE_TYPE_SUBMIT_INFO}; si.commandBufferCount = 1; si.pCommandBuffers = &cb;
    auto t0 = std::chrono::steady_clock::now();
    CK(vkQueueSubmit(c.q, 1, &si, fence));
    CK(vkWaitForFences(c.dev, 1, &fence, VK_TRUE, UINT64_MAX));
    wallMs = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
    uint64_t ts[2] = {0, 0};
    vkGetQueryPoolResults(c.dev, qp, 0, 2, sizeof(ts), ts, 8, VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT);
    gpuMs = (ts[1] - ts[0]) * c.props.limits.timestampPeriod / 1e6;
    vkDestroyFence(c.dev, fence, nullptr); vkDestroyQueryPool(c.dev, qp, nullptr); vkDestroyCommandPool(c.dev, pool, nullptr);
}

struct Case { uint32_t instr, q, i, mac, status, p[3], vs[4], vt[4], acc[4], dst[4]; };
struct Exp { uint32_t out[4], mac, status, p[2]; };
struct Out { uint32_t o[4], mac, status, ok, p1; };

int main(int argc, char **argv)
{
    if (argc < 3) { std::fprintf(stderr, "usage: host test <spv> <cases.bin> | host bench <spv> <threads> <iters> <reps>\n"); return 2; }
    Ctx c = init();
    std::printf("device=%s api=%u.%u timestampPeriod=%.3f\n", c.props.deviceName, VK_API_VERSION_MAJOR(c.props.apiVersion), VK_API_VERSION_MINOR(c.props.apiVersion), c.props.limits.timestampPeriod);
    if (!std::strcmp(argv[1], "test"))
    {
        auto raw = readFile(argv[3]);
        size_t n = raw.size() / (sizeof(Case) + sizeof(Exp));
        const Case *cs = (const Case *)raw.data(); const Exp *ex = (const Exp *)(raw.data() + n * sizeof(Case));
        Buf in = mkbuf(c, n * sizeof(Case)), out = mkbuf(c, n * sizeof(Out));
        std::memcpy(in.p, cs, n * sizeof(Case)); std::memset(out.p, 0xCD, n * sizeof(Out));
        Pipe p = mkpipe(c, argv[2], in, out, 4);
        uint32_t nn = (uint32_t)n; double g, w; run(c, p, &nn, 4, (nn + 63) / 64, g, w);
        const Out *os = (const Out *)out.p;
        uint64_t bad = 0, badVal = 0, badMac = 0, badStat = 0, notOk = 0;
        uint64_t byOp[64] = {0}, totOp[64] = {0};
        for (size_t k = 0; k < n; ++k)
        {
            bool v = std::memcmp(os[k].o, ex[k].out, 16) != 0, m = os[k].mac != ex[k].mac, s = os[k].status != ex[k].status;
            uint32_t opk = cs[k].instr & 0x3F; opk = opk < 0x3C ? opk : 0x30 + (((cs[k].instr >> 6) & 0xF) % 16);
            totOp[opk & 63]++;
            notOk += os[k].ok == 0;
            if (v || m || s)
            {
                ++bad; badVal += v; badMac += m; badStat += s; byOp[opk & 63]++;
                if (bad <= 12)
                    std::printf("MISMATCH case %zu instr %08x vs %08x %08x %08x %08x vt %08x %08x %08x %08x acc %08x %08x %08x %08x q %08x i %08x\n"
                                "   gpu %08x %08x %08x %08x mac %04x st %03x | ref %08x %08x %08x %08x mac %04x st %03x\n",
                                k, cs[k].instr, cs[k].vs[0], cs[k].vs[1], cs[k].vs[2], cs[k].vs[3], cs[k].vt[0], cs[k].vt[1], cs[k].vt[2], cs[k].vt[3],
                                cs[k].acc[0], cs[k].acc[1], cs[k].acc[2], cs[k].acc[3], cs[k].q, cs[k].i,
                                os[k].o[0], os[k].o[1], os[k].o[2], os[k].o[3], os[k].mac, os[k].status,
                                ex[k].out[0], ex[k].out[1], ex[k].out[2], ex[k].out[3], ex[k].mac, ex[k].status);
            }
        }
        std::printf("test cases=%zu mismatches=%llu (value %llu, mac %llu, status %llu) not_decoded=%llu gpu_ms=%.3f wall_ms=%.3f\n",
                    n, (unsigned long long)bad, (unsigned long long)badVal, (unsigned long long)badMac, (unsigned long long)badStat,
                    (unsigned long long)notOk, g, w);
        return bad != 0;
    }
    // bench
    uint32_t threads = std::atoi(argv[3]), iters = std::atoi(argv[4]), reps = argc > 5 ? std::atoi(argv[5]) : 5;
    Buf in = mkbuf(c, 64), out = mkbuf(c, (VkDeviceSize)threads * 16);
    float m[16] = {0.9f, 0.1f, -0.2f, 0.0f, 0.05f, 1.1f, 0.3f, 0.0f, 0.2f, -0.1f, 0.95f, 0.0f, 10.f, -5.f, 20.f, 1.0f};
    std::memcpy(in.p, m, 64);
    Pipe p = mkpipe(c, argv[2], in, out, 4);
    double best = 1e30, sum = 0; double w = 0, g = 0;
    run(c, p, &iters, 4, threads / 64, g, w); // warm-up
    for (uint32_t r = 0; r < reps; ++r) { run(c, p, &iters, 4, threads / 64, g, w); best = g < best ? g : best; sum += g; }
    const double ops = (double)threads * iters * 4.0;  // FMAC instructions (4 lanes each)
    uint32_t chk = 0; for (uint32_t k = 0; k < threads; ++k) chk ^= ((uint32_t *)out.p)[k * 4];
    std::printf("bench %s threads=%u iters=%u reps=%u gpu_ms_best=%.3f gpu_ms_mean=%.3f fmac_ops=%.3g Gops/s_best=%.2f ns_per_vertex_transform=%.4f chk=%08x\n",
                argv[2], threads, iters, reps, best, sum / reps, ops, ops / best / 1e6, best * 1e6 / ((double)threads * iters), chk);
    return 0;
}
