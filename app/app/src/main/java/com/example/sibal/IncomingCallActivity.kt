package com.example.sibal

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.util.Log
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.sibal.databinding.ActivityIncomingCallBinding

class IncomingCallActivity : AppCompatActivity() {

    private lateinit var binding: ActivityIncomingCallBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("IncomingCallActivity", "덮어 쓰기 화면 실행")
        binding = ActivityIncomingCallBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }
}
