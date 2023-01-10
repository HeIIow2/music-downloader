class AttributeThing:
    def __init__(self) -> None:
        self.an_attribute = 666

    def __setattr__(self, __name: str, __value: any) -> None:
        print(__name, __value)
        self.an_attribute = __value

    def __getattribute__(self, __name: str) -> any:
        print(__name)
        self.an_attribute += 333
        return self.an_attribute


if __name__ == "__main__":
    attribute_class = AttributeThing()

    attribute_class.an_attribute = 333
    #print(attribute_class.an_attribute)
