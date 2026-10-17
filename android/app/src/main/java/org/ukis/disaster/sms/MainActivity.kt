package org.ukis.disaster.sms

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.telephony.TelephonyManager
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    companion object {
        private const val PERMISSION_REQUEST_CODE = 2001
    }

    private lateinit var tvStatus: TextView
    private lateinit var tvCarrier: TextView
    private lateinit var tvServer: TextView
    private lateinit var tvLogs: TextView
    private lateinit var btnToggle: Button
    private lateinit var btnSos: Button

    private var isServiceActive = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvStatus = findViewById(R.id.tvStatus)
        tvCarrier = findViewById(R.id.tvCarrier)
        tvServer = findViewById(R.id.tvServer)
        tvLogs = findViewById(R.id.tvLogs)
        btnToggle = findViewById(R.id.btnToggle)
        btnSos = findViewById(R.id.btnSos)

        // Native 112 SOS Intent trigger
        btnSos.setOnClickListener {
            try {
                val dialIntent = Intent(Intent.ACTION_DIAL).apply {
                    data = Uri.parse("tel:112")
                }
                startActivity(dialIntent)
            } catch (e: Exception) {
                Toast.makeText(this, "Emergency dialer trigger: Dial 112", Toast.LENGTH_LONG).show()
            }
        }

        checkAndRequestPermissions()
        displayCarrierInfo()

        btnToggle.setOnClickListener {
            if (isServiceActive) {
                stopRelayService()
            } else {
                startRelayService()
            }
        }
    }

    /**
     * Clear permission rationale flow:
     * Never request POST_NOTIFICATIONS or Location silently on first launch.
     * Explain exact public safety and DPDP purpose limitation prior to system dialog.
     */
    private fun checkAndRequestPermissions() {
        val permissions = mutableListOf(
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_PHONE_STATE,
            Manifest.permission.INTERNET,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        val needed = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }

        if (needed.isNotEmpty()) {
            AlertDialog.Builder(this)
                .setTitle("DMMC Uttarakhand Public Safety Authorization")
                .setMessage(
                    "To protect lives during Himalayan natural disasters (Flash floods, Landslides, Cloudbursts, and Earthquakes), DMMC requires:\n\n" +
                    "1. Critical Notifications: To deliver emergency alert sirens even when device is locked.\n\n" +
                    "2. Location Tracking: To match your position against active hazard polygons and evacuation zones.\n\n" +
                    "Protected under India's DPDP Act 2023. Grant authorization?"
                )
                .setPositiveButton("GRANT PERMISSIONS") { _, _ ->
                    ActivityCompat.requestPermissions(this, needed.toTypedArray(), PERMISSION_REQUEST_CODE)
                }
                .setNegativeButton("LATER") { dialog, _ ->
                    dialog.dismiss()
                    appendLog("[SECURITY] Permissions deferred. Manual mountain district selection active.")
                }
                .setCancelable(false)
                .show()
        }
    }

    private fun displayCarrierInfo() {
        try {
            val tm = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
            val carrier = tm.simOperatorName.ifBlank { "BSNL Uttarakhand Telecom (SIM 1)" }
            tvCarrier.text = "Active Cellular SIM: $carrier"
            tvServer.text = "Central EOC Endpoint: http://10.0.2.2:8000"
        } catch (e: Exception) {
            tvCarrier.text = "Active Cellular SIM: Regional Mobile SIM"
        }
    }

    private fun startRelayService() {
        val intent = Intent(this, SmsGatewayService::class.java).apply {
            action = SmsGatewayService.ACTION_START
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        isServiceActive = true
        tvStatus.text = "STATUS: ONLINE (Cellular SIM Polling Active)"
        tvStatus.setTextColor(0xFF16A34A.toInt()) // Green
        btnToggle.text = "STOP CELLULAR RELAY"
        appendLog("[SYSTEM] Started physical SMS gateway background service.")
        Toast.makeText(this, "Android SMS Gateway Activated", Toast.LENGTH_SHORT).show()
    }

    private fun stopRelayService() {
        val intent = Intent(this, SmsGatewayService::class.java).apply {
            action = SmsGatewayService.ACTION_STOP
        }
        startService(intent)
        isServiceActive = false
        tvStatus.text = "STATUS: STANDBY"
        tvStatus.setTextColor(0xFFDC2626.toInt()) // Red
        btnToggle.text = "START CELLULAR RELAY"
        appendLog("[SYSTEM] Stopped background SMS service.")
    }

    private fun appendLog(msg: String) {
        val current = tvLogs.text.toString()
        tvLogs.text = "$msg\n$current".take(2000)
    }
}
