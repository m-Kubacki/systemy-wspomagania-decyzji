kwadrat(A, B, C, Roots) :-
    delta(A, B, C, Delta),       % Najpierw obliczamy delte
    (   Delta < 0                % Przypadek 1: Delta ujemna
    ->  Roots = []               % Brak pierwiastków rzeczywistych
    ;   Delta =:= 0              % Przypadek 2: Delta równa zero (uzywamy =:=)
    ->  X0 is -B / (2*A),   % Obliczanie delty
delta(A, B, C, Delta) :-
    Delta is B * B - 4 * A * C.

% Rozwiązywanie równania kwadratowego (dla rzeczywistych pierwiastków)
kwadrat(A, B, C, X1, X2) :-
    delta(A, B, C, Delta),
    Delta >= 0,
    SqrtDelta is sqrt(Delta),
    X1 is (-B + SqrtDelta) / (2 * A),
    X2 is (-B - SqrtDelta) / (2 * A).

% Obsługa braku pierwiastków rzeczywistych
kwadrat(A, B, C, _, _) :-
    delta(A, B, C, Delta),
    Delta < 0,
    write('Brak rozwiazan rzeczywistych'), nl,
    fail.
     % Obliczamy jeden pierwiastek
        Roots = [X0]             % Lista z jednym pierwiastkiem
    ;   % Delta > 0              % Przypadek 3: Delta dodatnia (niejawny else)
        SqrtDelta is sqrt(Delta),% Obliczamy pierwiastek z delty
        X1 is (-B - SqrtDelta) / (2*A), % Obliczamy pierwszy pierwiastek
        X2 is (-B + SqrtDelta) / (2*A), % Obliczamy drugi pierwiastek
        Roots = [X1, X2]         % Lista z dwoma pierwiastkami
    ).

% Predykat pomocniczy delta/4
delta(A, B, C, Delta) :-
    Delta is B*B - 4*A*C.