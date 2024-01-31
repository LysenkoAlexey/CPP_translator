program translated;
   var x: integer;
   var y: integer;
   var u: char;
   var k: string;
   var c: real;
   procedure second_function(a : integer; b : real);
      var x: integer;
      begin
         x := 3;      writeln(x, a, 'aaa');
      end; {END OF second_function}
begin
   y := 0;
   u := 'a';
   k := 'aaaa';
   c := 11.5;
   readln(x);
   while (x < 5) do
   begin
      x := x + 2;
   end;
   if ((x = 6) and ((y < 10) or (c > 10))) then
   begin
      y := y + 1;
   end
   else  
   begin
      c := c + 11;
   end;
   writeln(x, y, c);
end. {END OF translated}