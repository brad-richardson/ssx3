// G27 Vulkan descriptor-buffer properties probe (G27-original, session file).
// Evaluates the EXACT Granite guards (context.cpp:2271-2286,
// memory_allocator.cpp:835,1424) on Odin3/Adreno: descriptorBuffer
// feature, the three supports_descriptor_buffer sub-conditions, and
// the init-vs-use mismatch verdict. Links system libvulkan only.
#include <stdio.h>
#include <string.h>
#include <vulkan/vulkan.h>

int main(void) {
  VkApplicationInfo app = { VK_STRUCTURE_TYPE_APPLICATION_INFO };
  app.apiVersion = VK_API_VERSION_1_3;
  VkInstanceCreateInfo ici = { VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO };
  ici.pApplicationInfo = &app;
  VkInstance inst;
  if (vkCreateInstance(&ici, NULL, &inst) != VK_SUCCESS) {
    printf("G27-VKPROBE: vkCreateInstance FAILED\n");
    return 2;
  }
  uint32_t ngpu = 0;
  vkEnumeratePhysicalDevices(inst, &ngpu, NULL);
  printf("G27-VKPROBE: ngpu=%u\n", ngpu);
  VkPhysicalDevice gpus[4];
  vkEnumeratePhysicalDevices(inst, &ngpu, gpus);
  for (uint32_t g = 0; g < ngpu; g++) {
    VkPhysicalDeviceProperties2 props2 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2 };
    VkPhysicalDeviceDescriptorBufferPropertiesEXT dbprops;
    memset(&dbprops, 0, sizeof(dbprops));
    dbprops.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DESCRIPTOR_BUFFER_PROPERTIES_EXT;
    props2.pNext = &dbprops;
    vkGetPhysicalDeviceProperties2(gpus[g], &props2);
    VkPhysicalDeviceFeatures2 feats2 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2 };
    VkPhysicalDeviceDescriptorBufferFeaturesEXT dbfeats;
    memset(&dbfeats, 0, sizeof(dbfeats));
    dbfeats.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DESCRIPTOR_BUFFER_FEATURES_EXT;
    feats2.pNext = &dbfeats;
    vkGetPhysicalDeviceFeatures2(gpus[g], &feats2);
    printf("G27-VKPROBE: gpu%u name=%.64s\n", g, props2.properties.deviceName);
    printf("G27-VKPROBE: descriptorBuffer_feature=%u\n", dbfeats.descriptorBuffer);
    printf("G27-VKPROBE: samplerDescriptorSize=%u sampledImageDescriptorSize=%u storageImageDescriptorSize=%u\n",
           (unsigned)dbprops.samplerDescriptorSize, (unsigned)dbprops.sampledImageDescriptorSize,
           (unsigned)dbprops.storageImageDescriptorSize);
    printf("G27-VKPROBE: combinedImageSamplerDescriptorSingleArray=%u\n",
           (unsigned)dbprops.combinedImageSamplerDescriptorSingleArray);
    printf("G27-VKPROBE: maxSamplerRange=%llu maxResourceRange=%llu\n",
           (unsigned long long)dbprops.maxSamplerDescriptorBufferRange,
           (unsigned long long)dbprops.maxResourceDescriptorBufferRange);
    unsigned long long max_heap = dbprops.maxSamplerDescriptorBufferRange <
                                  dbprops.maxResourceDescriptorBufferRange
                                  ? dbprops.maxSamplerDescriptorBufferRange
                                  : dbprops.maxResourceDescriptorBufferRange;
    int c1 = (unsigned long long)dbprops.samplerDescriptorSize * 512ull * 1024ull <= max_heap;
    int c2 = (unsigned long long)dbprops.sampledImageDescriptorSize * 512ull * 1024ull <= max_heap;
    int c3 = dbprops.combinedImageSamplerDescriptorSingleArray != 0;
    printf("G27-VKPROBE: max_heap=%llu c1_sampler512K=%d c2_sampled512K=%d c3_singleArray=%d\n",
           max_heap, c1, c2, c3);
    printf("G27-VKPROBE: supports_descriptor_buffer=%d use_branch_1424=%d MISMATCH=%d\n",
           (c1 && c2 && c3), (dbfeats.descriptorBuffer != 0),
           ((dbfeats.descriptorBuffer != 0) && !(c1 && c2 && c3)));
  }
  printf("G27-VKPROBE: done exit=0\n");
  return 0;
}
