#include <bits/stdc++.h>
using namespace std;

const string ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const string KEY = "QWERTYUIOPASDFGHJKLZXCVBNM";

string encrypt(string pt) {
    string res = "";

    for (char c : pt) {

        if (c >= 'A' && c <= 'Z') {
            int index = c - 'A';
            res += KEY[index];
        }

        else if (c >= 'a' && c <= 'z') {
            int index = c - 'a';
            res += tolower(KEY[index]);
        }

        else {
            // Keep spaces, numbers and special characters unchanged
            res += c;
        }
    }

    return res;
}

string decrypt(string ct) {
    string res = "";

    for (char c : ct) {

        if (c >= 'A' && c <= 'Z') {
            int index = KEY.find(c);
            res += ALPHABET[index];
        }

        else if (c >= 'a' && c <= 'z') {
            char upper = toupper(c);
            int index = KEY.find(upper);
            res += tolower(ALPHABET[index]);
        }

        else {
            res += c;
        }
    }

    return res;
}

int main() {

    string pid;
    string diagnosticNote;

    cout << "Enter Patient ID = ";
    getline(cin, pid);

    cout << "Enter Diagnostic Note = ";
    getline(cin, diagnosticNote);

    // Encryption
    string encryptedID = encrypt(pid);
    string encryptedNote = encrypt(diagnosticNote);

    cout << "\nEncryption = \n";
    cout << "Original Patient ID = " << pid << endl;
    cout << "Encrypted Patient ID = " << encryptedID << endl;

    cout << "Original Note = " << diagnosticNote << endl;
    cout << "Encrypted Note = " << encryptedNote << endl;

    // Decryption
    string decryptedID = decrypt(encryptedID);
    string decryptedNote = decrypt(encryptedNote);

    cout << "\nDecryption = \n";
    cout << "Decrypted Patient ID: " << decryptedID << endl;
    cout << "Decrypted Note      : " << decryptedNote << endl;

    return 0;
}