def reporting_message(days_since_delivery):
    if days_since_delivery < 0:
        return "Check the delivery date."
    if days_since_delivery <= 7:
        return "Within the reporting period; review is still required."
    return "Outside this example's reporting period; ask support."


if __name__ == "__main__":
    print(reporting_message(3))
    print(reporting_message(9))
