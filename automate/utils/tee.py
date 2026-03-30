class Tee:
    def __init__(self, original, buffer):
        self.original = original
        self.buffer = buffer

    def write(self, data):
        self.original.write(data)   # show in terminal
        self.buffer.write(data)     # save to buffer

    def flush(self):
        self.original.flush()
        self.buffer.flush()