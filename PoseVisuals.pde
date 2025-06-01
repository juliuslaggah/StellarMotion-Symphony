import oscP5.*;
import netP5.*;
import ddf.minim.*; // Import Minim library

// OSC setup
OscP5 oscP5;
float rightWristX = 0, rightWristY = 0;
float leftWristX = 0, leftWristY = 0;
float headX = 0, headY = 0;
float prevRightWristX = 0, prevRightWristY = 0;
float prevLeftWristX = 0, prevLeftWristY = 0;
float prevHeadX = 0, prevHeadY = 0;
boolean isWaving = false;
boolean prevIsWaving = false;

// New gesture flags
boolean isThumbsUp = false;
boolean isPeace = false;
boolean isClap = false;

 // Audio setup
Minim minim;
AudioPlayer chimeSound;

// Particle system
ArrayList<Particle> particles = new ArrayList<Particle>();
int maxParticles = 90;
float movementThreshold = 5; // Pixels threshold to consider movement

void setup() {
  size(800, 600);
  oscP5 = new OscP5(this, 12000);
  background(0);
  frameRate(30);
  colorMode(HSB, 360, 100, 100);
  
  // Initialize Minim and load sound
  minim = new Minim(this);
  chimeSound = minim.loadFile("chime.wav"); // Ensure chime.wav is in data/ folder
}

void draw() {
  // Semi-transparent background for fade/trail effect
  fill(0, 0, 0, 30);
  rect(0, 0, width, height);
  
  // — Wave sound logic (unchanged) —
  if (isWaving && !prevIsWaving) {
    chimeSound.rewind();
    chimeSound.play();
  }
  prevIsWaving = isWaving;
  
  // — Thumbs-Up: Freeze all particles in place —
  if (isThumbsUp) {
    for (Particle p : particles) {
      p.display();
    }
    // We keep isThumbsUp true until the next OSC update flips it off
    return;
  }
  
  // — Clap: Clear all existing particles & reset canvas —
  if (isClap) {
    particles.clear();       // remove them all
    background(0);           // clear the screen fully
    isClap = false;          // reset so it only triggers once
    return;
  }
  
  // — Peace sign: Spawn a swirling spiral at each wrist location —
  if (isPeace) {
    float ix = rightWristX * width, iy = rightWristY * height;
    float jx = leftWristX * width, jy = leftWristY * height;
    spawnSpiral(ix, iy);
    spawnSpiral(jx, jy);
    // (Optional) You can also let this fall through into the normal particle update
  }
  
  // — Default: Regular particle spawning & updating —
  float rightWristSpeed = dist(
    rightWristX * width, rightWristY * height,
    prevRightWristX * width, prevRightWristY * height
  );
  float leftWristSpeed = dist(
    leftWristX * width, leftWristY * height,
    prevLeftWristX * width, prevLeftWristY * height
  );
  float headSpeed = dist(
    headX * width, headY * height,
    prevHeadX * width, prevHeadY * height
  );
  
  if (particles.size() < maxParticles && frameCount % 2 == 0) {
    if (rightWristSpeed > movementThreshold) {
      particles.add(new Particle(
        rightWristX * width, rightWristY * height,
        rightWristSpeed, "right_wrist"
      ));
    }
    if (leftWristSpeed > movementThreshold) {
      particles.add(new Particle(
        leftWristX * width, leftWristY * height,
        leftWristSpeed, "left_wrist"
      ));
    }
    if (headSpeed > movementThreshold) {
      particles.add(new Particle(
        headX * width, headY * height,
        headSpeed, "head"
      ));
    }
  }
  
  // Update and draw all particles normally
  for (int i = particles.size() - 1; i >= 0; i--) {
    Particle p = particles.get(i);
    p.update();
    p.display();
    if (p.isDead()) {
      particles.remove(i);
    }
  }
  
  // Update previous positions
  prevRightWristX = rightWristX;
  prevRightWristY = rightWristY;
  prevLeftWristX = leftWristX;
  prevLeftWristY = leftWristY;
  prevHeadX = headX;
  prevHeadY = headY;
}

void oscEvent(OscMessage msg) {
  if (msg.checkAddrPattern("/pose/right_wrist")) {
    rightWristX = msg.get(0).floatValue();
    rightWristY = msg.get(1).floatValue();
  } 
  else if (msg.checkAddrPattern("/pose/left_wrist")) {
    leftWristX = msg.get(0).floatValue();
    leftWristY = msg.get(1).floatValue();
  } 
  else if (msg.checkAddrPattern("/pose/head")) {
    headX = msg.get(0).floatValue();
    headY = msg.get(1).floatValue();
  } 
  else if (msg.checkAddrPattern("/gesture/waving")) {
    isWaving = (msg.get(0).intValue() == 1);
  } 
  else if (msg.checkAddrPattern("/gesture/thumbs_up")) {
    isThumbsUp = (msg.get(0).intValue() == 1);
  } 
  else if (msg.checkAddrPattern("/gesture/peace")) {
    isPeace = (msg.get(0).intValue() == 1);
  } 
  else if (msg.checkAddrPattern("/gesture/clap")) {
    isClap = (msg.get(0).intValue() == 1);
  }
}

void spawnSpiral(float cx, float cy) {
  int numPoints = 50;
  for (int i = 0; i < numPoints; i++) {
    float angle = map(i, 0, numPoints, 0, TWO_PI * 3); // 1.5 turns
    float r = map(i, 0, numPoints, 0, 50);             // spiral grows outward
    float sx = cx + cos(angle) * r;
    float sy = cy + sin(angle) * r;
    Particle spiralParticle = new Particle(sx, sy, r, "spiral");
    // Color variation for the spiral
    spiralParticle.hue = (frameCount * 2 + i * 3) % 360;
    spiralParticle.life = 100;
    spiralParticle.vx = cos(angle) * 2;
    spiralParticle.vy = sin(angle) * 2;
    particles.add(spiralParticle);
  }
}

void stop() {
  // Clean up Minim resources
  chimeSound.close();
  minim.stop();
  super.stop();
}

class Particle {
  float x, y;
  float vx, vy;
  float size;
  float life;
  float hue;
  String source;
  
  Particle(float x, float y, float speed, String source) {
    this.x = x;
    this.y = y;
    float angle = noise(x * 0.01, y * 0.01, frameCount * 0.02) * TWO_PI * 2;
    float speedFactor = map(speed, 0, 50, 1, 5);
    this.vx = cos(angle) * speedFactor;
    this.vy = sin(angle) * speedFactor;
    this.size = map(speed, 0, 50, 5, 15); // Size scales with speed
    this.life = 255;
    this.source = source;
    
    if (isWaving) {
      // Colors when waving
      if (source.equals("right_wrist")) this.hue = 60;   // Yellow
      else if (source.equals("left_wrist")) this.hue = 180; // Cyan
      else if (source.equals("head")) this.hue = 300;   // Magenta
      else this.hue = (frameCount * 2) % 360;           // Spiral fallback
    } 
    else {
      // Colors when not waving
      if (source.equals("right_wrist")) this.hue = 0;   // Red
      else if (source.equals("left_wrist")) this.hue = 120; // Green
      else if (source.equals("head")) this.hue = 240;  // Blue
      else this.hue = 200;                              // Spiral fallback
    }
  }
  
  void update() {
    float angle = noise(x * 0.01, y * 0.01, frameCount * 0.02) * TWO_PI;
    vx += cos(angle) * 0.1;
    vy += sin(angle) * 0.1;
    x += vx;
    y += vy;
    life -= 3;
  }
  
  void display() {
    noStroke();
    fill(hue, 80, 100, life);
    drawStar(x, y, 5, size / 2, size / 4); // Draw star with 5 points
  }
  
  void drawStar(float x, float y, int points, float outerRadius, float innerRadius) {
    float angle = TWO_PI / points;
    float halfAngle = angle / 2.0;
    beginShape();
    for (float a = 0; a < TWO_PI; a += angle) {
      float sx = x + cos(a) * outerRadius;
      float sy = y + sin(a) * outerRadius;
      vertex(sx, sy);
      sx = x + cos(a + halfAngle) * innerRadius;
      sy = y + sin(a + halfAngle) * innerRadius;
      vertex(sx, sy);
    }
    endShape(CLOSE);
  }
  
  boolean isDead() {
    return life <= 0 || x < 0 || x > width || y < 0 || y > height;
  }
}
