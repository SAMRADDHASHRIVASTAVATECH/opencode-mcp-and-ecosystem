package com.olcap.phone

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.olcap.phone.data.CapabilityProbe
import com.olcap.phone.service.OlcapForegroundService
import com.olcap.phone.ui.StatusRow
import com.olcap.phone.ui.theme.OlcapTheme

/**
 * OLCAP status screen. Shows honest status readouts (PHONE / MCP / Telephony /
 * AI Voice / SIMs / ACTIVE CALL / AUTONOMOUS ANSWERING), Start/Stop service,
 * Emergency Stop, and diagnostics. It does NOT claim abilities the device lacks.
 */
class MainActivity : ComponentActivity() {

    private val permLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        maybeRequestPermissions()

        setContent {
            OlcapTheme {
                val caps = remember { CapabilityProbe.probe(this) }
                Column(Modifier.padding(16.dp)) {
                    Text("OLCAP Phone Management",
                        style = MaterialTheme.typography.headlineSmall)
                    Spacer(Modifier.height(8.dp))
                    StatusRow("PHONE", if (caps.hasPhoneFeature) "Connected" else "No phone")
                    StatusRow("Telephony (monitor)",
                        if (caps.callStateMonitoring) "Available" else "Unavailable")
                    StatusRow("Telephony (control)",
                        if (caps.cellularCallControl) "Available" else "Limited")
                    StatusRow("Call audio (capture/inject)",
                        if (caps.callAudioCapture) "Available" else "Unavailable on this device")
                    StatusRow("Default dialer",
                        if (caps.defaultPhoneApp) "Yes" else "No")
                    StatusRow("AI Voice", if (caps.aiCellularConversation)
                        "Cellular path" else "Via provider/VoIP only")
                    StatusRow("ACTIVE CALL", "None")
                    StatusRow("AUTONOMOUS ANSWERING", "Disabled")
                    Spacer(Modifier.height(16.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { startService() }) {
                            Text("Start service") }
                        OutlinedButton(onClick = { stopService() }) {
                            Text("Stop") }
                    }
                    Spacer(Modifier.height(8.dp))
                    Button(
                        onClick = {
                            // Emergency stop: halt autonomous calling on this phone.
                            stopService()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                    ) { Text("EMERGENCY STOP") }
                }
            }
        }
    }

    private fun startService() {
        val svc = Intent(this, OlcapForegroundService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(svc)
        else startService(svc)
    }

    private fun stopService() {
        stopService(Intent(this, OlcapForegroundService::class.java))
    }

    private fun maybeRequestPermissions() {
        val needed = mutableListOf(
            Manifest.permission.READ_PHONE_STATE,
            Manifest.permission.CALL_PHONE,
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.READ_CALL_LOG,
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            needed.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val missing = needed.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            permLauncher.launch(missing.toTypedArray())
        }
    }
}
