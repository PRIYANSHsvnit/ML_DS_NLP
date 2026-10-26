#include <iostream>
#include <stdexcept>
#include <string>
using namespace std;

// This version uses standard C++ only (no Boost required).
// It is intended for the small toy RSA values used in this lab.
using int64 = long long;

struct EG {
    int64 g, x, y;
};

// Extended Euclidean Algorithm: returns g, x, y such that
// a*x + b*y = g = gcd(a, b).
EG egcd(int64 a, int64 b) {
    if (b == 0) {
        return {a, 1, 0};
    }

    EG t = egcd(b, a % b);
    int64 x = t.y;
    int64 y = t.x - (a / b) * t.y;
    return {t.g, x, y};
}

// Computes a^(-1) mod m. The inverse exists only when gcd(a, m) == 1.
int64 modinv(int64 a, int64 m) {
    if (m <= 0) {
        throw invalid_argument("Modulus must be positive.");
    }

    EG t = egcd(a, m);
    if (t.g != 1) {
        throw invalid_argument("Modular inverse does not exist: gcd(a, m) must be 1.");
    }

    return (t.x % m + m) % m;
}

// Binary modular exponentiation. Safe for this lab's small toy parameters.
int64 modexp(int64 base, int64 exp, int64 mod) {
    if (mod <= 0) {
        throw invalid_argument("Modulus must be positive.");
    }
    if (exp < 0) {
        throw invalid_argument("Exponent must be non-negative.");
    }

    base = (base % mod + mod) % mod;
    int64 res = 1 % mod;

    while (exp > 0) {
        if (exp % 2 == 1) {
            res = (res * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

int main() {
    try {
        cout << "=== RSA Implementation (Toy Example) ===\n";

        // Key generation: p and q are distinct prime numbers for this example.
        int64 p = 61, q = 53;
        int64 n = p * q;
        int64 phi = (p - 1) * (q - 1);
        int64 e = 17;

        if (p <= 1 || q <= 1 || p == q) {
            throw invalid_argument("Choose two distinct prime numbers greater than 1.");
        }
        if (egcd(e, phi).g != 1) {
            throw invalid_argument("The public exponent e must be coprime to phi(n).");
        }

        int64 d = modinv(e, phi);

        cout << "p = " << p << "\nq = " << q << "\n";
        cout << "n = " << n << "\nphi(n) = " << phi << "\n";
        cout << "Public exponent e = " << e << "\nPrivate exponent d = " << d << "\n";

        // RSA message must satisfy 0 <= m < n.
        int64 m = 65;
        if (m < 0 || m >= n) {
            throw invalid_argument("Message must satisfy 0 <= m < n.");
        }

        int64 c = modexp(m, e, n);
        int64 m_dec = modexp(c, d, n);

        cout << "\nMessage m = " << m;
        cout << "\nCiphertext c = " << c;
        cout << "\nDecrypted message m_dec = " << m_dec << "\n";

        if (m == m_dec) {
            cout << "\n[OK] Decryption successful!\n";
        } else {
            cout << "\n[ERROR] Decryption failed!\n";
        }
    } catch (const exception& ex) {
        cerr << "Error: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
