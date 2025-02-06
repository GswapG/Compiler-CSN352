int min(int a, int b) { return a < b ? a : b; }
 
unsigned int Z;
 
int rand_() {
	return (Z *= 3) >> 1;
}
 
void srand_() {
	struct timeval tv;
 
	gettimeofday(&tv, NULL);
	Z = tv.tv_sec ^ tv.tv_usec | 1;
}
 
int dd[N][N], n;
int uu[M], vv[M], ww[M];
 
void sort(int *hh, int l, int r) {
	while (l < r) {
		int i = l, j = l, k = r, h = hh[l + rand_() % (r - l)], tmp;
 
		while (j < k)
			if (ww[hh[j]] == ww[h])
				j++;
			else if (ww[hh[j]] < ww[h]) {
				tmp = hh[i], hh[i] = hh[j], hh[j] = tmp;
				i++, j++;
			} else {
				k--;
				tmp = hh[j], hh[j] = hh[k], hh[k] = tmp;
			}
		sort(hh, l, i);
		l = k;
	}
}
 
void relax(int k) {
	int i, j;
 
	for (i = 0; i < n; i++)
		for (j = 0; j < n; j++)
			dd[i][j] = min(dd[i][j], dd[i][k] + dd[k][j]);
}
 
int main() {
	int t;
 
	srand_();
	scanf("%d", &t);
	while (t--) {
		static int hh[M], ii[Q], jj[Q], kk[Q], ans[Q];
		int m, q, g, h, h_, i, j;
 
		scanf("%d%d%d", &n, &m, &q);
		for (h = 0; h < m; h++)
			scanf("%d%d%d", &uu[h], &vv[h], &ww[h]), uu[h]--, vv[h]--;
		for (g = 0; g < q; g++)
			scanf("%d%d%d", &ii[g], &jj[g], &kk[g]), ii[g]--, jj[g]--;
		for (h = 0; h < m; h++)
			hh[h] = h;
		sort(hh, 0, m);
		for (i = 0; i < n; i++)
			memset(dd[i], 0x3f, n * sizeof *dd[i]), dd[i][i] = 0;
		for (h = 0; h < m; h++) {
			i = uu[h], j = vv[h];
			dd[i][j] = dd[j][i] = 1;
		}
		for (i = 0; i < n; i++)
			relax(i);
		memset(ans, 0, q * sizeof *ans);
		for (h = 0; h < m; h++) {
			h_ = hh[h], i = uu[h_], j = vv[h_];
			if (dd[i][j] == 0)
				continue;
			dd[i][j] = dd[j][i] = 0, relax(i), relax(j);
			for (g = 0; g < q; g++)
				if (ans[g] == 0 && dd[ii[g]][jj[g]] < kk[g])
					ans[g] = ww[h_];
		}
		for (g = 0; g < q; g++)
			printf("%d ", ans[g]);
		printf("\n");
	}
	return 0;
}