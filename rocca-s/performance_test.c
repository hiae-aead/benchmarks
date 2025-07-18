#define _GNU_SOURCE  /* For posix_memalign */

#include "rocca-s.h"
#include "timing.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BASE_ITERATIONS  10000
#define WARMUP_TIME      0.25 // 0.25s warmup
#define COMPUTATION_TIME 1.0  // 1s computation time for measurements
#define NUM_MEASUREMENTS 5    // Number of measurement runs

const int len_test_case = 11;
size_t    test_case[11] = { 65536, 32768, 16384, 8192, 4096, 2048, 1024, 512, 256, 64, 16 };

static int csv_output = 0;

typedef struct {
    double        gbps;
    double        mbps;
    double        cycles_per_byte;
    rocca_stats_t *stats;
} perf_result_t;

static size_t
calculate_iterations(double warmup_time, size_t warmup_iterations)
{
    if (warmup_time <= 0 || warmup_iterations == 0) {
        return 100;
    }

    double iterations_per_second = (double) warmup_iterations / warmup_time;
    size_t target_iterations     = (size_t) (iterations_per_second * COMPUTATION_TIME);

    if (target_iterations < 10)
        target_iterations = 10;
    if (target_iterations > 100000)
        target_iterations = 100000;

    return target_iterations;
}

perf_result_t
speed_test_ad_work(size_t len)
{
    perf_result_t result = { 0 };

    uint8_t key[ROCCA_KEY_SIZE];
    memset(key, 1, ROCCA_KEY_SIZE);
    uint8_t iv[ROCCA_IV_SIZE];
    memset(iv, 1, ROCCA_IV_SIZE);

    uint8_t *ad = rocca_aligned_alloc(16, len);
    if (!ad) {
        fprintf(stderr, "Failed to allocate memory\n");
        return result;
    }
    memset(ad, 1, len);

    uint8_t tag[ROCCA_TAG_SIZE];
    rocca_context ctx;

    // Warmup phase
    rocca_timer_t warmup_timer;
    rocca_timer_start(&warmup_timer);
    size_t warmup_iterations = 0;

    do {
        rocca_init(&ctx, key, iv);
        rocca_add_ad(&ctx, ad, len);
        rocca_tag(&ctx, tag);
        warmup_iterations++;
        rocca_timer_stop(&warmup_timer);
    } while (rocca_timer_elapsed_seconds(&warmup_timer) < WARMUP_TIME);

    double warmup_time                = rocca_timer_elapsed_seconds(&warmup_timer);
    size_t iterations_per_measurement = calculate_iterations(warmup_time, warmup_iterations);

    result.stats = rocca_stats_create(NUM_MEASUREMENTS);
    if (!result.stats) {
        rocca_aligned_free(ad);
        return result;
    }

    for (int i = 0; i < NUM_MEASUREMENTS; i++) {
        rocca_timer_t timer;
        rocca_timer_start(&timer);

        for (size_t iter = 0; iter < iterations_per_measurement; iter++) {
            rocca_init(&ctx, key, iv);
            rocca_add_ad(&ctx, ad, len);
            rocca_tag(&ctx, tag);
        }

        rocca_timer_stop(&timer);

        double elapsed    = rocca_timer_elapsed_seconds(&timer);
        double throughput = ((double) iterations_per_measurement * len) / elapsed;
        rocca_stats_add(result.stats, throughput);
    }

    rocca_stats_compute(result.stats);

    result.mbps = result.stats->median / (1024.0 * 1024.0);
    result.gbps = (result.stats->median * 8.0) / 1e9;

    if (rocca_has_cycle_counter()) {
        double cpu_freq = rocca_get_cpu_frequency();
        if (cpu_freq > 0) {
            result.cycles_per_byte = cpu_freq / result.stats->median;
        }
    }

    rocca_aligned_free(ad);
    return result;
}

perf_result_t
speed_test_encode_work(size_t len, int AEAD)
{
    perf_result_t result = { 0 };

    uint8_t key[ROCCA_KEY_SIZE];
    memset(key, 1, ROCCA_KEY_SIZE);
    uint8_t iv[ROCCA_IV_SIZE];
    memset(iv, 1, ROCCA_IV_SIZE);

    size_t   ad_len = AEAD ? 48 : 0;
    uint8_t *ad     = NULL;
    if (ad_len > 0) {
        ad = rocca_aligned_alloc(16, ad_len);
        if (!ad) {
            fprintf(stderr, "Failed to allocate AD memory\n");
            return result;
        }
        memset(ad, 1, ad_len);
    }

    uint8_t *msg = rocca_aligned_alloc(16, len);
    uint8_t *ct  = rocca_aligned_alloc(16, len);
    if (!msg || !ct) {
        fprintf(stderr, "Failed to allocate memory\n");
        rocca_aligned_free(ad);
        rocca_aligned_free(msg);
        rocca_aligned_free(ct);
        return result;
    }
    memset(msg, 0x1, len);

    uint8_t tag[ROCCA_TAG_SIZE];
    rocca_context ctx;

    // Warmup phase
    rocca_timer_t warmup_timer;
    rocca_timer_start(&warmup_timer);
    size_t warmup_iterations = 0;

    do {
        rocca_init(&ctx, key, iv);
        if (ad) rocca_add_ad(&ctx, ad, ad_len);
        rocca_encrypt(&ctx, ct, msg, len);
        rocca_tag(&ctx, tag);
        warmup_iterations++;
        rocca_timer_stop(&warmup_timer);
    } while (rocca_timer_elapsed_seconds(&warmup_timer) < WARMUP_TIME);

    double warmup_time                = rocca_timer_elapsed_seconds(&warmup_timer);
    size_t iterations_per_measurement = calculate_iterations(warmup_time, warmup_iterations);

    result.stats = rocca_stats_create(NUM_MEASUREMENTS);
    if (!result.stats) {
        rocca_aligned_free(ad);
        rocca_aligned_free(msg);
        rocca_aligned_free(ct);
        return result;
    }

    for (int i = 0; i < NUM_MEASUREMENTS; i++) {
        rocca_timer_t timer;
        rocca_timer_start(&timer);

        for (size_t iter = 0; iter < iterations_per_measurement; iter++) {
            rocca_init(&ctx, key, iv);
            if (ad) rocca_add_ad(&ctx, ad, ad_len);
            rocca_encrypt(&ctx, ct, msg, len);
            rocca_tag(&ctx, tag);
        }

        rocca_timer_stop(&timer);

        double elapsed    = rocca_timer_elapsed_seconds(&timer);
        double throughput = ((double) iterations_per_measurement * len) / elapsed;
        rocca_stats_add(result.stats, throughput);
    }

    rocca_stats_compute(result.stats);

    result.mbps = result.stats->median / (1024.0 * 1024.0);
    result.gbps = (result.stats->median * 8.0) / 1e9;

    if (rocca_has_cycle_counter()) {
        double cpu_freq = rocca_get_cpu_frequency();
        if (cpu_freq > 0) {
            result.cycles_per_byte = cpu_freq / result.stats->median;
        }
    }

    rocca_aligned_free(ad);
    rocca_aligned_free(msg);
    rocca_aligned_free(ct);
    return result;
}

perf_result_t
speed_test_decode_work(size_t len, int AEAD)
{
    perf_result_t result = { 0 };

    uint8_t key[ROCCA_KEY_SIZE];
    memset(key, 1, ROCCA_KEY_SIZE);
    uint8_t iv[ROCCA_IV_SIZE];
    memset(iv, 1, ROCCA_IV_SIZE);

    size_t   ad_len = AEAD ? 48 : 0;
    uint8_t *ad     = NULL;
    if (ad_len > 0) {
        ad = rocca_aligned_alloc(16, ad_len);
        if (!ad) {
            fprintf(stderr, "Failed to allocate AD memory\n");
            return result;
        }
        memset(ad, 1, ad_len);
    }

    uint8_t *msg = rocca_aligned_alloc(16, len);
    uint8_t *ct  = rocca_aligned_alloc(16, len);
    uint8_t *dec = rocca_aligned_alloc(16, len);
    if (!msg || !ct || !dec) {
        fprintf(stderr, "Failed to allocate memory\n");
        rocca_aligned_free(ad);
        rocca_aligned_free(msg);
        rocca_aligned_free(ct);
        rocca_aligned_free(dec);
        return result;
    }
    memset(msg, 0x1, len);

    uint8_t tag[ROCCA_TAG_SIZE];
    rocca_context ctx;

    // First encrypt to get ciphertext
    rocca_init(&ctx, key, iv);
    if (ad) rocca_add_ad(&ctx, ad, ad_len);
    rocca_encrypt(&ctx, ct, msg, len);
    rocca_tag(&ctx, tag);

    // Warmup phase
    rocca_timer_t warmup_timer;
    rocca_timer_start(&warmup_timer);
    size_t warmup_iterations = 0;

    do {
        rocca_init(&ctx, key, iv);
        if (ad) rocca_add_ad(&ctx, ad, ad_len);
        rocca_decrypt(&ctx, dec, ct, len);
        rocca_tag(&ctx, tag);
        warmup_iterations++;
        rocca_timer_stop(&warmup_timer);
    } while (rocca_timer_elapsed_seconds(&warmup_timer) < WARMUP_TIME);

    double warmup_time                = rocca_timer_elapsed_seconds(&warmup_timer);
    size_t iterations_per_measurement = calculate_iterations(warmup_time, warmup_iterations);

    result.stats = rocca_stats_create(NUM_MEASUREMENTS);
    if (!result.stats) {
        rocca_aligned_free(ad);
        rocca_aligned_free(msg);
        rocca_aligned_free(ct);
        rocca_aligned_free(dec);
        return result;
    }

    for (int i = 0; i < NUM_MEASUREMENTS; i++) {
        rocca_timer_t timer;
        rocca_timer_start(&timer);

        for (size_t iter = 0; iter < iterations_per_measurement; iter++) {
            rocca_init(&ctx, key, iv);
            if (ad) rocca_add_ad(&ctx, ad, ad_len);
            rocca_decrypt(&ctx, dec, ct, len);
            rocca_tag(&ctx, tag);
        }

        rocca_timer_stop(&timer);

        double elapsed    = rocca_timer_elapsed_seconds(&timer);
        double throughput = ((double) iterations_per_measurement * len) / elapsed;
        rocca_stats_add(result.stats, throughput);
    }

    rocca_stats_compute(result.stats);

    result.mbps = result.stats->median / (1024.0 * 1024.0);
    result.gbps = (result.stats->median * 8.0) / 1e9;

    if (rocca_has_cycle_counter()) {
        double cpu_freq = rocca_get_cpu_frequency();
        if (cpu_freq > 0) {
            result.cycles_per_byte = cpu_freq / result.stats->median;
        }
    }

    rocca_aligned_free(ad);
    rocca_aligned_free(msg);
    rocca_aligned_free(ct);
    rocca_aligned_free(dec);
    return result;
}

void
print_result(const char *operation, size_t len, perf_result_t *result)
{
    if (csv_output) {
        printf("%zu,%s,%.2f,%.2f", len, operation, result->gbps, result->mbps);

        if (result->cycles_per_byte > 0) {
            printf(",%.2f", result->cycles_per_byte);
        } else {
            printf(",");
        }

        if (result->stats) {
            double cv = (result->stats->stddev / result->stats->mean) * 100.0;
            printf(",%.2f\n", cv);
        } else {
            printf(",\n");
        }
    } else {
        printf("%-8zu | %-10s | %8.2f | %8.2f", len, operation, result->gbps, result->mbps);

        if (result->cycles_per_byte > 0) {
            printf(" | %6.2f", result->cycles_per_byte);
        } else {
            printf(" |    N/A");
        }

        if (result->stats) {
            double cv = (result->stats->stddev / result->stats->mean) * 100.0;
            printf(" | %5.2f%%\n", cv);
        } else {
            printf(" |    N/A\n");
        }
    }
}

void
speed_test_encryption(void)
{
    if (csv_output) {
        printf("\n# Encryption Only Performance\n");
        printf("Size,Operation,Gbps,MB/s,Cycles/Byte,CV%%\n");
    } else {
        printf("\n================ Encryption Only Performance ================\n");
        printf("Size     | Operation  |   Gbps   |   MB/s   | cyc/B  | CV%%\n");
        printf("---------|------------|----------|----------|--------|-------\n");
    }

    for (int i = 0; i < len_test_case; i++) {
        perf_result_t enc_result = speed_test_encode_work(test_case[i], 0);
        perf_result_t dec_result = speed_test_decode_work(test_case[i], 0);

        print_result("encrypt", test_case[i], &enc_result);
        print_result("decrypt", test_case[i], &dec_result);

        rocca_stats_destroy(enc_result.stats);
        rocca_stats_destroy(dec_result.stats);

        if (!csv_output && i < len_test_case - 1) {
            printf("---------|------------|----------|----------|--------|-------\n");
        }
    }
}

void
speed_test_ad_only(void)
{
    if (csv_output) {
        printf("\n# AD Only (MAC) Performance\n");
        printf("Size,Operation,Gbps,MB/s,Cycles/Byte,CV%%\n");
    } else {
        printf("\n================ AD Only (MAC) Performance ==================\n");
        printf("Size     | Operation  |   Gbps   |   MB/s   | cyc/B  | CV%%\n");
        printf("---------|------------|----------|----------|--------|-------\n");
    }

    for (int i = 0; i < len_test_case; i++) {
        perf_result_t result = speed_test_ad_work(test_case[i]);
        print_result("MAC", test_case[i], &result);
        rocca_stats_destroy(result.stats);
    }
}

void
speed_test_aead(void)
{
    if (csv_output) {
        printf("\n# AEAD Performance\n");
        printf("Size,Operation,Gbps,MB/s,Cycles/Byte,CV%%\n");
    } else {
        printf("\n================== AEAD Performance =========================\n");
        printf("Size     | Operation  |   Gbps   |   MB/s   | cyc/B  | CV%%\n");
        printf("---------|------------|----------|----------|--------|-------\n");
    }

    for (int i = 0; i < len_test_case; i++) {
        perf_result_t enc_result = speed_test_encode_work(test_case[i], 1);
        perf_result_t dec_result = speed_test_decode_work(test_case[i], 1);

        print_result("encrypt", test_case[i], &enc_result);
        print_result("decrypt", test_case[i], &dec_result);

        rocca_stats_destroy(enc_result.stats);
        rocca_stats_destroy(dec_result.stats);

        if (!csv_output && i < len_test_case - 1) {
            printf("---------|------------|----------|----------|--------|-------\n");
        }
    }
}

static void
show_usage(const char *program_name)
{
    printf("Usage: %s [options]\n", program_name);
    printf("Options:\n");
    printf("  --csv           Output results in CSV format\n");
    printf("  --help, -h      Show this help message\n");
}

int
main(int argc, char *argv[])
{
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--csv") == 0) {
            csv_output = 1;
        } else if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            show_usage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "Error: Unknown option '%s'\n\n", argv[i]);
            show_usage(argv[0]);
            return 1;
        }
    }

    if (csv_output) {
        printf("# ROCCA-S Performance Test\n");
    } else {
        printf("=============================================================\n");
        printf("                   ROCCA-S Performance Test                  \n");
        printf("=============================================================\n");
    }

    double       timer_resolution = 1.0;
    rocca_timer_t res_timer;
    for (int i = 0; i < 100; i++) {
        rocca_timer_start(&res_timer);
        rocca_timer_stop(&res_timer);
        double elapsed = rocca_timer_elapsed_seconds(&res_timer);
        if (elapsed > 0 && elapsed < timer_resolution) {
            timer_resolution = elapsed;
        }
    }
    if (csv_output) {
        printf("# Timer resolution: ~%.2f ns\n", timer_resolution * 1e9);

        if (rocca_has_cycle_counter()) {
            double cpu_freq = rocca_get_cpu_frequency();
            if (cpu_freq > 0) {
                printf("# CPU frequency: ~%.2f GHz\n", cpu_freq / 1e9);
            }
        }
    } else {
        printf("Timer resolution: ~%.2f ns\n", timer_resolution * 1e9);

        if (rocca_has_cycle_counter()) {
            double cpu_freq = rocca_get_cpu_frequency();
            if (cpu_freq > 0) {
                printf("CPU frequency: ~%.2f GHz\n", cpu_freq / 1e9);
            }
        }

        printf("\nNote: CV%% = Coefficient of Variation (std dev / mean * 100)\n");
        printf("      Lower CV%% indicates more consistent performance\n");
    }

    speed_test_encryption();
    speed_test_ad_only();
    speed_test_aead();

    if (!csv_output) {
        printf("\n=============================================================\n");
    }

    return 0;
}