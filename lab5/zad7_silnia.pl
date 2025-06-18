% Silnia: factorial(N, Result)
factorial(0, 1) :- !.
factorial(N, Result) :-
    N > 0,
    N1 is N - 1,
    factorial(N1, R1),
    Result is N * R1.
