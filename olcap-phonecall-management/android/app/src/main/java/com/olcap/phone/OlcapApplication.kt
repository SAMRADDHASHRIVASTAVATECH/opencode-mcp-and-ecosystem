package com.olcap.phone

import android.app.Application

/**
 * OLCAP Phone Call Management application.
 *
 * The Android app is the AUTHORITATIVE source for phone state. It performs a
 * real capability probe, monitors call state, runs a foreground service, and
 * publishes state to the OLCAP control plane (the Python MCP layer) via the
 * configured bridge. The control plane then exposes phone.* tools to
 * OpenClaw/OpenCode.
 */
class OlcapApplication : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}
