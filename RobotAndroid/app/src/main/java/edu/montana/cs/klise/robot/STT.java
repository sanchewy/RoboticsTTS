package edu.montana.cs.klise.robot;

import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.speech.RecognizerIntent;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.widget.EditText;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Locale;

import static android.app.Activity.RESULT_OK;

/**
 * Created by bklise on 4/5/18.
 */

public class STT extends AppCompatActivity implements Runnable {
    final int REQ_CODE_SPEECH_INPUT = 100;
    Context context;
    ClientThread client;

    public STT(Context con) {
        this.context = con;
    }

    public void run() {
        while(true) {
//            Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
//            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
//            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE,  Locale.getDefault());
//            try {
//                startActivityForResult(intent, REQ_CODE_SPEECH_INPUT);
//                Log.v("LOGGING", "Start speech activity");
//            } catch (ActivityNotFoundException a) {
//
//            }
            Handler handler = new Handler(Looper.getMainLooper());
            handler.post(new Runnable() {
                @Override
                public void run() {
                    Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                    intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                    intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE,  Locale.getDefault());
                    try {
                        startActivityForResult(intent, REQ_CODE_SPEECH_INPUT);
                        Log.v("LOGGING", "Start speech activity");
                    } catch (ActivityNotFoundException a) {

                    }
                }
            });
        }
    }

    //new
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode) {
            case REQ_CODE_SPEECH_INPUT: {
                if (resultCode == RESULT_OK && null != data) {

                    ArrayList<String> result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);

                    String msg = result.get(0);

                    Toast toast = Toast.makeText(context, msg, Toast.LENGTH_SHORT);
                    toast.show();

                    if(msg.equals("start")) {
                        client = new ClientThread(((EditText) findViewById(R.id.talkText)).getText().toString(), msg);
                        client.start();
                    }
                }
                break;
            }

        }
    }//end new
}
