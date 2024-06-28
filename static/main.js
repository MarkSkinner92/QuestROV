let socket = io.connect('http://' + document.domain + ':' + location.port);
/*

This is the default input mapping responsible for taking key, button, and axis inputs and mapping them to certain ROV actions.
At runtime, it is replaced with the contents of inputMapping of config.json if that file is found.

axis : gamepad axis id (2 axis exist per joystick)
axisMultiplier : multiplies the value of the axis given (use to change direction of axis)

buttons are gamepad buttons
  - positive returns 1
  - negative returns -1
  - when released, a value of 0 is returned

keys are on the keyboard
  - positive returns 1
  - negative returns -1
  - when released, a value of 0 is returned

*/

let inputMapping = {};

// Try to update the key input mapping dictionary with the json file, otherwise, just fall back on the default.
$.getJSON('config_data', function(data) {
  console.log("Loaded config");
  console.log(data);
  if(data.inputMapping){
    inputMapping = data.inputMapping;
  }
});

pressedKeys = {}

// grab a reference to our attitude and heading widgets
let attitude = $.flightIndicator('#attitude', 'attitude', {roll:50, pitch:-20, size:150, showBox : false, img_directory : window.widgetImagePath});
let heading = $.flightIndicator('#heading', 'heading', {size:100, showBox : false, img_directory : window.widgetImagePath});

socket.on('imu', function(msg) {
    data = JSON.parse(msg);
    if(data?.pitch) attitude.setPitch(data.pitch)
    if(data?.roll) attitude.setRoll(data.roll)
    if(data?.heading) heading.setHeading(data.heading)
});

//this interval sends a ping at a realitively high frequency
//omitting this interval, or slowing it down to even 1hz makes the socket connection chopy and unreliable.
setInterval(() => {
  socket.emit('ping')
}, 1000/30)

function sendControl(name,value){
  socket.emit("man",name,value);
}

function checkGamepadSupport() {
  return 'getGamepads' in navigator;
}

// Object to store the previous state of gamepad buttons and axes
var previousState = {};

// Function to handle gamepad connected event
function handleGamepadConnected(event) {
  console.log("Gamepad connected:", event.gamepad.id);
}

// Function to handle gamepad disconnected event
function handleGamepadDisconnected(event) {
  console.log("Gamepad disconnected:", event.gamepad.id);
}

// Function to handle gamepad button state change
function handleButtonStateChange(gamepad, buttonIndex) {
  var buttonState = gamepad.buttons[buttonIndex].pressed;
  var previousButtonState = previousState[gamepad.index].buttons[buttonIndex];
  
  if (buttonState !== previousButtonState) {
    previousState[gamepad.index].buttons[buttonIndex] = buttonState;

    for (let mapcode in inputMapping) {
      if(inputMapping[mapcode].buttonPositive == buttonIndex){
        sendControl(mapcode, buttonState?1:0)
        // console.log(mapcode, buttonState?1:0)
      }else if(inputMapping[mapcode].buttonNegative == buttonIndex){
        sendControl(mapcode, (buttonState?1:0) * -1)
        // console.log(mapcode, (buttonState?1:0) * -1)
      }
    }
  }
}

// Function to handle gamepad axis state change
function handleAxisStateChange(gamepad, axisIndex) {
  var axisValue = gamepad.axes[axisIndex];
  var previousAxisValue = previousState[gamepad.index].axes[axisIndex];
  
  if (axisValue !== previousAxisValue) {
    previousState[gamepad.index].axes[axisIndex] = axisValue;

    for (let mapcode in inputMapping) {
      if(inputMapping[mapcode].axis == axisIndex){
        sendControl(mapcode, axisValue * inputMapping[mapcode].axisMultiplier)
        // console.log(mapcode, axisValue * inputMapping[mapcode].axisMultiplier)
      }
    }
  }
}

// Check for gamepad support
if (checkGamepadSupport()) {
  window.addEventListener("gamepadconnected", function(event) {
    handleGamepadConnected(event);
    previousState[event.gamepad.index] = {
      buttons: new Array(event.gamepad.buttons.length).fill(false),
      axes: new Array(event.gamepad.axes.length).fill(0)
    };
  });
  
  window.addEventListener("gamepaddisconnected", function(event) {
    handleGamepadDisconnected(event);
    delete previousState[event.gamepad.index];
  });

  // Function to continuously poll gamepad state
  function pollGamepads() {
    var gamepads = navigator.getGamepads();

    for (var i = 0; i < gamepads.length; i++) {
      var gamepad = gamepads[i];
      if (gamepad) {
        // Check button state changes
        for (var j = 0; j < gamepad.buttons.length; j++) {
          handleButtonStateChange(gamepad, j);
        }

        // Check axis state changes
        for (var k = 0; k < gamepad.axes.length; k++) {
          handleAxisStateChange(gamepad, k);
        }
      }
    }

    requestAnimationFrame(pollGamepads);
  }

  // Start polling gamepad state
  pollGamepads();
} else {
  console.log("Gamepad not supported");
}


// Function to handle keydown event
function handleKeyDown(event) {

  if(!pressedKeys[event.key]){
    pressedKeys[event.key] = true;

    for (let mapcode in inputMapping) {
      if(inputMapping[mapcode].keyPositive == event.key){
        sendControl(mapcode, 1)
        // console.log(mapcode, 1)
      }else if(inputMapping[mapcode].keyNegative == event.key){
        sendControl(mapcode, -1)
        // console.log(mapcode, -1)
      }
    }
  }

    // Display key info
    // document.getElementById("key-info").innerHTML = "Key Down: " + keyName + " (KeyCode: " + keyCode + ")";
}

// Function to handle keyup event
function handleKeyUp(event) {
  pressedKeys[event.key] = false;
  for (let mapcode in inputMapping) {
    if(inputMapping[mapcode].keyPositive == event.key || inputMapping[mapcode].keyNegative == event.key){
      sendControl(mapcode, 0)
      // console.log(mapcode, 0)
    }
  }

    // Display key info
    // document.getElementById("key-info").innerHTML = "Key Up: " + keyName + " (KeyCode: " + keyCode + ")";
}

// Add event listeners for keydown and keyup events
window.addEventListener("keydown", handleKeyDown);
window.addEventListener("keyup", handleKeyUp);


// TELEM
let telem = [];

registerTelem('telem');


function registerTelem(socketEventName){
  let myIndex = telem.length;
  socket.on(socketEventName, function(msg) {
    telem[myIndex] = `${msg}`;
    refreshTelem();
  })
}

function refreshTelem(){
  document.getElementById("telem").innerText = telem.join('\n');
}