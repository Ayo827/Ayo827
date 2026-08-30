import os
import re
import requests

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

session = requests.Session()
session.headers.update(headers)

repos = []
page = 1

while True:
    response = session.get(
        f"https://api.github.com/users/{USERNAME}/repos",
        params={
            "per_page": 100,
            "page": page,
            "type": "owner",
        },
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        break

    repos.extend(data)
    page += 1


languages = {}

for repo in repos:
    if repo["fork"]:
        continue

    response = session.get(repo["languages_url"])
    response.raise_for_status()

    repo_languages = response.json()

    for language, bytes_count in repo_languages.items():
        languages[language] = (
            languages.get(language, 0) + bytes_count
        )


total = sum(languages.values())

languages = sorted(
    languages.items(),
    key=lambda x: x[1],
    reverse=True,
)

rows = []

for language, bytes_count in languages[:10]:
    percentage = (bytes_count / total) * 100

    rows.append(
        f"| {language} | {percentage:.1f}% |"
    )

stack = """<!-- STACK_START -->

## 🛠️ Languages I've Worked With

| Language | Usage |
|----------|------:|
""" + "\n".join(rows) + """

<!-- STACK_END -->"""


with open("README.md", "r", encoding="utf-8") as file:
    readme = file.read()


pattern = r"<!-- STACK_START -->.*?<!-- STACK_END -->"

if re.search(pattern, readme, re.DOTALL):
    readme = re.sub(
        pattern,
        stack.strip(),
        readme,
        flags=re.DOTALL,
    )
else:
    readme += "\n\n" + stack


with open("README.md", "w", encoding="utf-8") as file:
    file.write(readme)

print("Updated GitHub stack.")
