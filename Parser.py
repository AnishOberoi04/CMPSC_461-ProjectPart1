import ASTNodeDefs as AST  

class Lexer:
    def __init__(self, code):
        self.code = code  
        self.position = 0  
        self.current_char = self.code[self.position]  
        self.tokens = []  

    # Move to the next position in the code
    def advance(self):
        self.position += 1  # Move to the next position
        if self.position < len(self.code):  # If still within the code length
            self.current_char = self.code[self.position]  # Update the current character
        else:
            self.current_char = None  # End of input, set current_char to None

    # Skip whitespaces.
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():  # Loop while current character is whitespace
            self.advance()  # Move to the next character

    # Tokenize an identifier.
    def identifier(self):
        result = ''  
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char  # Append character to identifier
            self.advance()  # Move to the next character
        return ('IDENTIFIER', result)  

    # Tokenize a number.
    def number(self):
        result = '' 
        while self.current_char is not None and self.current_char.isdigit():  # Loop through digits
            result += self.current_char  # Append digit to result
            self.advance()  # Move to the next character
        return ('NUMBER', int(result))  

    # Get the next token from the code
    def token(self):
        while self.current_char is not None:  
            if self.current_char.isspace():
                self.skip_whitespace()  
                continue
            if self.current_char.isalpha(): 
                ident = self.identifier()  
                if ident[1] == 'if':
                    return ('IF', 'if')  
                elif ident[1] == 'else':
                    return ('ELSE', 'else')  
                elif ident[1] == 'while':
                    return ('WHILE', 'while')  
                return ident  
            if self.current_char.isdigit():
                return self.number()  
            if self.current_char == '+':
                self.advance()  
                return ('PLUS', '+') 
            if self.current_char == '-':
                self.advance()  
                return ('MINUS', '-')  
            if self.current_char == '*':
                self.advance()  
                return ('MULTIPLY', '*')  
            if self.current_char == '/':
                self.advance()  
                return ('DIVIDE', '/')  
            if self.current_char == '=':
                self.advance()  
                if self.current_char == '=':
                    self.advance()  
                    return ('EQ', '==')  
                return ('EQUALS', '=')  
            if self.current_char == '!':
                self.advance()  
                if self.current_char == '=':
                    self.advance() 
                    return ('NEQ', '!=')  
            if self.current_char == '<':
                self.advance()  
                return ('LESS', '<')  
            if self.current_char == '>':
                self.advance()  
                return ('GREATER', '>')  
            if self.current_char == '(':
                self.advance()  
                return ('LPAREN', '(')  
            if self.current_char == ')':
                self.advance()  
                return ('RPAREN', ')')  
            if self.current_char == ':':
                self.advance()  
                return ('COLON', ':')  
            if self.current_char == ',':
                self.advance()  
                return ('COMMA', ',')  
            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)  

    # Collect all tokens into a list.
    def tokenize(self):
        while self.current_char is not None:  # Loop until end of input
            self.tokens.append(self.token())  # Add each token to the list
        return self.tokens  

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self.current_token = tokens.pop(0)  # Start with the first token

    # Advance to the next token in the list
    def advance(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)  # Update to the next token
        else:
            self.current_token = ('EOF', None)  # No more tokens, set to EOF

    def expect(self, token_type):
        if self.current_token[0] == token_type:  
            self.advance()  # Move to next token
        else:
            raise ValueError(f"Expected {token_type} but got {self.current_token[0]}")

    # Peek at the next token type without advancing
    def peek(self):
        if self.tokens:
            return self.tokens[0][0]  
        else:
            return None 

    def parse(self):
        return self.program()  
    
    def program(self):
        statements = []  
        while self.current_token[0] != 'EOF':  
            statements.append(self.statement())  # Parse each statement
        return statements  

    def statement(self):
        """
        Determines which type of statement to parse.
        - If it's an identifier, it could be an assignment or function call.
        - If it's 'if', it parses an if-statement.
        - If it's 'while', it parses a while-statement.
        
        TODO: Dispatch to the correct parsing function based on the current token.
        """
        if self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS': # Assignment
                return self.assign_stmt()  #AST of assign_stmt
            elif self.peek() == 'LPAREN': # Function call
                return self.function_call()  #AST of  function call
        elif self.current_token[0] == 'IF':
            return self.if_stmt() #AST of if stmt
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt()  #AST of while stmt
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")

    def assign_stmt(self):
        identifier = ('IDENTIFIER', self.current_token[1])  # Capture identifier
        self.expect('IDENTIFIER')  # Expect IDENTIFIER
        self.expect('EQUALS')  # Expect EQUALS sign
        expression = self.expression()  # Parse expression on the right side
        return AST.Assignment(identifier, expression)  


    def if_stmt(self):
        self.expect('IF')  # Expect IF keyword
        condition = self.boolean_expression()  # Parse boolean expression for condition
        self.expect('COLON')  # Expect COLON after condition
        block = self.block()  # Parse the block of statements
        else_block = None
        if self.current_token[0] == 'ELSE':  # Check for ELSE block
            self.expect('ELSE')
            self.expect('COLON')
            else_block = self.block()  # Parse else block
        return AST.IfStatement(condition, block, else_block)  

    def while_stmt(self):
        self.expect('WHILE')  # Expect WHILE keyword
        condition = self.boolean_expression()  # Parse boolean condition
        self.expect('COLON')  # Expect COLON after condition
        block_statements = self.block()  # Parse block within the while loop
        return AST.WhileStatement(condition, block_statements)  

    def block(self):
        statements = []  
        while self.current_token[0] not in ['EOF', 'ELSE', 'WHILE', 'IF']:  # Stop at control tokens
            statements.append(self.statement())  # Parse each statement in the block
        return AST.Block(statements)  

    def expression(self):
        left = self.term()  # Parse the left term
        while self.current_token[0] in ['PLUS', 'MINUS']:  # Handle + and -
            op = (self.current_token[0], self.current_token[1])  # Capture operator
            self.advance() # Skip the operator
            right = self.term()  # Parse right term
            left = AST.BinaryOperation(left, op, right)  
        return left

    def boolean_expression(self):
        left = self.term()  # Parse the left term
        while self.current_token[0] in ['EQ', 'NEQ', 'LESS', 'GREATER']:  # Loop for comparison operators
            op = (self.current_token[0], self.current_token[1])  # Capture operator
            self.advance()
            right = self.term()  # Parse right term
            left = AST.BooleanExpression(left, op, right)  # Create BooleanExpression AST node
        return left

    def term(self):
        left = self.factor()  # Parse left factor
        while self.current_token[0] in ['MULTIPLY', 'DIVIDE']:  # Loop for * and / operators
            op = (self.current_token[0], self.current_token[1])  # Capture operator
            self.advance()
            right = self.factor()  # Parse right factor
            left = AST.BinaryOperation(left, op, right)  # Create BinaryOperation AST node
        return left

    def factor(self):
        if self.current_token[0] == 'NUMBER':
            number = self.current_token[1]  # Capture number value
            self.expect('NUMBER')
            return ('NUMBER', number)  # Return as NUMBER token
        elif self.current_token[0] == 'IDENTIFIER':
            identifier = self.current_token[1]  # Capture identifier name
            self.expect('IDENTIFIER')
            return ('IDENTIFIER', identifier)  # Return as IDENTIFIER token
        elif self.current_token[0] == 'LPAREN':
            self.expect('LPAREN')
            expr = self.expression()  # Parse expression within parentheses
            self.expect('RPAREN')
            return expr
        else:
            raise ValueError(f"Unexpected token in factor: {self.current_token}")

    def function_call(self):
        func_name = ('IDENTIFIER', self.current_token[1])  # Capture function name
        self.expect('IDENTIFIER')
        self.expect('LPAREN')  # Expect opening parenthesis
        args = self.arg_list()  # Parse arguments
        self.expect('RPAREN')  # Expect closing parenthesis
        return AST.FunctionCall(func_name, args)  

    def arg_list(self):
        args = []  
        if self.current_token[0] != 'RPAREN':  # Check if argument list is not empty
            args.append(self.expression())  # Parse the first argument
            while self.current_token[0] == 'COMMA':  # Loop for additional arguments
                self.expect('COMMA')
                args.append(self.expression())  # Parse next argument
        return args  
