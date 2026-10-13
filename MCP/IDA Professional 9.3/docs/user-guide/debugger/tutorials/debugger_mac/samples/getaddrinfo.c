#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdio.h>

// gcc -o getaddrinfo_example getaddrinfo.c
int main(int argc, char **argv)
{
  if ( argc != 2 )
  {
    fprintf(stderr, "usage: %s <hostname>\n", argv[0]);
    return 1;
  }

  struct addrinfo hints;
  memset(&hints, 0, sizeof(hints));

  hints.ai_family = AF_INET;
  hints.ai_flags |= AI_CANONNAME;

  struct addrinfo *result;
  int code = getaddrinfo(argv[1], NULL, &hints, &result);
  if ( code != 0 )
  {
    fprintf(stderr, "failed: %d\n", code);
    return 1;
  }

  struct sockaddr_in *addr_in = (struct sockaddr_in *)result->ai_addr;
  char *ipstr = inet_ntoa(addr_in->sin_addr);
  printf("IP address: %s\n", ipstr);

  return 0;
}
