
const main = (function () {
    const mo = {};
    let command;
    let distance;
    let angle;
    let server_status;
    let car_status;
    let distance_traveled;
    let current_speed;
    let cpu_use;
    let free_memory;
    let total_memory;
    let battery_voltage
    let server_port = 65432;
    let server_addr = "192.168.0.101";   // the IP address of your Raspberry PI
    //let server_addr = "127.0.0.1";
    const net = require('net');

    /**
     * Sends a request and passes the response data (if any) to the function handler.
     * */
    const send_request = function(req_data, handler) {

        const client = net.createConnection({ port: server_port, host: server_addr }, () => {
            // 'connect' listener.
            console.log('connected to server!');
            // send the message
            client.write(req_data);
        });

        client.on("error", e => {
            console.log(`Endpoint is unreachable: ${server_addr}:${server_port}. ${e && e.message}`)
            server_status.val('Unreachable')
        });

        // get the data from the server
        client.on('data', (data) => {
            console.log(`Data received: ${data.toString()}`);
            server_status.val('OK')
            handler(data)
            client.end();
            client.destroy();
        });

        client.on('end', () => {
            console.log('disconnected from server');
        });

    }

    /**
     * Sends a command to the socket server in JSON format.
     * */
    const command_handler = (function(event) {

        //if (command == null)
        let command = event.target.id
        let cmd_to_send = {
            cmd: command,
            params: {}
        }

        if (command == 'forward' || command == 'backward') {
            cmd_to_send.params = {
                distance: parseInt(distance.val())
            }
        } else if(command == 'left' || command == 'right') {
            cmd_to_send.params = {
                angle: parseInt(angle.val())
            }
        }

        let json_str = JSON.stringify(cmd_to_send)
        console.log(json_str)
        send_request(json_str, (data) => {
            return
        })
    })

    /**
    * Updates all stats fields with data from PiCar
    * */
    const refresh_metrics = (function() {

        let cmd_to_send = {
            cmd: 'metrics'
        }
        let json_str = JSON.stringify(cmd_to_send)
        send_request(json_str, (data) => {
            let metrics = JSON.parse(data)
            console.log(`Refreshing metrics: ${data}`)
            car_status.val(metrics.car_status)
            distance_traveled.val(metrics.distance_traveled)
            current_speed.val(metrics.current_speed)
            cpu_use.val(metrics.cpu_use)
            free_memory.val(metrics.free_memory)
            total_memory.val(metrics.total_memory)
            battery_voltage.val(metrics.battery_voltage)
        })

    })

    /**
     * It is called from the index.html to initialized the visualization
     * */
    mo.init = async function () {
        command = $('img.command')
        distance = $('#distance')
        angle = $('#angle')
        server_status = $('#server_status')
        car_status = $('#car_status')
        distance_traveled = $('#distance_traveled')
        current_speed = $('#current_speed')
        cpu_use = $('#cpu_use')
        free_memory = $('#free_memory')
        total_memory = $('#total_memory')
        battery_voltage = $('#battery_voltage')

        command.on("click", command_handler);

        setInterval(refresh_metrics, 1500)
    };

    return mo;

})();