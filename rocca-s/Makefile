# Allow overriding compiler and flags from command line
CC ?= clang
CFLAGS ?= -O3 -march=native -std=c99
LDFLAGS ?=
LDFLAGS += -lm
TARGET = performance_test
SOURCES = performance_test.c rocca-s_ref.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET)
