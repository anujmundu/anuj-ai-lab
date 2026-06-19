from datetime import datetime


class DateTimeTool:

    def current_time(self):

        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


datetime_tool = DateTimeTool()