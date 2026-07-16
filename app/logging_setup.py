import logging, json, os

class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "module": record.name,
            "msg": record.getMessage(),
            **getattr(record, "extra_data", {}),
        }
        return json.dumps(entry)
    
def setup_logging():
    os.makedirs("logs", exist_ok=True)
    root = logging.getLogger("drivecast")
    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s"))

    jsonl = logging.FileHandler("logs/drive.jsonl")
    jsonl.setFormatter(JsonFormatter())

    root.addHandler(console)
    root.addHandler(jsonl)
    return root