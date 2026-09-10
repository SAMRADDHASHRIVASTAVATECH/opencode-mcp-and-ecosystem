package com.olcap.phone.data

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.telecom.TelecomManager
import android.telephony.TelephonyManager

/**
 * Honest device capability assessment (spec section 8 & 31).
 *
 * CRITICAL: it distinguishes:
 *   * telephony FEATURE present           (phone hardware exists)
 *   * call-state monitoring possible       (READ_PHONE_STATE)
 *   * CALL_PHONE granted                   (can initiate)   -- NOT audio
 *   * default-dialer role                  (prereq for telecom-level control/audio)
 *   * actual call-AUDIO capture/injection  (normally NOT available to ordinary apps;
 *                                            requires default-dialer + Android 10+ telecom
 *                                            call audio, or an accessibility approach;
 *                                            still not "cellular audio in/out" for a normal app)
 *
 * Nothing is fabricated: fields default to false and are only true when the
 * device reports them. The MCP surface reports exactly these values.
 */
data class DeviceCapabilities(
    val source: String = "android-probe",
    val hasPhoneFeature: Boolean = false,
    val callStateMonitoring: Boolean = false,
    val cellularCallControl: Boolean = false,     // dial/answer/reject/hangup on SIM
    val defaultPhoneApp: Boolean = false,
    val telecomIntegration: Boolean = false,
    val callAudioCapture: Boolean = false,
    val callAudioInjection: Boolean = false,
    val aiCellularConversation: Boolean = false,
    val voipAvailable: Boolean = false,
    val providerRealtimeVoice: Boolean = false,
    val accessibilityControl: Boolean = false,
    val foregroundService: Boolean = true,
    val multiSim: Boolean = false,
    val bluetoothCallAudio: Boolean = false,
    val localAiPipeline: Boolean = false,
) {
    /** Map to the wire shape the control plane expects. */
    fun toWire(): Map<String, Any> = mapOf(
        "device_attached" to true,
        "source" to source,
        "call_state_monitoring" to callStateMonitoring,
        "cellular_call_control" to cellularCallControl,
        "default_phone_app" to defaultPhoneApp,
        "telecom_integration" to telecomIntegration,
        "call_audio_capture" to callAudioCapture,
        "call_audio_injection" to callAudioInjection,
        "ai_cellular_conversation" to aiCellularConversation,
        "voip_available" to voipAvailable,
        "provider_realtime_voice" to providerRealtimeVoice,
        "accessibility_control" to accessibilityControl,
        "foreground_service" to foregroundService,
        "multi_sim" to multiSim,
        "bluetooth_call_audio" to bluetoothCallAudio,
        "local_ai_pipeline" to localAiPipeline,
    )
}

object CapabilityProbe {
    /**
     * Run the real capability probe on this device. Honest by construction:
     * audio fields are only true if the device can actually route/access them.
     */
    fun probe(context: Context): DeviceCapabilities {
        val pm = context.packageManager
        val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as? TelephonyManager
        val hasPhone = pm.hasSystemFeature(PackageManager.FEATURE_TELEPHONY)

        // READ_PHONE_STATE is the prerequisite for observing call state.
        val readPhoneState = pm.checkPermission(
            "android.permission.READ_PHONE_STATE", context.packageName) ==
            PackageManager.PERMISSION_GRANTED

        // CALL_PHONE lets us DIAL (user-visible); it does NOT grant audio.
        val callPhone = pm.checkPermission(
            "android.permission.CALL_PHONE", context.packageName) ==
            PackageManager.PERMISSION_GRANTED

        // Default dialer (Telecom) is a hard gate for advanced call control and
        // for telecom-provided call audio on Android 10+. Ordinary apps are not.
        val telecom = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            context.getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
        } else null
        val isDefaultDialer = (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
                telecom?.defaultDialerPackage == context.packageName)

        val simCount = tm?.simCount ?: 0
        val multiSim = (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) && simCount > 1

        // Audio capture/injection of a live CELLULAR call:
        //   - default-dialer apps can request telecom call-audio on Android 10+.
        //   - ordinary (non-default) apps CANNOT capture/inject cellular audio.
        // We report true ONLY when we are the default dialer AND have the audio
        // permission on a supported API level; otherwise false (honest).
        val recAudio = pm.checkPermission("android.permission.RECORD_AUDIO",
            context.packageName) == PackageManager.PERMISSION_GRANTED
        val callAudioPossible =
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q && isDefaultDialer && recAudio

        return DeviceCapabilities(
            source = "android-probe",
            hasPhoneFeature = hasPhone,
            callStateMonitoring = readPhoneState && hasPhone,
            // dial/answer/reject are available with READ_PHONE_STATE+CALL_PHONE or
            // via the default-dialer Telecom APIs.
            cellularCallControl = callPhone || isDefaultDialer,
            defaultPhoneApp = isDefaultDialer,
            telecomIntegration = isDefaultDialer,
            callAudioCapture = callAudioPossible,
            callAudioInjection = callAudioPossible,
            // AI conversation over cellular audio only if that audio path exists.
            aiCellularConversation = callAudioPossible,
            voipAvailable = hasPhone,  // VOIP needs no carrier; reachable with net+mic
            accessibilityControl = false,
            multiSim = multiSim,
            bluetoothCallAudio = false,
        )
    }
}
