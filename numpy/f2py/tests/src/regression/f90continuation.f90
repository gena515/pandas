SUBROUTINE TESTSUB(INPUT1, & ! Hello
! commenty
INPUT2, OUTPUT1, OUTPUT2) ! more comments
    INTEGER, INTENT(IN) :: INPUT1, INPUT2
    INTEGER, INTENT(OUT) :: OUTPUT1, OUTPUT2
    OUTPUT1 = INPUT1 + &
              INPUT2
    OUTPUT2 = INPUT1 * INPUT2
END SUBROUTINE TESTSUB
