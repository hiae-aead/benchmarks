CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99
LDFLAGS ?= 

# Detect architecture
ARCH := $(shell uname -m)

# Source files
SOURCES = encrypt.c test.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = aegis_test

# Benchmark files
BENCH_SOURCES = encrypt.c benchmark.c
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = aegis_benchmark

# Default target
ifeq ($(findstring arm,$(ARCH))$(findstring aarch64,$(ARCH)),)
all:
	@echo "Warning: This implementation is for ARM architecture only."
	@echo "Current architecture: $(ARCH)"
	@echo "Skipping build on non-ARM platform."
else
all: $(TARGET) $(BENCH_TARGET)
endif

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
ifeq ($(findstring arm,$(ARCH))$(findstring aarch64,$(ARCH)),)
clean:
	@echo "Nothing to clean on non-ARM platform."
else
clean:
	rm -f $(OBJECTS) $(BENCH_OBJECTS) $(TARGET) $(BENCH_TARGET)
endif

# Phony targets
.PHONY: all clean

# Dependencies
encrypt.o: encrypt.c api.h common.h 128x2-common.h
benchmark.o: benchmark.c crypto_aead.h timing.h
