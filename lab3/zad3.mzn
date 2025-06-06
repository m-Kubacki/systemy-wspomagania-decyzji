
int: n;
set of int: range = 0..n-1;

array[range] of var range: magic;

constraint
  forall(i in range)(
    magic[i] = sum(j in range)(bool2int(magic[j] = i))
  );


constraint
  sum(i in range)(magic[i]) = n;

constraint
  sum(i in range)(magic[i] * i) = n;

solve satisfy;

output ["magic = ", show(magic)];