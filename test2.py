class Event(object):

    def __init__(self, time, location, describe):
        self.time = time
        self.location = location
        self.describe = describe

    # 重写print
    def __str__(self):
        return ("time: {}; location: {}; describe: {}".format(
            self.time, self.location, self.describe))

    # 重写 < 符号用于sorted
    def __lt__(self, other):
        return self.time < other.time


if __name__ == '__main__':
    event1 = Event(time="2019-11-13",
                   location="California",
                   describe="Wildfire in CA.")
    event2 = Event(time="2020-01-12", location="NY", describe="xxx")
    event3 = Event(time="2016-12-13", location="UK", describe="xxx")

    events = [event1, event2, event3]
    # 按照类的time属性从小到大排序输出
    events = sorted(events)
    for event in events:
        print(event)
