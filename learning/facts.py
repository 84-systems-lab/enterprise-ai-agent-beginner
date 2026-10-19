reporting_days = 7
required_items = ["order number", "photographs"]
policy = {"title": "Returns policy", "days": reporting_days}

print(policy["title"])
print("Report within", policy["days"], "calendar days.")
for item in required_items:
    print("Bring:", item)
