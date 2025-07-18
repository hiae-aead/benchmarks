#ifndef TIMING_H
#define TIMING_H

#define _GNU_SOURCE  /* For posix_memalign */

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#    include <windows.h>
#    ifdef _MSC_VER
#        include <intrin.h>
#    endif
#elif defined(__APPLE__)
#    include <mach/mach_time.h>
#    include <sys/time.h>
#elif defined(_POSIX_VERSION) && (_POSIX_VERSION >= 199309L)
#    include <sys/time.h>
#    include <time.h>
#else
#    include <sys/time.h>
#endif

#if defined(__x86_64__) || defined(__i386__) || defined(_M_X64) || defined(_M_IX86)
#    define HAS_RDTSC 1
#endif

#if defined(__aarch64__) || defined(__arm__)
#    define HAS_ARM_COUNTER 1
#endif

typedef struct {
    double   start_time;
    double   end_time;
    uint64_t start_cycles;
    uint64_t end_cycles;
    int      has_cycles;
} rocca_timer_t;

typedef struct {
    double *values;
    size_t  count;
    size_t  capacity;
    double  min;
    double  max;
    double  sum;
    double  mean;
    double  median;
    double  stddev;
} rocca_stats_t;

static inline double
rocca_get_time(void)
{
#ifdef _WIN32
    LARGE_INTEGER freq, count;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&count);
    return (double) count.QuadPart / (double) freq.QuadPart;
#elif defined(__APPLE__)
    static mach_timebase_info_data_t timebase = { 0 };
    if (timebase.denom == 0) {
        mach_timebase_info(&timebase);
    }
    uint64_t time = mach_absolute_time();
    return (double) time * timebase.numer / timebase.denom / 1e9;
#elif defined(_POSIX_VERSION) && (_POSIX_VERSION >= 199309L)
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        return ts.tv_sec + ts.tv_nsec / 1e9;
    }
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1e6;
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1e6;
#endif
}

#ifdef HAS_RDTSC
static inline uint64_t
rocca_read_cycles(void)
{
#    if defined(__x86_64__) || defined(__i386__)
    uint32_t lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t) hi << 32) | lo;
#    elif defined(_M_X64) || defined(_M_IX86)
    return __rdtsc();
#    else
    return 0;
#    endif
}
#elif defined(HAS_ARM_COUNTER)
static inline uint64_t
rocca_read_cycles(void)
{
#    if defined(__aarch64__)
    uint64_t val;
    __asm__ __volatile__("mrs %0, cntvct_el0" : "=r"(val));
    return val;
#    else
    return 0;
#    endif
}
#else
static inline uint64_t
rocca_read_cycles(void)
{
    return 0;
}
#endif

static inline int
rocca_has_cycle_counter(void)
{
#if defined(HAS_RDTSC) || defined(HAS_ARM_COUNTER)
    return 1;
#else
    return 0;
#endif
}

static inline void
rocca_timer_start(rocca_timer_t *timer)
{
    timer->has_cycles = rocca_has_cycle_counter();
    if (timer->has_cycles) {
        timer->start_cycles = rocca_read_cycles();
        timer->end_cycles   = timer->start_cycles;
    }
    timer->start_time = rocca_get_time();
    timer->end_time   = timer->start_time;
}

static inline void
rocca_timer_stop(rocca_timer_t *timer)
{
    timer->end_time = rocca_get_time();
    if (timer->has_cycles) {
        timer->end_cycles = rocca_read_cycles();
    }
}

static inline double
rocca_timer_elapsed_seconds(const rocca_timer_t *timer)
{
    return timer->end_time - timer->start_time;
}

static inline uint64_t
rocca_timer_elapsed_cycles(const rocca_timer_t *timer)
{
    if (!timer->has_cycles)
        return 0;
    return timer->end_cycles - timer->start_cycles;
}

static inline double
rocca_get_cpu_frequency(void)
{
    if (!rocca_has_cycle_counter())
        return 0.0;

    const int iterations         = 5;
    double    freq_sum           = 0.0;
    int       valid_measurements = 0;

    for (int i = 0; i < iterations; i++) {
        rocca_timer_t timer;

        double target_time = 0.01; // 10ms
        rocca_timer_start(&timer);
        double start = rocca_get_time();

        while ((rocca_get_time() - start) < target_time) {
#ifdef _MSC_VER
            _ReadWriteBarrier();
#else
            __asm__ __volatile__("" ::: "memory");
#endif
        }

        rocca_timer_stop(&timer);

        double   elapsed = rocca_timer_elapsed_seconds(&timer);
        uint64_t cycles  = rocca_timer_elapsed_cycles(&timer);

        if (elapsed > 0 && cycles > 0) {
            double freq = cycles / elapsed;
            if (freq > 1e8 && freq < 1e10) {
                freq_sum += freq;
                valid_measurements++;
            }
        }
    }

    if (valid_measurements > 0) {
        return freq_sum / valid_measurements;
    }
    return 0.0;
}

static inline rocca_stats_t *
rocca_stats_create(size_t initial_capacity)
{
    rocca_stats_t *stats = (rocca_stats_t *) malloc(sizeof(rocca_stats_t));
    if (!stats)
        return NULL;

    stats->values = (double *) malloc(initial_capacity * sizeof(double));
    if (!stats->values) {
        free(stats);
        return NULL;
    }

    stats->capacity = initial_capacity;
    stats->count    = 0;
    stats->min      = INFINITY;
    stats->max      = -INFINITY;
    stats->sum      = 0.0;
    stats->mean     = 0.0;
    stats->median   = 0.0;
    stats->stddev   = 0.0;

    return stats;
}

static inline void
rocca_stats_destroy(rocca_stats_t *stats)
{
    if (stats) {
        free(stats->values);
        free(stats);
    }
}

static inline void
rocca_stats_add(rocca_stats_t *stats, double value)
{
    if (stats->count >= stats->capacity) {
        size_t  new_capacity = stats->capacity * 2;
        double *new_values   = (double *) realloc(stats->values, new_capacity * sizeof(double));
        if (!new_values)
            return;
        stats->values   = new_values;
        stats->capacity = new_capacity;
    }

    stats->values[stats->count++] = value;
    stats->sum += value;
    if (value < stats->min)
        stats->min = value;
    if (value > stats->max)
        stats->max = value;
}

static inline int
double_compare(const void *a, const void *b)
{
    double diff = *(double *) a - *(double *) b;
    return (diff > 0) - (diff < 0);
}

static inline void
rocca_stats_compute(rocca_stats_t *stats)
{
    if (stats->count == 0)
        return;

    stats->mean = stats->sum / stats->count;

    double *sorted = (double *) malloc(stats->count * sizeof(double));
    if (!sorted)
        return;
    memcpy(sorted, stats->values, stats->count * sizeof(double));
    qsort(sorted, stats->count, sizeof(double), double_compare);

    if (stats->count % 2 == 0) {
        stats->median = (sorted[stats->count / 2 - 1] + sorted[stats->count / 2]) / 2.0;
    } else {
        stats->median = sorted[stats->count / 2];
    }

    double variance = 0.0;
    for (size_t i = 0; i < stats->count; i++) {
        double diff = stats->values[i] - stats->mean;
        variance += diff * diff;
    }
    stats->stddev = sqrt(variance / stats->count);

    free(sorted);
}

static inline void *
rocca_aligned_alloc(size_t alignment, size_t size)
{
#ifdef _WIN32
    return _aligned_malloc(size, alignment);
#else
    void *ptr;
    if (posix_memalign(&ptr, alignment, size) != 0) {
        return NULL;
    }
    return ptr;
#endif
}

static inline void
rocca_aligned_free(void *ptr)
{
#ifdef _WIN32
    _aligned_free(ptr);
#else
    free(ptr);
#endif
}

#endif