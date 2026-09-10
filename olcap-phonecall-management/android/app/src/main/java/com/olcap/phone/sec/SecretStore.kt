package com.olcap.phone.sec

import android.content.Context
import android.content.SharedPreferences

/**
 * Minimal secure-value store. For real deployments, keys/tokens/bridge URL
 * should live in Android Keystore-backed encrypted prefs (EncryptedSharedPreferences).
 * No secret is ever put into source code.
 */
object SecretStore {
    private const val PREFS = "olcap_secrets"

    private fun p(context: Context): SharedPreferences =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun set(context: Context, key: String, value: String) {
        p(context).edit().putString(key, value).apply()
    }

    fun get(context: Context, key: String): String? = p(context).getString(key, null)
}
