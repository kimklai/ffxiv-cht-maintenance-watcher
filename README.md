## FF14 針對繁中版官方維護公告的追蹤器
簡易的追蹤官方不定期發出來的伺服器護維公告
並且將最新的公告發送到相應的dicord頻道中

### 手動執行
- python monitor.py
- 請確保環境變數中有 DISCORD_WEBHOOK

### 使用 github action
- 請在 project settings > security 裡面增加 DISCORD_WEBHOOK

#### DISCORD_WEBHOOK 格式
- 支援多頻道同時發送，中間用,分隔。
- ex: webhook1,webhook2
