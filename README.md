# Subarulink AWS Lamba API

This repo allows you to control Subaru's Stralink remote features through a REST api.

### Why? 

This simplifies the interface making it easy to create automations that unlock or remote start your car.

### How?

This basically creates a AWS lambda wrapper around the `subarulink` python library. Obviously you need to own a newer Subaru with an active starlink subscription that includes remote control features.

## REST API

* `PUT http://{your_api_gateway_url}` contol something...
  * json encoded body: `{ 'pin': xxxx }`
  * lock/unlock: add the param `doors` with value `locked` or `unlocked`
  * TODO: start/stop engine add the param `engine` with value `running` or `stopped`
  * TODO: climate settings
  * TODO: honk horn, turn on lights
* TODO: `GET http://{your_api_gateway_url}` summary of vehicle status

### Example

This will unlock the doors

```
POST /path/to/resource HTTP/1.1
Host: api_id.execute-api.us-east-2.amazonaws.com
Content-Type: application/json
x-api-key: xyz123

{
  "pin": "1234",
  "doors": "unlocked"
}
```

## AWS Setup

* lambda function 
* api gateway resource as lmabda trigger 
  * should be confgured as a gateway lambda proxy
  * requiring an an api key is obvisouly a good idea
* the lambda should have the following ENV vars:
  * `SUBARU_USERNAME`
  * `SUBARU_PASSWORD`
  * `SUBARU_DEVICE_ID` any 10 digit number, ex. a timestamp
  * `SUBARU_DEVICE_NAME=subarulink`
  * `SUBARU_VIN` your car's VIN

## Deploying

* see the included github actions workflow
* make sure you supply the right secrets to access your aws account

OR

* `bin/setup` to create a virtual env and install dependencies
* `bin/archive` to pack up the code
* upload `tmp/archive.zip` to your lambda function using the aws console or CLI
