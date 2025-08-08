from django.db import models

# restaurants/models.py
from config.models import BaseModel

DAYS_OF_WEEK = [
    ("MON", "Monday"),
    ("TUE", "Tuesday"),
    ("WED", "Wednesday"),
    ("THU", "Thursday"),
    ("FRI", "Friday"),
    ("SAT", "Saturday"),
    ("SUN", "Sunday"),
]


class Restaurant(BaseModel):
    name = models.CharField(max_length=50)  # 음식점 명
    description = models.TextField(null=True, blank=True)  # 음식점 설명
    address = models.CharField(max_length=200)  # 음식점 주소
    contact = models.CharField(max_length=50)  # 음식점 연락처
    open_time = models.TimeField(null=True, blank=True)  # 오픈 시간
    close_time = models.TimeField(null=True, blank=True)  # 마감 시간
    last_order = models.TimeField(null=True, blank=True)  # 라스트 오더 시간
    regular_holiday = models.CharField(
        choices=DAYS_OF_WEEK, max_length=3, null=True, blank=True
    )  # 정기 휴무일

    def __str__(self):
        return self.name
