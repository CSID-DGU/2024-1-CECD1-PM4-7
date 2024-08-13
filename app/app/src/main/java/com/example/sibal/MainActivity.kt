package com.example.sibal

import android.Manifest
import android.Manifest.permission.ANSWER_PHONE_CALLS
import android.app.role.RoleManager
import android.content.Context.ROLE_SERVICE
import android.content.Context.TELECOM_SERVICE
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.telecom.TelecomManager
import android.util.Log
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.ContextCompat.getSystemService

class MainActivity : AppCompatActivity() {
    val permissions = arrayOf(
        Manifest.permission.READ_PHONE_STATE,
        Manifest.permission.ANSWER_PHONE_CALLS,
        Manifest.permission.CALL_PHONE
    )

    override fun onCreate(savedInstancestate: Bundle?) {
        super.onCreate(savedInstancestate)
        Log.d("메인 액티비티", "메인 액티비티 실행")
        //퍼미션 런처 생성
        val permissionLauncher =
            registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted: Boolean ->
                if (!isGranted) {
                    Toast.makeText(this, "권한이 없다면 앱이 정상적으로 동작하지 않습니다.", Toast.LENGTH_SHORT).show()
                }
                //권한이 허용됐을 경우 앱 종료
                else {
                    finish()
                }
            }
        //퍼미션 런처 실행
        for(permission in permissions) {
            permissionLauncher.launch(permission)
        }

        val telecomManager = getSystemService(TELECOM_SERVICE) as TelecomManager
        val roleManager = getSystemService(ROLE_SERVICE) as RoleManager
        var intent: Intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_DIALER)
        
        //현재 앱을 기본 전화 앱으로 설정하도록 요청하는 런처 생성
        var requireDefualtDialerLauncher =
            registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
                val thisDefaultDialer = packageName == telecomManager.defaultDialerPackage
                if (!thisDefaultDialer) {
                    Toast.makeText(this, "기본 전화 앱 설정은 필수입니다.", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }

        //현재 앱이 기본 전화 앱이 아닐 경우 런처 실행
        if (packageName != telecomManager.defaultDialerPackage) {
            requireDefualtDialerLauncher.launch(intent)
        }
    }
}