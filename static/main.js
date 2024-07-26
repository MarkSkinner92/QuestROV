let socket = io.connect('http://' + location.host);

socket.on('connect',()=>{
  socket.emit('newDriver')
});
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

socket.on('leak', function(msg) {
  detectLeak();
  setTimeout(cancelLeak,2000)
});

socket.on('name', function(msg) {
  console.log("got name",msg);
  document.querySelector('.ROVname').innerText = msg;
});

socket.on('speedTest', function(){
  console.log("Uploading 100 Mb from the ROV to this computer (as a network speed test)")
  runFullSpeedTest();
});

function runFullSpeedTest(){
  doDownloadTest().then(() => {
    doUploadTest();
  });
}

function detectLeak(){
  console.log("leak")
  document.getElementById("holderDiv").style.background = "#FF000050";
  document.getElementById("leakText").style.display = "block";
  let audio = document.getElementById("leakAudio");
  audio.currentTime = 0;
  audio.play();
}
function cancelLeak(){
  document.getElementById("holderDiv").style.background = "#FFFFFF00";
  document.getElementById("leakText").style.display = "none";
}
//this interval sends a ping at a realitively high frequency
//omitting this interval, or slowing it down to even 1hz makes the socket connection chopy and unreliable.
setInterval(() => {
  socket.emit('ping')
}, 1000/30)

function sendControl(name,value){
  socket.emit("man",name,value);
}

function sendKeepAlive(){
  socket.emit("man","keepalive","ok");
}

// Send a keep alive every 4 seconds
setInterval(() => {
  sendKeepAlive();
}, 4000)

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

registerTelem('telem',0);
registerTelem('pressure',1);


function registerTelem(socketEventName,index){
  socket.on(socketEventName, function(msg) {
    telem[index] = `${msg}`;
    refreshTelem();
  })
}

function refreshTelem(){
  document.getElementById("telem").innerText = telem.join('\n');
}
function setInFocus(){
  document.getElementById("focusBtn").style.display = "none";
}
window.onfocus = () => {
  console.log("got focus");
  setInFocus()
}
window.onblur = () => {
  console.log("lost focus")
  document.getElementById("focusBtn").style.display = "block";
}

function doUploadTest(){
  let start_time;
  let speeds = [];

  axios({
    method: 'post',
    url: `http://${window.location.hostname}/network-test/post_file`,
    timeout: 10000,
    data: new ArrayBuffer(100 * 2 ** 20),
    onUploadProgress: (progress_event) => {
      if (start_time === undefined) {
        start_time = new Date().getTime();
        return;
      }

      const seconds = (new Date().getTime() - start_time) * 1e-3;
      const speed_Mb = 8 * (progress_event.loaded / seconds / 2 ** 20);
      const alpha_factor = 0.7;

      // Update upload speed with exponential smoothing
      let upload_speed = (this.upload_speed ?? 0) * (1 - alpha_factor) + alpha_factor * speed_Mb;

      console.log("progress on upload speed test:", speed_Mb, "Mbps");
      speeds.push(speed_Mb)
    },
  }).finally(()=>{
    let avg = 0;
    if(speeds.length > 0){
      if(speeds.length == 1) avg = speeds[0];
      if(speeds.length == 2) avg = (speeds[0] + speeds[1])/2;
      if(speeds.length > 2){
        avg = speeds[Math.floor(speeds.length/2)];
      }
    }
    console.log("avg (median) upload Speed",avg);
    socket.emit("uploadSpeed",avg);
  });

}

function doDownloadTest(){
  return new Promise((resolve) => {
    const one_hundred_mega_bytes = 100 * 2 ** 20;
    let start_time;
    let speeds = [];
    axios({
      method: 'get',
      url: `http://${window.location.hostname}/network-test/get_file`,
      timeout: 20000,
      params: {
        size: one_hundred_mega_bytes,
        avoid_cache: new Date().getTime(),
      },
      onDownloadProgress: (progress_event) => {
        if (start_time === undefined) {
          start_time = new Date().getTime();
          return;
        }

        const seconds = (new Date().getTime() - start_time) * 1e-3;
        const speed_Mb = 8 * (progress_event.loaded / seconds / 2 ** 20);
        const alpha_factor = 0.7;

        // Update download speed with exponential smoothing
        let download_speed = (this.download_speed ?? 0) * (1 - alpha_factor) + alpha_factor * speed_Mb;

        console.log("progress on download speed test:", speed_Mb, "Mbps");
        speeds.push(speed_Mb)
      },
    }).finally(() => {
      let avg = 0;
      if(speeds.length > 0){
        if(speeds.length == 1) avg = speeds[0];
        if(speeds.length == 2) avg = (speeds[0] + speeds[1])/2;
        if(speeds.length > 2){
          avg = speeds[Math.floor(speeds.length/2)];
        }
      }
      console.log("avg (median) download Speed",avg);
      socket.emit("downloadSpeed",avg);
      resolve();
    });
  });
}