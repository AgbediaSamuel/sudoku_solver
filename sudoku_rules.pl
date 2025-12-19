% Sudoku Constraint Rules for n^2 x n^2 boards
% Simplified version that works with pyswip

% Check if a value appears in a list
member_check(X, [X|_]).
member_check(X, [_|T]) :- member_check(X, T).

% Check if a value is NOT in a list (for constraint checking)
not_in_list(_, []).
not_in_list(X, [H|T]) :- X \= H, not_in_list(X, T).

% Extract a row from the board
get_row(Board, RowIdx, Row) :-
    nth0(RowIdx, Board, Row).

% Extract a column from the board
get_col([], _, []).
get_col([Row|Rows], ColIdx, [Val|Vals]) :-
    nth0(ColIdx, Row, Val),
    get_col(Rows, ColIdx, Vals).

% Extract a box/subgrid - simplified version
% For a 9x9 board (n=3), box at (row, col) is determined by (row//3, col//3)
get_box(Board, RowIdx, ColIdx, N, Box) :-
    BoxRow is (RowIdx // N) * N,
    BoxCol is (ColIdx // N) * N,
    extract_box(Board, BoxRow, BoxCol, N, 0, Box).

% Extract box values by iterating through rows
extract_box(_, _, _, N, N, []) :- !.
extract_box(Board, StartRow, StartCol, N, RowOffset, Result) :-
    RowOffset < N,
    ActualRow is StartRow + RowOffset,
    nth0(ActualRow, Board, Row),
    extract_box_row(Row, StartCol, N, 0, RowValues),
    NextRow is RowOffset + 1,
    extract_box(Board, StartRow, StartCol, N, NextRow, RestValues),
    append(RowValues, RestValues, Result).

% Extract N values from a row starting at StartCol
extract_box_row(_, _, N, N, []) :- !.
extract_box_row(Row, StartCol, N, ColOffset, [Val|Rest]) :-
    ColOffset < N,
    ActualCol is StartCol + ColOffset,
    nth0(ActualCol, Row, Val),
    NextCol is ColOffset + 1,
    extract_box_row(Row, StartCol, N, NextCol, Rest).

% Check if a move is valid (main constraint checker)
valid_move(Board, RowIdx, ColIdx, Value, N) :-
    % Value must not be 0 (empty cell marker)
    Value \= 0,
    % Check row constraint
    get_row(Board, RowIdx, Row),
    not_in_list(Value, Row),
    % Check column constraint
    get_col(Board, ColIdx, Col),
    not_in_list(Value, Col),
    % Check box constraint
    get_box(Board, RowIdx, ColIdx, N, Box),
    not_in_list(Value, Box).

% Find all valid values for a cell (simplified - just checks each value)
% This is called from Python with specific values to test
is_valid_value(Board, RowIdx, ColIdx, Value, N) :-
    valid_move(Board, RowIdx, ColIdx, Value, N).

% Check if the entire board is valid (no constraint violations)
valid_board(Board, N, BoardSize) :-
    length(Board, BoardSize),
    check_all_rows(Board),
    check_all_cols(Board, BoardSize, 0),
    check_all_boxes(Board, N, BoardSize).

% Helper predicates for board validation
check_all_rows([]).
check_all_rows([Row|Rows]) :-
    check_unique_nonzero(Row),
    check_all_rows(Rows).

check_all_cols(_, BoardSize, BoardSize) :- !.
check_all_cols(Board, BoardSize, ColIdx) :-
    ColIdx < BoardSize,
    get_col(Board, ColIdx, Col),
    check_unique_nonzero(Col),
    NextCol is ColIdx + 1,
    check_all_cols(Board, BoardSize, NextCol).

check_all_boxes(Board, N, BoardSize) :-
    BoxCount is BoardSize // N,
    check_boxes_iter(Board, N, BoxCount, 0, 0).

check_boxes_iter(_, _, BoxCount, BoxCount, _) :- !.
check_boxes_iter(Board, N, BoxCount, BoxRow, BoxCol) :-
    BoxRow < BoxCount,
    BoxCol < BoxCount,
    ActualRow is BoxRow * N,
    ActualCol is BoxCol * N,
    get_box(Board, ActualRow, ActualCol, N, Box),
    check_unique_nonzero(Box),
    NextCol is BoxCol + 1,
    (NextCol >= BoxCount ->
        (NextRow is BoxRow + 1, check_boxes_iter(Board, N, BoxCount, NextRow, 0))
    ;
        check_boxes_iter(Board, N, BoxCount, BoxRow, NextCol)
    ).

% Check that all non-zero values in a list are unique
check_unique_nonzero([]).
check_unique_nonzero([0|T]) :- !, check_unique_nonzero(T).
check_unique_nonzero([H|T]) :-
    H \= 0,
    not_in_list(H, T),
    check_unique_nonzero(T).
