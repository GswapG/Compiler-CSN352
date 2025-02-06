int n, m;
int ii[M], jj[M], ww[M];
int *eh[N], eo[N], *ei[N], eo_[N], mem[M * 10], *ptr = mem;
 
int *malloc_(int k) {
	int *aa = ptr;
 
	ptr += k;
	return aa;
}
 
int *realloc_(int *aa, int k, int k_) {
	int *bb = ptr;
 
	memcpy(bb, aa, k * sizeof *aa);
	ptr += k_;
	return bb;
}
 
void append(int d, int i) {
	int o = eo_[d]++;
	
	if (o >= 2 && (o & o - 1) == 0)
		ei[d] = realloc_(ei[d], o, o * 2);
	ei[d][o] = i;
}
 
long long dd[N]; int iq[N + 1], pq[N], cnt;
 
int lt(int i, int j) { return dd[i] < dd[j]; }
 
int p2(int p) {
	return (p *= 2) > cnt ? 0 : (p < cnt && lt(iq[p + 1], iq[p]) ? p + 1 : p);
}
 
void pq_up(int i) {
	int p, q, j;
 
	for (p = pq[i]; (q = p / 2) && lt(i, j = iq[q]); p = q)
		iq[pq[j] = p] = j;
	iq[pq[i] = p] = i;
}
 
void pq_dn(int i) {
	int p, q, j;
 
	for (p = pq[i]; (q = p2(p)) && lt(j = iq[q], i); p = q)
		iq[pq[j] = p] = j;
	iq[pq[i] = p] = i;
}
 
void pq_add_last(int i) {
	iq[pq[i] = ++cnt] = i;
}
 
int pq_remove_first() {
	int i = iq[1], j = iq[cnt--];
 
	if (j != i)
		pq[j] = 1, pq_dn(j);
	pq[i] = 0;
	return i;
}
 
void dijkstra() {
	int i, o;
 
	memset(dd, 0x3f, n * sizeof *dd), dd[0] = 0, pq_add_last(0);
	while (cnt) {
		i = pq_remove_first();
		for (o = eo[i]; o--; ) {
			int h = eh[i][o], j = jj[h];
			long long d = dd[i] + ww[h];
 
			if (dd[j] > d) {
				if (dd[j] == INF)
					pq_add_last(j);
				dd[j] = d, pq_up(j);
			}
		}
	}
}
 
int dd_[N];
 
void dijkstra_() {
	int i, d, o, o_, *ptr_;
 
	ptr_ = ptr;
	for (d = 0; d < n; d++)
		ei[d] = malloc_(2), eo_[d] = 0;
	for (i = 0; i < n; i++)
		dd_[i] = n;
	dd_[0] = 0, append(0, 0);
	for (d = 0; d < n; d++)
		for (o_ = 0; o_ < eo_[d]; o_++) {
			i = ei[d][o_];
			if (dd_[i] != d)
				continue;
			for (o = eo[i]; o--; ) {
				int h = eh[i][o], j = jj[h];
				long long d_ = d + dd[i] + ww[h] - dd[j];
 
				if (dd_[j] > d_)
					dd_[j] = d_, append(d_, j);
			}
		}
	for (i = 0; i < n; i++)
		if (dd[i] != INF)
			dd[i] += dd_[i];
	ptr = ptr_;
}
 
int main() {
	int q, k, h, i, t;
 
	scanf("%d%d%d", &n, &m, &q);
	for (h = 0; h < m; h++) {
		scanf("%d%d%d", &ii[h], &jj[h], &ww[h]), ii[h]--, jj[h]--;
		eo[ii[h]]++;
	}
	for (i = 0; i < n; i++)
		eh[i] = malloc_(eo[i]), eo[i] = 0;
	for (h = 0; h < m; h++) {
		i = ii[h];
		eh[i][eo[i]++] = h;
	}
	dijkstra();
	while (q--) {
		scanf("%d", &t);
		if (t == 1) {
			scanf("%d", &i), i--;
			printf("%lld\n", dd[i] == INF ? -1 : dd[i]);
		} else {
			scanf("%d", &k);
			while (k--) {
				scanf("%d", &h), h--;
				ww[h]++;
			}
			dijkstra_();
		}
	}
	return 0;
}
