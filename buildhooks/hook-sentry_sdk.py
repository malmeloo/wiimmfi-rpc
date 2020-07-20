# Hidden sentry_sdk imports for PyInstaller.
# Thanks to https://github.com/pyinstaller/pyinstaller/issues/4755#issuecomment-638409983


hiddenimports = [
    "sentry_sdk.integrations.stdlib",
    "sentry_sdk.integrations.excepthook",
    "sentry_sdk.integrations.dedupe",
    "sentry_sdk.integrations.atexit",
    "sentry_sdk.integrations.modules",
    "sentry_sdk.integrations.argv",
    "sentry_sdk.integrations.logging",
    "sentry_sdk.integrations.threading",

    "packaging.version",
    "packaging.specifiers",
    "packaging.requirements"
]
