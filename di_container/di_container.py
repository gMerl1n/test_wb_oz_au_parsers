import punq
from src.repository.product_repository.product_repository import RepositoryProduct, BaseRepositoryProduct
from src.repository.cookies_repository.cookies_repository import RepositoryCookies, BaseRepositoryCookies
from src.use_cases.cookies_use_cases import CookiesUseCases, BaseUseCasesCookies
from src.use_cases.product_use_cases import UseCasesProduct, BaseUseCasesProduct
from src.services.parsers_service.wb_service import BaseWBParser, WBParser
from src.services.parsers_service.oz_service import BaseOZParser, OZParser
from src.services.parsers_service.au_service import BaseAUParser, AUParser


class DIContainer:
    container = punq.Container()
    container.register(BaseRepositoryProduct, RepositoryProduct)
    container.register(BaseRepositoryCookies, RepositoryCookies)
    container.register(BaseUseCasesCookies, CookiesUseCases)
    container.register(BaseUseCasesProduct, UseCasesProduct)

    def get_parser_wb(self):
        self.container.register(BaseWBParser, WBParser)
        return self.container.resolve(BaseWBParser)

    def get_parser_oz(self):
        self.container.register(BaseOZParser, OZParser)
        return self.container.resolve(BaseOZParser)

    def get_parser_au(self):
        self.container.register(BaseAUParser, AUParser)
        return self.container.resolve(BaseAUParser)

    def get_use_cases_product(self):
        return self.container.resolve(BaseUseCasesProduct)


di_container = DIContainer()
