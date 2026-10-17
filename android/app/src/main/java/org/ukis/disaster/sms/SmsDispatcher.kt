package org.ukis.disaster.sms

import android.app.Activity
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.telephony.SmsManager
import android.util.Log

class SmsDispatcher(private val context: Context) {

    companion object {
        private const val TAG = "UKIS_SMS_DISPATCHER"
        const val ACTION_SMS_SENT = "org.ukis.disaster.sms.ACTION_SMS_SENT"
        const val ACTION_SMS_DELIVERED = "org.ukis.disaster.sms.ACTION_SMS_DELIVERED"
        const val EXTRA_SMS_ID = "extra_sms_id"
    }

    private val smsManager: SmsManager by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            context.getSystemService(SmsManager::class.java)
        } else {
            @Suppress("DEPRECATION")
            SmsManager.getDefault()
        }
    }

    fun dispatchEmergencyMessage(
        task: PendingSmsTask,
        onResult: (success: Boolean, status: String, errorMsg: String?) -> Unit
    ) {
        try {
            val flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            } else {
                PendingIntent.FLAG_UPDATE_CURRENT
            }

            val sentIntent = Intent(ACTION_SMS_SENT).apply {
                putExtra(EXTRA_SMS_ID, task.smsId)
            }
            val sentPI = PendingIntent.getBroadcast(context, task.smsId.hashCode(), sentIntent, flags)

            val deliveredIntent = Intent(ACTION_SMS_DELIVERED).apply {
                putExtra(EXTRA_SMS_ID, task.smsId)
            }
            val deliveredPI = PendingIntent.getBroadcast(context, task.smsId.hashCode() + 1, deliveredIntent, flags)

            val parts = smsManager.divideMessage(task.message)

            if (parts.size > 1) {
                val sentIntents = ArrayList<PendingIntent>().apply { repeat(parts.size) { add(sentPI) } }
                val deliveredIntents = ArrayList<PendingIntent>().apply { repeat(parts.size) { add(deliveredPI) } }
                smsManager.sendMultipartTextMessage(
                    task.recipientPhone,
                    null,
                    parts,
                    sentIntents,
                    deliveredIntents
                )
            } else {
                smsManager.sendTextMessage(
                    task.recipientPhone,
                    null,
                    task.message,
                    sentPI,
                    deliveredPI
                )
            }

            Log.i(TAG, "Dispatched SMS ${task.smsId} to ${task.recipientPhone} across ${parts.size} part(s).")
            onResult(true, "SENT_RADIO_ACK", null)

        } catch (e: Exception) {
            Log.e(TAG, "Failed to dispatch SMS ${task.smsId}: ${e.message}", e)
            onResult(false, "FAILED", e.message)
        }
    }
}
