from app.connectors.currency_connector import currency_connector


class CurrencyTool:

    def get_rates(self):

        return currency_connector.get_rates()


currency_tool = CurrencyTool()