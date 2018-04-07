/*
  Regn :: Arduino Weather Station

  @version    0.1.0
  @author     Mika Naylor [Autophagy] :: http://autophagy.io/
  @hardware   Mika Naylor [Autophagy] :: http://autophagy.io/

  @description
  An arduino client that reads temp, humidity, atmospheric pressure and
  luminosity at 3 second intervals. Takes 20 readings per interval and averages
  them in order to minimise anomalous readings.

  Implementation Details :: https://github.com/Autophagy/regn
*/

// Libraries
#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>
#include <Adafruit_BMP085_U.h>

// Constants
#define DHTPIN 12 // DHT22 connected to pin 12
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_LOW, 12345);
Adafruit_BMP085_Unified bmp = Adafruit_BMP085_Unified(10085);


// Variables
bool DEBUG = true; // Set to true to output sensor information to the Serial port.

long sensor_interval = 10000; // 10 seconds
float temperature;
float humidity;
float pressure;
float lux;

void setup() {

  if (DEBUG) {
    Serial.begin(115200);
  }

  dht.begin();
  tsl.enableAutoRange(true);
  tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_13MS);
  bmp.begin();
}

void loop() {
  temperature = getTemperature();
  humidity = getHumidity();
  pressure = getPressure();
  lux = getLux();

  if (DEBUG) {
    outputDebugInfo();
  }

  // Delay by sensor_interval for each read
  delay(sensor_interval);
}


// Returns the temperature reading from the DHT22 sensor
float getTemperature() {
  return dht.readTemperature();
}

// Returns the humidity reading from the DHT22 sensor
float getHumidity() {
  return dht.readHumidity();
}

// Returns the pressure reading from the BMP180 sensor
float getPressure() {
  sensors_event_t event;
  bmp.getEvent(&event);
  return event.pressure;
}

// Returns the lux reading from the TSL2561 sensor
float getLux() {
  sensors_event_t event;
  tsl.getEvent(&event);
  return event.light;
}

// Prints sensor info out to Serial for debugging purposes
void outputDebugInfo() {
  Serial.println("------------------------------------");

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" *C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %\t");

  Serial.print("Barometric pressure: ");
  Serial.print(pressure);
  Serial.println(" hPa");

  Serial.print("Luminosity: ");
  Serial.print(lux);
  Serial.println(" lux");

  Serial.println("------------------------------------");

}
