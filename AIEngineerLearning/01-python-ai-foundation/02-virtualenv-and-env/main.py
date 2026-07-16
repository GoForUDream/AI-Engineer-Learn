import config


def main():
    print("--- Configuration Loaded Successfully ---")
    print(f"Environment: {config.APP_ENV}")
    print(f"Log Level:   {config.LOG_LEVEL}")
    # Truncate the key in logs to keep it secure
    masked_key = f"{config.GEMINI_API_KEY[:6]}..." if config.GEMINI_API_KEY else "None"
    print(f"API Key:     {masked_key}")


if __name__ == "__main__":
    main()
