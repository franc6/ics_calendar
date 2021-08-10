import importlib

class ICalendarParser:
    @staticmethod
    def get_class(parser: str):
        parser = "parser_" + parser
        parser_package = ".parsers." + parser
        try:
            print(parser)
            module = importlib.import_module(parser_package, __package__)
            return getattr(module, parser)
        except ImportError:
            return None

    @staticmethod
    def get_instance(parser: str, *args):
        parser_cls = ICalendarParser.get_class(parser)
        if parser_cls is not None:
            return parser_cls(*args)
        return None

    def get_event_list(self, content: str, start, end, include_all_day: bool):
        pass

    def get_current_event(self, content: str, include_all_day: bool):
        pass
