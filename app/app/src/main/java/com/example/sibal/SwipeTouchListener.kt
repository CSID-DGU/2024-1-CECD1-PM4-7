package com.example.sibal

import android.content.Context
import android.view.MotionEvent
import android.view.View
import kotlin.math.abs

class SwipeTouchListener(ctx: Context, val onSwipe: () -> Unit) : View.OnTouchListener {

    private var downX: Float = 0f
    private var downY: Float = 0f

    override fun onTouch(view: View, motionEvent: MotionEvent): Boolean {
        when (motionEvent.action) {
            MotionEvent.ACTION_DOWN -> {
                downX = motionEvent.x
                downY = motionEvent.y
                return true
            }
            MotionEvent.ACTION_UP -> {
                val deltaX = motionEvent.x - downX
                val deltaY = motionEvent.y - downY

                if (abs(deltaX) > abs(deltaY) && abs(deltaX) > SWIPE_THRESHOLD) {
                    onSwipe()
                    return true
                }
            }
        }
        return false
    }

    companion object {
        private const val SWIPE_THRESHOLD = 100
    }
}