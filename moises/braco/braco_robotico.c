/*******************************************************************************
* rc_project_template.c
*
* This is meant to be a skeleton program for robotics cape projects. 
* Change this description and file name 
*******************************************************************************/

// usefulincludes is a collection of common system includes for the lazy
// This is not necessary for roboticscape projects but here for convenience
// #include <rc_usefulincludes.h> 
// main roboticscape API header
#include <rc/servo.h>
#include <pthread.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

#define SERV_ADDR "192.168.0.153"
#define PORT 5005    /* the port client will be connecting to */
#define BUFSIZE 1024

#define SERV_ADDR_INV "127.0.0.1"
#define PORT_INV 6670    /* the port client will be connecting to */
#define BUFSIZE_INV 100


#define PI 3.14159265

int signalstop = 0;
int pulse_1, pulse_2 = 2100, pulse_3 = 600, pulse_4 = 1300, pulse_5 = 1125, pulse_6 = 1662;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// function declarations
/*Thread to keep the arm pose untill the values are changed*/
void run_thread(void * unused)
{
	while(!signalstop)
	{
		pthread_mutex_lock(&mutex);
		rc_servo_send_pulse_us(2, pulse_2);
		rc_servo_send_pulse_us(3, pulse_3);
		rc_servo_send_pulse_us(4, pulse_4);
		rc_servo_send_pulse_us(5, pulse_5);
		rc_servo_send_pulse_us(6, pulse_6);
		pthread_mutex_unlock(&mutex);
		rc_usleep(15000);
	}
}

/*Sets pulse width for channel*/
void move2pos(int channel, int pulse)
{
	if (channel == 3)
	{
		pthread_mutex_lock(&mutex);
		pulse_3 = pulse;
		pthread_mutex_unlock(&mutex);
	}
	else if (channel == 4)
	{
		pthread_mutex_lock(&mutex);
		pulse_4 = pulse;
		pthread_mutex_unlock(&mutex);
	}
	else if (channel == 5)
	{
		pthread_mutex_lock(&mutex);
		pulse_5 = pulse;
		pthread_mutex_unlock(&mutex);
	}
	else if (channel == 6)
	{
		pthread_mutex_lock(&mutex);
		pulse_6 = pulse;
		pthread_mutex_unlock(&mutex);
	}
}

/*Smoothly moves joint to position*/
void move(int pulse3, int pulse4, int pulse5, int pulse6)
{
	while (pulse_3 != pulse3 || pulse_4 != pulse4 || pulse_5 != pulse5 || pulse_6 != pulse6)
	{
		//for (int i = 0; i < 3; i++)
		{
			if (pulse_5 < pulse5) move2pos(5, pulse_5 + 1);
			else if (pulse_5 > pulse5) move2pos(5, pulse_5 - 1);
			rc_usleep(400);
		}
		
		if (pulse_6 < pulse6) move2pos(6, pulse_6 + 1);
		else if (pulse_6 > pulse6) move2pos(6, pulse_6 - 1);
		rc_usleep(400);
		
		if (pulse_4 < pulse4) move2pos(4, pulse_4 + 1);
		else if (pulse_4 > pulse4) move2pos(4, pulse_4 - 1);
		rc_usleep(400);
		
		if (pulse_3 < pulse3) move2pos(3, pulse_3 + 1);
		else if (pulse_3 > pulse3) move2pos(3, pulse_3 - 1);
		rc_usleep(400);
		
	}
}

/*Moves piece to rest position*/
void restPos()
{
	move(900, 2300, 1800, 1800);
}


/*Converting angles to pulse widths*/
int angle2pulse(float theta, float min_theta, float max_theta, float min_pulse, float max_pulse) 
{
	float d_theta = max_theta - min_theta;
	float d_pulse = max_pulse - min_pulse;
	float pulse = ((theta - min_theta)/d_theta + min_pulse/d_pulse) * d_pulse;
	return (int) pulse;
}

int a6topulse(float angle)
{
	int output = angle2pulse(angle, -84, 66, 850, 2300);
	// if (output > 2150) output = 2150;
	// else if (output < 1100) output = 1100;
	return output;
}

int a5topulse(float angle)
//diminui o offset/output, chega mais perto do chão
{
	int output = angle2pulse(angle, 17, 90, 700, 1125);
	// if (output > 1800) output = 1800;
	// else if (output < 700) output = 700;
	return output;
}

int a4topulse(float angle)
//diminui o offset/output, fica mais esticado
{
	int output = angle2pulse(angle, 0, -90, 1300, 2250);
	// if (output > 2250) output = 2250;
	// else if (output < 1300) output = 1300;
	return output;
}

int a3topulse(float angle)
{
	
	int output = angle2pulse(angle, -45, -90, 600, 1100);
	// if (output > 1100) output = 1100;
	// else if (output < 600) output = 600;
	return output;
}

/*signal tool*/
/*Opens and closes tool*/
void signaltool(int open)
{
	if (open)
	{
		for (int i = 0; i < 50; i++)
		{
			// rc_servo_send_pulse_us(1,1300);
			rc_servo_send_pulse_us(1, 900);
			rc_usleep(15000);
		}
	}
	else
	{
		for (int i = 0; i < 50; i++)
		{
			// rc_servo_send_pulse_us(1,2800);
			rc_servo_send_pulse_us(1, 2200);
			rc_usleep(15000);
		}
	}
}

float get_xcm(float y)
{
	float x_px, x_cm;
	x_px = 415 - y;
	x_cm = x_px/12.0 + 12.34 - 1.423;
}

float get_ycm(float x)
{
	float y_px, y_cm;
	y_px = 300 - x;
	y_cm = y_px/12.0 - 10.5 + 1.1667;
}

/*Brute force inverse kinematics*/
moveInvKin(float x, float y, float z)
{
	float a6, a5, a4, a3, d;
	x = x + 10;
	a6 = (float) atan2((double)y, (double)x);
	a6 = (a6*180.0)/PI;
	d = (float) sqrt((double)((x*x) + (y*y)));
	
	float c3, c4, c5;
	float best = 10000000.0;
	for(c3 = -45; c3 >= -90; c3 = c3 - 1)
	{
		for (c4 = 0; c4 >= -90; c4 = c4 - 1)
		{
			for (c5 = 17; c5 <= 130; c5 = c5 + 1)
			{
				float dcd = 10.2*cos(c5*PI/180) + 9.7*cos((c5 + c4)*PI/180) + 12.1*cos((c5 + c4 + c3)*PI/180);
				float zcd = 7.9 + 10.2*sin(c5*PI/180) + 9.7*sin((c5 + c4)*PI/180) + 12.1*sin((c5 + c4 + c3)*PI/180);
				float cd = sqrt((dcd - d)*(dcd - d) + (zcd - z)*(zcd - z));
				if (cd < best){
					best = (abs(dcd - d) + abs(zcd - z));
					a3 = c3;
					a4 = c4;
					a5 = c5;
				}
			}
		}
	}
	printf("Angles: %f[6] %f[5] %f[4] %f[3]\n", a6, a5, a4, a3);
	printf("Best: %f\n", best);
	
	move(a3topulse(a3), a4topulse(a4), a5topulse(a5), a6topulse(a6));
}

serverInvKin(float x, float y, float z)
{
	int sockfd, numbytes;  
    char buf[BUFSIZE_INV];
    struct hostent *he;
    struct sockaddr_in their_addr; /* connector's address information */
    
    if ((he=gethostbyname(SERV_ADDR_INV)) == NULL) {  /* get the host info */
        herror("gethostbyname");
        exit(1);
    }
    
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket");
        exit(1);
	}
	
	their_addr.sin_family = AF_INET;      /* host byte order */
    their_addr.sin_port = htons(PORT_INV);    /* short, network byte order */
    their_addr.sin_addr = *((struct in_addr *)he->h_addr);
    bzero(&(their_addr.sin_zero), 8);     /* zero the rest of the struct */
    
    if (connect(sockfd, (struct sockaddr *)&their_addr, sizeof(struct sockaddr)) == -1) {
        perror("connect");
        exit(1);
	}
	
	char eixos[100];
	for(int i = 0; i < 100; i++) eixos[i] = '\0';
	sprintf(eixos, "%.3f %.3f %.3f", x, y, z);
    if (send(sockfd, eixos,  BUFSIZE_INV, 0) == -1){
    	perror("send");
    	exit (1);
	}
	printf("After the send function \n");
	if ((numbytes=recv(sockfd, buf, BUFSIZE_INV, 0)) == -1) {
		perror("recv");
		exit(1);
	}	

    buf[numbytes] = '\0';
    float a3, a4, a5, a6;
    

	printf("Angulos = %s \n", buf);
	sscanf(buf, "%f %f %f %f", &a6, &a5, &a4, &a3);
	
	move(a3topulse(a3), a4topulse(a4), a5topulse(a5), a6topulse(a6));
	
	close(sockfd);		
}

/*******************************************************************************
* int main() 
*
* This template main function contains these critical components
* - call to rc_initialize() at the beginning
* - main while loop that checks for EXITING condition
* - rc_cleanup() at the end
*******************************************************************************/
int main(){
	// always initialize cape library first
	// if(rc_initialize()){
	// 	fprintf(stderr,"ERROR: failed to initialize rc_initialize(), are you root?\n");
	// 	return -1;
	// }
	if (rc_servo_init()) {
		fprintf(stderr,"ERROR: failed to initialize rc_servo_init(), are you root?\n");
		return -1;
	}
	
	pthread_t arm_thread;
	pthread_create(&arm_thread, NULL, run_thread, NULL);
	
	sleep(3);
	
	int ext = 0;
	
	while (!ext)
	{
		int channel;
		float angle;
		int opt;
		
		printf("Operações: \n1- Demo\n2- Abrir ferramenta\n3- Fechar ferramenta\n4- Restaurar posição de repouso\n\n0- Sair\n\n");
		printf("Operação: ");
		scanf("%d", &opt);
		if (opt == 1)
		{
			int i;
			for (i = 0; i < 1; i++)
			{
				float x, y, z;
				float dx, dy, dz;
				//printf("Digite a posição X Y Z desejada, separada por espaços: ");
				//scanf("%f %f %f", &dx, &dy, &dz);
				dx = 23;
				dz = 0;
				
				if (i % 2 == 0)
				{
					dy = -5;
				}
				else
				{
					dy = 0;
				}
				
				int sockfd, numbytes;  
		        char buf[BUFSIZE];
		        struct hostent *he;
		        struct sockaddr_in their_addr; /* connector's address information */
		        
		        if ((he=gethostbyname(SERV_ADDR)) == NULL) {  /* get the host info */
		            herror("gethostbyname");
		            exit(1);
		        }
	            
	            if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
		            perror("socket");
		            exit(1);
	        	}
	        	
	        	their_addr.sin_family = AF_INET;      /* host byte order */
		        their_addr.sin_port = htons(PORT);    /* short, network byte order */
		        their_addr.sin_addr = *((struct in_addr *)he->h_addr);
		        bzero(&(their_addr.sin_zero), 8);     /* zero the rest of the struct */
		        
		        if (connect(sockfd, (struct sockaddr *)&their_addr, sizeof(struct sockaddr)) == -1) {
		            perror("connect");
		            exit(1);
	        	}
	        	
	        	if (send(sockfd, "1", 14, 0) == -1){ // "1" peça preta, "0" peça vermelha 
	            	perror("send");
			    	exit (1);
				}
				printf("After the send function \n");
				if ((numbytes=recv(sockfd, buf, BUFSIZE, 0)) == -1) {
	            		perror("recv");
	            		exit(1);
				}	
	
		        buf[numbytes] = '\0';
		        
	
	        	sscanf(buf, "%f %f %f", &x, &y, &z);
				close(sockfd);
				
				x = x+32;
				y = y+32;
				float aux = x;
				
				x = get_xcm(y);
				y = get_ycm(aux);
				
				printf("Peça = %.3f %.3f %.3f\n", x, y, z);
				
				signaltool(1);
				//moveInvKin(x,y,z+1);
				serverInvKin(x, y, z);
				rc_usleep(1000000);
				signaltool(0);
				restPos();
				serverInvKin(dx, dy, dz);
				rc_usleep(1000000);
				signaltool(1);
				restPos();
				signaltool(0);
			}
		}
		
		else if (opt == 2) signaltool(1);
		else if (opt == 3) signaltool(0);
		else if (opt == 4) restPos();
		else if (opt == 0) ext = 1;
		else printf("Operação Inválida!\n");
	}
	
	restPos();
	
	signalstop = 1;
	pthread_join(arm_thread, NULL);
	
	// exit cleanly
	rc_cleanup(); 
	return 0;
}


