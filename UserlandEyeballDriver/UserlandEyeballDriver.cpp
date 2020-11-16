// UserlandEyeballDriver.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include <stdio.h>
#include <stdlib.h>
#include <WinSock2.h>
#include <Windows.h>
#include <ws2tcpip.h>

#pragma comment(lib, "Ws2_32.lib")

SOCKET get_client(SOCKET ListenSocket) {
	printf("[DRIVER] Listening...\n");
	// listen for incomming connections
	if (listen(ListenSocket, SOMAXCONN) == SOCKET_ERROR) {
		printf("[DRIVER] Listen failed with error: %ld\n", WSAGetLastError());
		closesocket(ListenSocket);
		WSACleanup();
		return 1;
	}

	// accept incoming connection

	SOCKET ClientSocket = *(SOCKET *)malloc(sizeof(SOCKET));
	ClientSocket = INVALID_SOCKET;

	// Accept a client socket
	ClientSocket = WSAAccept(ListenSocket, NULL, NULL, NULL, NULL);
	if (ClientSocket == INVALID_SOCKET) {
		printf("[DRIVER] Socket accept failed: %d\n", WSAGetLastError());
		closesocket(ListenSocket);
		WSACleanup();
		return 1;
	}

	// return it
	return ClientSocket;
}

int read_pos(SOCKET sock, int* x, int* y) {
	char buff[4];
	// read data from the socket
	if (!recv(sock, buff, 4, 0)) {
		printf("[DRIVER] Receive Failed: No data read\n");
		return 1;
	}
	
	printf("Buffer -> %s\n", buff);

	// byte 1 is x, byte 2 is y
	*x = static_cast<short>(buff[0]);
	*y = static_cast<short>(buff[2]);

	return 0;
}

int main()
{
	// initialize WSA
	WSADATA wsaData;
	int iResult;
	struct addrinfo* result = NULL, * ptr = NULL, hints;

	SOCKET ListenSocket = INVALID_SOCKET;

	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;
	hints.ai_flags = AI_PASSIVE;



	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		printf("[DRIVER] WSAStartup failed: %d\n", iResult);
		exit(1);
	}

	// set up server socket
	
	// Resolve the local address and port to be used by the server
	iResult = getaddrinfo(NULL, "42000", &hints, &result);
	if (iResult != 0) {
		printf("[DRIVER] Socket getaddrinfo failed: %d\n", iResult);
		WSACleanup();
		return 1;
	}

	// initialize listening socket
	ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);

	// check validity
	if (ListenSocket == INVALID_SOCKET) {
		printf("[DRIVER] Error at socket(): %ld\n", WSAGetLastError());
		freeaddrinfo(result);
		WSACleanup();
		return 1;
	}

	// bind it to the port
	iResult = bind(ListenSocket, result->ai_addr, (int)result->ai_addrlen);
	if (iResult == SOCKET_ERROR) {
		printf("[DRIVER] Socket bind failed: %d\n", WSAGetLastError());
		freeaddrinfo(result);
		closesocket(ListenSocket);
		WSACleanup();
		return 1;
	}


	
	// loop foreverrrrrrr
	do {
		SOCKET sock = get_client(ListenSocket);
		int x = 0;
		int y = 0;

		// make sure nothing broke during initialization
		if (sock == 1) {
			//break;
			printf("SOCK INVALID!!!\n");
			return 1;
		}

		// keep reading positions from connected client
		while (!read_pos(sock, &x, &y)) {
			printf("[DRIVER] x: %d, y: %d\n", x, y);
		}

		printf("[DRIVER] Failed to read position data from client. Restarting...\n");
	} while(1);

	return 0;
}

