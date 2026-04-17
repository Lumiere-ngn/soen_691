class StateGuard:
    def __init__(self):
        self.state = "INIT"

    def transition(self, security_result):
        label = security_result["label"]

        if label == "SAFE":
            self.state = "VERIFIED"
        elif label == "UNCERTAIN":
            self.state = "BLOCKED"
        elif label == "DANGEROUS":
            self.state = "BLOCKED"

        return self.state

    def can_execute(self):
        return self.state == "VERIFIED"