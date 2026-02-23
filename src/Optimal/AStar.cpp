#include <bits/stdc++.h>
using namespace std;

// ===== Cấu trúc dữ liệu Node =====
struct Node {
    int x, y;   // tọa độ
    int R, G;   // thời gian đèn đỏ, xanh
    int C;      // 0 = đỏ, 1 = xanh (tại t=0)
    int Trem;   // thời gian còn lại của màu hiện tại (t=0)
};

// ===== Toàn cục =====
int Speed = 10; // vận tốc

// ===== Hàm tính thời gian di chuyển giữa 2 node =====
double distanceTime(const Node& a, const Node& b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    double dist = sqrt(dx*dx + dy*dy);
    return dist / Speed;
}

// ===== Hàm heuristic (ước lượng còn lại đến đích) =====
double heuristic(const Node& a, const Node& dest) {
    return distanceTime(a, dest);
}

// ===== Hàm tính thời gian chờ tại node i =====
double waitTime(const Node& node, double t) {
    int R = node.R, G = node.G;
    int T = R + G;
    if (T == 0) return 0.0; // không có đèn

    int offset = 0;
    if (node.C == 0) { 
        // đang đỏ
        offset = (R - node.Trem) % T;
    } else { 
        // đang xanh
        offset = (R + (G - node.Trem)) % T;
    }
    if (offset < 0) offset += T;

    double pos = fmod(offset + t, (double)T);
    if (pos < R) {
        return R - pos; // còn đỏ
    }
    return 0.0; // xanh
}

// ===== Truy vết đường đi =====
vector<int> reconstructPath(vector<int>& parent, int dest) {
    vector<int> path;
    for (int v = dest; v != -1; v = parent[v]) path.push_back(v);
    reverse(path.begin(), path.end());
    return path;
}

// ===== Thuật toán A* =====
pair<double, vector<int>> aStar(
        int start, int dest,
        const vector<Node>& nodes,
        const vector<vector<pair<int,double>>>& adj) 
{
    int n = nodes.size();
    const double INF = 1e100;
    vector<double> g(n, INF);
    vector<int> parent(n, -1);

    struct State {
        int u;
        double f, g;
        bool operator<(const State& other) const {
            return f > other.f; // ưu tiên f nhỏ
        }
    };

    priority_queue<State> pq;
    g[start] = 0;
    pq.push({start, heuristic(nodes[start], nodes[dest]), 0});

    while (!pq.empty()) {
        auto cur = pq.top(); pq.pop();
        int u = cur.u;
        if (cur.g > g[u]) continue; 
        if (u == dest) break; // tới đích

        for (auto [v, w] : adj[u]) {
            double arriveU = g[u];
            double wait = waitTime(nodes[u], arriveU);
            double departU = arriveU + wait;
            double arriveV = departU + w;

            if (arriveV + 1e-12 < g[v]) {
                g[v] = arriveV;
                parent[v] = u;
                double f = arriveV + heuristic(nodes[v], nodes[dest]);
                pq.push({v, f, arriveV});
            }
        }
    }

    return {g[dest], reconstructPath(parent, dest)};
}

// ===== Main =====
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    // cout << "Nhap so Node, so Path: ";
    cin >> n >> m;

    vector<Node> nodes(n);
    // cout << "Nhap cac Node (X Y R G C Trem):\n";
    for (int i = 0; i < n; i++) {
        // if (i == 0) cout << "Start: ";
        // else if (i == n-1) cout << "End:   ";
        // else cout << "Node " << i << ": ";
        cin >> nodes[i].x >> nodes[i].y
            >> nodes[i].R >> nodes[i].G
            >> nodes[i].C >> nodes[i].Trem;
    }

    vector<vector<pair<int,double>>> adj(n);
    // cout << "Nhap " << m << " canh (u v):\n";
    for (int k = 0; k < m; k++) {
        int u, v;
        // cout << "Path " << k+1 << ": ";
        cin >> u >> v;
        double w = distanceTime(nodes[u], nodes[v]);
        adj[u].push_back({v,w});
        adj[v].push_back({u,w});
    }

    auto [totalTime, path] = aStar(0, n-1, nodes, adj);

    cout.setf(ios::fixed); cout << setprecision(3);
    cout << "\nTong thoi gian: " << totalTime << " giay\n";
    cout << "Duong di: ";
    for (size_t i=0; i<path.size(); i++) {
        if (i) cout << " -> ";
        cout << path[i];
    }
    cout << "\n";
    return 0;
}

/*
7 10
0 0 5 7 1 4
30 0 8 5 0 3
60 0 6 6 1 2
30 20 7 7 1 2
60 20 10 4 0 1
85 20 5 9 1 7
100 40 6 6 0 2
0 1
1 2
2 5
5 6
0 3
3 4
4 5
1 3
2 4
3 6
*/