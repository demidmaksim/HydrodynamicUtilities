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
        "                    TechnicalList!$1:$1048576,"
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
        "                    TechnicalList!$1:$1048576,"
        "                    2,"
        "                    False"
        "                   )"
        "               ),"
        "         False"
        "       )"
        "    *IF("
        "         VLOOKUP("
        "             $B$4,"
        "             TechnicalList!$1:$1048576,"
        "             3,"
        "             False"
        '             )="Тотал",'
        "         0,"
        "         1"
        "        )"
        ")"
        "/VLOOKUP("
        "       $B$5,"
        "       TechnicalList!$K:$L,"
        "       2,"
        "       False"
        ")"
        "/IF("
        "       VLOOKUP("
        "              $B$4,"
        "              TechnicalList!$1:$1048576,"
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

delta = (
        '=ВПР('
        '       ИНДЕКС($A:$A;СТРОКА()+1);'
        '       $1:$1048576;'
        '       СУММЕСЛИМН('
        '               $1:$1;'
        '               $2:$2;'
        '               ИНДЕКС($2:$2;СТОЛБЕЦ());'
        '               $3:$3;'
        '               ИНДЕКС($3:$3;СТОЛБЕЦ());'
        '               $4:$4;{param1}'
        '       );'
        '       FALSE'
        ')'
        '-ВПР('
        '       ИНДЕКС($A:$A;СТРОКА());'
        '       $1:$1048576;'
        '       СУММЕСЛИМН('
        '               $1:$1;'
        '               $2:$2;'
        '               ИНДЕКС($2:$2;СТОЛБЕЦ());'
        '               $3:$3;'
        '               ИНДЕКС($3:$3;СТОЛБЕЦ());'
        '               $4:$4;{param2}'
        '       );'
        '       FALSE'
        ')'
        '-'
).replace(" ", "")


der = (
        '=ВПР('
        '       ИНДЕКС($A:$A;СТРОКА()+1);'
        '       $1:$1048576;'
        '       СУММЕСЛИМН('
        '               $1:$1;'
        '               $2:$2;'
        '               ИНДЕКС($2:$2;СТОЛБЕЦ());'
        '               $3:$3;'
        '               ИНДЕКС($3:$3;СТОЛБЕЦ());'
        '               $4:$4;{param}'
        '       );'
        '       FALSE'
        ')'
        '/('
        'ИНДЕКС($A:$A;СТРОКА()+1)'
        '-ИНДЕКС($A:$A;СТРОКА())'
        ')'
).replace(" ", "")



relatively = (
        '=ВПР('
        '       ИНДЕКС($A:$A;СТРОКА()+1);'
        '       $1:$1048576;'
        '       СУММЕСЛИМН('
        '               $1:$1;'
        '               $2:$2;'
        '               ИНДЕКС($2:$2;СТОЛБЕЦ());'
        '               $3:$3;'
        '               ИНДЕКС($3:$3;СТОЛБЕЦ());'
        '               $4:$4;{param}'
        '       )'
        ')'
        '/ВПР('
        '       ИНДЕКС($A:$A;СТРОКА());'
        '       $1:$1048576;'
        '       СУММЕСЛИМН('
        '               $1:$1;'
        '               $2:$2;'
        '               ИНДЕКС($2:$2;СТОЛБЕЦ());'
        '               $3:$3;'
        '               ИНДЕКС($3:$3;СТОЛБЕЦ());'
        '               $4:$4;{param}'
        '       )'
        ')'
        '-'
).replace(" ", "")
