package org.ukis.disaster.sms

import android.os.Build
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

data class PendingSmsTask(
    val smsId: String,
    val recipientPhone: String,
    val message: String,
    val targetCommunity: String,
    val hazardTier: String,
    val safeShelter: String?,
    val routeDirection: String?
)

class BackendApiClient(private val baseUrl: String = "http://10.0.2.2:8000") {

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    fun registerDevice(
        deviceId: String,
        carrierName: String,
        batteryPct: Int,
        signalStrengthBars: Int
    ): Boolean {
        val url = "$baseUrl/api/v1/telecom/android-gateway/register"
        val bodyJson = JSONObject().apply {
            put("device_id", deviceId)
            put("device_model", "${Build.MANUFACTURER} ${Build.MODEL}")
            put("android_version", "Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
            put("sim_carrier", carrierName)
            put("battery_pct", batteryPct)
            put("signal_strength_bars", signalStrengthBars)
            put("is_active", true)
        }

        val request = Request.Builder()
            .url(url)
            .post(bodyJson.toString().toRequestBody(jsonMediaType))
            .build()

        return try {
            client.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (e: Exception) {
            false
        }
    }

    fun fetchPendingSms(deviceId: String, limit: Int = 5): List<PendingSmsTask> {
        val url = "$baseUrl/api/v1/telecom/android-gateway/pending?device_id=$deviceId&limit=$limit"
        val request = Request.Builder().url(url).get().build()
        val tasks = mutableListOf<PendingSmsTask>()

        try {
            client.newCall(request).execute().use { response ->
                if (response.isSuccessful && response.body != null) {
                    val bodyString = response.body!!.string()
                    val jsonArray = JSONArray(bodyString)
                    for (i in 0 until jsonArray.length()) {
                        val obj = jsonArray.getJSONObject(i)
                        tasks.add(
                            PendingSmsTask(
                                smsId = obj.getString("sms_id"),
                                recipientPhone = obj.getString("recipient_phone"),
                                message = obj.getString("message"),
                                targetCommunity = obj.optString("target_community", "Uttarakhand"),
                                hazardTier = obj.optString("hazard_tier", "HIGH"),
                                safeShelter = if (obj.isNull("safe_shelter")) null else obj.getString("safe_shelter"),
                                routeDirection = if (obj.isNull("route_direction")) null else obj.getString("route_direction")
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            // Logged in caller
        }
        return tasks
    }

    fun acknowledgeDelivery(
        smsId: String,
        deviceId: String,
        status: String,
        carrierRef: String? = null,
        errorMessage: String? = null
    ): Boolean {
        val url = "$baseUrl/api/v1/telecom/android-gateway/ack"
        val bodyJson = JSONObject().apply {
            put("sms_id", smsId)
            put("device_id", deviceId)
            put("status", status)
            if (carrierRef != null) put("carrier_message_ref", carrierRef)
            if (errorMessage != null) put("error_message", errorMessage)
        }

        val request = Request.Builder()
            .url(url)
            .post(bodyJson.toString().toRequestBody(jsonMediaType))
            .build()

        return try {
            client.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (e: Exception) {
            false
        }
    }

    fun checkInSafe(
        phone: String,
        district: String,
        status: String = "SAFE",
        message: String? = null,
        linkedContacts: List<String> = emptyList()
    ): Boolean {
        val url = "$baseUrl/api/v1/citizen/check-in-safe"
        val bodyJson = JSONObject().apply {
            put("phone", phone)
            put("district", district)
            put("status", status)
            put("message", message ?: "Marked safe via Android App")
            put("linked_contacts", JSONArray(linkedContacts))
        }

        val request = Request.Builder()
            .url(url)
            .post(bodyJson.toString().toRequestBody(jsonMediaType))
            .build()

        return try {
            client.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (e: Exception) {
            false
        }
    }

    fun submitHazardReport(
        reporterPhone: String,
        district: String,
        hazardType: String,
        category: String,
        description: String,
        lat: Double,
        lon: Double
    ): Boolean {
        val url = "$baseUrl/api/v1/citizen/reports/submit"
        val bodyJson = JSONObject().apply {
            put("reporter_phone", reporterPhone)
            put("district", district)
            put("hazardType", hazardType)
            put("category", category)
            put("description", description)
            put("lat", lat)
            put("lon", lon)
        }

        val request = Request.Builder()
            .url(url)
            .post(bodyJson.toString().toRequestBody(jsonMediaType))
            .build()

        return try {
            client.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (e: Exception) {
            false
        }
    }
}
