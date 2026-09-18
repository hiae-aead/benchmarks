# Allow overriding compiler and flags from command line
# Use clang if it's installed, unless another compiler was asked for
ifeq ($(origin CC),default)
    CC := $(if $(shell command -v clang 2>/dev/null),clang,cc)
endif

CFLAGS ?= -O3 -march=native
LDFLAGS ?=

# Detect architecture and set appropriate flags
ARCH := $(shell uname -m)
ifeq ($(ARCH),x86_64)
    CFLAGS += -mavx2 -mvaes -maes
endif
CFLAGS += -std=c99

# Source files
SOURCES = encrypt.c test.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = aegis-128x2-vaes_test

# Benchmark files
BENCH_SOURCES = encrypt.c benchmark.c
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = aegis-128x2-vaes_benchmark

# Default target
all: $(TARGET) $(BENCH_TARGET)

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
encrypt.o: encrypt.c api.h common.h 128x2-common.h
benchmark.o: benchmark.c crypto_aead.h timing.h
