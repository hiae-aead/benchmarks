CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99 -I.
LDFLAGS ?=

# HiAEx2 modular source files
HIAEX2_SOURCES = hiaex2/HiAEx2.c hiaex2/HiAEx2_aesni_avx.c hiaex2/HiAEx2_arm.c hiaex2/HiAEx2_arm_sha3.c hiaex2/HiAEx2_software.c hiaex2/HiAEx2_stream.c hiaex2/HiAEx2_vaes_avx2.c

# Source files
SOURCES = encrypt.c $(HIAEX2_SOURCES)
OBJECTS = $(SOURCES:.c=.o)
TARGET = hiaex2_test

# Test files
TEST_SOURCES = test.c
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)
TEST_TARGET = hiaex2_test

# Benchmark files
BENCH_SOURCES = encrypt.c benchmark.c $(HIAEX2_SOURCES)
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = hiaex2_benchmark

# Default target
all: $(TEST_TARGET) $(BENCH_TARGET)

# Build the test target
$(TEST_TARGET): $(TEST_OBJECTS)
	$(CC) $(TEST_OBJECTS) -o $(TEST_TARGET) $(LDFLAGS)

# Build the benchmark target
$(BENCH_TARGET): $(BENCH_OBJECTS)
	$(CC) $(BENCH_OBJECTS) -o $(BENCH_TARGET) $(LDFLAGS) -lm

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TEST_OBJECTS) $(BENCH_OBJECTS) $(TEST_TARGET) $(BENCH_TARGET)

# Phony targets
.PHONY: all clean

# Dependencies
encrypt.o: encrypt.c crypto_aead.h api.h HiAEx2.h
test.o: test.c crypto_aead.h api.h
benchmark.o: benchmark.c crypto_aead.h timing.h
$(HIAEX2_SOURCES:.c=.o): HiAEx2.h hiaex2/HiAEx2_internal.h