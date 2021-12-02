E = csvread('./data/my_example.dat');
col1 = E(:,1);
col2 = E(:,2);
max_ids = max(max(col1,col2));
As= sparse(col1, col2, 1, max_ids, max_ids);
A = full(As);
node_degrees = sum(A, 2);
A_normalized = A ./ node_degrees;
[v,D] = eig(A_normalized);
v(:,1) % eigenvector
v(:,5) % eigenvector
v(:,6) % eigenvector

G = graph(A);
L = laplacian(G);
Lap = full(L);
[v2,D2] = eig(Lap)
v2(:1) % eigenvector of Laplacian
v2(:2) % eigenvector of Laplacian
v2(:3) % eigenvector of Laplacian