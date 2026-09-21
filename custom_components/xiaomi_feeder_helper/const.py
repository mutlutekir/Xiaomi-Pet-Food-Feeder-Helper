"""Constants for Xiaomi Feeder Helper."""

DOMAIN = "xiaomi_feeder_helper"
XIAOMI_HOME_DOMAIN = "xiaomi_home"

# Known Xiaomi smart pet feeder models that ha_xiaomi_home does not yet
# expose a manual-feed entity for. Extend this set if you confirm another
# model's siid/aiid for its own manual-feed action.
FEEDER_MODELS = {
    "xiaomi.feeder.iv2001",  # Xiaomi Smart Pet Feeder 2
}

# The device's manual "feed now" MIoT action (method "pet-food-out"):
# service id / action id, and the single "how many portions" parameter.
FEED_SIID = 2
FEED_AIID = 1
DEFAULT_PORTIONS = 1
