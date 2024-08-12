package com.example.sibal

import android.os.Bundle
import android.os.Looper
import android.os.Handler
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.example.sibal.databinding.ActivityCallEndedBinding

class CallEndedActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("CallEndedActivity", "전화 종료 화면 실행")
        val binding = ActivityCallEndedBinding.inflate(layoutInflater)
        setContentView(binding.root)

        Handler(Looper.getMainLooper()).postDelayed({
            finish()
        }, 2000)
    }
}