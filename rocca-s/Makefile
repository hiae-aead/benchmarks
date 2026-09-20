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
TEST_TARGET = rocca-s_test
TEST_SOURCES = test.c rocca-s.c

.PHONY: all test clean

all: $(TEST_TARGET) $(TARGET)

$(TARGET): $(SOURCES) rocca-s.h timing.h
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(LDFLAGS)

$(TEST_TARGET): $(TEST_SOURCES) rocca-s.h
	$(CC) $(CFLAGS) -o $@ $(TEST_SOURCES) $(LDFLAGS)

test: $(TEST_TARGET)
	./$(TEST_TARGET)

clean:
	rm -f $(TEST_TARGET) $(TARGET)
