# Top-level Makefile for IETF Cryptographic Benchmarks
# Builds all available algorithm implementations

# Detect architecture
ARCH := $(shell uname -m)

# Check compiler and warn if not using clang
ifeq ($(findstring clang,$(CC)),)
    $(info Warning: Using $(CC) compiler. For optimal performance, consider using clang: CC=clang make)
endif

# Directory list for algorithm implementations
INTEL_DIRS = aegis-128x2-aesni aegis-128x2-vaes aegis-128x4-avx512
COMMON_DIRS = aes128-gcm-openssl hiae hiaex2 hiaex4 rocca-s
ARM_DIRS = aegis-128x2-arm

# Check for OpenSSL availability
OPENSSL_AVAILABLE := $(shell pkg-config --exists libcrypto && echo yes)

.PHONY: all clean help benchmark benchmark-csv $(INTEL_DIRS) $(COMMON_DIRS) $(ARM_DIRS)

all: build-common build-intel build-arm

# Build common implementations (work on all architectures)
build-common: $(COMMON_DIRS)

# Build Intel-specific implementations
build-intel:
ifeq ($(findstring x86_64,$(ARCH))$(findstring amd64,$(ARCH))$(findstring i386,$(ARCH))$(findstring i686,$(ARCH)),)
	@echo "Skipping Intel-specific implementations on $(ARCH) architecture"
else
	@$(MAKE) $(INTEL_DIRS)
endif

# Build ARM-specific implementations
build-arm:
ifeq ($(findstring arm,$(ARCH))$(findstring aarch64,$(ARCH)),)
	@echo "Skipping ARM implementations on $(ARCH) architecture"
else
	@$(MAKE) $(ARM_DIRS)
endif

# Individual algorithm targets
aegis-128x2-aesni:
	@echo "Building AEGIS-128x2 (AES-NI)..."
	@$(MAKE) -C $@ all

aegis-128x2-vaes:
	@echo "Building AEGIS-128x2 (VAES)..."
	@$(MAKE) -C $@ all

aegis-128x4-avx512:
	@echo "Building AEGIS-128x4 (AVX-512)..."
	@$(MAKE) -C $@ all

aes128-gcm-openssl:
ifeq ($(OPENSSL_AVAILABLE),yes)
	@echo "Building AES-128-GCM (OpenSSL)..."
	@$(MAKE) -C $@ all
else
	@echo "Warning: OpenSSL not found, skipping AES-128-GCM implementation"
endif

hiae:
	@echo "Building HiAE..."
	@$(MAKE) -C $@ all

hiaex2:
	@echo "Building HiAEx2..."
	@$(MAKE) -C $@ all

hiaex4:
	@echo "Building HiAEx4..."
	@$(MAKE) -C $@ all

rocca-s:
	@echo "Building ROCCA-S..."
	@$(MAKE) -C $@ all

aegis-128x2-arm:
	@echo "Building AEGIS-128x2 (ARM)..."
	@$(MAKE) -C $@ all

# Clean all implementations
clean:
	@echo "Cleaning all implementations..."
	@for dir in $(INTEL_DIRS) $(COMMON_DIRS) $(ARM_DIRS); do \
		echo "Cleaning $$dir..."; \
		$(MAKE) -C $$dir clean; \
	done

# Test all built executables
test: all
	@echo "Running tests for all implementations..."
	@for dir in $(COMMON_DIRS); do \
		if [ -x "$$dir/$${dir}_test" ]; then \
			echo "Testing $$dir..."; \
			cd $$dir && ./$${dir}_test && cd ..; \
		elif [ "$$dir" = "hiae" ]; then \
			echo "Skipping $$dir (no test executable)"; \
		elif [ "$$dir" = "rocca-s" ]; then \
			echo "Skipping $$dir (benchmark only)"; \
		fi; \
	done
ifneq ($(findstring x86_64,$(ARCH))$(findstring amd64,$(ARCH))$(findstring i386,$(ARCH))$(findstring i686,$(ARCH)),)
	@for dir in $(INTEL_DIRS); do \
		if [ -x "$$dir/$${dir}_test" ]; then \
			echo "Testing $$dir..."; \
			cd $$dir && ./$${dir}_test && cd ..; \
		fi; \
	done
endif
ifneq ($(findstring arm,$(ARCH))$(findstring aarch64,$(ARCH)),)
	@for dir in $(ARM_DIRS); do \
		if [ -x "$$dir/$${dir}_test" ]; then \
			echo "Testing $$dir..."; \
			cd $$dir && ./$${dir}_test && cd ..; \
		fi; \
	done
endif

# Benchmark all built executables
# Force -march=native for optimal performance benchmarks
benchmark:
	@echo "Building benchmarks with -march=native for optimal performance..."
	@$(MAKE) all
	@echo "Running benchmarks for all implementations..."
	@for dir in $(COMMON_DIRS); do \
		if [ -x "$$dir/$${dir}_benchmark" ]; then \
			echo "Benchmarking $$dir..."; \
			cd $$dir && ./$${dir}_benchmark && cd ..; \
		fi; \
	done
ifneq ($(findstring x86_64,$(ARCH))$(findstring amd64,$(ARCH))$(findstring i386,$(ARCH))$(findstring i686,$(ARCH)),)
	@for dir in $(INTEL_DIRS); do \
		if [ -x "$$dir/$${dir}_benchmark" ]; then \
			echo "Benchmarking $$dir..."; \
			cd $$dir && ./$${dir}_benchmark && cd ..; \
		fi; \
	done
endif
ifneq ($(findstring arm,$(ARCH))$(findstring aarch64,$(ARCH)),)
	@for dir in $(ARM_DIRS); do \
		if [ -x "$$dir/$${dir}_benchmark" ]; then \
			echo "Benchmarking $$dir..."; \
			cd $$dir && ./$${dir}_benchmark && cd ..; \
		fi; \
	done
endif

# Run benchmarks with CSV output and save results
benchmark-csv:
	@echo "Building benchmarks with -march=native for optimal performance..."
	@$(MAKE) all
	@CSV_DIR="benchmark-results-$$(date +%Y%m%d-%H%M%S)"; \
	echo "Creating directory $$CSV_DIR for CSV results..."; \
	mkdir -p $$CSV_DIR; \
	echo "Running benchmarks with CSV output..."; \
	for dir in $(COMMON_DIRS); do \
		if [ -x "$$dir/$${dir}_benchmark" ]; then \
			echo "Benchmarking $$dir (CSV)..."; \
			cd $$dir && ./$${dir}_benchmark --csv > ../$$CSV_DIR/$${dir}.csv && cd ..; \
			echo "  Saved to $$CSV_DIR/$${dir}.csv"; \
		fi; \
	done; \
	ARCH_CHECK="$(findstring x86_64,$(ARCH))$(findstring amd64,$(ARCH))$(findstring i386,$(ARCH))$(findstring i686,$(ARCH))"; \
	if [ -n "$$ARCH_CHECK" ]; then \
		for dir in $(INTEL_DIRS); do \
			if [ -x "$$dir/$${dir}_benchmark" ]; then \
				echo "Benchmarking $$dir (CSV)..."; \
				cd $$dir && ./$${dir}_benchmark --csv > ../$$CSV_DIR/$${dir}.csv && cd ..; \
				echo "  Saved to $$CSV_DIR/$${dir}.csv"; \
			fi; \
		done; \
	fi; \
	ARM_CHECK="$(findstring arm,$(ARCH))$(findstring aarch64,$(ARCH))"; \
	if [ -n "$$ARM_CHECK" ]; then \
		for dir in $(ARM_DIRS); do \
			if [ -x "$$dir/$${dir}_benchmark" ]; then \
				echo "Benchmarking $$dir (CSV)..."; \
				cd $$dir && ./$${dir}_benchmark --csv > ../$$CSV_DIR/$${dir}.csv && cd ..; \
				echo "  Saved to $$CSV_DIR/$${dir}.csv"; \
			fi; \
		done; \
	fi; \
	echo ""; \
	echo "All CSV results saved to $$CSV_DIR/"

# Help target
help:
	@echo "IETF Cryptographic Benchmarks Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all            - Build all available implementations"
	@echo "  clean          - Clean all build artifacts"
	@echo "  test           - Run tests for all built implementations"
	@echo "  benchmark      - Run benchmarks for all built implementations"
	@echo "  benchmark-csv  - Run benchmarks with CSV output to timestamped directory"
	@echo "  help           - Show this help message"
	@echo ""
	@echo "Individual algorithm targets:"
	@echo "  aegis-128x2-aesni    - AEGIS-128x2 with AES-NI"
	@echo "  aegis-128x2-vaes     - AEGIS-128x2 with VAES"
	@echo "  aegis-128x2-arm      - AEGIS-128x2 for ARM (ARM only)"
	@echo "  aes128-gcm-openssl   - AES-128-GCM with OpenSSL"
	@echo "  hiae                 - HiAE algorithm"
	@echo "  hiaex2               - HiAEx2 algorithm"
	@echo "  hiaex4               - HiAEx4 algorithm"
	@echo "  rocca-s              - ROCCA-S stream cipher"
	@echo ""
	@echo "Architecture: $(ARCH)"
ifeq ($(OPENSSL_AVAILABLE),yes)
	@echo "OpenSSL: Available"
else
	@echo "OpenSSL: Not found (AES-GCM will be skipped)"
endif
