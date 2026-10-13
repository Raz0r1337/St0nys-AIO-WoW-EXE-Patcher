function A { return , @(5, 7) }
function B { return , (A) }
function C { $r = A; return , $r }
$x = B; "B: count=$($x.Count) [0]=$($x[0]) [1]=$($x[1])"
$y = C; "C: count=$($y.Count) [0]=$($y[0]) [1]=$($y[1])"
