include "globals.mzn";

int: N = 8;

array[1..N] of var 1..N: rows;


constraint alldifferent(rows);                            
constraint alldifferent([rows[i] + i | i in 1..N]);        
constraint alldifferent([rows[i] - i | i in 1..N]);        

solve satisfy;

output [
    "Rozwiązanie bez inverse:\n",
    "rows: ", show(rows)
];