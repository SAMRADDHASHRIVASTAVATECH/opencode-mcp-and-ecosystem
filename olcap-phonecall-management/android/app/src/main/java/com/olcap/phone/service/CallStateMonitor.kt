package com.olcap.phone.service

import android.content.Context
import android.telephony.PhoneStateListener
import android.telephony.TelephonyManager

/**
 * Observes device call state and forwards canonical transitions to a sink.
 *
 * This monitors SIM call state. It does NOT capture audio. Its purpose is to let
 * the control plane answer "what's happening with my phone calls?" and to drive
 * the call-state machine / events on the authoritative (Android) side.
 */
class CallStateMonitor(private val context: Context, private val sink: (Int, String) -> Unit) {

    private val tm: TelephonyManager?
        get() = context.getSystemService(Context.TELEPHONY_SERVICE) as? TelephonyManager
    private var listener: PhoneStateListener? = null

    fun start() {
        val tel = tm ?: return
        listener = object : PhoneStateListener() {
            override fun onCallStateChanged(state: Int, phoneNumber: String?) {
                val label = when (state) {
                    TelephonyManager.CALL_STATE_IDLE -> "IDLE"
                    TelephonyManager.CALL_STATE_RINGING -> "INCOMING_RINGING"
                    TelephonyManager.CALL_STATE_OFFHOOK -> "CALL_ACTIVE"
                    else -> "UNKNOWN"
                }
                sink(state, label)
            }
        }
        // READ_PHONE_STATE required; if not granted this simply reports nothing.
        try {
            listener?.let { tel.listen(it, PhoneStateListener.LISTEN_CALL_STATE) }
        } catch (e: SecurityException) {
            // Permission missing -> no monitoring; reported honestly via probe.
        }
    }

    fun stop() {
        val l = listener
        if (l != null) tm?.listen(l, PhoneStateListener.LISTEN_NONE)
        listener = null
    }
}
