import ollama

def get_response(prompt, stream=False):
    """
    Fetches the bot response using the Ollama API.
    
    :param prompt: The user input prompt.
    :param stream: If True, fetch the response in chunks.
    :return: The response from the model.
    """
    try:
        response = ollama.chat(
            model="llama3.2:1b-instruct-q3_K_M",
            messages=[{'role': 'user', 'content': prompt}],
            stream=stream  # Enable streaming if specified
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Failed to fetch response: {str(e)}")
