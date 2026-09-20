const express = require("express");

const app = express();

const PORT = 3000;

// Put the IP address from Arduino Serial Monitor here
const ARDUINO_IP = "10.128.196.248";

app.use(express.json());

app.use(express.static("public"));


app.post("/api/light", async (req, res) => {

    const room = req.body.room;

    try {
        //http://YOUR_NANO_IP/light?room=room_name

        const url =
            `http://${ARDUINO_IP}/light?room=${encodeURIComponent(room)}`;

        const response = await fetch(url);

        const message = await response.text();

        res.json({
            success: true,
            message: message
        });

    }

    catch (error) {

        console.error(error);

        res.status(500).json({
            success: false,
            error: "Could not connect to Arduino"
        });

    }
});


app.listen(PORT, () => {

    console.log(
        `Website running at http://localhost:${PORT}`
    );

});