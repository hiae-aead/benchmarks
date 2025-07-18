#ifndef CRYPTO_VERIFY_32_H
#define CRYPTO_VERIFY_32_H

static inline int crypto_verify_32(const unsigned char *x, const unsigned char *y)
{
    unsigned int differentbits = 0;
    int i;
    for (i = 0; i < 32; ++i) {
        differentbits |= x[i] ^ y[i];
    }
    return (1 & ((differentbits - 1) >> 8)) - 1;
}

#endif