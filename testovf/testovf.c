#include <limits.h>
#include <stdbool.h>
long big = LONG_MAX;
bool
testovf (void)
{
return big + LONG_MAX < big;
}

int main(void)
{
	return testovf();
}