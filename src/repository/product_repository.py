from abc import abstractmethod, ABC


class BaseRepositoryProduct(ABC):

    @abstractmethod
    def add_product(self):
        raise NotImplemented

    @abstractmethod
    def get_product_by_id(self):
        raise NotImplemented

    @abstractmethod
    def get_products(self):
        raise NotImplemented

    @abstractmethod
    def update_product_by_id(self):
        raise NotImplemented


class RepositoryProduct(BaseRepositoryProduct):

    def add_product(self):
        pass

    def get_product_by_id(self):
        pass

    def get_products(self):
        pass

    def update_product_by_id(self):
        pass