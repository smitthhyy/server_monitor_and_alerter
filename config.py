import yaml

class Config:
    def __init__(self, path="config.yaml"):
        with open(path) as f:
            data = yaml.safe_load(f)
        self.aws = data["aws"]
        self.thresholds = data["thresholds"]
        self.interval = data.get("interval_secs", 60)
        # new: optional string to tack on after [ALERT]
        self.subject_suffix = data.get("subject_suffix", "")
        self.logging_cfg = data.get("logging", {})


config = Config()
