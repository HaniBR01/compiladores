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
    INT = 6   # Number (integers)
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
        TODO: You will need to implement this method.
        """

        self.source = source
        self.curPos = 0
        self.curChar = ''
        self.tokens()

    def tokens(self):
        """
        This method is a token generator: it converts the string encapsulated
        into this object into a sequence of Tokens. Examples:

        >>> l = Lexer("10")
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT']

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
        ['INT', 'MUL', 'INT', 'SUB', 'INT']

        >>> l = Lexer('1 * 2 - 3 -- alkdjf adkjf dlkjf \\n')
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT', 'MUL', 'INT', 'SUB', 'INT', 'COM']

        >>> l = Lexer('1 * 2 - 3 -- alkdjf adkjf dlkjf \\n0x23 + 012')
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT', 'MUL', 'INT', 'SUB', 'INT', 'COM', 'HEX', 'ADD', 'OCT']

        >>> l = Lexer('1 + 21 -- 3 / 4 \\n~3 + 2 <= 2 -- * 4')
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT', 'ADD', 'INT', 'COM', 'NEG', 'INT', 'ADD', 'INT', 'LEQ', 'INT', 'COM']

        """
        token = self.getToken()
        while token.kind != TokenType.EOF:
            if token.kind != TokenType.WSP and token.kind != TokenType.NLN:
                yield token
            token = self.getToken()

    def getToken(self):
        """
        Return the next token.
        TODO: Implement this method!
        """

        # 1. EOF
        if self.curPos >= len(self.source):
            token = Token('', TokenType.EOF)
            self.curPos += 1
        
        # 2. WSP or 3. NLN
        elif self.source[self.curPos].isspace():
            if self.source[self.curPos] == '\n':
                token = Token('\n', TokenType.NLN)
                self.curPos += 1
            else:
                token = Token(self.source[self.curPos], TokenType.WSP)
                self.curPos += 1
        
        # 4. COM or 7. SUB
        elif self.source[self.curPos] == '-':
            if self.curPos + 1 < len(self.source) and self.source[self.curPos + 1] == '-':
                while self.curPos < len(self.source) and self.source[self.curPos] != '\n':
                    self.curPos += 1
                token = Token('', TokenType.COM)
            else:
                token = Token('-', TokenType.SUB)
                self.curPos += 1
        
        # 5. EQL
        elif self.source[self.curPos] == '=':
            token = Token('=', TokenType.EQL)
            self.curPos += 1
        
        # 6. ADD
        elif self.source[self.curPos] == '+':
            token = Token('+', TokenType.ADD)
            self.curPos += 1
        
        # 8. MUL
        elif self.source[self.curPos] == '*':
            token = Token('*', TokenType.MUL)
            self.curPos += 1
        
        # 9. DIV
        elif self.source[self.curPos] == '/':
            token = Token('/', TokenType.DIV)
            self.curPos += 1
        
        # 10. LEQ or 11. LTH
        elif self.source[self.curPos] == '<':
            if self.curPos + 1 < len(self.source) and self.source[self.curPos + 1] == '=':
                token = Token('<=', TokenType.LEQ)
                self.curPos += 2
            else:
                token = Token('<', TokenType.LTH)
                self.curPos += 1
        
        # 12. NEG
        elif self.source[self.curPos] == '~':
            token = Token('~', TokenType.NEG)
            self.curPos += 1
        
        # 13. NOT
        elif self.source[self.curPos:self.curPos+3] == 'not':
            token = Token('not', TokenType.NOT)
            self.curPos += 3
        
        # 14. LPR or 4. COM
        elif self.source[self.curPos] == '(':
            if self.source[self.curPos + 1] == '*':
                pos = self.curPos + 2
                while self.source[pos:pos+2] != '*)' and pos < len(self.source):
                    pos += 1
                pos += 2
                token = Token(self.source[self.curPos:pos], TokenType.COM)
                self.curPos = pos
            else:
                token = Token('(', TokenType.LPR)
                self.curPos += 1

        # 15. RPR
        elif self.source[self.curPos] == ')':
            token = Token(')', TokenType.RPR)
            self.curPos += 1

        # 16. TRU
        elif self.source[self.curPos:self.curPos+4] == 'true':
            token = Token('true', TokenType.TRU)
            self.curPos += 4
        
        # 17. FLS
        elif self.source[self.curPos:self.curPos+5] == 'false':
            token = Token('false', TokenType.FLS)
            self.curPos += 5

        # 18 INT, 19. BIN, 20. OCT, or 21. HEX
        elif self.source[self.curPos] == '0':
            if self.curPos + 1 >= len(self.source) or self.source[self.curPos + 1].isspace():
                token = Token('0', TokenType.INT)
                self.curPos += 1
            elif self.source[self.curPos + 1] in 'bB':
                pos = self.curPos + 2
                while pos < len(self.source) and self.source[pos] in '01':
                    pos += 1
                token = Token(self.source[self.curPos:pos], TokenType.BIN)
                self.curPos = pos
            elif self.source[self.curPos + 1] in 'xX':
                pos = self.curPos + 2
                while pos < len(self.source) and (self.source[pos].isdigit() or self.source[pos].lower() in 'abcdef'):
                    pos += 1
                token = Token(self.source[self.curPos:pos], TokenType.HEX)
                self.curPos = pos
            elif self.source[self.curPos + 1] in '01234567':
                pos = self.curPos + 2
                while pos < len(self.source) and self.source[pos] in '01234567':
                    pos += 1
                token = Token(self.source[self.curPos:pos], TokenType.OCT)
                self.curPos = pos

        elif self.source[self.curPos] in '123456789':
            pos = self.curPos + 1
            while pos < len(self.source) and self.source[pos] in '0123456789':
                pos += 1
            token = Token(self.source[self.curPos:pos], TokenType.INT)
            self.curPos = pos

        else:
            raise Exception(f'Invalid character: {self.source[self.curPos]} at position {self.curPos}')
             
        return token