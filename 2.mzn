%zad 2
int: n = 4; % liczba wierzchołków
set of int: V = 1..n; % zbiór wierzchołków
array[V] of var 1..n: kolor; % kolory wierzchołków

int: m = 4; % liczba krawędzi
array[1..m, 1..2] of int: edges = array2d(1..m, 1..2, [1,2, 2,3, 3,4, 4,1]); % lista krawędzi

constraint forall(i in 1..m) (
    kolor[edges[i,1]] != kolor[edges[i,2]] % sąsiednie wierzchołki mają różne kolory
);

solve minimize max(kolor); % minimalizujemy liczbę kolorów

output ["Kolory: \n" ++ concat([show(kolor[i]) ++ " " | i in V])];