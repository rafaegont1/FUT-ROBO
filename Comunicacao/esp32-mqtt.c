#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <string.h>
#include "esp_wifi.h"
#include "esp_wifi_types.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "mqtt_client.h"
#include "esp_check.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_timer.h"
#include "sdkconfig.h"
#include "hal/adc_types.h"
#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"
#include "sdkconfig.h"
#include "soc/clk_tree_defs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"



char topic[15], data[15];
adc_oneshot_unit_handle_t handle = NULL;
esp_mqtt_client_handle_t client = NULL;



static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
	esp_mqtt_event_handle_t event = event_data;
	sprintf(topic, "%.*s", event->topic_len, event->topic);
	sprintf(data, "%.*s", event->data_len, event->data);

	//printf("\n%d", 88);

	printf("\n%s", data);
}

void wifi()
{
	//Inicializando wifi:
	nvs_flash_init();
	esp_netif_init();
	esp_event_loop_create_default();
	esp_netif_create_default_wifi_sta();
	wifi_init_config_t wifi_initiation = WIFI_INIT_CONFIG_DEFAULT();
	esp_wifi_init(&wifi_initiation);
	wifi_config_t wifi_configuration = {
		.sta = {
					.ssid 		= "robotica",
					.password 	= "renato#305",
		},
	};
	esp_wifi_set_mode(WIFI_MODE_STA);
	esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_configuration);
	esp_wifi_start();
	esp_wifi_connect();
}

void mqtt()
{
	//Configuração do MQTT:
	esp_event_loop_create_default();
	esp_mqtt_client_config_t mqtt_cfg = {
		.broker.address.uri = "mqtt://test.mosquitto.org:1883",
		.credentials.client_id	= "ESP32",
	};
	client = esp_mqtt_client_init(&mqtt_cfg);

	esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);

	esp_mqtt_client_start(client);

	//Subscrevendo nos tópicos:
	esp_mqtt_client_subscribe(client, "testeesp32-pc", 1);
}

void app_main()
{
	wifi();

	sleep(3);

	mqtt();

	sleep(1);

	while(1)
	{
		//esp_mqtt_client_publish(client, "testeesp32-pc", "SOU O ESP32", 0, 1, 0);
		sleep(1);
	}
}
