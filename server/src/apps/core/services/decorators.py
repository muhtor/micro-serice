

def format_message(x):
    def message(msg, prefix):
        if "%s" in msg:
            return msg % prefix
        return msg
    return message


@format_message
def message_prefixing(message, prefix):
    return message
