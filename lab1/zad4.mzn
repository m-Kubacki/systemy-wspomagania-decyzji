
int:n = 6; % Liczba dostępnych posiłków
array[1..n] of int: ceny = [215, 275, 335, 355, 420, 580];
array[1..n] of string: nazwy = ["Owoce", "Frytki", "Sałatka", "Skrzydełka", "Paluszki", "Zestaw próbny"];
array[1..n] of int: yumyum = [0, 0, 1, 1, 2, 3];
int: target = 1505;

array[1..n] of var 0..target div min(ceny): x;

constraint sum(i in 1..n) (x[i] * ceny[i]) = target;

var int: total_yumyum = sum(i in 1..n) (x[i] * yumyum[i]);

solve maximize total_yumyum;


