from parser import *

# === Example Usage ===
if __name__ == "__main__":
    config_text = """
    date: 1 Jan 2025 # A tuple of number 1, keyword Jan, number 2025. This is a comment
    clients: [
        {
            name: "Adam"
            favouriteColor: rgb 15 255 255
            score: 120.4
        }
        {
            name: "Eve"
            favouriteColor: rgb 255 67 98
            score: 135.7
        }
    ]
    """
    tokens = tokenize("{" + config_text + "}")  # Wrap in top-level dict
    parser = Parser(tokens)
    parsed_config = parser.parse()
    print(parsed_config)
