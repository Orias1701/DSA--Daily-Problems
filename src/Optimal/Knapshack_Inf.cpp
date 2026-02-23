#include <bits/stdc++.h>
using namespace std;

int n, W;

int max(int a, int b) { return (a > b) ? a : b; }

vector<vector<int>> unboundedKnapsack(const vector<int>& weights, const vector<int>& values) {
    vector<vector<int>> DP(n + 1, vector<int>(W + 1, 0));

    for (int i = 0; i <= n; i++) {
        for (int w = 0; w <= W; w++) {
            if (i == 0 || w == 0) {
                DP[i][w] = 0;
            } else if (weights[i - 1] <= w) {
                DP[i][w] = max(values[i - 1] + DP[i][w - weights[i - 1]], DP[i - 1][w]);
            } else {
                DP[i][w] = DP[i - 1][w];
            }
        }
    }
    return DP;
}

void printDP(const vector<vector<int>>& DP) {
    cout << "\nDP Table:\n";
    for (int i = 0; i <= n; i++) {
        for (int w = 0; w <= W; w++) {
            cout << setw(6) << DP[i][w];
        }
        cout << "\n";
    }
}

void selected(const vector<vector<int>>& DP, const vector<int>& weights, const vector<int>& values) {
    int res = DP[n][W];
    cout << "\nMax Value: " << res << "\n";

    int w = W;
    cout << "\nSelected Objects: \n";
    for (int i = n; i > 0 && res > 0; i--) {
        if (res == DP[i - 1][w]) continue;
        else {
            cout << i << "  -  Weight: " << weights[i - 1] << "  -  Value: " << values[i - 1] << "\n";
            res -= values[i - 1];
            w -= weights[i - 1];
        }
    }
}

void knapsack(const vector<int>& weights, const vector<int>& values) {
    vector<vector<int>> DP = unboundedKnapsack(weights, values);
    if (W <= 25) printDP(DP);
    selected(DP, weights, values);
}

int main() {
    cout << "Number of Object: ";
    cin >> n;
    cout << "Enter max Weight: ";
    cin >> W;

    vector<int> weights(n), values(n);

    cout << "\nEnter object information:\n";
    for (int i = 0; i < n; i++) {
        cout << "\nObject " << i + 1 << ":\n";
        cout << "Weight: ";
        cin >> weights[i];
        cout << "Value:  ";
        cin >> values[i];
    }

    knapsack(weights, values);
    return 0;
}
