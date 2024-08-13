package com.example.sibal

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.Intent
import android.content.pm.PackageManager
import android.content.res.Resources
import android.os.Bundle
import android.telecom.TelecomManager
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.example.sibal.databinding.ActivityIncomingCallBinding

class IncomingCallActivity : AppCompatActivity() {
    private var parentWidth: Int = 0
    private lateinit var telecomManager: TelecomManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("IncomingCallActivity", "전화가 걸려왔을 때 화면 실행")
        val binding = ActivityIncomingCallBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val acceptButton = binding.accept
        val declineButton = binding.decline

        setupButtonDrag(acceptButton, true)
        setupButtonDrag(declineButton, false)

        parentWidth = Resources.getSystem().displayMetrics.widthPixels
        telecomManager = getSystemService(TELECOM_SERVICE) as TelecomManager
    }

    private fun setupButtonDrag(button: ImageView, isAcceptButton: Boolean) {
        var dX = 0f
        var initialX = 0f

        button.setOnTouchListener { view, event ->
            when (event.action) {
                //버튼을 눌렀을 때
                MotionEvent.ACTION_DOWN -> {
                    initialX = view.x  //버튼의 초기 위치 저장
                    dX = view.x - event.rawX  //버튼 이동 거리

                    view.animate()
                        .scaleX(1.3f)
                        .scaleY(1.3f)
                        .setDuration(0)
                        .start()
                    true
                }

                //버튼을 드래그 했을 때
                MotionEvent.ACTION_MOVE -> {
                    view.animate()
                        .x(event.rawX + dX)
                        .setDuration(0)
                        .start()

                    //전화 수신 버튼을 화면의 오른쪽으로 충분히 이동 시켰을 경우 -> 전화 수신
                    if (isAcceptButton && view.x > parentWidth * 0.4) {
                        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.ANSWER_PHONE_CALLS) == PackageManager.PERMISSION_GRANTED) {
                            Log.d("IncomingCallActivity", "전화 수신")
                            telecomManager.acceptRingingCall()
                            val intent = Intent(this, CallInProgressActivity::class.java)
                            startActivity(intent)
                            finish()
                        }

                    //전화 거절 버튼을 화면의 왼쪽으로 충분히 이동 시켰을 경우 -> 전화 종료
                    } else if (!isAcceptButton && view.x < parentWidth * 0.6) {
                        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.ANSWER_PHONE_CALLS) == PackageManager.PERMISSION_GRANTED) {
                            Log.d("IncomingCallActivity", "전화 종료")
                            telecomManager.endCall()
                            val intent = Intent(this, CallEndedActivity::class.java)
                            startActivity(intent)
                            finish()
                        }
                    }
                    true
                }

                //버튼을 땟을 때 -> 버튼이 제자리로 돌아감
                MotionEvent.ACTION_UP -> {
                        //버튼 위치를 원래대로 되돌리는 애니메이션
                        val moveBackAnim = ObjectAnimator.ofFloat(view, "x", initialX)
                        
                        //버튼 크기를 원래대로 되돌리는 애니메이션
                        val scaleBackXAnim = ObjectAnimator.ofFloat(view, "scaleX", 1f)
                        val scaleBackYAnim = ObjectAnimator.ofFloat(view, "scaleY", 1f)

                        //애니메이션 동시 실행
                        val animatorSet = AnimatorSet()
                        animatorSet.playTogether(moveBackAnim, scaleBackXAnim, scaleBackYAnim)
                        animatorSet.duration - 300
                        animatorSet.start()
                    true
                }
                else -> false
            }
        }
    }
}
