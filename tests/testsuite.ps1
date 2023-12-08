function CFL {
    param(
        [string]$Prog,
        [string]$Exp
    )

    $output = Invoke-Expression "& $Prog"

    if ($output -ne $exp) {
        Write-Host "$Prog FAILED!"
    } 
}

CFL -Prog "python ..\analysis.py -i .\test1_noLeak.txt -s" -Exp "NO LEAK"
CFL -Prog "python ..\analysis.py -i .\test2_leak.txt -s" -Exp "LEAK"
CFL -Prog "python ..\analysis.py -i .\test3_leak.txt -s" -Exp "LEAK"
CFL -Prog "python ..\analysis.py -i .\test4_noLeak.txt -s" -Exp "NO LEAK"
CFL -Prog "python ..\analysis.py -i .\testAll_leak.txt -s" -Exp "LEAK"

Write-Host "DONE"
