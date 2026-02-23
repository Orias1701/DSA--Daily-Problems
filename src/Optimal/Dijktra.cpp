#include <bits/stdc++.h>
using namespace std;

struct Node {
    double x, y;
    int R, G;   // chu kỳ đèn đỏ, xanh
    int state;  // 0 = đỏ, 1 = xanh
    int time; // thời gian còn lại
};

struct Edge {
    int u, v;
    double w;
};

struct State {
    int u;
    double g, f;
    bool operator<(const State &other) const {
        return f > other.f; // min-heap
    }
};

int N, P, D;
vector<Node> nodes;
vector<vector<pair<int,double>>> adj;
vector<int> goals;

double distEuclid(int a, int b) {
    double dx = nodes[a].x - nodes[b].x;
    double dy = nodes[a].y - nodes[b].y;
    return sqrt(dx*dx + dy*dy);
}

// Tính thời gian chờ tại node u khi đến lúc t
double waitTime(int u, double t) {
    if (u == 0) return 0.0; // node xuất phát luôn xanh
    Node &nd = nodes[u];
    int cycle = nd.R + nd.G;
    double passed;
    // Xác định trạng thái tại t=0
    if (nd.state == 0) {
        passed = nd.R - nd.time; // đang ở đỏ
    } else {
        passed = nd.R + (nd.G - nd.time); // đang ở xanh
    }
    double modT = fmod(passed + t, (double)cycle);

    if (modT < nd.R) {
        return nd.R - modT; // còn đang đỏ
    }
    return 0.0; // đang xanh
}

double Astar(int start, int goal) {
    vector<double> g(nodes.size(), 1e18);
    priority_queue<State> pq;
    g[start] = 0.0;
    pq.push({start, 0.0, distEuclid(start, goal)});

    while (!pq.empty()) {
        auto cur = pq.top(); pq.pop();
        int u = cur.u;
        if (u == goal) return g[u];
        if (cur.g > g[u]) continue;

        for (auto [v, w] : adj[u]) {
            double arrive = g[u] + w;
            double wait = waitTime(v, arrive);
            double newG = arrive + wait;
            if (newG < g[v]) {
                g[v] = newG;
                double f = newG + distEuclid(v, goal);
                pq.push({v, newG, f});
            }
        }
    }
    return 1e18;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cout << "Nhập số Node, Path, Destination ngăn cách bằng dấu cách:" << endl;
    cin >> N >> P >> D;

    // Node 0 mặc định
    nodes.push_back({0, 0, 0, 0, 1, 0});

    cout << "\n" << N << " Nodes:\n";
    cout << "X, Y: Tọa độ Node\n";
    cout << "R, G: Chu kì đèn Đỏ, Xanh của Node\n";
    cout << "S: Trạng thái hiện tại: 1 = G, 0 = R\n";
    cout << "T: Thời gian còn lại của trạng thái S\n";
    cout << "Mỗi dòng nhập X Y R G S T của 1 Node:" << endl;
    // Đọc N node
    for (int i = 1; i <= N; i++) {
        Node nd;
        cin >> nd.x >> nd.y >> nd.R >> nd.G >> nd.state >> nd.time;
        nodes.push_back(nd);
    }

    cout << "\n" << P << " Paths:\n";
    cout << "Mỗi dòng nhập STT 2 nốt tạo thành Path:" << endl;
    adj.assign(N+1, {});
    // Đọc P cạnh
    for (int i = 0; i < P; i++) {
        int u, v; cin >> u >> v;
        double d = distEuclid(u, v);
        adj[u].push_back({v, d});
        adj[v].push_back({u, d});
    }

    cout << "\n" << D << " Đích:\n";
    cout << "Nhập STT của các đích cách nhau bởi dấu cách:" << endl;
    goals.resize(D);
    for (int i = 0; i < D; i++) cin >> goals[i];
    
    cout << "\nĐộ dài đường đi ngắn nhất đến các điểm đích:" << endl;
    // Chạy A*
    for (int g : goals) {
        double ans = Astar(0, g);
        if (ans > 1e17) {
            cout << "Node " << g 
                << " (" << nodes[g].x << ", " << nodes[g].y << ")"
                << " : INF\n\n";
        } else {
            cout << "Node " << g 
                << " (" << nodes[g].x << ", " << nodes[g].y << ")"
                << " : " << fixed << setprecision(2) << ans << "\n\n";
        }
    }

    return 0;
}
