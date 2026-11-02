#include <array>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

using std::uint8_t;
using std::uint32_t;
using std::uint64_t;
using Bytes = std::vector<uint8_t>;

static uint32_t rotl32(uint32_t x, uint32_t n) {
    return (x << n) | (x >> (32U - n));
}

static uint32_t rotr32(uint32_t x, uint32_t n) {
    return (x >> n) | (x << (32U - n));
}

static std::string toHex(const Bytes& bytes) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (uint8_t byte : bytes) {
        out << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return out.str();
}

static void padLittleEndian(Bytes& data) {
    const uint64_t bitLength = static_cast<uint64_t>(data.size()) * 8ULL;
    data.push_back(0x80);
    while (data.size() % 64 != 56) data.push_back(0x00);
    for (unsigned int i = 0; i < 8; ++i) {
        data.push_back(static_cast<uint8_t>((bitLength >> (8U * i)) & 0xffU));
    }
}

static void padBigEndian(Bytes& data) {
    const uint64_t bitLength = static_cast<uint64_t>(data.size()) * 8ULL;
    data.push_back(0x80);
    while (data.size() % 64 != 56) data.push_back(0x00);
    for (int i = 7; i >= 0; --i) {
        data.push_back(static_cast<uint8_t>((bitLength >> (8U * i)) & 0xffU));
    }
}

static Bytes stateToBytesLE(const std::array<uint32_t, 4>& state) {
    Bytes out;
    out.reserve(16);
    for (uint32_t word : state) {
        for (unsigned int i = 0; i < 4; ++i)
            out.push_back(static_cast<uint8_t>((word >> (8U * i)) & 0xffU));
    }
    return out;
}

static Bytes stateToBytesBE(const uint32_t* state, std::size_t count) {
    Bytes out;
    out.reserve(count * 4);
    for (std::size_t j = 0; j < count; ++j) {
        for (int i = 3; i >= 0; --i)
            out.push_back(static_cast<uint8_t>((state[j] >> (8U * i)) & 0xffU));
    }
    return out;
}

// MD5: produces a 128-bit (16-byte) digest.
static std::string md5(const std::string& input) {
    static constexpr uint32_t K[64] = {
        0xd76aa478,0xe8c7b756,0x242070db,0xc1bdceee,0xf57c0faf,0x4787c62a,0xa8304613,0xfd469501,
        0x698098d8,0x8b44f7af,0xffff5bb1,0x895cd7be,0x6b901122,0xfd987193,0xa679438e,0x49b40821,
        0xf61e2562,0xc040b340,0x265e5a51,0xe9b6c7aa,0xd62f105d,0x02441453,0xd8a1e681,0xe7d3fbc8,
        0x21e1cde6,0xc33707d6,0xf4d50d87,0x455a14ed,0xa9e3e905,0xfcefa3f8,0x676f02d9,0x8d2a4c8a,
        0xfffa3942,0x8771f681,0x6d9d6122,0xfde5380c,0xa4beea44,0x4bdecfa9,0xf6bb4b60,0xbebfbc70,
        0x289b7ec6,0xeaa127fa,0xd4ef3085,0x04881d05,0xd9d4d039,0xe6db99e5,0x1fa27cf8,0xc4ac5665,
        0xf4292244,0x432aff97,0xab9423a7,0xfc93a039,0x655b59c3,0x8f0ccc92,0xffeff47d,0x85845dd1,
        0x6fa87e4f,0xfe2ce6e0,0xa3014314,0x4e0811a1,0xf7537e82,0xbd3af235,0x2ad7d2bb,0xeb86d391
    };
    static constexpr uint32_t S[64] = {
        7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22,
        5,9,14,20,5,9,14,20,5,9,14,20,5,9,14,20,
        4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23,
        6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21
    };

    Bytes data(input.begin(), input.end());
    padLittleEndian(data);

    std::array<uint32_t, 4> h = {0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476};
    for (std::size_t offset = 0; offset < data.size(); offset += 64) {
        uint32_t M[16];
        for (unsigned int j = 0; j < 16; ++j) {
            const std::size_t p = offset + j * 4;
            M[j] = static_cast<uint32_t>(data[p]) |
                   (static_cast<uint32_t>(data[p + 1]) << 8U) |
                   (static_cast<uint32_t>(data[p + 2]) << 16U) |
                   (static_cast<uint32_t>(data[p + 3]) << 24U);
        }

        uint32_t a = h[0], b = h[1], c = h[2], d = h[3];
        for (uint32_t i = 0; i < 64; ++i) {
            uint32_t f, g;
            if (i < 16) { f = (b & c) | (~b & d); g = i; }
            else if (i < 32) { f = (d & b) | (~d & c); g = (5U * i + 1U) % 16U; }
            else if (i < 48) { f = b ^ c ^ d; g = (3U * i + 5U) % 16U; }
            else { f = c ^ (b | ~d); g = (7U * i) % 16U; }
            const uint32_t temp = d;
            d = c;
            c = b;
            b = b + rotl32(a + f + K[i] + M[g], S[i]);
            a = temp;
        }
        h[0] += a; h[1] += b; h[2] += c; h[3] += d;
    }
    return toHex(stateToBytesLE(h));
}

// SHA-1: produces a 160-bit (20-byte) digest.
static std::string sha1(const std::string& input) {
    Bytes data(input.begin(), input.end());
    padBigEndian(data);
    uint32_t h[5] = {0x67452301,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0};

    for (std::size_t offset = 0; offset < data.size(); offset += 64) {
        uint32_t W[80];
        for (unsigned int i = 0; i < 16; ++i) {
            const std::size_t p = offset + i * 4;
            W[i] = (static_cast<uint32_t>(data[p]) << 24U) |
                   (static_cast<uint32_t>(data[p + 1]) << 16U) |
                   (static_cast<uint32_t>(data[p + 2]) << 8U) |
                   static_cast<uint32_t>(data[p + 3]);
        }
        for (unsigned int i = 16; i < 80; ++i)
            W[i] = rotl32(W[i - 3] ^ W[i - 8] ^ W[i - 14] ^ W[i - 16], 1);

        uint32_t a=h[0], b=h[1], c=h[2], d=h[3], e=h[4];
        for (unsigned int i = 0; i < 80; ++i) {
            uint32_t f, k;
            if (i < 20) { f = (b & c) | (~b & d); k = 0x5a827999; }
            else if (i < 40) { f = b ^ c ^ d; k = 0x6ed9eba1; }
            else if (i < 60) { f = (b & c) | (b & d) | (c & d); k = 0x8f1bbcdc; }
            else { f = b ^ c ^ d; k = 0xca62c1d6; }
            const uint32_t temp = rotl32(a, 5) + f + e + k + W[i];
            e = d; d = c; c = rotl32(b, 30); b = a; a = temp;
        }
        h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d; h[4]+=e;
    }
    return toHex(stateToBytesBE(h, 5));
}

// SHA-256: produces a 256-bit (32-byte) digest.
static std::string sha256(const std::string& input) {
    static constexpr uint32_t K[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
    };
    Bytes data(input.begin(), input.end());
    padBigEndian(data);
    uint32_t h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                     0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};

    for (std::size_t offset = 0; offset < data.size(); offset += 64) {
        uint32_t W[64];
        for (unsigned int i = 0; i < 16; ++i) {
            const std::size_t p = offset + i * 4;
            W[i] = (static_cast<uint32_t>(data[p]) << 24U) |
                   (static_cast<uint32_t>(data[p + 1]) << 16U) |
                   (static_cast<uint32_t>(data[p + 2]) << 8U) |
                   static_cast<uint32_t>(data[p + 3]);
        }
        for (unsigned int i = 16; i < 64; ++i) {
            const uint32_t s0 = rotr32(W[i-15], 7) ^ rotr32(W[i-15], 18) ^ (W[i-15] >> 3U);
            const uint32_t s1 = rotr32(W[i-2], 17) ^ rotr32(W[i-2], 19) ^ (W[i-2] >> 10U);
            W[i] = W[i-16] + s0 + W[i-7] + s1;
        }

        uint32_t a=h[0], b=h[1], c=h[2], d=h[3], e=h[4], f=h[5], g=h[6], hh=h[7];
        for (unsigned int i = 0; i < 64; ++i) {
            const uint32_t S1 = rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25);
            const uint32_t ch = (e & f) ^ (~e & g);
            const uint32_t temp1 = hh + S1 + ch + K[i] + W[i];
            const uint32_t S0 = rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22);
            const uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
            const uint32_t temp2 = S0 + maj;
            hh=g; g=f; f=e; e=d+temp1; d=c; c=b; b=a; a=temp1+temp2;
        }
        h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d;
        h[4]+=e; h[5]+=f; h[6]+=g; h[7]+=hh;
    }
    return toHex(stateToBytesBE(h, 8));
}

static void showDigests(const std::string& label, const std::string& message) {
    std::cout << "\n" << label << "\n";
    std::cout << "Message : " << message << "\n";
    std::cout << "MD5     : " << md5(message) << "\n";
    std::cout << "SHA-1   : " << sha1(message) << "\n";
    std::cout << "SHA-256 : " << sha256(message) << "\n";
}

int main() {
    std::string original;
    std::cout << "MD5, SHA-1 and SHA-256 Message Integrity Demo\n";
    std::cout << "Enter original message: ";
    std::getline(std::cin, original);

    showDigests("ORIGINAL MESSAGE DIGESTS", original);

    std::cout << "\nChoose received-message mode:\n";
    std::cout << "1. Enter a received message manually\n";
    std::cout << "2. Automatically change one character (demonstration)\n";
    std::cout << "Choice: ";
    int choice;
    if (!(std::cin >> choice)) {
        std::cerr << "Invalid choice.\n";
        return 1;
    }
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    std::string received;
    if (choice == 1) {
        std::cout << "Enter received message: ";
        std::getline(std::cin, received);
    } else if (choice == 2) {
        received = original;
        if (received.empty()) received = "a";
        else received[0] = (received[0] == 'a') ? 'b' : 'a';
        std::cout << "Automatically modified the first character.\n";
    } else {
        std::cerr << "Invalid choice. Please run the program again and choose 1 or 2.\n";
        return 1;
    }

    showDigests("RECEIVED / MODIFIED MESSAGE DIGESTS", received);

    const bool md5Match = (md5(original) == md5(received));
    const bool sha1Match = (sha1(original) == sha1(received));
    const bool sha256Match = (sha256(original) == sha256(received));

    std::cout << "\nINTEGRITY CHECK\n";
    std::cout << "MD5     : " << (md5Match ? "MATCH - message unchanged" : "MISMATCH - message modified") << "\n";
    std::cout << "SHA-1   : " << (sha1Match ? "MATCH - message unchanged" : "MISMATCH - message modified") << "\n";
    std::cout << "SHA-256 : " << (sha256Match ? "MATCH - message unchanged" : "MISMATCH - message modified") << "\n";

    std::cout << "\nNote: MD5 and SHA-1 are cryptographically weak. Use SHA-256 or stronger for modern hashing.\n";
    std::cout << "A plain digest does not authenticate the sender; use a MAC or digital signature when needed.\n";
    return 0;
}
