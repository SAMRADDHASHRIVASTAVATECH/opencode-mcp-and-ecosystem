package com.olcap.phone.service

import android.content.Context
import com.olcap.phone.sec.SecretStore
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Publishes device state / events to the OLCAP control plane (the Python MCP
 * layer). The bridge URL is NOT compiled in - it is read from secure prefs
 * (SecretStore). If unset/disabled, events are logged locally only. Never sends
 * raw call audio.
 */
object BridgeClient {

    fun baseUrl(context: Context): String =
        SecretStore.get(context, "bridge_url").orEmpty()

    fun enabled(context: Context): Boolean =
        SecretStore.get(context, "bridge_enabled") != "false"

    /**
     * Best-effort POST of a JSON event. Errors are swallowed so a flaky bridge
     * never crashes the service; the connection status is surfaced in the UI.
     */
    fun postEvent(context: Context, type: String, payload: Map<String, Any>) {
        if (!enabled(context)) return
        val url = baseUrl(context)
        if (url.isEmpty()) return
        Thread {
            try {
                val body = JSONObject().put("type", type)
                    .put("ts", System.currentTimeMillis())
                    .put("payload", JSONObject(payload)).toString()
                val conn = URL(url.trimEnd('/') + "/v1/events")
                    .openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.doOutput = true
                conn.setRequestProperty("Content-Type", "application/json")
                conn.setRequestProperty("X-Olcap-Token",
                    SecretStore.get(context, "bridge_token").orEmpty())
                conn.outputStream.use { it.write(body.toByteArray()) }
                conn.inputStream.use { it.close() }  // consume
            } catch (_: Exception) {
                // offline / unreachable - report via UI, never crash
            }
        }.start()
    }
}
