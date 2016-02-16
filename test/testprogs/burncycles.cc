#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

#include <chrono>
#include <string>

void usage(const char* exe) {
  printf("usage:\n  %s seconds granularity\n", exe);
}

int main(int argc, char** argv) {
  setbuf(stdout, nullptr);
  setbuf(stderr, nullptr);

  for (int i = 0; i < argc; i++) {
    if ((std::string(argv[i]) == "-h") ||
        (std::string(argv[i]) == "--help") ||
        (argc != 3)) {
      usage(argv[0]);
      return -1;
    }
  }

  char* ep;
  double secs = strtod(argv[1], &ep);
  if (*ep != '\0') {
    printf("invalid seconds: %s\n", argv[1]);
    usage(argv[0]);
    return -1;
  }
  double gran = strtod(argv[2], &ep);
  if (*ep != '\0') {
    printf("invalid granularity: %s\n", argv[2]);
    usage(argv[0]);
    return -1;
  }

  std::chrono::steady_clock::time_point startTime =
      std::chrono::steady_clock::now();
  uint64_t lastCount = 0;
  volatile double a, b, c, d, e, f, z;

  while (true) {
    // do stupid math
    a = 1234.21342;
    b = 87.1243;
    c = 0.00000123;
    d = 1e7;
    e = 1.0;
    f = 97087.97124390701;
    z = ((1/c) * (1/d) + f / a + b / (e * 2.0));
    z *= 3.14159265359;

    // time time snap shot
    std::chrono::steady_clock::time_point endTime =
        std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsedDur =
        std::chrono::duration_cast<std::chrono::duration<double> >
        (endTime - startTime);
    double elapsed = elapsedDur.count();

    // check interval
    uint64_t currCount = std::floor(elapsed / gran);
    if (currCount > lastCount) {
      lastCount = currCount;
      printf("count=%lu\n", currCount);
    }

    // check if done
    if (elapsed > secs) {
      printf("completed\n");
      break;
    }
  }

  return 0;
}
