# State Machine

## State list
- `BOOTING`
- `EMULATOR_READY`
- `GAME_LAUNCHING`
- `LOGIN_SCREEN`
- `SERVER_SELECT_SCREEN`
- `CHARACTER_SELECT_SCREEN`
- `LOADING_SCREEN`
- `HOME_SCREEN`
- `REWARD_SCREEN`
- `MAIL_SCREEN`
- `QUEST_SCREEN`
- `TRAIN_SCREEN`
- `POPUP_SCREEN`
- `DISCONNECTED_SCREEN`
- `UNKNOWN_SCREEN`
- `RECOVERY_STATE`
- `STOPPED`

## State model
Mỗi state nên định nghĩa:
- entry condition
- exit condition
- max timeout
- allowed actions
- fallback transition
- verification rule

## Transition principles
- Không transition chỉ vì 1 tín hiệu yếu
- Dùng nhiều anchor để xác nhận state
- Action quan trọng phải verify bằng state change hoặc UI change
- Mọi state phải có timeout

## Example transition table

| Current State | Trigger | Next State | Action |
|---|---|---|---|
| BOOTING | emulator online | EMULATOR_READY | init device |
| EMULATOR_READY | app launched | GAME_LAUNCHING | wait |
| GAME_LAUNCHING | loading detected | LOADING_SCREEN | wait |
| LOADING_SCREEN | home detected | HOME_SCREEN | idle |
| HOME_SCREEN | reward task start | REWARD_SCREEN | navigate reward |
| HOME_SCREEN | popup detected | POPUP_SCREEN | resolve popup |
| ANY | disconnect detected | DISCONNECTED_SCREEN | reconnect |
| ANY | unknown too long | RECOVERY_STATE | recovery flow |

## Unknown-state policy
Khi detect không chắc:
1. chụp screenshot
2. thử detect popup
3. back một lần
4. detect lại
5. nếu vẫn unknown -> recovery flow
6. nếu quá ngưỡng retry -> restart app

## Timeout policy
- State timeout: 10–30s tùy state
- Loading timeout: 45–60s
- Recovery timeout: 30–90s
- Nếu vượt ngưỡng thì escalate recovery level

## Recovery levels
### Level 1
- retry detection
- retry action

### Level 2
- back
- close popup
- navigate home

### Level 3
- restart app

### Level 4
- restart emulator
- mark run failed

## Suggested data model

```python
class StateSnapshot:
    state_name: str
    confidence: float
    timestamp: float
    anchors: list[str]
    metadata: dict
```
