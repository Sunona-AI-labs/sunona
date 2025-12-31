"""
Sunona Voice AI - Call Recording System

Production-grade call recording with storage, transcription,
and compliance features.

Features:
- Real-time audio recording
- Multiple storage backends (local, S3, Azure)
- Automatic transcription
- Recording metadata
- Consent management
- Retention policies
"""

import asyncio
import io
import json
import logging
import os
import tempfile
import wave
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, BinaryIO
import uuid

logger = logging.getLogger(__name__)


class RecordingStatus(Enum):
    """Recording lifecycle states."""
    PENDING = "pending"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class ConsentStatus(Enum):
    """Consent states for recording."""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    NOT_REQUIRED = "not_required"


@dataclass
class RecordingMetadata:
    """
    Metadata for a call recording.
    
    Attributes:
        recording_id: Unique identifier
        call_id: Associated call ID
        agent_id: AI agent ID
        user_id: User/account ID
        caller_number: Caller phone number
        callee_number: Called phone number
        started_at: Recording start time
        ended_at: Recording end time
        duration_seconds: Total duration
        file_size_bytes: Recording file size
        file_format: Audio format (wav, mp3, etc.)
        storage_location: Where recording is stored
        storage_url: URL to access recording
        consent_status: Recording consent status
        transcription_id: Associated transcription ID
        tags: Custom tags
        metadata: Additional metadata
    """
    recording_id: str
    call_id: str
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    caller_number: Optional[str] = None
    callee_number: Optional[str] = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    file_size_bytes: int = 0
    file_format: str = "wav"
    sample_rate: int = 16000
    channels: int = 1
    storage_location: str = "local"
    storage_url: Optional[str] = None
    status: RecordingStatus = RecordingStatus.PENDING
    consent_status: ConsentStatus = ConsentStatus.PENDING
    transcription_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recording_id": self.recording_id,
            "call_id": self.call_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "caller_number": self.caller_number,
            "callee_number": self.callee_number,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": round(self.duration_seconds, 2),
            "file_size_bytes": self.file_size_bytes,
            "file_format": self.file_format,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "storage_location": self.storage_location,
            "storage_url": self.storage_url,
            "status": self.status.value,
            "consent_status": self.consent_status.value,
            "transcription_id": self.transcription_id,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class StorageBackend(ABC):
    """Abstract base class for recording storage."""
    
    @abstractmethod
    async def save(
        self,
        recording_id: str,
        audio_data: bytes,
        metadata: RecordingMetadata,
    ) -> str:
        """
        Save recording to storage.
        
        Returns:
            Storage URL/path
        """
        pass
    
    @abstractmethod
    async def load(self, recording_id: str) -> Optional[bytes]:
        """Load recording from storage."""
        pass
    
    @abstractmethod
    async def delete(self, recording_id: str) -> bool:
        """Delete recording from storage."""
        pass
    
    @abstractmethod
    async def get_url(self, recording_id: str, expires_in: int = 3600) -> Optional[str]:
        """Get a signed URL for accessing the recording."""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str = "recordings"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, recording_id: str) -> Path:
        """Get file path for a recording."""
        # Organize by date
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        dir_path = self.base_path / date_prefix
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{recording_id}.wav"
    
    async def save(
        self,
        recording_id: str,
        audio_data: bytes,
        metadata: RecordingMetadata,
    ) -> str:
        """Save recording to local filesystem."""
        file_path = self._get_file_path(recording_id)
        
        # Save audio file
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        # Save metadata
        meta_path = file_path.with_suffix(".json")
        with open(meta_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        logger.info(f"Saved recording {recording_id} to {file_path}")
        return str(file_path)
    
    async def load(self, recording_id: str) -> Optional[bytes]:
        """Load recording from local filesystem."""
        file_path = self._get_file_path(recording_id)
        
        if not file_path.exists():
            return None
        
        with open(file_path, "rb") as f:
            return f.read()
    
    async def delete(self, recording_id: str) -> bool:
        """Delete recording from local filesystem."""
        file_path = self._get_file_path(recording_id)
        
        if file_path.exists():
            file_path.unlink()
            
            # Also delete metadata
            meta_path = file_path.with_suffix(".json")
            if meta_path.exists():
                meta_path.unlink()
            
            logger.info(f"Deleted recording {recording_id}")
            return True
        
        return False
    
    async def get_url(self, recording_id: str, expires_in: int = 3600) -> Optional[str]:
        """Get file path as URL (local only)."""
        file_path = self._get_file_path(recording_id)
        
        if file_path.exists():
            return f"file://{file_path.absolute()}"
        
        return None


class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend."""
    
    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        prefix: str = "recordings/",
    ):
        self.bucket = bucket
        self.region = region
        self.prefix = prefix
        self._client = None
    
    async def _get_client(self):
        """Get or create S3 client."""
        if self._client is None:
            try:
                import aioboto3
                session = aioboto3.Session()
                self._client = await session.client(
                    "s3",
                    region_name=self.region,
                ).__aenter__()
            except ImportError:
                logger.error("aioboto3 not installed for S3 storage")
                raise
        return self._client
    
    def _get_key(self, recording_id: str) -> str:
        """Get S3 key for a recording."""
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        return f"{self.prefix}{date_prefix}/{recording_id}.wav"
    
    async def save(
        self,
        recording_id: str,
        audio_data: bytes,
        metadata: RecordingMetadata,
    ) -> str:
        """Save recording to S3."""
        key = self._get_key(recording_id)
        client = await self._get_client()
        
        # Upload audio
        await client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=audio_data,
            ContentType="audio/wav",
            Metadata={
                "recording_id": recording_id,
                "call_id": metadata.call_id,
                "duration": str(metadata.duration_seconds),
            },
        )
        
        # Upload metadata
        meta_key = key.replace(".wav", ".json")
        await client.put_object(
            Bucket=self.bucket,
            Key=meta_key,
            Body=json.dumps(metadata.to_dict()),
            ContentType="application/json",
        )
        
        return f"s3://{self.bucket}/{key}"
    
    async def load(self, recording_id: str) -> Optional[bytes]:
        """Load recording from S3."""
        key = self._get_key(recording_id)
        client = await self._get_client()
        
        try:
            response = await client.get_object(Bucket=self.bucket, Key=key)
            return await response["Body"].read()
        except Exception:
            return None
    
    async def delete(self, recording_id: str) -> bool:
        """Delete recording from S3."""
        key = self._get_key(recording_id)
        client = await self._get_client()
        
        try:
            await client.delete_object(Bucket=self.bucket, Key=key)
            await client.delete_object(
                Bucket=self.bucket, 
                Key=key.replace(".wav", ".json"),
            )
            return True
        except Exception:
            return False
    
    async def get_url(self, recording_id: str, expires_in: int = 3600) -> Optional[str]:
        """Get presigned URL for S3 object."""
        key = self._get_key(recording_id)
        client = await self._get_client()
        
        try:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception:
            return None


class CallRecorder:
    """
    Real-time call recorder.
    
    Features:
    - Stream audio chunks during call
    - Automatic format handling
    - Consent management
    - Storage backend integration
    
    Example:
        recorder = CallRecorder(storage=LocalStorageBackend())
        
        # Start recording
        metadata = await recorder.start_recording(
            call_id="call_123",
            consent_status=ConsentStatus.GRANTED,
        )
        
        # Add audio chunks during call
        await recorder.add_audio(metadata.recording_id, chunk1)
        await recorder.add_audio(metadata.recording_id, chunk2)
        
        # Finish recording
        result = await recorder.stop_recording(metadata.recording_id)
        print(result.storage_url)  # Path to saved recording
    """
    
    def __init__(
        self,
        storage: Optional[StorageBackend] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        retention_days: int = 90,
    ):
        """
        Initialize call recorder.
        
        Args:
            storage: Storage backend (defaults to local)
            sample_rate: Audio sample rate
            channels: Number of audio channels
            retention_days: Days to retain recordings
        """
        self.storage = storage or LocalStorageBackend()
        self.sample_rate = sample_rate
        self.channels = channels
        self.retention_days = retention_days
        
        # Active recordings: recording_id -> (metadata, audio_buffer)
        self._active: Dict[str, tuple] = {}
        self._lock = asyncio.Lock()
    
    async def start_recording(
        self,
        call_id: str,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        caller_number: Optional[str] = None,
        callee_number: Optional[str] = None,
        consent_status: ConsentStatus = ConsentStatus.PENDING,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RecordingMetadata:
        """
        Start a new recording.
        
        Args:
            call_id: Associated call ID
            agent_id: AI agent ID
            user_id: User/account ID
            caller_number: Caller phone number
            callee_number: Called phone number
            consent_status: Recording consent status
            metadata: Additional metadata
        
        Returns:
            Recording metadata
        """
        recording_id = f"rec_{uuid.uuid4().hex}"
        
        rec_metadata = RecordingMetadata(
            recording_id=recording_id,
            call_id=call_id,
            agent_id=agent_id,
            user_id=user_id,
            caller_number=caller_number,
            callee_number=callee_number,
            started_at=datetime.now(timezone.utc),
            sample_rate=self.sample_rate,
            channels=self.channels,
            status=RecordingStatus.RECORDING,
            consent_status=consent_status,
            metadata=metadata or {},
        )
        
        async with self._lock:
            self._active[recording_id] = (rec_metadata, io.BytesIO())
        
        logger.info(f"Started recording {recording_id} for call {call_id}")
        return rec_metadata
    
    async def add_audio(
        self,
        recording_id: str,
        audio_chunk: bytes,
    ) -> bool:
        """
        Add audio chunk to active recording.
        
        Args:
            recording_id: Recording ID
            audio_chunk: Raw audio bytes (PCM)
        
        Returns:
            True if added successfully
        """
        async with self._lock:
            if recording_id not in self._active:
                logger.warning(f"Recording {recording_id} not found")
                return False
            
            metadata, buffer = self._active[recording_id]
            
            # Check consent
            if metadata.consent_status == ConsentStatus.DENIED:
                return False
            
            buffer.write(audio_chunk)
            return True
    
    async def stop_recording(
        self,
        recording_id: str,
    ) -> Optional[RecordingMetadata]:
        """
        Stop recording and save to storage.
        
        Args:
            recording_id: Recording ID
        
        Returns:
            Updated metadata with storage information
        """
        async with self._lock:
            if recording_id not in self._active:
                logger.warning(f"Recording {recording_id} not found")
                return None
            
            metadata, buffer = self._active.pop(recording_id)
        
        # Update metadata
        metadata.ended_at = datetime.now(timezone.utc)
        metadata.duration_seconds = (
            metadata.ended_at - metadata.started_at
        ).total_seconds()
        metadata.status = RecordingStatus.PROCESSING
        
        # Get audio data
        buffer.seek(0)
        raw_audio = buffer.read()
        
        if len(raw_audio) == 0:
            metadata.status = RecordingStatus.FAILED
            logger.warning(f"Recording {recording_id} has no audio data")
            return metadata
        
        # Convert to WAV format
        wav_data = self._create_wav(raw_audio)
        metadata.file_size_bytes = len(wav_data)
        
        # Save to storage
        try:
            storage_url = await self.storage.save(
                recording_id,
                wav_data,
                metadata,
            )
            metadata.storage_url = storage_url
            metadata.status = RecordingStatus.COMPLETED
            
            logger.info(
                f"Recording {recording_id} saved: "
                f"{metadata.duration_seconds:.1f}s, "
                f"{metadata.file_size_bytes} bytes"
            )
        except Exception as e:
            metadata.status = RecordingStatus.FAILED
            logger.error(f"Failed to save recording {recording_id}: {e}")
        
        return metadata
    
    async def cancel_recording(self, recording_id: str) -> bool:
        """Cancel an active recording without saving."""
        async with self._lock:
            if recording_id in self._active:
                del self._active[recording_id]
                logger.info(f"Cancelled recording {recording_id}")
                return True
        return False
    
    async def update_consent(
        self,
        recording_id: str,
        consent_status: ConsentStatus,
    ) -> bool:
        """
        Update consent status for a recording.
        
        If consent is denied, recording buffer is cleared.
        """
        async with self._lock:
            if recording_id not in self._active:
                return False
            
            metadata, buffer = self._active[recording_id]
            metadata.consent_status = consent_status
            
            if consent_status == ConsentStatus.DENIED:
                # Clear the buffer
                buffer.seek(0)
                buffer.truncate()
                logger.info(f"Consent denied for {recording_id}, buffer cleared")
            
            return True
    
    async def get_recording(
        self,
        recording_id: str,
    ) -> Optional[bytes]:
        """Get recording audio data from storage."""
        return await self.storage.load(recording_id)
    
    async def get_recording_url(
        self,
        recording_id: str,
        expires_in: int = 3600,
    ) -> Optional[str]:
        """Get URL to access recording."""
        return await self.storage.get_url(recording_id, expires_in)
    
    async def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording from storage."""
        return await self.storage.delete(recording_id)
    
    def _create_wav(self, raw_audio: bytes) -> bytes:
        """Create WAV file from raw PCM audio."""
        output = io.BytesIO()
        
        with wave.open(output, "wb") as wav:
            wav.setnchannels(self.channels)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(self.sample_rate)
            wav.writeframes(raw_audio)
        
        output.seek(0)
        return output.read()
    
    def get_active_recordings(self) -> List[str]:
        """Get list of active recording IDs."""
        return list(self._active.keys())


class RecordingManager:
    """
    High-level recording management.
    
    Features:
    - Recording lifecycle management
    - Retention policy enforcement
    - Search and filtering
    - Bulk operations
    """
    
    def __init__(
        self,
        recorder: Optional[CallRecorder] = None,
        storage: Optional[StorageBackend] = None,
    ):
        self.recorder = recorder or CallRecorder(storage=storage)
        self._recordings: Dict[str, RecordingMetadata] = {}
    
    async def start(
        self,
        call_id: str,
        **kwargs
    ) -> RecordingMetadata:
        """Start a new recording."""
        metadata = await self.recorder.start_recording(call_id, **kwargs)
        self._recordings[metadata.recording_id] = metadata
        return metadata
    
    async def stop(self, recording_id: str) -> Optional[RecordingMetadata]:
        """Stop a recording."""
        metadata = await self.recorder.stop_recording(recording_id)
        if metadata:
            self._recordings[recording_id] = metadata
        return metadata
    
    async def add_audio(self, recording_id: str, audio: bytes) -> bool:
        """Add audio to recording."""
        return await self.recorder.add_audio(recording_id, audio)
    
    def get_metadata(self, recording_id: str) -> Optional[RecordingMetadata]:
        """Get recording metadata."""
        return self._recordings.get(recording_id)
    
    def list_recordings(
        self,
        call_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[RecordingStatus] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[RecordingMetadata]:
        """List recordings with filtering."""
        results = []
        
        for rec in self._recordings.values():
            if call_id and rec.call_id != call_id:
                continue
            if user_id and rec.user_id != user_id:
                continue
            if status and rec.status != status:
                continue
            if since and rec.started_at < since:
                continue
            if until and rec.started_at > until:
                continue
            
            results.append(rec)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def cleanup_expired(
        self,
        retention_days: Optional[int] = None,
    ) -> int:
        """Delete recordings older than retention period."""
        days = retention_days or self.recorder.retention_days
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        deleted = 0
        for recording_id, metadata in list(self._recordings.items()):
            if metadata.started_at < cutoff:
                if await self.recorder.delete_recording(recording_id):
                    metadata.status = RecordingStatus.DELETED
                    deleted += 1
        
        logger.info(f"Cleaned up {deleted} expired recordings")
        return deleted


# Global recording manager
_global_manager: Optional[RecordingManager] = None


def get_recording_manager() -> RecordingManager:
    """Get or create global recording manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = RecordingManager()
    return _global_manager
