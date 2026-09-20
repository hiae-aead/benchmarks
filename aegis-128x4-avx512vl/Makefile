ifeq ($(origin CC),default)
    CC := $(if $(shell command -v clang 2>/dev/null),clang,cc)
endif

CFLAGS ?= -O3 -march=native
LDFLAGS ?=

COMMON_DIR = ../aegis-128x4-avx512

ARCH := $(shell uname -m)
ifeq ($(ARCH),x86_64)
    CFLAGS += -mavx512f -mavx512vl -mvaes -maes
else
    $(warning This implementation requires x86_64 with AVX512F, AVX512VL, VAES and AES support)
    $(warning Build will likely fail on $(ARCH) architecture)
endif

CFLAGS += -std=c99

SOURCES = encrypt.c test.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = aegis-128x4-avx512vl_test

BENCH_SOURCES = encrypt.c benchmark.c
BENCH_OBJECTS = $(BENCH_SOURCES:.c=.o)
BENCH_TARGET = aegis-128x4-avx512vl_benchmark

all: $(TARGET) $(BENCH_TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

$(BENCH_TARGET): $(BENCH_OBJECTS)
	$(CC) $(BENCH_OBJECTS) -o $(BENCH_TARGET) $(LDFLAGS) -lm

%.o: %.c
	$(CC) -I$(COMMON_DIR) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(BENCH_OBJECTS) $(TARGET) $(BENCH_TARGET)

.PHONY: all clean

encrypt.o: encrypt.c $(addprefix $(COMMON_DIR)/,api.h common.h crypto_aead.h crypto_declassify.h crypto_verify_16.h crypto_verify_32.h 128x4-common.h)
test.o: test.c $(addprefix $(COMMON_DIR)/,test.c crypto_aead.h api.h)
benchmark.o: benchmark.c $(addprefix $(COMMON_DIR)/,benchmark.c crypto_aead.h timing.h api.h)
