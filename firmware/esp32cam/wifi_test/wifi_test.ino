// wifi_test.ino — connecte l'ESP32 au Wi-Fi et affiche son IP
// Carte cible : AI-Thinker ESP32-CAM
// Objectif J2 : voir l'IP dans le moniteur serie, puis ping depuis le PC.

#include <WiFi.h>
#include "secrets.h"

void setup() {
  // Demarre la communication serie USB a 115200 bauds
  Serial.begin(115200);
  delay(1000);  // laisse le temps au moniteur serie de s'ouvrir

  Serial.println();
  Serial.println("=== ESP32-CAM : test Wi-Fi ===");

  // Mode station : l'ESP32 se comporte comme un client Wi-Fi (pas comme un point d'acces)
  WiFi.mode(WIFI_STA);

  Serial.print("Connexion au reseau : ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // On attend la connexion, max 20 secondes
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connecte !");
    Serial.print("Adresse IP : ");
    Serial.println(WiFi.localIP());   // l'IP attribuee par le routeur
    Serial.print("Force du signal (RSSI) : ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("ECHEC : pas de connexion au Wi-Fi.");
    Serial.println("Verifie le SSID, le mot de passe, et que le reseau est bien en 2.4 GHz.");
  }
}

void loop() {
  // Rien a faire en boucle pour ce test.
  // On pourrait afficher l'IP regulierement, mais pour J2 c'est suffisant.
  delay(5000);
}
