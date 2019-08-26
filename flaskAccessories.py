"""

A module for creating account_codes for users on jonathanolson.us

"""


import hashlib


def create_account_code(user_id):
    """
     A function to create a user account_code from their id, which is
     generated during their signup on my website. The returned account_code
     is simply an encryption of their id.

     Args:
        user_id: str - A string of their user id

    Returns:
        str - user account_code

    Raises:
        TypeError: Raises an exception when the input value cannot be hashed
    """

    # Make sure the user_id is a string:
    try:
        user_id = str(user_id)
    except TypeError:
        return "TypeError: argument 'user_id' cannot be hashed."

    # Encode the user_id
    encoded_user_id = user_id.encode()

    # Create a sha256 HASH object from the encoded user_id
    sha_hash_id = hashlib.sha256(encoded_user_id)

    # Retrieve the hech digest of the hashed id
    new_account_code = sha_hash_id.hexdigest()

    # Shorten the string: get every second character
    new_account_code = new_account_code[::2]

    return new_account_code
