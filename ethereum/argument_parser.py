# ============================================================================
# Call agument parser

def convert_to_int( text ):
    if text.startswith("0x"):
        return int(text, 16)
    else:
        return int(text)

def parse_args( text ):
    cur_pos = 0

    def peek_char():
        nonlocal cur_pos
        if cur_pos >= len(text):
            return None
        return text[cur_pos]

    def get_char():
        nonlocal cur_pos
        ch = peek_char()
        if ch is not None:
            cur_pos += 1
        return ch

    def skip_whitespace():
        nonlocal cur_pos
        while ch := peek_char():
            if not ch.isspace():
                break
            cur_pos += 1

    def parse_string_as_number():
        nonlocal cur_pos
        start = cur_pos
        assert get_char() == "\""
        while ch := get_char():
            if ch == "\"":
                return convert_to_int(text[start+1:cur_pos-1])
        raise ValueError(f"Unterminated string at position {start}")

    cur_token = None
    next_token = None

    def get_next_token():
        skip_whitespace()
        ch = peek_char()
        if ch is None:
            return get_char()
        elif ch in "[],":
            return get_char()
        elif ch == "\"":
            return parse_string_as_number()
        else:
            raise ValueError(f"Unexpected character: `{ch}` at position {cur_pos}")

    def peek_token():
        nonlocal cur_token, next_token
        if next_token is None:
            next_token = get_next_token()
        return next_token

    def get_token():
        nonlocal cur_token, next_token
        if next_token is not None:
            cur_token = next_token
            next_token = None
        else:
            cur_token = get_next_token()
        return cur_token

    def parse_expr( optional=False ):
        t = peek_token()
        if t is None:
            return None
        elif isinstance(t, int):
            return get_token()
        elif t == "[":  # list
            get_token()
            expr_list = parse_expr_list()
            if get_token() != "]":
                raise ValueError(f"Expected `]` at position {cur_pos}")
            return expr_list
        else:
            if optional:
                return None
            raise ValueError(f"Unexpected token: {t}")

    def parse_expr_list():
        expr_list = []
        while True:
            expr = parse_expr( optional=True )
            if expr is None:
                break
            expr_list.append(expr)
            if peek_token() == ",":
                get_token()
            else:
                break
        return expr_list

    exprs = parse_expr_list()
    if peek_token() is not None:
        raise ValueError(f"Unexpected token at the end: {get_token()}")
    return exprs

# end def parse_args
