CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99 -I.
LDFLAGS ?=

# HiAEx4 modular source files
HIAEX4_SOURCES = hiaex4/HiAEx4.c hiaex4/HiAEx4_arm.c hiaex4/HiAEx4_arm_sha3.c hiaex4/HiAEx4_software.c hiaex4/HiAEx4_stream.c hiaex4/HiAEx4_vaes_avx512.c

# Source files
SOURCES = encrypt.c $(HIAEX4_SOURCES)
OBJECTS = $(SOURCES:.c=.o)
TARGET = hiaex4_test

# Test files
TEST_SOURCES = test.c
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)
TEST_TARGET = hiaex4_test

# Benchmark files
BENCH_SOURCES = encrypt.c benchmark.c $(HIAEX4_SOURCES)
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = hiaex4_benchmark

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
encrypt.o: encrypt.c crypto_aead.h api.h HiAEx4.h
test.o: test.c crypto_aead.h api.h
benchmark.o: benchmark.c crypto_aead.h timing.h
$(HIAEX4_SOURCES:.c=.o): HiAEx4.h hiaex4/HiAEx4_internal.h