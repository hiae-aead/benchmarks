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

CFLAGS += -std=c99 -fomit-frame-pointer -Wall -I.
LDFLAGS += -lm

# Use pkg-config for OpenSSL if available
ifneq ($(shell pkg-config --exists libcrypto && echo yes),)
CFLAGS += $(shell pkg-config --cflags libcrypto)
LDFLAGS += $(shell pkg-config --libs libcrypto)
else
LDFLAGS += -lcrypto
endif

# Source files
SOURCES = encrypt.c
BENCHMARK_SOURCES = benchmark.c
TEST_SOURCES = test.c

# Object files
OBJECTS = $(SOURCES:.c=.o)
BENCHMARK_OBJECTS = $(BENCHMARK_SOURCES:.c=.o)
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)

# Targets
BENCHMARK = aes128-gcm-openssl_benchmark
TEST = aes128-gcm-openssl_test

all: $(BENCHMARK) $(TEST)

$(BENCHMARK): $(BENCHMARK_OBJECTS) $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(TEST): $(TEST_OBJECTS) $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJECTS) $(BENCHMARK_OBJECTS) $(TEST_OBJECTS) $(BENCHMARK) $(TEST)

.PHONY: all clean
