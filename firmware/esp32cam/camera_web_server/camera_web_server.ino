// camera_web_server.ino
// Serveur HTTP embarqué : page de flux + endpoint /capture (une image JPEG).
// Modèle : AI-Thinker ESP32-CAM. Baud série : 115200.

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "secrets.h"   // SSID + mot de passe, jamais versionné

// --- Broches du module AI-Thinker (fixées par le matériel) ---
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

static httpd_handle_t server = NULL;

// Handler pour /capture : renvoie UNE image JPEG brute.
static esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }
  // On indique au navigateur web que le contenu qu'on va lui envoyer est une image au format JPEG.
  httpd_resp_set_type(req, "image/jpeg");
  /* On ajoute un en-tête HTTP pour dire au navigateur d'afficher l'image directement à l'écran (inline) et 
  de lui donner un nom par défaut (capture.jpg) si l'utilisateur décide de l'enregistrer */
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  // C'est la fonction qui envoie les données au client (le navigateur web).
  esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  //Une fois que l'image a été envoyée, il faut impérativement libérer le buffer (fb) pour que la caméra puisse en prendre une autre.
  esp_camera_fb_return(fb);
  return res;
}

// Handler pour / : page HTML minimale (pour l'instant, sans flux).
static esp_err_t index_handler(httpd_req_t *req) {
  const char *html =
    "<!doctype html><html><head><meta charset='utf-8'>"
    "<title>ESP32-CAM</title></head><body>"
    "<h1>ESP32-CAM</h1>"
    "<p><a href='/capture'>/capture</a> (une image JPEG)</p>"
    "</body></html>";
  httpd_resp_set_type(req, "text/html; charset=utf-8");
  return httpd_resp_send(req, html, HTTPD_RESP_USE_STRLEN);
}

static void start_server() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  if (httpd_start(&server, &config) != ESP_OK) {
    Serial.println("Echec demarrage serveur HTTP");
    return;
  }
  httpd_uri_t uri_capture = { .uri="/capture", .method=HTTP_GET,
                              .handler=capture_handler, .user_ctx=NULL };
  httpd_uri_t uri_index   = { .uri="/",         .method=HTTP_GET,
                              .handler=index_handler,   .user_ctx=NULL };
  httpd_register_uri_handler(server, &uri_capture);
  httpd_register_uri_handler(server, &uri_index);
}

void setup() {
  Serial.begin(115200);
  delay(200);

  camera_config_t cfg = {};
  cfg.ledc_channel = LEDC_CHANNEL_0;
  cfg.ledc_timer   = LEDC_TIMER_0;
  cfg.pin_pwdn     = PWDN_GPIO_NUM;
  cfg.pin_reset    = RESET_GPIO_NUM;
  cfg.pin_xclk     = XCLK_GPIO_NUM;
  cfg.pin_sccb_sda = SIOD_GPIO_NUM;
  cfg.pin_sccb_scl = SIOC_GPIO_NUM;
  cfg.pin_d0       = Y2_GPIO_NUM;
  cfg.pin_d1       = Y3_GPIO_NUM;
  cfg.pin_d2       = Y4_GPIO_NUM;
  cfg.pin_d3       = Y5_GPIO_NUM;
  cfg.pin_d4       = Y6_GPIO_NUM;
  cfg.pin_d5       = Y7_GPIO_NUM;
  cfg.pin_d6       = Y8_GPIO_NUM;
  cfg.pin_d7       = Y9_GPIO_NUM;
  cfg.pin_vsync    = VSYNC_GPIO_NUM;
  cfg.pin_href     = HREF_GPIO_NUM;
  cfg.pin_pclk     = PCLK_GPIO_NUM;
  cfg.xclk_freq_hz = 20000000;
  cfg.pixel_format = PIXFORMAT_JPEG;
  cfg.frame_size   = FRAMESIZE_VGA;   // 640x480 : bon compromis netteté/poids
  cfg.jpeg_quality = 12;              // 0 = meilleure, 63 = pire
  cfg.fb_count     = 1;

  if (esp_camera_init(&cfg) != ESP_OK) {
    Serial.println("Echec init camera");
    return;
  }
  Serial.println("Camera OK");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connexion Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) { Serial.print("."); delay(500); }
  Serial.println();
  Serial.print("IP : "); Serial.println(WiFi.localIP());

  start_server();
  Serial.println("Serveur HTTP demarre");
}

void loop() {
  delay(10000);   // tout est gere par le serveur HTTP en tache de fond
}