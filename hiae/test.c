// Checks the code being benchmarked against known test vectors.

#include "crypto_aead.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define NAME    "HiAE"
#define MAX_LEN 4096

typedef struct {
    const char *name;
    const char *key;
    const char *nonce;
    const char *ad;
    const char *plaintext;
    const char *ciphertext;
    const char *tag;
} TestVector;

static const TestVector test_vectors[] = {
    { .name       = "Test Vector 1: empty plaintext, no AD",
      .key        = "4b7a9c3ef8d2165a0b3e5f8c9d4a7b1e2c5f8a9d3b6e4c7f0a1d2e5b8c9f4a7d",
      .nonce      = "a5b8c2d9e3f4a7b1c8d5e9f2a3b6c7d8",
      .ad         = "",
      .plaintext  = "",
      .ciphertext = "",
      .tag        = "a25049aa37deea054de461d10ce7840b" },
    { .name       = "Test Vector 2: single block plaintext, no AD",
      .key        = "2f8e4d7c3b9a5e1f8d2c6b4a9f3e7d5c1b8a6f4e3d2c9b5a8f7e6d4c3b2a1f9e",
      .nonce      = "7c3e9f5a1d8b4c6f2e9a5d7b3f8c1e4a",
      .ad         = "",
      .plaintext  = "55f00fcc339669aa55f00fcc339669aa",
      .ciphertext = "af9bd1865daa6fc351652589abf70bff",
      .tag        = "ed9e2edc8241c3184fc08972bd8e9952" },
    { .name       = "Test Vector 3: empty plaintext with AD",
      .key        = "9f3e7d5c4b8a2f1e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e",
      .nonce      = "3d8c7f2a5b9e4c1f8a6d3b7e5c2f9a4d",
      .ad         = "394a5b6c7d8e9fb0c1d2e3f405162738495a6b7c8d9eafc0d1e2f30415263748",
      .plaintext  = "",
      .ciphertext = "",
      .tag        = "7e19c04f68f5af633bf67529cfb5e5f4" },
    { .name       = "Test Vector 4: rate-aligned plaintext (256 bytes)",
      .key        = "6c8f2d5a9e3b7f4c1d8a5e9f3c7b2d6a4f8e1c9b5d3a7e2f4c8b6d9a1e5f3c7d",
      .nonce      = "9a5c7e3f1b8d4a6c2e9f5b7d3a8c1e6f",
      .ad         = "",
      .plaintext  = "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff"
                    "ffffffffffffffffffffffffffffffff",
      .ciphertext = "cf9f118ccc3ae98998ddaae1a5d1f9a1"
                    "69e4ca3e732baf7178cdd9a353057166"
                    "8fe403e77111eac3da34bf2f25719cea"
                    "09445cc58197b1c6ac490626724e7372"
                    "707cfb60cdba8262f0e33a1ef8adda1f"
                    "2e390a80c58e5c055d9be9bbccdc06ad"
                    "af74f1dcaa372204bf42e5e0e0ac5943"
                    "7a353978298837023f79fac6daa1fe8f"
                    "6bcaaaf060ae2e37ed7b7da0577a7643"
                    "5f0403b8e277b6bc2ea99682f2d0d577"
                    "77fec6d901e0d8fc7cf46bb97336812a"
                    "2d8cfd39053993288cce2c077fce0c6c"
                    "00e99cf919281b261acf86b058164f10"
                    "1d9c24e8f40b4fa0ed60955eeeb4e33f"
                    "f1087519c13db8e287199a7df7e94b0d"
                    "368da9ccf3d2ecebfa46f860348f8e3c",
      .tag        = "4f42c3042cba3973153673156309dd69" },
    { .name       = "Test Vector 5: rate + 1 byte plaintext",
      .key        = "3e9d6c5b4a8f7e2d1c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d",
      .nonce      = "6f2e8a5c9b3d7f1e4a8c5b9d3f7e2a6c",
      .ad         = "6778899aabbccddeef00112233445566",
      .plaintext  = "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc339669aa55f00fcc339669aa55f00f"
                    "cc",
      .ciphertext = "522e4cd9b0881809d80e149bb4ed8b8a"
                    "dd70b7257afca6c2bc38e4da11e290cf"
                    "cabd9dd1d4ed8c514482f444f903e42e"
                    "c21a7a605ee37f95a504ec667fabec40"
                    "66eb4521cdaf9c4eb7b62d659ab0a936"
                    "3b145f1120c1b2e589ab9cb893d01be0"
                    "d22182fc7de4932f1e8652b50e4a0d48"
                    "c49a8a1232b201e2e535cd95c15cf0ee"
                    "389b75e372653579c72c4dd1906fd81c"
                    "2b9fc2483fab8b4df5a09d59753b5bd4"
                    "1334be2e5085e349b6e5aac0c555a0a8"
                    "3e94eab974052131f8d451c9d85389a3"
                    "6126f93464e6f93119c6b1bf15b4c0a9"
                    "e6c9beb52e82c846c472f87c15ac49e9"
                    "9d59248ba7e6b97ca04327769d6b8c1f"
                    "751d95dba709fb335183c21476836ea1"
                    "ab",
      .tag        = "61bac11505dd8bbf55e7fbb7489de7b0" },
    { .name       = "Test Vector 6: rate - 1 byte plaintext",
      .key        = "8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f",
      .nonce      = "4d8b2f6a9c3e7f5d1b8a4c6e9f3d5b7a",
      .ad         = "",
      .plaintext  = "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "000000000000000000000000000000",
      .ciphertext = "2ba49be54eb675efe446fd597721d4cd"
                    "ca6e01f1a51728a859d8f206d13cdb08"
                    "ba4f0fe78fbbd6885964ed54e9beceed"
                    "1ff306642c4761e67efa7a2620e57128"
                    "15b5e9f066b42e879cd62e7adc2821e5"
                    "08311b88a6ee14bedcbac7ce339994c0"
                    "09bbbadf9444748e4ab9a91acbbc7301"
                    "742dab74aa1be6847ad8e9f08c170359"
                    "b87e0ccd480812aaaf847aff03c2e858"
                    "1c55848c2b50f6c6608540fe82627a2c"
                    "0f5ee37fbe9cdeab5f6c9799702bd303"
                    "2bf733e2108d03247cd20edaa2c322e5"
                    "bf086bfecc4ac97b61096f016c57d5d0"
                    "1c24d398cefd5ae8131c1f51f172ce9c"
                    "6d3b8395d396dcbd70b4af790018796b"
                    "31f0b0ad6198f86e5e1f26e9258492",
      .tag        = "221dd1b69afb4e0c149e0a058e471a4a" },
    { .name       = "Test Vector 7: medium plaintext with AD",
      .key        = "5d9c3b7a8f2e6d4c1b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c",
      .nonce      = "8c5a7d3f9b1e6c4a2f8d5b9e3c7a1f6d",
      .ad         = "95a6b7c8d9eafb0c1d2e3f5061728394"
                    "a5b6c7d8e9fa0b1c2d3e4f60718293a4"
                    "b5c6d7e8f90a1b2c3d4e5f708192a3b4"
                    "c5d6e7f8091a2b3c4d5e6f8091a2b3c4",
      .plaintext  = "32e14453e7a776781d4c4e2c3b23bca2"
                    "441ee4213bc3df25021b5106c22c98e8"
                    "a7b310142252c8dcff70a91d55cdc910"
                    "3c1eccd9b5309ef21793a664e0d4b63c"
                    "83530dcd1a6ad0feda6ff19153e9ee62"
                    "0325c1cb979d7b32e54f41da3af1c169"
                    "a24c47c1f6673e115f0cb73e8c507f15"
                    "eedf155261962f2d175c9ba3832f4933"
                    "fb330d28ad6aae787f12788706f45c92"
                    "e72aea146959d2d4fa01869f7d072a7b"
                    "f43b2e75265e1a000dde451b64658919"
                    "e93143d2781955fb4ca2a38076ac9eb4"
                    "9adc2b92b05f0ec7",
      .ciphertext = "1d8d56867870574d1c4ac114620c6a2a"
                    "bb44680fe321dd116601e2c92540f85a"
                    "11c41dcac9814397b8f37b812cd52c93"
                    "2db6ecbaa247c3e14f228bd792334570"
                    "2fc43ad1eb1b8086e2c3c57bb602971c"
                    "29772a35dfb1c45c66f81633e67fdc8d"
                    "8005457ddbe4179312abab981049eb0a"
                    "0a555b9fa01378878d7349111e2446fd"
                    "e89ce64022d032cbf0cf2672e00d7999"
                    "ed8b631c1b9bee547cbe464673464a4b"
                    "80e8f72ad2b91a40fdcee5357980c090"
                    "b34ab5e732e2a7df7613131ee42e42ec"
                    "6ae9b05ac5683ebe",
      .tag        = "e93686b266c481196d44536eb51b5f2d" },
    { .name       = "Test Vector 8: single byte plaintext",
      .key        = "7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a",
      .nonce      = "2e7c9f5d3b8a4c6f1e9b5d7a3f8c2e4a",
      .ad         = "",
      .plaintext  = "ff",
      .ciphertext = "21",
      .tag        = "3cf9020bd1cc59cc5f2f6ce19f7cbf68" },
    { .name       = "Test Vector 9: two blocks plaintext",
      .key        = "4c8b7a9f3e5d2c6b1a8f9e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b",
      .nonce      = "7e3c9a5f1d8b4e6c2a9f5d7b3e8c1a4f",
      .ad         = "c3d4e5f60718293a4b5c6d7e8fa0b1c2"
                    "d3e4f5061728394a5b6c7d8e9fb0c1d2"
                    "e3f405162738495a6b7c8d9eafc0d1e2",
      .plaintext  = "aa55f00fcc339669aa55f00fcc339669"
                    "aa55f00fcc339669aa55f00fcc339669",
      .ciphertext = "c2e199ac8c23ce6e3778e7fd0b4f8f75"
                    "2badd4b67be0cdc3f6c98ae5f6fb0d25",
      .tag        = "7aea3fbce699ceb1d0737e0483217745" },
    { .name       = "Test Vector 10: all zeros plaintext",
      .key        = "9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d",
      .nonce      = "5f9d3b7e2c8a4f6d1b9e5c7a3d8f2b6e",
      .ad         = "daebfc0d1e2f405162738495a6b7c8d9",
      .plaintext  = "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000"
                    "00000000000000000000000000000000",
      .ciphertext = "fc7f1142f681399099c5008980e73420"
                    "65b4e62a9b9cb301bdf441d3282b6aa9"
                    "3bd7cd735ef77755b4109f86b7c09083"
                    "8e7b05f08ef4947946155a03ff483095"
                    "152ef3dec8bdddae3990d00d41d5ee6c"
                    "90dcf65dbed4b7ebbe9bb4ef096e1238"
                    "d388bf15faacdb7a68be19dddc8a5b74"
                    "216f4442bfa32d1dfccdc9c4020baec9",
      .tag        = "ad0b841c3d145a6ee86dc7b67338f113" },
    { .name       = "Test Vector 11: partial-block AD and plaintext",
      .key        = "1122334455667788112233445566778811223344556677881122334455667788",
      .nonce      = "aabbccddeeff0011aabbccddeeff0011",
      .ad         = "0102030405060708090a0b0c0d",
      .plaintext  = "48656c6c6f576f726c64",
      .ciphertext = "1fb0e0348c6a3a917133",
      .tag        = "7d292173b55ba02dae56ac1224b7e775" }
};

static int
hex_decode(uint8_t *out, size_t max_len, const char *hex)
{
    size_t len = strlen(hex) / 2;
    if (len > max_len) {
        return -1;
    }
    for (size_t i = 0; i < len; i++) {
        unsigned int byte;
        if (sscanf(hex + 2 * i, "%2x", &byte) != 1) {
            return -1;
        }
        out[i] = (uint8_t) byte;
    }
    return (int) len;
}

static const char *
run_test_vector(const TestVector *tv)
{
    static uint8_t key[CRYPTO_KEYBYTES], nonce[CRYPTO_NPUBBYTES];
    static uint8_t ad[MAX_LEN], plaintext[MAX_LEN], decrypted[MAX_LEN];
    static uint8_t expected[MAX_LEN + CRYPTO_ABYTES], ciphertext[MAX_LEN + CRYPTO_ABYTES];
    unsigned long long clen, mlen;

    if (hex_decode(key, sizeof key, tv->key) != CRYPTO_KEYBYTES ||
        hex_decode(nonce, sizeof nonce, tv->nonce) != CRYPTO_NPUBBYTES) {
        return "bad key or nonce";
    }
    int ad_len = hex_decode(ad, sizeof ad, tv->ad);
    int pt_len = hex_decode(plaintext, sizeof plaintext, tv->plaintext);
    if (ad_len < 0 || pt_len < 0 || hex_decode(expected, MAX_LEN, tv->ciphertext) != pt_len ||
        hex_decode(expected + pt_len, CRYPTO_ABYTES, tv->tag) != CRYPTO_ABYTES) {
        return "bad test vector";
    }

    int ret = crypto_aead_encrypt(ciphertext, &clen, plaintext, pt_len, ad, ad_len, NULL, nonce, key);
    if (ret != 0 || clen != (unsigned long long) pt_len + CRYPTO_ABYTES || memcmp(ciphertext, expected, clen) != 0) {
        return "wrong ciphertext or tag";
    }
    ret = crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, ad, ad_len, nonce, key);
    if (ret != 0 || mlen != (unsigned long long) pt_len || memcmp(decrypted, plaintext, pt_len) != 0) {
        return "decryption failed";
    }
    ciphertext[clen - 1] ^= 1;
    if (crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, ad, ad_len, nonce, key) == 0) {
        return "a forged tag was accepted";
    }
    return NULL;
}

int
main(void)
{
    const size_t count  = sizeof test_vectors / sizeof test_vectors[0];
    int          failed = 0;

    for (size_t i = 0; i < count; i++) {
        const char *error = run_test_vector(&test_vectors[i]);
        if (error != NULL) {
            printf("%s: %s\n", test_vectors[i].name, error);
            failed++;
        }
    }
    printf("%s test vectors: %d passed, %d failed\n", NAME, (int) count - failed, failed);

    return failed > 0;
}
