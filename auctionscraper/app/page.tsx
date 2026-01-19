import {useEffect, useState} from "react";

export default function Home() {

    const [busses, setBusses] = useState()

    fetch("/busses.json").then(res => res.json()).then((data) => {
        console.log(data)
    })

    return (
        <html>
        <body>
        <div>
            hello
        </div>
        </body>
        </html>
    );
}
