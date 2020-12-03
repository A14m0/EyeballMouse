// UserlandEyeballDriver.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include <stdio.h>
#include <stdlib.h>
#include <WinSock2.h>
#include <Windows.h>
#include <ws2tcpip.h>

#pragma comment(lib, "Ws2_32.lib")


/// define required global inputs
int lc_state = 0;
int rc_state = 0;


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

int read_pos(SOCKET sock, int old_x, int old_y, int* x, int* y, int* lc, int* rc) {
	char buff[6];
	// read data from the socket
	if (!recv(sock, buff, 6, 0)) {
		printf("[DRIVER] Receive Failed: No data read\n");
		return 1;
	}
	
	printf("Buffer -> %s\n", buff);

	// byte 1 is x, byte 2 is y
	*x = static_cast<short>(buff[0]) + old_x;
	*y = static_cast<short>(buff[2]) + old_y;

	int flags = static_cast<short>(buff[4]); 

	*rc = flags & 1; 
	*lc = flags & 1;

	return 0;
}

int update_mouse(int* x, int* y) {
	// check x bounds
	if (*x < 0) *x = 0;
	if (*x > GetSystemMetrics(SM_CXSCREEN)) *x = GetSystemMetrics(SM_CXSCREEN);

	// check y bounds
	if (*y < 0) *y = 0;
	if (*y > GetSystemMetrics(SM_CYSCREEN)) *y = GetSystemMetrics(SM_CYSCREEN);

	
	// update, check for errors
	if (!SetCursorPos(*x, *y)) {
		printf("[DRIVER] Failed to update cursor position: %d\n", GetLastError());
	}

	return 0;
}

int handle_clicks(int lc, int rc) {
	int stateflags = 0;
	int one_ready_quit = 0;
	
	// check if the left button is down
	if(lc == 1 && lc_state == 0){
		// going from unclicked --> clicked
		stateflags |= MOUSEEVENTF_LEFTDOWN;
		lc_state = 1;
	} else if(lc_state == 1 && lc == 0) {
		// going from clicked --> unclicked
		stateflags |= MOUSEEVENTF_LEFTUP;
		lc_state = 0;
	} else {
		// left doesnt need updating, communicate that for later
		one_ready_quit = 1;
	}
	
	// check right button down
	if(rc == 1 && rc_state == 0){
		// going from unclicked --> clicked
		stateflags |= MOUSEEVENTF_RIGHTDOWN;
		rc_state = 1;
	} else if(rc_state == 1 && rc == 0){
		// going from clicked --> unclicked
		stateflags |= MOUSEEVENTF_RIGHTUP;
		rc_state = 0;
	} else if(one_ready_quit){
		// left and right done, no need to pass event
		return 0;
	}
	
	/* Future TODOs:
	 *    Add support for scrolling into this
	 *    (check MOUSEEVENTF_WHEEL)
	 */
	
	// pass the event
	mouse_event(stateflags, 0, 0, 0, nullptr);
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
		int lc = 0;
		int rc = 0;

		// make sure nothing broke during initialization
		if (sock == 1) {
			//break;
			printf("SOCK INVALID!!!\n");
			return 1;
		}

		// keep reading positions from connected client
		while (!read_pos(sock, x,y, &x, &y, &lc, &rc)) {
			printf("[DRIVER] x: %d, y: %d\n", x, y);
			printf("[DRIVER] LC: %d, RC: %d\n", lc, rc);

			// update the cursor position
			update_mouse(&x, &y);

			// do clicks if need be
			handle_clicks(lc, rc);

		}

		
		printf("[DRIVER] Failed to read position data from client. Restarting...\n");
	} while(1);

	return 0;
}

