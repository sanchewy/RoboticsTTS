package edu.montana.cs.klise.robot;

import android.content.Context;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.speech.tts.TextToSpeech;
import android.util.Log;
import android.widget.Toast;

import java.util.Locale;

/**
 * Created by bklise on 3/29/18.
 */

public class TTS extends Thread implements TextToSpeech.OnInitListener {
    private TextToSpeech tts;
    private Context context;
    public Handler handler;
    private String last;

    TTS(Context con) {
        context = con;
        tts = new TextToSpeech(con, this);
        last = "c";
    }

    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) {
            int result = tts.setLanguage(Locale.US);
            tts.setPitch(0);
            tts.setSpeechRate((float) 1);

            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                Toast.makeText(context, "Language or data not working", Toast.LENGTH_LONG).show();
            }
        }
    }

    public void run() {
        Looper.prepare();

        this.handler = new Handler() {
            @Override
            public void handleMessage(Message msg) {
                String response = msg.getData().getString("TT");
                Log.v("**SPEECH**", response);
                speakOut(response);
            }
        };

        Looper.loop();
    }

    public void speakOut(String text) {
        if (last != text) {
            last = text;
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);

            while (tts.isSpeaking()) {
                try {
                    Thread.sleep(200);
                } catch (Exception e) {

                }
            }
        }
    }
}
