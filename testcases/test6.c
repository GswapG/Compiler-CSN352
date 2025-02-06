int query(int i, int j) {
	int c;
 
	printf("? %d %d\n", i + 1, j + 1), fflush(stdout);
	scanf("%d", &c);
	return c;
}
 
int main() {
	int t;
 
	scanf("%d", &t);
	while (t--) {
		static int qu[N], uu[M], vv[M], ww[M];
		int n, m, cnt, h, i, c, c_;
 
		scanf("%d", &n);
		printf("%d\n", (n + 1) / 3);
		cnt = 0, c_ = 0, m = 0;
		for (i = 0; i < n; i++)
			if (cnt == 0)
				qu[cnt++] = i;
			else {
				c = query(qu[cnt - 1], i);
				if (cnt == 1)
					c_ = c;
				if (c == c_)
					qu[cnt++] = i;
				else {
					if (c == 0)
						uu[m] = i, vv[m] = qu[cnt - 1], ww[m] = qu[cnt - 2];
					else
						uu[m] = qu[cnt - 2], vv[m] = qu[cnt - 1], ww[m] = i;
					m++;
					cnt -= 2;
				}
			}
		printf("!");
		for (h = 0; h + 1 < cnt; h += 3)
			printf(" %d %d", qu[h] + 1, qu[h + 1] + 1);
		if (cnt <= 1 || c_ == 0)
			while (m--)
				printf(" %d %d", uu[m] + 1, vv[m] + 1);
		else
			while (m--)
				printf(" %d %d", vv[m] + 1, ww[m] + 1);
		printf("\n"), fflush(stdout);
	}
	return 0;
}