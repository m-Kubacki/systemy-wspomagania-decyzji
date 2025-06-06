int: items_n;
int: knapsacks_n;
int: capacity;

array[1..items_n] of int: values;
array[1..items_n] of int: weights;

array[1..items_n] of var 0..knapsacks_n: assigned;

constraint forall(k in 1..knapsacks_n) (
  sum(i in 1..items_n where assigned[i] == k)(weights[i]) <= capacity
);

var int: total_value = sum(i in 1..items_n where assigned[i] != 0)(values[i]);

solve maximize total_value;

output [
  "Total value: ", show(total_value), "\n",
  "Item assignments:\n"
] ++
[
  let { int: a = fix(assigned[i]) } in
    "Item \(i): " ++
    if a == 0 then "not packed\n" else "knapsack \(a)\n" endif
  | i in 1..items_n
];