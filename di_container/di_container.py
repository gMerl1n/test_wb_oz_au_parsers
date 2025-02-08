import punq
from src.repository.product_repository.product_repository import RepositoryProduct, BaseRepositoryProduct
from src.repository.cookies_repository.cookies_repository import RepositoryCookies, BaseRepositoryCookies
from src.use_cases.cookies_use_cases import CookiesUseCases, BaseUseCasesCookies
from src.use_cases.product_use_cases import UseCasesProduct, BaseUseCasesProduct
from src.services.parsers_service.wb_service import BaseWBParser, WBParser
from src.services.parsers_service.oz_service import BaseOZParser, OZParser
from src.services.parsers_service.au_service import BaseAUParser, AUParser
from config.settings import Settings


class DIContainer:
    container = punq.Container()
    container.register(BaseRepositoryProduct, RepositoryProduct)
    container.register(BaseRepositoryCookies, RepositoryCookies)
    container.register(BaseUseCasesCookies, CookiesUseCases)
    container.register(BaseUseCasesProduct, UseCasesProduct)

    container.register(BaseWBParser, WBParser)
    container.register(BaseOZParser, OZParser)
    container.register(BaseUseCasesCookies, OZParser)
    container.register(BaseAUParser, AUParser)

    container.register(Settings)

    def get_parser_wb(self) -> BaseWBParser:
        return self.container.resolve(BaseWBParser)

    def get_parser_oz(self) -> BaseOZParser:
        return self.container.resolve(BaseOZParser)

    def get_parser_au(self) -> BaseAUParser:
        return self.container.resolve(BaseAUParser)

    def get_use_cases_product(self) -> BaseUseCasesProduct:
        return self.container.resolve(BaseUseCasesProduct)


di_container = DIContainer()
