# Utils
import time


def search_analizer_manager(self, obj):
    """"""

    year, month, day, hour = time.strftime('%Y-%m-%d-%H').split('-')
    count = 'count'
    try:
        condition = obj.date_count[year][month][day].get(hour)
        if condition:
            obj.date_count[year][month][day][hour] += 1
        else:
            obj.date_count[year][month][day][hour] = 1
        obj.date_count[year][month][day][count] += 1
        obj.date_count[year][month][count] += 1
        obj.date_count[year][count] += 1
        obj.date_count[count] += 1
    except (KeyError,) as reason:
        reason = str(reason).replace("'", "")
        if reason == year:
            obj.date_count |= {
                year: {
                    month: {
                        day: {
                            hour: 1,
                            count: 1
                        },
                        count: 1
                    },
                    count: 1
                },
            }
            obj.date_count[count] += 1

        elif reason == month:
            print('noo')
            obj.date_count[year] |= {
                month: {
                    day: {
                        hour: 1,
                        count: 1
                    },
                    count: 1
                },
            }
            obj.date_count[count] += 1
            obj.date_count[year][count] += 1

        elif reason == day:
            obj.date_count[year][month] |= {
                day: {
                    hour: 1,
                    count: 1
                },
            }
            obj.date_count[count] += 1
            obj.date_count[year][count] += 1
            obj.date_count[year][month][count] += 1
    obj.save()
