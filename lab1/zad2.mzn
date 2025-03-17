int: target = 1505;

array[1..6] of int: ceny = [215, 275, 335, 355, 420, 580];
array[1..6] of string: nazwy = ["owoce", "frytki", "salatka", "skrzydelka", "paluszki", "zestaw_probny"]; 

array[1..6] of var 0..target div min(ceny): x;

constraint sum(i in 1..6) (x[i] * ceny[i]) = target;

solve satisfy;


