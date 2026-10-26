#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>

using std::cout;
using std::uint64_t;

// Add modulo mod without overflowing uint64_t. Preconditions: mod > 0, x < mod, y < mod.
static uint64_t add_mod(uint64_t x, uint64_t y, uint64_t mod) {
    // If x + y would reach/exceed mod, subtract before adding to avoid overflow.
    return (x >= mod - y) ? x - (mod - y) : x + y;
}

// Multiply modulo mod using add-and-double, without overflowing uint64_t.
static uint64_t mul_mod(uint64_t x, uint64_t y, uint64_t mod) {
    x %= mod;
    uint64_t result = 0;
    while (y > 0) {
        if ((y & 1ULL) != 0) {
            result = add_mod(result, x, mod);
        }
        x = add_mod(x, x, mod);
        y >>= 1;
    }
    return result;
}

// Calculate (base^exp) mod mod using binary exponentiation / repeated squaring.
uint64_t modexp(uint64_t base, uint64_t exp, uint64_t mod) {
    if (mod == 0) {
        throw std::invalid_argument("Modulus must be non-zero.");
    }

    uint64_t result = 1 % mod;
    base %= mod;

    while (exp > 0) {
        if ((exp & 1ULL) != 0) {
            result = mul_mod(result, base, mod);
        }
        base = mul_mod(base, base, mod);
        exp >>= 1;
    }
    return result;
}

int main() {
    // Suggested demonstration prime. g=13 is a primitive root modulo p.
    // These parameters are for a lab demonstration, NOT real-world security.
    constexpr uint64_t p = 4294967311ULL;
    constexpr uint64_t g = 13ULL;

    // Generate independent private values for Alice and Bob.
    std::random_device rd;
    std::mt19937_64 gen(rd());
    std::uniform_int_distribution<uint64_t> dist(2ULL, p - 2ULL);
    const uint64_t a = dist(gen);
    const uint64_t b = dist(gen);

    // Exchange public values.
    const uint64_t A = modexp(g, a, p);
    const uint64_t B = modexp(g, b, p);

    // Independently derive the shared key.
    const uint64_t KA = modexp(B, a, p);
    const uint64_t KB = modexp(A, b, p);

    cout << "Diffie-Hellman Key Exchange (Toy Demonstration)\n";
    cout << "Public prime p = " << p << '\n';
    cout << "Generator g = " << g << '\n';
    cout << "Alice private a = " << a << '\n';
    cout << "Alice public A = " << A << '\n';
    cout << "Bob private b = " << b << '\n';
    cout << "Bob public B = " << B << '\n';
    cout << "Shared key computed by Alice = " << KA << '\n';
    cout << "Shared key computed by Bob = " << KB << '\n';
    cout << "Keys match: " << (KA == KB ? "YES" : "NO") << '\n';

    return (KA == KB) ? 0 : 1;
}
