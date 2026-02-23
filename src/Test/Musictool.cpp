#include <windows.h>
#include <iostream>
#include <vector>
#include <tuple>
#include <chrono>
#include <thread>
#include <cmath>

using namespace std;

// --- CẤU HÌNH ---
const int Y_COORD = 915;
const vector<int> X_COORDS = {420, 635, 850, 1070, 1285, 1500};
const vector<int> VK_KEYS = {0x53, 0x44, 0x46, 0x4A, 0x4B, 0x4C}; // S, D, F, J, K, L
const vector<tuple<int, int, int>> BASE_COLORS(6, make_tuple(255, 255, 255));
const int CHANNEL_TOLERANCE = 25;
// ----------------

// Class hỗ trợ đọc pixel siêu tốc bằng BitBlt
class FastPixelReader {
private:
    HDC hScreenDC;
    HDC hMemoryDC;
    HBITMAP hBitmap;
    HGDIOBJ hOldBitmap;
    int minX, width, yPos;

public:
    FastPixelReader(int min_x, int max_x, int y) {
        minX = min_x;
        width = max_x - min_x + 1;
        yPos = y;

        // Khởi tạo thiết bị ảo trong RAM
        hScreenDC = GetDC(NULL);
        hMemoryDC = CreateCompatibleDC(hScreenDC);
        hBitmap = CreateCompatibleBitmap(hScreenDC, width, 1); // Chỉ tạo 1 dải ngang cao 1 pixel
        hOldBitmap = SelectObject(hMemoryDC, hBitmap);
    }

    ~FastPixelReader() {
        // Dọn dẹp RAM khi tắt bot
        SelectObject(hMemoryDC, hOldBitmap);
        DeleteObject(hBitmap);
        DeleteDC(hMemoryDC);
        ReleaseDC(NULL, hScreenDC);
    }

    void Update() {
        // Chụp dải màn hình (từ X nhỏ nhất đến X lớn nhất) đưa vào RAM
        BitBlt(hMemoryDC, 0, 0, width, 1, hScreenDC, minX, yPos, SRCCOPY);
    }

    tuple<int, int, int> GetColorAt(int x) {
        // Đọc màu từ RAM cực nhanh
        COLORREF color = GetPixel(hMemoryDC, x - minX, 0);
        return make_tuple(GetRValue(color), GetGValue(color), GetBValue(color));
    }
};

bool is_color_changed(tuple<int, int, int> current, tuple<int, int, int> base, int tolerance) {
    int r1, g1, b1, r2, g2, b2;
    tie(r1, g1, b1) = current;
    tie(r2, g2, b2) = base;
    return (abs(r1 - r2) > tolerance) || (abs(g1 - g2) > tolerance) || (abs(b1 - b2) > tolerance);
}

void send_key_event(int vk, bool press) {
    INPUT input = {0};
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = vk;
    if (!press) {
        input.ki.dwFlags = KEYEVENTF_KEYUP;
    }
    SendInput(1, &input, sizeof(INPUT));
}

int main() {
    cout << "🚀 Ready!!" << endl;
    cout << "Phím SPACE: Bật/Tạm dừng | Phím ESC: Thoát" << endl;

    vector<bool> key_states(6, false);
    bool macro_active = false;
    bool last_space_state = false;

    // Tìm điểm bắt đầu và kết thúc để chụp màn hình
    int min_x = X_COORDS.front();
    int max_x = X_COORDS.back();
    FastPixelReader screenReader(min_x, max_x, Y_COORD);

    while (true) {
        // Toggle macro bằng SPACE
        if (GetAsyncKeyState(VK_SPACE) & 0x8000) {
            if (!last_space_state) {
                macro_active = !macro_active;
                cout << (macro_active ? "[▶️ Start]" : "[⏸️ Pause]") << "..." << endl;
                last_space_state = true;
            }
        } else {
            last_space_state = false;
        }

        // Thoát bằng ESC
        if (GetAsyncKeyState(VK_ESCAPE) & 0x8000) {
            cout << "❌ Exitting..." << endl;
            break;
        }

        if (macro_active) {
            // Cập nhật dải pixel vào RAM
            screenReader.Update();

            for (size_t i = 0; i < 6; ++i) {
                auto current_color = screenReader.GetColorAt(X_COORDS[i]);

                if (is_color_changed(current_color, BASE_COLORS[i], CHANNEL_TOLERANCE)) {
                    if (!key_states[i]) {
                        send_key_event(VK_KEYS[i], true); // Nhấn
                        key_states[i] = true;
                    }
                } else {
                    if (key_states[i]) {
                        send_key_event(VK_KEYS[i], false); // Nhả
                        key_states[i] = false;
                    }
                }
            }
        }

        this_thread::sleep_for(chrono::milliseconds(1));
    }

    // Nhả toàn bộ phím đang giữ trước khi thoát
    for (size_t i = 0; i < 6; ++i) {
        if (key_states[i]) {
            send_key_event(VK_KEYS[i], false);
        }
    }
    ExitProcess(0);
    return 0;
}