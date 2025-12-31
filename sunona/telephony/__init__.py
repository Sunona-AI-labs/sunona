"""
Sunona Voice AI - Telephony Module

Telephony integration providers for voice calls.

Providers:
- twilio: Twilio voice calls
- plivo: Plivo voice calls
- vonage: Vonage (Nexmo) voice calls
- signalwire: SignalWire voice calls
- telnyx: Telnyx voice calls
- bandwidth: Bandwidth voice calls
"""

from sunona.telephony.twilio_handler import TwilioHandler

# Lazy imports for optional providers
def _get_plivo_handler():
    from sunona.telephony.plivo_handler import PlivoHandler
    return PlivoHandler

def _get_vonage_handler():
    from sunona.telephony.vonage_handler import VonageHandler
    return VonageHandler

def _get_signalwire_handler():
    from sunona.telephony.signalwire_handler import SignalWireHandler
    return SignalWireHandler

def _get_telnyx_handler():
    from sunona.telephony.telnyx_handler import TelnyxHandler
    return TelnyxHandler

def _get_bandwidth_handler():
    from sunona.telephony.bandwidth_handler import BandwidthHandler
    return BandwidthHandler

def _get_conference_manager():
    from sunona.telephony.conference import ConferenceManager
    return ConferenceManager

__all__ = [
    "TwilioHandler",
    "create_telephony_handler",
    "get_conference_manager",
]


def create_telephony_handler(provider: str, **kwargs):
    """
    Factory function to create a telephony handler.
    
    Args:
        provider: Provider name ('twilio', 'plivo', 'vonage', 'signalwire', 'telnyx', 'bandwidth')
        **kwargs: Provider-specific configuration
        
    Returns:
        Configured telephony handler
    """
    handlers = {
        "twilio": lambda: TwilioHandler(**kwargs),
        "plivo": lambda: _get_plivo_handler()(**kwargs),
        "vonage": lambda: _get_vonage_handler()(**kwargs),
        "signalwire": lambda: _get_signalwire_handler()(**kwargs),
        "telnyx": lambda: _get_telnyx_handler()(**kwargs),
        "bandwidth": lambda: _get_bandwidth_handler()(**kwargs),
    }
    
    if provider not in handlers:
        raise ValueError(
            f"Unknown telephony provider: {provider}. "
            f"Available: {', '.join(handlers.keys())}"
        )
    
    return handlers[provider]()


def get_conference_manager(**kwargs):
    """Get a conference manager instance."""
    ConferenceManager = _get_conference_manager()
    return ConferenceManager(**kwargs)


