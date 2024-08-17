# Define the categories for all of the classes
class Category:
    def __init__(self, name: str, type_name: str) -> None:
        self.name = name
        self.type_name = type_name

    def is_paired(self, another_name: str) -> bool:
        return self.name.split('-')[0] == another_name.split('-')[0]