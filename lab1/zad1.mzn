int: owoce = 215;
int: frytki = 275;
int: salatka = 335;
int: skrzydelka = 355;
int: paluszki = 420;
int: zestaw_probny = 580;

int: target = 1505;

var 0..target div owoce: x1;
var 0..target div frytki: x2;
var 0..target div salatka: x3;
var 0..target div skrzydelka: x4;
var 0..target div paluszki: x5;
var 0..target div zestaw_probny: x6;

constraint x1 * owoce + x2 * frytki + x3 * salatka + x4 * skrzydelka + x5 * paluszki + x6 * zestaw_probny = target;

solve satisfy;

output ["Owoce: " ++ show(x1) ++ "\n" ++
        "Frytki: " ++ show(x2) ++ "\n" ++
        "Sałatka: " ++ show(x3) ++ "\n" ++
        "Skrzydełka: " ++ show(x4) ++ "\n" ++
        "Paluszki: " ++ show(x5) ++ "\n" ++
        "Zestaw próbny: " ++ show(x6) ++ "\n"];
