#define RATE 128

static inline void
aegis128x4_init(const uint8_t *key, const uint8_t *nonce, aes_block_t *const state)
{
    static CRYPTO_ALIGN(64) const uint8_t c0_[AES_BLOCK_LENGTH] = {
        0x00, 0x01, 0x01, 0x02, 0x03, 0x05, 0x08, 0x0d, 0x15, 0x22, 0x37, 0x59, 0x90,
        0xe9, 0x79, 0x62, 0x00, 0x01, 0x01, 0x02, 0x03, 0x05, 0x08, 0x0d, 0x15, 0x22,
        0x37, 0x59, 0x90, 0xe9, 0x79, 0x62, 0x00, 0x01, 0x01, 0x02, 0x03, 0x05, 0x08,
        0x0d, 0x15, 0x22, 0x37, 0x59, 0x90, 0xe9, 0x79, 0x62, 0x00, 0x01, 0x01, 0x02,
        0x03, 0x05, 0x08, 0x0d, 0x15, 0x22, 0x37, 0x59, 0x90, 0xe9, 0x79, 0x62,
    };
    static CRYPTO_ALIGN(64) const uint8_t c1_[AES_BLOCK_LENGTH] = {
        0xdb, 0x3d, 0x18, 0x55, 0x6d, 0xc2, 0x2f, 0xf1, 0x20, 0x11, 0x31, 0x42, 0x73,
        0xb5, 0x28, 0xdd, 0xdb, 0x3d, 0x18, 0x55, 0x6d, 0xc2, 0x2f, 0xf1, 0x20, 0x11,
        0x31, 0x42, 0x73, 0xb5, 0x28, 0xdd, 0xdb, 0x3d, 0x18, 0x55, 0x6d, 0xc2, 0x2f,
        0xf1, 0x20, 0x11, 0x31, 0x42, 0x73, 0xb5, 0x28, 0xdd, 0xdb, 0x3d, 0x18, 0x55,
        0x6d, 0xc2, 0x2f, 0xf1, 0x20, 0x11, 0x31, 0x42, 0x73, 0xb5, 0x28, 0xdd,
    };

    const aes_block_t        c0 = AES_BLOCK_LOAD(c0_);
    const aes_block_t        c1 = AES_BLOCK_LOAD(c1_);
    CRYPTO_ALIGN(64) uint8_t context_bytes[AES_BLOCK_LENGTH];
    aes_block_t              context;
    aes_block_t              k;
    aes_block_t              n;
    int                      i;

    k = AES_BLOCK_BROADCAST128(key);
    n = AES_BLOCK_BROADCAST128(nonce);

    memset(context_bytes, 0, sizeof context_bytes);
    context_bytes[0 * 16]     = 0x00;
    context_bytes[0 * 16 + 1] = 0x03;
    context_bytes[1 * 16]     = 0x01;
    context_bytes[1 * 16 + 1] = 0x03;
    context_bytes[2 * 16]     = 0x02;
    context_bytes[2 * 16 + 1] = 0x03;
    context_bytes[3 * 16]     = 0x03;
    context_bytes[3 * 16 + 1] = 0x03;
    context                   = AES_BLOCK_LOAD(context_bytes);

    state[0] = AES_BLOCK_XOR(k, n);
    state[1] = c1;
    state[2] = c0;
    state[3] = c1;
    state[4] = AES_BLOCK_XOR(k, n);
    state[5] = AES_BLOCK_XOR(k, c0);
    state[6] = AES_BLOCK_XOR(k, c1);
    state[7] = AES_BLOCK_XOR(k, c0);
    for (i = 0; i < 10; i++) {
        state[3] = AES_BLOCK_XOR(state[3], context);
        state[7] = AES_BLOCK_XOR(state[7], context);
        aegis128x4_update(state, n, k);
    }
}

static inline void
aegis128x4_mac_fold(uint8_t *dst, const uint8_t *src)
{
    uint64_t lo = 0, hi = 0, x;
    int      i;

    for (i = 0; i < AES_BLOCK_LENGTH; i += 16) {
        memcpy(&x, src + i, 8);
        lo ^= x;
        memcpy(&x, src + i + 8, 8);
        hi ^= x;
    }
    memcpy(dst, &lo, 8);
    memcpy(dst + 8, &hi, 8);
}

static inline void
aegis128x4_mac(uint8_t *mac, size_t maclen, uint64_t adlen, uint64_t mlen, aes_block_t *const state)
{
    CRYPTO_ALIGN(64) uint8_t mac_multi_0[AES_BLOCK_LENGTH];
    CRYPTO_ALIGN(64) uint8_t mac_multi_1[AES_BLOCK_LENGTH];
    aes_block_t              tmp;
    int                      i;

    tmp = AES_BLOCK_LOAD_64x2(mlen << 3, adlen << 3);
    tmp = AES_BLOCK_XOR(tmp, state[2]);

    for (i = 0; i < 7; i++) {
        aegis128x4_update(state, tmp, tmp);
    }

    if (maclen == 16) {
        tmp = AES_BLOCK_XOR(state[6], AES_BLOCK_XOR(state[5], state[4]));
        tmp = AES_BLOCK_XOR(tmp, AES_BLOCK_XOR(state[3], state[2]));
        tmp = AES_BLOCK_XOR(tmp, AES_BLOCK_XOR(state[1], state[0]));
        AES_BLOCK_STORE(mac_multi_0, tmp);
        aegis128x4_mac_fold(mac, mac_multi_0);
    } else if (maclen == 32) {
        tmp = AES_BLOCK_XOR(state[3], state[2]);
        tmp = AES_BLOCK_XOR(tmp, AES_BLOCK_XOR(state[1], state[0]));
        AES_BLOCK_STORE(mac_multi_0, tmp);
        aegis128x4_mac_fold(mac, mac_multi_0);

        tmp = AES_BLOCK_XOR(state[7], state[6]);
        tmp = AES_BLOCK_XOR(tmp, AES_BLOCK_XOR(state[5], state[4]));
        AES_BLOCK_STORE(mac_multi_1, tmp);
        aegis128x4_mac_fold(mac + 16, mac_multi_1);
    } else {
        memset(mac, 0, maclen);
    }
}

static inline void
aegis128x4_absorb(const uint8_t *const src, aes_block_t *const state)
{
    aes_block_t msg0, msg1;

    msg0 = AES_BLOCK_LOAD(src);
    msg1 = AES_BLOCK_LOAD(src + AES_BLOCK_LENGTH);
    aegis128x4_update(state, msg0, msg1);
}

static inline void
aegis128x4_enc(uint8_t *const dst, const uint8_t *const src, aes_block_t *const state)
{
    aes_block_t msg0, msg1;
    aes_block_t tmp0, tmp1;

    msg0 = AES_BLOCK_LOAD(src);
    msg1 = AES_BLOCK_LOAD(src + AES_BLOCK_LENGTH);
    tmp0 = AES_BLOCK_XOR(msg0, state[6]);
    tmp0 = AES_BLOCK_XOR(tmp0, state[1]);
    tmp1 = AES_BLOCK_XOR(msg1, state[5]);
    tmp1 = AES_BLOCK_XOR(tmp1, state[2]);
    tmp0 = AES_BLOCK_XOR(tmp0, AES_BLOCK_AND(state[2], state[3]));
    tmp1 = AES_BLOCK_XOR(tmp1, AES_BLOCK_AND(state[6], state[7]));
    AES_BLOCK_STORE(dst, tmp0);
    AES_BLOCK_STORE(dst + AES_BLOCK_LENGTH, tmp1);

    aegis128x4_update(state, msg0, msg1);
}

static inline void
aegis128x4_xor_keystream(uint8_t *const dst, const uint8_t *const src, aes_block_t *const state)
{
    aes_block_t msg0, msg1;
    aes_block_t tmp0, tmp1, last;

    msg0 = AES_BLOCK_LOAD(src);
    msg1 = AES_BLOCK_LOAD(src + AES_BLOCK_LENGTH);
    tmp0 = AES_BLOCK_XOR(msg0, state[6]);
    tmp0 = AES_BLOCK_XOR(tmp0, state[1]);
    tmp1 = AES_BLOCK_XOR(msg1, state[5]);
    tmp1 = AES_BLOCK_XOR(tmp1, state[2]);
    tmp0 = AES_BLOCK_XOR(tmp0, AES_BLOCK_AND(state[2], state[3]));
    tmp1 = AES_BLOCK_XOR(tmp1, AES_BLOCK_AND(state[6], state[7]));
    AES_BLOCK_STORE(dst, tmp0);
    AES_BLOCK_STORE(dst + AES_BLOCK_LENGTH, tmp1);

    last     = state[7];
    state[7] = AES_ENC(state[6], state[7]);
    state[6] = AES_ENC(state[5], state[6]);
    state[5] = AES_ENC(state[4], state[5]);
    state[4] = AES_ENC(state[3], state[4]);
    state[3] = AES_ENC(state[2], state[3]);
    state[2] = AES_ENC(state[1], state[2]);
    state[1] = AES_ENC(state[0], state[1]);
    state[0] = AES_ENC(last, state[0]);
}

static inline void
aegis128x4_dec(uint8_t *const dst, const uint8_t *const src, aes_block_t *const state)
{
    aes_block_t msg0, msg1;

    msg0 = AES_BLOCK_LOAD(src);
    msg1 = AES_BLOCK_LOAD(src + AES_BLOCK_LENGTH);
    msg0 = AES_BLOCK_XOR(msg0, state[6]);
    msg0 = AES_BLOCK_XOR(msg0, state[1]);
    msg1 = AES_BLOCK_XOR(msg1, state[5]);
    msg1 = AES_BLOCK_XOR(msg1, state[2]);
    msg0 = AES_BLOCK_XOR(msg0, AES_BLOCK_AND(state[2], state[3]));
    msg1 = AES_BLOCK_XOR(msg1, AES_BLOCK_AND(state[6], state[7]));
    AES_BLOCK_STORE(dst, msg0);
    AES_BLOCK_STORE(dst + AES_BLOCK_LENGTH, msg1);

    aegis128x4_update(state, msg0, msg1);
}

static inline void
aegis128x4_declast(uint8_t *const dst, const uint8_t *const src, size_t len,
                   aes_block_t *const state)
{
    CRYPTO_ALIGN(64) uint8_t pad[RATE];
    aes_block_t              msg0, msg1;

    memset(pad, 0, sizeof pad);
    memcpy(pad, src, len);

    msg0 = AES_BLOCK_LOAD(pad);
    msg1 = AES_BLOCK_LOAD(pad + AES_BLOCK_LENGTH);
    msg0 = AES_BLOCK_XOR(msg0, state[6]);
    msg0 = AES_BLOCK_XOR(msg0, state[1]);
    msg1 = AES_BLOCK_XOR(msg1, state[5]);
    msg1 = AES_BLOCK_XOR(msg1, state[2]);
    msg0 = AES_BLOCK_XOR(msg0, AES_BLOCK_AND(state[2], state[3]));
    msg1 = AES_BLOCK_XOR(msg1, AES_BLOCK_AND(state[6], state[7]));
    AES_BLOCK_STORE(pad, msg0);
    AES_BLOCK_STORE(pad + AES_BLOCK_LENGTH, msg1);

    memset(pad + len, 0, sizeof pad - len);
    memcpy(dst, pad, len);

    msg0 = AES_BLOCK_LOAD(pad);
    msg1 = AES_BLOCK_LOAD(pad + AES_BLOCK_LENGTH);

    aegis128x4_update(state, msg0, msg1);
}

static int
encrypt_detached(uint8_t *c, uint8_t *mac, size_t maclen, const uint8_t *m, size_t mlen,
                 const uint8_t *ad, size_t adlen, const uint8_t *npub, const uint8_t *k)
{
    CRYPTO_ALIGN(64) aes_block_t state[8];
    CRYPTO_ALIGN(64) uint8_t     src[RATE];
    CRYPTO_ALIGN(64) uint8_t     dst[RATE];
    size_t                       i;

    aegis128x4_init(k, npub, state);

    for (i = 0; i + 4 * RATE <= adlen; i += 4 * RATE) {
        aegis128x4_absorb(ad + i, state);
        aegis128x4_absorb(ad + i + RATE, state);
        aegis128x4_absorb(ad + i + 2 * RATE, state);
        aegis128x4_absorb(ad + i + 3 * RATE, state);
    }
    for (; i + RATE <= adlen; i += RATE) {
        aegis128x4_absorb(ad + i, state);
    }
    if (adlen % RATE) {
        memset(src, 0, RATE);
        memcpy(src, ad + i, adlen % RATE);
        aegis128x4_absorb(src, state);
    }
    for (i = 0; i + 4 * RATE <= mlen; i += 4 * RATE) {
        aegis128x4_enc(c + i, m + i, state);
        aegis128x4_enc(c + i + RATE, m + i + RATE, state);
        aegis128x4_enc(c + i + 2 * RATE, m + i + 2 * RATE, state);
        aegis128x4_enc(c + i + 3 * RATE, m + i + 3 * RATE, state);
    }
    for (; i + RATE <= mlen; i += RATE) {
        aegis128x4_enc(c + i, m + i, state);
    }
    if (mlen % RATE) {
        memset(src, 0, RATE);
        memcpy(src, m + i, mlen % RATE);
        aegis128x4_enc(dst, src, state);
        memcpy(c + i, dst, mlen % RATE);
    }

    aegis128x4_mac(mac, maclen, adlen, mlen, state);

    return 0;
}

static int
decrypt_detached(uint8_t *m, const uint8_t *c, size_t clen, const uint8_t *mac, size_t maclen,
                 const uint8_t *ad, size_t adlen, const uint8_t *npub, const uint8_t *k)
{
    CRYPTO_ALIGN(64) aes_block_t state[8];
    CRYPTO_ALIGN(64) uint8_t     src[RATE];
    CRYPTO_ALIGN(64) uint8_t     dst[RATE];
    CRYPTO_ALIGN(64) uint8_t     computed_mac[32];
    const size_t                 mlen = clen;
    size_t                       i;
    int                          ret;

    aegis128x4_init(k, npub, state);

    for (i = 0; i + 4 * RATE <= adlen; i += 4 * RATE) {
        aegis128x4_absorb(ad + i, state);
        aegis128x4_absorb(ad + i + RATE, state);
        aegis128x4_absorb(ad + i + 2 * RATE, state);
        aegis128x4_absorb(ad + i + 3 * RATE, state);
    }
    for (; i + RATE <= adlen; i += RATE) {
        aegis128x4_absorb(ad + i, state);
    }
    if (adlen % RATE) {
        memset(src, 0, RATE);
        memcpy(src, ad + i, adlen % RATE);
        aegis128x4_absorb(src, state);
    }
    if (m != NULL) {
        for (i = 0; i + 4 * RATE <= mlen; i += 4 * RATE) {
            aegis128x4_dec(m + i, c + i, state);
            aegis128x4_dec(m + i + RATE, c + i + RATE, state);
            aegis128x4_dec(m + i + 2 * RATE, c + i + 2 * RATE, state);
            aegis128x4_dec(m + i + 3 * RATE, c + i + 3 * RATE, state);
        }
        for (; i + RATE <= mlen; i += RATE) {
            aegis128x4_dec(m + i, c + i, state);
        }
    } else {
        for (i = 0; i + 4 * RATE <= mlen; i += 4 * RATE) {
            aegis128x4_dec(dst, c + i, state);
            aegis128x4_dec(dst, c + i + RATE, state);
            aegis128x4_dec(dst, c + i + 2 * RATE, state);
            aegis128x4_dec(dst, c + i + 3 * RATE, state);
        }
        for (; i + RATE <= mlen; i += RATE) {
            aegis128x4_dec(dst, c + i, state);
        }
    }
    if (mlen % RATE) {
        if (m != NULL) {
            aegis128x4_declast(m + i, c + i, mlen % RATE, state);
        } else {
            aegis128x4_declast(dst, c + i, mlen % RATE, state);
        }
    }

    aegis128x4_mac(computed_mac, maclen, adlen, mlen, state);
    ret = -1;
    if (maclen == 16) {
        ret = crypto_verify_16(computed_mac, mac);
    } else if (maclen == 32) {
        ret = crypto_verify_32(computed_mac, mac);
    }
    crypto_declassify(&ret, sizeof ret);
    if (ret != 0 && m != NULL) {
        memset(m, 0, mlen);
    }
    return ret;
}

int
crypto_stream_xor(unsigned char *out, const unsigned char *in, unsigned long long len,
                  const unsigned char *npub, const unsigned char *k)
{
    CRYPTO_ALIGN(64) aes_block_t state[8];
    CRYPTO_ALIGN(64) uint8_t     src[RATE];
    CRYPTO_ALIGN(64) uint8_t     dst[RATE];
    size_t                       i, length;

    if (len > SIZE_MAX) {
        return -1;
    }
    length = (size_t) len;
    aegis128x4_init(k, npub, state);

    for (i = 0; length - i >= 4 * RATE; i += 4 * RATE) {
        aegis128x4_xor_keystream(out + i, in + i, state);
        aegis128x4_xor_keystream(out + i + RATE, in + i + RATE, state);
        aegis128x4_xor_keystream(out + i + 2 * RATE, in + i + 2 * RATE, state);
        aegis128x4_xor_keystream(out + i + 3 * RATE, in + i + 3 * RATE, state);
    }
    for (; length - i >= RATE; i += RATE) {
        aegis128x4_xor_keystream(out + i, in + i, state);
    }
    if (length != i) {
        memset(src, 0, RATE);
        memcpy(src, in + i, length - i);
        aegis128x4_xor_keystream(dst, src, state);
        memcpy(out + i, dst, length - i);
    }
    return 0;
}

int
crypto_aead_encrypt(unsigned char *c, unsigned long long *clen, const unsigned char *m,
                    unsigned long long mlen, const unsigned char *ad, unsigned long long adlen,
                    const unsigned char *nsec, const unsigned char *npub, const unsigned char *k)
{
    (void) nsec;

    if (clen != NULL) {
        *clen = 0;
    }
    if (mlen > SIZE_MAX - CRYPTO_ABYTES || adlen > SIZE_MAX) {
        return -1;
    }
    if (encrypt_detached((uint8_t *) c, c + (size_t) mlen, CRYPTO_ABYTES, (const uint8_t *) m,
                         (size_t) mlen, (const uint8_t *) ad, (size_t) adlen,
                         (const uint8_t *) npub, (const uint8_t *) k) != 0) {
        return -1;
    }
    if (clen != NULL) {
        *clen = mlen + CRYPTO_ABYTES;
    }
    return 0;
}

int
crypto_aead_decrypt(unsigned char *m, unsigned long long *mlen, unsigned char *nsec,
                    const unsigned char *c, unsigned long long clen, const unsigned char *ad,
                    unsigned long long adlen, const unsigned char *npub, const unsigned char *k)
{
    (void) nsec;

    if (mlen != NULL) {
        *mlen = 0;
    }
    if (clen < CRYPTO_ABYTES) {
        return -1;
    }
    if (decrypt_detached((uint8_t *) m, (const uint8_t *) c, (size_t) clen - CRYPTO_ABYTES,
                         (const uint8_t *) c + (size_t) clen - CRYPTO_ABYTES, CRYPTO_ABYTES,
                         (const uint8_t *) ad, (size_t) adlen, (const uint8_t *) npub,
                         (const uint8_t *) k) != 0) {
        return -1;
    }
    if (mlen != NULL) {
        *mlen = clen - CRYPTO_ABYTES;
    }
    return 0;
}
