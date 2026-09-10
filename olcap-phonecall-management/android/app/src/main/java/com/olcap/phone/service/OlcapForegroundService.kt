package com.olcap.phone.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.olcap.phone.MainActivity
import com.olcap.phone.R

/**
 * Foreground service that keeps the operator available while the phone is on,
 * within Android's permitted model. Shows the required persistent notification:
 * "OLCAP Phone Management: ACTIVE" plus status lines. Stops cleanly on
 * emergency stop / stop command.
 */
class OlcapForegroundService : Service() {

    private var monitor: CallStateMonitor? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startAsForeground()
        startMonitoring()
        return START_STICKY
    }

    private fun startAsForeground() {
        val channelId = "olcap_status"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val ch = NotificationChannel(channelId, "OLCAP Status",
                NotificationManager.IMPORTANCE_LOW)
            nm.createNotificationChannel(ch)
        }
        val launch = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE)
        val notif: Notification = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.drawable.ic_olcap)
            .setContentTitle(getString(R.string.active_label))
            .setContentText("Monitoring call state. No audio is captured.")
            .setOngoing(true)
            .setContentIntent(launch)
            .build()
        // phoneCall type requires FOREGROUND_SERVICE_PHONE_CALL permission.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notif, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_PHONE_CALL)
        } else {
            startForeground(1, notif)
        }
    }

    private fun startMonitoring() {
        val s = this
        monitor = CallStateMonitor(this) { state, label ->
            // Forward state to the control-plane bridge / persisted event log.
            BridgeClient.postEvent(s, "state_changed", mapOf("call_state" to label))
        }
        monitor?.start()
    }

    override fun onDestroy() {
        monitor?.stop()
        super.onDestroy()
    }
}
