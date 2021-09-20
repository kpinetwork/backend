class HelloWorld:
    def __init__(self):
        pass

    def hello_world(self) -> dict:
        return {"message": "hello this is a test"}

    def foo(self, a):  # NonCompliant
        b = 12
        if a == 1:
            return b
        return b
