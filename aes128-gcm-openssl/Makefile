# Allow overriding compiler and flags from command line
CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99
CFLAGS += -fomit-frame-pointer -Wall -I.
LDFLAGS ?=
LDFLAGS += -lcrypto -lm

# Source files
SOURCES = encrypt.c
BENCHMARK_SOURCES = benchmark.c
TEST_SOURCES = test.c

# Object files
OBJECTS = $(SOURCES:.c=.o)
BENCHMARK_OBJECTS = $(BENCHMARK_SOURCES:.c=.o)
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)

# Targets
BENCHMARK = aes_gcm_benchmark
TEST = aes_gcm_test

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
