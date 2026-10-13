R('''            $s = ($srcY * $S + $x) * 4; $d = $xor + ($y * $S + $x) * 4
            $b[$d] = $rgba[$s + 2]; $b[$d + 1] = $rgba[$s + 1]; $b[$d + 2] = $rgba[$s]; $b[$d + 3] = $rgba[$s + 3]
            if ($rgba[$s + 3] -eq 0) { $m = $and + $y * $maskRow + ($x -shr 3); $b[$m] = $b[$m] -bor (0x80 -shr ($x -band 7)) }''',
'''            # ($si/$di statt $s/$d: PowerShell-Variablen sind nicht case-sensitiv, $s waere $S)
            $si = ($srcY * $S + $x) * 4; $di = $xor + ($y * $S + $x) * 4
            $b[$di] = $rgba[$si + 2]; $b[$di + 1] = $rgba[$si + 1]; $b[$di + 2] = $rgba[$si]; $b[$di + 3] = $rgba[$si + 3]
            if ($rgba[$si + 3] -eq 0) { $m = $and + $y * $maskRow + ($x -shr 3); $b[$m] = $b[$m] -bor (0x80 -shr ($x -band 7)) }''')
