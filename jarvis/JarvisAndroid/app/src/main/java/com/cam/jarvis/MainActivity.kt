package com.cam.jarvis

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale
import kotlin.concurrent.thread

/**
 * Pantalla principal: mic + campo de texto + respuesta. Habla con
 * server.py (el cerebro que corre en el PC) y, si la respuesta trae
 * una "accion", la ejecuta aquí mismo en el celular (abrir una app,
 * abrir Spotify en una canción, o mandar un WhatsApp).
 */
class MainActivity : Activity(), TextToSpeech.OnInitListener {

    private lateinit var prefs: SharedPreferences
    private lateinit var campoServidor: EditText
    private lateinit var campoTexto: EditText
    private lateinit var textoRespuesta: TextView
    private var tts: TextToSpeech? = null

    companion object {
        const val CODIGO_VOZ = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences("jarvis", Context.MODE_PRIVATE)
        tts = TextToSpeech(this, this)

        campoServidor = findViewById(R.id.campoServidor)
        campoTexto = findViewById(R.id.campoTexto)
        textoRespuesta = findViewById(R.id.textoRespuesta)

        // Recuerda la última IP que usaste, para no tener que
        // escribirla cada vez que abres la app.
        campoServidor.setText(prefs.getString("servidor", "http://192.168.1.5:5000"))

        findViewById<Button>(R.id.btnHablar).setOnClickListener { iniciarReconocimientoDeVoz() }

        findViewById<Button>(R.id.btnEnviar).setOnClickListener {
            val texto = campoTexto.text.toString().trim()
            if (texto.isNotEmpty()) {
                enviarComando(texto)
                campoTexto.setText("")
            }
        }

        findViewById<Button>(R.id.btnAccesibilidad).setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts?.language = Locale("es", "ES")
        }
    }

    private fun iniciarReconocimientoDeVoz() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES")
        try {
            @Suppress("DEPRECATION")
            startActivityForResult(intent, CODIGO_VOZ)
        } catch (e: Exception) {
            Toast.makeText(this, "Este celular no tiene reconocimiento de voz disponible.", Toast.LENGTH_LONG).show()
        }
    }

    @Suppress("DEPRECATION")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == CODIGO_VOZ && resultCode == Activity.RESULT_OK) {
            val resultados = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            val texto = resultados?.firstOrNull()
            if (texto != null) {
                textoRespuesta.text = "Dijiste: \"$texto\""
                enviarComando(texto)
            }
        }
    }

    private fun enviarComando(texto: String) {
        val servidor = campoServidor.text.toString().trim().trimEnd('/')
        prefs.edit().putString("servidor", servidor).apply()

        textoRespuesta.text = "Pensando..."

        thread {
            try {
                val url = URL("$servidor/comando")
                val conexion = url.openConnection() as HttpURLConnection
                conexion.requestMethod = "POST"
                conexion.doOutput = true
                conexion.setRequestProperty("Content-Type", "application/json")
                conexion.connectTimeout = 5000
                conexion.readTimeout = 5000

                val cuerpo = JSONObject()
                cuerpo.put("texto", texto)
                OutputStreamWriter(conexion.outputStream).use { it.write(cuerpo.toString()) }

                val respuestaTexto = conexion.inputStream.bufferedReader().use { it.readText() }
                val json = JSONObject(respuestaTexto)
                val respuesta = json.optString("respuesta", "No hubo respuesta.")
                val accion = json.optJSONObject("accion")

                runOnUiThread {
                    textoRespuesta.text = respuesta
                    hablar(respuesta)
                }

                if (accion != null) {
                    ejecutarAccion(accion)
                }
            } catch (e: Exception) {
                runOnUiThread {
                    val mensaje = "No pude conectarme al servidor. Revisa la IP y que server.py esté corriendo en el PC."
                    textoRespuesta.text = mensaje
                    hablar(mensaje)
                }
            }
        }
    }

    private fun hablar(texto: String) {
        tts?.speak(texto, TextToSpeech.QUEUE_FLUSH, null, null)
    }

    private fun ejecutarAccion(accion: JSONObject) {
        when (accion.optString("tipo")) {
            "abrir_app" -> abrirApp(accion.optString("app"))
            "reproducir_spotify" -> abrirUri(accion.optString("uri"))
            "enviar_whatsapp" -> enviarWhatsapp(accion.optString("telefono"), accion.optString("mensaje"))
        }
    }

    /**
     * Busca entre las apps instaladas una cuyo nombre visible
     * contenga lo que se pidió, y la abre. Usa queryIntentActivities
     * (no getInstalledApplications) porque es lo que la etiqueta
     * <queries> del manifest permite ver desde Android 11 en
     * adelante.
     */
    private fun abrirApp(nombreBuscado: String) {
        val pm = packageManager
        val intentPrincipal = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val apps = pm.queryIntentActivities(intentPrincipal, PackageManager.MATCH_ALL)
        val buscado = nombreBuscado.lowercase(Locale.getDefault())

        val coincidencia = apps.firstOrNull {
            it.loadLabel(pm).toString().lowercase(Locale.getDefault()).contains(buscado)
        }

        runOnUiThread {
            val intentLanzar = coincidencia?.let { pm.getLaunchIntentForPackage(it.activityInfo.packageName) }
            if (intentLanzar != null) {
                startActivity(intentLanzar)
            } else {
                Toast.makeText(this, "No encontré la app \"$nombreBuscado\" instalada.", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun abrirUri(uri: String) {
        if (uri.isEmpty()) return
        runOnUiThread {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(uri)))
            } catch (e: Exception) {
                Toast.makeText(this, "No pude abrir eso. ¿Tienes Spotify instalado?", Toast.LENGTH_LONG).show()
            }
        }
    }

    /**
     * Abre WhatsApp con el mensaje YA ESCRITO en el chat de ese
     * número (eso lo hace cualquier app sin permisos especiales).
     * Avisa al servicio de accesibilidad que hay un mensaje
     * pendiente; ese servicio es el que de verdad "toca" el botón
     * de enviar cuando WhatsApp termine de abrir.
     */
    private fun enviarWhatsapp(telefono: String, mensaje: String) {
        if (telefono.isEmpty()) return
        val uri = Uri.parse("https://wa.me/$telefono?text=${Uri.encode(mensaje)}")
        JarvisAccessibilityService.mensajePendienteAEnviar = true
        runOnUiThread {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, uri))
            } catch (e: Exception) {
                Toast.makeText(this, "No pude abrir WhatsApp.", Toast.LENGTH_LONG).show()
            }
        }
    }
}
