using UnityEngine;
using Debug = UnityEngine.Debug;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine.SceneManagement;
using System.Diagnostics;
using System.IO;
using UnityEngine.UI;

public class MainMenu : MonoBehaviour
{
	//vlakno
	Thread receiveThread;
	//klient
	UdpClient client;
	//port
	public int port;
	//vek
	public string age;

	public string lastPacket = "";
	public string allPackets = "";



	void Start()
	{
		Init();
	}


	private void Init()
	{
		print("UPDSend.Init()");
		//port na ktorom komunikuju klient a server
		port = 5065;

		//priradenie metody vlaknu
		receiveThread = new Thread(new ThreadStart(GetData));
		receiveThread.IsBackground = true;
		//start vlakna
		receiveThread.Start();

	}


	private void GetData()
	{
		client = new UdpClient(port);
		while (true)
		{
			try
			{
				IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("127.0.0.1"), port);
				byte[] data = client.Receive(ref anyIP);

				string text = Encoding.UTF8.GetString(data);
				print(">> " + text);
				lastPacket = text;
				allPackets = allPackets + text;
				Debug.Log("Vek:" + text);

			}
			catch (Exception e)
			{
				print(e.ToString());
			}
		}
	}

	public string GetLastPacket()
	{
		allPackets = "";
		return lastPacket;
	}

	void OnApplicationQuit()
	{
		if (receiveThread != null)
		{
			receiveThread.Abort();
			Debug.Log(receiveThread.IsAlive);
		}
	}
	void OnGUI()
	{
		Rect rectObj = new Rect(40, 10, 200, 400);

		GUIStyle style = new GUIStyle();

		style.alignment = TextAnchor.LowerLeft;

		GUI.Box(rectObj, "# UDPReceive\n127.0.0.1 " + port + " #\n"

				  + "\nLast Packet: \n" + lastPacket

				  , style);

		Debug.Log("My packet: " + lastPacket);


		if (lastPacket == "(25-32)" ||
		lastPacket == "(38-43)" ||
		lastPacket == "(48-53)" ||
		lastPacket == "(60-100)"
		)
		{
			receiveThread.Abort();
			SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex + 1);
		}
		else
		{
			
			receiveThread.Abort();
			SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex + 2);
		}
	}

}