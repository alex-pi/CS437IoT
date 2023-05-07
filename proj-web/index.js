
const main = (function () {
    const mo = {};
    let server_port = 65432;
    //let server_addr = "192.168.0.104";   // the IP address of your Raspberry PI
    //let server_addr = "127.0.0.1";
    //let server_addr = "108.255.58.24";
    const net = require('net');

    /**
     * Sends a request and passes the response data (if any) to the function handler.
     * */
    const send_request = function(req_data, handler) {

        let server_addr = server_input.val()
        const client = net.createConnection({ port: server_port, host: server_addr, keepAlive: true}, () => {
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
        let plant_id = event.target.id
        let cmd_to_send = {
            cmd: 'water',
            params: {
                ml: parseInt($(`#w_${plant_id}`).val()),
                plant: plant_id
            }
        }

        let json_str = JSON.stringify(cmd_to_send)
        console.log(json_str)
        send_request(json_str, (data) => {
            return
        })
    })

    /**
     * It is called from the index.html to initialized the visualization
     * */
    mo.init = async function () {
        btns = $('img.button')
        server_input = $('#server')

        // Add click event listener to the image
        btns.on("mousedown", function() {
            // Add 'pressed' class when the image is pressed
            $(this).addClass("pressed");
        }).on("mouseup", function() {
            // Remove 'pressed' class when the mouse is released
            $(this).removeClass("pressed");
        }).on("mouseup", command_handler);
    };

    return mo;

})();