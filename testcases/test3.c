long long choose(int n, int k) {
	return k == 0 ? 1 : (long long) choose(n - 1, k - 1) * n / k;
}
 
int main() {
	static int aa[N], bb[N];
	static long long dp[N + 1][2], dq[N + 1][2][2], tt[2][2];
	int n, a_, b_, d, k, u, u_, v, v_;
	long long a, b, x, ans;
 
	scanf("%lld%lld", &a, &b);
	n = 0;
	while (a > 0)
		aa[n++] = a % 10, a /= 10;
	n = 0;
	while (b > 0)
		bb[n++] = b % 10, b /= 10;
	n = N;
	while (n > 0 && aa[n - 1] == bb[n - 1])
		n--;
	if (n == 0) {
		printf("1\n");
		return 0;
	}
	a_ = aa[n - 1], b_ = bb[n - 1];
	ans = choose(n + D - 1, D - 1) - choose(n + D - (b_ - a_ - 1) - 1, D - (b_ - a_ - 1) - 1);
	for (k = 1; k <= n; k++)
		memset(dp[k], 0, sizeof dp[k]);
	dp[1][0] = 1;
	for (d = 0; d < D; d++) {
		if (d > a_ && d < b_)
			continue;
		for (k = 1; k < n; k++) {
			b = bb[n - 1 - k];
			for (u = 0; u < 2; u++) {
				x = dp[k][u];
				if (x == 0 || u == 0 && d > b)
					continue;
				u_ = u == 0 && d == b ? 0 : 1;
				dp[k + 1][u_] += x;
			}
		}
	}
	ans += dp[n][0] + dp[n][1];
	for (k = 1; k <= n; k++)
		memset(dp[k], 0, sizeof dp[k]);
	dp[1][0] = 1;
	for (d = D - 1; d >= 0; d--) {
		if (d > a_ && d < b_)
			continue;
		for (k = 1; k < n; k++) {
			a = aa[n - 1 - k];
			for (u = 0; u < 2; u++) {
				x = dp[k][u];
				if (x == 0 || u == 0 && d < a)
					continue;
				u_ = u == 0 && d == a ? 0 : 1;
				dp[k + 1][u_] += x;
			}
		}
	}
	ans += dp[n][0] + dp[n][1];
	if (n >= 2) {
		for (k = 2; k <= n; k++)
			memset(dq[k], 0, sizeof dq[k]);
		dq[2][0][1] = 1;
		for (d = D - 1; d >= 0; d--) {
			if (d > a_ && d < b_)
				continue;
			if (d == b_)
				for (k = 2; k <= n; k++) {
					a = aa[n - k];
					memset(tt, 0, sizeof tt);
					for (u = 0; u < 2; u++)
						for (v = 0; v < 2; v++) {
							x = dq[k][u][v];
							if (x == 0 || u == 0 && d < a)
								continue;
							u_ = u == 0 && d == a ? 0 : 1;
							tt[u_][v] += x;
						}
					memcpy(dq[k], tt, sizeof tt);
				}
			if (d == a_)
				for (k = 2; k <= n; k++) {
					b = bb[k - 2];
					memset(tt, 0, sizeof tt);
					for (u = 0; u < 2; u++)
						for (v = 0; v < 2; v++) {
							x = dq[k][u][v];
							if (x == 0)
								continue;
							v_ = d == b ? v : (d < b ? 1 : 0);
							tt[u][v_] += x;
						}
					memcpy(dq[k], tt, sizeof tt);
				}
			for (k = 2; k < n; k++) {
				a = aa[n - k - (d > b_ ? 0 : 1)], b = bb[k - 2 + (d > a_ ? 0 : 1)];
				for (u = 0; u < 2; u++)
					for (v = 0; v < 2; v++) {
						x = dq[k][u][v];
						if (x == 0 || u == 0 && d < a)
							continue;
						u_ = u == 0 && d == a ? 0 : 1;
						v_ = d == b ? v : (d < b ? 1 : 0);
						dq[k + 1][u_][v_] += x;
					}
			}
		}
		ans -= dq[n][0][1] + dq[n][1][1];
	}
	printf("%lld\n", ans);
	return 0;
}
