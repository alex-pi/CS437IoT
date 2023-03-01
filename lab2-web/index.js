
const main = (function () {
    const mo = {};
    let command;
    let distance;
    let angle;
    let car_status;
    let distance_traveled;
    let current_speed;
    let cpu_use;
    let free_memory;
    let total_memory;
    let server_port = 65432;
    //let server_addr = "192.168.0.101";   // the IP address of your Raspberry PI
    let server_addr = "127.0.0.1";
    const net = require('net');

    const send_request = function(req_data, handler) {

        const client = net.createConnection({ port: server_port, host: server_addr }, () => {
            // 'connect' listener.
            console.log('connected to server!');
            // send the message
            client.write(req_data);
        });

        // get the data from the server
        client.on('data', (data) => {
            console.log(`Data received: ${data.toString()}`);
            handler(data)
            client.end();
            client.destroy();
        });

        client.on('end', () => {
            console.log('disconnected from server');
        });

    }

    const command_handler = (function(event) {

        //if (command == null)
        let command = event.target.id
        let cmd_to_send = {
            cmd: command,
            params: {}
        }

        if (command == 'forward' || command == 'backward') {
            cmd_to_send.params = {
                distance: distance.val()
            }
        } else if(command == 'left' || command == 'right') {
            cmd_to_send.params = {
                angle: angle.val()
            }
        }

        let json_str = JSON.stringify(cmd_to_send)
        console.log(json_str)
        send_request(json_str, (data) => {
            return
        })
    })

    const metrics_refresh = (function() {

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

        })

    })

    /**
     * It is called from the index.html to initialized the visualization
     * */
    mo.init = async function () {
        command = $('img.command')
        distance = $('#distance')
        angle = $('#angle')
        car_status = $('#car_status')
        distance_traveled = $('#distance_traveled')
        current_speed = $('#current_speed')
        cpu_use = $('#cpu_use')
        free_memory = $('#free_memory')
        total_memory = $('#total_memory')

        command.on("click", command_handler);

        setInterval(metrics_refresh, 3000)
    };

    return mo;

})();