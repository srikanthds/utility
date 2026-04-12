#include <stdio.h>
#include <ctype.h>

#define MAX 1000

int main()
{

int s, pi, ci;
char plain[MAX], cipher[MAX];

printf("*** Encryption & decryption using substitution cipher ***\n\n");
printf("Enter the plain text:\n");

gets(plain);
while(1)
{
  printf("\nKey (number of shifts per character) for encryption : ");
  scanf("%d", &s);
  if(s < 1 || s > 25) // || logical or function
    printf("Bad input! Enter a value between 1 and 25.");
  else
    break;
}
printf("\nAfter processing (spaces preserved, letters capitalized, numbers processed):\n");
for(ci = 0, pi = 0; plain[pi] != '\0'; pi++)
{
  if(isalpha(plain[pi]))   // If a character passed to isalpha() is an alphabet, it returns a non-zero //integer, if not it returns 0
  {
    putchar(toupper(plain[pi]));
    // The toupper() function is used to convert lowercase alphabet to uppercase
    // putchar() function is a file handling function in which is used to write a character on //standard output/screen.
    cipher[ci++] = ((toupper(plain[pi]) - 'A') + s% 26) % 26 + 'A';
  }
  else if(isdigit(plain[pi]))   // Handle numbers: shift digits 0-9
  {
    putchar(plain[pi]);
    cipher[ci++] = ((plain[pi] - '0') + s) % 10 + '0';
  }
  else if(plain[pi] == ' ')   // Preserve spaces
  {
    putchar(' ');
    cipher[ci++] = ' ';
  }
}
cipher[ci] = '\0';
printf("\n\nAfter encryption:\n%s\n", cipher);
while(1)
{
  printf("\nKey for decryption : ");
  scanf("%d", &s);
  if(s< 1 || s> 25)
    printf("Bad input! Enter a value between 1 and 25.");
  else
    break;
}
for(pi = 0, ci = 0; cipher[ci] != '\0'; ci++)
{
  if(isalpha(cipher[ci]))
    plain[pi++] = ((cipher[ci] - 'A') + (26 - s)) % 26 + 'A';
  else if(isdigit(cipher[ci]))   // Decrypt digits
    plain[pi++] = ((cipher[ci] - '0') + (10 - s % 10)) % 10 + '0';
  else if(cipher[ci] == ' ')   // Preserve spaces during decryption
    plain[pi++] = ' ';
}
plain[pi] = '\0';
printf("\nAfter decryption:\n%s\n", plain);
return 0;

}

