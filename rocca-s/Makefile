# Allow overriding compiler and flags from command line
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

CFLAGS += -std=c99 -I.
LDFLAGS += -lm

TARGET = rocca-s_benchmark
SOURCES = performance_test.c rocca-s.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET)
