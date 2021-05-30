from datetime import date, timedelta
from dictdiffer import utils
from notion.collection import NotionDate
from src.Notion import Notion
import pandas as pd
import utils


class Scrum(Notion):
    board = None

    def __init__(self):
        super().__init__()
        self.set_scrum()

    def set_scrum(self):
        url = self.conf["SCRUM"]["URL"]
        self.board = self.client.get_collection_view(url)

    def get_filtered_card_ids(self, key, value):
        card_ids = []
        for card in self.board.collection.get_rows():
            current = self.client.get_block(card.id)

            if getattr(current, key) != value:
                continue

            card_ids.append(card.id)

        return card_ids

    def get_analysis_data_of_week(self):
        duration = self.conf["CARD"]["DURATION"]
        status = self.conf["CARD"]["STATUS"]
        done = self.conf["SCRUM"]["STEPS"]["DONE"]

        cards = self.board.collection.get_rows()
        task_count = len(cards)

        times = utils.get_time_series(utils.add_time(days=-7))
        task_durations = [float(task_count) for _ in range(len(times))]

        for card in cards:
            if card.get_property(status) != done:
                continue

            notion_date = card.get_property(duration)

            # 해당 태스크 끝내는 데 걸린 시간
            task_duration = notion_date.end - notion_date.start

            # 해당 태스크를 하루에 처리한 양
            task_per_day = float(1 / (task_duration.days + 1))

            duration_count = 1

            subtracting_start_date = notion_date.start + pd.Timedelta(days=1)
            subtracting_finish_date = notion_date.end + pd.Timedelta(days=1)

            for index, time in enumerate(times):
                if time < subtracting_start_date:
                    continue
                elif subtracting_start_date <= time <= subtracting_finish_date:
                    task_durations[index] = (
                        task_durations[index] - task_per_day * duration_count
                    )
                    duration_count += 1
                else:
                    task_durations[index] = (
                        task_durations[index] - task_per_day * duration_count
                    )
        print(task_durations)

        return {"task_count": task_count, "data": task_durations}
