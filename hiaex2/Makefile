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
HIAEX2_SOURCES = hiaex2/HiAEx2.c hiaex2/HiAEx2_aesni_avx.c hiaex2/HiAEx2_arm.c hiaex2/HiAEx2_arm_sha3.c hiaex2/HiAEx2_software.c hiaex2/HiAEx2_stream.c hiaex2/HiAEx2_vaes_avx2.c
HIAEX2_HEADERS = HiAEx2.h hiaex2/HiAEx2_internal.h hiaex2/softaes.h common/common.h common/cpu.h

TEST_SOURCES = encrypt.c test.c $(HIAEX2_SOURCES)
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)
TEST_TARGET = hiaex2_test

BENCH_SOURCES = encrypt.c benchmark.c $(HIAEX2_SOURCES)
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = hiaex2_benchmark

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

encrypt.o: encrypt.c crypto_aead.h api.h HiAEx2.h
test.o: test.c crypto_aead.h api.h
benchmark.o: benchmark.c crypto_aead.h api.h timing.h
$(HIAEX2_SOURCES:.c=.o): $(HIAEX2_HEADERS)
