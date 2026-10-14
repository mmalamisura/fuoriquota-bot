name: Fuori Quota Bot

on:
  schedule:
    - cron: '0 7 * * *'   # 09:00 Italia = 07:00 UTC
    - cron: '0 12 * * *'  # 14:00 Italia = 12:00 UTC
    - cron: '45 18 * * *' # 20:45 Italia = 18:45 UTC
  workflow_dispatch: # per farlo partire a mano

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run bot
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          CHANNEL_ID: ${{ secrets.CHANNEL_ID }}
          ODDS_API_KEY: ${{ secrets.ODDS_API_KEY }}
        run: python bot.py
