from abc import abstractmethod, ABC


class BaseRepository(ABC):

    @abstractmethod
    def add_item(self):
        raise NotImplemented

    @abstractmethod
    def get_item_by_id(self):
        raise NotImplemented

    @abstractmethod
    def get_items(self):
        raise NotImplemented

    @abstractmethod
    def update_item_by_id(self):
        raise NotImplemented


class Repository(BaseRepository):

    def add_item(self):
        pass

    def get_item_by_id(self):
        pass

    def get_items(self):
        pass

    def update_item_by_id(self):
        pass