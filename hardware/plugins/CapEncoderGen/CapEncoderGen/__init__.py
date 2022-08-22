try:
    from .plugin import CapEncoderGenPlugin
    plugin = CapEncoderGenPlugin()
    plugin.register()
except Exception as e:
    from .logger import get_logger
    get_logger().exception(e, exc_info=True)
