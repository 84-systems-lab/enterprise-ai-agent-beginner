from pathlib import Path

policy_path = Path("resources/company/returns-policy.md")
policy_text = policy_path.read_text(encoding="utf-8")
print(policy_text)
