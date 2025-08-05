# Allow overriding compiler and flags from command line
CC ?= clang
CFLAGS ?= -O3 -std=c99
LDFLAGS ?=
LDFLAGS += -lm

# Detect architecture and select appropriate implementation
ARCH := $(shell uname -m)

# Add ARM crypto extensions for ARM builds
ifeq ($(ARCH),arm64)
    CFLAGS += -march=native+crypto
else ifeq ($(ARCH),aarch64)
    CFLAGS += -march=native+crypto
else
    CFLAGS += -march=native
endif
TARGET = rocca-s_benchmark
SOURCES = performance_test.c rocca-s.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET)
