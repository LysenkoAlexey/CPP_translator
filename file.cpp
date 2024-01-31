int x;
char c;
string c2;
float y,z;
void main(int a, int b)
{
	int x, y = 0;
	char u = 'a';
	string k = 'aaaa';
	float c = 11.5;
	cin >> x;
	while (x < 5) {
		x = x + 2;
	}
	if ((x == 6) && ((y < 10) || (c > 10))) {
		y = y+1;
	}
	else {
		c = c + 11;
	}


	cout << x << y << c;


}
void second_function(int a, float b){
    int x = 3 + 2;
    x = 3;

    cout << x << a << 'aaa';

}