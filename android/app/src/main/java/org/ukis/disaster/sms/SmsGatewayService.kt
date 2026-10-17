package org.ukis.disaster.sms

import android.app.*
import android.content.Context
import android.content.Intent
import android.os.BatteryManager
import android.os.Build
import android.os.IBinder
import android.telephony.TelephonyManager
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*
import java.util.UUID

class SmsGatewayService : Service() {

    companion object {
        private const val TAG = "UKIS_GATEWAY_SERVICE"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "ukis_sms_gateway_channel"
        const val ACTION_START = "ACTION_START"
        const val ACTION_STOP = "ACTION_STOP"
    }

    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private lateinit var apiClient: BackendApiClient
    private lateinit var smsDispatcher: SmsDispatcher
    private var isRunning = false
    private var deviceId: String = ""

    override fun onCreate() {
        super.onCreate()
        apiClient = BackendApiClient()
        smsDispatcher = SmsDispatcher(this)
        deviceId = getOrCreateDeviceId()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> stopGateway()
            else -> startGateway()
        }
        return START_STICKY
    }

    private fun startGateway() {
        if (isRunning) return
        isRunning = true

        val notification = buildForegroundNotification("Cellular Gateway Active — Monitoring EOC Dispatch Queue")
        startForeground(NOTIFICATION_ID, notification)

        serviceScope.launch {
            Log.i(TAG, "Starting Android SMS Gateway polling loop for device: $deviceId")

            while (isRunning && isActive) {
                try {
                    val carrierName = getSimCarrierName()
                    val batteryLevel = getBatteryLevel()

                    // 1. Heartbeat & Registration
                    apiClient.registerDevice(
                        deviceId = deviceId,
                        carrierName = carrierName,
                        batteryPct = batteryLevel,
                        signalStrengthBars = 4
                    )

                    // 2. Fetch pending emergency tasks
                    val tasks = apiClient.fetchPendingSms(deviceId, limit = 3)
                    for (task in tasks) {
                        Log.w(TAG, "EMERGENCY DISPATCH TRIGGERED: SMS ${task.smsId} -> ${task.recipientPhone}")
                        smsDispatcher.dispatchEmergencyMessage(task) { success, status, errorMsg ->
                            apiClient.acknowledgeDelivery(
                                smsId = task.smsId,
                                deviceId = deviceId,
                                status = if (success) "DELIVERED" else "FAILED",
                                carrierRef = "SIM-${UUID.randomUUID().toString().take(6).uppercase()}",
                                errorMessage = errorMsg
                            )
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error in polling loop: ${e.message}")
                }

                // Poll interval: 5.0 seconds
                delay(5000)
            }
        }
    }

    private fun stopGateway() {
        isRunning = false
        serviceScope.cancel()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "UKIS Disaster SMS Gateway Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "24/7 background relay for emergency Uttarakhand disaster SMS broadcasts"
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildForegroundNotification(content: String): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("UKIS Mountain Disaster SMS Relay")
            .setContentText(content)
            .setSmallIcon(android.R.drawable.stat_sys_warning)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build()
    }

    private fun getOrCreateDeviceId(): String {
        val prefs = getSharedPreferences("ukis_gateway_prefs", Context.MODE_PRIVATE)
        var id = prefs.getString("device_id", null)
        if (id == null) {
            id = "AND-GW-" + UUID.randomUUID().toString().take(8).uppercase()
            prefs.edit().putString("device_id", id).apply()
        }
        return id
    }

    private fun getSimCarrierName(): String {
        return try {
            val tm = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
            val name = tm.simOperatorName
            if (!name.isNullOrBlank()) name else "BSNL Mobile / Regional Indian SIM"
        } catch (e: Exception) {
            "BSNL Mobile"
        }
    }

    private fun getBatteryLevel(): Int {
        return try {
            val bm = getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        } catch (e: Exception) {
            95
        }
    }

    override fun onDestroy() {
        stopGateway()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
