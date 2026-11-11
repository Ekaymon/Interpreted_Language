# Interpreter Script #
import sys 

variables = {}
functions = {} # initialise dictionaries that store variables and functions created in the interpreted script

def if_handler(fields): # handle if statements
    if fields[2] == "mvars": # mvars flag allows multiple variables to be used, so set both x and y to the values of the 2 passed variables
        x = float(variables[fields[4]])
        y = float(variables[fields[5]])
    else: # no flag means only 1 variable is being used, so set x to its value and y to the passed number
        x = float(variables[fields[4]])
        y = float(fields[5])

    if fields[3] == "=":
        if x == y:
            call_function(fields[6])
    elif fields[3] == "!=":
        if x != y:
            call_function(fields[6])
    elif fields[3] == ">":
        if x > y:
            call_function(fields[6])
    elif fields[3] == "<":
        if x < y:
            call_function(fields[6])
    elif fields[3] == ">=":
        if x >= y:
            call_function(fields[6])
    elif fields[3] == "<=":
        if x <= y:
            call_function(fields[6])

    # do the requested comparison and if true, call requested function

def standard_library(fields): # define the standard library
    if fields[1] == "out": # define out command
        if fields[2] == "var": # if var flag used, output the value of the variable with the passed name
            print(variables[fields[3]])

        else: # if var flag not used, output the passed string
            print(fields[2])

    elif fields[1] == "in": # define in command
        name = fields[3] # set new variable's name to the passed value
        contents = input(fields[2]) # prompt user for the contents of the variable

        variables.update({name: contents}) # add the new variable to the variable dictionary

    elif fields[1] == "var": # define var command
        variables.update({fields[2]: fields[3]}) # create variable using passed name and value

    elif fields[1] == "if": # define if command
        if_handler(fields) # pass over to if statement handler 

    elif fields[1] == "for": # define for command
        for i in range(int(fields[2])):
            call_function(fields[3])

    elif fields[1] == "exit": # define exit command
        quit() # stop execution of program
    
def maths_library(fields): # define the maths library
    if fields[1] == "vars": # vars flag means 2 variables are being processed so set x and y to the values of the passed variables, if it fails the variables either aren't numbers or don't exist
        try: 
            x = float(variables[fields[3]])
            y = float(variables[fields[4]])
        except:
            print("Error: variable input in equation not number or variables not created.")
    else: # no flag means 2 numbers are being processed so set x and y to the values passed, if it fails the values aren't numbers
        try:
            x = float(fields[3])
            y = float(fields[4])
        except:
            print("Error: input in equation not number.")

    try:
        if fields[2] == "+":
            answer = x + y

        elif fields[2] == "-":
            answer = x - y

        elif fields[2] == "*":
            answer = x * y

        elif fields[2] == "/":
            answer = x / y

        elif fields[2] == "^":
            answer = x ** y
    except:
        pass

    # do requested operation and store result
    
    try: # assign answer to variable passed either by creating it or updating an old one, discard result if no variable passed
        if fields[5] != "":
            variables.update({fields[5]: answer})
    except:
        pass

def define_function(fields): # create a function
    name = fields[2] # name the function the passed name

    for i in range(3): # remove the first 3 parts of the command because they are the function definition part, removing leaves only the actual command
        fields.pop(0)

    function_contents = ""
    for i in range(len(fields)): # set the function command to the remaining part of the command, combined into 1 string with colon delimeters added back
        function_contents += fields[i]
        function_contents += ":"

    functions.update({name: function_contents}) # add function name and command to functions dictionary

def call_function(name): # call the requested user-created function
    function_parser(functions[name])

def function_library(fields): # define the function library
    if fields[1] == "def": # def keyword creates a function
        define_function(fields)
    elif fields[1] == "call": # call keyword calls an existing function
        call_function(fields[2])

def function_parser(functions_list): # parse functions separately cause they're weird (it could go in the regular parser probably, but this is easier to change trust)
    commands = functions_list.strip().split("&") # split the string of everything a function does into its distinct commands
    for i in range(len(commands)): # actually do each command
        fields = commands[i].strip().split(":") # this is the same as the regular parser, split each command into individual fields
        if fields[0] == "":
            fields.pop(0) # remove the first field cause it'll be blank and break stuff
        if fields[0] == "s": # back to regular parser again
            standard_library(fields)
        elif fields[0] == "m":
            maths_library(fields)
        elif fields[0] == "f":
            function_library(fields)

def parse(line): # parse each line in the script individually
    fields = line.strip().split(":") # split the command up using the colon delimeter
    
    if fields[0] == "s":
        standard_library(fields)
    elif fields[0] == "m":
        maths_library(fields)
    elif fields[0] == "f":
        function_library(fields)

    # chose library based on library flag

def main(): # load file
    try: # if passed a script file from the command line attempt to open that. If not, or if that fails, ask the user for a script file
        file = open(sys.argv[1], "r")
    except:
        file = open(input("Enter path to script file: "), "r")

    for line in file: # parse each line in file
        parse(line)

if __name__ == "__main__":
    main()
