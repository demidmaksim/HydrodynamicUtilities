formula = (
        "=("
        "    VLOOKUP("
        "         INDEX("
        "                $1:$1048576,"
        "                ROW()+1,"
        "                4"
        "               ),"
        "         Data!$1:$1048576,"
        "         1+SUMIFS("
        "                Data!$1:$1,"
        "                Data!$2:$2,"
        "                $B$3,"
        "                Data!$3:$3,"
        "                INDEX($1:$1,COLUMN()),"
        "                Data!$4:$4,"
        "                VLOOKUP("
        "                    $B$4,"
        "                    TL!$1:$1048576,"
        "                    2,"
        "                    False"
        "                   )"
        "               ),"
        "         False"
        "       )"
        "    -VLOOKUP("
        "         INDEX("
        "                $1:$1048576,"
        "                ROW(),"
        "                4"
        "               ),"
        "         Data!$1:$1048576,"
        "         1+SUMIFS("
        "                Data!$1:$1,"
        "                Data!$2:$2,"
        "                $B$3,"
        "                Data!$3:$3,"
        "                INDEX($1:$1,COLUMN()),"
        "                Data!$4:$4,"
        "                VLOOKUP("
        "                    $B$4,"
        "                    TL!$1:$1048576,"
        "                    2,"
        "                    False"
        "                   )"
        "               ),"
        "         False"
        "       )"
        "    *IF("
        "         VLOOKUP("
        "             $B$4,"
        "             TL!$1:$1048576,"
        "             3,"
        "             False"
        '             )="Тотал",'
        "         0,"
        "         1"
        "        )"
        ")"
        "/IF("
        '       $B$5="млрд.",'
        "       10^9,"
        "       IF("
        '           $B$5="млн.",'
        "           10^6,"
        "           IF("
        '               $B$5="тыс.",'
        "               10^3,"
        "               1"
        "              )"
        "         )"
        ")"
        "/IF("
        "       VLOOKUP("
        "              $B$4,"
        "              TL!$1:$1048576,"
        "              3,"
        "              False"
        '          )="Расход",'
        "          INDEX("
        "                $1:$1048576,"
        "                ROW()+1,"
        "                4"
        "               )"
        "          -INDEX("
        "                $1:$1048576,"
        "                ROW(),"
        "                4"
        "               ),"
        "       1"
        ")"
    ).replace(" ", "")
