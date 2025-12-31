#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

#define TFT_CS   4
#define TFT_DC   16
#define TFT_RST  17
#define TFT_SCLK 18
#define TFT_MOSI 5

#define W 240
#define H 320
#define GW 120
#define GH 160

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

uint8_t grid[GW][GH];
struct Cell { uint16_t x; uint16_t y; };
Cell frontier[4000];
int frontierSize = 0;
uint16_t palette[8];

int sx = W / GW;
int sy = H / GH;

uint16_t mixColor(uint16_t base) {
  int r = ((base >> 11) & 0x1F) * 8 + random(-20,21);
  int g = ((base >> 5) & 0x3F) * 4 + random(-20,21);
  int b = (base & 0x1F) * 8 + random(-20,21);
  r = constrain(r,0,255);
  g = constrain(g,0,255);
  b = constrain(b,0,255);
  return tft.color565(r,g,b);
}

// Add cell with 4-way symmetry
void addSymmetric(int x, int y, uint16_t color) {
  int xs[2] = {x, GW - 1 - x};
  int ys[2] = {y, GH - 1 - y};
  for(int i=0;i<2;i++){
    for(int j=0;j<2;j++){
      int px = xs[i], py = ys[j];
      if(grid[px][py]==0){
        grid[px][py]=1;
        tft.fillRect(px*sx, py*sy, sx, sy, color);
        frontier[frontierSize++] = { (uint16_t)px, (uint16_t)py };
      }
      delay(1);
    }
  }
}

void resetPattern(){
  tft.fillScreen(ST77XX_BLACK);
  memset(grid,0,sizeof(grid));
  frontierSize=0;
  for(int i=0;i<8;i++){
    palette[i]=tft.color565(random(60,256),random(60,256),random(60,256));
  }
  int cx = GW/2;
  int cy = GH/2;
  addSymmetric(cx,cy,palette[random(8)]);
}

void setup(){
  SPI.begin(TFT_SCLK,-1,TFT_MOSI,TFT_CS);
  tft.init(W,H);
  tft.setRotation(1);
  randomSeed(esp_random());
  resetPattern();
}

void loop(){
  if(frontierSize==0){
    resetPattern();
    return;
  }

  // Slow down growth by reducing steps
  int stepsPerFrame = 1; // << slower
  for(int step=0; step<stepsPerFrame; step++){
    if(frontierSize==0) break;

    int idx = random(frontierSize);
    Cell c = frontier[idx];

    // Grow in all directions for better coverage
    int dirs[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};
    int dirIdx = random(4);
    int nx = c.x + dirs[dirIdx][0];
    int ny = c.y + dirs[dirIdx][1];

    if(nx<0||nx>=GW||ny<0||ny>=GH) continue;
    if(grid[nx][ny]!=0) continue;

    uint16_t col = mixColor(palette[random(8)]);
    addSymmetric(nx,ny,col);

    frontier[idx] = frontier[--frontierSize]; // remove used
  }

  // If frontier gets too big (screen almost filled), force restart
  if(frontierSize>3000){
    resetPattern();
  }
}
