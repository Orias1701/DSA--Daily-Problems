#include <iostream>
#include <string>
#include <vector>
#include <iomanip>
#include <sstream>
#include <cstdint>

using namespace std;

using u64 = uint64_t;
using u08 = uint8_t;

const u64 DEFAULT = 0xcbf29ce484222325ULL; // = 14695981039346656037
const u64 PRIME = 0x100000001b3ULL; // MAGIC! = 1099511628211
const u64 SMALL = 13;

u64 bitXor(u64 a, u64 b) {
    return a ^ b;
}

u64 bitMultiply(u64 a, u64 b) {
    return a * b;
}

u64 bitRotating(u64 value, int shift) {
    shift &= 63;
    if (shift == 0) return value;
    return (value << shift) | (value >> (64 - shift));
}

u64 hashing(const string& input) {
    u64 hashed = DEFAULT;
    for (char c : input) {
        u08 BYTE = static_cast<u08>(c);
        hashed = bitXor(hashed, BYTE);
        hashed = bitMultiply(hashed, PRIME);
        hashed = bitRotating(hashed, SMALL);
    }
    return hashed;
}

string intToHex(u64 hashed) {
    stringstream ss;
    // << fill  = '0'  << 16 char  << hex << value
    ss << setfill('0') << setw(16) << hex << hashed;
    return ss.str();
}


int main() {
    // --- TEST CASE ---
    string text_1 = "Bai tap lon Hash C++";
    string text_2 = "Bai tap lon Hash C--";

    // Gọi trực tiếp tên hàm
    u64 res_1 = hashing(text_1);
    u64 res_2 = hashing(text_2);

    // Gọi trực tiếp hàm chuyển đổi
    string hex_1 = intToHex(res_1);
    string hex_2 = intToHex(res_2);

    // In kết quả
    cout << "-----------------------------------" << endl;
    cout << "Input 1 : \"" << text_1 << "\"" << endl;
    cout << "Hash Int: " << res_1 << endl;
    cout << "Hash Hex: " << hex_1 << endl;
    cout << "-----------------------------------" << endl;
    cout << "Input 2 : \"" << text_2 << "\"" << endl;
    cout << "Hash Int: " << res_2 << endl;
    cout << "Hash Hex: " << hex_2 << endl;
    cout << "-----------------------------------" << endl;

    system("pause");
    return 0;
}