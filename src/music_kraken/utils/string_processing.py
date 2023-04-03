def unify(string: str) -> str:
    """
    returns an unified str, to make comparosons easy.
    an unified string has following attributes:
     - is lowercase
    """
    
    return string.lower()

def fit_to_file_system(string: str) -> str:
    string = string.strip()
    
    while string[0] == ".":
        if len(string) == 0:
            return string
        
        string = string[1:]
        
    string = string.replace("/", "|").replace("\\", "|")
        
    return string
    