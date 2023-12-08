define i32 @main(i32 %0, i8** %1) {
        %res = call i32 @SOURCE ()
        call i32 @SINK (i32 %res)
        ret i32 0
}
declare dso_local i32 @SOURCE()
declare dso_local i32 @SINK(i32)