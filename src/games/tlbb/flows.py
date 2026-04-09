from __future__ import annotations

from core.models import StateName, TaskName


TASK_RULES = {
    TaskName.LAUNCH.value: {
        "preconditions": set(),
        "target_state": StateName.HOME_SCREEN,
        "entry_anchor": None,
        "claim_anchor": None,
    },
    TaskName.CLAIM_REWARD.value: {
        "preconditions": {StateName.HOME_SCREEN},
        "target_state": StateName.REWARD_SCREEN,
        "entry_anchor": "reward_entry",
        "claim_anchor": "reward_claim_all",
    },
    TaskName.CLAIM_MAIL.value: {
        "preconditions": {StateName.HOME_SCREEN},
        "target_state": StateName.MAIL_SCREEN,
        "entry_anchor": "mail_entry",
        "claim_anchor": "mail_claim_all",
    },
}

UNIMPLEMENTED_TASKS = {
    TaskName.DAILY.value,
    TaskName.QUEST.value,
    TaskName.TRAIN.value,
}

