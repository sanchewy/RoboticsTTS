package edu.montana.cs.klise.robot;

import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.net.Network;
import android.net.sip.SipAudioCall;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.widget.RemoteViews;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Locale;

import static android.app.Activity.RESULT_OK;

public class ServerThread extends Thread {

    Context context;
//    public static Server inst;
    ServerSocket serverSocket;
    int P;
    Socket socket;
    BufferedReader input;
    SipAudioCall.Listener listener;
    int PORT = 9998;
    //Network parent;
    MainActivity parent;//new
    //Handler mainHandler = new Handler(Looper.getMainLooper());

    TTS tts; //new
    Thread receiveThread;//new

    public ServerThread(Context c) {
        this.context = c;
    }

//    public static Server getInst() {
//        if(inst == null) {
//            inst = new Server();
//        }
//        return inst;
//    }

    /*public void setParent(Network c) {
        parent = c;
    }*/
    public void setParent(MainActivity c, TTS tts) {//new
        this.tts = tts;
        parent = c;
    }

    public void run() {
        //Looper.prepare();
        while(true) {
            //Log.v("LOGGING", "Looped");
            if (serverSocket == null || socket.isClosed()) {
                try {
                    try {
                        serverSocket = new ServerSocket(PORT);
                    } catch (IOException e) {
                        Log.v("LOGGING", "Could not listen on port " + PORT);
                        System.exit(-1);
                    }

                    Log.v("LOGGING", "Server Listening");
                    long startTime = System.currentTimeMillis(); //fetch starting time

                    try {
                        this.socket = serverSocket.accept();
                    } catch (IOException e) {
                        Log.v("LOGGING", "Accept failed: " + PORT);
                        System.exit(-1);
                    }
                    this.input = new BufferedReader(new InputStreamReader(this.socket.getInputStream()));
                    //String read = input.readLine();
                /*mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        Toast toast = Toast.makeText(context, "Socket Accepted", Toast.LENGTH_SHORT);
                        toast.show();
                    }
                });*/
                } catch (IOException e) {
                    e.printStackTrace();
                    Log.w("ERROR", "Server was not established.");
                }
                Log.v("LOGGING", "Made it past blocking server accept.");
            } else {//new
                //Log.v("LOGGING", "Running");
                //Looper.prepare();
                try {
                    //Log.v("LOGGING", "Text to Speach");
                    String in = input.readLine();
                    if(in != null) {
                        Log.v("**SPEACH**", in);

                        Message sendMsg = tts.handler.obtainMessage();
                        if (sendMsg != null) {
                            Bundle b = new Bundle();
                            b.putString("TT", in);
                            sendMsg.setData(b);
                            tts.handler.sendMessage(sendMsg);
                        }
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
                //Looper.loop();
            }//end new
        }
        //Looper.loop();
    }
}
