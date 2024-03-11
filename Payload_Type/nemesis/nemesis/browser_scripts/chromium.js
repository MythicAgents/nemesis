function(task, responses){
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(responses.length > 0){
            let tables = [];
            try{
                let allData = JSON.parse(responses[0]);
                let data = allData["nemesis_chromium_logins"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "browser":{"plaintext": data[i]["browser"]},
                        "decrypted": {"plaintext": data[i]["password_value_dec"]},
                        "realm": {"plaintext": data[i]["signon_realm"] },
                        "user": {"plaintext": data[i]["username"]},
                        "username": {"plaintext": data[i]["username_value"]},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": data[i],
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Logon Data"
                                    },
                                ]
                            }},
                    });
                }
                tables.push(
                    {
                            "headers": [
                                {"plaintext": "browser", "type": "string", width: 70},
                                {"plaintext": "decrypted", "type": "string", fillWidth: true},
                                {"plaintext": "realm", "type": "string", fillWidth: true},
                                {"plaintext": "user", "type": "string", fillWidth: true},
                                {"plaintext": "username", "type": "string", fillWidth: true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Login Data"
                        }
                    );
                data = allData["nemesis_chromium_history"];
                output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "browser":{"plaintext": data[i]["browser"]},
                        "title": {"plaintext": data[i]["title"]},
                        "count": {"plaintext": data[i]["visit_count"] },
                        "last": {"plaintext": data[i]["last_visit_time"]},
                        "user": {"plaintext": data[i]["user"]},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": data[i],
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing History Data"
                                    },
                                ]
                            }},
                    });
                }
                tables.push(
                        {
                            "headers": [
                                {"plaintext": "browser", "type": "string", width: 70},
                                {"plaintext": "title", "type": "string", fillWidth: true},
                                {"plaintext": "count", "type": "number", width: 70},
                                {"plaintext": "last", "type": "date", fillWidth: true},
                                {"plaintext": "user", "type": "string", fillWidth: true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "History"
                        });
                data = allData["nemesis_chromium_downloads"];
                output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "browser":{"plaintext": data[i]["browser"]},
                        "user": {"plaintext": data[i]["username"]},
                        "path": {"plaintext": data[i]["download_path"] },
                        "size": {"plaintext": data[i]["total_bytes"]},
                        "url": {"plaintext": data[i]["url"]},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": data[i],
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Download Data"
                                    },
                                ]
                            }},
                    });
                }
                tables.push(
                        {
                            "headers": [
                                {"plaintext": "browser", "type": "string", width: 70},
                                {"plaintext": "user", "type": "string", fillWidth: true},
                                {"plaintext": "path", "type": "string", fillWidth: true},
                                {"plaintext": "size", "type": "size", width: 70},
                                {"plaintext": "url", "type": "string", fillWidth: true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Download History"
                        }
                )
                return {"table": tables}
            }catch(error){
                console.log(error);
                const combined = responses.reduce( (prev, cur) => {
                    return prev + cur;
                }, "");
                return {'plaintext': combined};
            }
        }else{
            return {"plaintext": "No output from command"};
        }
    }else{
        return {"plaintext": "No data to display..."};
    }
}