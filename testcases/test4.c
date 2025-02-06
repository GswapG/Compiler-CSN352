long long power(long long a, int k) {
	long long p = 1;
 
	while (k) {
		if (k & 1)
			p = p * a % md;
		a = a * a % md;
		k >>= 1;
	}
	return p;
}
 
int vv[N], ff[N], gg[N], kk[N];
 
void init() {
	int i, b;
 
	ff[0] = gg[0] = 1;
	for (i = 1; i < N; i++) {
		vv[i] = i == 1 ? 1 : (long long) vv[i - md % i] * (md / i + 1) % md;
		ff[i] = (long long) ff[i - 1] * i % md;
		gg[i] = (long long) gg[i - 1] * vv[i] % md;
	}
	for (b = 1; b < N; b++)
		kk[b] = kk[b & b - 1] + 1;
}
 
void exp_(int *aa, int n) {
	static int bb[L + 1];
	int i, j, x;
 
	bb[0] = 1;
	for (i = 1; i < n; i++) {
		x = 0;
		for (j = 1; j <= i; j++)
			x = (x + (long long) bb[i - j] * aa[j] % md * j) % md;
		bb[i] = (long long) x * vv[i] % md;
	}
	memcpy(aa, bb, n * sizeof *bb);
}
 
void log_(int *aa, int n) {
	static int bb[L + 1];
	int i, j, x;
 
	bb[0] = 0;
	for (i = 1; i < n; i++) {
		x = (long long) aa[i] * i % md;
		for (j = 1; j < i; j++)
			x = (x - (long long) aa[i - j] * bb[j] % md * j % md + md) % md;
		bb[i] = (long long) x * vv[i] % md;
	}
	memcpy(aa, bb, n * sizeof *bb);
}
 
int solve(int n, int a) {
	static int dp[N][L + 1];
	int l, h, b, k;
 
	l = 0;
	while (1 << l <= n)
		l++;
	for (b = 0; b < 1 << l; b++)
		dp[b][kk[b]] = gg[b];
	for (h = 0; h < l; h++)
		for (b = 0; b < 1 << l; b++)
			if ((b & 1 << h) != 0)
				for (k = 0; k <= l; k++)
					dp[b][k] = (dp[b][k] + dp[b ^ 1 << h][k]) % md;
	for (b = 0; b < 1 << l; b++) {
		log_(dp[b], l + 1);
		for (k = 0; k <= l; k++)
			dp[b][k] = (long long) dp[b][k] * a % md;
		exp_(dp[b], l + 1);
	}
	for (h = 0; h < l; h++)
		for (b = 0; b < 1 << l; b++)
			if ((b & 1 << h) != 0)
				for (k = 0; k <= l; k++)
					dp[b][k] = (dp[b][k] - dp[b ^ 1 << h][k] + md) % md;
	return (long long) dp[n][kk[n]] * ff[n] % md;
}
 
int main() {
	int n, a;
 
	scanf("%d%d%d", &n, &a, &md), init();
	printf("%lld\n", (power(a, n) - (n % 2 != 0 ? 0 : solve(n, a)) + md) % md);
	return 0;
}