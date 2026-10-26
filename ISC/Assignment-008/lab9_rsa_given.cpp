
#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
using namespace std;

// ---------- TODO(1): Extended Euclidean Algorithm ----------
struct EG { cpp_int g, x, y; };
EG egcd(cpp_int a, cpp_int b) {
    // Fill the missing code here.
}

// ---------- TODO(2): Modular Inverse ----------
cpp_int modinv(cpp_int a, cpp_int m) {
    auto t = egcd(a, m);
    //fill the missing code here
}

// ---------- TODO(3): Modular Exponentiation ----------
cpp_int modexp(cpp_int base, cpp_int exp, const cpp_int& mod) {
    base %= mod;
    cpp_int res = 1;
   // Fill the missing code here.
    return res;
}

int main() {
    cout << "=== RSA Implementation (Toy Example) ===\n";

    // ---------- TODO(4): Key Generation ----------
    cpp_int p = 61, q = 53;   // Example primes (students can change)
    cpp_int n;
    cpp_int phi;
    cpp_int e;           // Common choice for public exponent
    cpp_int d;
	//Fill in your code here.

    cout << "p = " << p << "\nq = " << q << "\n";
    cout << "n = " << n << "\nphi(n) = " << phi << "\n";
    cout << "Public exponent e = " << e << "\nPrivate exponent d = " << d << "\n";

    // ---------- TODO(5): Encrypt & Decrypt ----------
    cpp_int m = 65;   // Example message (integer)
    cpp_int c; // ciphertext
	//Fill in your code here.

    cout << "\nMessage m = " << m;
    cout << "\nCiphertext c = " << c;
    cout << "\nDecrypted message m_dec = " << m_dec << "\n";

    if (m == m_dec) cout << "\n[OK] Decryption successful!\n";
    else cout << "\n[ERROR] Decryption failed!\n";

    return 0;
}
