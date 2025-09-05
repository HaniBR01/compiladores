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
    STR = 3   # Strings
    TRU = 4   # The constant true
    FLS = 5   # The constant false
    NUM = 6   # Number (integers)
    BIN = 7   # Number (binary)
    OCT = 8   # Number (octal)
    HEX = 9   # Number (hexadecimal)
    EQL = 201
    ADD = 202
    SUB = 203
    MUL = 204
    DIV = 205
    LEQ = 206
    LTH = 207
    NEG = 208
    NOT = 209
    LPR = 210
    RPR = 211


class Lexer:
    
    def __init__(self, source):
        """
        The constructor of the lexer. It receives the string that shall be
        scanned.
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

        >>> l = Lexer("10")
        >>> [tk.kind.name for tk in l.tokens()]
        ['NUM']

        >>> l = Lexer("01")
        >>> [tk.kind.name for tk in l.tokens()]
        ['OCT']

        >>> l = Lexer("0b1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['BIN']

        >>> l = Lexer("0B1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['BIN']

        >>> l = Lexer("0x1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['HEX']

        >>> l = Lexer("0X1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['HEX']

        >>> l = Lexer("0X1 + 0xA + 0XABCDEF + 0xA0B1C2D3E4F5")
        >>> [tk.kind.name for tk in l.tokens()]
        ['HEX', 'ADD', 'HEX', 'ADD', 'HEX', 'ADD', 'HEX']

        >>> l = Lexer("0b1 + 0xA + 0B01010101 + 0xA0B1C2D3E4F5")
        >>> [tk.kind.name for tk in l.tokens()]
        ['BIN', 'ADD', 'HEX', 'ADD', 'BIN', 'ADD', 'HEX']

        >>> l = Lexer('1 * 2 - 3')
        >>> [tk.kind.name for tk in l.tokens()]
        ['NUM', 'MUL', 'NUM', 'SUB', 'NUM']

        >>> l = Lexer('1 * 2 - 3 -- alkdjf adkjf dlkjf \\n')
        >>> [tk.kind.name for tk in l.tokens()]
        ['NUM', 'MUL', 'NUM', 'SUB', 'NUM', 'COM']

        >>> l = Lexer('1 * 2 - 3 -- alkdjf adkjf dlkjf \\n0x23 + 012')
        >>> [tk.kind.name for tk in l.tokens()]
        ['NUM', 'MUL', 'NUM', 'SUB', 'NUM', 'COM', 'HEX', 'ADD', 'OCT']
        """
        token = self.getToken()
        while token.kind != TokenType.EOF:
            if token.kind not in [TokenType.WSP, TokenType.NLN]:
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