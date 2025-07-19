CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99 -I.
LDFLAGS ?=

# HiAE modular source files
HIAE_SOURCES = hiae/HiAE.c hiae/HiAE_aesni.c hiae/HiAE_arm.c hiae/HiAE_arm_sha3.c hiae/HiAE_software.c hiae/HiAE_stream.c hiae/HiAE_vaes_avx512.c

# Source files
SOURCES = encrypt.c $(HIAE_SOURCES)
OBJECTS = $(SOURCES:.c=.o)
TARGET = hiae_test

# Benchmark files
BENCH_SOURCES = encrypt.c benchmark.c $(HIAE_SOURCES)
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = hiae_benchmark

# Default target
all: $(BENCH_TARGET)

# Build the main target
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Build the benchmark target
$(BENCH_TARGET): $(BENCH_OBJECTS)
	$(CC) $(BENCH_OBJECTS) -o $(BENCH_TARGET) $(LDFLAGS) -lm

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(BENCH_OBJECTS) $(TARGET) $(BENCH_TARGET)

# Phony targets
.PHONY: all clean

# Dependencies
encrypt.o: encrypt.c crypto_aead.h api.h HiAE.h
benchmark.o: benchmark.c crypto_aead.h timing.h
$(HIAE_SOURCES:.c=.o): HiAE.h hiae/HiAE_internal.h
