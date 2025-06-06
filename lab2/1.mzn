include "globals.mzn";
%zad 1
int: N = 8;
array[1..N] of var 1..N: queens; % queens[i] to kolumna, w której stoi hetman w wierszu i

% Każdy hetman musi być w osobnym wierszu i kolumnie
constraint all_different(queens);

% Hetmany nie mogą atakować się po przekątnych
constraint all_different([queens[i] + i | i in 1..N]);
constraint all_different([queens[i] - i | i in 1..N]);

solve satisfy;

% Wyświetlanie wyniku jako szachownicy
output [
    concat([ if fix(queens[i]) == j then "H " else ". " endif | j in 1..N ]) ++ "\n" | i in 1..N
];