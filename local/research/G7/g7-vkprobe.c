// G7 Odin Vulkan capability probe — replicates the paraLLEl-GS gate at
// gs/gs_renderer.cpp:807-817 + Granite Device::supports_subgroup_size_log2
// (Granite/vulkan/device.cpp:5808-5850) with args (true, 2, 6, COMPUTE).
// Read-only device queries; no surface, no queues, no shaders.
#include <stdio.h>
#include <string.h>
#include <vulkan/vulkan.h>

int main(void)
{
	uint32_t inst_ver = 0;
	vkEnumerateInstanceVersion(&inst_ver);
	printf("instanceVersion=%u.%u.%u\n", VK_VERSION_MAJOR(inst_ver),
	       VK_VERSION_MINOR(inst_ver), VK_VERSION_PATCH(inst_ver));

	VkApplicationInfo app = { VK_STRUCTURE_TYPE_APPLICATION_INFO, NULL,
		"g7probe", 1, "g7probe", 1, VK_API_VERSION_1_3 };
	VkInstanceCreateInfo ici = { VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
		NULL, 0, &app, 0, NULL, 0, NULL };
	VkInstance inst;
	if (vkCreateInstance(&ici, NULL, &inst) != VK_SUCCESS) {
		printf("CREATE_INSTANCE_FAIL\n");
		return 1;
	}

	uint32_t ndev = 0;
	vkEnumeratePhysicalDevices(inst, &ndev, NULL);
	printf("physicalDevices=%u\n", ndev);
	VkPhysicalDevice devs[8];
	if (ndev > 8) ndev = 8;
	vkEnumeratePhysicalDevices(inst, &ndev, devs);

	for (uint32_t d = 0; d < ndev; d++) {
		VkPhysicalDeviceVulkan11Features f11 = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_FEATURES, NULL };
		VkPhysicalDeviceVulkan12Features f12 = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES, &f11 };
		VkPhysicalDeviceVulkan13Features f13 = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES, &f12 };
		VkPhysicalDeviceFeatures2 f2 = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2, &f13 };
		vkGetPhysicalDeviceFeatures2(devs[d], &f2);

		VkPhysicalDeviceVulkan11Properties p11 = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_PROPERTIES, NULL };
		VkPhysicalDeviceVulkan13Properties p13 = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_PROPERTIES, &p11 };
		VkPhysicalDeviceDriverProperties drv = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DRIVER_PROPERTIES, &p13 };
		VkPhysicalDeviceProperties2 p2 = {
			VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2, &drv };
		vkGetPhysicalDeviceProperties2(devs[d], &p2);
		VkPhysicalDeviceProperties *P = &p2.properties;

		printf("--- device %u ---\n", d);
		printf("deviceName=%s\n", P->deviceName);
		printf("deviceType=%u apiVersion=%u.%u.%u driverID=%u driverName=%s driverInfo=%s\n",
		       P->deviceType, VK_VERSION_MAJOR(P->apiVersion),
		       VK_VERSION_MINOR(P->apiVersion), VK_VERSION_PATCH(P->apiVersion),
		       drv.driverID, drv.driverName, drv.driverInfo);
		printf("vendorID=0x%x deviceID=0x%x\n", P->vendorID, P->deviceID);

		// Gate items, one line each: name=value (1/0 or raw).
		printf("descriptorIndexing=%d\n", !!f12.descriptorIndexing);
		printf("timelineSemaphore=%d\n", !!f12.timelineSemaphore);
		printf("bufferDeviceAddress=%d\n", !!f12.bufferDeviceAddress);
		printf("storageBuffer8BitAccess=%d\n", !!f12.storageBuffer8BitAccess);
		printf("storageBuffer16BitAccess=%d\n", !!f11.storageBuffer16BitAccess);
		printf("shaderInt16=%d\n", !!f2.features.shaderInt16);
		printf("scalarBlockLayout=%d\n", !!f12.scalarBlockLayout);
		VkSubgroupFeatureFlags need =
			VK_SUBGROUP_FEATURE_ARITHMETIC_BIT | VK_SUBGROUP_FEATURE_SHUFFLE_BIT |
			VK_SUBGROUP_FEATURE_VOTE_BIT | VK_SUBGROUP_FEATURE_BALLOT_BIT |
			VK_SUBGROUP_FEATURE_BASIC_BIT;
		printf("subgroupOps=0x%x need=0x%x have_all=%d subgroupSize=%u\n",
		       p11.subgroupSupportedOperations, need,
		       ((p11.subgroupSupportedOperations & need) == need),
		       p11.subgroupSize);
		printf("subgroupSizeControl=%d computeFullSubgroups=%d minSubgroupSize=%u maxSubgroupSize=%u requiredStages=0x%x\n",
		       !!f13.subgroupSizeControl, !!f13.computeFullSubgroups,
		       p13.minSubgroupSize, p13.maxSubgroupSize,
		       p13.requiredSubgroupSizeStages);
		// Predicate replica: (true, 2, 6, COMPUTE).
		int pred = 0;
		if (f13.subgroupSizeControl && f13.computeFullSubgroups) {
			uint32_t mn = 1u << 2, mx = 1u << 6;
			if (mn <= p13.minSubgroupSize && mx >= p13.maxSubgroupSize)
				pred = 1; // full_range
			else if (!(mn > p13.maxSubgroupSize || mx < p13.minSubgroupSize))
				pred = (p13.requiredSubgroupSizeStages &
				        VK_SHADER_STAGE_COMPUTE_BIT) != 0;
		}
		printf("subgroup_pred_log2_2_6_compute=%d\n", pred);
		printf("maxComputeSharedMemorySize=%u ge32k=%d\n",
		       P->limits.maxComputeSharedMemorySize,
		       P->limits.maxComputeSharedMemorySize >= 32 * 1024);
	}
	vkDestroyInstance(inst, NULL);
	printf("DONE\n");
	return 0;
}
