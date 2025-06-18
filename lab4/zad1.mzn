include "globals.mzn";


int: N = 16; 
array[1..N] of var 1..N: rows;

constraint alldifferent(rows);
constraint alldifferent([rows[c] - c | c in 1..N]);
constraint alldifferent([rows[c] + c | c in 1..N]);
constraint rows[1] <= N div 2; 
constraint rows[2] != 2;

solve satisfy;

output ["Rozwiązanie dla N = \(N):\n"];
output ["Pozycje hetmanów (wiersz dla każdej kolumny): rows = \(rows)\n\n"];
output ["Plansza:\n"];
output [ if fix(rows[c]) == r then " Q" else " ." endif ++
         if c == N then "\n" else "" endif
       | r in 1..N, c in 1..N ];