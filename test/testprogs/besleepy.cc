#include <cmath>
#include <csignal>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

#include <chrono>
#include <string>
#include <thread>

void usage(const char* exe) {
  printf("usage:\n  %s seconds granularity\n", exe);
}

void signalHandler(int signum) {
  if (signum == SIGABRT) {
    printf("got SIGABRT\n");
  } else if (signum == SIGINT) {
    printf("got SIGINT\n");
  } else if (signum == SIGTERM) {
    printf("got SIGTERM\n");
  }
  exit(-1);
}

int main(int argc, char** argv) {
  setbuf(stdout, nullptr);
  setbuf(stderr, nullptr);

  signal(SIGABRT, signalHandler);
  signal(SIGINT, signalHandler);
  signal(SIGTERM, signalHandler);

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

  uint64_t microsleep = static_cast<uint64_t>(gran * 1e6);
  for (int64_t remaining = static_cast<int64_t>(secs / gran);
       remaining > 0; remaining--) {
    std::this_thread::sleep_for(std::chrono::microseconds(microsleep));
    printf("remaining=%li\n", remaining);
  }

  return 0;
}
