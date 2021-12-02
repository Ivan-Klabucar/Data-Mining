% When you switch between datasets change k to the relevant number of
% clusters
E = csvread('./data/example1.dat');
%E = csvread('./data/example2.dat');
k = 4; % because we know we are searching for 4/2 clusters
col1 = E(:,1);
col2 = E(:,2);
max_ids = max(max(col1,col2));
As= sparse(col1, col2, 1, max_ids, max_ids);

% Step 1. Affinity matrix
A = full(As);

% Step 2. 
node_degrees = sum(A, 2);
D = diag(node_degrees);
L = D^(-0.5) * A * D^(-0.5);

% Step 3. Calculate k eigenvectors with largest eigen values
[X, D] = eigs(L, k, 'LA'); % matrix

% Step 4. renormalize X
X_row_denominator = sum(X.^2, 2).^(0.5);
Y = X ./ X_row_denominator;

% Step 5. k-means on Y
%node_clusters = kmeans(Y,k,'Display','final','Replicates',30)
node_clusters = kmeans(Y,k) % Vector where each node is assigned a cluster
writematrix(node_clusters, './data/nodes_by_cluster1.txt');


