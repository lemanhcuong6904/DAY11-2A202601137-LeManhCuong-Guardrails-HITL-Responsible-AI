"""
Lab 11 — Configuration & API Key Setup
"""
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-5-mini")


def setup_api_key():
    """Load OpenAI API key from environment or prompt."""
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = input("Enter OpenAI API Key: ")
    print("API key loaded.")


# Allowed banking topics (used by topic_filter)
ALLOWED_TOPICS = [
    "banking", "account", "transaction", "transfer",
    "loan", "interest", "savings", "credit",
    "deposit", "withdrawal", "balance", "payment",
    "tai khoan", "giao dich", "tiet kiem", "lai suat",
    "chuyen tien", "the tin dung", "so du", "vay",
    "ngan hang", "atm",
    "tài khoản", "giao dịch", "tiết kiệm", "lãi suất",
    "chuyển tiền", "thẻ tín dụng", "số dư", "ngân hàng",
]

# Blocked topics (immediate reject)
BLOCKED_TOPICS = [
    "hack", "exploit", "weapon", "drug", "illegal",
    "violence", "gambling", "bomb", "kill", "steal",
]
