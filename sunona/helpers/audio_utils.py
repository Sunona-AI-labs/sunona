"""
Sunona Voice AI - Audio Utilities

Audio format conversion and processing utilities.
"""

import io
import struct
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def convert_audio_format(
    audio_bytes: bytes,
    from_format: str,
    to_format: str,
    sample_rate: int = 16000,
    channels: int = 1,
) -> bytes:
    """
    Convert audio between formats.
    
    Args:
        audio_bytes: Input audio bytes
        from_format: Source format ('pcm', 'mulaw', 'wav')
        to_format: Target format ('pcm', 'mulaw', 'wav')
        sample_rate: Sample rate in Hz
        channels: Number of audio channels
        
    Returns:
        Converted audio bytes
    """
    if from_format == to_format:
        return audio_bytes
    
    # PCM to WAV
    if from_format == "pcm" and to_format == "wav":
        return pcm_to_wav(audio_bytes, sample_rate, channels)
    
    # WAV to PCM
    if from_format == "wav" and to_format == "pcm":
        return wav_to_pcm(audio_bytes)
    
    # Mulaw to PCM
    if from_format == "mulaw" and to_format == "pcm":
        return mulaw_to_pcm(audio_bytes)
    
    # PCM to Mulaw
    if from_format == "pcm" and to_format == "mulaw":
        return pcm_to_mulaw(audio_bytes)
    
    logger.warning(f"Unsupported conversion: {from_format} -> {to_format}")
    return audio_bytes


def pcm_to_wav(
    pcm_bytes: bytes,
    sample_rate: int = 16000,
    channels: int = 1,
    bits_per_sample: int = 16,
) -> bytes:
    """
    Convert raw PCM audio to WAV format.
    
    Args:
        pcm_bytes: Raw PCM audio bytes
        sample_rate: Sample rate in Hz
        channels: Number of channels
        bits_per_sample: Bits per sample (8 or 16)
        
    Returns:
        WAV file bytes
    """
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm_bytes)
    
    # Create WAV header
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,  # File size minus 8
        b'WAVE',
        b'fmt ',
        16,  # fmt chunk size
        1,   # Audio format (PCM)
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size,
    )
    
    return wav_header + pcm_bytes


def wav_to_pcm(wav_bytes: bytes) -> bytes:
    """
    Extract raw PCM data from WAV file.
    
    Args:
        wav_bytes: WAV file bytes
        
    Returns:
        Raw PCM audio bytes
    """
    # Simple extraction - skip 44-byte WAV header
    if len(wav_bytes) > 44 and wav_bytes[:4] == b'RIFF':
        return wav_bytes[44:]
    return wav_bytes


def mulaw_to_pcm(mulaw_bytes: bytes) -> bytes:
    """
    Convert µ-law encoded audio to linear PCM.
    
    Args:
        mulaw_bytes: µ-law encoded audio bytes
        
    Returns:
        Linear PCM audio bytes (16-bit)
    """
    MULAW_BIAS = 33
    MULAW_MAX = 32635
    
    pcm_samples = []
    
    for mulaw_byte in mulaw_bytes:
        # Invert all bits
        mulaw_value = ~mulaw_byte & 0xFF
        
        # Extract sign and magnitude
        sign = (mulaw_value >> 7) & 1
        exponent = (mulaw_value >> 4) & 0x07
        mantissa = mulaw_value & 0x0F
        
        # Convert to linear
        sample = ((mantissa << 3) + MULAW_BIAS) << exponent
        sample -= MULAW_BIAS
        
        if sign:
            sample = -sample
        
        # Pack as 16-bit signed integer
        pcm_samples.append(struct.pack('<h', max(-32768, min(32767, sample))))
    
    return b''.join(pcm_samples)


def pcm_to_mulaw(pcm_bytes: bytes) -> bytes:
    """
    Convert linear PCM audio to µ-law encoding.
    
    Args:
        pcm_bytes: Linear PCM audio bytes (16-bit)
        
    Returns:
        µ-law encoded audio bytes
    """
    MULAW_BIAS = 33
    MULAW_MAX = 32635
    
    mulaw_samples = []
    
    # Process 16-bit samples
    for i in range(0, len(pcm_bytes), 2):
        if i + 1 < len(pcm_bytes):
            sample = struct.unpack('<h', pcm_bytes[i:i+2])[0]
        else:
            break
        
        # Determine sign
        sign = 1 if sample < 0 else 0
        sample = abs(sample)
        
        # Clip and add bias
        sample = min(sample, MULAW_MAX)
        sample += MULAW_BIAS
        
        # Find exponent
        exponent = 7
        for exp in range(7, -1, -1):
            if sample >= (1 << (exp + 3)):
                exponent = exp
                break
        
        # Calculate mantissa
        mantissa = (sample >> (exponent + 3)) & 0x0F
        
        # Combine and invert
        mulaw_value = ~((sign << 7) | (exponent << 4) | mantissa) & 0xFF
        mulaw_samples.append(bytes([mulaw_value]))
    
    return b''.join(mulaw_samples)


def resample_audio(
    audio_bytes: bytes,
    from_rate: int,
    to_rate: int,
) -> bytes:
    """
    Resample audio to a different sample rate.
    
    Note: This is a simple linear interpolation resampling.
    For production use, consider using scipy or librosa.
    
    Args:
        audio_bytes: Input audio bytes (16-bit PCM)
        from_rate: Source sample rate in Hz
        to_rate: Target sample rate in Hz
        
    Returns:
        Resampled audio bytes
    """
    if from_rate == to_rate:
        return audio_bytes
    
    # Unpack 16-bit samples
    samples = []
    for i in range(0, len(audio_bytes), 2):
        if i + 1 < len(audio_bytes):
            samples.append(struct.unpack('<h', audio_bytes[i:i+2])[0])
    
    if not samples:
        return audio_bytes
    
    # Calculate resampling ratio
    ratio = to_rate / from_rate
    new_length = int(len(samples) * ratio)
    
    # Simple linear interpolation
    resampled = []
    for i in range(new_length):
        src_idx = i / ratio
        idx = int(src_idx)
        frac = src_idx - idx
        
        if idx >= len(samples) - 1:
            sample = samples[-1]
        else:
            sample = int(samples[idx] * (1 - frac) + samples[idx + 1] * frac)
        
        resampled.append(struct.pack('<h', max(-32768, min(32767, sample))))
    
    return b''.join(resampled)


def get_audio_duration(
    audio_bytes: bytes,
    sample_rate: int = 16000,
    bits_per_sample: int = 16,
    channels: int = 1,
) -> float:
    """
    Calculate audio duration in seconds.
    
    Args:
        audio_bytes: Audio bytes
        sample_rate: Sample rate in Hz
        bits_per_sample: Bits per sample
        channels: Number of channels
        
    Returns:
        Duration in seconds
    """
    bytes_per_sample = bits_per_sample // 8
    bytes_per_second = sample_rate * channels * bytes_per_sample
    return len(audio_bytes) / bytes_per_second
