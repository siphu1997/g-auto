SCREEN_SIGNATURES: dict[str, dict[str, set[str]]] = {
    "HOME_SCREEN": {
        "all_of": {"home_minimap", "home_menu"},
        "any_of": {"reward_entry", "mail_entry"},
        "none_of": {"loading_spinner"},
    },
    "REWARD_SCREEN": {
        "all_of": {"reward_claim_all"},
        "any_of": set(),
        "none_of": set(),
    },
    "MAIL_SCREEN": {
        "all_of": {"mail_claim_all"},
        "any_of": set(),
        "none_of": set(),
    },
    "POPUP_SCREEN": {
        "all_of": {"popup_close"},
        "any_of": set(),
        "none_of": set(),
    },
    "LOADING_SCREEN": {
        "all_of": {"loading_spinner"},
        "any_of": set(),
        "none_of": {"home_minimap", "home_menu"},
    },
}

