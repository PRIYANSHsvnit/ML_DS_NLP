#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
using namespace std;

// ---------- TODO(1): Extended Euclidean Algorithm ----------
// Returns g, x, y such that a*x + b*y = g = gcd(a, b).
struct EG { cpp_int g, x, y; };
EG egcd(cpp_int a, cpp_int b) {
    if (b == 0) {
        return {a, 1, 0};
    }

    EG t = egcd(b, a % b);
    return {t.g, t.y, t.x - (a / b) * t.y};
}

// ---------- TODO(2): Modular Inverse ----------
// Finds x such that (a*x) % m == 1. This exists only when gcd(a,m) == 1.
cpp_int modinv(cpp_int a, cpp_int m) {
    if (m <= 0) {
        throw invalid_argument("Modulus must be positive.");
    }

    EG t = egcd(a, m);
    if (t.g != 1) {
        throw invalid_argument("Modular inverse does not exist: gcd(a, m) != 1.");
    }

    // Ensure the answer is in the range 0 ... m-1, even if x is negative.
    return (t.x % m + m) % m;
}

// ---------- TODO(3): Modular Exponentiation ----------
// Computes base^exp mod mod efficiently using repeated squaring.
cpp_int modexp(cpp_int base, cpp_int exp, const cpp_int& mod) {
    if (mod <= 0) {
        throw invalid_argument("Modulus must be positive.");
    }
    if (exp < 0) {
        throw invalid_argument("Exponent must be non-negative.");
    }

    base = (base % mod + mod) % mod;
    cpp_int res = 1 % mod;

    while (exp > 0) {
        if (exp % 2 != 0) {
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

        // ---------- TODO(4): Key Generation ----------
        cpp_int p = 61, q = 53;   // Example primes (students can change)
        cpp_int n = p * q;
        cpp_int phi = (p - 1) * (q - 1);
        cpp_int e = 17;            // Public exponent; gcd(e, phi) must be 1

        if (egcd(e, phi).g != 1) {
            throw invalid_argument("Choose e such that gcd(e, phi(n)) = 1.");
        }
        cpp_int d = modinv(e, phi);

        cout << "p = " << p << "\nq = " << q << "\n";
        cout << "n = " << n << "\nphi(n) = " << phi << "\n";
        cout << "Public exponent e = " << e << "\nPrivate exponent d = " << d << "\n";

        // ---------- TODO(5): Encrypt & Decrypt ----------
        cpp_int m = 65;   // Example message (integer)
        if (m < 0 || m >= n) {
            throw invalid_argument("Message must satisfy 0 <= m < n.");
        }

        cpp_int c = modexp(m, e, n);       // Encryption: c = m^e mod n
        cpp_int m_dec = modexp(c, d, n);   // Decryption: m = c^d mod n

        cout << "\nMessage m = " << m;
        cout << "\nCiphertext c = " << c;
        cout << "\nDecrypted message m_dec = " << m_dec << "\n";

        if (m == m_dec) cout << "\n[OK] Decryption successful!\n";
        else cout << "\n[ERROR] Decryption failed!\n";
    } catch (const exception& ex) {
        cerr << "Error: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}