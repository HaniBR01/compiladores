import sys
import enum


class Token:
    """
    This class contains the definition of Tokens. A token has two fields: its
    text and its kind. The "kind" of a token is a constant that identifies it
    uniquely. See the TokenType to know the possible identifiers (if you want).
    You don't need to change this class.
    """
    def __init__(self, tokenText, tokenKind):
        # The token's actual text. Used for identifiers, strings, and numbers.
        self.text = tokenText
        # The TokenType that this token is classified as.
        self.kind = tokenKind


class TokenType(enum.Enum):
    """
    These are the possible tokens. You don't need to change this class at all.
    """

    EOF = -1  # End of file
    NLN = 0   # New line
    WSP = 1   # White Space
    COM = 2   # Comment
    NUM = 3   # Number (integers)
    STR = 4   # Strings
    TRU = 5   # The constant true
    FLS = 6   # The constant false
    VAR = 7   # An identifier
    LET = 8   # The 'let' of the let expression
    INX = 9   # The 'in' of the let expression
    END = 10  # The 'end' of the let expression
    EQL = 201 # x = y
    ADD = 202 # x + y
    SUB = 203 # x - y
    MUL = 204 # x * y
    DIV = 205 # x / y
    LEQ = 206 # x <= y
    LTH = 207 # x < y
    NEG = 208 # ~x
    NOT = 209 # not x
    LPR = 210 # (
    RPR = 211 # )
    ASN = 212 # The assignment '<-' operator
    ORX = 213 # x or y
    AND = 214 # x and y
    IFX = 215 # The 'if' of a conditional expression
    THN = 216 # The 'then' of a conditional expression
    ELS = 217 # The 'else' of a conditional expression
    FNX = 218 # The 'fn' that declares an anonymous function
    ARW = 219 # The '=>' that separates the parameter from the body of function



class Lexer:
    
    def __init__(self, source):
        """
        The constructor of the lexer. It receives the string that shall be
        scanned.
        TODO: You will need to implement this method.
        """

        self.source = source + '\n'
        self.curPos = -1
        self.curChar = ''
        self.nextChar()

    def nextChar(self):
        """
        Advance the 'curPos' pointer and set the 'curChar' variable.
        """
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0'  # End of file character
        else:
            self.curChar = self.source[self.curPos]

    def peek(self):
        """
        Return the next character without advancing the pointer.
        """
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos + 1]

    def _skip_whitespace(self):
        """
        Skip whitespace characters.
        """
        while self.curChar.isspace() and self.curChar != '\n':
            self.nextChar()

    def _skip_comment(self):
        """
        Skip single-line and multi-line comments.
        """
        if self.curChar == '-' and self.peek() == '-':
            while self.curChar != '\n':
                self.nextChar()
            return Token('', TokenType.COM)
        elif self.curChar == '(' and self.peek() == '*':
            startPos = self.curPos
            self.nextChar()  # consume (
            self.nextChar()  # consume *
            while not (self.curChar == '*' and self.peek() == ')'):
                if self.curChar == '\0':
                    raise Exception("Unterminated multi-line comment.")
                self.nextChar()
            self.nextChar()  # consume *
            self.nextChar()  # consume )
            return Token(self.source[startPos:self.curPos+1], TokenType.COM)
        return None


    def _process_number(self):
        """
        Process numeric literals (NUM, BIN, OCT, HEX).
        """
        startPos = self.curPos
        if self.curChar == '0':
            if self.peek() in 'bB':
                self.nextChar()
                self.nextChar()
                startPos = self.curPos
                while self.curChar in '01':
                    self.nextChar()
                return Token(self.source[startPos:self.curPos], TokenType.BIN)
            elif self.peek() in 'xX':
                self.nextChar()
                self.nextChar()
                startPos = self.curPos
                while self.curChar.isdigit() or self.curChar.lower() in 'abcdef':
                    self.nextChar()
                return Token(self.source[startPos:self.curPos], TokenType.HEX)
            elif self.peek() in '01234567':
                self.nextChar()
                startPos = self.curPos
                while self.curChar in '01234567':
                    self.nextChar()
                return Token(self.source[startPos:self.curPos], TokenType.OCT)
            else: # Just a 0
                self.nextChar()
                return Token('0', TokenType.NUM)
        elif self.curChar.isdigit():
            startPos = self.curPos
            while self.curChar.isdigit():
                self.nextChar()
            return Token(self.source[startPos:self.curPos], TokenType.NUM)
        return None

    def _process_keyword_or_identifier(self):
        """
        Process keywords.
        """
        startPos = self.curPos
        if self.curChar.isalpha():
            while self.curChar.isalnum():
                self.nextChar()
            
            tokenText = self.source[startPos:self.curPos]
            if tokenText == 'true':
                return Token(tokenText, TokenType.TRU)
            elif tokenText == 'false':
                return Token(tokenText, TokenType.FLS)
            elif tokenText == 'not':
                return Token(tokenText, TokenType.NOT)
            elif tokenText == 'let':
                return Token(tokenText, TokenType.LET)
            elif tokenText == 'in':
                return Token(tokenText, TokenType.INX)
            elif tokenText == 'end':
                return Token(tokenText, TokenType.END)
            elif tokenText == 'if':
                return Token(tokenText, TokenType.IFX)
            elif tokenText == 'then':
                return Token(tokenText, TokenType.THN)
            elif tokenText == 'else':
                return Token(tokenText, TokenType.ELS)
            elif tokenText == 'and':
                return Token(tokenText, TokenType.AND)
            elif tokenText == 'or':
                return Token(tokenText, TokenType.ORX)
            elif tokenText == 'fn':
                return Token(tokenText, TokenType.FNX)
            else:
                return Token(tokenText, TokenType.VAR)
        return None

    def __iter__(self):
        return self

    def __next__(self):
        token = self.getToken()
        if token.kind == TokenType.EOF:
            raise StopIteration
        return token


    def tokens(self):
        """
        This method is a token generator: it converts the string encapsulated
        into this object into a sequence of Tokens. Examples:

        >>> l = Lexer("1 + 3")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.NUM: 3>]

        >>> l = Lexer('1 * 2 -- 3\\n')
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.MUL: 204>, <TokenType.NUM: 3>]

        >>> l = Lexer("1 + var")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.VAR: 7>]

        >>> l = Lexer("let v <- 2 in v end")
        >>> [tk.kind.name for tk in l.tokens()]
        ['LET', 'VAR', 'ASN', 'NUM', 'INX', 'VAR', 'END']
        """
        token = self.getToken()
        while token.kind != TokenType.EOF:
            if (
                token.kind != TokenType.WSP
                and token.kind != TokenType.COM
                and token.kind != TokenType.NLN
            ):
                yield token
            token = self.getToken()

    def getToken(self):
        """
        Return the next token.
        """

        self._skip_whitespace()
        
        token = self._skip_comment()
        if token:
            return token

        if self.curChar == '\0':
            token = Token('', TokenType.EOF)
        elif self.curChar == '\n':
            token = Token('\n', TokenType.NLN)
            self.nextChar()
        elif self.curChar == '=':
            token = Token('=', TokenType.EQL)
            if self.peek() == '>':
                self.nextChar()
                token = Token('=>', TokenType.ARW)
            self.nextChar()
        elif self.curChar == '+':
            token = Token('+', TokenType.ADD)
            self.nextChar()
        elif self.curChar == '-':
            token = Token('-', TokenType.SUB)
            self.nextChar()
        elif self.curChar == '*':
            token = Token('*', TokenType.MUL)
            self.nextChar()
        elif self.curChar == '/':
            token = Token('/', TokenType.DIV)
            self.nextChar()
        elif self.curChar == '<':
            if self.peek() == '=':
                self.nextChar()
                token = Token('<=', TokenType.LEQ)
            elif self.peek() == '-':
                self.nextChar()
                token = Token('<-', TokenType.ASN)
            else:
                token = Token('<', TokenType.LTH)
            self.nextChar()
        elif self.curChar == '~':
            token = Token('~', TokenType.NEG)
            self.nextChar()
        elif self.curChar == '(':
            token = Token('(', TokenType.LPR)
            self.nextChar()
        elif self.curChar == ')':
            token = Token(')', TokenType.RPR)
            self.nextChar()
        elif self.curChar.isdigit():
            token = self._process_number()
        elif self.curChar.isalpha():
            token = self._process_keyword_or_identifier()
        else:
            raise Exception(f'Invalid character: {self.curChar} at position {self.curPos}')
        
        return token