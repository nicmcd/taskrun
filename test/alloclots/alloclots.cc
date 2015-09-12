#include <cstdint>
#include <cstdio>
#include <cstdlib>

#include <string>
#include <thread>
#include <vector>

void usage(const char* exe) {
  printf("usage:\n  %s block_size usleep num_blocks\n", exe);
}

int main(int argc, char** argv) {
  for (int i = 0; i < argc; i++) {
    if ((std::string(argv[i]) == "-h") ||
        (std::string(argv[i]) == "--help") ||
        (argc != 4)) {
      usage(argv[0]);
      return -1;
    }
  }

  char* ep;
  uint64_t blockSize = strtoull(argv[1], &ep, 0);
  if (*ep != '\0') {
    printf("invalid block_size: %s\n", argv[1]);
    usage(argv[0]);
    return -1;
  }
  uint64_t usleep = strtoull(argv[2], &ep, 0);
  if (*ep != '\0') {
    printf("invalid usleep: %s\n", argv[2]);
    usage(argv[0]);
    return -1;
  }
  uint64_t numBlocks = strtoull(argv[3], &ep, 0);
  if (*ep != '\0') {
    printf("invalid num_blocks: %s\n", argv[3]);
    usage(argv[0]);
    return -1;
  }

  std::vector<uint8_t*> ptrs(numBlocks, NULL);;
  uint64_t blocks = 0;
  uint64_t total = 0;
  printf("+blocks=%lu total=%lu\n", blocks, total);
  for (uint8_t*& ptr : ptrs) {
    ptr = new uint8_t[blockSize];
    for (uint64_t p = 0; p < blockSize; p += 4096) {
      ptr[p] = 123;
    }
    if (blockSize % 4096 != 0) {
      uint64_t p = (blockSize / 4096) * 4096;
      ptr[p] = 123;
    }
    blocks++;
    total += blockSize;
    printf("+blocks=%lu total=%lu\n", blocks, total);
    std::this_thread::sleep_for(std::chrono::microseconds(usleep));
  }
  printf("all allocated\n");

  for (uint8_t*& ptr : ptrs) {
    delete[] ptr;
    blocks--;
    total -= blockSize;
    printf("-blocks=%lu total=%lu\n", blocks, total);
    std::this_thread::sleep_for(std::chrono::microseconds(usleep));
  }

  return 0;
}
