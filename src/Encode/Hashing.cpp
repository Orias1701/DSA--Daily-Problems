#include <bits/stdc++.h>

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
    u64 HASH = DEFAULT;
    cout << "KHỞI TẠO HASH: " << HASH << endl;
    cout << "-----------------------------------" << endl;
    for (char c : input) {
        cout << "Xử lý kí tự: " << c << endl;
        u08 BYTE = static_cast<u08>(c);
        cout << "Chuyển 8 bit cuối của " << c << " thành số nguyên: " << int(BYTE) << endl;

        cout << "HASH xor " << c << " = " << HASH  << " xor " << int(BYTE) << " = ";
        HASH = bitXor(HASH, BYTE);
        cout << HASH << endl;

        cout << "HASH * PRIME = " << HASH << " * " << PRIME << " = ";
        HASH = bitMultiply(HASH, PRIME);
        cout << HASH << endl;
        
        HASH = bitRotating(HASH, SMALL);
        cout << "HASH xoay " << SMALL << " bit: " << HASH << endl;
        cout << "-----------------------------------" << endl;
    }
    return HASH;
}

string intToHex(u64 HASH) {
    stringstream ss;
    // << fill  = '0'  << 16 char  << hex << value
    ss << setfill('0') << setw(16) << hex << HASH;
    return ss.str();
}

int main() {
    // --- TEST CASE ---
    string texts[2] = {"ABC", "ABD"};
    u64 res[2];
    string hex[2];

    // Gọi hàm băm
    for (int i = 0; i < 2; i++){
        cout << "\nXỬ LÝ CHUỖI: \"" << texts[i] << "\"" << endl;
        res[i] = hashing(texts[i]);
    }

    // Gọi hàm chuyển đổi
    hex[0] = intToHex(res[0]);
    hex[1] = intToHex(res[1]);

    // In kết quả
    cout << "\nKết quả băm: " << endl;
    cout << "-----------------------------------" << endl;
    cout << "Input 1 : \"" << texts[0] << "\"" << endl;
    cout << "Hash Int: " << res[0] << endl;
    cout << "Hash Hex: " << hex[0] << endl;
    cout << "-----------------------------------" << endl;
    cout << "Input 2 : \"" << texts[1] << "\"" << endl;
    cout << "Hash Int: " << res[1] << endl;
    cout << "Hash Hex: " << hex[1] << endl;
    cout << "-----------------------------------" << endl;

    system("pause");
    return 0;
}