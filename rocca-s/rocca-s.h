#ifndef ROCCA_S_H
#define ROCCA_S_H

#include <stdlib.h>
#include <stdint.h>

#define ROCCA_KEY_SIZE       (32)
#define ROCCA_IV_SIZE        (16)
#define ROCCA_MSG_BLOCK_SIZE (32)
#define ROCCA_TAG_SIZE       (32)
#define ROCCA_STATE_NUM      ( 7)

typedef struct ROCCA_CTX {
	uint8_t key[ROCCA_KEY_SIZE/16][16];
	uint8_t state[ROCCA_STATE_NUM][16];
	size_t size_ad;
	size_t size_m;
} rocca_context;

void rocca_init(rocca_context * ctx, const uint8_t * key, const uint8_t * iv);
void rocca_add_ad(rocca_context * ctx, const uint8_t * in, size_t size);
void rocca_encrypt(rocca_context * ctx, uint8_t * out, const uint8_t * in, size_t size);
void rocca_decrypt(rocca_context * ctx, uint8_t * out, const uint8_t * in, size_t size);
void rocca_tag(rocca_context * ctx, uint8_t *tag);

#endif
