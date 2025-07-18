CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99
LDFLAGS ?=

# Source files
SOURCES = encrypt.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = hiae_test

# Benchmark files
BENCH_SOURCES = encrypt.c benchmark.c
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
encrypt.o: encrypt.c crypto_aead.h api.h HiAE_amalgamated.c
benchmark.o: benchmark.c crypto_aead.h timing.h
