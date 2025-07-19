# Allow overriding compiler and flags from command line
CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99
LDFLAGS ?=
LDFLAGS += -lm

# Detect architecture and select appropriate implementation
ARCH := $(shell uname -m)
ifeq ($(ARCH),arm64)
    ROCCA_IMPL = rocca-s_arm.c
else ifeq ($(ARCH),aarch64)
    ROCCA_IMPL = rocca-s_arm.c
else
    ROCCA_IMPL = rocca-s_ref.c
endif

TARGET = performance_test
SOURCES = performance_test.c $(ROCCA_IMPL)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET)
