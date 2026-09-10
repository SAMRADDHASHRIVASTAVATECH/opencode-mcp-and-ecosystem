"""Bluetooth HFP (Hands-Free Profile) manager for Windows.

Manages the Bluetooth HFP connection between Windows and Android phone,
providing digital bidirectional audio path for AI voice calls.
"""
from __future__ import annotations

import asyncio
import logging
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class HFPState(Enum):
    """HFP connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUDIO_ACTIVE = "audio_active"
    ERROR = "error"


@dataclass
class HFPDeviceInfo:
    """Bluetooth HFP device information."""
    name: str
    address: str
    hfp_available: bool = False
    audio_in_endpoint: Optional[str] = None  # Microphone (uplink to phone)
    audio_out_endpoint: Optional[str] = None  # Speaker (downlink from phone)
    connected: bool = False
    state: HFPState = HFPState.DISCONNECTED


@dataclass
class AudioEndpoints:
    """Windows audio endpoint information."""
    hfp_speaker_name: str = ""
    hfp_speaker_id: str = ""
    hfp_microphone_name: str = ""
    hfp_microphone_id: str = ""
    speaker_available: bool = False
    microphone_available: bool = False


class BluetoothHFPManager:
    """Manages Bluetooth HFP connection and audio routing.
    
    This class provides:
    - Device discovery and pairing
    - HFP connection management
    - Audio endpoint detection
    - Audio routing for TTS (uplink) and STT (downlink)
    """
    
    def __init__(self, adb_serial: Optional[str] = None):
        self.adb_serial = adb_serial
        self._state = HFPState.DISCONNECTED
        self._device_info: Optional[HFPDeviceInfo] = None
        self._audio_endpoints = AudioEndpoints()
        self._state_callbacks: list[Callable[[HFPState], None]] = []
        self._monitor_task: Optional[asyncio.Task] = None
        
    @property
    def state(self) -> HFPState:
        return self._state
    
    @property
    def device_info(self) -> Optional[HFPDeviceInfo]:
        return self._device_info
    
    @property
    def audio_endpoints(self) -> AudioEndpoints:
        return self._audio_endpoints
    
    def on_state_change(self, callback: Callable[[HFPState], None]):
        """Register a callback for state changes."""
        self._state_callbacks.append(callback)
    
    def _set_state(self, new_state: HFPState):
        """Update state and notify callbacks."""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            logger.info(f"HFP state: {old_state.value} -> {new_state.value}")
            for cb in self._state_callbacks:
                try:
                    cb(new_state)
                except Exception as e:
                    logger.error(f"State callback error: {e}")
    
    async def discover_android_device(self) -> Optional[HFPDeviceInfo]:
        """Discover Android device via ADB and get Bluetooth info."""
        try:
            # Get device info via ADB
            cmd = ["adb"]
            if self.adb_serial:
                cmd.extend(["-s", self.adb_serial])
            cmd.extend(["shell", "dumpsys", "bluetooth_manager"])
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            output = stdout.decode("utf-8", errors="ignore")
            
            # Parse Bluetooth info
            device_name = ""
            device_address = ""
            hfp_available = False
            
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Name:"):
                    device_name = line.split(":", 1)[1].strip()
                elif line.startswith("Address:"):
                    device_address = line.split(":", 1)[1].strip()
                elif "HeadsetService" in line:
                    hfp_available = True
            
            if device_name and device_address:
                self._device_info = HFPDeviceInfo(
                    name=device_name,
                    address=device_address,
                    hfp_available=hfp_available
                )
                logger.info(f"Discovered Android: {device_name} ({device_address}), HFP: {hfp_available}")
                return self._device_info
            
            return None
            
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return None
    
    async def check_hfp_connection(self) -> bool:
        """Check if HFP is currently connected."""
        try:
            cmd = ["adb"]
            if self.adb_serial:
                cmd.extend(["-s", self.adb_serial])
            cmd.extend(["shell", "dumpsys", "bluetooth_manager"])
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            output = stdout.decode("utf-8", errors="ignore")
            
            # Check HeadsetService state
            in_headset_service = False
            for line in output.splitlines():
                if "Profile: HeadsetService" in line:
                    in_headset_service = True
                elif in_headset_service:
                    if "mActiveDevice:" in line and "null" not in line:
                        return True
                    elif "mVirtualCallStarted: true" in line:
                        return True
                    elif line.startswith("Profile:") or line.startswith("---"):
                        break
            
            return False
            
        except Exception as e:
            logger.error(f"HFP connection check failed: {e}")
            return False
    
    async def get_windows_audio_endpoints(self) -> AudioEndpoints:
        """Discover Windows Bluetooth HFP audio endpoints."""
        try:
            # Get audio endpoints via PowerShell
            cmd = [
                "powershell", "-Command",
                "Get-PnpDevice -Class AudioEndpoint | Where-Object { $_.FriendlyName -match 'ManaDrive.*Hands-Free' } | Select-Object FriendlyName, Status, InstanceId | ConvertTo-Json"
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            import json
            devices = json.loads(stdout.decode("utf-8", errors="ignore"))
            
            if not isinstance(devices, list):
                devices = [devices]
            
            endpoints = AudioEndpoints()
            
            for device in devices:
                name = device.get("FriendlyName", "")
                instance_id = device.get("InstanceId", "")
                status = device.get("Status", "")
                
                if "Speakers" in name and "Hands-Free" in name:
                    endpoints.hfp_speaker_name = name
                    endpoints.hfp_speaker_id = instance_id
                    endpoints.speaker_available = status in ("OK", "Degraded")
                    logger.info(f"HFP Speaker: {name} (Status: {status})")
                elif "Microphone" in name and "Hands-Free" in name:
                    endpoints.hfp_microphone_name = name
                    endpoints.hfp_microphone_id = instance_id
                    endpoints.microphone_available = status in ("OK", "Degraded")
                    logger.info(f"HFP Microphone: {name} (Status: {status})")
            
            self._audio_endpoints = endpoints
            return endpoints
            
        except Exception as e:
            logger.error(f"Audio endpoint discovery failed: {e}")
            return AudioEndpoints()
    
    async def activate_hfp_connection(self) -> bool:
        """Activate the HFP connection from Windows to Android."""
        try:
            # Check if already connected
            if await self.check_hfp_connection():
                logger.info("HFP already connected")
                self._set_state(HFPState.CONNECTED)
                return True
            
            self._set_state(HFPState.CONNECTING)
            
            # Try to connect via Windows Bluetooth
            # First, check if device is paired
            cmd = [
                "powershell", "-Command",
                "Get-PnpDevice -Class Bluetooth | Where-Object { $_.FriendlyName -match 'ManaDrive' -and $_.InstanceId -match 'BTHENUM' } | Select-Object -First 1 | ForEach-Object { $_.InstanceId }"
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            device_id = stdout.decode("utf-8", errors="ignore").strip()
            
            if not device_id:
                logger.error("No paired Android device found")
                self._set_state(HFPState.ERROR)
                return False
            
            # Enable the device to activate HFP
            cmd = [
                "powershell", "-Command",
                f"Enable-PnpDevice -InstanceId '{device_id}' -Confirm:$false"
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.warning(f"Enable-PnpDevice returned non-zero: {stderr.decode()}")
            
            # Wait for connection
            for _ in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)
                if await self.check_hfp_connection():
                    self._set_state(HFPState.CONNECTED)
                    logger.info("HFP connection activated successfully")
                    return True
            
            logger.warning("HFP connection timeout")
            self._set_state(HFPState.DISCONNECTED)
            return False
            
        except Exception as e:
            logger.error(f"HFP activation failed: {e}")
            self._set_state(HFPState.ERROR)
            return False
    
    async def deactivate_hfp_connection(self) -> bool:
        """Deactivate the HFP connection."""
        try:
            # Disable the device
            cmd = [
                "powershell", "-Command",
                "Get-PnpDevice -Class Bluetooth | Where-Object { $_.FriendlyName -match 'ManaDrive' -and $_.InstanceId -match 'BTHENUM' } | Select-Object -First 1 | ForEach-Object { Disable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false }"
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            self._set_state(HFPState.DISCONNECTED)
            logger.info("HFP connection deactivated")
            return True
            
        except Exception as e:
            logger.error(f"HFP deactivation failed: {e}")
            return False
    
    async def start_monitoring(self, interval: float = 5.0):
        """Start monitoring HFP connection state."""
        async def monitor_loop():
            while True:
                try:
                    # Check Android side
                    hfp_connected = await self.check_hfp_connection()
                    
                    # Check Windows side
                    endpoints = await self.get_windows_audio_endpoints()
                    
                    if hfp_connected and endpoints.speaker_available and endpoints.microphone_available:
                        if self._state != HFPState.AUDIO_ACTIVE:
                            self._set_state(HFPState.AUDIO_ACTIVE)
                    elif hfp_connected:
                        if self._state != HFPState.CONNECTED:
                            self._set_state(HFPState.CONNECTED)
                    else:
                        if self._state not in (HFPState.DISCONNECTED, HFPState.CONNECTING):
                            self._set_state(HFPState.DISCONNECTED)
                            
                except Exception as e:
                    logger.error(f"Monitor error: {e}")
                
                await asyncio.sleep(interval)
        
        self._monitor_task = asyncio.create_task(monitor_loop())
    
    async def stop_monitoring(self):
        """Stop monitoring HFP connection state."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
    
    async def get_capability_report(self) -> dict:
        """Get a comprehensive capability report."""
        # Discover device
        device = await self.discover_android_device()
        
        # Check HFP connection
        hfp_connected = await self.check_hfp_connection()
        
        # Get audio endpoints
        endpoints = await self.get_windows_audio_endpoints()
        
        return {
            "android_device": {
                "name": device.name if device else None,
                "address": device.address if device else None,
                "hfp_available": device.hfp_available if device else False,
                "connected": hfp_connected
            },
            "windows_endpoints": {
                "hfp_speaker": endpoints.hfp_speaker_name,
                "hfp_speaker_available": endpoints.speaker_available,
                "hfp_microphone": endpoints.hfp_microphone_name,
                "hfp_microphone_available": endpoints.microphone_available
            },
            "bridge_state": self._state.value,
            "full_duplex_capable": (
                hfp_connected and 
                endpoints.speaker_available and 
                endpoints.microphone_available
            )
        }


def create_hfp_manager(adb_serial: Optional[str] = None) -> BluetoothHFPManager:
    """Create a Bluetooth HFP manager instance."""
    return BluetoothHFPManager(adb_serial=adb_serial)
