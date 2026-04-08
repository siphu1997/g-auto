# Configuration Schema

## Principles
- Tách config theo domain
- Có default + override
- Validate schema khi startup
- Dễ chỉnh mà không cần sửa core code

## app.yaml
```yaml
app:
  env: local
  debug: true
  log_level: INFO
  data_dir: ./data
```

## emulator.yaml
```yaml
emulator:
  provider: ldplayer
  adb_serial: 127.0.0.1:5555
  profile: ldplayer_1280x720
  resolution:
    width: 1280
    height: 720
  dpi: 240
  restart_on_failure: true
```

## bot.yaml
```yaml
bot:
  tick_interval_ms: 1200
  screenshot_interval_ms: 1500
  verify_after_action: true
  save_debug_screenshots: true
  max_unknown_retries: 3
```

## tasks.yaml
```yaml
tasks:
  launch:
    enabled: true
  claim_reward:
    enabled: true
    max_duration_sec: 120
  claim_mail:
    enabled: true
    max_duration_sec: 120
  daily:
    enabled: true
    max_duration_sec: 600
  quest:
    enabled: true
    max_duration_sec: 900
  train:
    enabled: false
    max_duration_sec: 1800
```

## schedules.yaml
```yaml
schedules:
  enabled: true
  jobs:
    - name: morning_daily
      task: daily
      cron: "0 8 * * *"
    - name: noon_claim
      task: claim_reward
      cron: "0 12 * * *"
```

## Recommended schema sections
- `app`
- `emulator`
- `bot`
- `vision`
- `recovery`
- `tasks`
- `schedules`

## Recovery example
```yaml
recovery:
  detect_retry: 3
  action_retry: 2
  state_timeout_sec: 20
  loading_timeout_sec: 60
  restart_app_after_failures: 3
  restart_emulator_after_failures: 5
```
