f:def:correct:s:out:Correct! My number was 2!:&:s:exit
s:var:number:2
s:in:I have picked a number! It is either 1 or 2. Enter your guess for the number! :guess
s:if:mvars:=:guess:number:correct
s:in:Incorrect! Try guessing again! :guess
s:if:mvars:=:guess:number:correct