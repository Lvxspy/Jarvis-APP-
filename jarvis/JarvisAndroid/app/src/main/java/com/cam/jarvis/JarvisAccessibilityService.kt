package com.cam.jarvis

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

/**
 * Este es el único trozo de Jarvis que necesita el permiso de
 * Accesibilidad: WhatsApp no tiene una forma oficial de "enviar un
 * mensaje sin que el usuario toque el botón", así que esto simula
 * ese toque por ti, DESPUÉS de que MainActivity ya dejó el mensaje
 * escrito en el chat correcto.
 *
 * Solo actúa cuando mensajePendienteAEnviar está en true (es decir,
 * justo después de que Jarvis te mandó a abrir un chat de WhatsApp
 * por voz) — nunca toca nada por su cuenta en otro momento.
 */
class JarvisAccessibilityService : AccessibilityService() {

    companion object {
        var mensajePendienteAEnviar = false
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (!mensajePendienteAEnviar) return
        if (event == null) return
        if (event.packageName?.toString() != "com.whatsapp") return

        val raiz = rootInActiveWindow ?: return
        val boton = buscarBotonEnviar(raiz)
        if (boton != null) {
            boton.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            mensajePendienteAEnviar = false
        }
    }

    private fun buscarBotonEnviar(nodo: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        // Intento 1: el id que WhatsApp ha usado históricamente para
        // el botón de enviar.
        val porId = nodo.findAccessibilityNodeInfosByViewId("com.whatsapp:id/send")
        if (porId.isNotEmpty()) return porId[0]

        // Intento 2 (respaldo): por si WhatsApp cambió el id en una
        // actualización, busca por descripción del botón.
        return buscarPorDescripcion(nodo)
    }

    private fun buscarPorDescripcion(nodo: AccessibilityNodeInfo?): AccessibilityNodeInfo? {
        if (nodo == null) return null
        val descripcion = nodo.contentDescription?.toString()?.lowercase() ?: ""
        if (nodo.isClickable && (descripcion.contains("enviar") || descripcion.contains("send"))) {
            return nodo
        }
        for (i in 0 until nodo.childCount) {
            val hijo = nodo.getChild(i) ?: continue
            val encontrado = buscarPorDescripcion(hijo)
            if (encontrado != null) return encontrado
        }
        return null
    }

    override fun onInterrupt() {}
}
