"""
Sunona Voice AI - Input Handlers Module

Handlers for processing input from various telephony sources.
"""

from sunona.input_handlers.default_handler import DefaultInputHandler

# Lazy imports for telephony handlers
def _get_twilio_handler():
    from sunona.input_handlers.twilio_handler import TwilioInputHandler
    return TwilioInputHandler

def _get_plivo_handler():
    from sunona.input_handlers.plivo_handler import PlivoInputHandler
    return PlivoInputHandler

def _get_exotel_handler():
    from sunona.input_handlers.exotel_handler import ExotelInputHandler
    return ExotelInputHandler


# Direct exports
TwilioInputHandler = _get_twilio_handler()
PlivoInputHandler = _get_plivo_handler()
ExotelInputHandler = _get_exotel_handler()


__all__ = [
    "DefaultInputHandler",
    "TwilioInputHandler",
    "PlivoInputHandler",
    "ExotelInputHandler",
    "create_input_handler",
]


def create_input_handler(provider: str = "default", **kwargs):
    """
    Factory function to create an input handler.
    
    Defaults to 'default' handler unless explicitly specified.
    
    Args:
        provider: Handler provider name (default: 'default')
            - 'default': Default handler (no telephony)
            - 'twilio': Twilio Media Streams
            - 'plivo': Plivo audio streams
            - 'exotel': Exotel audio streams
        **kwargs: Provider-specific configuration
        
    Returns:
        Input handler instance
        
    Example:
        # Uses default handler
        handler = create_input_handler()
        
        # Use Twilio for telephony
        handler = create_input_handler("twilio")
    """
    handlers = {
        "default": DefaultInputHandler,
        "twilio": TwilioInputHandler,
        "plivo": PlivoInputHandler,
        "exotel": ExotelInputHandler,
    }
    
    # Default to 'default' if not specified or None
    if not provider:
        provider = "default"
    
    if provider not in handlers:
        # Fallback to default for unknown providers
        import warnings
        warnings.warn(f"Unknown handler '{provider}', using 'default'")
        provider = "default"
    
    return handlers[provider](**kwargs)


def get_default_input_handler(**kwargs):
    """Get the default input handler."""
    return DefaultInputHandler(**kwargs)
