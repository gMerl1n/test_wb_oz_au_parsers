from src.repository.product_repository import RepositoryProduct, BaseRepositoryProduct
from src.repository.cookies_repository import RepositoryCookies, BaseRepositoryCookies
from src.use_cases.cookies_use_cases import CookiesUseCases, BaseUseCasesCookies
from src.use_cases.product_use_cases import UseCasesProduct, BaseUseCasesProduct
from src.services.wb_service import BaseWBParser, WBParser
from src.services.oz_service import BaseOZParser, OZParser
from src.services.au_service import BaseAUParser, AUParser
import punq


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


di_container = DIContainer()
