#include <iostream>
#include <string>
using namespace std;

string encrypt(string text, int shift) {
    string result = "";

    shift %= 26;

    for (char ch : text) {
        if (isupper(ch))
            result += char((ch - 'A' + shift) % 26 + 'A');
        else if (islower(ch))
            result += char((ch - 'a' + shift) % 26 + 'a');
        else
            result += ch; // Keep spaces, numbers, symbols unchanged
    }

    return result;
}

string decrypt(string cipher, int shift) {
    string result = "";

    shift %= 26;

    for (char ch : cipher) {
        if (isupper(ch))
            result += char((ch - 'A' - shift + 26) % 26 + 'A');
        else if (islower(ch))
            result += char((ch - 'a' - shift + 26) % 26 + 'a');
        else
            result += ch;
    }

    return result;
}

int main() {
    string text;
    int shift;

    cout << "Enter text = ";
    getline(cin, text);

    cout << "Enter shift value = ";
    cin >> shift;

    string cipher = encrypt(text, shift);
    cout << "Encrypted Text = " << cipher << endl;

    string plain = decrypt(cipher, shift);
    cout << "Decrypted Text = " << plain << endl;

    return 0;
}