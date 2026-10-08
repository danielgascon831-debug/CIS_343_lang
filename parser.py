from typing import Literal

class Node:
    """A syntax-tree node whose string shows its structure and fields."""

    def __str__(self):
        return "\n".join(self.tree_lines())

    def tree_lines(self, prefix="", field="", connector=""):
        label = self.__class__.__name__
        children = []
        for name, value in vars(self).items():
            if isinstance(value, Node):
                children.append((name, value))
            elif value is not None:
                label += f" ({name}={value!r})"

        lines = [f"{prefix}{connector}{field}{label}"]
        if connector:
            prefix += "    " if connector == "└── " else "│   "
        for index, (name, child) in enumerate(children):
            branch = "└── " if index == len(children) - 1 else "├── "
            lines.extend(child.tree_lines(prefix, f"{name}: ", branch))
        return lines


class Crispiness(Node):
    def __init__(self, more = None):
        self.more = more


class Cooked(Node):
    def __init__(self, style: Literal["scrambled", "poached", "fried"]):
        self.style = style


class Protein(Node):
    """Base class for the three protein productions."""


class Bacon(Protein):
    def __init__(self, crispiness):
        self.crispiness = crispiness


class Sausage(Protein):
    pass


class Eggs(Protein):
    def __init__(self, cooked):
        self.cooked = cooked


class Bread(Node):
    def __init__(self, kind: Literal["toast", "biscuits", "English_muffin"]):
        self.kind = kind


class Breakfast(Node):
    def __init__(self, main, side = None):
        self.main = main
        self.side = side
        if self.side is not None and not isinstance(self.main, Protein):
            raise ValueError("Only a protein can have a breakfast on_the_side.")


class Parser:
    def __init__(self, text):
        # Multiword terminals use underscores and are consumed as single tokens.
        self.tokens = text.split()
        self.current = 0

    def peek(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def consume(self, word):
        next = self.peek()
        if next != word or next is None:
            raise SyntaxError(
                f"consumed {word!r} at word {self.current + 1}, "
                f"got {self.peek()!r}"
            )
        self.current += 1
        return next

    def parse(self):
        tree = self.breakfast()
        if self.peek() is not None:
            raise SyntaxError(
                f"Unconsumed word {self.peek()!r} at word {self.current + 1}"
            )
        return tree

    def breakfast(self):
        # breakfast -> bread | protein ("with" breakfast "on_the_side")?
        if self.peek() in ("toast", "biscuits", "English_muffin"):
            return self.bread()
        return f"{self.protein()} with {self.breakfast()} on_the_side"

    def protein(self):
        # protein -> crispiness "crispy_bacon" | "sausage" | cooked "eggs"
        return f"{self.crispiness()} {self.consume(self.peek())}"

    def crispiness(self):
        # crispiness -> "really" | "really" crispiness
        # Think of how to implement with loop and recursion
        if self.tokens[self.current+1] in ("really"):
            self.consume(self.peek())
            self.consume(self.peek())
            return "really really"
        return self.consume(self.peek())


    def cooked(self):
        # cooked -> "scrambled" | "poached" | "fried"
        raise NotImplementedError()

    def bread(self):
        # bread -> "toast" | "biscuits" | "English_muffin"
        raise NotImplementedError()


if __name__ == "__main__":
    text = "really really crispy_bacon with scrambled eggs with toast on_the_side on_the_side"
    breakfast = Parser(text).parse()
    print(breakfast)
