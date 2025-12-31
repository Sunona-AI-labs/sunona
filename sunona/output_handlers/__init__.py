"""
Sunona Voice AI - Output Handlers Module

Handlers for processing and delivering output to telephony sources.
"""

from sunona.output_handlers.default_handler import DefaultOutputHandler

# Lazy imports for telephony handlers
def _get_twilio_handler():
    from sunona.output_handlers.twilio_handler import TwilioOutputHandler
    return TwilioOutputHandler

def _get_plivo_handler():
    from sunona.output_handlers.plivo_handler import PlivoOutputHandler
    return PlivoOutputHandler

def _get_exotel_handler():
    from sunona.output_handlers.exotel_handler import ExotelOutputHandler
    return ExotelOutputHandler


# Direct exports
TwilioOutputHandler = _get_twilio_handler()
PlivoOutputHandler = _get_plivo_handler()
ExotelOutputHandler = _get_exotel_handler()


__all__ = [
    "DefaultOutputHandler",
    "TwilioOutputHandler",
    "PlivoOutputHandler",
    "ExotelOutputHandler",
    "create_output_handler",
]


def create_output_handler(provider: str = "default", **kwargs):
    """
    Factory function to create an output handler.
    
    Defaults to 'default' handler unless explicitly specified.
    
    Args:
        provider: Handler provider name (default: 'default')
            - 'default': Default handler (no telephony)
            - 'twilio': Twilio Media Streams
            - 'plivo': Plivo audio streams
            - 'exotel': Exotel audio streams
        **kwargs: Provider-specific configuration
        
    Returns:
        Output handler instance
        
    Example:
        # Uses default handler
        handler = create_output_handler()
        
        # Use Twilio for telephony
        handler = create_output_handler("twilio")
    """
    handlers = {
        "default": DefaultOutputHandler,
        "twilio": TwilioOutputHandler,
        "plivo": PlivoOutputHandler,
        "exotel": ExotelOutputHandler,
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


def get_default_output_handler(**kwargs):
    """Get the default output handler."""
    return DefaultOutputHandler(**kwargs)
