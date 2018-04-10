package edu.montana.cs.klise.robot;

import android.util.Log;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;

/**
 * Created by bklise on 4/5/18.
 */

public class ClientThread extends Thread {
    String dstAddress;// = "10.200.3.13";
    int dstPort = 9999;
    Socket socket;
    ObjectOutputStream out;
    STT stt;
    String message;

    public ClientThread(String ip, String message) {
        dstAddress = ip;
        this.message = message;
    }

    public void run() {
        Log.v("LOGGING", "Running client thread");
        try {
            SocketAddress address = new InetSocketAddress(dstAddress, dstPort);
            socket = new Socket();
            socket.connect(address);
            //socket = new Socket(dstAddress, dstPort);
            Log.v("LOGGING", "Client created");

            send(message);
            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void send(String message) throws IOException {
        /*Log.v("LOGGING", "Get output stream");
        out = new ObjectOutputStream(socket.getOutputStream());

        Log.v("LOGGING", "OutputStreamWriter");
        OutputStreamWriter osw = new OutputStreamWriter(out);

        Log.v("LOGGING", "BufferedWriter");
        BufferedWriter bw = new BufferedWriter(osw);

        Log.v("LOGGING", "PrintWriter");
        PrintWriter out = new PrintWriter(bw, true);*/
        PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);

        Log.v("LOGGING", "Print message");
        out.println(message);

        Log.v("LOGGING", "Message sent");
    }
}
