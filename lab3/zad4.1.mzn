include "globals.mzn";


int: N = 8;


array[1..N] of var 1..N: rows; 
array[1..N] of var 1..N: cols; 


constraint alldifferent(rows);                          
constraint alldifferent([rows[i] + i | i in 1..N]);         
constraint alldifferent([rows[i] - i | i in 1..N]);         

constraint inverse(rows, cols);

solve satisfy;

output [
    "Rozwiązanie przy użyciu inverse:\n",
    "rows: ", show(rows), "\n",
    "cols: ", show(cols)
];