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
HIAE_SOURCES = hiae/HiAE.c hiae/HiAE_aesni.c hiae/HiAE_arm.c hiae/HiAE_arm_sha3.c hiae/HiAE_software.c hiae/HiAE_stream.c hiae/HiAE_vaes_avx512.c
HIAE_HEADERS = HiAE.h hiae/HiAE_internal.h hiae/HiAE_stream_xor.h hiae/softaes.h common/common.h common/cpu.h

TEST_SOURCES = encrypt.c test.c $(HIAE_SOURCES)
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)
TEST_TARGET = hiae_test

BENCH_SOURCES = encrypt.c benchmark.c $(HIAE_SOURCES)
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = hiae_benchmark

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

encrypt.o: encrypt.c crypto_aead.h api.h HiAE.h
test.o: test.c crypto_aead.h api.h HiAE.h
benchmark.o: benchmark.c crypto_aead.h api.h timing.h
$(HIAE_SOURCES:.c=.o): $(HIAE_HEADERS)
