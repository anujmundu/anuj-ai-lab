class ToolRegistry:

    def __init__(self):

        self.tools = {}

    def register(
        self,
        name,
        tool
    ):

        self.tools[name] = tool

    def list_tools(
        self
    ):

        return list(
            self.tools.keys()
        )

    def get_tool(
        self,
        name
    ):

        return self.tools.get(
            name
        )


tool_registry = ToolRegistry()