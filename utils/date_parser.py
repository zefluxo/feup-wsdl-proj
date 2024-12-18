from dateutil import parser


def parse(date:str):
    
    try: return parser.parse(date, dayfirst=True, fuzzy=True)
    except parser.ParserError: return False
    
""" def parse(date: str):
    
    try:
        
        parsed_date = parser.parse(date, dayfirst=True, fuzzy=True)
        if parsed_date.day and parsed_date.month:
            return parsed_date.strftime("%d/%m/%Y")
        else:
            return parsed_date.strftime("%Y")
    
    except parser.ParserError: return False
     """