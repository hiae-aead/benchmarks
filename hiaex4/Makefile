# Use clang if it's installed, unless another compiler was asked for
ifeq ($(origin CC),default)
    CC := $(if $(shell command -v clang 2>/dev/null),clang,cc)
endif

LDFLAGS ?=

ARCH := $(shell uname -m)
ifeq ($(ARCH),arm64)
    CFLAGS ?= -O3 -mcpu=native
else ifeq ($(ARCH),aarch64)
    CFLAGS ?= -O3 -mcpu=native
else
    CFLAGS ?= -O3 -march=native
endif

# Kept out of CFLAGS, so that overriding CFLAGS doesn't break the build
BUILD_CFLAGS = $(CFLAGS) -std=c99 -I.

# Copied from libhiae
HIAEX4_SOURCES = hiaex4/HiAEx4.c hiaex4/HiAEx4_arm.c hiaex4/HiAEx4_arm_sha3.c hiaex4/HiAEx4_software.c hiaex4/HiAEx4_stream.c hiaex4/HiAEx4_vaes_avx512.c
HIAEX4_HEADERS = HiAEx4.h hiaex4/HiAEx4_internal.h hiaex4/HiAEx4_stream_xor.h hiaex4/softaes.h common/common.h common/cpu.h

TEST_SOURCES = encrypt.c test.c $(HIAEX4_SOURCES)
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)
TEST_TARGET = hiaex4_test

BENCH_SOURCES = encrypt.c benchmark.c $(HIAEX4_SOURCES)
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = hiaex4_benchmark

all: $(TEST_TARGET) $(BENCH_TARGET)

$(TEST_TARGET): $(TEST_OBJECTS)
	$(CC) $(TEST_OBJECTS) -o $(TEST_TARGET) $(LDFLAGS)

$(BENCH_TARGET): $(BENCH_OBJECTS)
	$(CC) $(BENCH_OBJECTS) -o $(BENCH_TARGET) $(LDFLAGS) -lm

%.o: %.c
	$(CC) $(BUILD_CFLAGS) -c $< -o $@

clean:
	rm -f $(TEST_OBJECTS) $(BENCH_OBJECTS) $(TEST_TARGET) $(BENCH_TARGET)

.PHONY: all clean

encrypt.o: encrypt.c crypto_aead.h api.h HiAEx4.h
test.o: test.c crypto_aead.h api.h HiAEx4.h
benchmark.o: benchmark.c crypto_aead.h api.h timing.h
$(HIAEX4_SOURCES:.c=.o): $(HIAEX4_HEADERS)
