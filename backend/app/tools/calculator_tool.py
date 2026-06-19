class CalculatorTool:

    def calculate(
        self,
        expression: str
    ):

        try:

            result = eval(expression)

            return str(result)

        except Exception:

            return "Invalid expression"


calculator_tool = CalculatorTool()