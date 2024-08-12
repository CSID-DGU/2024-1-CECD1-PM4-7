package com.example.sibal

import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.telecom.TelecomManager
import android.util.Log
import android.view.MotionEvent
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.example.sibal.databinding.ActivityCallInProgressBinding

class CallInProgressActivity : AppCompatActivity() {
    private lateinit var telecomManager: TelecomManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("CallInProgressActivity", "전화 수신 화면 실행")
        val binding = ActivityCallInProgressBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val declineButton: ImageView = binding.decline2
        telecomManager = getSystemService(TELECOM_SERVICE) as TelecomManager

        declineButton.setOnTouchListener { v, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    (v as ImageView).setColorFilter(Color.argb(150, 0, 0, 0)) // 어두운 색 적용
                    true
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.ANSWER_PHONE_CALLS) == PackageManager.PERMISSION_GRANTED) {
                        Log.d("IncomingCallActivity", "전화 종료")
                        telecomManager.endCall()
                        val intent = Intent(this, CallEndedActivity::class.java)
                        startActivity(intent)
                        finish()
                    }
                    true
                }
                else -> false
            }
        }
    }
}