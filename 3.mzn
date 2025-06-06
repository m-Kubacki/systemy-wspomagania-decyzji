% Zadanie 3

include "globals.mzn";

array[1..9, 1..9] of var 1..9: grid;

constraint forall(i in 1..9) (
    all_different([grid[i, j] | j in 1..9]) /\  % Wiersze
    all_different([grid[j, i] | j in 1..9])     % Kolumny
);

constraint forall(i in 0..2, j in 0..2) (
    all_different([grid[3*i + k, 3*j + l] | k in 1..3, l in 1..3]) % Bloki 3x3
);

solve satisfy;

output ["Sudoku rozwiązane:\n" ++ concat([ if j == 9 then show(grid[i,j]) ++ "\n" else show(grid[i,j]) ++ " " endif | i in 1..9, j in 1..9])];