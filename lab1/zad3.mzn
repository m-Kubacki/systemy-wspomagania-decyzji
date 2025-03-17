include "C:/Users/Michal/Desktop/Idz na studia mowili/semestr 6/systemy wspomagania decyzji SWD/lab1/zad_3_dane.dzn";


int: n;
array[1..n] of int: ceny;
array[1..n] of string: nazwy;
int: target;

array[1..n] of var 0..target div min(ceny): x;

constraint sum(i in 1..n) (x[i] * ceny[i]) = target;

solve satisfy;


