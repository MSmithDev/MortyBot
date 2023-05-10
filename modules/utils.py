import tiktoken


# Function to check the number of tokens in a message
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
def checkTokenCount(input: str) -> int:
    print("Checking tokens...")
    num_tokens = len(encoding.encode(input))
    return num_tokens