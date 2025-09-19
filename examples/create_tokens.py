from picas.documents import Task

def create_tokens(fields: dict, offset: int = 0) -> list:
    """
    Create the tokens as a list of Task documents.

    The fields parameter is a dictionary where keys are field names and values are
    lists of input values. For every 'input' value a unique id is assigned and the
    corresponding input value is used to create a token.

    For example, the following becomes a list of tokens:
     {'input': [
        "echo 'this is token A'",
        "echo 'this is token B'",
        "echo 'this is token C'"]
     }


    :param fields: A dictionary where keys are field names and values are lists of input values.
    :param offset: An integer offset to start numbering the token IDs from (default is 0).
     This is useful if you want to create tokens in multiple batches and ensure unique IDs.
    :return: A list of Task documents representing the tokens. For the example above,
      it would return a list of three Task objects with .id attributes set to
      'token_0', 'token_1', and 'token_2' respectively and .input attributes of each set to
      "echo 'this is token A'", "echo 'this is token B'", and "echo 'this is token C'".
    """
    tokens = []
    n_docs = offset
    for arg in fields:
        for line in fields[arg]:
            token = {
                '_id': 'token_' + str(n_docs),
                'type': 'token',
                arg: line,
            }
            tokens.append(Task(token))
            n_docs += 1

    return tokens
