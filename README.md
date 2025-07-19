# IETF Cryptographic Benchmarks

This repository contains cryptographic benchmarking implementations for various AEAD (Authenticated Encryption with Associated Data) algorithms designed for high-performance, both on ARM and Intel CPUs.

## Included Algorithms

- **AEGIS-128x2** variants
- **AES-128-GCM** (OpenSSL backend)
- **HiAE**
- **ROCCA-S** cipher

## Quick Start

Each algorithm is in its own directory with consistent build system:

```bash
cd <algorithm-directory>
make                    # Build test and benchmark executables
./<algorithm>_test      # Run functionality tests
./<algorithm>_benchmark # Run performance benchmarks
```

**Performance Recommendation:** For optimal performance, use `clang` as your compiler:

```bash
CC=clang make
```

Clang typically produces faster cryptographic code than GCC due to better optimization of vectorized operations and loop unrolling.

## Performance Testing

Benchmarks test multiple message sizes (64B to 64KB) and measure:
- Throughput (Gbps/Mbps)
- Cycles per byte
- Cross-platform performance characteristics
