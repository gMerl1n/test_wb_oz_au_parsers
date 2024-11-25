from abc import abstractmethod, ABC


class BaseUseCasesProduct(ABC):

    @abstractmethod
    def add_product(self):
        raise NotImplemented


class UseCasesProduct(BaseUseCasesProduct):

    def add_product(self):
        pass