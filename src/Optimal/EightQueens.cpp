#include <iostream>
#include <cmath>
#include <iomanip>

using namespace std;

int hau[20], dong, cot;
int n, dem = 0;

int abs(int x) {
    return (x < 0) ? -x : x;
}

bool xung_dot() {
    int i = 0;
    bool found = false;
    while (!found && (i < cot)) {
        found = (dong == hau[i]) || (cot - i == abs(dong - hau[i]));
        i++;
    }
    return found;
}

void in_nghiem() {
    cout << "\n" << setw(8) << ++dem << ": ";
    for (int i = 0; i < n; i++) {
        cout << setw(8) << hau[i];
    }
}

int main() {
    cout << "Nhap so quan hau: ";
    cin >> n;

    dong = cot = 0;
    while (cot >= 0) {
        while (dong < n) {
            if (xung_dot()) {
                dong++;
            } else {
                hau[cot] = dong;
                cot++;
                dong = 0;
                if (cot == n) {
                    in_nghiem();
                    dong = n;
                }
            }
        }
        cot--;
        dong = hau[cot] + 1;
    }
    cout << "\n\nTong so nghiem: " << dem;
    return 0;
}
