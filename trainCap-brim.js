var io = require('socket.io-client')
var socket = io.connect('http://localhost:8080')
socket.emit('targetConnected', {})
socket.on('setSpeed', function(data) {
	console.log("Got speed from server "+data.speed)
	global_speed = data.speed
	sendPy("l1.speed = "+global_speed.toString())
})

var spawn = require('child_process').spawn
var python_process = spawn('/usr/bin/python',['./brimWorker.py'])
function sendPy(cmd) {
  console.log("#########"+cmd)
  python_process.stdin.write(cmd+"\n")
}
python_process.stdout.on('data', function(data) {
  console.log('stdout: '+data)
});
python_process.stderr.on('data', function(data) {
  console.log('stderr: '+data)
});
python_process.stderr.on('close', function(code) {
  console.log('close: '+code)
});


var global_speed = 0
/*
sendPy("from dccpi import *")
sendPy("e = DCCRPiEncoder(pin_a=8,pin_b=9,pin_break=7)")
sendPy("c = DCCController(e)")
sendPy("l1 = DCCLocomotive('DCC', 3)")
sendPy("c.register(l1)")
sendPy("c.start()")
sendPy("l1.reverse()")
*/
setInterval(function() {
//	sendPy("l1.speed = "+global_speed.toString())
},1000)

