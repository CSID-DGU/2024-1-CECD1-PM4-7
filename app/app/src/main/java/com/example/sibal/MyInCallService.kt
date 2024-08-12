package com.example.sibal

import android.content.Intent
import android.telecom.Call
import android.telecom.InCallService

class MyInCallService : InCallService() {

    override fun onCallAdded(call: Call) {
        super.onCallAdded(call)

        val intent = Intent(this, IncomingCallActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent)
    }

    override fun onCallRemoved(call: Call) {
        super.onCallRemoved(call)
    }
}