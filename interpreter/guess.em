f:def:correct1:s:out:Correct! My number was 2!
f:def:correct2:s:exit
s:var:number:2
s:in:I have picked a number! It is either 1 or 2. Enter your guess for the number! :guess
s:if:mvars:=:guess:number:correct1
s:if:mvars:=:guess:number:correct2
s:in:Incorrect! Try guessing again! :guess
s:if:mvars:=:guess:number:correct1
s:if:mvars:=:guess:number:correct2