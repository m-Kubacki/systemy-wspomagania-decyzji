% Use this editor as a MiniZinc scratch book

int: nodesNumber;
int: minColorsNumber;
array[1..nodesNumber, 1..nodesNumber] of bool: edges;

array[int] of int: maxClique;

array[1..nodesNumber] of var 1..nodesNumber: nodes;
var 1..nodesNumber: colorsNumber;

constraint colorsNumber = max(nodes);

constraint forall(i, j in 1..nodesNumber where edges[i, j]) (
  nodes[i] != nodes[j]
);

constraint forall(i in 1..minColorsNumber) (
  nodes[i] = i
);

constraint forall(i, j in index_set(maxClique) where i < j) (
  nodes[maxClique[i]] != nodes[maxClique[j]]
);

solve minimize colorsNumber;

output [
  "colorsNumber = \(colorsNumber)\n",
  "nodes = \(nodes)\n"
];