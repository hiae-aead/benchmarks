static void
stream_xor(HiAE_state_t *state_opaque, uint8_t *ci, const uint8_t *mi, size_t size)
{
    HIAE_ALIGN(64) DATA128b state[STATE];
    const DATA128b zero = SIMD_ZERO_128();
    size_t i = 0;
    size_t offset = 0;

    if (size == 0) {
        return;
    }
    memcpy(state, state_opaque->opaque, sizeof state);
    for (; size - i >= UNROLL_BLOCK_SIZE; i += UNROLL_BLOCK_SIZE) {
#    define STREAM_BLOCK(o) \
        SIMD_STORE(ci + i + BLOCK_SIZE * (o), \
                   SIMD_XOR(enc_offset(state, zero, (o)), SIMD_LOAD(mi + i + BLOCK_SIZE * (o))))
        STREAM_BLOCK(0);
        STREAM_BLOCK(1);
        STREAM_BLOCK(2);
        STREAM_BLOCK(3);
        STREAM_BLOCK(4);
        STREAM_BLOCK(5);
        STREAM_BLOCK(6);
        STREAM_BLOCK(7);
        STREAM_BLOCK(8);
        STREAM_BLOCK(9);
        STREAM_BLOCK(10);
        STREAM_BLOCK(11);
        STREAM_BLOCK(12);
        STREAM_BLOCK(13);
        STREAM_BLOCK(14);
        STREAM_BLOCK(15);
#    undef STREAM_BLOCK
    }
    for (; size - i >= BLOCK_SIZE; i += BLOCK_SIZE, offset++) {
        const DATA128b block = enc_offset(state, zero, (int) offset);
        SIMD_STORE(ci + i, SIMD_XOR(block, SIMD_LOAD(mi + i)));
    }
    if (i < size) {
        HIAE_ALIGN(64) uint8_t buf[BLOCK_SIZE];
        SIMD_STORE(buf, enc_offset(state, zero, (int) offset));
        for (size_t j = 0; j < size - i; j++) {
            ci[i + j] = mi[i + j] ^ buf[j];
        }
        offset++;
    }
    offset %= STATE;
    memcpy(state_opaque->opaque, state + offset, (STATE - offset) * BLOCK_SIZE);
    memcpy(state_opaque->opaque + (STATE - offset) * BLOCK_SIZE, state, offset * BLOCK_SIZE);
}
